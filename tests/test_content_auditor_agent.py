"""Tests TDD para ContentAuditorAgent (audita las 9 unidades del curso)."""

from pathlib import Path

import pytest

from src.multiagent_core.content_auditor_agent import ContentAuditorAgent


@pytest.fixture
def auditor() -> ContentAuditorAgent:
    return ContentAuditorAgent()


class TestAuditUnitEstructura:
    def test_retorna_diccionario_con_las_4_dimensiones(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_1_TEST.md"
        md_path.write_text(
            "# UNIDAD 1: Test\n**Duración:** 1 semana\n\n## Objetivos\nTexto.\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)

        assert resultado["unidad"] == "UNIDAD_1_TEST.md"
        assert set(resultado["hallazgos"].keys()) == {
            "latex",
            "pedagogico",
            "codigo",
            "curricular",
        }
        assert isinstance(resultado["total_hallazgos"], int)


class TestDimensionLatex:
    def test_detecta_delimitadores_dollar_desbalanceados(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\nFormula sin cerrar: $x = y + z\n", encoding="utf-8"
        )
        resultado = auditor.audit_unit(md_path)
        assert len(resultado["hallazgos"]["latex"]) > 0

    def test_detecta_comando_latex_mal_formado_delta_pegado(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n$$\\DeltaG = 5$$\n", encoding="utf-8"
        )
        resultado = auditor.audit_unit(md_path)
        assert any("DeltaG" in h or "\\Delta" in h for h in resultado["hallazgos"]["latex"])

    def test_no_marca_diagrama_ascii_con_simbolo_griego_como_error_latex(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n```\n"
            "Energía ΔG\n"
            "   ^\n"
            "   |   * * *\n"
            "---+-------> Radio r\n"
            "```\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert resultado["hallazgos"]["latex"] == []

    def test_formula_bien_formada_no_genera_hallazgos(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\nLa energía libre es $$\\Delta G = \\Delta H - T \\Delta S$$.\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert resultado["hallazgos"]["latex"] == []


class TestDimensionCodigo:
    def test_detecta_funcion_sin_docstring(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n```python\ndef calcular(x):\n    return x * 2\n```\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert any("docstring" in h.lower() for h in resultado["hallazgos"]["codigo"])

    def test_detecta_funcion_sin_type_hints(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            '# Test\n\n```python\ndef calcular(x):\n    """Docstring."""\n    return x * 2\n```\n',
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert any("type hint" in h.lower() for h in resultado["hallazgos"]["codigo"])

    def test_funcion_bien_documentada_no_genera_hallazgos_de_docstring_ni_tipos(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            '# Test\n\n```python\n'
            'def calcular(x: float) -> float:\n'
            '    """Duplica un valor.\n\n'
            '    Args:\n'
            '        x: Valor de entrada.\n\n'
            '    Returns:\n'
            '        El valor duplicado.\n'
            '    """\n'
            '    return x * 2\n```\n',
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert not any(
            "docstring" in h.lower() or "type hint" in h.lower()
            for h in resultado["hallazgos"]["codigo"]
        )

    def test_reutiliza_code_auditor_agent_para_detectar_eval(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            '# Test\n\n```python\ndef f():\n    """Doc."""\n    eval("1+1")\n```\n',
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert any("eval" in h.lower() for h in resultado["hallazgos"]["codigo"])


class TestDimensionPedagogico:
    def test_detecta_ausencia_de_ciclo_pseudocodigo_mermaid_python(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            '# Test\n\n```python\ndef f(x: int) -> int:\n    """Doc."""\n    return x\n```\n',
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert any(
            "hilo de oro" in h.lower() or "pseudoc" in h.lower()
            for h in resultado["hallazgos"]["pedagogico"]
        )

    def test_no_marca_hallazgo_si_hay_ciclo_completo(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            '# Test\n\n'
            '```pseudocodigo\nFUNCIÓN f(x)\n    RETORNAR x\nFIN_FUNCIÓN\n```\n\n'
            '```mermaid\ngraph TD\n    a --> b\n```\n\n'
            '```python\ndef f(x: int) -> int:\n    """Doc."""\n    return x\n```\n\n'
            '```pytest\ndef test_f():\n    assert f(1) == 1\n```\n',
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert not any(
            "hilo de oro" in h.lower() for h in resultado["hallazgos"]["pedagogico"]
        )

    def test_detecta_ausencia_de_analogia_didactica(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text("# Test\n\nSolo texto plano sin analogías.\n", encoding="utf-8")
        resultado = auditor.audit_unit(md_path)
        assert any("analog" in h.lower() for h in resultado["hallazgos"]["pedagogico"])

    def test_no_marca_hallazgo_de_analogia_si_existe(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n### 💡 Analogía Didáctica: Ejemplo\n\nTexto de la analogía.\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert not any("analog" in h.lower() for h in resultado["hallazgos"]["pedagogico"])
