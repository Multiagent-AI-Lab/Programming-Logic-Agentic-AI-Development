"""
Agente Tutor (TutorAgent) - Lógica de Programación y Desarrollo Agéntico 🧠
==========================================================================

Este agente ayuda a los estudiantes a resolver dudas sobre los contenidos de
las unidades del curso usando un sistema RAG local (Retrieval-Augmented Generation)
con embeddings de ChromaDB que busca en los archivos Markdown de las lecciones
y cita la sección exacta de origen.
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional

import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar API Keys de .env
load_dotenv()
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

logger = logging.getLogger(__name__)

DEFAULT_CHROMA_DIRNAME = ".chroma"
TOP_K_RESULTS = 3

_SOCRATIC_RULES: dict[str, str] = {
    "zerodivisionerror": (
        "Antes de darte la respuesta: revisa tu código. ¿Estás dividiendo entre "
        "una variable que podría valer cero? Piensa en el ejemplo de la Unidad 2 "
        "(volumen de nanopartícula): ¿qué pasaría si el radio fuera cero antes de "
        "dividir? ¿Cómo validarías el denominador antes de la operación?"
    ),
    "indexerror": (
        "Antes de darte la respuesta: ¿estás accediendo a una posición de una "
        "lista de coordenadas o radios sin verificar antes su tamaño? Revisa si "
        "usaste `len(tu_lista)` para confirmar que el índice existe antes de "
        "indexar."
    ),
    "keyerror": (
        "Antes de darte la respuesta: ¿estás accediendo a una clave de un "
        "diccionario de propiedades de materiales que podría no existir? "
        "¿Qué pasa si usas `diccionario.get('clave', valor_default)` en vez de "
        "`diccionario['clave']` directamente?"
    ),
}

_SOCRATIC_FALLBACK = (
    "Antes de darte la respuesta directa: si fueras el intérprete de Python, "
    "¿por qué estarías confundido con este error? Vuelve a leer el mensaje "
    "completo, línea por línea."
)


class TutorAgent:
    """Agente Tutor RAG que responde dudas del curso usando embeddings de ChromaDB
    sobre la documentación local del curso."""

    def __init__(self, course_dir: Path, chroma_path: Optional[Path] = None):
        self.course_dir = Path(course_dir)
        self.model_name = "gemini-1.5-flash"
        self.chroma_path = (
            Path(chroma_path)
            if chroma_path
            else self.course_dir / DEFAULT_CHROMA_DIRNAME
        )
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_path))
        self.collection = self.chroma_client.get_or_create_collection("lecciones_curso")
        self._build_index()

    def _get_markdown_files(self) -> list[Path]:
        """Obtiene todos los archivos Markdown de las unidades del curso."""
        return list(self.course_dir.glob("UNIDAD_*.md"))

    def _split_into_sections(self, content: str) -> list[str]:
        """Divide un documento Markdown por secciones (headers H2 o H3)."""
        return [s.strip() for s in re.split(r"\n(?=##?\s)", content) if s.strip()]

    def _build_index(self) -> None:
        """Indexa los MDs del curso en ChromaDB, partidos por sección, si aún no lo están."""
        if self.collection.count() > 0:
            return

        documents: list[str] = []
        metadatas: list[dict] = []
        ids: list[str] = []

        for filepath in self._get_markdown_files():
            try:
                content = filepath.read_text(encoding="utf-8")
            except OSError as e:
                logger.error("Error leyendo %s: %s", filepath.name, e)
                continue

            for idx, section in enumerate(self._split_into_sections(content)):
                title_match = re.match(r"##?\s+(.+)", section)
                title = title_match.group(1).strip() if title_match else filepath.stem
                documents.append(section)
                metadatas.append({"source": filepath.name, "section": title})
                ids.append(f"{filepath.stem}__{idx}")

        if documents:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def _search_local_docs(self, query: str) -> str:
        """
        Búsqueda semántica (RAG) con embeddings de ChromaDB sobre los documentos locales.
        Retorna los bloques de texto más relevantes, citando la sección exacta de origen.
        """
        if self.collection.count() == 0:
            return "No se encontraron documentos locales relevantes."

        resultados = self.collection.query(query_texts=[query], n_results=TOP_K_RESULTS)
        documentos = resultados.get("documents", [[]])[0]
        metadatas = resultados.get("metadatas", [[]])[0]

        if not documentos:
            return "No se encontraron documentos locales relevantes."

        context_parts = []
        for doc, meta in zip(documentos, metadatas):
            fuente = meta.get("source", "desconocido")
            seccion = meta.get("section", "")
            context_parts.append(
                f"--- Fuente: {fuente} | Sección: {seccion} ---\n{doc}\n"
            )

        return "\n".join(context_parts)

    def _diagnose_error(
        self, error_message: str, code_context: str = ""
    ) -> Optional[str]:
        """Genera una pista socrática si el mensaje contiene un error de Python conocido.

        Args:
            error_message: Texto de la pregunta del alumno, potencialmente
                conteniendo un traceback o nombre de excepción de Python.
            code_context: Contexto adicional opcional sobre el código que
                produjo el error (no usado por las reglas actuales, reservado
                para heurísticas futuras).

        Returns:
            Una pregunta guía en español si se detecta un error real
            (heurística: contiene "Traceback" o un nombre de excepción
            terminado en "Error"); None si el texto no parece contener
            un error real.
        """
        if not error_message:
            return None

        contiene_traceback = "traceback" in error_message.lower()
        contiene_nombre_error = bool(re.search(r"\b\w*Error\b", error_message))
        if not (contiene_traceback or contiene_nombre_error):
            return None

        error_lower = error_message.lower()
        for nombre_error, pregunta in _SOCRATIC_RULES.items():
            if nombre_error in error_lower:
                return pregunta

        return _SOCRATIC_FALLBACK

    def ask(self, question: str) -> str:
        """Responde a la duda del estudiante, con pista socrática si detecta un error.

        Args:
            question: Pregunta o mensaje de error del estudiante.

        Returns:
            Si `question` contiene un traceback o nombre de excepción de
            Python reconocible, retorna primero una pregunta guía (no la
            solución directa), coherente con la política pedagógica del
            curso de auditar antes de confiar en el código. Si es una
            pregunta conceptual sin error, responde directamente vía Gemini
            con contexto local recuperado.
        """
        pista_socratica = self._diagnose_error(question)
        if pista_socratica:
            return pista_socratica

        context = self._search_local_docs(question)

        prompt = f"""
Eres un Agente Tutor experto en Lógica de Programación y Desarrollo Agéntico con IA para el curso de Ingeniería en Nanotecnología de la UCEMICH.
Tu misión es guiar al estudiante de forma clara, didáctica y técnica.

Usa el siguiente contexto recuperado de las lecciones del curso para responder la pregunta del alumno.
Si la información no está en el contexto, indícalo amablemente y responde con base en tus conocimientos generales del curso.

---
CONTEXTO DE LECCIONES:
{context}
---

PREGUNTA DEL ALUMNO:
{question}

Responde en español de forma estructurada, usando Markdown. Explica el paso a paso del razonamiento lógico.
"""
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.exception("Fallo al invocar al modelo Gemini")
            return f"Error al invocar al modelo Gemini: {e}\n\n[Contexto Local Recuperado]:\n{context}"


if __name__ == "__main__":
    # Prueba del Agente en local
    BASE_DIR = Path(__file__).parent.parent.parent
    tutor = TutorAgent(BASE_DIR)
    print("🤖 Agente Tutor inicializado. Haz una pregunta sobre el curso:")
    print("Duda: ¿Qué es el control por coincidencia de patrones?")
    respuesta = tutor.ask("¿Qué es el control por coincidencia de patrones?")
    print("\n=== RESPUESTA DEL TUTOR ===")
    print(respuesta)
