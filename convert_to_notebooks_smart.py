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
        print(
            "Instalar con: winget install OpenJS.NodeJS (Windows) o desde https://nodejs.org"
        )
        sys.exit(1)

    BASE_DIR = Path(__file__).parent
    SOURCE_DIR = BASE_DIR / "lecciones"
    output_dir = BASE_DIR / "notebooks"
    output_dir.mkdir(exist_ok=True)

    files_to_convert = [
        "UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md",
        "UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md",
        "UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md",
        "UNIDAD_3_VARIABLES_OPERADORES.md",
        "UNIDAD_4_ESTRUCTURAS_DECISION.md",
        "UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md",
        "UNIDAD_6_MODULARIDAD_IA_MCP.md",
        "UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.md",
        "UNIDAD_8_PROYECTO_INTEGRADOR.md",
        "EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md",
        "EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.md",
        "EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.md",
    ]

    print("=" * 75)
    print("INICIANDO CONVERSOR MULTIAGENTE PEDAGÓGICO V3")
    print("=" * 75)
    print(f"Directorio Base: {BASE_DIR}")
    print(f"Directorio de Salida: {output_dir}\n")

    # Instanciar el agente compilador del consejo
    compiler = NotebookCompilerAgent()

    converted = 0
    missing = []

    for filename in files_to_convert:
        filepath = SOURCE_DIR / filename
        if not filepath.exists():
            missing.append(filename)
            continue

        try:
            compiler.compile(filepath, output_dir)
            converted += 1
        except Exception as e:
            print(f"  [ERROR] Error al compilar {filename}: {e}")

    print("\n" + "=" * 75)
    print("RESUMEN DE EJECUCION")
    print("=" * 75)
    print(f"  [OK] Convertidos con exito: {converted}")
    if missing:
        print(
            f"  [PENDIENTE] Archivos Markdown no encontrados aun (pendientes de creacion): {len(missing)}"
        )
        for f in missing:
            print(f"  - {f}")
    print("=" * 75)

    if missing or converted < len(files_to_convert):
        sys.exit(1)
