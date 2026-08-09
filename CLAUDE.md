# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este proyecto

Material del curso "Lógica de Programación y Desarrollo Agéntico con IA" (UCEMICH, Ingeniería en IA y Nanotecnología, primer semestre). Combina 9 unidades teóricas en Markdown, un sistema de agentes Python en `src/multiagent_core/`, y un pipeline que convierte esas unidades en Jupyter Notebooks. `implementation_plan.md` es el documento maestro de auditoría pedagógica que originó el trabajo hecho hasta ahora (infraestructura, cierre de brechas curriculares, sistema de agentes, pulido de notebooks — ya completado). Trabajo en curso posterior a ese plan vive en `docs/superpowers/specs/` y `docs/superpowers/plans/`.

## Comandos esenciales

```bash
# Activar entorno (conda, preferido — trae todas las dependencias incluyendo chromadb)
conda activate ia_logprog

# Correr toda la suite de tests
pytest tests/ -v --tb=short

# Correr un solo archivo de test
pytest tests/test_tutor_agent.py -v

# Correr un solo test
pytest tests/test_tutor_agent.py::TestAsk::test_construye_prompt_con_contexto_y_pregunta -v

# Formatear/lint (en ese orden) antes de dar por terminado cualquier cambio en src/
python -m isort src/multiagent_core/<archivo>.py
python -m black src/multiagent_core/<archivo>.py
python -m ruff check src/multiagent_core/<archivo>.py

# Regenerar los 9 notebooks tras editar cualquier UNIDAD_*.md
python convert_to_notebooks_smart.py
```

Requiere Node.js instalado (`npx` en el PATH) — los diagramas Mermaid se renderizan a SVG vía `@mermaid-js/mermaid-cli`; el script verifica esto al inicio y falla con instrucciones claras si falta.

No hay `pyproject.toml`/`pytest.ini` — el descubrimiento de tests funciona porque `conftest.py` en la raíz inserta el proyecto en `sys.path`, y `src/` y `src/multiagent_core/` tienen `__init__.py`. Los imports en el código y en los tests son siempre absolutos desde la raíz: `from src.multiagent_core.tutor_agent import TutorAgent`.

## Arquitectura del sistema de agentes

8 agentes en `src/multiagent_core/`, cada uno con responsabilidad única, heurísticos y sin LLM salvo `TutorAgent`:

- **`NotebookCompilerAgent`** (`notebook_compiler_agent.py`) — parsea un `UNIDAD_*.md` línea por línea y genera el `.ipynb` correspondiente. Reconoce fences de longitud variable (3+ backticks) para soportar bloques anidados (p. ej. un ejemplo de `.md` dentro de un bloque ` ```markdown `); el fence de cierre debe coincidir exactamente en longitud con el de apertura, no basta con 3 backticks cualquiera. Usa `MathAgent` (clase interna) para traducir símbolos Unicode matemáticos a LaTeX, y `FlowchartAgent` para inyectar diagramas Mermaid automáticos cuando detecta una función de más de 5 líneas. `_is_only_math()` distingue fórmulas LaTeX reales de diagramas de arte ASCII que casualmente contienen un símbolo griego (heurística: ≥2 líneas que empiezan con caracteres de dibujo como `|`, `*`, `^`).
- **`FlowchartAgent`** — AST de Python → diagrama Mermaid (`graph TD`).
- **`PseudocodeAgent`** — traduce entre pseudocódigo UCEMICH (la sintaxis propia del curso: `SI/SINO/FIN_SI`, `PARA/FIN_PARA`, `MIENTRAS/FIN_MIENTRAS`, `FUNCIÓN/RETORNAR/FIN_FUNCIÓN`, definida en `UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md`), Mermaid, y esqueletos Python.
- **`CodeAuditorAgent`** — análisis estático (AST + regex) de estilo PEP8 y seguridad OWASP sobre código de estudiantes; también ejecuta pytest vía subprocess (`run_pytest`).
- **`EvaluatorAgent`** — califica código contra los 4 criterios de la Rúbrica Genérica (`RUBRICA_GENERAL.md`), reutilizando `CodeAuditorAgent` internamente.
- **`OrchestratorAgent`** — coordina Auditor + Flowchart + Evaluator en un reporte Markdown único.
- **`TutorAgent`** — el único agente con LLM: RAG semántico con ChromaDB sobre los 9 `UNIDAD_*.md` (indexados por sección, citando fuente exacta) + Gemini para responder, con debugger socrático (`_diagnose_error`) y memoria episódica local (`_add_episode`/`_retrieve_relevant_episodes`, coincidencia por prefijo). Requiere `GEMINI_API_KEY` en el entorno o `.env`; sin ella, no falla al instanciarse (solo `ask()` retorna un mensaje de error controlado con el contexto local igual). `chroma_path` y `memory_path` son inyectables en el constructor específicamente para poder aislar tests con `tmp_path` — cualquier ruta de archivo/directorio nueva que se agregue a un agente debe seguir ese mismo patrón, no hardcodear rutas.
- **`ContentAuditorAgent`** — heurístico, sin LLM: audita el contenido pedagógico de un `UNIDAD_*.md` en 4 dimensiones (LaTeX malformado, ciclo Hilo de Oro incompleto, código de ejemplo sin docstring/type hints o con riesgos OWASP, alineación curricular contra el programa oficial en `docs/legado/`). Reutiliza `extract_fenced_blocks()` (función a nivel de módulo en `notebook_compiler_agent.py`) y `CodeAuditorAgent` internamente.

**Pipeline de contenido**: `UNIDAD_*.md` (fuente de verdad) → `convert_to_notebooks_smart.py` → `NotebookCompilerAgent.compile()` → `notebooks/*.ipynb`. Los notebooks nunca se editan a mano; cualquier cambio de contenido va al `.md` y se regenera. `convert_to_notebooks_smart.py` lista explícitamente los 9 archivos a convertir (`UNIDAD_0` a `UNIDAD_8`).

## Convenciones del contenido pedagógico

- **Hilo de Oro**: cada concepto nuevo del curso sigue el flujo Pseudocódigo → Mermaid → Python → pytest. Al escribir o revisar contenido de unidades, verificar que este ciclo esté completo.
- **Política de IA progresiva**: U1-U3 sin IA para código (solo consultas conceptuales), U4-U6 con Copiloto documentado, U7-U8 IA como herramienta principal con auditoría. Tabla completa en `UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md` sección 0.5.
- **Contexto de nanotecnología obligatorio**: todo ejemplo de código usa datos/problemas de nanotecnología (radios de nanopartículas, redes cristalinas, coeficientes de difusión), nunca ejemplos genéricos de programación.
- **Links a ellibrodepython.com**: aparecen al final de secciones teóricas en U1-U6 (fundamentos de sintaxis Python); deliberadamente ausentes en U7-U8 (código de producción/proyecto integrador, no fundamentos). No agregar sin verificar que la unidad efectivamente enseña sintaxis básica nueva.
- **`docs/legado/`** contiene material histórico del curso 2023-2024 y el programa de asignatura oficial (`docs/legado/planeacion_2023_2024/Programa_de_Asignatura_Logica_Programacion_IA_v2_extracted.txt`, texto plano con numeración `N.M` parseable por regex) — está en `.gitignore`, existe localmente pero no se publica en GitHub.

## Flujo de trabajo esperado para cambios grandes

Este proyecto usa el flujo `superpowers:brainstorming` → spec en `docs/superpowers/specs/` → `superpowers:writing-plans` → plan en `docs/superpowers/plans/` para cualquier trabajo no trivial (nuevo agente, cambio de arquitectura, conexión de features existentes). Los specs y planes ya escritos documentan decisiones de diseño y su razonamiento — revisarlos antes de proponer algo que pueda solaparse.

TDD estricto en todo el código de `src/multiagent_core/`: test que falla primero, luego implementación mínima. Los tests existentes son "tests de caracterización" para agentes preexistentes y TDD real para agentes nuevos — mismo estándar de rigor para ambos casos.


# PROJECT_PLAN Integration
# Added by Claude Config Manager Extension

When working on this project, always refer to and maintain the project plan located at `PROJECT_PLAN.md` in the workspace root.

**Instructions for Claude Code:**
1. **Read the project plan first** - Always check `PROJECT_PLAN.md` when starting work to understand the project context, architecture, and current priorities.
2. **Update the project plan regularly** - When making significant changes, discoveries, or completing major features, update the relevant sections in PROJECT_PLAN.md to keep it current.
3. **Use it for context** - Reference the project plan when making architectural decisions, understanding dependencies, or explaining code to ensure consistency with project goals.

**Plan Mode Integration:**
- **When entering plan mode**: Read the current PROJECT_PLAN.md to understand existing context and priorities
- **During plan mode**: Build upon and refine the existing project plan structure
- **When exiting plan mode**: ALWAYS update PROJECT_PLAN.md with your new plan details, replacing or enhancing the relevant sections (Architecture, TODO, Development Workflow, etc.)
- **Plan persistence**: The PROJECT_PLAN.md serves as the permanent repository for all planning work - plan mode should treat it as the single source of truth

This ensures better code quality and maintains project knowledge continuity across different Claude Code sessions and plan mode iterations.
