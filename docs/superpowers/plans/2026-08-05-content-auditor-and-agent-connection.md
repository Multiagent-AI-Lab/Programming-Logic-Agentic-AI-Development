# ContentAuditorAgent + Conexión de Agentes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cerrar el hueco de auditoría de contenido pedagógico con un `ContentAuditorAgent` nuevo, y conectar los 6 agentes sin punto de entrada real (`TutorAgent`, `PseudocodeAgent`, `CodeAuditorAgent`, `EvaluatorAgent`, `FlowchartAgent`, `OrchestratorAgent`) con su audiencia real (alumno y/o docente) mediante celdas ejecutables en los 9 notebooks del curso.

**Architecture:** Se agrega un octavo agente heurístico (`content_auditor_agent.py`) que reutiliza lógica ya existente (`CodeAuditorAgent`, y una función de parseo de fences extraída de `NotebookCompilerAgent`). Los 9 MDs fuente reciben una celda nueva "🛠️ Herramientas de esta unidad" que se propaga a los `.ipynb` vía el pipeline `convert_to_notebooks_smart.py` ya existente — ningún notebook se edita a mano. `TutorAgent` gana memoria episódica JSON local y un debugger socrático; `OrchestratorAgent` gana routing simple por tipo de entrada.

**Tech Stack:** Python 3.11, pytest (TDD), `ast`/`re`/`json` de stdlib, `nbformat`, `chromadb` (ya en uso), sin LLM nuevo, sin dependencias nuevas de red.

## Global Constraints

- TDD estricto en todo código nuevo: test que falla primero, luego implementación mínima, confirmado por el usuario en toda la sesión previa.
- Ningún agente nuevo requiere pago ni API key salvo `TutorAgent` (ya usa `GEMINI_API_KEY`, gratuita).
- Estilo: type hints completos, docstrings Google-style completas (`Args:`, `Returns:`) en TODO el código nuevo — no replicar el estilo parcial de una sola línea que tiene hoy parte de `tutor_agent.py`.
- Sin números mágicos: usar constantes nombradas a nivel de módulo (patrón ya establecido: `TOP_K_RESULTS = 3` en `tutor_agent.py:29`).
- Firma pública inyectable para rutas de test: cualquier ruta de archivo/directorio que un agente use debe ser parámetro opcional del constructor (patrón ya establecido: `chroma_path: Optional[Path] = None` en `TutorAgent.__init__`), nunca hardcodeada, para permitir aislar tests con `tmp_path`.
- Tras `black`/`isort`/`ruff` (herramientas ya instaladas en `environment.yml`), correr sobre cualquier archivo `.py` nuevo o modificado antes de dar una tarea por terminada.
- Después de cualquier cambio a un MD fuente de unidad, regenerar notebooks con `python convert_to_notebooks_smart.py` y confirmar "Convertidos con éxito: 9" sin errores.
- Después de cualquier cambio a código en `src/multiagent_core/`, correr `pytest tests/ -v --tb=short` y confirmar 100% passing antes de commitear.

---

## File Structure

Archivos que este plan crea o modifica:

**Nuevos:**
- `src/multiagent_core/content_auditor_agent.py` — el agente nuevo (Bloque 1)
- `tests/test_content_auditor_agent.py`
- `src/multiagent_core/_mermaid_utils.py` — utilidad compartida de generación de IDs de nodo Mermaid (Bloque 3d)
- `tests/test_mermaid_utils.py`

**Modificados:**
- `requirements.txt` — agregar `chromadb`, `pydantic`, `rich` (Bloque 5)
- `src/multiagent_core/notebook_compiler_agent.py` — extraer `extract_fenced_blocks()` (prerequisito Bloque 1)
- `tests/test_notebook_compiler_agent.py` — tests de la función extraída
- `src/multiagent_core/tutor_agent.py` — debugger socrático (3a) + memoria episódica (Bloque 4)
- `tests/test_tutor_agent.py` — tests de ambas features
- `src/multiagent_core/orchestrator_agent.py` — routing simple (3b)
- `tests/test_orchestrator_agent.py` — tests de routing
- `src/multiagent_core/flowchart_agent.py` — usa `_mermaid_utils` (3d)
- `src/multiagent_core/pseudocode_agent.py` — usa `_mermaid_utils` (3d)
- Los 8 agentes existentes + `content_auditor_agent.py` — agregar `SKILL_METADATA` (3c)
- Los 9 `UNIDAD_*.md` — celda "🛠️ Herramientas de esta unidad" (Bloque 2)
- `RUBRICA_GENERAL.md` — sección de flujo de uso del docente para `EvaluatorAgent`/`OrchestratorAgent` (Bloque 2)
- `.gitignore` — agregar `.tutor_memory.json` (Bloque 4)

---

## Bloque 5: Sincronizar dependencias (primero — es el más barato)

### Task 1: Agregar dependencias faltantes a requirements.txt

**Files:**
- Modify: `requirements.txt:1-3`

**Interfaces:**
- Consumes: nada (cambio de archivo de texto plano)
- Produces: `requirements.txt` alineado con `environment.yml`

- [ ] **Step 1: Ver el estado actual**

Ejecutar: `head -5 requirements.txt` y confirmar que faltan `chromadb`, `pydantic`, `rich` (ya confirmado en la investigación previa, este paso es solo para que el ejecutor lo vea con sus propios ojos antes de editar).

- [ ] **Step 2: Editar el archivo**

Agregar estas 3 líneas después de `ipytest>=0.14.0` en `requirements.txt`, replicando exactamente los rangos de versión ya usados en `environment.yml`:

```
rich>=13.0.0
pydantic>=2.0.0,<3.0.0
chromadb>=0.5.0
```

- [ ] **Step 3: Verificar en un entorno limpio**

```bash
python -m venv /tmp/test_reqs_venv
/tmp/test_reqs_venv/Scripts/python -m pip install -r requirements.txt -q
/tmp/test_reqs_venv/Scripts/python -c "import chromadb, pydantic, rich; print('OK')"
```

Expected: imprime `OK` sin `ModuleNotFoundError`.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "fix: sincronizar requirements.txt con environment.yml (chromadb, pydantic, rich)"
```

---

## Bloque 1 (parte A — prerequisito): Extraer `extract_fenced_blocks()`

### Task 2: Escribir el test de la función `extract_fenced_blocks`

**Files:**
- Test: `tests/test_notebook_compiler_agent.py` (agregar clase nueva al final del archivo)

**Interfaces:**
- Consumes: nada
- Produces: contrato esperado de `extract_fenced_blocks(content: str) -> list[tuple[str, str, str]]` que la Task 3 debe implementar — cada tupla es `(fence, language, code_content)`.

- [ ] **Step 1: Escribir los tests**

Agregar al final de `tests/test_notebook_compiler_agent.py` (después de la clase `TestFencesAnidados` existente):

```python
class TestExtractFencedBlocks:
    def test_extrae_bloque_python_simple(self):
        from src.multiagent_core.notebook_compiler_agent import extract_fenced_blocks

        content = "Texto antes\n\n```python\nx = 1\n```\n\nTexto después"
        bloques = extract_fenced_blocks(content)

        assert len(bloques) == 1
        fence, language, code = bloques[0]
        assert fence == "```"
        assert language == "python"
        assert code == "x = 1"

    def test_extrae_multiples_bloques(self):
        from src.multiagent_core.notebook_compiler_agent import extract_fenced_blocks

        content = "```python\na = 1\n```\n\ntexto\n\n```bash\necho hola\n```"
        bloques = extract_fenced_blocks(content)

        assert len(bloques) == 2
        assert bloques[0][1] == "python"
        assert bloques[1][1] == "bash"

    def test_respeta_fence_de_4_backticks_con_anidado_de_3(self):
        from src.multiagent_core.notebook_compiler_agent import extract_fenced_blocks

        content = "````markdown\n# Titulo\n\n```python\ndef f():\n    pass\n```\n````"
        bloques = extract_fenced_blocks(content)

        assert len(bloques) == 1
        fence, language, code = bloques[0]
        assert fence == "````"
        assert language == "markdown"
        assert "```python" in code
        assert "def f():" in code

    def test_sin_bloques_retorna_lista_vacia(self):
        from src.multiagent_core.notebook_compiler_agent import extract_fenced_blocks

        assert extract_fenced_blocks("solo texto plano, sin fences") == []
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_notebook_compiler_agent.py::TestExtractFencedBlocks -v`
Expected: FAIL con `ImportError: cannot import name 'extract_fenced_blocks'`

- [ ] **Step 3: Commit del test (RED)**

```bash
git add tests/test_notebook_compiler_agent.py
git commit -m "test: agregar tests para extract_fenced_blocks (RED)"
```

### Task 3: Implementar `extract_fenced_blocks()` y refactorizar `compile()` para usarla

**Files:**
- Modify: `src/multiagent_core/notebook_compiler_agent.py:94-189` (método `compile`)

**Interfaces:**
- Consumes: nada nuevo
- Produces: `extract_fenced_blocks(content: str) -> list[tuple[str, str, str]]`, función a nivel de módulo (no método de clase, para que `ContentAuditorAgent` la importe sin instanciar `NotebookCompilerAgent`).

- [ ] **Step 1: Escribir la función extraída**

Agregar esta función a nivel de módulo en `src/multiagent_core/notebook_compiler_agent.py`, **antes** de la clase `NotebookCompilerAgent` (después de la clase `MathAgent`, línea 85):

```python
def extract_fenced_blocks(content: str) -> list[tuple[str, str, str]]:
    """Extrae bloques de código delimitados por fences ``` de un texto Markdown.

    Respeta fences anidados: un bloque exterior de 4+ backticks que contiene
    fences de 3 backticks en su interior se extrae completo, sin cortarse en
    el primer fence interno (comportamiento CommonMark estándar).

    Args:
        content: Texto Markdown completo a escanear.

    Returns:
        Lista de tuplas (fence, language, code_content) en orden de aparición.
        `fence` es la secuencia de backticks original (p. ej. "```" o "````").
        `language` es el identificador de lenguaje tras el fence (puede ser "").
        `code_content` es el texto entre el fence de apertura y cierre.
    """
    lines = content.split("\n")
    blocks: list[tuple[str, str, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        fence_match = re.match(r"^(`{3,})(.*)$", line)
        if fence_match:
            fence = fence_match.group(1)
            language = fence_match.group(2).strip()
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != fence:
                code_lines.append(lines[i])
                i += 1
            blocks.append((fence, language, "\n".join(code_lines)))
        i += 1
    return blocks
```

- [ ] **Step 2: Ejecutar los tests de la Task 2 y confirmar que pasan**

Run: `pytest tests/test_notebook_compiler_agent.py::TestExtractFencedBlocks -v`
Expected: 4 tests PASS

- [ ] **Step 3: Refactorizar `compile()` para consumir la función extraída**

Reemplazar el método `compile` completo en `src/multiagent_core/notebook_compiler_agent.py` (líneas 94-189) por esta versión que usa `extract_fenced_blocks` internamente, preservando exactamente el mismo comportamiento observable (mismo manejo de `current_md`, `_is_only_math`, generación de Mermaid):

```python
    def compile(self, md_filepath: Path, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        nb_path = output_dir / (md_filepath.stem + ".ipynb")

        with open(md_filepath, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        nb = nbf.v4.new_notebook()

        nb.metadata = {
            "kernelspec": {
                "display_name": "Python 3.11",
                "language": "python",
                "name": "python3",
            }
        }

        current_md: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]

            fence_match = re.match(r"^(`{3,})(.*)$", line)
            if fence_match:
                fence = fence_match.group(1)
                language = fence_match.group(2).strip()
                code_lines: list[str] = []
                i += 1
                while i < len(lines) and lines[i].strip() != fence:
                    code_lines.append(lines[i])
                    i += 1

                code_content = "\n".join(code_lines)

                if current_md:
                    md_text = "\n".join(current_md)
                    nb.cells.append(
                        nbf.v4.new_markdown_cell(self.math_agent.process_latex(md_text))
                    )
                    current_md = []

                if language == "python" or language == "":
                    if not self._is_only_math(code_content):
                        nb.cells.append(nbf.v4.new_code_cell(code_content.strip()))

                        if "def " in code_content and len(code_lines) > 5:
                            mermaid_flow = self.flowchart_agent.build_mermaid_flowchart(
                                code_content
                            )
                            if "graph TD" in mermaid_flow:
                                nb.cells.append(
                                    nbf.v4.new_markdown_cell(
                                        f"#### 📊 Diagrama de Flujo Autogenerado:\n\n```mermaid\n{mermaid_flow}\n```"
                                    )
                                )
                    else:
                        nb.cells.append(
                            nbf.v4.new_markdown_cell(
                                f"$$\\displaystyle{{{self.math_agent.process_latex(code_content)}}}$$"
                            )
                        )
                else:
                    nb.cells.append(
                        nbf.v4.new_markdown_cell(
                            f"{fence}{language}\n{code_content}\n{fence}"
                        )
                    )
                i += 1
            else:
                current_md.append(line)
                i += 1

        if current_md:
            md_text = "\n".join(current_md)
            nb.cells.append(
                nbf.v4.new_markdown_cell(self.math_agent.process_latex(md_text))
            )

        with open(nb_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)

        print(f"  [OK] Compilado: {nb_path.name}")
        return nb_path
```

Nota: este refactor mantiene la lógica inline en `compile()` en vez de forzar una reescritura total a base de `extract_fenced_blocks()`, porque `compile()` necesita el índice `i` para intercalar el `current_md` acumulado entre bloques — extraer completamente rompería esa intercalación. `extract_fenced_blocks()` queda disponible como función independiente para `ContentAuditorAgent` (Task 6), que sí puede iterar bloques sin necesidad de intercalar markdown.

- [ ] **Step 4: Correr toda la suite de notebook_compiler_agent para confirmar cero regresión**

Run: `pytest tests/test_notebook_compiler_agent.py -v --tb=short`
Expected: todos los tests (incluyendo `TestFencesAnidados` y `TestExtractFencedBlocks`) PASS — 15 tests en total en este archivo.

- [ ] **Step 5: Regenerar los 9 notebooks y confirmar que U8 sigue bien**

```bash
python convert_to_notebooks_smart.py
python -c "
import json
nb = json.load(open('notebooks/UNIDAD_8_PROYECTO_INTEGRADOR.ipynb', encoding='utf-8'))
for cell in nb['cells']:
    src = ''.join(cell['source'])
    if 'Entrega de Laboratorio de Nanotecnolog' in src:
        assert src.strip().startswith('\`\`\`\`markdown')
        assert src.strip().endswith('\`\`\`\`')
        print('OK: fence de 4 backticks preservado tras refactor')
        break
"
```

Expected: imprime `OK: fence de 4 backticks preservado tras refactor` sin `AssertionError`.

- [ ] **Step 6: black/isort/ruff**

```bash
python -m isort src/multiagent_core/notebook_compiler_agent.py
python -m black src/multiagent_core/notebook_compiler_agent.py
python -m ruff check src/multiagent_core/notebook_compiler_agent.py
```

Expected: sin cambios de isort/black más allá de formato, ruff sin hallazgos.

- [ ] **Step 7: Commit**

```bash
git add src/multiagent_core/notebook_compiler_agent.py notebooks/
git commit -m "refactor: extraer extract_fenced_blocks() de NotebookCompilerAgent.compile()"
```

---

## Bloque 1 (parte B): `ContentAuditorAgent`

### Task 4: Escribir tests de Dimensión 1 (LaTeX) y Dimensión 3 (calidad de código)

**Files:**
- Test: `tests/test_content_auditor_agent.py` (nuevo)

**Interfaces:**
- Consumes: `extract_fenced_blocks` de `src.multiagent_core.notebook_compiler_agent` (Task 3), `CodeAuditorAgent` de `src.multiagent_core.code_auditor_agent` (ya existe)
- Produces: contrato esperado de `ContentAuditorAgent.audit_unit(md_path: Path) -> Dict[str, Any]` que la Task 5 debe implementar.

- [ ] **Step 1: Escribir los tests**

```python
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
        md_path.write_text(
            "# Test\n\n$$\\DeltaG = 5$$\n", encoding="utf-8"
        )
        resultado = auditor.audit_unit(md_path)
        assert any("DeltaG" in h or "\\Delta" in h for h in resultado["hallazgos"]["latex"])

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
            '# Test\n\n```python\n'
            'def calcular(x: float) -> float:\n'
            '    """Duplica un valor.\n\n'
            '    Args:\n'
            '        x: Valor de entrada.\n\n'
            '    Returns:\n'
            '        El valor duplicado.\n'
            '    """\n'
            '    return x * 2\n```\n',
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
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_content_auditor_agent.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'src.multiagent_core.content_auditor_agent'`

- [ ] **Step 3: Commit (RED)**

```bash
git add tests/test_content_auditor_agent.py
git commit -m "test: agregar tests de dimensiones LaTeX y código para ContentAuditorAgent (RED)"
```

### Task 5: Implementar Dimensión 1 (LaTeX) y Dimensión 3 (código) de `ContentAuditorAgent`

**Files:**
- Create: `src/multiagent_core/content_auditor_agent.py`

**Interfaces:**
- Consumes: `extract_fenced_blocks(content: str) -> list[tuple[str, str, str]]` (Task 3), `CodeAuditorAgent().audit_style(code: str) -> List[str]` y `.audit_security(code: str) -> List[str]` (ya existen)
- Produces: `ContentAuditorAgent.audit_unit(md_path: Path) -> Dict[str, Any]` con claves `unidad`, `hallazgos` (dict con `latex`, `pedagogico`, `codigo`, `curricular`), `total_hallazgos`.

- [ ] **Step 1: Escribir la implementación (parcial — solo dimensiones LaTeX y código; pedagógico/curricular en Task 7)**

```python
"""
Agente Auditor de Contenido (ContentAuditorAgent) - Lógica de Programación UCEMICH 🔍
======================================================================================

Audita las 9 unidades del curso (contenido escrito por el mantenedor, no por
estudiantes) contra 4 dimensiones de calidad: rigor matemático/LaTeX,
coherencia pedagógica (Hilo de Oro), calidad de código de ejemplo, y
cumplimiento curricular contra el programa oficial. Heurístico puro, sin LLM.
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List

from .code_auditor_agent import CodeAuditorAgent
from .notebook_compiler_agent import extract_fenced_blocks

SKILL_METADATA = {
    "name": "content_auditor_agent",
    "description": "Audita el contenido pedagógico de las unidades del curso (LaTeX, pedagogía, código, cumplimiento curricular).",
    "version": "1.0.0",
    "input": "md_path: Path (audit_unit) | course_dir: Path (audit_all_units)",
    "output": "Dict[str, Any] con hallazgos por dimensión (audit_unit) | str Markdown (audit_all_units)",
    "requires_api_key": False,
}

LATEX_KNOWN_MALFORMED = {
    r"\DeltaG": r"\Delta G",
    r"\DeltaH": r"\Delta H",
    r"\DeltaS": r"\Delta S",
}


class ContentAuditorAgent:
    """Agente que audita el contenido pedagógico de las unidades del curso."""

    def __init__(self) -> None:
        self.code_auditor = CodeAuditorAgent()

    def _audit_latex(self, content: str) -> List[str]:
        """Detecta delimitadores LaTeX desbalanceados y comandos mal formados.

        Args:
            content: Texto completo del MD de la unidad.

        Returns:
            Lista de descripciones de hallazgos; vacía si no hay problemas.
        """
        hallazgos: List[str] = []

        dollar_count = content.count("$") - 2 * content.count("$$")
        if dollar_count % 2 != 0:
            hallazgos.append(
                "Delimitadores '$' desbalanceados: hay un número impar de '$' "
                "simples fuera de bloques '$$...$$', lo que sugiere una fórmula "
                "sin cerrar."
            )

        for malformado, correcto in LATEX_KNOWN_MALFORMED.items():
            if malformado in content:
                hallazgos.append(
                    f"Comando LaTeX mal formado: '{malformado}' encontrado; "
                    f"debería ser '{correcto}' (falta espacio, KaTeX no lo renderiza)."
                )

        return hallazgos

    def _audit_codigo(self, python_blocks: List[str]) -> List[str]:
        """Audita bloques de código Python de ejemplo (docstrings, type hints, estilo).

        Args:
            python_blocks: Lista de bloques de código Python extraídos del MD.

        Returns:
            Lista de descripciones de hallazgos; vacía si no hay problemas.
        """
        hallazgos: List[str] = []

        for code in python_blocks:
            hallazgos.extend(self.code_auditor.audit_style(code))
            hallazgos.extend(self.code_auditor.audit_security(code))

            try:
                tree = ast.parse(code)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                if ast.get_docstring(node) is None:
                    hallazgos.append(
                        f"Función '{node.name}' sin docstring en el código de ejemplo."
                    )
                args_sin_tipo = [
                    a.arg for a in node.args.args if a.annotation is None
                ]
                if args_sin_tipo or node.returns is None:
                    hallazgos.append(
                        f"Función '{node.name}' sin type hints completos "
                        f"(argumentos sin tipo: {args_sin_tipo or 'ninguno'}, "
                        f"retorno anotado: {node.returns is not None})."
                    )

        return hallazgos

    def audit_unit(self, md_path: Path) -> Dict[str, Any]:
        """Audita una unidad del curso contra las 4 dimensiones de calidad.

        Args:
            md_path: Ruta al archivo Markdown de la unidad.

        Returns:
            Diccionario con la unidad auditada, hallazgos por dimensión
            ("latex", "pedagogico", "codigo", "curricular") y el total.
        """
        content = md_path.read_text(encoding="utf-8")
        bloques = extract_fenced_blocks(content)
        python_blocks = [code for _, lang, code in bloques if lang == "python"]

        hallazgos = {
            "latex": self._audit_latex(content),
            "pedagogico": [],
            "codigo": self._audit_codigo(python_blocks),
            "curricular": [],
        }
        total = sum(len(v) for v in hallazgos.values())

        return {
            "unidad": md_path.name,
            "hallazgos": hallazgos,
            "total_hallazgos": total,
        }
```

Nota: `_audit_latex` y `_audit_codigo` están completos en esta tarea; `pedagogico` y `curricular` quedan como listas vacías hasta las Tasks 6 y 7. Esto es intencional — cada dimensión se implementa y prueba de forma incremental.

- [ ] **Step 2: Ejecutar los tests de Task 4 y confirmar que las clases de LaTeX y Código pasan**

Run: `pytest tests/test_content_auditor_agent.py -v -k "TestAuditUnitEstructura or TestDimensionLatex or TestDimensionCodigo"`
Expected: todos PASS (la clase `TestAuditUnitEstructura` también debe pasar porque las 4 claves ya existen, aunque 2 estén vacías).

- [ ] **Step 3: black/isort/ruff**

```bash
python -m isort src/multiagent_core/content_auditor_agent.py
python -m black src/multiagent_core/content_auditor_agent.py
python -m ruff check src/multiagent_core/content_auditor_agent.py
```

- [ ] **Step 4: Commit**

```bash
git add src/multiagent_core/content_auditor_agent.py
git commit -m "feat: implementar ContentAuditorAgent dimensiones LaTeX y código (GREEN)"
```

### Task 6: Escribir y implementar Dimensión 2 (coherencia pedagógica — Hilo de Oro)

**Files:**
- Test: `tests/test_content_auditor_agent.py` (agregar clase)
- Modify: `src/multiagent_core/content_auditor_agent.py`

**Interfaces:**
- Consumes: `extract_fenced_blocks` (ya importada)
- Produces: método `_audit_pedagogico(bloques: list[tuple[str, str, str]], content: str) -> List[str]`, invocado desde `audit_unit`.

- [ ] **Step 1: Escribir los tests**

Agregar a `tests/test_content_auditor_agent.py`:

```python
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
            '# Test\n\n'
            '```pseudocodigo\nFUNCIÓN f(x)\n    RETORNAR x\nFIN_FUNCIÓN\n```\n\n'
            '```mermaid\ngraph TD\n    a --> b\n```\n\n'
            '```python\ndef f(x: int) -> int:\n    """Doc."""\n    return x\n```\n\n'
            '```pytest\ndef test_f():\n    assert f(1) == 1\n```\n',
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
        md_path.write_text("# Test\n\nSolo texto plano sin analogías.\n", encoding="utf-8")
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
        assert not any("analog" in h.lower() for h in resultado["hallazgos"]["pedagogico"])
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_content_auditor_agent.py::TestDimensionPedagogico -v`
Expected: FAIL (todos los hallazgos esperados están vacíos porque `_audit_pedagogico` no existe aún — `hallazgos["pedagogico"]` es siempre `[]` en la Task 5).

- [ ] **Step 3: Implementar `_audit_pedagogico` y conectarlo en `audit_unit`**

Agregar este método a la clase `ContentAuditorAgent` en `src/multiagent_core/content_auditor_agent.py` (después de `_audit_codigo`):

```python
    def _audit_pedagogico(
        self, bloques: List[tuple], content: str
    ) -> List[str]:
        """Verifica coherencia pedagógica: Hilo de Oro y presencia de analogías.

        Args:
            bloques: Bloques de código extraídos vía extract_fenced_blocks.
            content: Texto completo del MD, para buscar el patrón de analogía.

        Returns:
            Lista de descripciones de hallazgos; vacía si no hay problemas.
        """
        hallazgos: List[str] = []

        idiomas_presentes = {lang for _, lang, _ in bloques}
        hilo_de_oro_esperado = {"pseudocodigo", "mermaid", "python", "pytest"}
        if not hilo_de_oro_esperado.issubset(idiomas_presentes):
            faltantes = hilo_de_oro_esperado - idiomas_presentes
            hallazgos.append(
                "Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → "
                f"Python → pytest): faltan bloques de tipo {sorted(faltantes)}."
            )

        if "### 💡 Analogía" not in content and "### 💡 ANALOGÍA" not in content.upper():
            hallazgos.append(
                "No se encontró ninguna sección de Analogía Didáctica "
                "(patrón '### 💡 Analogía') en esta unidad."
            )

        return hallazgos
```

Y modificar `audit_unit` (reemplazar la línea `"pedagogico": [],` por la llamada real):

```python
        hallazgos = {
            "latex": self._audit_latex(content),
            "pedagogico": self._audit_pedagogico(bloques, content),
            "codigo": self._audit_codigo(python_blocks),
            "curricular": [],
        }
```

- [ ] **Step 4: Ejecutar y confirmar que pasa**

Run: `pytest tests/test_content_auditor_agent.py -v`
Expected: todos los tests de `TestDimensionPedagogico` y los anteriores PASS.

- [ ] **Step 5: black/isort/ruff + commit**

```bash
python -m isort src/multiagent_core/content_auditor_agent.py
python -m black src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
python -m ruff check src/multiagent_core/content_auditor_agent.py
git add src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
git commit -m "feat: agregar dimensión pedagógica (Hilo de Oro + analogías) a ContentAuditorAgent"
```

### Task 7: Escribir y implementar Dimensión 4 (cumplimiento curricular)

**Files:**
- Test: `tests/test_content_auditor_agent.py` (agregar clase)
- Modify: `src/multiagent_core/content_auditor_agent.py`

**Interfaces:**
- Consumes: `docs/legado/planeacion_2023_2024/Programa_de_Asignatura_Logica_Programacion_IA_v2_extracted.txt` (archivo ya existente, texto plano)
- Produces: método `_audit_curricular(unidad_num: int, content: str) -> List[str]`, invocado desde `audit_unit`; función módulo `_parse_programa_oficial(programa_path: Path) -> Dict[int, dict]` que retorna `{numero_unidad: {"subtemas": [...], "semanas": "..."}}`.

- [ ] **Step 1: Escribir los tests**

Agregar a `tests/test_content_auditor_agent.py`:

```python
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
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_content_auditor_agent.py::TestDimensionCurricular -v`
Expected: FAIL con `ImportError: cannot import name '_parse_programa_oficial'`

- [ ] **Step 3: Implementar el parser del programa oficial y la dimensión curricular**

Agregar a `src/multiagent_core/content_auditor_agent.py`, a nivel de módulo (después de `LATEX_KNOWN_MALFORMED`):

```python
def _parse_programa_oficial(programa_path: Path) -> Dict[int, dict]:
    """Parsea el programa de asignatura oficial en subtemas y semanas por unidad.

    Args:
        programa_path: Ruta al .txt del programa oficial extraído (formato con
            líneas "Unidad N: Título (Semana(s) X)" seguidas de líneas "N.M. subtema").

    Returns:
        Diccionario {numero_unidad: {"subtemas": [...], "semanas": str}}.
    """
    if not programa_path.exists():
        return {}

    content = programa_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    mapeo: Dict[int, dict] = {}
    unidad_actual = None

    for line in lines:
        unidad_match = re.match(
            r"^Unidad (\d+):.*\((Semanas? [\d\-]+)\)", line
        )
        if unidad_match:
            unidad_actual = int(unidad_match.group(1))
            mapeo[unidad_actual] = {
                "subtemas": [],
                "semanas": unidad_match.group(2),
            }
            continue

        subtema_match = re.match(r"^(\d+)\.(\d+)\.\s+(.+)$", line)
        if subtema_match and unidad_actual is not None:
            unidad_del_subtema = int(subtema_match.group(1))
            if unidad_del_subtema == unidad_actual:
                mapeo[unidad_actual]["subtemas"].append(subtema_match.group(3))

    return mapeo


_PROGRAMA_OFICIAL_PATH = (
    Path(__file__).parent.parent.parent
    / "docs"
    / "legado"
    / "planeacion_2023_2024"
    / "Programa_de_Asignatura_Logica_Programacion_IA_v2_extracted.txt"
)
```

Y agregar el método a la clase `ContentAuditorAgent` (después de `_audit_pedagogico`):

```python
    def _audit_curricular(self, md_path: Path, content: str) -> List[str]:
        """Verifica cobertura temática y duración contra el programa oficial.

        Args:
            md_path: Ruta del MD, usada para extraer el número de unidad del nombre.
            content: Texto completo del MD.

        Returns:
            Lista de descripciones de hallazgos; vacía si la unidad no se
            reconoce por nombre o no hay discrepancias.
        """
        unidad_match = re.match(r"UNIDAD_(\d+)_", md_path.name)
        if not unidad_match:
            return []

        numero_unidad = int(unidad_match.group(1))
        mapeo = _parse_programa_oficial(_PROGRAMA_OFICIAL_PATH)
        if numero_unidad not in mapeo:
            return []

        hallazgos: List[str] = []
        info = mapeo[numero_unidad]
        content_lower = content.lower()

        for subtema in info["subtemas"]:
            palabras_clave = [
                p.strip(".,()").lower()
                for p in subtema.split()
                if len(p) > 4
            ][:3]
            if palabras_clave and not any(p in content_lower for p in palabras_clave):
                hallazgos.append(
                    f"Subtema del programa oficial posiblemente no cubierto: "
                    f"'{subtema}' (ninguna de las palabras clave {palabras_clave} "
                    "aparece en el contenido)."
                )

        duracion_match = re.search(r"\*\*Duraci[óo]n:\*\*\s*(.+)", content)
        if duracion_match:
            duracion_texto = duracion_match.group(1)
            numeros_programa = re.findall(r"\d+", info["semanas"])
            if numeros_programa and not any(
                n in duracion_texto for n in numeros_programa
            ):
                hallazgos.append(
                    f"Posible discrepancia de duración: el MD dice "
                    f"'{duracion_texto.strip()}' pero el programa oficial indica "
                    f"'{info['semanas']}'."
                )

        return hallazgos
```

Y modificar `audit_unit` una última vez para conectar la dimensión curricular:

```python
        hallazgos = {
            "latex": self._audit_latex(content),
            "pedagogico": self._audit_pedagogico(bloques, content),
            "codigo": self._audit_codigo(python_blocks),
            "curricular": self._audit_curricular(md_path, content),
        }
```

- [ ] **Step 4: Ejecutar y confirmar que pasa**

Run: `pytest tests/test_content_auditor_agent.py -v`
Expected: todos los tests PASS.

- [ ] **Step 5: black/isort/ruff + commit**

```bash
python -m isort src/multiagent_core/content_auditor_agent.py
python -m black src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
python -m ruff check src/multiagent_core/content_auditor_agent.py
git add src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
git commit -m "feat: agregar dimensión de cumplimiento curricular a ContentAuditorAgent"
```

### Task 8: Implementar `audit_all_units` y correr contra las 9 unidades reales

**Files:**
- Test: `tests/test_content_auditor_agent.py` (agregar clase)
- Modify: `src/multiagent_core/content_auditor_agent.py`

**Interfaces:**
- Consumes: `audit_unit` (Tasks 5-7)
- Produces: `audit_all_units(course_dir: Path) -> str`

- [ ] **Step 1: Escribir el test**

```python
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
            "# UNIDAD 1\n\n```python\ndef f(x: int) -> int:\n    \"\"\"Doc.\"\"\"\n    return x\n```\n",
            encoding="utf-8",
        )
        reporte = auditor.audit_all_units(tmp_path)
        assert "# Reporte de Auditoría de Contenido" in reporte
        assert "UNIDAD_1_TEST.md" in reporte
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_content_auditor_agent.py::TestAuditAllUnits -v`
Expected: FAIL con `AttributeError: 'ContentAuditorAgent' object has no attribute 'audit_all_units'`

- [ ] **Step 3: Implementar `audit_all_units`**

Agregar a la clase `ContentAuditorAgent` (al final, después de `audit_unit`):

```python
    def audit_all_units(self, course_dir: Path) -> str:
        """Audita todas las unidades del curso y genera un reporte Markdown consolidado.

        Args:
            course_dir: Directorio raíz del curso, donde viven los UNIDAD_*.md.

        Returns:
            Reporte consolidado en Markdown, con una sección por unidad auditada,
            ordenadas alfabéticamente por nombre de archivo.
        """
        md_files = sorted(Path(course_dir).glob("UNIDAD_*.md"))

        secciones = ["# Reporte de Auditoría de Contenido", ""]
        total_general = 0

        for md_path in md_files:
            resultado = self.audit_unit(md_path)
            total_general += resultado["total_hallazgos"]

            secciones.append(f"## {resultado['unidad']} ({resultado['total_hallazgos']} hallazgos)")
            secciones.append("")

            for dimension, hallazgos in resultado["hallazgos"].items():
                if not hallazgos:
                    continue
                secciones.append(f"### {dimension.capitalize()}")
                for h in hallazgos:
                    secciones.append(f"- {h}")
                secciones.append("")

            if resultado["total_hallazgos"] == 0:
                secciones.append("- ✅ Sin hallazgos.")
                secciones.append("")

        secciones.insert(2, f"**Total de hallazgos en {len(md_files)} unidades: {total_general}**\n")

        return "\n".join(secciones)
```

- [ ] **Step 4: Ejecutar y confirmar que pasa**

Run: `pytest tests/test_content_auditor_agent.py -v`
Expected: todos los tests PASS (suite completa de `ContentAuditorAgent`).

- [ ] **Step 5: Correr el auditor contra las 9 unidades reales y guardar el reporte**

```bash
python -c "
from pathlib import Path
from src.multiagent_core.content_auditor_agent import ContentAuditorAgent

auditor = ContentAuditorAgent()
reporte = auditor.audit_all_units(Path('.'))
Path('docs/superpowers/content_audit_report.md').write_text(reporte, encoding='utf-8')
print(reporte[:2000])
"
```

Expected: se ejecuta sin excepciones y genera `docs/superpowers/content_audit_report.md`. **Este reporte se revisa manualmente con el usuario antes de aplicar ninguna corrección de contenido** — no forma parte de este plan de implementación de código; es un artefacto de salida a discutir aparte.

- [ ] **Step 6: black/isort/ruff + commit**

```bash
python -m isort src/multiagent_core/content_auditor_agent.py
python -m black src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
python -m ruff check src/multiagent_core/content_auditor_agent.py
git add src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py docs/superpowers/content_audit_report.md
git commit -m "feat: implementar audit_all_units y generar primer reporte de auditoría de contenido"
```

---

## Bloque 3d: Refactor — unificar generación de IDs de nodo Mermaid

Se hace antes del Bloque 3b/3a porque `OrchestratorAgent` (3b) importará `PseudocodeAgent`, y conviene que ambos agentes de diagramas ya compartan la utilidad antes de tocar el routing.

### Task 9: Escribir tests de la utilidad compartida `_mermaid_utils`

**Files:**
- Test: `tests/test_mermaid_utils.py` (nuevo)

**Interfaces:**
- Consumes: nada
- Produces: contrato esperado de `MermaidNodeCounter` con método `next_id() -> str` y atributo/reset `reset()`.

- [ ] **Step 1: Escribir los tests**

```python
"""Tests TDD para la utilidad compartida de generación de IDs de nodo Mermaid."""

from src.multiagent_core._mermaid_utils import MermaidNodeCounter


class TestMermaidNodeCounter:
    def test_primer_id_es_node_1(self):
        counter = MermaidNodeCounter()
        assert counter.next_id() == "node_1"

    def test_ids_incrementan_secuencialmente(self):
        counter = MermaidNodeCounter()
        assert counter.next_id() == "node_1"
        assert counter.next_id() == "node_2"
        assert counter.next_id() == "node_3"

    def test_reset_reinicia_el_contador(self):
        counter = MermaidNodeCounter()
        counter.next_id()
        counter.next_id()
        counter.reset()
        assert counter.next_id() == "node_1"
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_mermaid_utils.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'src.multiagent_core._mermaid_utils'`

- [ ] **Step 3: Commit (RED)**

```bash
git add tests/test_mermaid_utils.py
git commit -m "test: agregar tests para MermaidNodeCounter (RED)"
```

### Task 10: Implementar `MermaidNodeCounter` y migrar `FlowchartAgent`/`PseudocodeAgent`

**Files:**
- Create: `src/multiagent_core/_mermaid_utils.py`
- Modify: `src/multiagent_core/flowchart_agent.py:15-20`
- Modify: `src/multiagent_core/pseudocode_agent.py:18-23`

**Interfaces:**
- Produces: `MermaidNodeCounter` con `.next_id() -> str` y `.reset() -> None`
- Reemplaza: el atributo `self.node_counter` y método `_next_node_id()` de ambas clases por una instancia de `MermaidNodeCounter`.

- [ ] **Step 1: Implementar la utilidad**

```python
"""
Utilidad compartida de generación de IDs de nodo Mermaid.

Usada por FlowchartAgent y PseudocodeAgent, que generan diagramas de flujo
en formato Mermaid con la misma convención de identificadores (node_1,
node_2, ...).
"""


class MermaidNodeCounter:
    """Genera identificadores secuenciales de nodo para diagramas Mermaid."""

    def __init__(self) -> None:
        self._count = 0

    def next_id(self) -> str:
        """Genera el siguiente identificador de nodo.

        Returns:
            Identificador con el formato "node_N", donde N inicia en 1.
        """
        self._count += 1
        return f"node_{self._count}"

    def reset(self) -> None:
        """Reinicia el contador a cero."""
        self._count = 0
```

- [ ] **Step 2: Ejecutar los tests de Task 9 y confirmar que pasan**

Run: `pytest tests/test_mermaid_utils.py -v`
Expected: 3 tests PASS

- [ ] **Step 3: Migrar `FlowchartAgent`**

En `src/multiagent_core/flowchart_agent.py`, reemplazar:

```python
import ast


class FlowchartAgent:
    """Agente que traduce código Python a sintaxis de diagramas de flujo Mermaid."""

    def __init__(self):
        self.node_counter = 0

    def _next_node_id(self) -> str:
        self.node_counter += 1
        return f"node_{self.node_counter}"
```

por:

```python
import ast

from ._mermaid_utils import MermaidNodeCounter


class FlowchartAgent:
    """Agente que traduce código Python a sintaxis de diagramas de flujo Mermaid."""

    def __init__(self) -> None:
        self._node_counter = MermaidNodeCounter()

    def _next_node_id(self) -> str:
        return self._node_counter.next_id()
```

Y en `build_mermaid_flowchart`, reemplazar la línea `self.node_counter = 0` (línea 39) por `self._node_counter.reset()`.

- [ ] **Step 4: Migrar `PseudocodeAgent`**

En `src/multiagent_core/pseudocode_agent.py`, reemplazar:

```python
import ast
import re


class PseudocodeAgent:
    """Agente que convierte pseudocódigo UCEMICH a Mermaid, Python a pseudocódigo,
    y pseudocódigo a un esqueleto Python."""

    def __init__(self):
        self.node_counter = 0

    def _next_node_id(self) -> str:
        self.node_counter += 1
        return f"node_{self.node_counter}"
```

por:

```python
import ast
import re

from ._mermaid_utils import MermaidNodeCounter


class PseudocodeAgent:
    """Agente que convierte pseudocódigo UCEMICH a Mermaid, Python a pseudocódigo,
    y pseudocódigo a un esqueleto Python."""

    def __init__(self) -> None:
        self._node_counter = MermaidNodeCounter()

    def _next_node_id(self) -> str:
        return self._node_counter.next_id()
```

Y en `pseudocode_to_mermaid`, reemplazar la línea `self.node_counter = 0` (línea 27) por `self._node_counter.reset()`.

- [ ] **Step 5: Correr toda la suite de ambos agentes para confirmar cero regresión**

Run: `pytest tests/test_flowchart_agent.py tests/test_pseudocode_agent.py -v --tb=short`
Expected: todos los tests existentes siguen PASS — la salida Mermaid generada debe ser byte-idéntica a antes del refactor (mismos IDs `node_1`, `node_2`, etc.).

- [ ] **Step 6: black/isort/ruff + commit**

```bash
python -m isort src/multiagent_core/_mermaid_utils.py src/multiagent_core/flowchart_agent.py src/multiagent_core/pseudocode_agent.py
python -m black src/multiagent_core/_mermaid_utils.py src/multiagent_core/flowchart_agent.py src/multiagent_core/pseudocode_agent.py
python -m ruff check src/multiagent_core/_mermaid_utils.py src/multiagent_core/flowchart_agent.py src/multiagent_core/pseudocode_agent.py
git add src/multiagent_core/_mermaid_utils.py src/multiagent_core/flowchart_agent.py src/multiagent_core/pseudocode_agent.py tests/test_mermaid_utils.py
git commit -m "refactor: unificar generación de IDs de nodo Mermaid en MermaidNodeCounter"
```

---

## Bloque 3b: Routing simple en `OrchestratorAgent`

### Task 11: Escribir tests de `_detect_input_type` y del routing en `generate_pedagogical_report`

**Files:**
- Test: `tests/test_orchestrator_agent.py` (agregar clases)

**Interfaces:**
- Consumes: nada nuevo de fuera
- Produces: contrato esperado de `OrchestratorAgent._detect_input_type(student_code: str) -> str`, valores posibles `"python_con_funciones"`, `"python_sin_funciones"`, `"pseudocodigo"`.

- [ ] **Step 1: Escribir los tests**

Agregar a `tests/test_orchestrator_agent.py` (después de `CODIGO_EJEMPLO`, antes de la clase existente):

```python
CODIGO_PSEUDOCODIGO = """
FUNCIÓN calcular_volumen_esfera(radio_nm)
    SI radio_nm <= 0 ENTONCES
        RETORNAR -1
    FIN_SI
    RETORNAR (4 / 3) * 3.14159 * radio_nm ** 3
FIN_FUNCIÓN
"""

CODIGO_SIN_FUNCIONES = "x = 1 + 1\nprint(x)"


class TestDetectInputType:
    def test_detecta_pseudocodigo_por_palabras_clave_ucemich(
        self, orchestrator: OrchestratorAgent
    ):
        assert orchestrator._detect_input_type(CODIGO_PSEUDOCODIGO) == "pseudocodigo"

    def test_detecta_python_con_funciones(self, orchestrator: OrchestratorAgent):
        assert orchestrator._detect_input_type(CODIGO_EJEMPLO) == "python_con_funciones"

    def test_detecta_python_sin_funciones(self, orchestrator: OrchestratorAgent):
        assert (
            orchestrator._detect_input_type(CODIGO_SIN_FUNCIONES)
            == "python_sin_funciones"
        )


class TestRoutingEnReporte:
    def test_pseudocodigo_usa_pseudocode_agent_en_vez_de_flowchart_agent(
        self, orchestrator: OrchestratorAgent
    ):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_PSEUDOCODIGO, unit_number=2
        )
        assert "```mermaid" in reporte
        assert "graph TD" in reporte
        assert "[ESTILO]" not in reporte
        assert "[SEGURIDAD]" not in reporte

    def test_python_sin_funciones_omite_diagrama_mermaid(
        self, orchestrator: OrchestratorAgent
    ):
        reporte = orchestrator.generate_pedagogical_report(
            CODIGO_SIN_FUNCIONES, unit_number=3
        )
        assert "[DIAGRAMA]" not in reporte
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_orchestrator_agent.py -v -k "TestDetectInputType or TestRoutingEnReporte"`
Expected: FAIL con `AttributeError: 'OrchestratorAgent' object has no attribute '_detect_input_type'`

- [ ] **Step 3: Commit (RED)**

```bash
git add tests/test_orchestrator_agent.py
git commit -m "test: agregar tests de routing por tipo de entrada en OrchestratorAgent (RED)"
```

### Task 12: Implementar `_detect_input_type` y el routing en `OrchestratorAgent`

**Files:**
- Modify: `src/multiagent_core/orchestrator_agent.py`

**Interfaces:**
- Consumes: `PseudocodeAgent` (Task 10, ya migrado a `MermaidNodeCounter`)
- Produces: `_detect_input_type(student_code: str) -> str`; `generate_pedagogical_report` modificado para usar el routing.

- [ ] **Step 1: Reescribir el archivo completo con el routing agregado**

```python
"""
Agente Orquestador (OrchestratorAgent) - Lógica de Programación UCEMICH 🧩
==========================================================================

Coordina CodeAuditorAgent, FlowchartAgent, PseudocodeAgent y EvaluatorAgent
para producir un reporte pedagógico unificado en Markdown a partir del
código o pseudocódigo de un estudiante y el número de unidad correspondiente.
Clasifica automáticamente el tipo de entrada para evitar invocar agentes
que no aplican (p. ej. CodeAuditorAgent sobre pseudocódigo).
"""

from pathlib import Path
from typing import Optional

from .code_auditor_agent import CodeAuditorAgent
from .evaluator_agent import EvaluatorAgent
from .flowchart_agent import FlowchartAgent
from .pseudocode_agent import PseudocodeAgent

SKILL_METADATA = {
    "name": "orchestrator_agent",
    "description": "Coordina CodeAuditorAgent, FlowchartAgent/PseudocodeAgent y EvaluatorAgent en un reporte pedagógico único, con routing automático por tipo de entrada.",
    "version": "1.1.0",
    "input": "student_code: str, unit_number: int, test_file_path: Optional[Path]",
    "output": "str (reporte Markdown consolidado)",
    "requires_api_key": False,
}

PSEUDOCODE_KEYWORDS = ("INICIO", "FUNCIÓN", "FIN_SI", "FIN_FUNCIÓN", "MIENTRAS", "PARA")


class OrchestratorAgent:
    """Agente que coordina el consejo de agentes pedagógicos y consolida un reporte único."""

    def __init__(self) -> None:
        self.auditor = CodeAuditorAgent()
        self.flowchart_agent = FlowchartAgent()
        self.pseudocode_agent = PseudocodeAgent()
        self.evaluator = EvaluatorAgent()

    def _detect_input_type(self, student_code: str) -> str:
        """Clasifica la entrada del estudiante para decidir qué sub-agentes invocar.

        Args:
            student_code: Código o pseudocódigo entregado por el estudiante.

        Returns:
            "pseudocodigo" si contiene palabras clave de la sintaxis UCEMICH;
            "python_con_funciones" si es Python con al menos un `def`;
            "python_sin_funciones" en cualquier otro caso.
        """
        if any(kw in student_code.upper() for kw in PSEUDOCODE_KEYWORDS):
            return "pseudocodigo"
        if "def " in student_code:
            return "python_con_funciones"
        return "python_sin_funciones"

    def generate_pedagogical_report(
        self,
        student_code: str,
        unit_number: int,
        test_file_path: Optional[Path] = None,
    ) -> str:
        """Genera un reporte pedagógico unificado: auditoría + diagrama + calificación.

        Args:
            student_code: Código, pseudocódigo, o texto entregado por el estudiante.
            unit_number: Número de unidad del curso (0-8) a la que pertenece la entrega.
            test_file_path: Ruta opcional a un archivo de pruebas pytest asociado.

        Returns:
            Reporte consolidado en formato Markdown. El contenido varía según
            el tipo de entrada detectado: pseudocódigo omite auditoría de
            estilo/seguridad (no aplica) y usa PseudocodeAgent para el
            diagrama; Python sin funciones omite el diagrama de flujo.
        """
        tipo_entrada = self._detect_input_type(student_code)

        secciones = [f"# Reporte Pedagógico Unificado — Unidad {unit_number}", ""]

        if tipo_entrada != "pseudocodigo":
            auditoria = self.auditor.generate_report(student_code, test_file_path)
            secciones.extend([auditoria, ""])

        if tipo_entrada == "pseudocodigo":
            diagrama = self.pseudocode_agent.pseudocode_to_mermaid(student_code)
            secciones.extend(
                [
                    "## [DIAGRAMA] Diagrama de Flujo Autogenerado (desde pseudocódigo)",
                    "",
                    "```mermaid",
                    diagrama,
                    "```",
                    "",
                ]
            )
        elif tipo_entrada == "python_con_funciones":
            diagrama = self.flowchart_agent.build_mermaid_flowchart(student_code)
            secciones.extend(
                [
                    "## [DIAGRAMA] Diagrama de Flujo Autogenerado",
                    "",
                    "```mermaid",
                    diagrama,
                    "```",
                    "",
                ]
            )

        evaluacion = self.evaluator.evaluate(student_code, test_file_path)
        secciones.extend(
            [
                "## [CALIFICACIÓN] Evaluación contra Rúbrica Genérica",
                "",
                evaluacion["retroalimentacion"],
            ]
        )

        return "\n".join(secciones)


if __name__ == "__main__":
    orchestrator = OrchestratorAgent()
    codigo_ejemplo = """
def calcular_volumen_esfera(radio_nm):
    if radio_nm <= 0:
        return -1
    else:
        volumen = (4 / 3) * 3.14159 * radio_nm ** 3
        return volumen
"""
    print(orchestrator.generate_pedagogical_report(codigo_ejemplo, unit_number=2))
```

- [ ] **Step 2: Ejecutar toda la suite de orchestrator y confirmar cero regresión**

Run: `pytest tests/test_orchestrator_agent.py -v --tb=short`
Expected: los 6 tests originales (`TestGeneratePedagogicalReport`) siguen PASS (el código Python con funciones sigue produciendo el mismo reporte, solo cambia el mecanismo interno) + los tests nuevos de routing PASS.

- [ ] **Step 3: black/isort/ruff + commit**

```bash
python -m isort src/multiagent_core/orchestrator_agent.py
python -m black src/multiagent_core/orchestrator_agent.py tests/test_orchestrator_agent.py
python -m ruff check src/multiagent_core/orchestrator_agent.py
git add src/multiagent_core/orchestrator_agent.py tests/test_orchestrator_agent.py
git commit -m "feat: agregar routing por tipo de entrada a OrchestratorAgent"
```

---

## Bloque 3a: Debugger socrático en `TutorAgent`

### Task 13: Escribir tests de `_diagnose_error`

**Files:**
- Test: `tests/test_tutor_agent.py` (agregar clase)

**Interfaces:**
- Consumes: nada nuevo
- Produces: contrato esperado de `TutorAgent._diagnose_error(error_message: str, code_context: str = "") -> Optional[str]`.

- [ ] **Step 1: Escribir los tests**

Agregar a `tests/test_tutor_agent.py` (después de `TestAsk`):

```python
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

        with patch("src.multiagent_core.tutor_agent.genai.GenerativeModel") as mock_model_cls:
            mock_model_cls.return_value.generate_content.return_value = mock_response
            respuesta = tutor.ask(pregunta_con_error)

        assert "denominador" in respuesta.lower() or "cero" in respuesta.lower()

    def test_pregunta_conceptual_sin_traceback_no_recibe_pista_socratica(
        self, course_dir: Path, chroma_path: Path
    ):
        tutor = TutorAgent(course_dir=course_dir, chroma_path=chroma_path)
        mock_response = MagicMock()
        mock_response.text = "Una variable es un espacio en memoria."

        with patch("src.multiagent_core.tutor_agent.genai.GenerativeModel") as mock_model_cls:
            mock_model_cls.return_value.generate_content.return_value = mock_response
            respuesta = tutor.ask("¿Qué es una variable?")

        assert respuesta == "Una variable es un espacio en memoria."
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_tutor_agent.py -v -k "TestDiagnoseError or TestAskConTraceback"`
Expected: FAIL con `AttributeError: 'TutorAgent' object has no attribute '_diagnose_error'`

- [ ] **Step 3: Commit (RED)**

```bash
git add tests/test_tutor_agent.py
git commit -m "test: agregar tests de debugger socrático para TutorAgent (RED)"
```

### Task 14: Implementar `_diagnose_error` y conectarlo en `ask`

**Files:**
- Modify: `src/multiagent_core/tutor_agent.py`

**Interfaces:**
- Produces: `_diagnose_error(error_message: str, code_context: str = "") -> Optional[str]`
- Modifica: `ask()` para anteponer la pista socrática cuando la pregunta contiene un traceback.

- [ ] **Step 1: Agregar el diccionario de reglas y el método**

Agregar después de `TOP_K_RESULTS = 3` en `src/multiagent_core/tutor_agent.py`:

```python
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
```

Y agregar el método a la clase `TutorAgent` (después de `_search_local_docs`, antes de `ask`):

```python
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
```

- [ ] **Step 2: Ejecutar los tests de `_diagnose_error` y confirmar que pasan**

Run: `pytest tests/test_tutor_agent.py -v -k TestDiagnoseError`
Expected: 5 tests PASS

- [ ] **Step 3: Conectar `_diagnose_error` dentro de `ask()`**

Reemplazar el método `ask` completo en `src/multiagent_core/tutor_agent.py`:

```python
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
```

- [ ] **Step 4: Ejecutar toda la suite de tutor_agent y confirmar cero regresión**

Run: `pytest tests/test_tutor_agent.py -v --tb=short`
Expected: todos los tests (los 5 originales de `TestAsk`/`TestSearchLocalDocs`/`TestGetMarkdownFiles` + los nuevos de `TestDiagnoseError`/`TestAskConTraceback`) PASS.

- [ ] **Step 5: black/isort/ruff + commit**

```bash
python -m isort src/multiagent_core/tutor_agent.py
python -m black src/multiagent_core/tutor_agent.py tests/test_tutor_agent.py
python -m ruff check src/multiagent_core/tutor_agent.py
git add src/multiagent_core/tutor_agent.py tests/test_tutor_agent.py
git commit -m "feat: agregar debugger socrático a TutorAgent.ask()"
```

---

## Bloque 4: Memoria episódica para `TutorAgent`

### Task 15: Escribir tests de memoria episódica

**Files:**
- Test: `tests/test_tutor_agent.py` (agregar clase; también modificar el `__init__` de la fixture si aplica)

**Interfaces:**
- Consumes: nada nuevo
- Produces: contrato esperado de `TutorAgent.__init__(..., memory_path: Optional[Path] = None)`, `_add_episode(question: str, answer_summary: str) -> None`, `_retrieve_relevant_episodes(query: str, top_k: int = 3) -> list[dict]`.

- [ ] **Step 1: Escribir los tests**

Agregar a `tests/test_tutor_agent.py` (al final del archivo):

```python
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
        tutor._add_episode("¿qué es una variable en Python?", "Resumen sobre variables.")
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

        with patch("src.multiagent_core.tutor_agent.genai.GenerativeModel") as mock_model_cls:
            mock_model_cls.return_value.generate_content.return_value = mock_response
            tutor.ask("¿qué es una variable en Python?")

            mock_model_cls.return_value.generate_content.reset_mock()
            tutor.ask("y las variables, se pueden reasignar?")

        prompt_enviado = mock_model_cls.return_value.generate_content.call_args[0][0]
        assert "sesiones anteriores" in prompt_enviado.lower() or "pregunta anterior" in prompt_enviado.lower()
```

Y agregar el import de `json` al inicio del archivo de test:

```python
import json
```

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `pytest tests/test_tutor_agent.py -v -k "TestMemoriaEpisodica or TestAskUsaMemoria"`
Expected: FAIL con `TypeError: TutorAgent.__init__() got an unexpected keyword argument 'memory_path'`

- [ ] **Step 3: Commit (RED)**

```bash
git add tests/test_tutor_agent.py
git commit -m "test: agregar tests de memoria episódica para TutorAgent (RED)"
```

### Task 16: Implementar memoria episódica en `TutorAgent`

**Files:**
- Modify: `src/multiagent_core/tutor_agent.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `memory_path` como atributo público, `_add_episode`, `_retrieve_relevant_episodes`, constante `MAX_EPISODIOS`.
- Modifica: `ask()` para guardar cada intercambio y recuperar contexto de episodios previos.

- [ ] **Step 1: Agregar el import de `json` y la constante**

En `src/multiagent_core/tutor_agent.py`, agregar `import json` a los imports de stdlib (junto a `logging`, `os`, `re`), y agregar después de `TOP_K_RESULTS = 3`:

```python
DEFAULT_MEMORY_FILENAME = ".tutor_memory.json"
MAX_EPISODIOS = 50
```

- [ ] **Step 2: Modificar `__init__` para aceptar `memory_path`**

Reemplazar el `__init__` actual:

```python
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
```

por:

```python
    def __init__(
        self,
        course_dir: Path,
        chroma_path: Optional[Path] = None,
        memory_path: Optional[Path] = None,
    ) -> None:
        self.course_dir = Path(course_dir)
        self.model_name = "gemini-1.5-flash"
        self.chroma_path = (
            Path(chroma_path)
            if chroma_path
            else self.course_dir / DEFAULT_CHROMA_DIRNAME
        )
        self.memory_path = (
            Path(memory_path)
            if memory_path
            else self.course_dir / DEFAULT_MEMORY_FILENAME
        )
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_path))
        self.collection = self.chroma_client.get_or_create_collection("lecciones_curso")
        self._build_index()
```

- [ ] **Step 3: Agregar los métodos de memoria episódica**

Agregar después de `_search_local_docs` (antes de `_diagnose_error`):

```python
    def _load_episodes(self) -> list[dict]:
        """Carga los episodios guardados desde memory_path.

        Returns:
            Lista de episodios (dicts con "question", "answer_summary"), o
            lista vacía si el archivo no existe o está corrupto.
        """
        if not self.memory_path.exists():
            return []
        try:
            return json.loads(self.memory_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _add_episode(self, question: str, answer_summary: str) -> None:
        """Guarda una pregunta y su respuesta como episodio en memoria local.

        Args:
            question: Pregunta formulada por el alumno.
            answer_summary: Resumen o texto completo de la respuesta dada.
        """
        episodios = self._load_episodes()
        episodios.append({"question": question, "answer_summary": answer_summary})
        episodios = episodios[-MAX_EPISODIOS:]
        self.memory_path.write_text(
            json.dumps(episodios, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _retrieve_relevant_episodes(
        self, query: str, top_k: int = TOP_K_RESULTS
    ) -> list[dict]:
        """Recupera episodios previos relevantes por solapamiento de palabras clave.

        Args:
            query: Texto de la pregunta actual, usado para buscar episodios
                temáticamente relacionados.
            top_k: Número máximo de episodios a retornar.

        Returns:
            Lista de episodios ordenados por relevancia descendente, cada uno
            con "question", "answer_summary" y "score" (0.0-1.0).
        """
        episodios = self._load_episodes()
        query_words = set(query.lower().split())

        puntuados = []
        for ep in episodios:
            ep_words = set(ep["question"].lower().split())
            overlap = len(query_words & ep_words)
            score = overlap / max(len(query_words), 1)
            if score > 0:
                puntuados.append({**ep, "score": round(score, 3)})

        puntuados.sort(key=lambda e: e["score"], reverse=True)
        return puntuados[:top_k]
```

- [ ] **Step 4: Conectar la memoria episódica en `ask()`**

Reemplazar el método `ask` completo:

```python
    def ask(self, question: str) -> str:
        """Responde a la duda del estudiante, con pista socrática y memoria episódica.

        Args:
            question: Pregunta o mensaje de error del estudiante.

        Returns:
            Si `question` contiene un traceback o nombre de excepción de
            Python reconocible, retorna primero una pregunta guía (no la
            solución directa). Si es una pregunta conceptual, responde vía
            Gemini con contexto local del curso y de episodios previos
            relacionados de sesiones anteriores en la misma máquina.
        """
        pista_socratica = self._diagnose_error(question)
        if pista_socratica:
            return pista_socratica

        context = self._search_local_docs(question)
        episodios_previos = self._retrieve_relevant_episodes(question)

        contexto_memoria = ""
        if episodios_previos:
            lineas = [
                f"  - Pregunta anterior: \"{ep['question']}\" (respuesta resumida: {ep['answer_summary'][:150]})"
                for ep in episodios_previos
            ]
            contexto_memoria = (
                "\n\nContexto de sesiones anteriores (memoria episódica):\n"
                + "\n".join(lineas)
            )

        prompt = f"""
Eres un Agente Tutor experto en Lógica de Programación y Desarrollo Agéntico con IA para el curso de Ingeniería en Nanotecnología de la UCEMICH.
Tu misión es guiar al estudiante de forma clara, didáctica y técnica.

Usa el siguiente contexto recuperado de las lecciones del curso para responder la pregunta del alumno.
Si la información no está en el contexto, indícalo amablemente y responde con base en tus conocimientos generales del curso.

---
CONTEXTO DE LECCIONES:
{context}
{contexto_memoria}
---

PREGUNTA DEL ALUMNO:
{question}

Responde en español de forma estructurada, usando Markdown. Explica el paso a paso del razonamiento lógico.
"""
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            respuesta_texto = response.text
        except Exception as e:
            logger.exception("Fallo al invocar al modelo Gemini")
            respuesta_texto = (
                f"Error al invocar al modelo Gemini: {e}\n\n"
                f"[Contexto Local Recuperado]:\n{context}"
            )

        self._add_episode(question, respuesta_texto[:300])
        return respuesta_texto
```

Nota: `_add_episode` se llama incluso si `ask()` cayó en el bloque `except` (error de Gemini) — así el alumno también recibe continuidad si vuelve a preguntar algo relacionado tras un fallo temporal de la API.

- [ ] **Step 5: Ejecutar toda la suite de tutor_agent**

Run: `pytest tests/test_tutor_agent.py -v --tb=short`
Expected: todos los tests (originales + socráticos + memoria episódica) PASS.

- [ ] **Step 6: Agregar `.tutor_memory.json` a `.gitignore`**

Editar `.gitignore`, agregar bajo la sección de ChromaDB:

```
# Memoria episódica local del TutorAgent (se regenera por alumno/máquina)
.tutor_memory.json
```

- [ ] **Step 7: black/isort/ruff + commit**

```bash
python -m isort src/multiagent_core/tutor_agent.py
python -m black src/multiagent_core/tutor_agent.py tests/test_tutor_agent.py
python -m ruff check src/multiagent_core/tutor_agent.py
git add src/multiagent_core/tutor_agent.py tests/test_tutor_agent.py .gitignore
git commit -m "feat: agregar memoria episódica JSON local a TutorAgent"
```

---

## Bloque 3c: `SKILL_METADATA` en los agentes restantes

### Task 17: Agregar `SKILL_METADATA` a los agentes que aún no lo tienen

**Files:**
- Modify: `src/multiagent_core/code_auditor_agent.py`
- Modify: `src/multiagent_core/flowchart_agent.py`
- Modify: `src/multiagent_core/pseudocode_agent.py`
- Modify: `src/multiagent_core/evaluator_agent.py`
- Modify: `src/multiagent_core/notebook_compiler_agent.py`

Nota: `orchestrator_agent.py` y `content_auditor_agent.py` ya tienen `SKILL_METADATA` desde las Tasks 12 y 5 respectivamente. `tutor_agent.py` se agrega aquí también si no se agregó antes.

**Interfaces:**
- No afecta ninguna interfaz pública existente — solo agrega un dict a nivel de módulo. No requiere tests nuevos (es documentación estructurada, no comportamiento).

- [ ] **Step 1: Agregar a `code_auditor_agent.py`**

Después de los imports, antes de `class CodeAuditorAgent:`:

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

- [ ] **Step 2: Agregar a `flowchart_agent.py`**

Después de `from ._mermaid_utils import MermaidNodeCounter`, antes de `class FlowchartAgent:`:

```python
SKILL_METADATA = {
    "name": "flowchart_agent",
    "description": "Genera diagramas de flujo Mermaid a partir del AST de una función Python.",
    "version": "1.0.0",
    "input": "code_source: str",
    "output": "str (diagrama Mermaid en formato graph TD)",
    "requires_api_key": False,
}
```

- [ ] **Step 3: Agregar a `pseudocode_agent.py`**

Después de `from ._mermaid_utils import MermaidNodeCounter`, antes de `class PseudocodeAgent:`:

```python
SKILL_METADATA = {
    "name": "pseudocode_agent",
    "description": "Traduce entre pseudocódigo UCEMICH, diagramas Mermaid y esqueletos Python.",
    "version": "1.0.0",
    "input": "pseudocode: str | code_source: str (según el método)",
    "output": "str (Mermaid, pseudocódigo, o esqueleto Python según el método)",
    "requires_api_key": False,
}
```

- [ ] **Step 4: Agregar a `evaluator_agent.py`**

Después de `from .code_auditor_agent import CodeAuditorAgent`, antes de `NIVELES = (...)`:

```python
SKILL_METADATA = {
    "name": "evaluator_agent",
    "description": "Califica código de estudiantes contra la Rúbrica Genérica de Laboratorio.",
    "version": "1.0.0",
    "input": "student_code: str, test_file_path: Optional[Path]",
    "output": "Dict[str, Any] con criterios calificados y calificación final",
    "requires_api_key": False,
}
```

- [ ] **Step 5: Agregar a `notebook_compiler_agent.py`**

Después de los imports, antes de `class MathAgent:`:

```python
SKILL_METADATA = {
    "name": "notebook_compiler_agent",
    "description": "Convierte MDs de las unidades del curso en notebooks .ipynb ejecutables.",
    "version": "1.0.0",
    "input": "md_filepath: Path, output_dir: Path",
    "output": "Path (ruta del .ipynb generado)",
    "requires_api_key": False,
}
```

- [ ] **Step 6: Agregar a `tutor_agent.py`**

Después de `logger = logging.getLogger(__name__)`, antes de `DEFAULT_CHROMA_DIRNAME = ".chroma"`:

```python
SKILL_METADATA = {
    "name": "tutor_agent",
    "description": "Responde dudas del curso vía RAG semántico (ChromaDB) + Gemini, con debugger socrático y memoria episódica.",
    "version": "2.0.0",
    "input": "question: str (ask) | course_dir: Path, chroma_path: Optional[Path], memory_path: Optional[Path] (constructor)",
    "output": "str (respuesta en Markdown, o pregunta socrática si detecta un error)",
    "requires_api_key": True,
}
```

- [ ] **Step 7: Correr la suite completa para confirmar que agregar los dicts no rompió nada**

Run: `pytest tests/ -v --tb=short`
Expected: 100% passing (agregar un dict a nivel de módulo no debería afectar ningún test existente; este paso es solo verificación de seguridad).

- [ ] **Step 8: black/isort/ruff sobre todos los archivos tocados + commit**

```bash
python -m isort src/multiagent_core/*.py
python -m black src/multiagent_core/*.py
python -m ruff check src/multiagent_core/*.py
git add src/multiagent_core/code_auditor_agent.py src/multiagent_core/flowchart_agent.py src/multiagent_core/pseudocode_agent.py src/multiagent_core/evaluator_agent.py src/multiagent_core/notebook_compiler_agent.py src/multiagent_core/tutor_agent.py
git commit -m "docs: agregar SKILL_METADATA a los agentes restantes"
```

---

## Bloque 2: Conectar los 6 agentes con celdas en notebooks

Cada tarea de este bloque edita el MD fuente correspondiente (nunca el `.ipynb` directamente) y luego regenera los 9 notebooks.

### Task 18: Celda de `TutorAgent` en las 9 unidades (U0-U8) + guía de API key en U0

**Files:**
- Modify: `UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md`
- Modify: `UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md`
- Modify: `UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md`
- Modify: `UNIDAD_3_VARIABLES_OPERADORES.md`
- Modify: `UNIDAD_4_ESTRUCTURAS_DECISION.md`
- Modify: `UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md`
- Modify: `UNIDAD_6_MODULARIDAD_IA_MCP.md`
- Modify: `UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.md`
- Modify: `UNIDAD_8_PROYECTO_INTEGRADOR.md`

**Interfaces:**
- Consumes: `TutorAgent(course_dir: Path, chroma_path=None, memory_path=None)` y `.ask(question: str) -> str` (Tasks 14, 16)

- [ ] **Step 1: Agregar sección "0.9 Tu Tutor Personal: Cómo Obtener tu Gemini API Key" en U0**

En `UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md`, insertar esta sección nueva **antes** de `## 📖 Referencias` (justo después del cierre de la sección `# 0.8 El Libro de Python...`, que termina con la línea `... La restricción es sobre el uso de IA para escribir código, no sobre qué material de consulta lees.` seguida de `---`):

```markdown
# 0.9 Tu Tutor Personal: TutorAgent

El curso incluye un agente tutor que responde dudas conceptuales citando exactamente la sección de las unidades donde está la respuesta — a diferencia de un asistente genérico, `TutorAgent` conoce el contenido específico de este curso.

## Obtener tu API Key gratuita de Gemini

1. Ir a [aistudio.google.com/apikey](https://aistudio.google.com/apikey) e iniciar sesión con tu cuenta de Google.
2. Hacer clic en "Create API Key" — es gratuito, no requiere tarjeta de crédito para el tier básico.
3. Copiar la key generada.
4. Guardarla como variable de entorno antes de abrir el notebook:
   ```powershell
   $env:GEMINI_API_KEY = "tu_clave_aqui"
   ```
   O, si usas un archivo `.env` en la raíz del proyecto (recomendado):
   ```
   GEMINI_API_KEY=tu_clave_aqui
   ```

> [!IMPORTANT]
> Cada alumno debe generar **su propia** API key. No compartas la tuya ni uses una key ajena — el tier gratuito tiene un límite de peticiones por minuto/día, y compartir una sola key entre el grupo la agotaría rápido para todos.

## Cómo usar TutorAgent en cualquier notebook

Cada unidad de este curso incluye una celda "🛠️ Herramientas de esta unidad" al final. Para `TutorAgent`, instáncialo **una sola vez** por notebook y reutiliza la misma variable:

```python
from pathlib import Path
from src.multiagent_core.tutor_agent import TutorAgent

# Instanciar una sola vez (abrir el índice tiene un costo fijo ~0.3s)
tutor = TutorAgent(course_dir=Path("."))
```

```python
# Reutiliza la variable "tutor" en cualquier celda posterior para preguntar
print(tutor.ask("¿qué es una variable?"))
```

Nota: la primera vez que ejecutes esto en una sesión nueva de Colab, `TutorAgent` indexa las 9 unidades del curso (tarda unos segundos); en ejecuciones posteriores en la misma máquina es instantáneo. Si `course_dir` no apunta a la raíz del repositorio (por ejemplo, tras un `git clone` en una ruta distinta en Colab), ajusta la ruta al directorio donde están los archivos `UNIDAD_*.md`.

📖 Referencia: [aistudio.google.com](https://aistudio.google.com/apikey)

---
```

- [ ] **Step 2: Agregar celda "🛠️ Herramientas de esta unidad" (solo TutorAgent) al final de U1**

Ubicar el final de `UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md` (antes de cualquier banco de preguntas, o al final absoluto si no hay uno) e insertar:

```markdown
---

## 🛠️ Herramientas de esta Unidad

**TutorAgent** — resuelve tus dudas conceptuales sobre CLI, Git y Vibe Coding citando el contenido exacto de esta unidad:

```python
from pathlib import Path
from src.multiagent_core.tutor_agent import TutorAgent

tutor = TutorAgent(course_dir=Path("."))
print(tutor.ask("¿qué es el Vibe Coding y por qué no reemplaza el pensamiento computacional?"))
```

No requiere configuración adicional más allá de tu `GEMINI_API_KEY` (ver Unidad 0, sección 0.9).
```

- [ ] **Step 3: Repetir el mismo patrón de celda "🛠️ Herramientas de esta unidad" (solo TutorAgent) en U2 a U8**

Para cada uno de `UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md`, `UNIDAD_3_VARIABLES_OPERADORES.md`, `UNIDAD_4_ESTRUCTURAS_DECISION.md`, `UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md`, `UNIDAD_6_MODULARIDAD_IA_MCP.md`, `UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.md`, `UNIDAD_8_PROYECTO_INTEGRADOR.md`: insertar al final del archivo una sección igual a la de U1, adaptando solo la pregunta de ejemplo al tema de esa unidad. Estas celdas se combinan con las de otros agentes (Tasks 19-21) que también van al final de las mismas unidades — cuando una unidad reciba más de una celda de herramientas, van todas bajo el mismo encabezado `## 🛠️ Herramientas de esta Unidad`, una sub-sección por agente. Ejemplos de pregunta por unidad:

- U2: `"¿cómo se escribe una prueba de escritorio para una función con pseudocódigo?"`
- U3: `"¿cuál es la diferencia entre shallow copy y deep copy?"`
- U4: `"¿cuándo usar match/case en vez de if/elif/else?"`
- U5: `"¿qué diferencia hay entre un contador, un acumulador y una bandera?"`
- U6: `"¿cómo se desempaquetan los argumentos con **kwargs en una tool call MCP?"`
- U7: `"¿cómo se calcula el camino mínimo en un grafo de red cristalina con NetworkX?"`
- U8: `"¿qué hace el MAEC cuando detecta un import peligroso en el código del alumno?"`

- [ ] **Step 4: Regenerar los 9 notebooks**

```bash
python convert_to_notebooks_smart.py
```

Expected: "Convertidos con éxito: 9" sin errores.

- [ ] **Step 5: Verificar que TutorAgent aparece en las 9 unidades**

```bash
grep -l "TutorAgent" notebooks/*.ipynb | wc -l
```

Expected: `9`

- [ ] **Step 6: Commit**

```bash
git add UNIDAD_*.md notebooks/
git commit -m "feat: agregar TutorAgent como herramienta transversal en las 9 unidades"
```

### Task 19: Celda de `PseudocodeAgent`/`FlowchartAgent` en U2-U8

**Files:**
- Modify: `UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md` a `UNIDAD_8_PROYECTO_INTEGRADOR.md` (7 archivos)

**Interfaces:**
- Consumes: `PseudocodeAgent().pseudocode_to_mermaid/python_to_pseudocode/pseudocode_to_python_skeleton` (ya existentes, migrado en Task 10), `FlowchartAgent().build_mermaid_flowchart` (ya existente, migrado en Task 10)

- [ ] **Step 1: Agregar sub-sección de `PseudocodeAgent` bajo "🛠️ Herramientas de esta Unidad" en U2**

En `UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md`, dentro de la sección "🛠️ Herramientas de esta Unidad" ya creada en la Task 18, agregar (antes o después de la sub-sección de TutorAgent, mismo nivel de encabezado `###`):

```markdown
### PseudocodeAgent — verifica tu Hilo de Oro

Escribe tu solución en pseudocódigo UCEMICH y visualiza su diagrama de flujo antes de traducir a Python:

```python
from src.multiagent_core.pseudocode_agent import PseudocodeAgent

agent = PseudocodeAgent()
mi_pseudocodigo = """
FUNCIÓN calcular_volumen_esfera(radio_nm)
    SI radio_nm <= 0 ENTONCES
        RETORNAR -1
    SINO
        volumen <- (4 / 3) * 3.14159 * radio_nm ** 3
        RETORNAR volumen
    FIN_SI
FIN_FUNCIÓN
"""
print(agent.pseudocode_to_mermaid(mi_pseudocodigo))
```

Copia el resultado en [mermaid.live](https://mermaid.live) para verlo renderizado, o pégalo en una celda Markdown de este notebook dentro de un bloque ` ```mermaid `.
```

- [ ] **Step 2: Agregar la misma sub-sección de `PseudocodeAgent` en U3 a U6**

Para `UNIDAD_3_VARIABLES_OPERADORES.md`, `UNIDAD_4_ESTRUCTURAS_DECISION.md`, `UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md`, `UNIDAD_6_MODULARIDAD_IA_MCP.md`: agregar la misma sub-sección "PseudocodeAgent — verifica tu Hilo de Oro" con el mismo snippet (reutilizable, no depende del tema específico de la unidad).

- [ ] **Step 3: Agregar sub-sección de `FlowchartAgent` en U7 y U8**

En `UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.md` y `UNIDAD_8_PROYECTO_INTEGRADOR.md` (unidades de código de producción más complejo, donde el alumno trabaja con funciones Python reales en vez de pseudocódigo desde cero), agregar en su lugar:

```markdown
### FlowchartAgent — visualiza el flujo de tu función

Pega tu propia función Python para ver su diagrama de flujo generado automáticamente:

```python
from src.multiagent_core.flowchart_agent import FlowchartAgent

agent = FlowchartAgent()
mi_codigo = """
def mi_funcion(x):
    if x > 0:
        return x * 2
    return 0
"""
print(agent.build_mermaid_flowchart(mi_codigo))
```
```

- [ ] **Step 4: Regenerar los 9 notebooks y verificar**

```bash
python convert_to_notebooks_smart.py
grep -l "PseudocodeAgent" notebooks/*.ipynb | wc -l
grep -l "FlowchartAgent" notebooks/*.ipynb | wc -l
```

Expected: `PseudocodeAgent` en 5 notebooks (U2-U6); `FlowchartAgent` en al menos 2 (U7, U8) — más las apariciones indirectas ya existentes vía diagramas autogenerados de `NotebookCompilerAgent`.

- [ ] **Step 5: Commit**

```bash
git add UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md UNIDAD_3_VARIABLES_OPERADORES.md UNIDAD_4_ESTRUCTURAS_DECISION.md UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md UNIDAD_6_MODULARIDAD_IA_MCP.md UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.md UNIDAD_8_PROYECTO_INTEGRADOR.md notebooks/
git commit -m "feat: agregar PseudocodeAgent (U2-U6) y FlowchartAgent (U7-U8) como herramientas de autoverificación"
```

### Task 20: Celda de `CodeAuditorAgent` y `EvaluatorAgent` (auto-chequeo del alumno)

**Files:**
- Modify: `UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md` a `UNIDAD_8_PROYECTO_INTEGRADOR.md` (7 archivos)
- Modify: `UNIDAD_8_PROYECTO_INTEGRADOR.md` (mención adicional en el checklist de entrega ya existente)

**Interfaces:**
- Consumes: `CodeAuditorAgent().generate_report(student_code, test_file_path=None)`, `EvaluatorAgent().evaluate(student_code, test_file_path=None)` (ya existentes)

- [ ] **Step 1: Agregar sub-sección de `CodeAuditorAgent` + `EvaluatorAgent` en U2 a U8**

En cada una de las 7 unidades (U2-U8), dentro de la sección "🛠️ Herramientas de esta Unidad", agregar:

```markdown
### CodeAuditorAgent y EvaluatorAgent — audita tu código antes de entregar

Corre tu propio código a través del auditor y el evaluador antes de entregarlo, para detectar problemas de estilo, seguridad, o saber tu calificación aproximada contra la rúbrica:

```python
from src.multiagent_core.code_auditor_agent import CodeAuditorAgent
from src.multiagent_core.evaluator_agent import EvaluatorAgent

mi_codigo = """
def calcular_area(radio):
    return 3.14159 * radio ** 2
"""

auditor = CodeAuditorAgent()
print(auditor.generate_report(mi_codigo))

evaluador = EvaluatorAgent()
resultado = evaluador.evaluate(mi_codigo)
print(resultado["retroalimentacion"])
```
```

- [ ] **Step 2: Agregar mención de `CodeAuditorAgent` al checklist de entrega en U8**

En `UNIDAD_8_PROYECTO_INTEGRADOR.md`, localizar la sección `## 14. Checklist de Entrega Pre-Defensa` (creada en el Día 2-3) y agregar un ítem nuevo a la lista existente:

```markdown
- [ ] Corriste `CodeAuditorAgent` y `EvaluatorAgent` sobre tu código final y revisaste sus hallazgos antes de entregar.
```

- [ ] **Step 3: Regenerar los 9 notebooks y verificar**

```bash
python convert_to_notebooks_smart.py
grep -l "CodeAuditorAgent" notebooks/*.ipynb | wc -l
grep -l "EvaluatorAgent" notebooks/*.ipynb | wc -l
```

Expected: ambos en 7 notebooks (U2-U8).

- [ ] **Step 4: Commit**

```bash
git add UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md UNIDAD_3_VARIABLES_OPERADORES.md UNIDAD_4_ESTRUCTURAS_DECISION.md UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md UNIDAD_6_MODULARIDAD_IA_MCP.md UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.md UNIDAD_8_PROYECTO_INTEGRADOR.md notebooks/
git commit -m "feat: agregar CodeAuditorAgent y EvaluatorAgent como herramientas de auto-chequeo pre-entrega"
```

### Task 21: Sección de flujo de uso del docente en `RUBRICA_GENERAL.md`

**Files:**
- Modify: `RUBRICA_GENERAL.md`

**Interfaces:**
- Consumes: `OrchestratorAgent().generate_pedagogical_report(student_code, unit_number, test_file_path=None)` (ya existente, con routing agregado en Task 12), `EvaluatorAgent().evaluate` (ya existente)

- [ ] **Step 1: Leer el final del archivo actual**

Ejecutar `tail -20 RUBRICA_GENERAL.md` para confirmar el punto exacto de inserción (después de la sección "📌 Notas de Aplicación" existente, al final del archivo).

- [ ] **Step 2: Agregar la sección nueva al final de `RUBRICA_GENERAL.md`**

```markdown

---

## 🤖 Flujo de Calificación para el Docente (OrchestratorAgent)

Para agilizar la calificación y mantener consistencia entre entregas, usa `OrchestratorAgent` desde terminal (o un script/notebook propio, no destinado al alumno):

```python
from pathlib import Path
from src.multiagent_core.orchestrator_agent import OrchestratorAgent

orchestrator = OrchestratorAgent()

# Lee el código entregado por el alumno desde su archivo
codigo_alumno = Path("entregas/alumno_x/solucion.py").read_text(encoding="utf-8")
test_file = Path("entregas/alumno_x/test_solucion.py")  # opcional

reporte = orchestrator.generate_pedagogical_report(
    codigo_alumno, unit_number=5, test_file_path=test_file
)
print(reporte)
```

El reporte generado incluye automáticamente:
- Auditoría de estilo (PEP 8) y seguridad (OWASP), omitida si la entrega es pseudocódigo.
- Diagrama de flujo Mermaid autogenerado (desde Python o desde pseudocódigo, según lo que el `OrchestratorAgent` detecte).
- Calificación contra los 4 criterios de la Rúbrica Genérica de Laboratorio de este documento.

Guarda el reporte como parte del expediente de la entrega:

```python
Path("entregas/alumno_x/reporte_evaluacion.md").write_text(reporte, encoding="utf-8")
```

Este flujo es **complementario, no sustituto**, del criterio "Proceso (Hilo de Oro)" de la rúbrica — ese criterio requiere revisión humana del pseudocódigo y diagrama entregados, ya que `EvaluatorAgent` no puede verificarlo automáticamente (ver `src/multiagent_core/evaluator_agent.py`, método `_evaluar_proceso`).
```

- [ ] **Step 3: Verificar que el archivo sigue siendo Markdown válido**

Ejecutar `tail -40 RUBRICA_GENERAL.md` y confirmar visualmente que la nueva sección quedó bien formada, sin romper la tabla o encabezados previos.

- [ ] **Step 4: Commit**

```bash
git add RUBRICA_GENERAL.md
git commit -m "docs: agregar flujo de calificación con OrchestratorAgent a RUBRICA_GENERAL.md"
```

---

## Verificación Final (todo el plan)

### Task 22: Suite completa, regeneración final de notebooks, y checklist de la spec

**Files:** ninguno nuevo — solo verificación

- [ ] **Step 1: Suite completa de pytest**

```bash
pytest tests/ -v --tb=short
```

Expected: 100% passing. Contar el número total de tests y confirmar que es mayor a 63 (el número antes de este plan) — se espera un incremento de aproximadamente 45-50 tests nuevos entre `ContentAuditorAgent` (Tasks 4,6,7,8), `_mermaid_utils` (Task 9), routing de `OrchestratorAgent` (Task 11), debugger socrático y memoria episódica de `TutorAgent` (Tasks 13, 15), y `extract_fenced_blocks` (Task 2).

- [ ] **Step 2: Regenerar notebooks una última vez y confirmar 9/9**

```bash
python convert_to_notebooks_smart.py
```

Expected: "Convertidos con éxito: 9"

- [ ] **Step 3: Verificar dependencias sincronizadas**

```bash
python -m venv /tmp/final_check_venv
/tmp/final_check_venv/Scripts/python -m pip install -r requirements.txt -q
/tmp/final_check_venv/Scripts/python -c "import chromadb, pydantic, rich; print('Bloque 5 OK')"
```

- [ ] **Step 4: Confirmar `TutorAgent` en las 9 unidades**

```bash
grep -l "TutorAgent" notebooks/*.ipynb | wc -l
```

Expected: `9`

- [ ] **Step 5: Confirmar `.tutor_memory.json` ignorado por git**

```bash
git check-ignore .tutor_memory.json && echo "OK: ignorado"
```

- [ ] **Step 6: Checklist de cobertura de la spec (autoevaluación, no requiere comandos)**

Confirmar manualmente que cada bloque de la spec (`docs/superpowers/specs/2026-08-05-content-auditor-and-agent-connection-design.md`) tiene tarea(s) correspondiente(s) en este plan:
- Bloque 1 (`ContentAuditorAgent`, 4 dimensiones) → Tasks 2-8. ✓
- Bloque 2 (conectar 6 agentes) → Tasks 18-21. ✓
- Bloque 3a (debugger socrático) → Tasks 13-14. ✓
- Bloque 3b (routing) → Tasks 11-12. ✓
- Bloque 3c (SKILL_METADATA) → Task 17 (+ Tasks 5, 12 que ya lo incluyen inline). ✓
- Bloque 3d (refactor Mermaid) → Tasks 9-10. ✓
- Bloque 4 (memoria episódica) → Tasks 15-16. ✓
- Bloque 5 (sincronizar dependencias) → Task 1. ✓

- [ ] **Step 7: Commit final de verificación (si hubo algún ajuste menor durante esta tarea)**

```bash
git status
# Si hay cambios pendientes de las verificaciones, commitear; si no, no hacer nada.
```
