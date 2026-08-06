# Renderizado SVG estático de diagramas Mermaid — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar los bloques de texto ` ```mermaid ` (13 manuales + hasta 35 autogenerados) por imágenes SVG pre-renderizadas embebidas, para que los diagramas se vean idénticos en VS Code, GitHub y Google Colab.

**Architecture:** Un componente nuevo `MermaidRenderer` (texto Mermaid → SVG en disco, con caché por hash SHA-256 y reintento ante fallo intermitente de Chromium) se inyecta en `NotebookCompilerAgent` (para los diagramas autogenerados por `FlowchartAgent`) y en `ContentAuditorAgent` (para detectar Mermaid con sintaxis inválida). Los 13 diagramas manuales de los `.md` se reemplazan directamente por script, usando URLs absolutas de GitHub porque el `.md` y el `.ipynb` viven en niveles de directorio distintos.

**Tech Stack:** Python 3.11, `@mermaid-js/mermaid-cli` (`mmdc`, vía `npx`, requiere Node.js), `subprocess`, `hashlib`, `tempfile`, pytest con mocks (sin invocar Node real en tests).

## Global Constraints

- TDD estricto: test que falla primero (RED), implementación mínima (GREEN), refactor, commit atómico.
- Type hints completos en todas las funciones públicas; docstrings estilo Google.
- Rutas de archivo/directorio siempre inyectables en el constructor — nunca hardcodeadas (mismo patrón que `chroma_path`/`memory_path` en `TutorAgent`, `programa_path` en `ContentAuditorAgent`).
- Ningún test debe invocar Node/`mmdc`/Chromium real — todo mockeado con `unittest.mock.patch` sobre `subprocess.run` y `shutil.which`.
- `subprocess.run` recibe la ruta absoluta resuelta de `npx` (vía `shutil.which("npx")`), nunca el literal `"npx"` — en Windows es `npx.cmd`, y nunca `shell=True` (el texto Mermaid va a un archivo temporal, no a un string de shell).
- black/isort/ruff limpios en cada archivo modificado o creado en `src/`.
- pytest 100% verde tras cada tarea que toque `src/` o `tests/`.
- Notebooks regenerados (`python convert_to_notebooks_smart.py`) tras cualquier cambio de contenido en un `.md`.
- Node.js es prerequisito de sistema (no un paquete Python) — documentado en `README.md`, verificado al inicio de `convert_to_notebooks_smart.py` con `shutil.which`, fallando rápido con instrucciones claras si falta.
- SVG generados se comitean a git (`notebooks/assets/diagramas/`) — las URLs de `raw.githubusercontent.com` usadas en los `.md` dependen de que existan en el repo remoto.

---

### Task 1: `MermaidRenderer` — caché, invocación de `mmdc`, reintento

**Files:**
- Create: `src/multiagent_core/mermaid_renderer.py`
- Test: `tests/test_mermaid_renderer.py`

**Interfaces:**
- Produces: `class MermaidRenderer` con `__init__(self, output_dir: Path) -> None` y `render(self, mermaid_source: str) -> Path`. Lanza `RuntimeError` si Node/`npx` no está disponible (en `__init__`) o si `mmdc` falla dos veces consecutivas (en `render`, con el `stderr` original incluido en el mensaje).

- [ ] **Step 1: Escribir el test de caché miss (primera invocación genera el SVG)**

```python
# tests/test_mermaid_renderer.py
"""Tests TDD para MermaidRenderer (texto Mermaid -> SVG con caché)."""

import hashlib
import subprocess
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
    def test_primera_invocacion_genera_svg_y_lo_retorna(self, npx_disponible, tmp_path: Path):
        renderer = MermaidRenderer(output_dir=tmp_path)
        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=_mock_subprocess_exitoso(tmp_path),
        ) as mock_run:
            resultado = renderer.render(MERMAID_VALIDO)

        assert resultado.exists()
        assert resultado.suffix == ".svg"
        assert mock_run.call_count == 1

    def test_nombre_del_svg_es_hash_sha256_del_texto(self, npx_disponible, tmp_path: Path):
        renderer = MermaidRenderer(output_dir=tmp_path)
        esperado = hashlib.sha256(MERMAID_VALIDO.encode()).hexdigest()[:16]
        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run",
            side_effect=_mock_subprocess_exitoso(tmp_path),
        ):
            resultado = renderer.render(MERMAID_VALIDO)

        assert resultado.name == f"{esperado}.svg"
```

- [ ] **Step 2: Correr el test, verificar que falla porque `mermaid_renderer.py` no existe**

Run: `pytest tests/test_mermaid_renderer.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'src.multiagent_core.mermaid_renderer'`

- [ ] **Step 3: Implementación mínima — caché miss, invocación básica**

```python
# src/multiagent_core/mermaid_renderer.py
"""
Agente Renderizador de Mermaid (MermaidRenderer) 🎨
====================================================

Convierte texto de diagrama Mermaid en un archivo SVG estático, con caché
por hash de contenido, para que los diagramas se vean idénticos en
VS Code, GitHub y Google Colab (que no renderiza ```mermaid``` nativamente).
"""

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

SKILL_METADATA = {
    "name": "mermaid_renderer",
    "description": "Renderiza texto Mermaid a SVG estático con caché por hash de contenido.",
    "version": "1.0.0",
    "input": "mermaid_source: str",
    "output": "Path (ruta del .svg generado o cacheado)",
    "requires_api_key": False,
}

_HASH_LENGTH = 16


class MermaidRenderer:
    """Convierte texto Mermaid en SVG, cacheado por hash SHA-256 del contenido."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        npx_path = shutil.which("npx")
        if npx_path is None:
            raise RuntimeError(
                "Node.js no está instalado o 'npx' no está en el PATH. "
                "Los diagramas Mermaid requieren Node.js para renderizarse como SVG. "
                "Instalar con: winget install OpenJS.NodeJS (Windows) o desde https://nodejs.org"
            )
        self._npx_path = npx_path

    def render(self, mermaid_source: str) -> Path:
        """Renderiza texto Mermaid a SVG, reusando el archivo cacheado si existe.

        Args:
            mermaid_source: Texto del diagrama Mermaid (sin los fences ```mermaid).

        Returns:
            Ruta al archivo .svg generado o previamente cacheado.
        """
        file_hash = hashlib.sha256(mermaid_source.encode("utf-8")).hexdigest()[:_HASH_LENGTH]
        svg_path = self.output_dir / f"{file_hash}.svg"
        if svg_path.exists():
            return svg_path

        self._render_con_mmdc(mermaid_source, svg_path)
        return svg_path

    def _render_con_mmdc(self, mermaid_source: str, svg_path: Path) -> None:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".mmd", delete=False, encoding="utf-8"
        )
        try:
            tmp_file.write(mermaid_source)
            tmp_file.close()
            cmd = [
                self._npx_path,
                "--yes",
                "@mermaid-js/mermaid-cli",
                "-i",
                tmp_file.name,
                "-o",
                str(svg_path),
                "-b",
                "white",
            ]
            resultado = subprocess.run(cmd, capture_output=True, text=True)
            if resultado.returncode != 0:
                raise RuntimeError(resultado.stderr)
        finally:
            Path(tmp_file.name).unlink(missing_ok=True)
```

- [ ] **Step 4: Correr el test, verificar que pasa**

Run: `pytest tests/test_mermaid_renderer.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Escribir el test de caché hit (segunda llamada no invoca `mmdc`)**

```python
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
```

- [ ] **Step 6: Correr el test, verificar que pasa sin cambios de implementación**

Run: `pytest tests/test_mermaid_renderer.py -v`
Expected: PASS (3 tests) — el chequeo `if svg_path.exists()` del Step 3 ya cubre este caso.

- [ ] **Step 7: Escribir el test del archivo temporal (se crea y se borra en éxito y en fallo)**

```python
class TestArchivoTemporal:
    def test_temporal_se_borra_tras_render_exitoso(self, npx_disponible, tmp_path: Path):
        renderer = MermaidRenderer(output_dir=tmp_path)
        rutas_temporales = []

        def side_effect(cmd, *args, **kwargs):
            rutas_temporales.append(Path(cmd[cmd.index("-i") + 1]))
            svg_path = Path(cmd[cmd.index("-o") + 1])
            svg_path.write_text("<svg></svg>", encoding="utf-8")
            return MagicMock(returncode=0, stderr="")

        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run", side_effect=side_effect
        ):
            renderer.render(MERMAID_VALIDO)

        assert not rutas_temporales[0].exists()

    def test_temporal_se_borra_incluso_si_mmdc_falla(self, npx_disponible, tmp_path: Path):
        renderer = MermaidRenderer(output_dir=tmp_path)
        rutas_temporales = []

        def side_effect(cmd, *args, **kwargs):
            rutas_temporales.append(Path(cmd[cmd.index("-i") + 1]))
            return MagicMock(returncode=1, stderr="Parse error on line 1")

        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run", side_effect=side_effect
        ):
            with pytest.raises(RuntimeError):
                renderer.render("graph TD\n    A[Roto(sin comillas)]")

        assert not rutas_temporales[0].exists()
```

- [ ] **Step 8: Correr el test, verificar que pasa**

Run: `pytest tests/test_mermaid_renderer.py -v`
Expected: PASS (5 tests) — el `finally` del Step 3 ya cubre ambos casos.

- [ ] **Step 9: Escribir el test de reintento (falla una vez, luego tiene éxito)**

```python
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
            "src.multiagent_core.mermaid_renderer.subprocess.run", side_effect=side_effect
        ):
            resultado = renderer.render(MERMAID_VALIDO)

        assert resultado.exists()
        assert llamadas["count"] == 2

    def test_propaga_error_tras_dos_fallos_consecutivos(self, npx_disponible, tmp_path: Path):
        renderer = MermaidRenderer(output_dir=tmp_path)

        def side_effect(cmd, *args, **kwargs):
            return MagicMock(returncode=1, stderr="Parse error on line 3")

        with patch(
            "src.multiagent_core.mermaid_renderer.subprocess.run", side_effect=side_effect
        ):
            with pytest.raises(RuntimeError, match="Parse error"):
                renderer.render("graph TD\n    A[Roto(sin comillas)]")
```

- [ ] **Step 10: Correr el test, verificar que falla (aún no hay reintento)**

Run: `pytest tests/test_mermaid_renderer.py::TestReintento -v`
Expected: FAIL en `test_reintenta_una_vez_si_mmdc_falla_la_primera_vez` — `llamadas["count"] == 1`, no `2`.

- [ ] **Step 11: Implementar el reintento en `_render_con_mmdc`**

```python
    def _render_con_mmdc(self, mermaid_source: str, svg_path: Path) -> None:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".mmd", delete=False, encoding="utf-8"
        )
        try:
            tmp_file.write(mermaid_source)
            tmp_file.close()
            cmd = [
                self._npx_path,
                "--yes",
                "@mermaid-js/mermaid-cli",
                "-i",
                tmp_file.name,
                "-o",
                str(svg_path),
                "-b",
                "white",
            ]
            ultimo_error = ""
            for intento in range(2):
                resultado = subprocess.run(cmd, capture_output=True, text=True)
                if resultado.returncode == 0:
                    return
                ultimo_error = resultado.stderr
            raise RuntimeError(ultimo_error)
        finally:
            Path(tmp_file.name).unlink(missing_ok=True)
```

- [ ] **Step 12: Correr todos los tests de `MermaidRenderer`**

Run: `pytest tests/test_mermaid_renderer.py -v`
Expected: PASS (7 tests)

- [ ] **Step 13: Escribir el test de Node no disponible**

```python
class TestNodeNoDisponible:
    def test_lanza_runtime_error_si_npx_no_esta_en_path(self, tmp_path: Path):
        with patch("src.multiagent_core.mermaid_renderer.shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="Node.js"):
                MermaidRenderer(output_dir=tmp_path)
```

- [ ] **Step 14: Correr el test, verificar que pasa sin cambios (ya implementado en Step 3)**

Run: `pytest tests/test_mermaid_renderer.py -v`
Expected: PASS (8 tests)

- [ ] **Step 15: Formatear, ordenar imports, lint**

```bash
python -m isort src/multiagent_core/mermaid_renderer.py tests/test_mermaid_renderer.py
python -m black src/multiagent_core/mermaid_renderer.py tests/test_mermaid_renderer.py
python -m ruff check src/multiagent_core/mermaid_renderer.py tests/test_mermaid_renderer.py
```

- [ ] **Step 16: Commit**

```bash
git add src/multiagent_core/mermaid_renderer.py tests/test_mermaid_renderer.py
git commit -m "feat: agregar MermaidRenderer (texto Mermaid -> SVG con caché y reintento)"
```

---

### Task 2: Integrar `MermaidRenderer` en `NotebookCompilerAgent`

**Files:**
- Modify: `src/multiagent_core/notebook_compiler_agent.py:131-137` (constructor), `:191-201` (inyección del diagrama autogenerado)
- Modify: `tests/test_notebook_compiler_agent.py` (fixture compartida + 4 tests que llaman `compile()`)

**Interfaces:**
- Consumes: `MermaidRenderer(output_dir: Path)` y `MermaidRenderer.render(mermaid_source: str) -> Path` de Task 1.
- Produces: `NotebookCompilerAgent.__init__(self, mermaid_renderer: Optional[MermaidRenderer] = None) -> None`. Si `mermaid_renderer` es `None`, construye uno propio apuntando a `<cwd>/notebooks/assets/diagramas` (comportamiento de producción); los tests siempre inyectan un mock.

- [ ] **Step 1: Escribir el test de integración (el markdown generado usa `<img>` + `<details>`, no el bloque crudo)**

Reemplazar el test existente en `tests/test_notebook_compiler_agent.py:85-94`:

```python
    def test_notebook_generado_incluye_diagrama_mermaid_autogenerado(
        self, markdown_fixture: Path, tmp_path: Path, mermaid_renderer_mock
    ):
        compiler = NotebookCompilerAgent(mermaid_renderer=mermaid_renderer_mock)
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_fixture, output_dir)

        nb = nbformat.read(nb_path, as_version=4)
        markdown_cells = [c for c in nb.cells if c.cell_type == "markdown"]
        celda_diagrama = next(
            c for c in markdown_cells if "Diagrama de Flujo Autogenerado" in c.source
        )
        assert "<img src=" in celda_diagrama.source
        assert "<details>" in celda_diagrama.source
        assert "```mermaid" in celda_diagrama.source

        nombre_svg = mermaid_renderer_mock.render.return_value.name
        assert f'src="assets/diagramas/{nombre_svg}"' in celda_diagrama.source
```

Agregar la fixture compartida al inicio de `TestNotebookCompilerAgentCompile` (antes de `markdown_fixture`, línea 44):

```python
    @pytest.fixture
    def mermaid_renderer_mock(self, tmp_path: Path):
        from unittest.mock import MagicMock

        mock = MagicMock()
        svg_path = tmp_path / "diagrama_falso.svg"
        svg_path.write_text("<svg></svg>", encoding="utf-8")
        mock.render.return_value = svg_path
        return mock
```

- [ ] **Step 2: Actualizar las otras 3 llamadas a `compiler.compile()` en la misma clase para inyectar el mock**

En `tests/test_notebook_compiler_agent.py`, las líneas 67, 77 y 98 (`test_compile_genera_archivo_ipynb`, `test_notebook_generado_tiene_celda_de_codigo_python`, `test_compile_crea_output_dir_si_no_existe`) cambian:

```python
    def test_compile_genera_archivo_ipynb(
        self, markdown_fixture: Path, tmp_path: Path, mermaid_renderer_mock
    ):
        compiler = NotebookCompilerAgent(mermaid_renderer=mermaid_renderer_mock)
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_fixture, output_dir)
        assert nb_path.exists()
        assert nb_path.suffix == ".ipynb"

    def test_notebook_generado_tiene_celda_de_codigo_python(
        self, markdown_fixture: Path, tmp_path: Path, mermaid_renderer_mock
    ):
        compiler = NotebookCompilerAgent(mermaid_renderer=mermaid_renderer_mock)
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_fixture, output_dir)

        nb = nbformat.read(nb_path, as_version=4)
        code_cells = [c for c in nb.cells if c.cell_type == "code"]
        assert len(code_cells) == 1
        assert "def calcular_area" in code_cells[0].source

    def test_compile_crea_output_dir_si_no_existe(
        self, markdown_fixture: Path, tmp_path: Path, mermaid_renderer_mock
    ):
        compiler = NotebookCompilerAgent(mermaid_renderer=mermaid_renderer_mock)
        output_dir = tmp_path / "carpeta_inexistente" / "anidada"
        compiler.compile(markdown_fixture, output_dir)
        assert output_dir.exists()
```

`test_lanza_error_si_markdown_no_existe` (línea 102) no usa `markdown_fixture` y no llega a la rama del flowchart (falla antes, al abrir el archivo) — no necesita el mock, se deja igual.

- [ ] **Step 3: Correr los tests, verificar que fallan (constructor aún no acepta `mermaid_renderer`)**

Run: `pytest tests/test_notebook_compiler_agent.py -v`
Expected: FAIL con `TypeError: NotebookCompilerAgent.__init__() got an unexpected keyword argument 'mermaid_renderer'`

- [ ] **Step 4: Modificar el constructor de `NotebookCompilerAgent`**

En `src/multiagent_core/notebook_compiler_agent.py`, agregar el import y modificar `__init__` (líneas 10-15 y 131-137):

```python
import re
from pathlib import Path
from typing import Optional

import nbformat as nbf

from .flowchart_agent import FlowchartAgent
from .mermaid_renderer import MermaidRenderer
```

```python
class NotebookCompilerAgent:
    """Agente que traduce un Markdown completo a un archivo .ipynb listo para los alumnos."""

    def __init__(self, mermaid_renderer: Optional[MermaidRenderer] = None) -> None:
        self.math_agent = MathAgent()
        self.flowchart_agent = FlowchartAgent()
        self.mermaid_renderer = mermaid_renderer or MermaidRenderer(
            output_dir=Path.cwd() / "notebooks" / "assets" / "diagramas"
        )
```

- [ ] **Step 5: Modificar la inyección del diagrama autogenerado**

En `notebook_compiler_agent.py:191-201`, reemplazar:

```python
                        # Generar diagrama de flujo autointegrado (si es una función y el usuario lo desea)
                        if "def " in code_content and len(code_lines) > 5:
                            mermaid_flow = self.flowchart_agent.build_mermaid_flowchart(
                                code_content
                            )
                            if "graph TD" in mermaid_flow:
                                svg_path = self.mermaid_renderer.render(mermaid_flow)
                                rel_path = f"assets/diagramas/{svg_path.name}"
                                nb.cells.append(
                                    nbf.v4.new_markdown_cell(
                                        f"#### 📊 Diagrama de Flujo Autogenerado:\n\n"
                                        f'<img src="{rel_path}" alt="Diagrama de flujo Mermaid" '
                                        f'style="max-width: 100%; background-color: white; padding: 8px;">\n\n'
                                        f"<details>\n<summary>Ver código fuente Mermaid (editable)</summary>\n\n"
                                        f"```mermaid\n{mermaid_flow}\n```\n\n</details>"
                                    )
                                )
```

- [ ] **Step 6: Correr los tests**

Run: `pytest tests/test_notebook_compiler_agent.py -v`
Expected: PASS (todos)

- [ ] **Step 7: Correr la suite completa (verificar que no se rompió nada en otros archivos que instancian `NotebookCompilerAgent`)**

Run: `pytest tests/ -v --tb=short`
Expected: PASS 100% — `ContentAuditorAgent` importa `extract_fenced_blocks` (función a nivel de módulo, no la clase) de `notebook_compiler_agent.py`, así que no debería verse afectado por el cambio de constructor.

- [ ] **Step 8: Formatear, ordenar imports, lint**

```bash
python -m isort src/multiagent_core/notebook_compiler_agent.py tests/test_notebook_compiler_agent.py
python -m black src/multiagent_core/notebook_compiler_agent.py tests/test_notebook_compiler_agent.py
python -m ruff check src/multiagent_core/notebook_compiler_agent.py tests/test_notebook_compiler_agent.py
```

- [ ] **Step 9: Commit**

```bash
git add src/multiagent_core/notebook_compiler_agent.py tests/test_notebook_compiler_agent.py
git commit -m "feat: NotebookCompilerAgent renderiza diagramas autogenerados como SVG embebido"
```

---

### Task 3: Verificación de Node en `convert_to_notebooks_smart.py`

**Files:**
- Modify: `convert_to_notebooks_smart.py`

**Interfaces:**
- Consumes: `shutil.which` (stdlib).
- Produces: ninguno (script de entrada, no expone interfaz a otras tareas).

- [ ] **Step 1: Agregar el chequeo de Node al inicio del script**

En `convert_to_notebooks_smart.py`, modificar el bloque `if __name__ == "__main__":`:

```python
"""
CONVERSOR INTELIGENTE DE MARKDOWN A NOTEBOOKS (CONSEJO DE AGENTES) 🚀
===================================================================

Script de automatización que utiliza el NotebookCompilerAgent del consejo de agentes
para transformar las lecciones Markdown del repositorio en Jupyter Notebooks listos
para su uso por parte de los estudiantes.
"""

import shutil
import sys
from pathlib import Path

from src.multiagent_core.notebook_compiler_agent import NotebookCompilerAgent

if __name__ == "__main__":
    if shutil.which("npx") is None:
        print("ERROR: Node.js no está instalado o 'npx' no está en el PATH.")
        print("Los diagramas Mermaid requieren Node.js para renderizarse como SVG.")
        print("Instalar con: winget install OpenJS.NodeJS (Windows) o desde https://nodejs.org")
        sys.exit(1)

    BASE_DIR = Path(__file__).parent
    output_dir = BASE_DIR / "notebooks"
    output_dir.mkdir(exist_ok=True)
```

El resto del script (`files_to_convert`, el loop de conversión) queda igual.

- [ ] **Step 2: Verificar manualmente que el script sigue corriendo con Node disponible**

Run: `python convert_to_notebooks_smart.py`
Expected: `Convertidos con exito: 9` (igual que antes), sin el mensaje de error de Node (ya que sí está instalado en esta máquina).

- [ ] **Step 3: Formatear, ordenar imports, lint**

```bash
python -m isort convert_to_notebooks_smart.py
python -m black convert_to_notebooks_smart.py
python -m ruff check convert_to_notebooks_smart.py
```

- [ ] **Step 4: Commit**

```bash
git add convert_to_notebooks_smart.py
git commit -m "feat: verificar disponibilidad de Node.js al inicio de convert_to_notebooks_smart.py"
```

---

### Task 4: Reemplazar los 13 diagramas manuales en los `.md` por imagen + fuente colapsada

**Files:**
- Modify: `UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md` (3 diagramas)
- Modify: `UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md` (3 diagramas)
- Modify: `UNIDAD_4_ESTRUCTURAS_DECISION.md` (2 diagramas — ya con la sintaxis corregida de la investigación previa)
- Modify: `UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md` (2 diagramas — ya con la sintaxis corregida de la investigación previa)
- Modify: `UNIDAD_6_MODULARIDAD_IA_MCP.md` (2 diagramas)
- Modify: `UNIDAD_8_PROYECTO_INTEGRADOR.md` (1 diagrama)
- Create: 13 archivos en `notebooks/assets/diagramas/<hash>.svg`

**Interfaces:**
- Consumes: `MermaidRenderer` de Task 1 (se invoca desde un script puntual, no queda como código de producción).

- [ ] **Step 1: Escribir el script de reemplazo (uso único, no forma parte de `src/`)**

```python
# scripts/replace_manual_mermaid_diagrams.py (temporal, se borra tras usarlo)
"""Reemplaza los bloques ```mermaid``` manuales de 6 UNIDAD_*.md por <img> + <details>."""

import re
from pathlib import Path

from src.multiagent_core.mermaid_renderer import MermaidRenderer

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "notebooks" / "assets" / "diagramas"
RAW_BASE = (
    "https://raw.githubusercontent.com/Multiagent-AI-Lab/"
    "Programming-Logic-Agentic-AI-Development/master/notebooks/assets/diagramas"
)

UNITS = [
    "UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md",
    "UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md",
    "UNIDAD_4_ESTRUCTURAS_DECISION.md",
    "UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md",
    "UNIDAD_6_MODULARIDAD_IA_MCP.md",
    "UNIDAD_8_PROYECTO_INTEGRADOR.md",
]

FENCE_RE = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)


def make_replacement(renderer: MermaidRenderer, mermaid_source: str) -> str:
    svg_path = renderer.render(mermaid_source)
    url = f"{RAW_BASE}/{svg_path.name}"
    return (
        f'<img src="{url}" alt="Diagrama de flujo Mermaid" '
        f'style="max-width: 100%; background-color: white; padding: 8px;">\n\n'
        f"<details>\n<summary>Ver código fuente Mermaid (editable)</summary>\n\n"
        f"```mermaid\n{mermaid_source}\n```\n\n</details>"
    )


def main() -> None:
    renderer = MermaidRenderer(output_dir=ASSETS_DIR)
    for unit_name in UNITS:
        path = PROJECT_ROOT / unit_name
        content = path.read_text(encoding="utf-8")
        nuevo_contenido = FENCE_RE.sub(
            lambda m: make_replacement(renderer, m.group(1)), content
        )
        path.write_text(nuevo_contenido, encoding="utf-8")
        print(f"{unit_name}: reemplazado")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Ejecutar el script**

Run: `python scripts/replace_manual_mermaid_diagrams.py`
Expected: 6 líneas `<UNIDAD>: reemplazado`, y 13 archivos `.svg` nuevos en `notebooks/assets/diagramas/` (nombrados por hash, distintos de los 13 SVG de nombre descriptivo generados durante la investigación de diseño — esos se eliminan en el Step 4).

- [ ] **Step 3: Verificar visualmente que cada `.md` tiene el patrón esperado**

```bash
grep -c "<details>" UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md UNIDAD_4_ESTRUCTURAS_DECISION.md UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md UNIDAD_6_MODULARIDAD_IA_MCP.md UNIDAD_8_PROYECTO_INTEGRADOR.md
```

Expected: 3, 3, 2, 2, 2, 1 respectivamente (coincide con el conteo de diagramas por unidad).

- [ ] **Step 4: Eliminar los SVG de nombre descriptivo generados durante la investigación de diseño (ya reemplazados por los de nombre-hash)**

```bash
rm notebooks/assets/diagramas/u1_pensamiento_computacional_cli_diagrama_*.svg
rm notebooks/assets/diagramas/u2_metodologia_algoritmos_pruebas_diagrama_*.svg
rm notebooks/assets/diagramas/u4_estructuras_decision_diagrama_*.svg
rm notebooks/assets/diagramas/u5_ciclos_bucles_agenticos_diagrama_*.svg
rm notebooks/assets/diagramas/u6_modularidad_ia_mcp_diagrama_*.svg
rm notebooks/assets/diagramas/u8_proyecto_integrador_diagrama_*.svg
```

- [ ] **Step 5: Borrar el script de uso único**

```bash
rm scripts/replace_manual_mermaid_diagrams.py
```

- [ ] **Step 6: Regenerar los 9 notebooks**

Run: `python convert_to_notebooks_smart.py`
Expected: `Convertidos con exito: 9`

- [ ] **Step 7: Correr la suite completa de tests**

Run: `pytest tests/ -v --tb=short`
Expected: PASS 100%

- [ ] **Step 8: Commit**

```bash
git add UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md UNIDAD_4_ESTRUCTURAS_DECISION.md UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md UNIDAD_6_MODULARIDAD_IA_MCP.md UNIDAD_8_PROYECTO_INTEGRADOR.md notebooks/
git commit -m "fix: reemplazar diagramas Mermaid manuales por SVG embebido (Colab no los renderiza como texto)"
```

---

### Task 5: `ContentAuditorAgent` detecta Mermaid con sintaxis inválida

**Files:**
- Modify: `src/multiagent_core/content_auditor_agent.py:91-98` (constructor), `:194-221` (`_audit_pedagogico`)
- Modify: `tests/test_content_auditor_agent.py` (fixture + 2 tests nuevos)

**Interfaces:**
- Consumes: `MermaidRenderer(output_dir: Path)` y `MermaidRenderer.render(mermaid_source: str) -> Path` de Task 1. `extract_fenced_blocks()` (ya existente) retorna `list[tuple[str, str, str]]` de `(fence, language, code)` — los bloques con `language == "mermaid"` son los que se validan.
- Produces: `ContentAuditorAgent.__init__(self, programa_path: Optional[Path] = None, mermaid_renderer: Optional[MermaidRenderer] = None) -> None`.

- [ ] **Step 1: Escribir el test de detección de sintaxis inválida**

```python
# tests/test_content_auditor_agent.py — agregar al final del archivo
class TestValidacionSintaxisMermaid:
    @pytest.fixture
    def auditor_con_mermaid_mock(self):
        from unittest.mock import MagicMock

        mock_renderer = MagicMock()
        return ContentAuditorAgent(mermaid_renderer=mock_renderer), mock_renderer

    def test_detecta_diagrama_mermaid_con_error_de_sintaxis(
        self, auditor_con_mermaid_mock, tmp_path: Path
    ):
        auditor, mock_renderer = auditor_con_mermaid_mock
        mock_renderer.render.side_effect = RuntimeError(
            "Parse error on line 1: Expecting 'TEXT', got 'PS'"
        )
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n```mermaid\ngraph TD\n    A[Roto(sin comillas)]\n```\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert any(
            "sintaxis" in h.lower() for h in resultado["hallazgos"]["pedagogico"]
        )

    def test_no_marca_diagrama_mermaid_valido_como_error(
        self, auditor_con_mermaid_mock, tmp_path: Path
    ):
        auditor, mock_renderer = auditor_con_mermaid_mock
        mock_renderer.render.return_value = tmp_path / "hash123.svg"
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(
            "# Test\n\n```mermaid\ngraph TD\n    A[Inicio] --> B[Fin]\n```\n",
            encoding="utf-8",
        )
        resultado = auditor.audit_unit(md_path)
        assert not any(
            "sintaxis" in h.lower() for h in resultado["hallazgos"]["pedagogico"]
        )
```

- [ ] **Step 2: Correr el test, verificar que falla (constructor aún no acepta `mermaid_renderer`)**

Run: `pytest tests/test_content_auditor_agent.py::TestValidacionSintaxisMermaid -v`
Expected: FAIL con `TypeError: ContentAuditorAgent.__init__() got an unexpected keyword argument 'mermaid_renderer'`

- [ ] **Step 3: Modificar el constructor de `ContentAuditorAgent`**

En `src/multiagent_core/content_auditor_agent.py`, agregar el import y modificar `__init__`:

```python
from .code_auditor_agent import CodeAuditorAgent
from .mermaid_renderer import MermaidRenderer
from .notebook_compiler_agent import extract_fenced_blocks
```

```python
    def __init__(
        self,
        programa_path: Optional[Path] = None,
        mermaid_renderer: Optional[MermaidRenderer] = None,
    ) -> None:
        self.code_auditor = CodeAuditorAgent()
        self.programa_path = (
            Path(programa_path) if programa_path else _PROGRAMA_OFICIAL_PATH
        )
        self.mermaid_renderer = mermaid_renderer or MermaidRenderer(
            output_dir=Path.cwd() / "notebooks" / "assets" / "diagramas"
        )
```

- [ ] **Step 4: Agregar la validación de sintaxis en `_audit_pedagogico`**

Modificar la firma y el cuerpo de `_audit_pedagogico` en `content_auditor_agent.py:194-221`:

```python
    def _audit_pedagogico(self, bloques: List[tuple], content: str) -> List[str]:
        """Verifica coherencia pedagógica: Hilo de Oro, analogías, y sintaxis Mermaid.

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

        if not re.search(r"^#{2,4}.*analog", content, re.IGNORECASE | re.MULTILINE):
            hallazgos.append(
                "No se encontró ninguna sección de Analogía Didáctica "
                "(encabezado H2-H4 que contenga 'analog...') en esta unidad."
            )

        mermaid_blocks = [code for _, lang, code in bloques if lang == "mermaid"]
        for diagrama in mermaid_blocks:
            try:
                self.mermaid_renderer.render(diagrama)
            except RuntimeError as e:
                if "Parse error" in str(e):
                    hallazgos.append(
                        f"Diagrama Mermaid con error de sintaxis: {str(e).splitlines()[0]}"
                    )

        return hallazgos
```

- [ ] **Step 5: Correr los tests nuevos**

Run: `pytest tests/test_content_auditor_agent.py::TestValidacionSintaxisMermaid -v`
Expected: PASS (2 tests)

- [ ] **Step 6: Correr la suite completa de `ContentAuditorAgent`**

Run: `pytest tests/test_content_auditor_agent.py -v`
Expected: PASS 100% (verifica que el `auditor` fixture existente, que usa `ContentAuditorAgent()` sin argumentos, sigue funcionando — construye su propio `MermaidRenderer` real, pero como ningún otro test de este archivo tiene bloques ` ```mermaid ` en su MD de prueba, `render()` nunca se invoca en esos casos).

- [ ] **Step 7: Correr la suite completa del proyecto**

Run: `pytest tests/ -v --tb=short`
Expected: PASS 100%

- [ ] **Step 8: Formatear, ordenar imports, lint**

```bash
python -m isort src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
python -m black src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
python -m ruff check src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
```

- [ ] **Step 9: Commit**

```bash
git add src/multiagent_core/content_auditor_agent.py tests/test_content_auditor_agent.py
git commit -m "feat: ContentAuditorAgent detecta diagramas Mermaid con sintaxis inválida"
```

---

### Task 6: Documentar el prerequisito de Node.js y regenerar el reporte de auditoría

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `docs/superpowers/content_audit_report.md` (regenerado, no editado a mano)

**Interfaces:** ninguna (documentación y regeneración de reporte).

- [ ] **Step 1: Agregar la sección de prerequisito de Node.js al README**

En `README.md`, tras la sección "🚀 Configuración del Entorno de Trabajo" (después del bloque de registro del kernel Jupyter, antes de "🛠️ Guía de Herramientas"), agregar:

```markdown
### 4. Instalar Node.js (requerido para diagramas Mermaid)

Los diagramas de flujo del curso se renderizan como imágenes SVG estáticas
(para verse igual en VS Code, GitHub y Google Colab), usando
`@mermaid-js/mermaid-cli` vía `npx`. Esto requiere Node.js instalado en el
sistema — no es un paquete de Python, no se instala vía conda/pip:

```bash
winget install OpenJS.NodeJS
```

O descárgalo desde [nodejs.org](https://nodejs.org). `convert_to_notebooks_smart.py`
verifica automáticamente si Node.js está disponible al iniciar y muestra
instrucciones si falta.
```

- [ ] **Step 2: Actualizar la mención de agentes sin Node en `CLAUDE.md`**

En `CLAUDE.md`, en el bloque de "Comandos esenciales", tras la línea de `# Regenerar los 9 notebooks tras editar cualquier UNIDAD_*.md`, agregar una nota:

```markdown
Requiere Node.js instalado (`npx` en el PATH) — los diagramas Mermaid se renderizan a SVG vía `@mermaid-js/mermaid-cli`; el script verifica esto al inicio y falla con instrucciones claras si falta.
```

- [ ] **Step 3: Regenerar el reporte de auditoría de contenido**

```python
from pathlib import Path
from src.multiagent_core.content_auditor_agent import ContentAuditorAgent

auditor = ContentAuditorAgent()
reporte = auditor.audit_all_units(Path("."))
Path("docs/superpowers/content_audit_report.md").write_text(reporte, encoding="utf-8")
```

Run como script de una línea o desde una sesión interactiva de Python en la raíz del proyecto.

- [ ] **Step 4: Revisar el reporte regenerado — comparar el conteo de hallazgos "pedagogico" contra el reporte anterior**

El reporte anterior (previo a esta tarea) tenía 31 hallazgos, todos de la categoría "Hilo de Oro incompleto" documentada como ruido de convención. Si la nueva validación de sintaxis Mermaid encuentra algo, aparecerá como un hallazgo nuevo con el texto "Diagrama Mermaid con error de sintaxis" — dado que los 2 errores reales conocidos (U4, U5) ya se corrigieron en la investigación previa a este plan, se espera que el conteo total no aumente. Si aparece alguno inesperado, investigarlo antes de continuar (no ignorarlo).

- [ ] **Step 5: Commit**

```bash
git add README.md CLAUDE.md docs/superpowers/content_audit_report.md
git commit -m "docs: documentar prerequisito de Node.js y regenerar reporte de auditoría"
```

---

### Task 7: Verificación final end-to-end

**Files:** ninguno modificado — solo verificación.

**Interfaces:** ninguna.

- [ ] **Step 1: Correr la suite completa de tests**

Run: `pytest tests/ -v --tb=short`
Expected: PASS 100%

- [ ] **Step 2: Regenerar los 9 notebooks desde cero (confirmar que el pipeline completo funciona junto)**

Run: `python convert_to_notebooks_smart.py`
Expected: `Convertidos con exito: 9`, sin errores.

- [ ] **Step 3: Verificar que no quedan bloques ` ```mermaid ` sin envolver en `<details>` en ningún `.md`**

```bash
grep -rn '```mermaid' UNIDAD_*.md
```

Expected: cada ocurrencia debe estar precedida por un `<img src=` y envuelta en `<details>` en las líneas cercanas (verificación visual del grep, no solo conteo — confirmar que no quedó ningún bloque suelto sin reemplazar).

- [ ] **Step 4: Verificar que los SVG de los 13 diagramas manuales están commiteados**

```bash
git status --short notebooks/assets/diagramas/
```

Expected: vacío (todo ya comiteado en tareas anteriores) — si aparece algo, es un olvido de una tarea previa, agregarlo y commitearlo antes de terminar.

- [ ] **Step 5: Push a GitHub**

```bash
git push origin master
```

- [ ] **Step 6: Verificar manualmente en el navegador**

Abrir `https://github.com/Multiagent-AI-Lab/Programming-Logic-Agentic-AI-Development/blob/master/UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md` y confirmar que los diagramas se ven como imagen. Abrir el notebook correspondiente en Colab y confirmar lo mismo.
