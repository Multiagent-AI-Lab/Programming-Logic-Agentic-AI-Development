"""Tests TDD para MermaidRenderer (texto Mermaid -> SVG con caché)."""

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.multiagent_core.mermaid_renderer import MermaidRenderer

MERMAID_VALIDO = "graph TD\n    A[Inicio] --> B[Fin]"


@pytest.fixture
def npx_disponible():
    with patch("src.multiagent_core.mermaid_renderer.shutil.which") as mock_which:
        mock_which.return_value = r"C:\nodejs\npx.cmd"
        yield mock_which


def _mock_subprocess_exitoso(output_dir: Path):
    def side_effect(cmd, *args, **kwargs):
        svg_path = Path(cmd[cmd.index("-o") + 1])
        svg_path.write_text("<svg>contenido de prueba</svg>", encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    return side_effect


class TestCacheMiss:
    def test_primera_invocacion_genera_svg_y_lo_retorna(
        self, npx_disponible, tmp_path: Path
    ):
        renderer = MermaidRenderer(output_dir=tmp_path)
        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=_mock_subprocess_exitoso(tmp_path),
        ) as mock_run:
            resultado = renderer.render(MERMAID_VALIDO)

        assert resultado.exists()
        assert resultado.suffix == ".svg"
        assert mock_run.call_count == 1

    def test_nombre_del_svg_es_hash_sha256_del_texto(
        self, npx_disponible, tmp_path: Path
    ):
        renderer = MermaidRenderer(output_dir=tmp_path)
        esperado = hashlib.sha256(MERMAID_VALIDO.encode()).hexdigest()[:16]
        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=_mock_subprocess_exitoso(tmp_path),
        ):
            resultado = renderer.render(MERMAID_VALIDO)

        assert resultado.name == f"{esperado}.svg"


class TestCacheHit:
    def test_segunda_llamada_con_mismo_texto_no_invoca_subprocess(
        self, npx_disponible, tmp_path: Path
    ):
        renderer = MermaidRenderer(output_dir=tmp_path)
        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=_mock_subprocess_exitoso(tmp_path),
        ) as mock_run:
            primera = renderer.render(MERMAID_VALIDO)
            segunda = renderer.render(MERMAID_VALIDO)

        assert primera == segunda
        assert mock_run.call_count == 1


class TestArchivoTemporal:
    def test_temporal_se_borra_tras_render_exitoso(
        self, npx_disponible, tmp_path: Path
    ):
        renderer = MermaidRenderer(output_dir=tmp_path)
        rutas_temporales = []

        def side_effect(cmd, *args, **kwargs):
            rutas_temporales.append(Path(cmd[cmd.index("-i") + 1]))
            svg_path = Path(cmd[cmd.index("-o") + 1])
            svg_path.write_text("<svg></svg>", encoding="utf-8")
            return MagicMock(returncode=0, stderr="")

        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=side_effect,
        ):
            renderer.render(MERMAID_VALIDO)

        assert not rutas_temporales[0].exists()

    def test_temporal_se_borra_incluso_si_mmdc_falla(
        self, npx_disponible, tmp_path: Path
    ):
        renderer = MermaidRenderer(output_dir=tmp_path)
        rutas_temporales = []

        def side_effect(cmd, *args, **kwargs):
            rutas_temporales.append(Path(cmd[cmd.index("-i") + 1]))
            return MagicMock(returncode=1, stderr="Parse error on line 1")

        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=side_effect,
        ):
            with pytest.raises(RuntimeError):
                renderer.render("graph TD\n    A[Roto(sin comillas)]")

        assert not rutas_temporales[0].exists()


class TestReintento:
    def test_reintenta_una_vez_si_mmdc_falla_la_primera_vez(
        self, npx_disponible, tmp_path: Path
    ):
        renderer = MermaidRenderer(output_dir=tmp_path)
        llamadas = {"count": 0}

        def side_effect(cmd, *args, **kwargs):
            llamadas["count"] += 1
            if llamadas["count"] == 1:
                return MagicMock(returncode=1, stderr="Chromium launch failed")
            svg_path = Path(cmd[cmd.index("-o") + 1])
            svg_path.write_text("<svg></svg>", encoding="utf-8")
            return MagicMock(returncode=0, stderr="")

        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=side_effect,
        ):
            resultado = renderer.render(MERMAID_VALIDO)

        assert resultado.exists()
        assert llamadas["count"] == 2

    def test_propaga_error_tras_dos_fallos_consecutivos(
        self, npx_disponible, tmp_path: Path
    ):
        renderer = MermaidRenderer(output_dir=tmp_path)

        def side_effect(cmd, *args, **kwargs):
            return MagicMock(returncode=1, stderr="Parse error on line 3")

        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=side_effect,
        ):
            with pytest.raises(RuntimeError, match="Parse error"):
                renderer.render("graph TD\n    A[Roto(sin comillas)]")


class TestNodeNoDisponible:
    def test_lanza_runtime_error_si_npx_no_esta_en_path(self, tmp_path: Path):
        with patch(
            "src.multiagent_core.mermaid_renderer.shutil.which", return_value=None
        ):
            with pytest.raises(RuntimeError, match="Node.js"):
                MermaidRenderer(output_dir=tmp_path)

    def test_no_crea_output_dir_si_node_no_esta_disponible(self, tmp_path: Path):
        output_dir = tmp_path / "no_deberia_existir"
        with patch(
            "src.multiagent_core.mermaid_renderer.shutil.which", return_value=None
        ):
            with pytest.raises(RuntimeError):
                MermaidRenderer(output_dir=output_dir)
        assert not output_dir.exists()
