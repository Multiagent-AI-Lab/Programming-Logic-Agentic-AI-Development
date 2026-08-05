"""Tests TDD para PseudocodeAgent (convención UCEMICH 2026)."""

import pytest

from src.multiagent_core.pseudocode_agent import PseudocodeAgent


@pytest.fixture
def agent() -> PseudocodeAgent:
    return PseudocodeAgent()


class TestPseudocodeToMermaid:
    def test_traduce_si_sino_a_diagrama_con_dos_ramas(self, agent: PseudocodeAgent):
        pseudocodigo = """
SI radio_nm <= 0 ENTONCES
    ESCRIBIR "Error: el radio debe ser positivo"
SINO
    volumen <- (4 / 3) * 3.14159 * radio_nm ** 3
FIN_SI
"""
        resultado = agent.pseudocode_to_mermaid(pseudocodigo)
        assert "graph TD" in resultado
        assert "-- Sí -->" in resultado
        assert "-- No -->" in resultado

    def test_traduce_para_a_nodo_de_iteracion(self, agent: PseudocodeAgent):
        pseudocodigo = """
PARA i DESDE 1 HASTA 10 HACER
    ESCRIBIR i
FIN_PARA
"""
        resultado = agent.pseudocode_to_mermaid(pseudocodigo)
        assert "graph TD" in resultado
        assert "PARA" in resultado or "Iterar" in resultado

    def test_traduce_mientras_a_nodo_de_iteracion(self, agent: PseudocodeAgent):
        pseudocodigo = """
MIENTRAS temperatura > 298 HACER
    temperatura <- temperatura - 5
FIN_MIENTRAS
"""
        resultado = agent.pseudocode_to_mermaid(pseudocodigo)
        assert "graph TD" in resultado
        assert "MIENTRAS" in resultado or "Iterar" in resultado

    def test_pseudocodigo_vacio_retorna_diagrama_minimo(self, agent: PseudocodeAgent):
        resultado = agent.pseudocode_to_mermaid("")
        assert "graph TD" in resultado


class TestPythonToPseudocode:
    def test_traduce_funcion_simple_con_if_else(self, agent: PseudocodeAgent):
        codigo = """
def calcular_volumen_esfera(radio_nm):
    if radio_nm <= 0:
        return -1
    else:
        volumen = (4 / 3) * 3.14159 * radio_nm ** 3
        return volumen
"""
        resultado = agent.python_to_pseudocode(codigo)
        assert "FUNCIÓN calcular_volumen_esfera" in resultado
        assert "SI" in resultado
        assert "SINO" in resultado
        assert "FIN_SI" in resultado
        assert "RETORNAR" in resultado
        assert "FIN_FUNCIÓN" in resultado

    def test_traduce_asignacion_con_flecha(self, agent: PseudocodeAgent):
        codigo = """
def doblar(x):
    resultado = x * 2
    return resultado
"""
        resultado = agent.python_to_pseudocode(codigo)
        assert "resultado <- x * 2" in resultado

    def test_sin_funcion_retorna_mensaje_de_error(self, agent: PseudocodeAgent):
        resultado = agent.python_to_pseudocode("x = 1 + 1")
        assert "No se encontró una definición de función" in resultado


class TestPseudocodeToPythonSkeleton:
    def test_genera_firma_de_funcion_con_docstring(self, agent: PseudocodeAgent):
        pseudocodigo = """
FUNCIÓN calcular_volumen_esfera(radio_nm)
    SI radio_nm <= 0 ENTONCES
        RETORNAR -1
    SINO
        volumen <- (4 / 3) * 3.14159 * radio_nm ** 3
        RETORNAR volumen
    FIN_SI
FIN_FUNCIÓN
"""
        resultado = agent.pseudocode_to_python_skeleton(pseudocodigo)
        assert resultado.startswith("def calcular_volumen_esfera(radio_nm")
        assert '"""' in resultado
        assert "pass" in resultado

    def test_esqueleto_no_incluye_logica_de_negocio(self, agent: PseudocodeAgent):
        pseudocodigo = """
FUNCIÓN sumar(a, b)
    resultado <- a + b
    RETORNAR resultado
FIN_FUNCIÓN
"""
        resultado = agent.pseudocode_to_python_skeleton(pseudocodigo)
        assert "a + b" not in resultado

    def test_sin_funcion_retorna_mensaje_de_error(self, agent: PseudocodeAgent):
        resultado = agent.pseudocode_to_python_skeleton("ESCRIBIR \"hola\"")
        assert "No se encontró" in resultado
