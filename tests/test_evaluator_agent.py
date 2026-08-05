"""Tests TDD para EvaluatorAgent (califica contra RUBRICA_GENERAL.md)."""

from pathlib import Path

import pytest

from src.multiagent_core.evaluator_agent import EvaluatorAgent

CODIGO_RIESGOSO = """
def calcularEnergia(masa, VelocidadEfectiva):
    API_KEY = "sk-proj-1234567890abcdefghijklmnop"
    eval("print('calculando')")
    energia = 0.5 * masa * (VelocidadEfectiva ** 2)
    return energia
"""

CODIGO_LIMPIO = """
def calcular_energia_cinetica(masa_kg: float, velocidad_m_s: float) -> float:
    \"\"\"Calcula la energía cinética de un cuerpo.

    Args:
        masa_kg: Masa del cuerpo en kilogramos.
        velocidad_m_s: Velocidad del cuerpo en metros por segundo.

    Returns:
        Energía cinética en Joules.
    \"\"\"
    if masa_kg <= 0:
        raise ValueError("La masa debe ser positiva")
    return 0.5 * masa_kg * (velocidad_m_s ** 2)
"""


@pytest.fixture
def evaluator() -> EvaluatorAgent:
    return EvaluatorAgent()


class TestEvaluate:
    def test_retorna_diccionario_con_cuatro_criterios(self, evaluator: EvaluatorAgent):
        resultado = evaluator.evaluate(CODIGO_LIMPIO)
        assert set(resultado["criterios"].keys()) == {
            "Corrección lógica",
            "Proceso (Hilo de Oro)",
            "Calidad de código",
            "Pruebas (pytest)",
        }

    def test_cada_criterio_tiene_nivel_y_retroalimentacion(self, evaluator: EvaluatorAgent):
        resultado = evaluator.evaluate(CODIGO_LIMPIO)
        for criterio in resultado["criterios"].values():
            assert criterio["nivel"] in (
                "Insuficiente",
                "En desarrollo",
                "Competente",
                "Sobresaliente",
            )
            assert isinstance(criterio["retroalimentacion"], str)
            assert criterio["retroalimentacion"]

    def test_codigo_riesgoso_recibe_nivel_bajo_en_calidad_de_codigo(
        self, evaluator: EvaluatorAgent
    ):
        resultado = evaluator.evaluate(CODIGO_RIESGOSO)
        assert resultado["criterios"]["Calidad de código"]["nivel"] in (
            "Insuficiente",
            "En desarrollo",
        )

    def test_codigo_limpio_recibe_nivel_alto_en_calidad_de_codigo(
        self, evaluator: EvaluatorAgent
    ):
        resultado = evaluator.evaluate(CODIGO_LIMPIO)
        assert resultado["criterios"]["Calidad de código"]["nivel"] in (
            "Competente",
            "Sobresaliente",
        )

    def test_calificacion_final_es_promedio_numerico_entre_0_y_100(
        self, evaluator: EvaluatorAgent
    ):
        resultado = evaluator.evaluate(CODIGO_LIMPIO)
        assert 0 <= resultado["calificacion_final"] <= 100

    def test_sin_test_file_penaliza_criterio_de_pruebas(self, evaluator: EvaluatorAgent):
        resultado = evaluator.evaluate(CODIGO_LIMPIO, test_file_path=None)
        assert resultado["criterios"]["Pruebas (pytest)"]["nivel"] == "Insuficiente"

    def test_con_test_file_que_pasa_mejora_criterio_de_pruebas(
        self, evaluator: EvaluatorAgent, tmp_path: Path
    ):
        test_file = tmp_path / "test_dummy.py"
        test_file.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
        resultado = evaluator.evaluate(CODIGO_LIMPIO, test_file_path=test_file)
        assert resultado["criterios"]["Pruebas (pytest)"]["nivel"] != "Insuficiente"

    def test_retroalimentacion_general_es_string_no_vacio(self, evaluator: EvaluatorAgent):
        resultado = evaluator.evaluate(CODIGO_LIMPIO)
        assert isinstance(resultado["retroalimentacion"], str)
        assert len(resultado["retroalimentacion"]) > 0
