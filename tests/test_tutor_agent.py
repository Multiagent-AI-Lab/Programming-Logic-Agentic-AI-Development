"""Tests de caracterización para TutorAgent (RAG con ChromaDB)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

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
    (tmp_path / "EXTRA_TEST.md").write_text(
        "# EXTRA: Material complementario\n\n## Tema Extra\nContenido de la parte EXTRA del curso.\n",
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
    def test_encuentra_archivos_unidad_y_extra_md(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        archivos = tutor._get_markdown_files()
        nombres = {f.name for f in archivos}
        assert nombres == {"UNIDAD_1_TEST.md", "UNIDAD_2_TEST.md", "EXTRA_TEST.md"}


class TestExtractDois:
    def test_extrae_un_doi_simple(self, course_dir: Path, chroma_path: Path):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        texto = (
            "Ver Vollath, D. (2018). *Beilstein J. Nanotechnol.*, 9, 2265. "
            "DOI: [10.3762/bjnano.9.211](https://doi.org/10.3762/bjnano.9.211)."
        )
        assert tutor._extract_dois(texto) == ["10.3762/bjnano.9.211"]

    def test_extrae_doi_con_parentesis_internos(
        self, course_dir: Path, chroma_path: Path
    ):
        """Regresión: el DOI real de Van Hardeveld & Hartog (1969) contiene
        paréntesis en su propio identificador. Un regex que intente parsear
        la URL delimitando por ')' trunca este DOI incorrectamente."""
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        texto = (
            "Van Hardeveld, R., & Hartog, F. (1969). *Surface Science*, 15(2), 189–230. "
            "DOI: [10.1016/0039-6028(69)90148-4](https://doi.org/10.1016/0039-6028(69)90148-4)."
        )
        assert tutor._extract_dois(texto) == ["10.1016/0039-6028(69)90148-4"]

    def test_deduplica_doi_repetido_en_el_mismo_texto(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        texto = (
            "Primera mención. DOI: [10.1039/d2na00809b](https://doi.org/10.1039/d2na00809b). "
            "Segunda mención del mismo. DOI: [10.1039/d2na00809b](https://doi.org/10.1039/d2na00809b)."
        )
        assert tutor._extract_dois(texto) == ["10.1039/d2na00809b"]

    def test_texto_sin_doi_retorna_lista_vacia(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        assert tutor._extract_dois("Texto sin ninguna cita bibliográfica.") == []

    def test_texto_con_link_doi_invalido_no_extrae_nada(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        texto = (
            "Ver el trabajo de Vollath. DOI: [ver Vollath 2018](https://example.com)."
        )
        assert tutor._extract_dois(texto) == []


class TestFetchAbstract:
    def test_retorna_abstract_limpio_de_markup_jats(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"abstract": "<jats:p>Texto del abstract con markup.</jats:p>"}
        }
        mock_response.raise_for_status.return_value = None

        with patch(
            "src.multiagent_core.tutor_agent.requests.get",
            return_value=mock_response,
        ):
            resultado = tutor._fetch_abstract("10.3762/bjnano.9.211")

        assert resultado == "Texto del abstract con markup."

    def test_retorna_none_si_falla_la_peticion_de_red(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)

        with patch(
            "src.multiagent_core.tutor_agent.requests.get",
            side_effect=requests.exceptions.Timeout("timeout simulado"),
        ):
            resultado = tutor._fetch_abstract("10.9999/doi-inexistente")

        assert resultado is None

    def test_retorna_none_si_el_registro_no_tiene_abstract(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {}}
        mock_response.raise_for_status.return_value = None

        with patch(
            "src.multiagent_core.tutor_agent.requests.get",
            return_value=mock_response,
        ):
            resultado = tutor._fetch_abstract("10.1234/sin-abstract")

        assert resultado is None

    def test_retorna_none_si_status_code_es_error(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404"
        )

        with patch(
            "src.multiagent_core.tutor_agent.requests.get",
            return_value=mock_response,
        ):
            resultado = tutor._fetch_abstract("10.0000/no-existe")

        assert resultado is None


class TestBuildIndexConDois:
    @pytest.fixture
    def course_dir_con_doi(self, tmp_path: Path) -> Path:
        (tmp_path / "UNIDAD_TEST.md").write_text(
            "# Unidad de prueba\n\n"
            "## Sección con cita\n\n"
            "Un dato real respaldado por literatura. "
            "DOI: [10.3762/bjnano.9.211](https://doi.org/10.3762/bjnano.9.211).\n",
            encoding="utf-8",
        )
        return tmp_path

    @pytest.fixture
    def course_dir_con_doi_repetido(self, tmp_path: Path) -> Path:
        (tmp_path / "UNIDAD_A_TEST.md").write_text(
            "# Unidad A\n\n## Sección A\n\n"
            "DOI: [10.1039/D0MA00439A](https://doi.org/10.1039/D0MA00439A).\n",
            encoding="utf-8",
        )
        (tmp_path / "UNIDAD_B_TEST.md").write_text(
            "# Unidad B\n\n## Sección B\n\n"
            "DOI: [10.1039/D0MA00439A](https://doi.org/10.1039/D0MA00439A).\n",
            encoding="utf-8",
        )
        return tmp_path

    def test_abstract_se_indexa_con_metadata_de_referencia_doi(
        self, course_dir_con_doi: Path, chroma_path: Path
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"abstract": "Abstract de prueba sobre energía superficial."}
        }
        mock_response.raise_for_status.return_value = None

        with patch(
            "src.multiagent_core.tutor_agent.requests.get",
            return_value=mock_response,
        ):
            tutor = TutorAgent(course_dir=course_dir_con_doi, chroma_path=chroma_path)

        resultado = tutor._search_local_docs("energía superficial")
        assert "Referencia DOI: 10.3762/bjnano.9.211" in resultado
        assert "Abstract de prueba sobre energía superficial" in resultado

    def test_doi_que_falla_no_impide_indexar_el_resto_del_archivo(
        self, course_dir_con_doi: Path, chroma_path: Path
    ):
        with patch(
            "src.multiagent_core.tutor_agent.requests.get",
            side_effect=requests.exceptions.Timeout("timeout simulado"),
        ):
            tutor = TutorAgent(course_dir=course_dir_con_doi, chroma_path=chroma_path)

        resultado = tutor._search_local_docs("sección con cita")
        assert "UNIDAD_TEST.md" in resultado

    def test_doi_repetido_en_dos_archivos_solo_consulta_crossref_una_vez(
        self, course_dir_con_doi_repetido: Path, chroma_path: Path
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"abstract": "Abstract único sobre nucleación."}
        }
        mock_response.raise_for_status.return_value = None

        with patch(
            "src.multiagent_core.tutor_agent.requests.get",
            return_value=mock_response,
        ) as mock_get:
            TutorAgent(course_dir=course_dir_con_doi_repetido, chroma_path=chroma_path)

        mock_get.assert_called_once()

    def test_doi_repetido_en_dos_archivos_indexa_un_solo_documento_con_ambas_fuentes(
        self, course_dir_con_doi_repetido: Path, chroma_path: Path
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"abstract": "Abstract único sobre nucleación."}
        }
        mock_response.raise_for_status.return_value = None

        with patch(
            "src.multiagent_core.tutor_agent.requests.get",
            return_value=mock_response,
        ):
            tutor = TutorAgent(
                course_dir=course_dir_con_doi_repetido, chroma_path=chroma_path
            )

        resultado = tutor._search_local_docs("nucleación")
        assert "UNIDAD_A_TEST.md" in resultado
        assert "UNIDAD_B_TEST.md" in resultado
        # Solo debe aparecer un bloque de referencia, no dos
        assert resultado.count("Referencia DOI: 10.1039/D0MA00439A") == 1


class TestChromaPathCreation:
    def test_crea_chroma_path_si_ni_el_directorio_padre_existe(
        self, course_dir: Path, tmp_path: Path
    ):
        """Regresión: tras un git clone fresco (p. ej. en Colab), '.chroma/'
        está en .gitignore y no existe — ni siquiera su directorio padre,
        si chroma_path apunta a una ruta anidada nueva. PersistentClient de
        ChromaDB no garantiza crear rutas anidadas por sí solo en todos los
        entornos; TutorAgent debe crearlo explícitamente antes de instanciar
        el cliente."""
        chroma_path_anidado = tmp_path / "nivel_a" / "nivel_b" / ".chroma"
        assert not chroma_path_anidado.parent.exists()

        TutorAgent(course_dir=course_dir, chroma_path=chroma_path_anidado)

        assert chroma_path_anidado.exists()

    def test_reindexar_automaticamente_si_chroma_existente_usa_otro_embedding(
        self, course_dir: Path, chroma_path: Path
    ):
        """Regresión: un .chroma/ ya indexado con un embedding function
        distinto (p. ej. de una versión anterior de TutorAgent, o de una
        sesión previa de un alumno) hacía que get_or_create_collection
        lanzara ValueError('Embedding function conflict...') y TutorAgent()
        crasheara por completo al instanciarse. Debe detectar el conflicto y
        reindexar automáticamente en vez de fallar."""
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        chroma_client = chromadb.PersistentClient(path=str(chroma_path))
        coleccion_vieja = chroma_client.get_or_create_collection(
            "lecciones_curso", embedding_function=DefaultEmbeddingFunction()
        )
        coleccion_vieja.add(documents=["contenido viejo de prueba"], ids=["viejo_1"])
        del chroma_client, coleccion_vieja

        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        resultado = tutor._search_local_docs("¿qué es una variable?")

        assert "UNIDAD_1_TEST.md" in resultado


class TestEmbeddingMultilingue:
    @pytest.fixture
    def course_dir_con_seccion_conceptual(self, tmp_path: Path) -> Path:
        """Reproduce el patrón del bug real: una sección corta dominada por
        código (el 'Paso 2' real de U3) compite contra una sección larga con
        una analogía conceptual extensa en español (la 'ANALOGÍA DIDÁCTICA 1'
        real de U3). Con el embedding en inglés (all-MiniLM-L6-v2, default de
        ChromaDB), la analogía nunca aparecía en el top-30 para preguntas
        conceptuales en español."""
        (tmp_path / "UNIDAD_TEST.md").write_text(
            "# Unidad de prueba\n\n"
            "### Paso 2: Guardar un dato en una variable\n\n"
            "```python\n"
            "radio_nm = 5.2\n"
            "print(radio_nm)\n"
            "```\n\n"
            "Aquí `radio_nm` es una variable.\n\n"
            "### Analogía Didáctica: Variables como Etiquetas en un Almacén\n\n"
            "Para comprender qué es una variable, imaginemos un almacén de "
            "materiales. Una variable es una etiqueta de papel colgante donde "
            "escribimos un nombre legible. Esta etiqueta no contiene la "
            "sustancia; es solo un trozo de papel que se puede colgar del asa "
            "de un recipiente físico que guarda el valor real. El nombre de la "
            "variable identifica el dato, pero el dato en sí vive en otro "
            "lugar de la memoria de la computadora.\n",
            encoding="utf-8",
        )
        return tmp_path

    def test_pregunta_conceptual_recupera_seccion_de_analogia_no_solo_codigo(
        self, course_dir_con_seccion_conceptual: Path, chroma_path: Path
    ):
        tutor = TutorAgent(
            course_dir=course_dir_con_seccion_conceptual, chroma_path=chroma_path
        )
        resultado = tutor._search_local_docs("¿qué es una variable?")
        assert "Analogía Didáctica" in resultado


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
        self, course_dir: Path, chroma_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("GEMINI_API_KEY", "key-de-prueba")
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.text = "Respuesta simulada del tutor"

        with patch("src.multiagent_core.tutor_agent.genai.Client") as mock_client_cls:
            mock_client_cls.return_value.models.generate_content.return_value = (
                mock_response
            )
            respuesta = tutor.ask("¿Qué es una variable?")

        assert respuesta == "Respuesta simulada del tutor"
        llamada = mock_client_cls.return_value.models.generate_content.call_args
        assert llamada.kwargs["model"] == tutor.model_name
        prompt_enviado = llamada.kwargs["contents"]
        assert "¿Qué es una variable?" in prompt_enviado
        assert "Variables" in prompt_enviado

    def test_maneja_error_de_la_api_sin_lanzar_excepcion(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)

        with patch("src.multiagent_core.tutor_agent.genai.Client") as mock_client_cls:
            mock_client_cls.return_value.models.generate_content.side_effect = (
                RuntimeError("fallo de red")
            )
            respuesta = tutor.ask("¿Qué es una variable?")

        assert "Error al invocar al modelo Gemini" in respuesta
        assert "Contexto Local Recuperado" in respuesta

    def test_sin_api_key_en_entorno_no_falla_construir_tutoragent(
        self, course_dir: Path, chroma_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Regresión: TutorAgent debe poder instanciarse sin GEMINI_API_KEY en
        el entorno (p. ej. un alumno que aún no configuró su key) — solo
        ask() debe fallar de forma controlada, nunca el constructor."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
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
        self, course_dir: Path, chroma_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("GEMINI_API_KEY", "key-de-prueba")
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.text = "Respuesta completa del LLM"

        pregunta_con_error = (
            "Me sale este error:\nTraceback (most recent call last):\n"
            "ZeroDivisionError: division by zero\n¿Qué hago?"
        )

        with patch("src.multiagent_core.tutor_agent.genai.Client") as mock_client_cls:
            mock_client_cls.return_value.models.generate_content.return_value = (
                mock_response
            )
            respuesta = tutor.ask(pregunta_con_error)

        assert "denominador" in respuesta.lower() or "cero" in respuesta.lower()

    def test_pregunta_conceptual_sin_traceback_no_recibe_pista_socratica(
        self, course_dir: Path, chroma_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("GEMINI_API_KEY", "key-de-prueba")
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.text = "Una variable es un espacio en memoria."

        with patch("src.multiagent_core.tutor_agent.genai.Client") as mock_client_cls:
            mock_client_cls.return_value.models.generate_content.return_value = (
                mock_response
            )
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
        self,
        course_dir: Path,
        chroma_path: Path,
        memory_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setenv("GEMINI_API_KEY", "key-de-prueba")
        tutor = TutorAgent(
            course_dir=course_dir, chroma_path=chroma_path, memory_path=memory_path
        )
        mock_response = MagicMock()
        mock_response.text = "Respuesta simulada"

        with patch("src.multiagent_core.tutor_agent.genai.Client") as mock_client_cls:
            mock_client_cls.return_value.models.generate_content.return_value = (
                mock_response
            )
            tutor.ask("¿qué es una variable en Python?")

            mock_client_cls.return_value.models.generate_content.reset_mock()
            tutor.ask("y las variables, se pueden reasignar?")

        llamada = mock_client_cls.return_value.models.generate_content.call_args
        prompt_enviado = llamada.kwargs["contents"]
        assert (
            "sesiones anteriores" in prompt_enviado.lower()
            or "pregunta anterior" in prompt_enviado.lower()
        )
