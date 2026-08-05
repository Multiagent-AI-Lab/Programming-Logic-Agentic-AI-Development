"""Tests de caracterización para NotebookCompilerAgent y MathAgent."""

from pathlib import Path

import nbformat
import pytest

from src.multiagent_core.notebook_compiler_agent import MathAgent, NotebookCompilerAgent


class TestMathAgent:
    def test_traduce_simbolos_unicode_comunes_a_latex(self):
        math_agent = MathAgent()
        resultado = math_agent.process_latex("La derivada parcial es ∂ y el gradiente ∇")
        assert r"\partial" in resultado
        assert r"\nabla" in resultado

    def test_envuelve_bloques_dollar_dollar_en_displaystyle(self):
        math_agent = MathAgent()
        resultado = math_agent.process_latex("$$x = y + z$$")
        assert r"\displaystyle" in resultado


class TestIsOnlyMath:
    def test_formula_simple_de_una_linea_es_matematica_pura(self):
        compiler = NotebookCompilerAgent()
        assert compiler._is_only_math("F = ∇ × E") is True

    def test_diagrama_ascii_con_simbolo_griego_no_es_matematica_pura(self):
        """Regresión: un diagrama de ejes/curvas en texto no debe tratarse como
        fórmula LaTeX solo porque contiene un símbolo griego (ej. Δ)."""
        compiler = NotebookCompilerAgent()
        diagrama = (
            "Energía ΔG\n"
            "   ^\n"
            "   |        * * * (Barrera de energía crítica ΔG*)\n"
            "   |      *       *\n"
            "---+-------------------> Radio r"
        )
        assert compiler._is_only_math(diagrama) is False


class TestNotebookCompilerAgentCompile:
    @pytest.fixture
    def markdown_fixture(self, tmp_path: Path) -> Path:
        contenido = """# Titulo de Prueba

Texto introductorio con formula $$E = mc^2$$.

```python
def calcular_area(radio: float) -> float:
    area = 3.14159 * radio ** 2
    if area > 100:
        categoria = "grande"
    else:
        categoria = "pequena"
    return area
```

Texto de cierre.
"""
        md_path = tmp_path / "UNIDAD_TEST.md"
        md_path.write_text(contenido, encoding="utf-8")
        return md_path

    def test_compile_genera_archivo_ipynb(self, markdown_fixture: Path, tmp_path: Path):
        compiler = NotebookCompilerAgent()
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_fixture, output_dir)
        assert nb_path.exists()
        assert nb_path.suffix == ".ipynb"

    def test_notebook_generado_tiene_celda_de_codigo_python(
        self, markdown_fixture: Path, tmp_path: Path
    ):
        compiler = NotebookCompilerAgent()
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_fixture, output_dir)

        nb = nbformat.read(nb_path, as_version=4)
        code_cells = [c for c in nb.cells if c.cell_type == "code"]
        assert len(code_cells) == 1
        assert "def calcular_area" in code_cells[0].source

    def test_notebook_generado_incluye_diagrama_mermaid_autogenerado(
        self, markdown_fixture: Path, tmp_path: Path
    ):
        compiler = NotebookCompilerAgent()
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_fixture, output_dir)

        nb = nbformat.read(nb_path, as_version=4)
        markdown_cells = [c for c in nb.cells if c.cell_type == "markdown"]
        assert any("```mermaid" in c.source for c in markdown_cells)

    def test_compile_crea_output_dir_si_no_existe(self, markdown_fixture: Path, tmp_path: Path):
        compiler = NotebookCompilerAgent()
        output_dir = tmp_path / "carpeta_inexistente" / "anidada"
        compiler.compile(markdown_fixture, output_dir)
        assert output_dir.exists()

    def test_lanza_error_si_markdown_no_existe(self, tmp_path: Path):
        compiler = NotebookCompilerAgent()
        with pytest.raises(FileNotFoundError):
            compiler.compile(tmp_path / "no_existe.md", tmp_path / "salida")


class TestFencesAnidados:
    """Regresión: un bloque ```markdown que contiene ejemplos ```python/```pytest
    anidados (fence exterior con 4 backticks) no debe cortarse en el primer
    fence interno de 3 backticks."""

    @pytest.fixture
    def markdown_con_fence_anidado(self, tmp_path: Path) -> Path:
        contenido = """# Unidad de Prueba

Ejemplo de archivo de entrega:

````markdown
# Entrega de Alumno

Texto de ejemplo.

```python
def suma(a: int, b: int) -> int:
    return a + b
```
````

Texto final tras el bloque anidado.
"""
        md_path = tmp_path / "UNIDAD_TEST_ANIDADO.md"
        md_path.write_text(contenido, encoding="utf-8")
        return md_path

    def test_bloque_anidado_se_preserva_como_una_sola_celda_markdown(
        self, markdown_con_fence_anidado: Path, tmp_path: Path
    ):
        compiler = NotebookCompilerAgent()
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_con_fence_anidado, output_dir)

        nb = nbformat.read(nb_path, as_version=4)
        markdown_cells = [c for c in nb.cells if c.cell_type == "markdown"]
        bloque = next((c for c in markdown_cells if "Entrega de Alumno" in c.source), None)
        assert bloque is not None
        assert "def suma" in bloque.source
        assert "return a + b" in bloque.source

    def test_fence_de_salida_preserva_la_cantidad_de_backticks_del_original(
        self, markdown_con_fence_anidado: Path, tmp_path: Path
    ):
        """El fence exterior debe seguir teniendo 4 backticks en la celda de salida;
        con solo 3 sería ambiguo frente al ```python anidado en su interior."""
        compiler = NotebookCompilerAgent()
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_con_fence_anidado, output_dir)

        nb = nbformat.read(nb_path, as_version=4)
        markdown_cells = [c for c in nb.cells if c.cell_type == "markdown"]
        bloque = next((c for c in markdown_cells if "Entrega de Alumno" in c.source), None)
        assert bloque.source.strip().startswith("````markdown")
        assert bloque.source.strip().endswith("````")

    def test_texto_posterior_al_bloque_anidado_no_se_pierde(
        self, markdown_con_fence_anidado: Path, tmp_path: Path
    ):
        compiler = NotebookCompilerAgent()
        output_dir = tmp_path / "notebooks_salida"
        nb_path = compiler.compile(markdown_con_fence_anidado, output_dir)

        nb = nbformat.read(nb_path, as_version=4)
        todo_el_texto = "\n".join(c.source for c in nb.cells)
        assert "Texto final tras el bloque anidado" in todo_el_texto


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
