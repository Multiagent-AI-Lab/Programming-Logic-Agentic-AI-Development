"""Tests de caracterización para TutorAgent (RAG con ChromaDB)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.multiagent_core.tutor_agent import TutorAgent


@pytest.fixture
def course_dir(tmp_path: Path) -> Path:
    (tmp_path / "UNIDAD_1_TEST.md").write_text(
        "# Unidad 1\n\n## Variables\nUna variable guarda un valor en memoria y tiene un nombre identificador.\n",
        encoding="utf-8",
    )
    (tmp_path / "UNIDAD_2_TEST.md").write_text(
        "# Unidad 2\n\n## Pseudocódigo\nEl pseudocódigo UCEMICH describe algoritmos usando INICIO, FIN, SI y PARA.\n",
        encoding="utf-8",
    )
    (tmp_path / "notas.txt").write_text("archivo no markdown, no debe incluirse", encoding="utf-8")
    return tmp_path


@pytest.fixture
def chroma_path(tmp_path: Path) -> Path:
    return tmp_path / ".chroma_test"


class TestGetMarkdownFiles:
    def test_encuentra_solo_archivos_unidad_md(self, course_dir: Path, chroma_path: Path):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        archivos = tutor._get_markdown_files()
        nombres = {f.name for f in archivos}
        assert nombres == {"UNIDAD_1_TEST.md", "UNIDAD_2_TEST.md"}


class TestSearchLocalDocs:
    def test_encuentra_seccion_relevante_por_busqueda_semantica(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        resultado = tutor._search_local_docs("¿qué es una variable?")
        assert "UNIDAD_1_TEST.md" in resultado
        assert "Variables" in resultado

    def test_cita_la_seccion_exacta_de_origen(self, course_dir: Path, chroma_path: Path):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        resultado = tutor._search_local_docs("sintaxis de pseudocódigo con SI y PARA")
        assert "UNIDAD_2_TEST.md" in resultado

    def test_indice_es_persistente_entre_instancias(self, course_dir: Path, chroma_path: Path):
        TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        tutor2 = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        resultado = tutor2._search_local_docs("variable")
        assert "No se encontraron documentos locales relevantes" not in resultado


class TestAsk:
    def test_construye_prompt_con_contexto_y_pregunta(self, course_dir: Path, chroma_path: Path):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.text = "Respuesta simulada del tutor"

        with patch("src.multiagent_core.tutor_agent.genai.GenerativeModel") as mock_model_cls:
            mock_model_cls.return_value.generate_content.return_value = mock_response
            respuesta = tutor.ask("¿Qué es una variable?")

        assert respuesta == "Respuesta simulada del tutor"
        prompt_enviado = mock_model_cls.return_value.generate_content.call_args[0][0]
        assert "¿Qué es una variable?" in prompt_enviado
        assert "Variables" in prompt_enviado

    def test_maneja_error_de_la_api_sin_lanzar_excepcion(self, course_dir: Path, chroma_path: Path):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)

        with patch("src.multiagent_core.tutor_agent.genai.GenerativeModel") as mock_model_cls:
            mock_model_cls.return_value.generate_content.side_effect = RuntimeError("fallo de red")
            respuesta = tutor.ask("¿Qué es una variable?")

        assert "Error al invocar al modelo Gemini" in respuesta
        assert "Contexto Local Recuperado" in respuesta
