"""
Agente Auditor de Contenido (ContentAuditorAgent) - Lógica de Programación UCEMICH 🔍
======================================================================================

Audita las 9 unidades del curso (contenido escrito por el mantenedor, no por
estudiantes) contra 4 dimensiones de calidad: rigor matemático/LaTeX,
coherencia pedagógica (Hilo de Oro), calidad de código de ejemplo, y
cumplimiento curricular contra el programa oficial. Heurístico puro, sin LLM.
"""

import ast
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from .code_auditor_agent import CodeAuditorAgent
from .mermaid_renderer import MermaidRenderer
from .notebook_compiler_agent import extract_fenced_blocks

SKILL_METADATA = {
    "name": "content_auditor_agent",
    "description": "Audita el contenido pedagógico de las unidades del curso (LaTeX, pedagogía, código, cumplimiento curricular).",
    "version": "1.0.0",
    "input": "md_path: Path (audit_unit) | course_dir: Path (audit_all_units)",
    "output": "Dict[str, Any] con hallazgos por dimensión (audit_unit) | str Markdown (audit_all_units)",
    "requires_api_key": False,
}

LATEX_KNOWN_MALFORMED = {
    r"\DeltaG": r"\Delta G",
    r"\DeltaH": r"\Delta H",
    r"\DeltaS": r"\Delta S",
}

_CELDA_MAGICA_IPYTHON = re.compile(r"^\s*[%!]", re.MULTILINE)
_ARGUMENTOS_SIN_TIPO_ESPERADO = {"self", "cls"}


@lru_cache(maxsize=None)
def _parse_programa_oficial(programa_path: Path) -> Dict[int, dict]:
    """Parsea el programa de asignatura oficial en subtemas y semanas por unidad.

    El resultado se cachea por ruta (`lru_cache`) porque `audit_all_units`
    invoca esta función una vez por cada unidad auditada, y el archivo no
    cambia entre esas llamadas dentro de una misma ejecución.

    Args:
        programa_path: Ruta al .txt del programa oficial extraído (formato con
            líneas "Unidad N: Título (Semana(s) X)" seguidas de líneas "N.M. subtema").

    Returns:
        Diccionario {numero_unidad: {"subtemas": [...], "semanas": str}}.
    """
    if not programa_path.exists():
        return {}

    content = programa_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    mapeo: Dict[int, dict] = {}
    unidad_actual = None

    for line in lines:
        unidad_match = re.match(r"^Unidad (\d+):.*\((Semanas? [\d\-]+)\)", line)
        if unidad_match:
            unidad_actual = int(unidad_match.group(1))
            mapeo[unidad_actual] = {
                "subtemas": [],
                "semanas": unidad_match.group(2),
            }
            continue

        subtema_match = re.match(r"^(\d+)\.(\d+)\.\s+(.+)$", line)
        if subtema_match and unidad_actual is not None:
            unidad_del_subtema = int(subtema_match.group(1))
            if unidad_del_subtema == unidad_actual:
                mapeo[unidad_actual]["subtemas"].append(subtema_match.group(3))

    return mapeo


_PROGRAMA_OFICIAL_PATH = (
    Path(__file__).parent.parent.parent
    / "docs"
    / "legado"
    / "planeacion_2023_2024"
    / "Programa_de_Asignatura_Logica_Programacion_IA_v2_extracted.txt"
)


class ContentAuditorAgent:
    """Agente que audita el contenido pedagógico de las unidades del curso."""

    def __init__(
        self,
        programa_path: Optional[Path] = None,
        mermaid_renderer: Optional[MermaidRenderer] = None,
    ) -> None:
        self.code_auditor = CodeAuditorAgent()
        self.programa_path = (
            Path(programa_path) if programa_path else _PROGRAMA_OFICIAL_PATH
        )
        self.mermaid_renderer = mermaid_renderer or MermaidRenderer(
            output_dir=Path.cwd() / "notebooks" / "assets" / "diagramas"
        )

    def _audit_latex(self, content: str) -> List[str]:
        """Detecta delimitadores LaTeX desbalanceados y comandos mal formados.

        Args:
            content: Texto completo del MD de la unidad.

        Returns:
            Lista de descripciones de hallazgos; vacía si no hay problemas.
        """
        hallazgos: List[str] = []

        sin_fences = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        tokens = re.findall(r"\$\$|\$", sin_fences)
        doble_count = sum(1 for t in tokens if t == "$$")
        simple_count = sum(1 for t in tokens if t == "$")
        if doble_count % 2 != 0:
            hallazgos.append(
                "Delimitadores '$$' desbalanceados: hay un número impar de "
                "bloques '$$', lo que sugiere una fórmula en bloque sin cerrar."
            )
        if simple_count % 2 != 0:
            hallazgos.append(
                "Delimitadores '$' desbalanceados: hay un número impar de '$' "
                "simples fuera de bloques '$$...$$', lo que sugiere una fórmula "
                "sin cerrar."
            )

        for malformado, correcto in LATEX_KNOWN_MALFORMED.items():
            if malformado in content:
                hallazgos.append(
                    f"Comando LaTeX mal formado: '{malformado}' encontrado; "
                    f"debería ser '{correcto}' (falta espacio, KaTeX no lo renderiza)."
                )

        return hallazgos

    def _audit_codigo(self, python_blocks: List[str]) -> List[str]:
        """Audita bloques de código Python de ejemplo (docstrings, type hints, estilo).

        Ignora la longitud de línea (PEP8 79 cols) porque el código de
        ejemplo del curso prioriza claridad didáctica en español sobre ese
        límite, y excluye funciones ``test_*`` de la exigencia de docstring/
        type hints (son ejemplos de pytest, no funciones de producción).
        Bloques con sintaxis mágica de IPython/Colab (``%pip install``,
        ``!comando``) se tratan como válidos y no generan un falso positivo
        de "error de sintaxis". ``self`` y ``cls`` nunca se marcan como
        "argumento sin tipo" — anotarlos no es válido en Python idiomático.

        Args:
            python_blocks: Lista de bloques de código Python extraídos del MD.

        Returns:
            Lista de descripciones de hallazgos; vacía si no hay problemas.
        """
        hallazgos: List[str] = []

        for code in python_blocks:
            if _CELDA_MAGICA_IPYTHON.search(code):
                continue

            hallazgos.extend(
                h for h in self.code_auditor.audit_style(code) if "PEP 8" not in h
            )
            hallazgos.extend(self.code_auditor.audit_security(code))

            try:
                tree = ast.parse(code)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name.startswith("test_"):
                    continue
                if ast.get_docstring(node) is None:
                    hallazgos.append(
                        f"Función '{node.name}' sin docstring en el código de ejemplo."
                    )
                args_sin_tipo = [
                    a.arg
                    for a in node.args.args
                    if a.annotation is None
                    and a.arg not in _ARGUMENTOS_SIN_TIPO_ESPERADO
                ]
                if args_sin_tipo or node.returns is None:
                    hallazgos.append(
                        f"Función '{node.name}' sin type hints completos "
                        f"(argumentos sin tipo: {args_sin_tipo or 'ninguno'}, "
                        f"retorno anotado: {node.returns is not None})."
                    )

        return hallazgos

    def _audit_pedagogico(self, bloques: List[tuple], content: str) -> List[str]:
        """Verifica coherencia pedagógica: Hilo de Oro, analogías, y sintaxis Mermaid.

        Args:
            bloques: Bloques de código extraídos vía extract_fenced_blocks.
            content: Texto completo del MD, para buscar el patrón de analogía.

        Returns:
            Lista de descripciones de hallazgos; vacía si no hay problemas.
        """
        hallazgos: List[str] = []

        idiomas_presentes = {lang for _, lang, _ in bloques}
        hilo_de_oro_esperado = {"pseudocodigo", "mermaid", "python", "pytest"}
        if not hilo_de_oro_esperado.issubset(idiomas_presentes):
            faltantes = hilo_de_oro_esperado - idiomas_presentes
            hallazgos.append(
                "Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → "
                f"Python → pytest): faltan bloques de tipo {sorted(faltantes)}."
            )

        if not re.search(r"^#{2,4}.*analog", content, re.IGNORECASE | re.MULTILINE):
            hallazgos.append(
                "No se encontró ninguna sección de Analogía Didáctica "
                "(encabezado H2-H4 que contenga 'analog...') en esta unidad."
            )

        mermaid_blocks = [code for _, lang, code in bloques if lang == "mermaid"]
        for diagrama in mermaid_blocks:
            try:
                self.mermaid_renderer.render(diagrama)
            except RuntimeError as e:
                if "Parse error" in str(e):
                    hallazgos.append(
                        f"Diagrama Mermaid con error de sintaxis: {str(e).splitlines()[0]}"
                    )
                else:
                    hallazgos.append(
                        "No se pudo validar el diagrama Mermaid (fallo de "
                        f"infraestructura, no de sintaxis): {str(e).splitlines()[0]}"
                    )

        return hallazgos

    def _audit_curricular(self, md_path: Path, content: str) -> List[str]:
        """Verifica cobertura temática y duración contra el programa oficial.

        Args:
            md_path: Ruta del MD, usada para extraer el número de unidad del nombre.
            content: Texto completo del MD.

        Returns:
            Lista de descripciones de hallazgos; vacía si la unidad no se
            reconoce por nombre o no hay discrepancias.
        """
        unidad_match = re.match(r"UNIDAD_(\d+)_", md_path.name)
        if not unidad_match:
            return []

        numero_unidad = int(unidad_match.group(1))
        mapeo = _parse_programa_oficial(self.programa_path)
        if numero_unidad not in mapeo:
            return []

        hallazgos: List[str] = []
        info = mapeo[numero_unidad]
        content_lower = content.lower()

        for subtema in info["subtemas"]:
            palabras_clave = [
                p.strip(".,()").lower() for p in subtema.split() if len(p) > 4
            ][:3]
            if palabras_clave and not any(p in content_lower for p in palabras_clave):
                hallazgos.append(
                    f"Subtema del programa oficial posiblemente no cubierto: "
                    f"'{subtema}' (ninguna de las palabras clave {palabras_clave} "
                    "aparece en el contenido)."
                )

        duracion_match = re.search(r"\*\*Duraci[óo]n:\*\*\s*(.+)", content)
        if duracion_match:
            duracion_texto = duracion_match.group(1)
            numeros_programa = re.findall(r"\d+", info["semanas"])
            if numeros_programa and not any(
                n in duracion_texto for n in numeros_programa
            ):
                hallazgos.append(
                    f"Posible discrepancia de duración: el MD dice "
                    f"'{duracion_texto.strip()}' pero el programa oficial indica "
                    f"'{info['semanas']}'."
                )

        return hallazgos

    _UNIT_NUMBER_PATTERN = re.compile(r"unit_number\s*=\s*(\d+)")

    def _verifica_unit_number(
        self, python_blocks: List[str], md_path: Path
    ) -> List[str]:
        """Verifica que unit_number en la celda de auto-evaluación coincida
        con el número de unidad indicado por el nombre del archivo.

        Args:
            python_blocks: Bloques de código Python extraídos del MD.
            md_path: Ruta del MD, usada para extraer el número de unidad.

        Returns:
            Lista con un hallazgo por cada bloque cuyo unit_number no
            coincida; vacía si coincide o si el archivo no se reconoce
            por nombre.
        """
        unidad_match = re.match(r"UNIDAD_(\d+)_", md_path.name)
        if not unidad_match:
            return []
        numero_esperado = int(unidad_match.group(1))

        hallazgos: List[str] = []
        for code in python_blocks:
            match = self._UNIT_NUMBER_PATTERN.search(code)
            if match and int(match.group(1)) != numero_esperado:
                hallazgos.append(
                    f"La celda de auto-evaluación usa unit_number={match.group(1)}, "
                    f"pero el archivo es de la Unidad {numero_esperado}."
                )
        return hallazgos

    _WRITEFILE_LINEA = re.compile(r"^\s*%%writefile\s+(\S+)", re.MULTILINE)

    def _extrae_writefiles_reales(self, python_blocks: List[str]) -> List[tuple]:
        """Extrae líneas reales de %%writefile (primera línea no en blanco
        de una celda), ignorando menciones en prosa o dentro de f-strings.

        Args:
            python_blocks: Bloques de código Python extraídos del MD.

        Returns:
            Lista de tuplas (nombre_archivo, indice_del_bloque_en_python_blocks).
        """
        resultado = []
        for idx, code in enumerate(python_blocks):
            for match in self._WRITEFILE_LINEA.finditer(code):
                resultado.append((match.group(1), idx))
        return resultado

    def _tiene_definicion_previa(
        self, python_blocks: List[str], indice_bloque: int
    ) -> bool:
        """Verifica si algún bloque anterior a indice_bloque define una
        función o clase (ast.parse + ast.walk), tolerando bloques con
        errores de sintaxis (se ignoran, no cuentan como definición).

        Args:
            python_blocks: Bloques de código Python extraídos del MD.
            indice_bloque: Índice del bloque que contiene el %%writefile.

        Returns:
            True si algún bloque anterior tiene al menos una FunctionDef,
            AsyncFunctionDef o ClassDef.
        """
        for code in python_blocks[:indice_bloque]:
            try:
                tree = ast.parse(code)
            except SyntaxError:
                continue
            if any(
                isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                for n in ast.walk(tree)
            ):
                return True
        return False

    def _verifica_writefiles_con_definicion(
        self, python_blocks: List[str]
    ) -> List[str]:
        """Verifica que todo %%writefile real tenga una definición de
        función/clase en algún bloque anterior del mismo MD.

        Args:
            python_blocks: Bloques de código Python extraídos del MD.

        Returns:
            Lista con un hallazgo por cada %%writefile sin definición
            previa; vacía si todos tienen definición o no hay ninguno.
        """
        hallazgos: List[str] = []
        for nombre_archivo, indice_bloque in self._extrae_writefiles_reales(
            python_blocks
        ):
            if not self._tiene_definicion_previa(python_blocks, indice_bloque):
                hallazgos.append(
                    f"'%%writefile {nombre_archivo}' no tiene ninguna definición "
                    "de función o clase en un bloque de código anterior del "
                    "mismo archivo — el alumno no tendría qué código pegar."
                )
        return hallazgos

    def _verifica_fences_balanceados(self, content: str) -> List[str]:
        """Detecta fences de apertura que extract_fenced_blocks() no pudo
        cerrar correctamente — señal indirecta: el último bloque extraído
        consume texto hasta el final del documento, aunque el .md real
        siga teniendo contenido después de ese fence en el texto fuente.

        No reimplementa el parseo de fences: reutiliza extract_fenced_blocks()
        (notebook_compiler_agent.py) como fuente de verdad, y solo inspecciona
        si su comportamiento de "consumir hasta EOF" ocurrió indebidamente.

        Args:
            content: Texto completo del MD de la unidad.

        Returns:
            Lista con un hallazgo si el último fence no cierra correctamente;
            vacía si no hay bloques o todos cierran bien.
        """
        bloques = extract_fenced_blocks(content)
        if not bloques:
            return []

        ultimo_fence, ultimo_lang, ultimo_codigo = bloques[-1]
        if not ultimo_codigo:
            return []

        primera_linea_codigo = ultimo_codigo.split("\n")[0]
        linea_apertura = f"{ultimo_fence}{ultimo_lang}"
        marcador_apertura = f"{linea_apertura}\n{primera_linea_codigo}"
        posicion_apertura = content.rfind(marcador_apertura)
        if posicion_apertura == -1:
            return []

        resto_tras_apertura = content[posicion_apertura:]
        lineas_resto = resto_tras_apertura.split("\n")
        cierre_encontrado = any(
            linea.strip() == ultimo_fence for linea in lineas_resto[1:]
        )
        if not cierre_encontrado:
            return [
                f"Posible fence de código sin cerrar: un bloque abierto con "
                f"'{ultimo_fence}' no encuentra su línea de cierre exacta en "
                "el resto del documento — extract_fenced_blocks() pudo haber "
                "consumido contenido no destinado a ser código."
            ]
        return []

    def _verifica_celda_setup(self, content: str) -> List[str]:
        """Verifica que la celda estándar de setup (git clone + os.chdir)
        esté presente en el MD.

        Args:
            content: Texto completo del MD de la unidad.

        Returns:
            Lista con un hallazgo si falta el patrón; vacía si está presente.
        """
        if "git clone" not in content or "os.chdir" not in content:
            return [
                "No se encontró la celda de setup estándar (git clone + "
                "os.chdir) en esta unidad."
            ]
        return []

    def _audit_invariantes_estructurales(
        self, python_blocks: List[str], content: str, md_path: Path
    ) -> List[str]:
        """Audita invariantes estructurales: consistencia de la celda de
        auto-evaluación (donde ya existe) e invariantes generales del
        Hilo de Oro aplicables a las 9 unidades.

        Args:
            python_blocks: Bloques de código Python extraídos del MD.
            content: Texto completo del MD de la unidad.
            md_path: Ruta del MD, usada para extraer el número de unidad.

        Returns:
            Lista concatenada de hallazgos de las 4 verificaciones.
        """
        hallazgos: List[str] = []
        hallazgos.extend(self._verifica_unit_number(python_blocks, md_path))
        hallazgos.extend(self._verifica_writefiles_con_definicion(python_blocks))
        hallazgos.extend(self._verifica_fences_balanceados(content))
        hallazgos.extend(self._verifica_celda_setup(content))
        return hallazgos

    def audit_unit(self, md_path: Path) -> Dict[str, Any]:
        """Audita una unidad del curso contra las 5 dimensiones de calidad.

        Args:
            md_path: Ruta al archivo Markdown de la unidad.

        Returns:
            Diccionario con la unidad auditada, hallazgos por dimensión
            ("latex", "pedagogico", "codigo", "curricular", "estructural")
            y el total.
        """
        content = md_path.read_text(encoding="utf-8")
        bloques = extract_fenced_blocks(content)
        python_blocks = [code for _, lang, code in bloques if lang == "python"]

        hallazgos = {
            "latex": self._audit_latex(content),
            "pedagogico": self._audit_pedagogico(bloques, content),
            "codigo": self._audit_codigo(python_blocks),
            "curricular": self._audit_curricular(md_path, content),
            "estructural": self._audit_invariantes_estructurales(
                python_blocks, content, md_path
            ),
        }
        total = sum(len(v) for v in hallazgos.values())

        return {
            "unidad": md_path.name,
            "hallazgos": hallazgos,
            "total_hallazgos": total,
        }

    def audit_all_units(self, course_dir: Path) -> str:
        """Audita todas las unidades del curso y genera un reporte Markdown consolidado.

        Args:
            course_dir: Directorio raíz del curso, donde viven los UNIDAD_*.md.

        Returns:
            Reporte consolidado en Markdown, con una sección por unidad auditada,
            ordenadas alfabéticamente por nombre de archivo.
        """
        md_files = sorted(Path(course_dir).glob("UNIDAD_*.md"))

        secciones = ["# Reporte de Auditoría de Contenido", ""]
        total_general = 0

        for md_path in md_files:
            resultado = self.audit_unit(md_path)
            total_general += resultado["total_hallazgos"]

            secciones.append(
                f"## {resultado['unidad']} ({resultado['total_hallazgos']} hallazgos)"
            )
            secciones.append("")

            for dimension, hallazgos in resultado["hallazgos"].items():
                if not hallazgos:
                    continue
                secciones.append(f"### {dimension.capitalize()}")
                for h in hallazgos:
                    secciones.append(f"- {h}")
                secciones.append("")

            if resultado["total_hallazgos"] == 0:
                secciones.append("- ✅ Sin hallazgos.")
                secciones.append("")

        secciones.insert(
            2, f"**Total de hallazgos en {len(md_files)} unidades: {total_general}**\n"
        )

        return "\n".join(secciones)


if __name__ == "__main__":
    auditor = ContentAuditorAgent()
    course_dir = Path(__file__).parent.parent.parent / "lecciones"
    print(auditor.audit_all_units(course_dir))
