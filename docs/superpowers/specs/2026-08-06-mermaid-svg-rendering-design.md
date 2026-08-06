# Renderizado SVG estático de diagramas Mermaid — Diseño

## Contexto y problema

Los notebooks del curso contienen diagramas Mermaid en dos formas:

1. **13 diagramas manuales**, escritos directamente como bloques ` ```mermaid ` en 6 de los 9 `UNIDAD_*.md` (U1, U2, U4, U5, U6, U8).
2. **35 diagramas autogenerados**, producidos por `FlowchartAgent.build_mermaid_flowchart()` a partir del AST de cualquier función de ejemplo con más de 5 líneas, e inyectados por `NotebookCompilerAgent.compile()` (`notebook_compiler_agent.py:191-201`) en cada corrida de `convert_to_notebooks_smart.py`.

Google Colab no renderiza nativamente bloques ` ```mermaid ` en celdas markdown — los muestra como texto de código sin interpretar. VS Code sí los renderiza (vía extensión de Markdown Preview), lo que hizo el problema invisible hasta verificar los notebooks publicados en GitHub/Colab.

Durante la investigación de los 13 diagramas manuales se encontraron además **2 errores reales de sintaxis Mermaid** en el contenido fuente (paréntesis sin escapar en etiquetas de nodo), que rompían el renderizado incluso en VS Code. Ya corregidos en `UNIDAD_4_ESTRUCTURAS_DECISION.md` y `UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md` como parte de esta investigación.

## Objetivo

Reemplazar los bloques de texto ` ```mermaid ` por imágenes SVG pre-renderizadas embebidas, para que los diagramas se vean idénticos en VS Code, GitHub y Colab, sin depender de JavaScript en tiempo de ejecución ni de que el visor soporte Mermaid nativamente.

## Arquitectura

### Componente nuevo: `MermaidRenderer`

`src/multiagent_core/mermaid_renderer.py` — clase con responsabilidad única: texto Mermaid → archivo SVG en disco, con caché.

```python
class MermaidRenderer:
    def __init__(self, output_dir: Path) -> None: ...
    def render(self, mermaid_source: str) -> Path: ...
```

- `render()` calcula `hashlib.sha256(mermaid_source.encode()).hexdigest()[:16]` y comprueba si `<output_dir>/<hash>.svg` ya existe. Si existe, lo retorna sin invocar nada (caché).
- Si no existe: escribe `mermaid_source` a un archivo temporal (`tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False, encoding="utf-8")`), invoca `mmdc` sobre ese archivo, y borra el temporal en un bloque `finally` (se ejecuta tanto si `mmdc` tuvo éxito como si falló, para no dejar basura en fallos repetidos).
- En `__init__`, verifica disponibilidad de Node con `shutil.which("npx")` y guarda la ruta resuelta completa (`self._npx_path`), no solo el literal `"npx"`. **En Windows, `npx` es en realidad `npx.cmd`**, y `subprocess.run(["npx", ...])` sin `shell=True` puede no resolverlo correctamente dependiendo de cómo Python arme el `PATH` interno — `shutil.which("npx")` sí lo resuelve a la ruta absoluta real (p. ej. `C:\...\npx.cmd`), y pasar esa ruta absoluta a `subprocess.run` evita el problema sin necesitar `shell=True` (que introduciría riesgo de inyección si el texto Mermaid llegara a interpolarse en el comando, cosa que no debe pasar — el texto Mermaid va al archivo temporal, nunca a un string de shell). Si `shutil.which("npx")` devuelve `None`, lanza `RuntimeError` (ver sección "Verificación de Node").
- **Reintento ante fallo de `mmdc`**: durante la validación manual, 2 de 13 invocaciones fallaron por un lanzamiento fallido de Chromium/Puppeteer (no por error de sintaxis Mermaid) — un fallo intermitente observado, no hipotético. `render()` reintenta una vez automáticamente si `subprocess.run` retorna código de salida distinto de cero, antes de propagar la excepción. Un segundo fallo consecutivo sí se propaga como `RuntimeError` con el `stderr` de `mmdc` incluido (para distinguir un fallo de infraestructura de un error real de sintaxis Mermaid, como los 2 encontrados en U4/U5).
- `output_dir` es inyectable en el constructor (mismo patrón que `chroma_path`/`memory_path` en `TutorAgent` — permite aislar tests con `tmp_path`, sin rutas hardcodeadas).
- Truncar el hash a 16 caracteres es suficiente para evitar colisiones en un corpus de ~50 diagramas; mantiene los nombres de archivo legibles.

### Integración en `NotebookCompilerAgent` (diagramas autogenerados)

En `notebook_compiler_agent.py:191-201`, donde hoy se construye el markdown con el bloque de texto:

```python
if "def " in code_content and len(code_lines) > 5:
    mermaid_flow = self.flowchart_agent.build_mermaid_flowchart(code_content)
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

`NotebookCompilerAgent` recibe una instancia de `MermaidRenderer` inyectada en su constructor (apuntando a `<repo_root>/notebooks/assets/diagramas/`), siguiendo el mismo patrón de dependencias explícitas que ya usa con `FlowchartAgent` y `MathAgent`.

La ruta en el `<img>` es **relativa** (`assets/diagramas/<hash>.svg`) porque el `.ipynb` vive en `notebooks/`, al mismo nivel que `notebooks/assets/`.

### Los 13 diagramas manuales (en los `.md`)

Mismo patrón de imagen + `<details>`, aplicado directamente al texto de los 6 `UNIDAD_*.md`, con una diferencia: la ruta usa la **URL absoluta** `https://raw.githubusercontent.com/Multiagent-AI-Lab/Programming-Logic-Agentic-AI-Development/master/notebooks/assets/diagramas/<hash>.svg`, porque el `.md` vive en la raíz del repo, un nivel de directorio distinto al `.ipynb` — una ruta relativa no puede servir a ambos contextos simultáneamente.

Estos 13 SVG ya fueron generados y verificados manualmente durante la investigación (con `npx @mermaid-js/mermaid-cli`, fondo transparente) y están en `notebooks/assets/diagramas/` con nombres descriptivos (`u1_pensamiento_computacional_cli_diagrama_1.svg`, etc.) en vez de hash — **se regenerarán con `-b white` y nombre por hash** para quedar consistentes con el mecanismo del `MermaidRenderer`, usando el mismo script de reemplazo ya escrito (`replace_mermaid.py` en el scratchpad de la sesión) adaptado a la nueva convención de nombres.

### Verificación de Node

Al inicio de `convert_to_notebooks_smart.py`, antes de procesar cualquier unidad:

```python
import shutil

if shutil.which("npx") is None:
    print("ERROR: Node.js no está instalado o 'npx' no está en el PATH.")
    print("Los diagramas Mermaid requieren Node.js para renderizarse como SVG.")
    print("Instalar con: winget install OpenJS.NodeJS (Windows) o desde https://nodejs.org")
    sys.exit(1)
```

Falla rápido con instrucciones claras, en vez de abortar a mitad de la compilación de la unidad 5 de 9. Documentado como prerequisito en `README.md` junto a la sección de configuración del entorno conda (Node.js no es un paquete Python, no puede ir en `requirements.txt`/`environment.yml`).

### Aprovechamiento: validación de sintaxis en `ContentAuditorAgent`

`ContentAuditorAgent._audit_pedagogico()` (`content_auditor_agent.py`) ya inspecciona los bloques Mermaid de cada unidad para verificar el ciclo "Hilo de Oro". Los 2 errores reales de sintaxis Mermaid encontrados en U4/U5 durante esta investigación (paréntesis sin escapar) solo se detectaron por revisión visual manual — `mmdc` los habría rechazado con un error de parseo claro (`Parse error on line N`, como efectivamente ocurrió al intentar renderizarlos).

Se añade una nueva dimensión de auditoría: por cada bloque ` ```mermaid ` extraído, `ContentAuditorAgent` invoca `MermaidRenderer.render()` dentro de un `try/except`. Si `mmdc` retorna un error de parseo (no un fallo de infraestructura tipo timeout de Chromium — distinguible por el mensaje de `stderr`, que en un error de sintaxis contiene `"Parse error"`), se agrega un hallazgo: `"Diagrama Mermaid con error de sintaxis: <resumen del error>"`. Esto convierte una clase de defecto que hoy solo se detecta manualmente en una verificación automática que corre en cada regeneración del reporte de auditoría.

Nota de alcance: esto reusa `MermaidRenderer` como dependencia de `ContentAuditorAgent` (inyectada en el constructor, mismo patrón que `programa_path`), no duplica lógica de invocación de `mmdc`.

### Caché y control de versiones

- `notebooks/assets/diagramas/*.svg` se comitea a git — sin esto, las URLs de `raw.githubusercontent.com` usadas en los `.md` devolverían 404. Son archivos pequeños (10-100 KB observado en las pruebas).
- El caché por hash de contenido significa que una corrida incremental (un solo `.md` modificado) solo re-renderiza los diagramas cuyo texto Mermaid cambió; el resto reusa el SVG existente sin invocar `mermaid-cli`.
- SVG huérfanos (de un diagrama cuyo código fuente cambió, dejando el hash viejo sin referencias) se toleran sin limpieza automática en esta iteración — son archivos pequeños; una limpieza posterior es un problema separado y menor, fuera de alcance aquí.

## Testing

- **`test_mermaid_renderer.py`** (nuevo): caché hit (segunda llamada con el mismo texto no invoca `subprocess`, mockeado), caché miss (invoca `subprocess.run` con la ruta absoluta resuelta de `npx` y los argumentos esperados), el archivo temporal `.mmd` se crea y se borra tanto en éxito como en fallo (verificado con `tmp_path` + espiar la llamada a borrado), reintento automático (`subprocess.run` mockeado para fallar una vez y luego tener éxito → `render()` retorna sin error), fallo tras 2 intentos consecutivos propaga `RuntimeError` con el `stderr` original, error claro cuando `shutil.which` retorna `None`. Sin depender de Node real — todo mockeado, para no romper CI/máquinas sin Node instalado.
- **`test_notebook_compiler_agent.py`**: actualizar `test_notebook_generado_incluye_diagrama_mermaid_autogenerado` (línea 85) — el assert `any("```mermaid" in c.source ...)` ya no aplica tal cual, pasa a verificar `any("<img" in c.source and "<details>" in c.source ...)`. Este test recibe un `MermaidRenderer` con `subprocess` mockeado (fixture), no invoca Node real.
- Test de integración liviano confirmando que la ruta relativa generada (`assets/diagramas/<hash>.svg`) es correcta dado un texto Mermaid de ejemplo.
- **`test_content_auditor_agent.py`**: nuevo caso — un bloque Mermaid con sintaxis inválida (reproduciendo el patrón real encontrado en U4: `[texto(con paréntesis sin comillas)]`) produce un hallazgo de "error de sintaxis"; un bloque válido no lo produce. `MermaidRenderer` mockeado para simular ambos casos (`stderr` con `"Parse error"` vs. éxito), sin invocar Node real.

## Fuera de alcance

- No se construye un mecanismo de limpieza automática (`--prune`) de SVG huérfanos en esta iteración.
- No se agrega CI/pipeline de publicación — el renderizado ocurre en la máquina de quien ejecuta `convert_to_notebooks_smart.py` (hoy, manualmente).
- No se cambia el comportamiento para otros lenguajes de bloque de código (pytest, pseudocódigo, etc.) — solo Mermaid.
- La distinción entre "error de sintaxis Mermaid" y "fallo de infraestructura de mmdc" en `ContentAuditorAgent` se basa en buscar `"Parse error"` en el `stderr` — una heurística de texto, no un parseo estructurado del error. Suficiente para el caso observado; no se construye un parser robusto de la salida de `mmdc`.
