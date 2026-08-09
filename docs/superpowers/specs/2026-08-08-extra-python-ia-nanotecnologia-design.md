# EXTRA_PYTHON_IA_NANOTECNOLOGIA — Diseño

## Contexto y objetivo

El curso UCEMICH ("Lógica de Programación y Desarrollo Agéntico con IA") ya cubre la lógica formal de programación (bucles, condicionales, funciones, function calling) con más rigor que el curso público "AI Python for Beginners" de DeepLearning.AI. Sin embargo, ese material público sí tiene algo que el temario oficial no enseña explícitamente como práctica de código: el patrón **"Python como orquestador de llamadas a un LLM"** (prompts como f-strings, iterar con `for` preguntando a un LLM, extraer datos estructurados de texto libre) — repetido una y otra vez a lo largo de sus lecciones.

El notebook original (`docs/legado/AI Python for Beginners-20260807T143600Z-1-001/AI Python for Beginners/AI Python for Beginners.ipynb`, 620 celdas) fue evaluado a fondo:
- Usa `openai`/`gpt-4o-mini` con `helper_functions.py` externo — no aplica directamente al proyecto (que usa Gemini vía `google.genai`, mismo patrón que `TutorAgent`).
- Sus ejemplos son genéricos/turísticos (journals de viaje, recetas, clima) — violan la convención del proyecto de "contexto de nanotecnología obligatorio en todo ejemplo de código".
- Las celdas 587-619 son anotaciones/experimentos personales del propio usuario, con código roto (indentación inválida) y fragmentos sueltos — no forman parte del curso oficial y se descartan.
- Está en inglés.

Objetivo: producir una pieza **complementaria, opcional, independiente** de la secuencia U0-U8, que enseñe ese patrón con ejemplos 100% de nanotecnología, en español, usando Gemini — y que de paso cierre huecos reales de sintaxis Python que ni el notebook original ni las 9 unidades cubren a fondo (confirmados contra el índice real de `ellibrodepython.com`, la referencia que el curso ya cita en U1-U6).

## Alcance

**Dentro de alcance:**
- Un archivo fuente `EXTRA_PYTHON_IA_NANOTECNOLOGIA.md` en la raíz del repo, mismo formato que las 9 unidades (fences ` ```python `, headers, badge de Colab).
- Datos de apoyo en `data/bitacoras_laboratorio/` (bitácoras `.txt` de síntesis de nanopartículas, un CSV de experimentos).
- Integración al pipeline existente: agregar el nuevo `.md` a la lista de `convert_to_notebooks_smart.py`, generando `notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA.ipynb` con `NotebookCompilerAgent` sin modificarlo.

**Fuera de alcance (explícitamente):**
- No se modifica ninguna `UNIDAD_*.md` existente.
- No se modifica `RUBRICA_GENERAL.md` — esta pieza no es evaluada salvo decisión posterior explícita.
- No se construye el `ContentIntegratorAgent` (idea de integración distribuida en U2/U5/U6) — queda pausada para retomar después, de forma independiente a este trabajo.
- No se modifica `NotebookCompilerAgent`, `FlowchartAgent`, ni ningún agente existente.

## Estructura de contenido

Adaptación de las ~10 lecciones del original + 6 secciones nuevas que cierran huecos de sintaxis (confirmados ausentes tanto en el original como en las 9 unidades, comparando contra el índice de `ellibrodepython.com`). Orden propuesto (número final de sección se ajusta al escribir, este es el mapa temático):

1. **Fundamentos + primer prompt a un LLM** — strings, variables, `type()`. `get_llm_response(prompt)` se define en la primera celda de código del notebook (usando `genai.Client`, mismo patrón que `tutor_agent.py`), visible y editable — sin archivo `helper_functions.py` externo, para no ocultar el código real detrás de un import de caja negra.
2. **F-strings con formato** *(nuevo — hueco real)* — construir prompts con datos interpolados y formato numérico (`:.2f`), ejemplo: reportar un diámetro de nanopartícula con precisión controlada.
3. **Automatizando tareas con listas + IA** — clasificar bitácoras de laboratorio con `for`, patrón "Relevante/No relevante" (adaptado del original, ya esbozado y aprobado en una iteración previa de esta conversación).
4. **List comprehensions** *(nuevo)* — filtrar bitácoras o resultados numéricos de forma concisa.
5. **`enumerate`/`zip`** *(nuevo)* — recorrer listas paralelas de materiales y sus propiedades.
6. **Diccionarios para estructurar datos experimentales + IA** — priorizar/organizar resultados de síntesis.
7. **Tuplas y sets** *(nuevo)* — coordenadas atómicas inmutables (tupla), conjunto de materiales únicos detectados en un lote de bitácoras (set).
8. **Comparaciones lógicas y decisiones asistidas por IA** — condicionar acciones según resultados de una consulta al LLM.
9. **Manejo de excepciones** *(nuevo — conecta directo con el hilo conductor)* — `try`/`except` alrededor de la llamada al LLM (fallo de red, respuesta inesperada), mismo espíritu que el manejo de errores ya presente en `TutorAgent.ask()`.
10. **Archivos de texto y CSV** — leer bitácoras de síntesis, extraer reactivo límite/rendimiento con IA (sección ya esbozada y aprobada: "Iterando con IA: Clasificar y Extraer Información de Bitácoras de Laboratorio").
11. **Funciones propias reutilizables** — conversión de unidades, cálculos de propiedades de nanopartículas.
12. **`*args`/`**kwargs`** *(nuevo)* — generalizar una función que arma prompts con número variable de parámetros experimentales.
13. **Paquetes built-in y de terceros** — `math`/`statistics`/`random` y `pandas`/`matplotlib` aplicados a datasets de nanotecnología (puede reusar `data/nanoparticulas_ejemplo.csv` ya existente en el proyecto).
14. **Instalación de paquetes con `pip`** — igual que el original, adaptado al contexto Colab del proyecto (mismo patrón `if 'google.colab' in sys.modules:` ya usado en las 9 unidades).
15. **Consumir una API REST real: PubChem PUG REST** *(reemplaza la lección de clima del original)* — `requests.get()` a `pubchem.ncbi.nlm.nih.gov` para consultar propiedades (peso molecular, fórmula) de materiales ya recurrentes en el curso (oro, plata, TiO2), sin API key. Verificado en vivo que el endpoint responde correctamente. El resultado se interpreta/contextualiza con una llamada a `get_llm_response`.
16. **Cierre: `genai.Client` en detalle** — system prompt, temperatura, mismo patrón que ya usa `TutorAgent`, cerrando el círculo de "cómo funciona por dentro lo que usaste en toda la pieza".

Cada sección: intro breve → 1-2 bloques de código comentado (con docstrings estilo Google donde aplique, consistente con la convención del proyecto) → ejercicio práctico con contexto de nanotecnología → enlace 📖 a `ellibrodepython.com` donde exista una lección específica de ese sitio relacionada (no se copia contenido, solo se referencia, igual que U1-U6).

## Testing y verificación

- Tras escribir el `.md`, correr `python convert_to_notebooks_smart.py` y confirmar que el nuevo notebook se genera sin error, incluido en el conteo de "Convertidos con éxito".
- `ContentAuditorAgent` corre automáticamente sobre el nuevo `.md` como parte de `audit_all_units()` — revisar el reporte regenerado para confirmar que no introduce hallazgos de calidad nuevos (LaTeX malformado, código sin docstring, etc.), aceptando que el hallazgo "Ciclo del Hilo de Oro incompleto" es esperado y no aplica aquí (esta pieza no sigue el ciclo Pseudocódigo→Mermaid→Python→pytest de las 9 unidades, es una pieza de práctica libre, no un laboratorio formal).
- Verificación manual: abrir el notebook generado en Colab (mismo patrón de clonado del repo + Secrets ya usado en las 9 unidades) y confirmar que al menos 2-3 celdas de ejemplo (una por cada tipo: `for`+LLM, extracción de archivo, consulta a PubChem) ejecutan correctamente.
