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
        md_path.write_text("# Test\n\n$$\\DeltaG = 5$$\n", encoding="utf-8")
        resultado = auditor.audit_unit(md_path)
        assert any(
            "DeltaG" in h or "\\Delta" in h for h in resultado["hallazgos"]["latex"]
        )

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
            "# Test\n\n```python\n"
            "def calcular(x: float) -> float:\n"
            '    """Duplica un valor.\n\n'
            "    Args:\n"
            "        x: Valor de entrada.\n\n"
            "    Returns:\n"
            "        El valor duplicado.\n"
            '    """\n'
            "    return x * 2\n```\n",
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

    def test_no_marca_longitud_de_linea_en_codigo_de_ejemplo(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        linea_larga = (
            "x = " + "1 + " * 30 + "1  # comentario explicativo largo en español"
        )
        md_path.write_text(
            f'# Test\n\n```python\ndef f(x: int) -> int:\n    """Doc."""\n    {linea_larga}\n    return x\n```\n',
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert not any("79 caracteres" in h for h in resultado["hallazgos"]["codigo"])

    def test_no_exige_docstring_ni_type_hints_en_funciones_test(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n```python\ndef test_calcula_volumen():\n    assert calcular(1) == 2\n```\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert not any(
            "docstring" in h.lower() or "type hint" in h.lower()
            for h in resultado["hallazgos"]["codigo"]
        )

    def test_no_marca_error_de_sintaxis_en_celda_magica_de_ipython(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n```python\nimport sys\nif 'google.colab' in sys.modules:\n"
            "    %pip install -q rich\n```\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert not any(
            "sintaxis" in h.lower() for h in resultado["hallazgos"]["codigo"]
        )

    def test_no_marca_self_ni_cls_como_argumento_sin_tipo(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n```python\nclass Ejemplo:\n"
            '    def metodo(self) -> None:\n        """Doc."""\n        pass\n\n'
            '    @classmethod\n    def crear(cls) -> "Ejemplo":\n'
            '        """Doc."""\n        return cls()\n```\n',
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert not any(
            "type hint" in h.lower() for h in resultado["hallazgos"]["codigo"]
        )


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
            "# Test\n\n"
            "```pseudocodigo\nFUNCIÓN f(x)\n    RETORNAR x\nFIN_FUNCIÓN\n```\n\n"
            "```mermaid\ngraph TD\n    a --> b\n```\n\n"
            '```python\ndef f(x: int) -> int:\n    """Doc."""\n    return x\n```\n\n'
            "```pytest\ndef test_f():\n    assert f(1) == 1\n```\n",
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
        md_path.write_text(
            "# Test\n\nSolo texto plano sin analogías.\n", encoding="utf-8"
        )
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
        assert not any(
            "analog" in h.lower() for h in resultado["hallazgos"]["pedagogico"]
        )


class TestDimensionCurricular:
    def test_parse_programa_oficial_extrae_subtemas_por_unidad(self):
        from src.multiagent_core.content_auditor_agent import _parse_programa_oficial

        programa_path = (
            Path(__file__).parent.parent
            / "docs"
            / "legado"
            / "planeacion_2023_2024"
            / "Programa_de_Asignatura_Logica_Programacion_IA_v2_extracted.txt"
        )
        mapeo = _parse_programa_oficial(programa_path)

        assert 6 in mapeo
        assert any("lambda" in s.lower() for s in mapeo[6]["subtemas"])
        assert "Semanas 11-13" in mapeo[6]["semanas"] or "11-13" in mapeo[6]["semanas"]

    def test_detecta_subtema_faltante(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "UNIDAD_6_MODULARIDAD_IA_MCP.md"
        md_path.write_text(
            "# UNIDAD 6\n**Duración:** 1 semana\n\nSolo texto genérico sin cubrir "
            "los subtemas oficiales del programa.\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert len(resultado["hallazgos"]["curricular"]) > 0

    def test_no_marca_hallazgo_si_unidad_no_se_reconoce_por_nombre(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        md_path = tmp_path / "ARCHIVO_SIN_NUMERO_DE_UNIDAD.md"
        md_path.write_text("# Test\n\nTexto.\n", encoding="utf-8")
        resultado = auditor.audit_unit(md_path)
        assert resultado["hallazgos"]["curricular"] == []


class TestAuditAllUnits:
    def test_recorre_las_9_unidades_reales_sin_excepciones(
        self, auditor: ContentAuditorAgent
    ):
        course_dir = Path(__file__).parent.parent
        reporte = auditor.audit_all_units(course_dir)

        assert isinstance(reporte, str)
        assert "UNIDAD_0" in reporte
        assert "UNIDAD_8" in reporte

    def test_reporte_es_markdown_con_encabezados_por_unidad(
        self, auditor: ContentAuditorAgent, tmp_path: Path
    ):
        (tmp_path / "UNIDAD_1_TEST.md").write_text(
            '# UNIDAD 1\n\n```python\ndef f(x: int) -> int:\n    """Doc."""\n    return x\n```\n',
            encoding="utf-8",
        )
        reporte = auditor.audit_all_units(tmp_path)
        assert "# Reporte de Auditoría de Contenido" in reporte
        assert "UNIDAD_1_TEST.md" in reporte
