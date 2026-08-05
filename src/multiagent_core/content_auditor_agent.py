"""
Agente Auditor de Contenido (ContentAuditorAgent) - Lógica de Programación UCEMICH 🔍
======================================================================================

Audita las 9 unidades del curso (contenido escrito por el mantenedor, no por
estudiantes) contra 4 dimensiones de calidad: rigor matemático/LaTeX,
coherencia pedagógica (Hilo de Oro), calidad de código de ejemplo, y
cumplimiento curricular contra el programa oficial. Heurístico puro, sin LLM.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List

from .code_auditor_agent import CodeAuditorAgent
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


class ContentAuditorAgent:
    """Agente que audita el contenido pedagógico de las unidades del curso."""

    def __init__(self) -> None:
        self.code_auditor = CodeAuditorAgent()

    def _audit_latex(self, content: str) -> List[str]:
        """Detecta delimitadores LaTeX desbalanceados y comandos mal formados.

        Args:
            content: Texto completo del MD de la unidad.

        Returns:
            Lista de descripciones de hallazgos; vacía si no hay problemas.
        """
        hallazgos: List[str] = []

        dollar_count = content.count("$") - 2 * content.count("$$")
        if dollar_count % 2 != 0:
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

        Args:
            python_blocks: Lista de bloques de código Python extraídos del MD.

        Returns:
            Lista de descripciones de hallazgos; vacía si no hay problemas.
        """
        hallazgos: List[str] = []

        for code in python_blocks:
            hallazgos.extend(self.code_auditor.audit_style(code))
            hallazgos.extend(self.code_auditor.audit_security(code))

            try:
                tree = ast.parse(code)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                if ast.get_docstring(node) is None:
                    hallazgos.append(
                        f"Función '{node.name}' sin docstring en el código de ejemplo."
                    )
                args_sin_tipo = [a.arg for a in node.args.args if a.annotation is None]
                if args_sin_tipo or node.returns is None:
                    hallazgos.append(
                        f"Función '{node.name}' sin type hints completos "
                        f"(argumentos sin tipo: {args_sin_tipo or 'ninguno'}, "
                        f"retorno anotado: {node.returns is not None})."
                    )

        return hallazgos

    def _audit_pedagogico(self, bloques: List[tuple], content: str) -> List[str]:
        """Verifica coherencia pedagógica: Hilo de Oro y presencia de analogías.

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

        if (
            "### 💡 Analogía" not in content
            and "### 💡 ANALOGÍA" not in content.upper()
        ):
            hallazgos.append(
                "No se encontró ninguna sección de Analogía Didáctica "
                "(patrón '### 💡 Analogía') en esta unidad."
            )

        return hallazgos

    def audit_unit(self, md_path: Path) -> Dict[str, Any]:
        """Audita una unidad del curso contra las 4 dimensiones de calidad.

        Args:
            md_path: Ruta al archivo Markdown de la unidad.

        Returns:
            Diccionario con la unidad auditada, hallazgos por dimensión
            ("latex", "pedagogico", "codigo", "curricular") y el total.
        """
        content = md_path.read_text(encoding="utf-8")
        bloques = extract_fenced_blocks(content)
        python_blocks = [code for _, lang, code in bloques if lang == "python"]

        hallazgos = {
            "latex": self._audit_latex(content),
            "pedagogico": self._audit_pedagogico(bloques, content),
            "codigo": self._audit_codigo(python_blocks),
            "curricular": [],
        }
        total = sum(len(v) for v in hallazgos.values())

        return {
            "unidad": md_path.name,
            "hallazgos": hallazgos,
            "total_hallazgos": total,
        }
