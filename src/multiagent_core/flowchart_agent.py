"""
Agente Generador de Diagramas (FlowchartAgent) - Lógica de Programación UCEMICH 📊
=============================================================================

Genera de forma automática un diagrama de flujo en formato Mermaid a partir
de una función en Python usando el árbol de sintaxis abstracta (AST).
"""

import ast

from ._mermaid_utils import MermaidNodeCounter


class FlowchartAgent:
    """Agente que traduce código Python a sintaxis de diagramas de flujo Mermaid."""

    def __init__(self) -> None:
        self._node_counter = MermaidNodeCounter()

    def _next_node_id(self) -> str:
        return self._node_counter.next_id()

    def build_mermaid_flowchart(self, code_source: str) -> str:
        """Lee un código fuente en Python y genera la cadena del diagrama Mermaid."""
        try:
            tree = ast.parse(code_source)
        except Exception as e:
            return f"%% Error al parsear código: {e}\n"

        # Encontrar la primera función en el código
        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_node = node
                break

        if not func_node:
            return "%% No se encontró una definición de función (def) para diagramar.\n"

        self._node_counter.reset()
        mermaid_lines = ["graph TD", f"    start([Inicio: {func_node.name}])"]

        last_node = "start"

        # Procesar los nodos del cuerpo de la función
        mermaid_lines, _ = self._process_body(func_node.body, mermaid_lines, last_node)

        return "\n".join(mermaid_lines)

    def _process_body(
        self, statements, lines: list, last_node: str
    ) -> tuple[list, str]:
        """Procesa una secuencia de sentencias (body) recursivamente."""
        current_last = last_node

        for stmt in statements:
            if isinstance(stmt, ast.Assign):
                # Asignación de variable
                node_id = self._next_node_id()
                # Obtener nombre de variable asignada
                targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
                targets_str = ", ".join(targets) if targets else "var"
                lines.append(f'    {node_id}["Asignar: {targets_str}"]')
                lines.append(f"    {current_last} --> {node_id}")
                current_last = node_id

            elif isinstance(stmt, ast.If):
                # Estructura condicional (Si - Entonces)
                cond_id = self._next_node_id()
                # Simplificar texto de la condición
                cond_text = "Condición"
                lines.append(f'    {cond_id}{{{{"{cond_text}?"}}}}')
                lines.append(f"    {current_last} --> {cond_id}")

                # Procesar rama verdadera
                true_id = self._next_node_id()
                lines.append(f'    {true_id}["Rama Verdadero (Si)"]')
                lines.append(f"    {cond_id} -- Sí --> {true_id}")
                lines, last_true = self._process_body(stmt.body, lines, true_id)

                # Procesar rama falsa (si existe)
                if stmt.orelse:
                    false_id = self._next_node_id()
                    lines.append(f'    {false_id}["Rama Falso (Sino)"]')
                    lines.append(f"    {cond_id} -- No --> {false_id}")
                    lines, last_false = self._process_body(stmt.orelse, lines, false_id)

                    # Unir ambas ramas
                    join_id = self._next_node_id()
                    lines.append(f'    {join_id}["Unión Condicional"]')
                    lines.append(f"    {last_true} --> {join_id}")
                    lines.append(f"    {last_false} --> {join_id}")
                    current_last = join_id
                else:
                    # Si no hay rama falsa, la condición va directo al final de la rama verdadera
                    join_id = self._next_node_id()
                    lines.append(f'    {join_id}["Unión Condicional"]')
                    lines.append(f"    {cond_id} -- No --> {join_id}")
                    lines.append(f"    {last_true} --> {join_id}")
                    current_last = join_id

            elif isinstance(stmt, ast.While) or isinstance(stmt, ast.For):
                # Estructura de Ciclo (Mientras / Para)
                loop_cond_id = self._next_node_id()
                loop_type = "Mientras" if isinstance(stmt, ast.While) else "Para"
                lines.append(f'    {loop_cond_id}{{{{"{loop_type} Iterar?"}}}}')
                lines.append(f"    {current_last} --> {loop_cond_id}")

                body_start_id = self._next_node_id()
                lines.append(f'    {body_start_id}["Cuerpo del Bucle"]')
                lines.append(f"    {loop_cond_id} -- Sí --> {body_start_id}")

                lines, last_body_node = self._process_body(
                    stmt.body, lines, body_start_id
                )
                # Volver a la condición del bucle (bucle cerrado)
                lines.append(f"    {last_body_node} --> {loop_cond_id}")

                # Nodo de salida del bucle
                exit_id = self._next_node_id()
                lines.append(f'    {exit_id}["Salir Bucle"]')
                lines.append(f"    {loop_cond_id} -- No --> {exit_id}")
                current_last = exit_id

            elif isinstance(stmt, ast.Return):
                # Retorno de función
                node_id = self._next_node_id()
                lines.append(f"    {node_id}([Fin / Retorno])")
                lines.append(f"    {current_last} --> {node_id}")
                current_last = node_id

        return lines, current_last


if __name__ == "__main__":
    # Prueba local del Agente
    example_code = """
def evaluar_temperatura(temp):
    if temp > 100:
        estado = "Gaseoso"
    else:
        estado = "Líquido"
    return estado
"""
    agent = FlowchartAgent()
    print("=== PROBANDO GENERADOR DE MERMAID ===")
    print(agent.build_mermaid_flowchart(example_code))
