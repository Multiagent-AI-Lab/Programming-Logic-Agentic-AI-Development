# Diseño: ContentAuditorAgent + Conexión de los 7 Agentes con su Audiencia Real

**Fecha:** 2026-08-05
**Estado:** Aprobado, pendiente de plan de implementación

## Contexto y motivación

El usuario preguntó si el contenido de las 9 unidades del curso se generó con ayuda de un agente pedagógico/científico experto (como el "Consejo de Expertos" de 7 roles del proyecto hermano `IA NANOTECNOLOGIA`). La respuesta honesta es no: el contenido lo escribió Claude directamente, sin que ningún agente propio del proyecto lo generara ni lo auditara.

Se comparó `GOVERNANCE.md` y `PROTOCOLO_MAESTRO.md` de `IA NANOTECNOLOGIA` (Consejo de 7 agentes: `@Architect`, `@Scientist`, `@Engineer`, `@Safety_Gate`, `@Analyst`, `@Librarian`, `@QA`, con 3 loops de retroalimentación L1/L2/L3 y 8 Componentes Obligatorios de nivel doctoral) contra el estado de este proyecto. Los 8 Componentes Obligatorios de ese proyecto (≥1000 palabras de teoría, verificación SymPy, gráficos Seaborn/Plotly) no aplican a un curso de primer semestre sin conocimientos previos — se requiere un checklist propio, no una copia literal.

Durante la investigación surgió un segundo hallazgo, más importante: de los 7 agentes ya construidos en `src/multiagent_core/` (con 63 tests pasando), **solo 2 (`NotebookCompilerAgent`, `FlowchartAgent`) tienen uso real** en el flujo del curso — el pipeline MD→notebook. Los otros 5 (`CodeAuditorAgent`, `PseudocodeAgent`, `EvaluatorAgent`, `OrchestratorAgent`, `TutorAgent`) no tienen ningún punto de entrada documentado ni celda de uso en ningún notebook — existen como código con tests, invisibles para el alumno o el docente en la práctica.

Se verificó que ningún agente requiere pago: 6 de 7 son Python puro sin dependencias de red; solo `TutorAgent` necesita una `GEMINI_API_KEY`, gratuita vía [aistudio.google.com](https://aistudio.google.com/apikey) (cada alumno genera la suya, no se comparte una key entre el grupo por límites de cuota).

## Objetivo

1. Cerrar el hueco de auditoría de contenido con un `ContentAuditorAgent` heurístico (sin LLM) que revise las 9 unidades contra 4 dimensiones de calidad.
2. Conectar los 6 agentes sin punto de entrada real (`TutorAgent`, `PseudocodeAgent`, `CodeAuditorAgent`, `EvaluatorAgent`, `FlowchartAgent`, `OrchestratorAgent`) con su audiencia real (alumno vs. docente); `NotebookCompilerAgent` ya tiene su único usuario real (el mantenedor del curso) cubierto por el README existente.
3. Aplicar 3 mejoras puntuales inspiradas en `external_skills/` de `IA NANOTECNOLOGIA`, adaptadas a este dominio (sin química/toxicidad): debugger socrático, routing simple, metadata estructurada.
4. Documentar cómo el alumno obtiene su `GEMINI_API_KEY` gratuita.
5. Memoria episódica para `TutorAgent` con backend JSON local únicamente (sin Mem0, para no introducir una segunda cuenta/API que cada alumno tendría que gestionar).

## Bloque 1 — `ContentAuditorAgent`

Nuevo agente en `src/multiagent_core/content_auditor_agent.py`, heurístico puro (sin LLM, sin API key), siguiendo el patrón de dataclass tipado ya usado en `EvaluatorAgent`.

**Prerequisito — extraer el parser de fences a una función reutilizable.** `NotebookCompilerAgent.compile()` (`notebook_compiler_agent.py:120-174`) ya contiene la lógica correcta para parsear bloques ` ``` ` respetando fences anidados de longitud variable (el fix de backticks aplicado esta sesión). Esa lógica no está extraída como función independiente — antes de escribir `ContentAuditorAgent`, refactorizar esa parte de `compile()` a una función pura `extract_fenced_blocks(content: str) -> list[tuple[str, str, str]]` (retorna `(fence, language, code_content)` por bloque) en `notebook_compiler_agent.py`, y que `compile()` la consuma. `ContentAuditorAgent` importa y reutiliza esa misma función — evita reimplementar el manejo de fences anidados por segunda vez con riesgo de que un fix futuro no se replique en ambos lugares.

### API pública

```python
def audit_unit(md_path: Path) -> Dict[str, Any]:
    """Retorna {"unidad": str, "hallazgos": {...4 dimensiones...}, "total_hallazgos": int}"""

def audit_all_units(course_dir: Path) -> str:
    """Recorre las 9 unidades y genera un reporte Markdown consolidado."""
```

**El agente no autocorrige nada** — solo reporta. Las correcciones las aplica Claude tras revisar cada hallazgo con criterio (algunos son falsos positivos, como ya se vio con el diagrama ASCII de U6 detectado y corregido manualmente esta sesión).

### Dimensión 1: Rigor matemático/LaTeX

- Extraer bloques `$...$` y `$$...$$`; verificar delimitadores balanceados.
- Detectar comandos LaTeX mal formados conocidos por patrón (ej. `\DeltaG` sin espacio, en vez de `\Delta G`) — exactamente el bug ya corregido manualmente en `UNIDAD_6_MODULARIDAD_IA_MCP.md`.
- Heurística de "diagrama ASCII disfrazado de fórmula": reutilizar/extender el criterio ya implementado en `NotebookCompilerAgent._is_only_math` (bloques multilínea con ≥2 líneas que empiezan con caracteres de dibujo ASCII no son LaTeX).
- Verificar que cada símbolo matemático nuevo introducido tenga su definición cercana en el texto (heurística de proximidad de N líneas).

### Dimensión 2: Coherencia pedagógica (Hilo de Oro)

- Por unidad, verificar presencia de al menos un ciclo Pseudocódigo→Mermaid→Python→pytest (buscar bloques ` ```pseudocodigo `, ` ```mermaid `, ` ```python `, ` ```pytest ` en proximidad razonable).
- Detectar saltos de complejidad: si el primer bloque de código Python de una sección usa construcciones no introducidas antes en el documento (heurística: `class`, comprehensions, decoradores antes de cualquier ejemplo básico).
- Verificar presencia de analogías didácticas (patrón `### 💡 Analogía` ya usado consistentemente en las 9 unidades).

### Dimensión 3: Calidad de código de ejemplo

- Reutilizar `CodeAuditorAgent.audit_style()` y `audit_security()` sobre cada bloque ` ```python ` extraído del MD — no reinventar lógica ya existente.
- Nuevo: verificar con `ast` que cada `FunctionDef` tenga docstring (`ast.get_docstring`) y type hints en todos los argumentos y el retorno.

### Dimensión 4: Cumplimiento curricular

- Mapeo estático `{unidad: [subtemas]}` parseado una vez desde `docs/legado/planeacion_2023_2024/Programa_de_Asignatura_Logica_Programacion_IA_v2_extracted.txt` (texto plano con numeración `N.M` ya confirmada como parseable por regex).
- Verificar cobertura temática: cada subtema del programa oficial (ej. "6.2. Funciones Lambda, argumentos opcionales...") debe tener mención de sus palabras clave en el MD de la unidad correspondiente.
- Verificar duración/semanas: comparar el campo `**Duración:**` de cada MD contra las semanas declaradas en el programa oficial (fuente: sección "4. Estructura del Temario"). Ya se detectó una discrepancia real: el programa dice U5 = "Semanas 7-10" y U8 = "Semana 16", mientras que el Mapa del Semestre del README (Día 5) usa semanas distintas — se corrige como parte de este ciclo, sea por el agente o manualmente si el auditor la vuelve a señalar.
- Cross-check contra `implementation_plan.md` (brechas B1-B7): confirmar que las brechas marcadas como cerradas en el Día 2-3 siguen presentes.

### Tests

TDD como el resto del proyecto: `tests/test_content_auditor_agent.py` con fixtures de MD pequeños que fuercen cada tipo de hallazgo (fórmula desbalanceada, función sin docstring, subtema faltante, duración incorrecta), más una verificación de que las 9 unidades reales se auditan sin excepciones no controladas.

## Bloque 2 — Conectar los 7 agentes con su audiencia real

Clasificación por audiencia (confirmada en la conversación):

| Agente | Audiencia | Punto de entrada nuevo |
|---|---|---|
| `NotebookCompilerAgent` | Solo mantenedor del curso | Ninguno nuevo — ya documentado en README, sin cambios |
| `TutorAgent` | Alumno, uso continuo | **Presente en las 9 unidades (U0-U8), sin excepción** — celda "🛠️ Herramientas de esta unidad" en cada notebook + guía de `GEMINI_API_KEY` en `UNIDAD_0`. A diferencia de los demás agentes (que solo aparecen donde aplican temáticamente), `TutorAgent` es transversal: el alumno puede tener dudas conceptuales en cualquier unidad, así que su celda va en todas, incluida U0 donde además se explica por primera vez cómo obtener la API key. |
| `PseudocodeAgent` | Alumno, autoverificación del Hilo de Oro | Celda de ejemplo en notebooks de U2-U8 (donde aplica pseudocódigo) |
| `CodeAuditorAgent` | Alumno, auto-chequeo pre-entrega | Celda de ejemplo en notebooks, mención en checklist de entrega de `UNIDAD_8` |
| `EvaluatorAgent` | Alumno (auto-chequeo) + Docente (calificación) | Celda de ejemplo en notebooks + sección nueva en `RUBRICA_GENERAL.md` explicando el flujo de uso del docente desde terminal |
| `FlowchartAgent` | Alumno (uso directo opcional) + uso indirecto ya existente | Mención breve junto a `PseudocodeAgent`, ya que comparten propósito de visualización |
| `OrchestratorAgent` | Principalmente Docente, alumno opcional | Sección en `RUBRICA_GENERAL.md` (flujo de calificación) + mención opcional en notebooks como "reporte completo" |

**Formato de la celda "🛠️ Herramientas de esta unidad"**: una celda markdown + una celda de código al final de cada notebook (después de la última sección de contenido, antes del banco de preguntas si aplica), con:
- Explicación breve de qué agente(s) aplican a esa unidad y para qué.
- Snippet de código listo para copiar/ejecutar (`from src.multiagent_core.X import Y; ...`).
- Nota de qué requiere `GEMINI_API_KEY` (solo `TutorAgent`) vs. qué es gratis sin configuración.

Esto se inserta en los **MDs fuente** (no directamente en los `.ipynb`), siguiendo el mismo patrón ya usado para badges de Colab — el pipeline `convert_to_notebooks_smart.py` lo propaga automáticamente al regenerar.

**Reglas del snippet de `TutorAgent` (evitar reinicialización costosa):** abrir el `PersistentClient` de ChromaDB tiene un costo fijo medible (~0.3s) incluso cuando el índice ya existe. El snippet debe instanciar `TutorAgent` **una sola vez en su propia celda** (ej. `tutor = TutorAgent(course_dir=Path("."))`), y las celdas de preguntas subsecuentes deben reutilizar esa misma variable (`tutor.ask("...")`) en vez de crear una instancia nueva por pregunta. Documentar esto explícitamente en el texto de la celda markdown, no solo implícitamente en el código.

**Nota de robustez para Colab**: si `course_dir` se resuelve mal (ruta relativa que no apunta a la raíz del repo clonado), `TutorAgent` no lanza excepción — simplemente no encuentra MDs y responde sin contexto local, sin avisar por qué (fallo silencioso, no un crash). El snippet debe usar una forma robusta de resolver `course_dir` (ej. buscar hacia arriba desde el notebook hasta encontrar un archivo `UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md`, o instrucción explícita de qué ruta usar en Colab vs. local) para minimizar este riesgo. También advertir que la primera ejecución en un Colab efímero reindexa las 9 unidades desde cero (`.chroma/` no viaja en el repo, está en `.gitignore`) y tarda más que ejecuciones posteriores.

## Bloque 3 — Mejoras puntuales a agentes existentes

### 3a. Debugger socrático en `TutorAgent`

Inspirado en `external_skills/pedagogy/socratic_debugger.py` de `IA NANOTECNOLOGIA`, adaptado al dominio de este curso (sin física/química, con tipos de error de programación básica y contexto de nanotecnología del propio curso).

Nuevo método `_diagnose_error(error_message: str, code_context: str = "") -> Optional[str]` en `TutorAgent`: si `ask()` detecta que la pregunta contiene un traceback de Python (heurística: contiene "Traceback" o termina en `Error:`), retorna primero una pregunta guía en vez de la solución directa, coherente con la política pedagógica "auditar antes de confiar en el código". Ejemplos de mapeo error→pregunta (con contexto de nanopartículas/estructuras de datos del curso, no física de MD):
- `ZeroDivisionError` → pregunta sobre validar el denominador antes de dividir (conectando con el ejemplo de radio de nanopartícula ya usado en U2).
- `IndexError` en listas de coordenadas → pregunta sobre verificar `len()` antes de indexar.
- `KeyError` en diccionarios de propiedades de materiales → pregunta sobre `dict.get()` con valor default.
- Fallback genérico si no hay regla específica: pregunta abierta tipo "si fueras el intérprete de Python, ¿por qué estarías confundido aquí?".

Solo activa esta pregunta socrática en preguntas que parecen contener un error real; si la pregunta es conceptual (sin traceback), `ask()` funciona exactamente igual que hoy.

### 3b. Routing simple en `OrchestratorAgent`

Inspirado en `external_skills/routing/task_classifier.py`. Nuevo método privado `_detect_input_type(student_code: str) -> str` que clasifica la entrada como `"python_con_funciones"`, `"python_sin_funciones"`, o `"pseudocodigo"` (heurística: presencia de palabras clave UCEMICH como `INICIO`, `FUNCIÓN`, `FIN_SI` vs. sintaxis Python real). Ajusta `generate_pedagogical_report()`:
- Si es pseudocódigo: usa `PseudocodeAgent.pseudocode_to_mermaid()` en vez de `FlowchartAgent`, y omite `CodeAuditorAgent` (no aplica a pseudocódigo).
- Si es Python sin funciones: omite la generación de diagrama Mermaid (ya es el comportamiento actual de `FlowchartAgent`, que retorna mensaje de "no se encontró función" — el routing evita la llamada innecesaria).

### 3c. `SKILL_METADATA` en los 8 agentes (7 existentes + `ContentAuditorAgent`)

Dict al inicio de cada módulo, siguiendo el patrón de `external_skills/*/*.py`:
```python
SKILL_METADATA = {
    "name": "code_auditor_agent",
    "description": "Audita estilo PEP8 y seguridad OWASP de código Python de estudiantes.",
    "version": "1.0.0",
    "input": "code: str, test_file_path: Optional[Path]",
    "output": "List[str] (audit_style/audit_security) | str (generate_report)",
    "requires_api_key": False,
}
```
Cambio no invasivo — no altera comportamiento, solo agrega documentación estructurada. Se agrega a los 8 archivos.

### 3d. Refactor menor: unificar `_next_node_id`/`node_counter`

`FlowchartAgent.__init__`/`_next_node_id` (`flowchart_agent.py:15-20`) y `PseudocodeAgent.__init__`/`_next_node_id` (`pseudocode_agent.py:18-23`) tienen código idéntico para generar IDs de nodo Mermaid (`node_N`). Dado que ambos módulos ya se tocan en este ciclo (routing del Bloque 3b decide entre ellos), extraer esa lógica compartida a una utilidad común — por ejemplo una clase pequeña `MermaidNodeCounter` o una función `next_node_id(counter: int) -> tuple[str, int]` en un módulo nuevo `_mermaid_utils.py` dentro de `multiagent_core/` — y que ambas clases la reutilicen. Cambio acotado, sin alterar la salida Mermaid generada (mismos IDs, mismo formato).

### Nota de estilo para todo el código nuevo de este ciclo

`tutor_agent.py` tiene hoy varios docstrings de una sola línea sin `Args:`/`Returns:` (ej. `_get_markdown_files`, `_split_into_sections`), por debajo del estándar Google-style completo que sí cumplen `evaluator_agent.py` y `orchestrator_agent.py`. **Todo el código nuevo de este ciclo (`ContentAuditorAgent`, `_diagnose_error`, `_detect_input_type`, funciones de memoria episódica) debe seguir el estándar completo** (`Args:`, `Returns:`, `Raises:` cuando aplique) — no replicar el estilo parcial existente en partes de `tutor_agent.py`. No se reescriben las docstrings ya existentes de `tutor_agent.py` que no se tocan directamente (fuera de alcance de este ciclo).

## Bloque 4 — Memoria episódica para `TutorAgent`

Backend **solo JSON local** (sin Mem0), decisión explícita para no requerir una segunda cuenta/API por alumno.

**Firma consistente con el patrón ya establecido**: `TutorAgent.__init__` ya acepta `chroma_path: Optional[Path] = None` inyectable, usado por `tests/test_tutor_agent.py` vía fixture `chroma_path(tmp_path)` para aislar cada test. La ruta de memoria episódica debe seguir el mismo patrón — agregar `memory_path: Optional[Path] = None` al `__init__`, con default `course_dir / ".tutor_memory.json"` si no se pasa explícitamente. **No usar una ruta fija sin parámetro inyectable** — de lo contrario los tests de memoria episódica no podrían aislarse con `tmp_path` y arriesgarían escribir un archivo real en el repo durante `pytest`.

Nuevas funciones en `src/multiagent_core/tutor_agent.py` (o módulo separado `episodic_memory.py` si crece, a decidir en el plan de implementación):
- `_add_episode(question: str, answer_summary: str) -> None`: guarda en el JSON local apuntado por `self.memory_path`; se agrega esa entrada a `.gitignore` (patrón `.tutor_memory.json`, ya que el archivo vive en la raíz del curso por default).
- `_retrieve_relevant_episodes(query: str, top_k: int = 3) -> list[dict]`: búsqueda lineal por solapamiento de palabras clave (mismo patrón de fallback ya visto en `episodic_retriever.py` de referencia, sin dependencia externa).
- `ask()` se extiende: antes de construir el prompt, recupera episodios relevantes ya guardados en `.tutor_memory.json` (persisten entre sesiones de Python en la misma máquina, no solo dentro de la ejecución actual) y los añade como contexto adicional ("en una pregunta anterior discutimos X..."), mejorando continuidad conversacional entre sesiones sin requerir servidor ni login.
- Límite de episodios guardados: constante nombrada `MAX_EPISODIOS = 50` a nivel de módulo (mismo patrón que la constante existente `TOP_K_RESULTS = 3` en `tutor_agent.py:29`), no un número mágico inline.

Dado que cada alumno corre su propia instalación local (`.chroma/` y `.tutor_memory.json` son locales por diseño), no se requiere un `user_id` real — la memoria es por instalación/máquina, que en la práctica del curso equivale a "por alumno".

## Bloque 5 — Sincronizar `requirements.txt` con `environment.yml`

Hallazgo de la revisión pre-implementación: `requirements.txt` no declara `chromadb`, `pydantic` ni `rich`, pese a que `environment.yml` sí los tiene (agregados en el Día 1). Esto ya es un bug preexistente — cualquiera que instale solo con `pip install -r requirements.txt` (en vez de `conda env create -f environment.yml`) no puede ejecutar `TutorAgent` hoy por falta de `chromadb`.

El Bloque 2 agrava el impacto de este bug: al agregar celdas `TutorAgent()` a los notebooks, cualquier alumno que siga solo `requirements.txt` (documentado en el README como alternativa a conda) obtendría `ModuleNotFoundError: chromadb` la primera vez que ejecute la celda. Se corrige agregando las 3 dependencias faltantes a `requirements.txt`, alineándolo con `environment.yml`.

## Orden de implementación sugerido

El Bloque 5 (sincronizar dependencias) es el más barato y debe ir primero — es un fix de una línea que evita que el resto del trabajo se pruebe sobre un entorno inconsistente. El Bloque 1 requiere primero extraer `extract_fenced_blocks()` de `notebook_compiler_agent.py` (su prerequisito). El Bloque 2 (conectar agentes a notebooks) debe ir antes que el Bloque 4 (memoria episódica de `TutorAgent`), porque la memoria solo aporta valor una vez que el alumno realmente tiene forma de invocar `TutorAgent` repetidamente. El Bloque 3 (mejoras puntuales, incluyendo el refactor 3d que toca `FlowchartAgent`/`PseudocodeAgent`) no depende de los demás. Orden recomendado: 5 → 1 → 2 → 3 → 4.

## Fuera de alcance

- Mem0 (cloud) — explícitamente descartado por requerir cuenta adicional.
- Registry centralizado de skills (`external_skills/registry.py`) — no aplica al tamaño de este proyecto (7-8 agentes cohesivos vs. 13+ skills dispersas).
- Loops de retroalimentación automáticos (L1/L2/L3 de `IA NANOTECNOLOGIA`) — contradice la decisión ya tomada de que las correcciones de contenido las aplica Claude con revisión humana, no automáticamente.
- Generación de contenido nuevo por agentes (equivalente a `@Scientist`/`@Engineer` generando unidades desde cero) — las 9 unidades ya están escritas; este ciclo es de auditoría y conexión, no de generación.

## Verificación

1. `pytest tests/ -v --tb=short` — suite completa (63 tests actuales + nuevos de `ContentAuditorAgent`, `extract_fenced_blocks`, y memoria episódica) debe pasar al 100%.
2. `ContentAuditorAgent.audit_all_units()` corrido contra las 9 unidades reales, sin excepciones no controladas; reporte revisado manualmente para decidir qué hallazgos corregir.
3. Cada notebook regenerado (`python convert_to_notebooks_smart.py`) debe incluir la celda "🛠️ Herramientas de esta unidad" correspondiente. Verificación específica: `grep -l "TutorAgent" notebooks/*.ipynb` debe devolver las 9 unidades (U0-U8) sin excepción — es el único agente transversal a todas.
4. Prueba manual de `TutorAgent.ask()` con una pregunta que contenga un traceback simulado, confirmando que retorna pregunta socrática antes que solución directa.
5. Prueba manual de memoria episódica: llamar `ask()` en una instancia, luego crear una **segunda instancia nueva** de `TutorAgent` apuntando al mismo `memory_path` (simulando una nueva sesión de Python/notebook) y confirmar que su siguiente `ask()` recupera contexto de la pregunta anterior si son temáticamente relacionadas — esto valida que la memoria persiste entre sesiones, no solo dentro de una misma instancia en memoria RAM.
6. Confirmar que `.tutor_memory.json` está en `.gitignore`.
7. `pip install -r requirements.txt` en un entorno virtual limpio, confirmar que `import chromadb`, `import pydantic`, `import rich` funcionan sin error (verifica el fix del Bloque 5).
8. Confirmar que `notebook_compiler_agent.py` sigue generando notebooks idénticos tras extraer `extract_fenced_blocks()` (regresión: comparar output antes/después del refactor sobre al menos `UNIDAD_8_PROYECTO_INTEGRADOR.md`, que ya tiene el caso de fences anidados).
9. Confirmar que `FlowchartAgent` y `PseudocodeAgent` siguen generando el mismo Mermaid tras el refactor 3d (regresión sobre los tests ya existentes de ambos).
