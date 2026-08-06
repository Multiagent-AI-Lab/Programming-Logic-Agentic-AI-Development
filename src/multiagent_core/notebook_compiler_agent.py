"""
Agente Compilador de Notebooks (NotebookCompilerAgent) 🚀
=========================================================

Este agente parsea archivos Markdown de las lecciones y los convierte
en Jupyter Notebooks interactivos (.ipynb), enriqueciendo fórmulas LaTeX
y agregando desgloses didácticos de código.
"""

import re
from pathlib import Path
from typing import Optional

import nbformat as nbf

from .flowchart_agent import FlowchartAgent
from .mermaid_renderer import MermaidRenderer

SKILL_METADATA = {
    "name": "notebook_compiler_agent",
    "description": "Convierte MDs de las unidades del curso en notebooks .ipynb ejecutables.",
    "version": "1.0.0",
    "input": "md_filepath: Path, output_dir: Path",
    "output": "Path (ruta del .ipynb generado)",
    "requires_api_key": False,
}


class MathAgent:
    """Sub-Agente que traduce caracteres matemáticos UTF-8 comunes a su equivalente en LaTeX."""

    UNICODE_TO_LATEX = {
        "∂": r"\partial",
        "∇": r"\nabla",
        "²": r"^2",
        "³": r"^3",
        "⁴": r"^4",
        "₀": r"_0",
        "₁": r"_1",
        "₂": r"_2",
        "₃": r"_3",
        "≤": r"\leq",
        "≥": r"\geq",
        "≈": r"\approx",
        "∞": r"\infty",
        "∫": r"\int",
        "∑": r"\sum",
        "∏": r"\prod",
        "√": r"\sqrt",
        "×": r"\times",
        "÷": r"\div",
        "±": r"\pm",
        "≠": r"\neq",
        "α": r"\alpha",
        "β": r"\beta",
        "γ": r"\gamma",
        "δ": r"\delta",
        "ε": r"\varepsilon",
        "θ": r"\theta",
        "λ": r"\lambda",
        "μ": r"\mu",
        "π": r"\pi",
        "ρ": r"\rho",
        "σ": r"\sigma",
        "τ": r"\tau",
        "φ": r"\phi",
        "ψ": r"\psi",
        "ω": r"\omega",
        "Δ": r"\Delta",
        "ℏ": r"\hbar",
        "Å": r"\text{\r{A}}",
    }

    def process_latex(self, text: str) -> str:
        """Traduce símbolos matemáticos Unicode a LaTeX y envuelve fórmulas en \\displaystyle."""
        # Reemplazos simples de caracteres Unicode a comandos LaTeX
        for char, latex in self.UNICODE_TO_LATEX.items():
            text = text.replace(char, latex)

        # Forzar \displaystyle en ecuaciones largas $$...$$ y $...$
        text = re.sub(
            r"\$\$(.+?)\$\$",
            lambda m: f"$$\\displaystyle{{{m.group(1).strip()}}}$$",
            text,
            flags=re.DOTALL,
        )
        text = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", self._fix_inline, text)
        return text

    def _fix_inline(self, match):
        """Envuelve fórmulas inline complejas (fracciones, sumas, integrales) en \\displaystyle."""
        content = match.group(1).strip()
        if any(x in content for x in ["\\frac", "\\sum", "\\int", "\\geq", "\\leq"]):
            return "$\\displaystyle{" + content + "}$"
        return f"${content}$"


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


class NotebookCompilerAgent:
    """Agente que traduce un Markdown completo a un archivo .ipynb listo para los alumnos."""

    def __init__(self, mermaid_renderer: Optional[MermaidRenderer] = None) -> None:
        self.math_agent = MathAgent()
        self.flowchart_agent = FlowchartAgent()
        self.mermaid_renderer = mermaid_renderer or MermaidRenderer(
            output_dir=Path.cwd() / "notebooks" / "assets" / "diagramas"
        )

    def compile(self, md_filepath: Path, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        nb_path = output_dir / (md_filepath.stem + ".ipynb")

        with open(md_filepath, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        nb = nbf.v4.new_notebook()

        # Metadatos del notebook
        nb.metadata = {
            "kernelspec": {
                "display_name": "Python 3.11",
                "language": "python",
                "name": "python3",
            }
        }

        current_md = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Detectar celdas de código
            fence_match = re.match(r"^(`{3,})(.*)$", line)
            if fence_match:
                fence = fence_match.group(1)
                language = fence_match.group(2).strip()
                code_lines = []
                i += 1
                while i < len(lines) and lines[i].strip() != fence:
                    code_lines.append(lines[i])
                    i += 1

                code_content = "\n".join(code_lines)

                # Guardar markdown acumulado anterior
                if current_md:
                    md_text = "\n".join(current_md)
                    nb.cells.append(
                        nbf.v4.new_markdown_cell(self.math_agent.process_latex(md_text))
                    )
                    current_md = []

                # Si el código es ejecutable en Jupyter (Python)
                if language == "python" or language == "":
                    # Verificar si el código no es notación matemática pura en formato código
                    if not self._is_only_math(code_content):
                        # Agregar celda de código
                        nb.cells.append(nbf.v4.new_code_cell(code_content.strip()))

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
                    else:
                        # Si es notación matemática pura escrita en ```, transformarla
                        nb.cells.append(
                            nbf.v4.new_markdown_cell(
                                f"$$\\displaystyle{{{self.math_agent.process_latex(code_content)}}}$$"
                            )
                        )
                else:
                    # Otros lenguajes se mantienen como celdas de markdown descriptivas,
                    # preservando la longitud original del fence (p. ej. 4 backticks si
                    # el bloque contiene ejemplos con fences ``` anidados en su interior).
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

    def _is_only_math(self, text: str) -> bool:
        """Determina si un bloque de código es realmente notación matemática.

        Excluye diagramas de arte ASCII (ejes, flechas, curvas dibujadas con
        '|', '-', '*', '^', '>') que casualmente contienen un símbolo griego
        pero no son una fórmula LaTeX válida.
        """
        math_indicators = ["∂", "∇", "∫", "∑", "∏", "Δ"]
        ascii_art_chars = ("|", "^", "*", "+", ">", "<")
        lines = text.strip().split("\n")
        looks_like_ascii_art = (
            len(lines) > 2
            and sum(1 for line in lines if line.strip().startswith(ascii_art_chars))
            >= 2
        )
        return (
            any(x in text for x in math_indicators)
            and "def " not in text
            and "import " not in text
            and not looks_like_ascii_art
        )


if __name__ == "__main__":
    # Prueba de compilación rápida
    compiler = NotebookCompilerAgent()
    print("NotebookCompilerAgent inicializado.")
