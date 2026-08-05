"""
Agente de Pseudocódigo (PseudocodeAgent) - Lógica de Programación UCEMICH 📝
============================================================================

Traduce entre la convención de pseudocódigo UCEMICH 2026 (ver
UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md), diagramas Mermaid y Python,
reforzando el Hilo de Oro del curso: Pseudocódigo → Mermaid → Python → pytest.
"""

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

    def pseudocode_to_mermaid(self, pseudocode: str) -> str:
        """Traduce pseudocódigo UCEMICH (SI/PARA/MIENTRAS) a un diagrama Mermaid."""
        self.node_counter = 0
        lines = [
            line.strip() for line in pseudocode.strip().split("\n") if line.strip()
        ]

        mermaid_lines = ["graph TD", "    start([Inicio])"]
        last_node = "start"

        if_id = None
        for line in lines:
            if line.upper().startswith("SI "):
                cond_id = self._next_node_id()
                condicion = line[3:].split("ENTONCES")[0].strip()
                mermaid_lines.append(f'    {cond_id}{{{{"SI {condicion}?"}}}}')
                mermaid_lines.append(f"    {last_node} --> {cond_id}")
                last_node = cond_id
                if_id = cond_id
            elif line.upper().startswith("SINO"):
                false_id = self._next_node_id()
                mermaid_lines.append(f'    {false_id}["Rama SINO"]')
                mermaid_lines.append(f"    {if_id} -- No --> {false_id}")
                last_node = false_id
            elif line.upper().startswith("FIN_SI"):
                continue
            elif line.upper().startswith("PARA "):
                loop_id = self._next_node_id()
                mermaid_lines.append(f'    {loop_id}{{{{"PARA {line[4:].strip()}"}}}}')
                mermaid_lines.append(f"    {last_node} --> {loop_id}")
                last_node = loop_id
            elif line.upper().startswith("FIN_PARA"):
                continue
            elif line.upper().startswith("MIENTRAS "):
                loop_id = self._next_node_id()
                mermaid_lines.append(
                    f'    {loop_id}{{{{"MIENTRAS {line[9:].strip()}"}}}}'
                )
                mermaid_lines.append(f"    {last_node} --> {loop_id}")
                last_node = loop_id
            elif line.upper().startswith("FIN_MIENTRAS"):
                continue
            else:
                node_id = self._next_node_id()
                texto = line.replace('"', "'")
                mermaid_lines.append(f'    {node_id}["{texto}"]')
                if (
                    line.upper().startswith("SINO") is False
                    and if_id
                    and last_node == if_id
                ):
                    mermaid_lines.append(f"    {last_node} -- Sí --> {node_id}")
                else:
                    mermaid_lines.append(f"    {last_node} --> {node_id}")
                last_node = node_id

        end_id = self._next_node_id()
        mermaid_lines.append(f"    {end_id}([Fin])")
        mermaid_lines.append(f"    {last_node} --> {end_id}")

        return "\n".join(mermaid_lines)

    def python_to_pseudocode(self, code_source: str) -> str:
        """Traduce una función Python simple a pseudocódigo UCEMICH."""
        try:
            tree = ast.parse(code_source)
        except SyntaxError as e:
            return f"# Error al parsear código: {e}"

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_node = node
                break

        if not func_node:
            return "# No se encontró una definición de función (def) para traducir."

        params = ", ".join(arg.arg for arg in func_node.args.args)
        lines = [f"FUNCIÓN {func_node.name}({params})"]
        lines.extend(self._body_to_pseudocode(func_node.body, indent=1))
        lines.append("FIN_FUNCIÓN")
        return "\n".join(lines)

    def _body_to_pseudocode(self, statements, indent: int) -> list[str]:
        """Traduce recursivamente una lista de sentencias AST a líneas de pseudocódigo UCEMICH."""
        pad = "    " * indent
        lines: list[str] = []
        for stmt in statements:
            if isinstance(stmt, ast.Assign):
                targets = [ast.unparse(t) for t in stmt.targets]
                value = ast.unparse(stmt.value)
                lines.append(f"{pad}{', '.join(targets)} <- {value}")
            elif isinstance(stmt, ast.If):
                cond = ast.unparse(stmt.test)
                lines.append(f"{pad}SI {cond} ENTONCES")
                lines.extend(self._body_to_pseudocode(stmt.body, indent + 1))
                if stmt.orelse:
                    lines.append(f"{pad}SINO")
                    lines.extend(self._body_to_pseudocode(stmt.orelse, indent + 1))
                lines.append(f"{pad}FIN_SI")
            elif isinstance(stmt, ast.For):
                target = ast.unparse(stmt.target)
                iter_expr = ast.unparse(stmt.iter)
                lines.append(f"{pad}PARA {target} EN {iter_expr} HACER")
                lines.extend(self._body_to_pseudocode(stmt.body, indent + 1))
                lines.append(f"{pad}FIN_PARA")
            elif isinstance(stmt, ast.While):
                cond = ast.unparse(stmt.test)
                lines.append(f"{pad}MIENTRAS {cond} HACER")
                lines.extend(self._body_to_pseudocode(stmt.body, indent + 1))
                lines.append(f"{pad}FIN_MIENTRAS")
            elif isinstance(stmt, ast.Return):
                valor = ast.unparse(stmt.value) if stmt.value is not None else ""
                lines.append(f"{pad}RETORNAR {valor}".rstrip())
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Name) and call.func.id == "print":
                    args = ", ".join(ast.unparse(a) for a in call.args)
                    lines.append(f"{pad}ESCRIBIR {args}")
        return lines

    def pseudocode_to_python_skeleton(self, pseudocode: str) -> str:
        """Genera un esqueleto Python (firma + docstring, sin cuerpo) a partir de
        un bloque FUNCIÓN...FIN_FUNCIÓN en pseudocódigo UCEMICH."""
        match = re.search(
            r"FUNCI[ÓO]N\s+(\w+)\s*\(([^)]*)\)", pseudocode, re.IGNORECASE
        )
        if not match:
            return "# No se encontró un bloque FUNCIÓN...FIN_FUNCIÓN para traducir."

        nombre = match.group(1)
        params_raw = [p.strip() for p in match.group(2).split(",") if p.strip()]
        params_firma = (
            ", ".join(f"{p}: float" for p in params_raw) if params_raw else ""
        )

        args_doc = "\n".join(f"        {p}: Descripción de {p}." for p in params_raw)
        if not args_doc:
            args_doc = "        (Sin parámetros)"

        skeleton = [
            f"def {nombre}({params_firma}) -> float:",
            '    """',
            f"    {nombre.replace('_', ' ').capitalize()}.",
            "",
            "    Args:",
            args_doc,
            "",
            "    Returns:",
            "        Resultado calculado por la función.",
            '    """',
            "    pass",
        ]
        return "\n".join(skeleton)
