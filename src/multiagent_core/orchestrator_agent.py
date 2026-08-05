"""
Agente Orquestador (OrchestratorAgent) - Lógica de Programación UCEMICH 🧩
==========================================================================

Coordina CodeAuditorAgent, FlowchartAgent y EvaluatorAgent para producir
un reporte pedagógico unificado en Markdown a partir del código de un
estudiante y el número de unidad correspondiente.
"""

from pathlib import Path
from typing import Optional

from .code_auditor_agent import CodeAuditorAgent
from .evaluator_agent import EvaluatorAgent
from .flowchart_agent import FlowchartAgent


class OrchestratorAgent:
    """Agente que coordina el consejo de agentes pedagógicos y consolida un reporte único."""

    def __init__(self):
        self.auditor = CodeAuditorAgent()
        self.flowchart_agent = FlowchartAgent()
        self.evaluator = EvaluatorAgent()

    def generate_pedagogical_report(
        self,
        student_code: str,
        unit_number: int,
        test_file_path: Optional[Path] = None,
    ) -> str:
        """Genera un reporte pedagógico unificado: auditoría + diagrama + calificación.

        Args:
            student_code: Código fuente Python entregado por el estudiante.
            unit_number: Número de unidad del curso (0-8) a la que pertenece la entrega.
            test_file_path: Ruta opcional a un archivo de pruebas pytest asociado.

        Returns:
            Reporte consolidado en formato Markdown.
        """
        auditoria = self.auditor.generate_report(student_code, test_file_path)
        diagrama = self.flowchart_agent.build_mermaid_flowchart(student_code)
        evaluacion = self.evaluator.evaluate(student_code, test_file_path)

        secciones = [
            f"# Reporte Pedagógico Unificado — Unidad {unit_number}",
            "",
            auditoria,
            "",
            "## [DIAGRAMA] Diagrama de Flujo Autogenerado",
            "",
            "```mermaid",
            diagrama,
            "```",
            "",
            "## [CALIFICACIÓN] Evaluación contra Rúbrica Genérica",
            "",
            evaluacion["retroalimentacion"],
        ]
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
