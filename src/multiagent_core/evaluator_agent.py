"""
Agente Evaluador (EvaluatorAgent) - Lógica de Programación UCEMICH 📊
=====================================================================

Califica código de estudiantes contra la Rúbrica Genérica de Laboratorio
(4 criterios × 4 niveles) definida en RUBRICA_GENERAL.md, reutilizando
CodeAuditorAgent para el análisis de estilo, seguridad y pruebas.
"""

import ast
from pathlib import Path
from typing import Any, Dict, Optional

from .code_auditor_agent import CodeAuditorAgent

NIVELES = ("Insuficiente", "En desarrollo", "Competente", "Sobresaliente")
PUNTAJE_POR_NIVEL = {
    "Insuficiente": 45.0,
    "En desarrollo": 67.0,
    "Competente": 82.0,
    "Sobresaliente": 95.0,
}


class EvaluatorAgent:
    """Agente que evalúa código de estudiantes contra la rúbrica genérica del curso."""

    def __init__(self):
        self.auditor = CodeAuditorAgent()

    def _evaluar_correccion_logica(self, student_code: str) -> Dict[str, str]:
        """Califica si el código compila (nivel mínimo de corrección lógica)."""
        try:
            ast.parse(student_code)
        except SyntaxError as e:
            return {
                "nivel": "Insuficiente",
                "retroalimentacion": f"El código no compila: {e}",
            }
        return {
            "nivel": "Competente",
            "retroalimentacion": "El código es sintácticamente válido. Verifica manualmente casos borde.",
        }

    def _evaluar_proceso(self, student_code: str) -> Dict[str, str]:
        """Evalúa el criterio de Hilo de Oro (pseudocódigo → Mermaid → Python → pytest).

        No verificable automáticamente a partir del código fuente solo; siempre
        retorna "En desarrollo" con una nota para el estudiante.
        """
        return {
            "nivel": "En desarrollo",
            "retroalimentacion": (
                "No es posible verificar automáticamente el pseudocódigo ni el diagrama previos; "
                "documenta el flujo Pseudocódigo → Mermaid → Python → pytest en tu entrega."
            ),
        }

    def _evaluar_calidad_codigo(self, student_code: str) -> Dict[str, str]:
        """Califica estilo y seguridad reutilizando CodeAuditorAgent."""
        style_issues = self.auditor.audit_style(student_code)
        security_issues = self.auditor.audit_security(student_code)
        total_issues = len(style_issues) + len(security_issues)

        if security_issues:
            nivel = "Insuficiente"
        elif total_issues >= 2:
            nivel = "En desarrollo"
        elif total_issues == 1:
            nivel = "Competente"
        else:
            nivel = "Sobresaliente"

        detalle = style_issues + security_issues
        retro = (
            "Hallazgos: " + "; ".join(detalle)
            if detalle
            else "Sin hallazgos de estilo ni seguridad."
        )
        return {"nivel": nivel, "retroalimentacion": retro}

    def _evaluar_pruebas(self, test_file_path: Optional[Path]) -> Dict[str, str]:
        """Califica el criterio de pruebas ejecutando pytest sobre test_file_path si existe."""
        if test_file_path is None or not Path(test_file_path).exists():
            return {
                "nivel": "Insuficiente",
                "retroalimentacion": "No se proporcionó un archivo de pruebas pytest.",
            }

        resultado = self.auditor.run_pytest(Path(test_file_path))
        if resultado["passed"]:
            return {
                "nivel": "Competente",
                "retroalimentacion": "Las pruebas unitarias proporcionadas pasan correctamente.",
            }
        return {
            "nivel": "En desarrollo",
            "retroalimentacion": f"Las pruebas fallan:\n{resultado['output']}",
        }

    def evaluate(
        self, student_code: str, test_file_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Evalúa el código del estudiante contra los 4 criterios de la rúbrica genérica.

        Args:
            student_code: Código fuente Python entregado por el estudiante.
            test_file_path: Ruta opcional a un archivo de pruebas pytest asociado.

        Returns:
            Diccionario con los 4 criterios calificados, la calificación final
            promedio (0-100) y una retroalimentación general consolidada.
        """
        criterios = {
            "Corrección lógica": self._evaluar_correccion_logica(student_code),
            "Proceso (Hilo de Oro)": self._evaluar_proceso(student_code),
            "Calidad de código": self._evaluar_calidad_codigo(student_code),
            "Pruebas (pytest)": self._evaluar_pruebas(test_file_path),
        }

        puntajes = [PUNTAJE_POR_NIVEL[c["nivel"]] for c in criterios.values()]
        calificacion_final = round(sum(puntajes) / len(puntajes), 2)

        resumen = "\n".join(
            f"- {nombre}: {c['nivel']} — {c['retroalimentacion']}"
            for nombre, c in criterios.items()
        )
        retroalimentacion = f"Calificación final: {calificacion_final}/100\n\n{resumen}"

        return {
            "criterios": criterios,
            "calificacion_final": calificacion_final,
            "retroalimentacion": retroalimentacion,
        }


if __name__ == "__main__":
    evaluator = EvaluatorAgent()
    codigo_ejemplo = """
def calcularArea(radio):
    eval("print('riesgo')")
    return 3.14159 * radio ** 2
"""
    print(evaluator.evaluate(codigo_ejemplo)["retroalimentacion"])
