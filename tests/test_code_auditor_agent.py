"""Tests de caracterización para CodeAuditorAgent."""

from pathlib import Path

import pytest

from src.multiagent_core.code_auditor_agent import CodeAuditorAgent


@pytest.fixture
def auditor() -> CodeAuditorAgent:
    return CodeAuditorAgent()


class TestAuditStyle:
    def test_reporta_linea_que_excede_79_caracteres(self, auditor: CodeAuditorAgent):
        codigo = "x = " + "1 + " * 30 + "1"
        issues = auditor.audit_style(codigo)
        assert any("79 caracteres" in issue for issue in issues)

    def test_no_reporta_linea_larga_si_contiene_url(self, auditor: CodeAuditorAgent):
        codigo = "# ver https://ejemplo.com/" + "a" * 70
        issues = auditor.audit_style(codigo)
        assert not any("79 caracteres" in issue for issue in issues)

    def test_reporta_variable_en_camel_case(self, auditor: CodeAuditorAgent):
        """Caracterización: la heurística solo dispara con minúscula inicial (camelCase), no PascalCase."""
        issues = auditor.audit_style("velocidadEfectiva = 10")
        assert any("CamelCase" in issue for issue in issues)

    def test_no_reporta_nada_para_codigo_limpio(self, auditor: CodeAuditorAgent):
        issues = auditor.audit_style("radio_nm = 5.2\nvolumen = radio_nm ** 3")
        assert issues == []


class TestAuditSecurity:
    def test_detecta_uso_de_eval(self, auditor: CodeAuditorAgent):
        issues = auditor.audit_security("eval('print(1)')")
        assert any("eval" in issue for issue in issues)

    def test_detecta_uso_de_exec(self, auditor: CodeAuditorAgent):
        issues = auditor.audit_security("exec('x = 1')")
        assert any("exec" in issue for issue in issues)

    def test_detecta_api_key_expuesta_en_texto_plano(self, auditor: CodeAuditorAgent):
        codigo = 'API_KEY = "sk-proj-1234567890abcdefghij"'
        issues = auditor.audit_security(codigo)
        assert any("credencial" in issue.lower() or "api key" in issue.lower() for issue in issues)

    def test_no_reporta_falso_positivo_con_os_environ(self, auditor: CodeAuditorAgent):
        codigo = 'api_key = os.environ["MI_API_KEY_LARGA_1234567890"]'
        issues = auditor.audit_security(codigo)
        assert issues == []

    def test_no_detecta_division_sin_proteccion_contra_cero(self, auditor: CodeAuditorAgent):
        """Caracterización: el bloque de detección de división por cero es un no-op actualmente."""
        issues = auditor.audit_security("resultado = a / b")
        assert issues == []

    def test_retorna_error_controlado_con_sintaxis_invalida(self, auditor: CodeAuditorAgent):
        issues = auditor.audit_security("def foo(:\n    pass")
        assert len(issues) == 1
        assert "sintaxis" in issues[0].lower()


class TestRunPytest:
    def test_reporta_passed_true_cuando_pruebas_pasan(
        self, auditor: CodeAuditorAgent, tmp_path: Path
    ):
        test_file = tmp_path / "test_dummy.py"
        test_file.write_text("def test_siempre_pasa():\n    assert True\n", encoding="utf-8")
        result = auditor.run_pytest(test_file)
        assert result["passed"] is True

    def test_reporta_passed_false_cuando_pruebas_fallan(
        self, auditor: CodeAuditorAgent, tmp_path: Path
    ):
        test_file = tmp_path / "test_dummy_fail.py"
        test_file.write_text("def test_siempre_falla():\n    assert False\n", encoding="utf-8")
        result = auditor.run_pytest(test_file)
        assert result["passed"] is False
        assert result["output"]

    def test_invoca_pytest_como_modulo_del_interprete_actual(
        self, auditor: CodeAuditorAgent, tmp_path: Path, mocker
    ):
        """Regresión: debe usar [sys.executable, '-m', 'pytest', ...], no ['pytest', ...] —
        el binario 'pytest' puede no estar en el PATH del kernel en Colab aunque el
        paquete sí esté instalado (mismo tipo de brecha vista con ipytest esta sesión)."""
        import sys

        test_file = tmp_path / "test_dummy.py"
        test_file.write_text("def test_siempre_pasa():\n    assert True\n", encoding="utf-8")

        mock_run = mocker.patch("src.multiagent_core.code_auditor_agent.subprocess.run")
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "1 passed"
        mock_run.return_value.stderr = ""

        auditor.run_pytest(test_file)

        args_llamada = mock_run.call_args[0][0]
        assert args_llamada[0] == sys.executable
        assert args_llamada[1] == "-m"
        assert args_llamada[2] == "pytest"

    def test_retorna_passed_false_sin_lanzar_excepcion_con_cero_tests_recolectados(
        self, auditor: CodeAuditorAgent, tmp_path: Path
    ):
        """Regresión: un archivo de tests sin ningún test recolectable (exit code 5 de
        pytest) no debe lanzar excepción — debe comportarse igual que un fallo normal."""
        test_file = tmp_path / "test_vacio.py"
        test_file.write_text("# sin tests aquí\n", encoding="utf-8")

        result = auditor.run_pytest(test_file)

        assert result["passed"] is False


class TestGenerateReport:
    def test_reporte_sin_test_file_incluye_estilo_y_seguridad(self, auditor: CodeAuditorAgent):
        reporte = auditor.generate_report("radio_nm = 5.2")
        assert "[ESTILO]" in reporte
        assert "[SEGURIDAD]" in reporte
        assert "[TESTS]" not in reporte

    def test_reporte_con_test_file_incluye_seccion_tests(
        self, auditor: CodeAuditorAgent, tmp_path: Path
    ):
        test_file = tmp_path / "test_dummy.py"
        test_file.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
        reporte = auditor.generate_report("radio_nm = 5.2", test_file_path=test_file)
        assert "[TESTS]" in reporte

    def test_reporte_marca_ok_si_no_hay_hallazgos(self, auditor: CodeAuditorAgent):
        reporte = auditor.generate_report("radio_nm = 5.2")
        assert "[OK]" in reporte
