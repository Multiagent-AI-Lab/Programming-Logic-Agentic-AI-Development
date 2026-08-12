"""Tests TDD para CurriculumMapAgent (heurística de prerequisitos + render del DAG)."""

from pathlib import Path

import pytest

from src.multiagent_core.curriculum_map_agent import CurriculumMapAgent


@pytest.fixture
def agent() -> CurriculumMapAgent:
    return CurriculumMapAgent()


def _escribir_unidad(tmp_path: Path, numero: int, contenido: str) -> Path:
    nombres = {
        0: "UNIDAD_0_TEST.md",
        1: "UNIDAD_1_TEST.md",
        2: "UNIDAD_2_TEST.md",
        3: "UNIDAD_3_TEST.md",
        5: "UNIDAD_5_TEST.md",
        6: "UNIDAD_6_TEST.md",
    }
    md_path = tmp_path / nombres[numero]
    md_path.write_text(contenido, encoding="utf-8")
    return md_path


class TestSuggestPrerequisites:
    def test_detecta_termino_compartido_entre_dos_unidades(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        _escribir_unidad(
            tmp_path, 3,
            "# UNIDAD 3\n\nEsta unidad enseña bucles for y while con ejemplos.\n",
        )
        _escribir_unidad(
            tmp_path, 5,
            "# UNIDAD 5\n\nAquí reutilizamos los bucles vistos antes para simular.\n",
        )
        candidatos = agent.suggest_prerequisites(tmp_path)

        assert 5 in candidatos
        terminos_u5 = [c["termino"] for c in candidatos[5]]
        assert "bucle" in terminos_u5
        assert candidatos[5][terminos_u5.index("bucle")]["unidad_origen"] == 3

    def test_no_genera_candidato_si_termino_solo_aparece_en_una_unidad(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        _escribir_unidad(
            tmp_path, 3,
            "# UNIDAD 3\n\nEsta unidad enseña bucles for y while.\n",
        )
        _escribir_unidad(
            tmp_path, 5,
            "# UNIDAD 5\n\nAquí no se menciona nada relacionado.\n",
        )
        candidatos = agent.suggest_prerequisites(tmp_path)

        assert candidatos.get(5, []) == []

    def test_no_genera_candidato_desde_unidad_posterior_hacia_anterior(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        """Regresión: un término en U5 no debe generar candidato para U3
        (U5 es posterior, no puede ser prerequisito de una unidad anterior)."""
        _escribir_unidad(
            tmp_path, 3,
            "# UNIDAD 3\n\nTexto sin términos relevantes.\n",
        )
        _escribir_unidad(
            tmp_path, 5,
            "# UNIDAD 5\n\nEsta unidad enseña bucles for y while.\n",
        )
        candidatos = agent.suggest_prerequisites(tmp_path)

        assert candidatos.get(3, []) == []

    def test_busqueda_de_fstrings_opera_sobre_codigo_no_prosa(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        _escribir_unidad(
            tmp_path, 3,
            '# UNIDAD 3\n\n```python\nx = f"{nombre}"\n```\n',
        )
        _escribir_unidad(
            tmp_path, 5,
            '# UNIDAD 5\n\n```python\ny = f"{valor}"\n```\n',
        )
        candidatos = agent.suggest_prerequisites(tmp_path)

        terminos_u5 = [c["termino"] for c in candidatos.get(5, [])]
        assert "f-string" in terminos_u5

    def test_mencion_de_fstring_en_prosa_sin_codigo_no_genera_candidato(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        """Regresión: 'f-string' no aparece nombrado como concepto en ningún
        .md real del curso — solo se usa la sintaxis en código. Mencionar la
        palabra en prosa (sin el patrón f" real en un bloque de código) no
        debe disparar el candidato."""
        _escribir_unidad(
            tmp_path, 3,
            "# UNIDAD 3\n\nAquí se habla de f-string como concepto, sin código.\n",
        )
        _escribir_unidad(
            tmp_path, 5,
            "# UNIDAD 5\n\nTambién se menciona f-string aquí, sin código real.\n",
        )
        candidatos = agent.suggest_prerequisites(tmp_path)

        terminos_u5 = [c["termino"] for c in candidatos.get(5, [])]
        assert "f-string" not in terminos_u5

    def test_evidencia_incluye_fragmento_textual(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        _escribir_unidad(
            tmp_path, 2,
            "# UNIDAD 2\n\nSe explican las pruebas unitarias con pytest.\n",
        )
        _escribir_unidad(
            tmp_path, 6,
            "# UNIDAD 6\n\nLa suite usa pruebas unitarias otra vez.\n",
        )
        candidatos = agent.suggest_prerequisites(tmp_path)

        terminos_u6 = {c["termino"]: c for c in candidatos.get(6, [])}
        assert "pruebas unitarias" in terminos_u6
        assert len(terminos_u6["pruebas unitarias"]["evidencia"]) > 0


class TestRenderDag:
    def test_incluye_cadena_secuencial_completa(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        for n in range(9):
            (tmp_path / f"UNIDAD_{n}_TEST.md").write_text(
                f"# UNIDAD {n}\n\n## 📚 Prerequisitos de esta unidad\n\n"
                "- La secuencia de la unidad anterior (sin conceptos "
                "específicos adicionales que reforzar).\n"
                if n > 0
                else f"# UNIDAD {n}\n\nSin sección de prerequisitos.\n",
                encoding="utf-8",
            )
        mermaid = agent.render_dag(tmp_path)

        assert "U0" in mermaid and "U8" in mermaid
        assert "U0" in mermaid and "-->" in mermaid

    def test_incluye_los_3_subgraphs_de_fase(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        for n in range(9):
            (tmp_path / f"UNIDAD_{n}_TEST.md").write_text(
                f"# UNIDAD {n}\n", encoding="utf-8"
            )
        mermaid = agent.render_dag(tmp_path)

        assert "Sin IA para código" in mermaid
        assert "IA Moderada" in mermaid
        assert "IA Extensiva" in mermaid

    def test_genera_flecha_punteada_por_relacion_declarada(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        (tmp_path / "UNIDAD_3_TEST.md").write_text(
            "# UNIDAD 3\n", encoding="utf-8"
        )
        (tmp_path / "UNIDAD_5_TEST.md").write_text(
            "# UNIDAD 5\n\n## 📚 Prerequisitos de esta unidad\n\n"
            "- **Bucles `for`/`while`** (Unidad 3) — se reutilizan en la "
            "simulación.\n",
            encoding="utf-8",
        )
        mermaid = agent.render_dag(tmp_path)

        assert "-.Bucles" in mermaid or "-.bucles" in mermaid.lower()

    def test_unidad_sin_relaciones_no_genera_flecha_punteada_extra(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        (tmp_path / "UNIDAD_3_TEST.md").write_text(
            "# UNIDAD 3\n", encoding="utf-8"
        )
        (tmp_path / "UNIDAD_5_TEST.md").write_text(
            "# UNIDAD 5\n\n## 📚 Prerequisitos de esta unidad\n\n"
            "- La secuencia de la unidad anterior (sin conceptos "
            "específicos adicionales que reforzar).\n",
            encoding="utf-8",
        )
        mermaid = agent.render_dag(tmp_path)

        assert "-." not in mermaid

    def test_linea_mal_formada_se_ignora_silenciosamente(
        self, agent: CurriculumMapAgent, tmp_path: Path
    ):
        """Regresión: una línea que no matchea el formato exacto
        (ej. 'unidad' minúscula o 'U5' abreviado) no debe lanzar excepción
        ni generar una flecha — se ignora como prosa libre."""
        (tmp_path / "UNIDAD_5_TEST.md").write_text(
            "# UNIDAD 5\n\n## 📚 Prerequisitos de esta unidad\n\n"
            "- **Bucles** (unidad 3) — formato incorrecto, minúscula.\n",
            encoding="utf-8",
        )
        mermaid = agent.render_dag(tmp_path)

        assert "-." not in mermaid
