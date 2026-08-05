"""Tests de caracterización para TutorAgent (RAG con ChromaDB)."""

import json
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
    (tmp_path / "notas.txt").write_text(
        "archivo no markdown, no debe incluirse", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def chroma_path(tmp_path: Path) -> Path:
    return tmp_path / ".chroma_test"


class TestGetMarkdownFiles:
    def test_encuentra_solo_archivos_unidad_md(
        self, course_dir: Path, chroma_path: Path
    ):
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

    def test_cita_la_seccion_exacta_de_origen(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        resultado = tutor._search_local_docs("sintaxis de pseudocódigo con SI y PARA")
        assert "UNIDAD_2_TEST.md" in resultado

    def test_indice_es_persistente_entre_instancias(
        self, course_dir: Path, chroma_path: Path
    ):
        TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        tutor2 = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        resultado = tutor2._search_local_docs("variable")
        assert "No se encontraron documentos locales relevantes" not in resultado


class TestAsk:
    def test_construye_prompt_con_contexto_y_pregunta(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.text = "Respuesta simulada del tutor"

        with patch(
            "src.multiagent_core.tutor_agent.genai.GenerativeModel"
        ) as mock_model_cls:
            mock_model_cls.return_value.generate_content.return_value = mock_response
            respuesta = tutor.ask("¿Qué es una variable?")

        assert respuesta == "Respuesta simulada del tutor"
        prompt_enviado = mock_model_cls.return_value.generate_content.call_args[0][0]
        assert "¿Qué es una variable?" in prompt_enviado
        assert "Variables" in prompt_enviado

    def test_maneja_error_de_la_api_sin_lanzar_excepcion(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)

        with patch(
            "src.multiagent_core.tutor_agent.genai.GenerativeModel"
        ) as mock_model_cls:
            mock_model_cls.return_value.generate_content.side_effect = RuntimeError(
                "fallo de red"
            )
            respuesta = tutor.ask("¿Qué es una variable?")

        assert "Error al invocar al modelo Gemini" in respuesta
        assert "Contexto Local Recuperado" in respuesta


class TestDiagnoseError:
    def test_zero_division_error_da_pregunta_sobre_validar_denominador(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        pregunta = tutor._diagnose_error("ZeroDivisionError: division by zero")
        assert pregunta is not None
        assert "denominador" in pregunta.lower() or "cero" in pregunta.lower()

    def test_index_error_da_pregunta_sobre_verificar_longitud(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        pregunta = tutor._diagnose_error("IndexError: list index out of range")
        assert pregunta is not None
        assert "len(" in pregunta or "longitud" in pregunta.lower()

    def test_key_error_da_pregunta_sobre_dict_get(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        pregunta = tutor._diagnose_error("KeyError: 'radio_nm'")
        assert pregunta is not None
        assert "get(" in pregunta or "clave" in pregunta.lower()

    def test_error_desconocido_da_pregunta_generica_de_fallback(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        pregunta = tutor._diagnose_error("SomeWeirdError: mensaje raro")
        assert pregunta is not None
        assert "?" in pregunta

    def test_mensaje_sin_error_retorna_none(self, course_dir: Path, chroma_path: Path):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        assert tutor._diagnose_error("") is None


class TestAskConTraceback:
    def test_pregunta_con_traceback_recibe_pista_socratica_antes_de_la_respuesta(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.text = "Respuesta completa del LLM"

        pregunta_con_error = (
            "Me sale este error:\nTraceback (most recent call last):\n"
            "ZeroDivisionError: division by zero\n¿Qué hago?"
        )

        with patch(
            "src.multiagent_core.tutor_agent.genai.GenerativeModel"
        ) as mock_model_cls:
            mock_model_cls.return_value.generate_content.return_value = mock_response
            respuesta = tutor.ask(pregunta_con_error)

        assert "denominador" in respuesta.lower() or "cero" in respuesta.lower()

    def test_pregunta_conceptual_sin_traceback_no_recibe_pista_socratica(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.text = "Una variable es un espacio en memoria."

        with patch(
            "src.multiagent_core.tutor_agent.genai.GenerativeModel"
        ) as mock_model_cls:
            mock_model_cls.return_value.generate_content.return_value = mock_response
            respuesta = tutor.ask("¿Qué es una variable?")

        assert respuesta == "Una variable es un espacio en memoria."


@pytest.fixture
def memory_path(tmp_path: Path) -> Path:
    return tmp_path / ".tutor_memory_test.json"


class TestMemoriaEpisodica:
    def test_add_episode_persiste_en_archivo_json(
        self, course_dir: Path, chroma_path: Path, memory_path: Path
    ):
        tutor = TutorAgent(
            course_dir=course_dir, chroma_path=chroma_path, memory_path=memory_path
        )
        tutor._add_episode("¿qué es una variable?", "Una variable guarda un valor.")

        assert memory_path.exists()
        contenido = json.loads(memory_path.read_text(encoding="utf-8"))
        assert len(contenido) == 1
        assert contenido[0]["question"] == "¿qué es una variable?"

    def test_retrieve_relevant_episodes_encuentra_por_solapamiento_de_palabras(
        self, course_dir: Path, chroma_path: Path, memory_path: Path
    ):
        tutor = TutorAgent(
            course_dir=course_dir, chroma_path=chroma_path, memory_path=memory_path
        )
        tutor._add_episode(
            "¿qué es una variable en Python?", "Resumen sobre variables."
        )
        tutor._add_episode("¿cómo funciona un bucle for?", "Resumen sobre bucles.")

        resultados = tutor._retrieve_relevant_episodes("dudas sobre variable")
        assert len(resultados) >= 1
        assert "variable" in resultados[0]["question"].lower()

    def test_memoria_persiste_entre_instancias_nuevas(
        self, course_dir: Path, chroma_path: Path, memory_path: Path
    ):
        tutor1 = TutorAgent(
            course_dir=course_dir, chroma_path=chroma_path, memory_path=memory_path
        )
        tutor1._add_episode("¿qué es un ciclo while?", "Resumen sobre while.")

        tutor2 = TutorAgent(
            course_dir=course_dir, chroma_path=chroma_path, memory_path=memory_path
        )
        resultados = tutor2._retrieve_relevant_episodes("ciclo while")
        assert len(resultados) >= 1

    def test_limite_de_episodios_no_crece_indefinidamente(
        self, course_dir: Path, chroma_path: Path, memory_path: Path
    ):
        from src.multiagent_core.tutor_agent import MAX_EPISODIOS

        tutor = TutorAgent(
            course_dir=course_dir, chroma_path=chroma_path, memory_path=memory_path
        )
        for i in range(MAX_EPISODIOS + 10):
            tutor._add_episode(f"pregunta {i}", f"respuesta {i}")

        contenido = json.loads(memory_path.read_text(encoding="utf-8"))
        assert len(contenido) == MAX_EPISODIOS

    def test_default_memory_path_es_course_dir_tutor_memory_json(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        assert tutor.memory_path == course_dir / ".tutor_memory.json"


class TestAskUsaMemoria:
    def test_ask_incluye_contexto_de_pregunta_anterior_relacionada(
        self, course_dir: Path, chroma_path: Path, memory_path: Path
    ):
        tutor = TutorAgent(
            course_dir=course_dir, chroma_path=chroma_path, memory_path=memory_path
        )
        mock_response = MagicMock()
        mock_response.text = "Respuesta simulada"

        with patch(
            "src.multiagent_core.tutor_agent.genai.GenerativeModel"
        ) as mock_model_cls:
            mock_model_cls.return_value.generate_content.return_value = mock_response
            tutor.ask("¿qué es una variable en Python?")

            mock_model_cls.return_value.generate_content.reset_mock()
            tutor.ask("y las variables, se pueden reasignar?")

        prompt_enviado = mock_model_cls.return_value.generate_content.call_args[0][0]
        assert (
            "sesiones anteriores" in prompt_enviado.lower()
            or "pregunta anterior" in prompt_enviado.lower()
        )
