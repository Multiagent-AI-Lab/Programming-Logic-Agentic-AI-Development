"""
Agente Mapa Curricular (CurriculumMapAgent) - Lógica de Programación UCEMICH 🗺️
=================================================================================

Genera el mapa de dependencias entre las 9 unidades del curso: sugiere
candidatos de relación de concepto entre unidades (para aprobación humana)
y renderiza el diagrama Mermaid final a partir de relaciones ya aprobadas.
Heurístico puro, sin LLM.
"""

import re
from pathlib import Path
from typing import Dict, List

from .notebook_compiler_agent import extract_fenced_blocks

SKILL_METADATA = {
    "name": "curriculum_map_agent",
    "description": "Sugiere y renderiza el mapa de dependencias entre unidades del curso.",
    "version": "1.0.0",
    "input": "course_dir: Path",
    "output": "Dict[int, List[dict]] (suggest_prerequisites) | str Mermaid (render_dag)",
    "requires_api_key": False,
}

# 19 conceptos curados (ver spec §2); algunas variantes ortográficas del
# mismo concepto (ej. "recursión"/"recursivo") se listan como strings
# separados para que la coincidencia de substring detecte ambas formas.
TERMINOS_TECNICOS_CURADOS = [
    "variables",
    "tipos de datos",
    "tipo de dato",
    "diccionario",
    "lista",
    "arreglo",
    "string",
    "cadena",
    "recursión",
    "recursivo",
    "operador",
    "pruebas unitarias",
    "pytest",
    "bucle",
    "cohesión",
    "acoplamiento",
    "type hint",
    "anotación de tipo",
    "*args",
    "**kwargs",
    "lambda",
    "clase",
    "ast",
    "análisis estático",
    "sandbox",
    "mcp",
    "function calling",
    "pseudocódigo",
    "hilo de oro",
]

_FSTRING_PATTERN = re.compile(r'f["\']')
_UNIT_NUMBER_FROM_FILENAME = re.compile(r"UNIDAD_(\d+)_")
_PREREQUISITO_LINEA = re.compile(r"^- \*\*(.+?)\*\*\s*\(Unidad (\d+)\)")


class CurriculumMapAgent:
    """Agente que sugiere y renderiza el mapa de dependencias entre unidades."""

    _NOMBRES_UNIDAD = {
        0: "Entorno de Trabajo",
        1: "Pensamiento Computacional",
        2: "Metodología y Pruebas",
        3: "Variables y Operadores",
        4: "Estructuras de Decisión",
        5: "Ciclos y Bucles Agénticos",
        6: "Modularidad y MCP",
        7: "Estructuras de Datos y Grafos",
        8: "Proyecto Integrador",
    }

    def _numero_de_unidad(self, md_path: Path) -> int:
        """Extrae el número de unidad del nombre de archivo, o -1 si no aplica."""
        match = _UNIT_NUMBER_FROM_FILENAME.match(md_path.name)
        return int(match.group(1)) if match else -1

    def _leer_unidades_ordenadas(self, course_dir: Path) -> List[tuple]:
        """Lee todas las UNIDAD_*.md y las retorna ordenadas por número.

        Returns:
            Lista de tuplas (numero_unidad, contenido_completo, python_blocks).
        """
        resultado = []
        for md_path in course_dir.glob("UNIDAD_*.md"):
            numero = self._numero_de_unidad(md_path)
            if numero == -1:
                continue
            content = md_path.read_text(encoding="utf-8")
            bloques = extract_fenced_blocks(content)
            python_blocks = [code for _, lang, code in bloques if lang == "python"]
            resultado.append((numero, content, python_blocks))
        return sorted(resultado, key=lambda t: t[0])

    def _buscar_evidencia_prosa(self, termino: str, content: str) -> str:
        """Retorna la primera línea de content que menciona termino, o ''."""
        for linea in content.split("\n"):
            if termino.lower() in linea.lower():
                return linea.strip()
        return ""

    def suggest_prerequisites(self, course_dir: Path) -> Dict[int, List[dict]]:
        """Sugiere candidatos de relación de concepto entre unidades.

        Para cada unidad, busca en unidades ANTERIORES apariciones de los
        términos técnicos curados; si el mismo término aparece también en
        la unidad actual, es un candidato de relación. No escribe nada a
        disco — solo retorna candidatos para revisión humana.

        Args:
            course_dir: Directorio raíz del curso, donde viven los UNIDAD_*.md.

        Returns:
            Diccionario {numero_unidad: [candidatos]}, donde cada candidato
            es {"unidad_origen": int, "termino": str, "evidencia": str}.
        """
        unidades = self._leer_unidades_ordenadas(course_dir)
        resultado: Dict[int, List[dict]] = {}

        for i, (numero_actual, content_actual, blocks_actual) in enumerate(unidades):
            candidatos: List[dict] = []
            unidades_anteriores = unidades[:i]

            for termino in TERMINOS_TECNICOS_CURADOS:
                if termino.lower() not in content_actual.lower():
                    continue
                for numero_origen, content_origen, _ in unidades_anteriores:
                    if termino.lower() in content_origen.lower():
                        candidatos.append(
                            {
                                "unidad_origen": numero_origen,
                                "termino": termino,
                                "evidencia": self._buscar_evidencia_prosa(
                                    termino, content_actual
                                ),
                            }
                        )
                        break

            fstring_en_actual = any(_FSTRING_PATTERN.search(b) for b in blocks_actual)
            if fstring_en_actual:
                for numero_origen, _, blocks_origen in unidades_anteriores:
                    if any(_FSTRING_PATTERN.search(b) for b in blocks_origen):
                        candidatos.append(
                            {
                                "unidad_origen": numero_origen,
                                "termino": "f-string",
                                "evidencia": 'patrón f" detectado en código',
                            }
                        )
                        break

            resultado[numero_actual] = candidatos

        return resultado

    def _extrae_relaciones_de_seccion(self, content: str) -> List[dict]:
        """Extrae relaciones (término, unidad_origen) de la sección de
        prerequisitos ya escrita, ignorando líneas que no matcheen el
        formato exacto.

        Args:
            content: Texto completo del MD de la unidad.

        Returns:
            Lista de {"termino": str, "unidad_origen": int}.
        """
        relaciones = []
        for linea in content.split("\n"):
            match = _PREREQUISITO_LINEA.match(linea.strip())
            if match:
                relaciones.append(
                    {"termino": match.group(1), "unidad_origen": int(match.group(2))}
                )
        return relaciones

    def render_dag(self, course_dir: Path) -> str:
        """Genera el diagrama Mermaid del mapa de dependencias del curso.

        Lee, de cada UNIDAD_*.md, la sección '## 📚 Prerequisitos de esta
        unidad' ya aprobada y escrita, y genera el string Mermaid completo
        (cadena secuencial + subgraphs de fase + flechas de concepto).

        Args:
            course_dir: Directorio raíz del curso, donde viven los UNIDAD_*.md.

        Returns:
            String Mermaid crudo (sin fences ```mermaid).
        """
        unidades = self._leer_unidades_ordenadas(course_dir)
        numeros_presentes = {n for n, _, _ in unidades}

        lineas = ["graph LR"]

        fases = [
            ("SIN_IA", "Sin IA para código (U1-U3)", [1, 2, 3]),
            ("IA_MEDIA", "IA Moderada, asistencia documentada (U4-U6)", [4, 5, 6]),
            ("IA_EXT", "IA Extensiva (U7-U8)", [7, 8]),
        ]
        for id_fase, etiqueta, numeros in fases:
            lineas.append(f'  subgraph {id_fase}["{etiqueta}"]')
            lineas.append("    direction TB")
            for n in numeros:
                if n in numeros_presentes:
                    nombre = self._NOMBRES_UNIDAD.get(n, f"Unidad {n}")
                    lineas.append(f"    U{n}[U{n}: {nombre}]")
            lineas.append("  end")

        if 0 in numeros_presentes:
            nombre_u0 = self._NOMBRES_UNIDAD.get(0, "Entorno de Trabajo")
            lineas.append(f"  U0[U0: {nombre_u0}] --> U1")

        cadena = " --> ".join(f"U{n}" for n in sorted(numeros_presentes) if n >= 1)
        if cadena:
            lineas.append(f"  {cadena}")

        for numero_actual, content, _ in unidades:
            for relacion in self._extrae_relaciones_de_seccion(content):
                lineas.append(
                    f"  U{relacion['unidad_origen']} -.{relacion['termino']}.-> U{numero_actual}"
                )

        lineas.append("  style SIN_IA fill:#ffe0e0,stroke:#cc6666")
        lineas.append("  style IA_MEDIA fill:#fff4cc,stroke:#ccaa33")
        lineas.append("  style IA_EXT fill:#d4f4dd,stroke:#66aa77")

        return "\n".join(lineas)


if __name__ == "__main__":
    agent = CurriculumMapAgent()
    course_dir = Path(__file__).parent.parent.parent / "lecciones"
    candidatos = agent.suggest_prerequisites(course_dir)
    for unidad, lista in sorted(candidatos.items()):
        print(f"\n=== Unidad {unidad} ===")
        for c in lista:
            print(
                f"  - {c['termino']} (de Unidad {c['unidad_origen']}): {c['evidencia']}"
            )
    print("\n\n=== DAG actual (basado en secciones ya aprobadas) ===")
    print(agent.render_dag(course_dir))
