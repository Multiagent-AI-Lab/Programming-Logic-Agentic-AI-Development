"""Tests TDD para OrchestratorAgent (coordina CodeAuditorAgent + FlowchartAgent + EvaluatorAgent)."""

import pytest

from src.multiagent_core.orchestrator_agent import OrchestratorAgent

CODIGO_EJEMPLO = """
def calcular_volumen_esfera(radio_nm):
    if radio_nm <= 0:
        return -1
    else:
        volumen = (4 / 3) * 3.14159 * radio_nm ** 3
        return volumen
"""

CODIGO_PSEUDOCODIGO = """
FUNCIÓN calcular_volumen_esfera(radio_nm)
    SI radio_nm <= 0 ENTONCES
        RETORNAR -1
    FIN_SI
    RETORNAR (4 / 3) * 3.14159 * radio_nm ** 3
FIN_FUNCIÓN
"""

CODIGO_SIN_FUNCIONES = "x = 1 + 1\nprint(x)"


@pytest.fixture
def orchestrator() -> OrchestratorAgent:
    return OrchestratorAgent()


class TestDetectInputType:
    def test_detecta_pseudocodigo_por_palabras_clave_ucemich(
        self, orchestrator: OrchestratorAgent
    ):
        assert orchestrator._detect_input_type(CODIGO_PSEUDOCODIGO) == "pseudocodigo"

    def test_detecta_python_con_funciones(self, orchestrator: OrchestratorAgent):
        assert orchestrator._detect_input_type(CODIGO_EJEMPLO) == "python_con_funciones"

    def test_detecta_python_sin_funciones(self, orchestrator: OrchestratorAgent):
        assert (
            orchestrator._detect_input_type(CODIGO_SIN_FUNCIONES)
            == "python_sin_funciones"
        )


class TestRoutingEnReporte:
    def test_pseudocodigo_usa_pseudocode_agent_en_vez_de_flowchart_agent(
        self, orchestrator: OrchestratorAgent
    ):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_PSEUDOCODIGO, unit_number=2
        )
        assert "```mermaid" in reporte
        assert "graph TD" in reporte
        assert "[ESTILO]" not in reporte
        assert "[SEGURIDAD]" not in reporte

    def test_python_sin_funciones_omite_diagrama_mermaid(
        self, orchestrator: OrchestratorAgent
    ):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_SIN_FUNCIONES, unit_number=3
        )
        assert "[DIAGRAMA]" not in reporte


class TestGeneratePedagogicalReport:
    def test_retorna_string_markdown(self, orchestrator: OrchestratorAgent):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_EJEMPLO, unit_number=2
        )
        assert isinstance(reporte, str)
        assert reporte.startswith("#")

    def test_incluye_seccion_de_auditoria(self, orchestrator: OrchestratorAgent):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_EJEMPLO, unit_number=2
        )
        assert "[ESTILO]" in reporte or "Estilo" in reporte
        assert "[SEGURIDAD]" in reporte or "Seguridad" in reporte

    def test_incluye_diagrama_mermaid(self, orchestrator: OrchestratorAgent):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_EJEMPLO, unit_number=2
        )
        assert "```mermaid" in reporte
        assert "graph TD" in reporte

    def test_incluye_calificacion(self, orchestrator: OrchestratorAgent):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_EJEMPLO, unit_number=2
        )
        assert "Calificación" in reporte or "calificacion" in reporte.lower()

    def test_incluye_numero_de_unidad(self, orchestrator: OrchestratorAgent):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_EJEMPLO, unit_number=5
        )
        assert "Unidad 5" in reporte

    def test_codigo_sin_funcion_no_rompe_el_reporte(
        self, orchestrator: OrchestratorAgent
    ):
        reporte = orchestrator.generate_pedagogical_report("x = 1 + 1", unit_number=3)
        assert isinstance(reporte, str)
        assert len(reporte) > 0
