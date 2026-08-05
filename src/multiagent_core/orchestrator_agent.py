"""
Agente Orquestador (OrchestratorAgent) - Lógica de Programación UCEMICH 🧩
==========================================================================

Coordina CodeAuditorAgent, FlowchartAgent, PseudocodeAgent y EvaluatorAgent
para producir un reporte pedagógico unificado en Markdown a partir del
código o pseudocódigo de un estudiante y el número de unidad correspondiente.
Clasifica automáticamente el tipo de entrada para evitar invocar agentes
que no aplican (p. ej. CodeAuditorAgent sobre pseudocódigo).
"""

from pathlib import Path
from typing import Optional

from .code_auditor_agent import CodeAuditorAgent
from .evaluator_agent import EvaluatorAgent
from .flowchart_agent import FlowchartAgent
from .pseudocode_agent import PseudocodeAgent

SKILL_METADATA = {
    "name": "orchestrator_agent",
    "description": "Coordina CodeAuditorAgent, FlowchartAgent/PseudocodeAgent y EvaluatorAgent en un reporte pedagógico único, con routing automático por tipo de entrada.",
    "version": "1.1.0",
    "input": "student_code: str, unit_number: int, test_file_path: Optional[Path]",
    "output": "str (reporte Markdown consolidado)",
    "requires_api_key": False,
}

PSEUDOCODE_KEYWORDS = ("INICIO", "FUNCIÓN", "FIN_SI", "FIN_FUNCIÓN", "MIENTRAS", "PARA")


class OrchestratorAgent:
    """Agente que coordina el consejo de agentes pedagógicos y consolida un reporte único."""

    def __init__(self) -> None:
        self.auditor = CodeAuditorAgent()
        self.flowchart_agent = FlowchartAgent()
        self.pseudocode_agent = PseudocodeAgent()
        self.evaluator = EvaluatorAgent()

    def _detect_input_type(self, student_code: str) -> str:
        """Clasifica la entrada del estudiante para decidir qué sub-agentes invocar.

        Args:
            student_code: Código o pseudocódigo entregado por el estudiante.

        Returns:
            "pseudocodigo" si contiene palabras clave de la sintaxis UCEMICH;
            "python_con_funciones" si es Python con al menos un `def`;
            "python_sin_funciones" en cualquier otro caso.
        """
        if any(kw in student_code.upper() for kw in PSEUDOCODE_KEYWORDS):
            return "pseudocodigo"
        if "def " in student_code:
            return "python_con_funciones"
        return "python_sin_funciones"

    def generate_pedagogical_report(
        self,
        student_code: str,
        unit_number: int,
        test_file_path: Optional[Path] = None,
    ) -> str:
        """Genera un reporte pedagógico unificado: auditoría + diagrama + calificación.

        Args:
            student_code: Código, pseudocódigo, o texto entregado por el estudiante.
            unit_number: Número de unidad del curso (0-8) a la que pertenece la entrega.
            test_file_path: Ruta opcional a un archivo de pruebas pytest asociado.

        Returns:
            Reporte consolidado en formato Markdown. El contenido varía según
            el tipo de entrada detectado: pseudocódigo omite auditoría de
            estilo/seguridad (no aplica) y usa PseudocodeAgent para el
            diagrama; Python sin funciones omite el diagrama de flujo.
        """
        tipo_entrada = self._detect_input_type(student_code)

        secciones = [f"# Reporte Pedagógico Unificado — Unidad {unit_number}", ""]

        if tipo_entrada != "pseudocodigo":
            auditoria = self.auditor.generate_report(student_code, test_file_path)
            secciones.extend([auditoria, ""])

        if tipo_entrada == "pseudocodigo":
            diagrama = self.pseudocode_agent.pseudocode_to_mermaid(student_code)
            secciones.extend(
                [
                    "## [DIAGRAMA] Diagrama de Flujo Autogenerado (desde pseudocódigo)",
                    "",
                    "```mermaid",
                    diagrama,
                    "```",
                    "",
                ]
            )
        elif tipo_entrada == "python_con_funciones":
            diagrama = self.flowchart_agent.build_mermaid_flowchart(student_code)
            secciones.extend(
                [
                    "## [DIAGRAMA] Diagrama de Flujo Autogenerado",
                    "",
                    "```mermaid",
                    diagrama,
                    "```",
                    "",
                ]
            )

        evaluacion = self.evaluator.evaluate(student_code, test_file_path)
        secciones.extend(
            [
                "## [CALIFICACIÓN] Evaluación contra Rúbrica Genérica",
                "",
                evaluacion["retroalimentacion"],
            ]
        )

        return "\n".join(secciones)


if __name__ == "__main__":
    orchestrator = OrchestratorAgent()
    codigo_ejemplo = """
def calcular_volumen_esfera(radio_nm):
    if radio_nm <= 0:
        return -1
    else:
        volumen = (4 / 3) * 3.14159 * radio_nm ** 3
        return volumen
"""
    print(orchestrator.generate_pedagogical_report(codigo_ejemplo, unit_number=2))
