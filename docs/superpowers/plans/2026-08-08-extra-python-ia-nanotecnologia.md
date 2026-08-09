# EXTRA_PYTHON_IA_NANOTECNOLOGIA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Producir 3 archivos Markdown fuente (Parte 1: Fundamentos, Parte 2: Datos y Archivos, Parte 3: Paquetes y APIs) que adaptan el curso público "AI Python for Beginners" al contexto del curso UCEMICH — nanotecnología, español, Gemini — y sus 3 notebooks generados, como pieza complementaria opcional fuera de la secuencia U0-U8.

**Architecture:** Cada parte es un `.md` autocontenido en el mismo formato que las 9 unidades existentes (badge de Colab, celda de setup con clonado de repo, fences ` ```python ` con código comentado), integrado al pipeline `convert_to_notebooks_smart.py` → `NotebookCompilerAgent` → `notebooks/*.ipynb` sin modificar ningún agente existente. Datos de apoyo (bitácoras de laboratorio, CSV de experimentos) viven en `data/bitacoras_laboratorio/`.

**Tech Stack:** Markdown, Python 3.11, `google.genai` (Gemini), `requests`, `beautifulsoup4`, `pandas`, `matplotlib`, mismo pipeline de conversión ya existente (`NotebookCompilerAgent`, `MermaidRenderer` para cualquier diagrama que se agregue).

## Global Constraints

- Todos los ejemplos de código usan contexto de nanotecnología (nanopartículas de oro/plata/TiO2, bitácoras de síntesis, propiedades de materiales) — cero ejemplos genéricos/turísticos/de clima.
- `get_llm_response(prompt: str) -> str` se define en la PRIMERA celda de código de CADA una de las 3 partes (no se importa de un archivo `helper_functions.py` externo), usando `genai.Client(api_key=os.environ["GEMINI_API_KEY"])` — mismo patrón que `src/multiagent_core/tutor_agent.py:ask()`.
- Cada parte es autocontenida: no depende de que el alumno haya ejecutado una parte anterior en la misma sesión de Colab.
- Cada parte lleva su propio badge "Open in Colab" y su propia celda de setup con clonado de repo — mismo patrón exacto que las 9 `UNIDAD_*.md` (`if 'google.colab' in sys.modules: ... git clone ... os.chdir(repo_dir)`).
- La celda de API key usa el mismo patrón de doble-nombre-de-secreto ya usado en `UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md` (prueba `GEMINI_API_KEY`, luego `GOOGLE_API_KEY`).
- Todo bloque de código con función propia lleva docstring estilo Google y type hints — misma convención que el resto del proyecto.
- No se modifica `NotebookCompilerAgent`, `FlowchartAgent`, `MermaidRenderer`, ni ningún agente existente.
- No se modifica ninguna `UNIDAD_*.md` ni `RUBRICA_GENERAL.md`.
- Tras escribir cada `.md`, se regeneran los notebooks (`python convert_to_notebooks_smart.py`) y se corre la suite completa (`pytest tests/ -v --tb=short`) para confirmar que nada existente se rompió.

---

### Task 1: Datos de apoyo — bitácoras de laboratorio y CSV de experimentos

**Files:**
- Create: `data/bitacoras_laboratorio/sintesis_au_np.txt`
- Create: `data/bitacoras_laboratorio/sintesis_ag_np.txt`
- Create: `data/bitacoras_laboratorio/sintesis_tio2_np.txt`
- Create: `data/bitacoras_laboratorio/reunion_comite.txt`
- Create: `data/bitacoras_laboratorio/orden_reactivos.txt`
- Create: `data/bitacoras_laboratorio/experimentos_verano_2026.csv`
- Create: `data/bitacoras_laboratorio/README.md`

**Interfaces:**
- Produces: 5 archivos `.txt` de bitácoras (3 relevantes a síntesis, 2 no relevantes — para el ejercicio de clasificación de la Parte 1 sección 3), 1 archivo `.csv` de experimentos (para Parte 3, sección de pandas/matplotlib), usados como rutas relativas `data/bitacoras_laboratorio/<archivo>` desde los 3 `.md`.

- [ ] **Step 1: Crear las 3 bitácoras relevantes (síntesis de nanopartículas)**

`data/bitacoras_laboratorio/sintesis_au_np.txt`:
```
Bitácora de síntesis — Nanopartículas de oro (Au)
Fecha: 14 de marzo de 2026
Investigador: L. Ramírez

Se preparó una solución de HAuCl4 0.01% (25 mL) y se calentó a ebullición
bajo agitación constante. Al alcanzar el punto de ebullición, se añadió
citrato de sodio al 1% (2.5 mL) de forma rápida, observándose un cambio
de color de amarillo pálido a azul oscuro y finalmente a rojo rubí en un
lapso de 8 minutos, confirmando la formación de nanopartículas esféricas.

El reactivo límite fue el citrato de sodio, dado que se usó en proporción
estequiométrica menor respecto al HAuCl4. Rendimiento estimado: 87%.
Diámetro promedio determinado por DLS: 15.3 nm, con índice de
polidispersidad de 0.18.

Observación adicional: la solución permaneció estable (sin agregación
visible) durante al menos 72 horas de almacenamiento a 4°C.
```

`data/bitacoras_laboratorio/sintesis_ag_np.txt`:
```
Bitácora de síntesis — Nanopartículas de plata (Ag)
Fecha: 2 de abril de 2026
Investigador: J. Torres

Reducción de AgNO3 (0.001 M, 50 mL) con NaBH4 (0.002 M, 15 mL) en baño
de hielo, bajo agitación vigorosa durante 30 minutos. La adición lenta
del agente reductor fue crítica para evitar la agregación de partículas.

El NaBH4 actuó como reactivo límite. Rendimiento reportado: 92%.
El diámetro promedio de las nanopartículas, medido por TEM, fue de
8.7 nm, con morfología predominantemente esférica y baja dispersión
de tamaño.

La suspensión coloidal resultante presentó un color amarillo característico,
consistente con el plasmón de resonancia superficial esperado para
nanopartículas de plata de este tamaño.
```

`data/bitacoras_laboratorio/sintesis_tio2_np.txt`:
```
Bitácora de síntesis — Nanopartículas de TiO2
Fecha: 20 de abril de 2026
Investigador: M. Herrera

Síntesis por método sol-gel: hidrólisis controlada de isopropóxido de
titanio (TTIP) en etanol anhidro, con adición gota a gota de agua
desionizada bajo atmósfera de nitrógeno. El gel resultante se secó a
80°C durante 12 horas y se calcinó a 450°C por 3 horas para inducir la
fase cristalina anatasa.

El TTIP fue el reactivo límite. Rendimiento del proceso: 78%,
considerando pérdidas durante la etapa de calcinación.
Diámetro promedio de cristalita (Scherrer, XRD): 22.4 nm.

La fase anatasa fue confirmada por difracción de rayos X, sin señales
significativas de la fase rutilo.
```

- [ ] **Step 2: Crear las 2 bitácoras NO relevantes (para el ejercicio de clasificación)**

`data/bitacoras_laboratorio/reunion_comite.txt`:
```
Minuta de reunión — Comité de Seguridad del Laboratorio
Fecha: 10 de marzo de 2026

Asistentes: Dra. Ibarra (coordinadora), L. Ramírez, J. Torres, M. Herrera.

Se revisó el protocolo de disposición de residuos con nanopartículas
metálicas. Se acordó actualizar las hojas de seguridad (MSDS) del
citrato de sodio y del NaBH4 antes de fin de mes.

Se discutió el calendario de mantenimiento del equipo de DLS —
programado para la última semana de marzo, lo que implicará suspender
temporalmente las mediciones de tamaño de partícula.

Próxima reunión: 24 de marzo de 2026, 10:00 AM.
```

`data/bitacoras_laboratorio/orden_reactivos.txt`:
```
Orden de compra de reactivos — Laboratorio de Nanomateriales
Fecha: 5 de marzo de 2026

Proveedor: Distribuidora Química del Bajío
Solicitado por: M. Herrera

Artículos:
- HAuCl4 (ácido cloroáurico), 5 g — 2 unidades
- AgNO3 (nitrato de plata), 25 g — 1 unidad
- Isopropóxido de titanio (TTIP), 500 mL — 1 unidad
- Citrato de sodio dihidratado, 100 g — 3 unidades
- Guantes de nitrilo, talla M, caja de 100 — 5 cajas

Fecha estimada de entrega: 15 días hábiles.
Presupuesto autorizado: $18,450 MXN.
```

- [ ] **Step 3: Crear el CSV de experimentos**

`data/bitacoras_laboratorio/experimentos_verano_2026.csv`:
```
fecha,material,diametro_nm,rendimiento_pct,metodo
2026-03-14,Au,15.3,87,reduccion_citrato
2026-04-02,Ag,8.7,92,reduccion_borohidruro
2026-04-20,TiO2,22.4,78,sol_gel
2026-05-05,Au,12.1,90,reduccion_citrato
2026-05-12,Ag,9.4,88,reduccion_borohidruro
2026-05-19,TiO2,19.8,81,sol_gel
2026-05-26,Au,17.6,84,reduccion_citrato
2026-06-02,Ag,7.9,95,reduccion_borohidruro
```

- [ ] **Step 4: Crear el README del directorio**

`data/bitacoras_laboratorio/README.md`:
```markdown
# Bitácoras de Laboratorio (datos de ejemplo)

Datos ficticios de síntesis de nanopartículas, usados en
`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md`,
`_PARTE2_DATOS_Y_ARCHIVOS.md` y `_PARTE3_PAQUETES_Y_APIS.md` para
ejercicios de lectura de archivos, clasificación y extracción de
información con LLM.

- `sintesis_au_np.txt`, `sintesis_ag_np.txt`, `sintesis_tio2_np.txt`:
  bitácoras relevantes (describen procedimientos de síntesis).
- `reunion_comite.txt`, `orden_reactivos.txt`: bitácoras NO relevantes
  (administrativas), usadas para el ejercicio de clasificación por
  relevancia.
- `experimentos_verano_2026.csv`: dataset tabular de experimentos,
  usado con `pandas`/`matplotlib` en la Parte 3.

Todos los datos son ficticios, generados para fines pedagógicos.
```

- [ ] **Step 5: Commit**

```bash
git add data/bitacoras_laboratorio/
git commit -m "feat: agregar datos de apoyo (bitácoras de laboratorio) para EXTRA_PYTHON_IA_NANOTECNOLOGIA"
```

---

### Task 2: Parte 1 — Fundamentos (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md`)

**Files:**
- Create: `EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md`
- Modify: `convert_to_notebooks_smart.py:29-39` (agregar a `files_to_convert`)

**Interfaces:**
- Consumes: `data/bitacoras_laboratorio/{sintesis_au_np,sintesis_ag_np,sintesis_tio2_np,reunion_comite,orden_reactivos}.txt` de Task 1.
- Produces: notebook `notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.ipynb`, y la función `get_llm_response(prompt: str) -> str` documentada aquí (Parte 2 y 3 la redefinen igual, no la importan de aquí).

- [ ] **Step 1: Escribir el encabezado, badge de Colab y celda de setup**

Contenido inicial de `EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md`:

````markdown
# EXTRA: Python + IA aplicado a Nanotecnología — Parte 1: Fundamentos

Material complementario y opcional, fuera de la secuencia de las 9 unidades del curso.
Refuerza el patrón **Python como orquestador de llamadas a un LLM** — prompts como
f-strings, iterar con `for` preguntando a un LLM, extraer datos estructurados — a
través de ejemplos de síntesis y caracterización de nanopartículas.

Adaptado del curso público ["AI Python for Beginners"](https://www.deeplearning.ai/courses/ai-python-for-beginners)
de DeepLearning.AI, con ejemplos reescritos para nanotecnología y usando Gemini en
vez de OpenAI.

**Contenido de esta parte:** tipos de datos, f-strings, listas y comprehensions,
`enumerate`/`zip`, diccionarios, tuplas y sets, comparaciones lógicas — todo con el
patrón Python+LLM como hilo conductor.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Multiagent-AI-Lab/Programming-Logic-Agentic-AI-Development/blob/master/notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.ipynb)

```python
import os
import sys

if 'google.colab' in sys.modules:
    repo_dir = "Programming-Logic-Agentic-AI-Development"
    if not os.path.exists(repo_dir):
        !git clone -q https://github.com/Multiagent-AI-Lab/{repo_dir}.git
    os.chdir(repo_dir)
    %pip install -q google-genai
```

---

## 1. Tu primera función para hablar con un LLM

Vas a definir una función que envía una instrucción (prompt) a Gemini y retorna su
respuesta como texto. La usarás en cada sección de esta pieza.

```python
import os
import sys
from google import genai

if 'google.colab' in sys.modules:
    from google.colab import userdata
    for nombre_secreto in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        try:
            os.environ["GEMINI_API_KEY"] = userdata.get(nombre_secreto)
            break
        except Exception:
            continue
    else:
        print(
            "⚠️ No se encontró el secreto GEMINI_API_KEY ni GOOGLE_API_KEY en Colab. "
            "Créalo en el ícono de llave 🔑 de la barra lateral izquierda."
        )


def get_llm_response(prompt: str) -> str:
    """Envía un prompt a Gemini y retorna el texto de la respuesta.

    Args:
        prompt: Instrucción completa a enviar al modelo.

    Returns:
        Texto de la respuesta del modelo.
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text
```

Pruébala:

```python
respuesta = get_llm_response("Explica en una oración qué es una nanopartícula.")
print(respuesta)
```
````

- [ ] **Step 2: Escribir la sección de tipos de datos + f-strings (secciones 1-2 del mapa temático)**

Agregar después de la sección 1:

````markdown
## 2. Tipos de datos: caracterizando una síntesis

```python
material = "oro"
diametro_nm = 15.3
es_esferica = True

print(type(material))
print(type(diametro_nm))
print(type(es_esferica))
```

`str` para texto, `float` para números decimales, `bool` para verdadero/falso.

### F-strings: construir prompts con datos reales

En vez de escribir el prompt a mano, puedes interpolar variables directamente:

```python
material = "oro"
diametro_nm = 15.3

prompt = f"¿Qué aplicaciones tiene una nanopartícula de {material} de {diametro_nm} nm de diámetro?"
print(prompt)
```

También puedes controlar el formato numérico — por ejemplo, mostrar solo 2 decimales:

```python
diametro_nm = 15.34782
print(f"Diámetro promedio: {diametro_nm:.2f} nm")
```

**Ejercicio:** define `rendimiento_pct = 87.456` y construye un f-string que reporte
"Rendimiento: 87.46%" (2 decimales).

📖 [Cadenas en Python](https://ellibrodepython.com/cadenas-python) · [Nombrando variables](https://ellibrodepython.com/nombrando-variables-python)
````

- [ ] **Step 3: Escribir la sección de listas + IA (sección 3 del mapa temático)**

Agregar después de la sección 2 — este es el ejemplo ya esbozado y aprobado en el diseño:

````markdown
## 3. Automatizando tareas con listas + IA

Cinco bitácoras de laboratorio conviven en la carpeta `data/bitacoras_laboratorio/` —
algunas describen síntesis de nanopartículas, otras son notas administrativas.
Revisarlas a mano es lento; vas a automatizarlo.

```python
bitacoras = [
    "sintesis_au_np.txt", "sintesis_ag_np.txt", "sintesis_tio2_np.txt",
    "reunion_comite.txt", "orden_reactivos.txt",
]

for archivo in bitacoras:
    with open(f"data/bitacoras_laboratorio/{archivo}", encoding="utf-8") as f:
        contenido = f.read()

    prompt = f"""Responde solo "Relevante" o "No relevante":
la bitácora describe un procedimiento de síntesis de nanopartículas.

Bitácora:
{contenido}"""

    print(f"{archivo} -> {get_llm_response(prompt)}")
```

**Ejercicio:** cambia el criterio del prompt para clasificar por otra propiedad
(por ejemplo, "menciona un rendimiento por encima del 85%"). ¿Cambia el resultado?

📖 [Bucle for en Python](https://ellibrodepython.com/for-python)
````

- [ ] **Step 4: Escribir la sección de list comprehensions (sección 4)**

````markdown
## 4. List comprehensions: filtrar de forma concisa

El `for` de la sección anterior también se puede escribir en una sola línea cuando
solo necesitas construir una lista nueva a partir de otra:

```python
rendimientos = [87, 92, 78, 90, 88, 81, 84, 95]

altos = [r for r in rendimientos if r >= 88]
print(altos)
```

Equivale a:

```python
altos = []
for r in rendimientos:
    if r >= 88:
        altos.append(r)
print(altos)
```

**Ejercicio:** usando `rendimientos`, construye con comprehension una lista con la
diferencia de cada valor respecto al promedio (`sum(rendimientos) / len(rendimientos)`).

📖 [List comprehensions](https://ellibrodepython.com/list-comprehension)
````

- [ ] **Step 5: Escribir la sección de enumerate/zip (sección 5)**

````markdown
## 5. `enumerate` y `zip`: recorrer listas paralelas

```python
materiales = ["Au", "Ag", "TiO2"]
diametros_nm = [15.3, 8.7, 22.4]

for indice, material in enumerate(materiales):
    print(f"{indice}: {material}")
```

`zip` recorre dos listas a la vez, emparejando elementos por posición:

```python
for material, diametro in zip(materiales, diametros_nm):
    prompt = f"En una oración, ¿para qué se usa una nanopartícula de {material} de {diametro} nm?"
    print(f"{material}: {get_llm_response(prompt)}")
```

📖 [Iterar con zip](https://ellibrodepython.com/zip-python) · [Iterar con enumerate](https://ellibrodepython.com/enumerate-python)
````

- [ ] **Step 6: Escribir la sección de diccionarios + IA (sección 6)**

````markdown
## 6. Diccionarios para estructurar datos experimentales + IA

```python
experimento = {
    "material": "Au",
    "diametro_nm": 15.3,
    "rendimiento_pct": 87,
    "metodo": "reduccion_citrato",
}

prompt = f"""Con base en estos datos experimentales, sugiere UNA mejora al
procedimiento de síntesis:

Material: {experimento['material']}
Diámetro: {experimento['diametro_nm']} nm
Rendimiento: {experimento['rendimiento_pct']}%
Método: {experimento['metodo']}"""

print(get_llm_response(prompt))
```

**Ejercicio:** agrega una clave `"temperatura_C"` al diccionario `experimento` y
modifica el prompt para que la IA la tome en cuenta en su sugerencia.

📖 [Diccionario](https://ellibrodepython.com/diccionario-python)
````

- [ ] **Step 7: Escribir la sección de tuplas y sets (sección 7)**

````markdown
## 7. Tuplas y sets

Una tupla es como una lista, pero no se puede modificar después de creada — útil
para datos que no deben cambiar, como una coordenada atómica:

```python
posicion_atomo = (0.0, 0.0, 0.0)  # coordenadas x, y, z en Å
print(posicion_atomo[0])  # 0.0
```

Un set (conjunto) guarda valores únicos, sin orden ni repetidos:

```python
materiales_en_lote = ["Au", "Ag", "Au", "TiO2", "Ag", "Au"]
materiales_unicos = set(materiales_en_lote)
print(materiales_unicos)  # {'Au', 'Ag', 'TiO2'}
```

**Ejercicio:** dada la lista `metodos = ["reduccion_citrato", "sol_gel", "reduccion_citrato", "reduccion_borohidruro", "sol_gel"]`,
usa un set para obtener los métodos de síntesis distintos usados en el laboratorio.

📖 [Tupla o tuple](https://ellibrodepython.com/tupla-python) · [Set](https://ellibrodepython.com/set-python)
````

- [ ] **Step 8: Escribir la sección de comparaciones lógicas (sección 8) y el enlace a la Parte 2**

````markdown
## 8. Comparaciones lógicas y decisiones asistidas por IA

```python
diametro_nm = 15.3
rendimiento_pct = 87

if diametro_nm < 20 and rendimiento_pct >= 85:
    prompt = "Este lote de nanopartículas cumple los criterios de calidad. Sugiere el siguiente paso experimental."
else:
    prompt = "Este lote no cumple los criterios de calidad. Sugiere qué ajustar en el procedimiento."

print(get_llm_response(prompt))
```

📖 [Operadores lógicos](https://ellibrodepython.com/operadores-logicos-python) · [Operadores relacionales](https://ellibrodepython.com/operadores-relacionales-python)

---

**Continúa en la [Parte 2: Datos y Archivos →](EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.md)**
````

- [ ] **Step 9: Agregar el archivo a `convert_to_notebooks_smart.py`**

En `convert_to_notebooks_smart.py:29-39`, modificar `files_to_convert`:

```python
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
    ]
```

(Las Partes 2 y 3 se agregan en sus propias tareas — no las incluyas todavía.)

- [ ] **Step 10: Regenerar notebooks y verificar**

Run: `python convert_to_notebooks_smart.py`
Expected: `Convertidos con exito: 10` (las 9 unidades + esta parte nueva), sin errores.

- [ ] **Step 11: Correr la suite completa de tests**

Run: `pytest tests/ -v --tb=short`
Expected: PASS 100% — este cambio no toca ningún archivo de `src/` ni `tests/`, así que no debería alterar el resultado; se corre para confirmar que agregar el `.md` no rompió nada del pipeline.

- [ ] **Step 12: Commit**

```bash
git add EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md convert_to_notebooks_smart.py notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.ipynb
git commit -m "feat: agregar EXTRA_PYTHON_IA_NANOTECNOLOGIA Parte 1 (Fundamentos)"
```

---

### Task 3: Parte 2 — Datos y Archivos (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.md`)

**Files:**
- Create: `EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.md`
- Modify: `convert_to_notebooks_smart.py` (agregar a `files_to_convert`, después de la Parte 1)

**Interfaces:**
- Consumes: `data/bitacoras_laboratorio/sintesis_au_np.txt` de Task 1. Redefine `get_llm_response()` igual que la Parte 1 (no la importa) — ver Global Constraints.
- Produces: notebook `notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.ipynb`.

- [ ] **Step 1: Escribir el encabezado, badge de Colab, celda de setup y `get_llm_response` (idéntico patrón a la Parte 1)**

````markdown
# EXTRA: Python + IA aplicado a Nanotecnología — Parte 2: Datos y Archivos

Continuación de la [Parte 1: Fundamentos](EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md).
Esta parte es autocontenida — no necesitas haber ejecutado la Parte 1 en esta sesión.

**Contenido de esta parte:** manejo de excepciones, lectura de archivos de texto y
CSV, funciones propias, `*args`/`**kwargs`.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Multiagent-AI-Lab/Programming-Logic-Agentic-AI-Development/blob/master/notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.ipynb)

```python
import os
import sys

if 'google.colab' in sys.modules:
    repo_dir = "Programming-Logic-Agentic-AI-Development"
    if not os.path.exists(repo_dir):
        !git clone -q https://github.com/Multiagent-AI-Lab/{repo_dir}.git
    os.chdir(repo_dir)
    %pip install -q google-genai
```

```python
import os
import sys
from google import genai

if 'google.colab' in sys.modules:
    from google.colab import userdata
    for nombre_secreto in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        try:
            os.environ["GEMINI_API_KEY"] = userdata.get(nombre_secreto)
            break
        except Exception:
            continue
    else:
        print(
            "⚠️ No se encontró el secreto GEMINI_API_KEY ni GOOGLE_API_KEY en Colab. "
            "Créalo en el ícono de llave 🔑 de la barra lateral izquierda."
        )


def get_llm_response(prompt: str) -> str:
    """Envía un prompt a Gemini y retorna el texto de la respuesta.

    Args:
        prompt: Instrucción completa a enviar al modelo.

    Returns:
        Texto de la respuesta del modelo.
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text
```

---
````

- [ ] **Step 2: Escribir la sección de excepciones (sección 9)**

````markdown
## 9. Manejo de excepciones

Cuando llamas a un LLM, la petición puede fallar (sin conexión, respuesta
inesperada). Envolver la llamada en `try`/`except` evita que un solo fallo
detenga todo tu programa:

```python
def consultar_con_seguridad(prompt: str) -> str:
    """Consulta al LLM y retorna un mensaje de error controlado si falla.

    Args:
        prompt: Instrucción a enviar al modelo.

    Returns:
        La respuesta del modelo, o un mensaje de error si la consulta falla.
    """
    try:
        return get_llm_response(prompt)
    except Exception as e:
        return f"No se pudo obtener respuesta del modelo: {e}"


print(consultar_con_seguridad("Explica qué es la resonancia de plasmón superficial."))
```

Este es el mismo patrón que usa `TutorAgent.ask()` en el proyecto: nunca dejar que
un fallo de red interrumpa el flujo completo del programa.

**Ejercicio:** modifica `consultar_con_seguridad` para que, si `prompt` es una
cadena vacía, lance un `ValueError("El prompt no puede estar vacío")` antes de
llamar al LLM — y captúralo con otro `except`.

📖 [Excepciones en Python](https://ellibrodepython.com/excepciones-python)
````

- [ ] **Step 3: Escribir la sección de archivos + IA (sección 10) — ya esbozada y aprobada**

````markdown
## 10. Extraer datos estructurados de una bitácora

Vas a usar un LLM para extraer el reactivo límite y el rendimiento reportado de
una bitácora de texto libre, sin formato fijo — la clase de tarea que un `parser`
con expresiones regulares haría frágil, pero que un LLM maneja bien porque
entiende el lenguaje natural del texto.

```python
with open("data/bitacoras_laboratorio/sintesis_au_np.txt", encoding="utf-8") as f:
    bitacora = f.read()

prompt = f"""A partir de la siguiente bitácora de síntesis, extrae:
- Reactivo límite
- Rendimiento reportado (%)
- Diámetro promedio de nanopartícula (nm), si se menciona

Responde en formato JSON con esas tres claves.

Bitácora:
{bitacora}"""

resultado = get_llm_response(prompt)
print(resultado)
```

**Nota de auditoría:** un LLM puede alucinar un valor que no está en el texto.
Nunca uses la salida de este patrón directamente en un reporte de laboratorio sin
verificar contra la bitácora original — este es exactamente el rol de "Auditor de
Código" que la Unidad 0 (sección 0.5) espera de ti a partir de la Unidad 4.

📖 [Leer archivos](https://ellibrodepython.com/leer-archivos-python)
````

- [ ] **Step 4: Escribir la sección de funciones propias (sección 11)**

````markdown
## 11. Funciones propias reutilizables

```python
def diametro_a_area_superficial(diametro_nm: float) -> float:
    """Calcula el área superficial de una nanopartícula esférica.

    Args:
        diametro_nm: Diámetro de la nanopartícula, en nanómetros.

    Returns:
        Área superficial en nm², asumiendo geometría esférica perfecta.
    """
    radio_nm = diametro_nm / 2
    return 4 * 3.14159 * radio_nm ** 2


area = diametro_a_area_superficial(15.3)
print(f"Área superficial: {area:.2f} nm²")
```

**Ejercicio:** escribe una función `resumir_con_ia(diametro_nm)` que calcule el
área con la función anterior y le pida a `get_llm_response` que explique en una
oración por qué esa área es relevante para la reactividad química de la
nanopartícula.

📖 [Funciones en Python](https://ellibrodepython.com/funciones-en-python)
````

- [ ] **Step 5: Escribir la sección de `*args`/`**kwargs` (sección 12) y el enlace a la Parte 3**

````markdown
## 12. `*args` y `**kwargs`: prompts con número variable de datos

A veces no sabes de antemano cuántos parámetros experimentales vas a recibir.
`**kwargs` te deja pasar cualquier cantidad de argumentos con nombre:

```python
def construir_prompt_experimento(**kwargs) -> str:
    """Arma un prompt describiendo un experimento con un número variable de datos.

    Args:
        **kwargs: Pares clave-valor con los datos del experimento
            (ej. material="Au", diametro_nm=15.3).

    Returns:
        Prompt de texto listo para enviar a get_llm_response.
    """
    lineas = [f"{clave}: {valor}" for clave, valor in kwargs.items()]
    datos = "\n".join(lineas)
    return f"Con base en estos datos experimentales, da tu diagnóstico:\n{datos}"


prompt = construir_prompt_experimento(material="Ag", diametro_nm=8.7, rendimiento_pct=92)
print(get_llm_response(prompt))
```

**Ejercicio:** llama a `construir_prompt_experimento` con un dato experimental
distinto (ej. `temperatura_C=25, ph=7.2`) y confirma que la función lo maneja sin
modificar su código.

📖 [Uso de args y kwargs](https://ellibrodepython.com/args-kwargs-python)

---

**Continúa en la [Parte 3: Paquetes y APIs →](EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.md)**
````

- [ ] **Step 6: Agregar el archivo a `convert_to_notebooks_smart.py`**

Agregar `"EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.md"` a `files_to_convert`, después de la Parte 1.

- [ ] **Step 7: Regenerar notebooks y verificar**

Run: `python convert_to_notebooks_smart.py`
Expected: `Convertidos con exito: 11`.

- [ ] **Step 8: Correr la suite completa de tests**

Run: `pytest tests/ -v --tb=short`
Expected: PASS 100%.

- [ ] **Step 9: Commit**

```bash
git add EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.md convert_to_notebooks_smart.py notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.ipynb
git commit -m "feat: agregar EXTRA_PYTHON_IA_NANOTECNOLOGIA Parte 2 (Datos y Archivos)"
```

---

### Task 4: Parte 3 — Paquetes y APIs (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.md`)

**Files:**
- Create: `EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.md`
- Modify: `convert_to_notebooks_smart.py` (agregar a `files_to_convert`, después de la Parte 2)

**Interfaces:**
- Consumes: `data/bitacoras_laboratorio/experimentos_verano_2026.csv` de Task 1. Redefine `get_llm_response()` igual que las Partes 1-2.
- Produces: notebook `notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.ipynb`.

- [ ] **Step 1: Escribir el encabezado, badge de Colab, celda de setup y `get_llm_response`**

````markdown
# EXTRA: Python + IA aplicado a Nanotecnología — Parte 3: Paquetes y APIs

Continuación de la [Parte 2: Datos y Archivos](EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.md).
Esta parte es autocontenida — no necesitas haber ejecutado las partes anteriores en esta sesión.

**Contenido de esta parte:** paquetes built-in y de terceros, instalación con `pip`,
consumir una API REST real (PubChem), web scraping, y cómo funciona `genai.Client`
por dentro.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Multiagent-AI-Lab/Programming-Logic-Agentic-AI-Development/blob/master/notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.ipynb)

```python
import os
import sys

if 'google.colab' in sys.modules:
    repo_dir = "Programming-Logic-Agentic-AI-Development"
    if not os.path.exists(repo_dir):
        !git clone -q https://github.com/Multiagent-AI-Lab/{repo_dir}.git
    os.chdir(repo_dir)
    %pip install -q google-genai beautifulsoup4
```

```python
import os
import sys
from google import genai

if 'google.colab' in sys.modules:
    from google.colab import userdata
    for nombre_secreto in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        try:
            os.environ["GEMINI_API_KEY"] = userdata.get(nombre_secreto)
            break
        except Exception:
            continue
    else:
        print(
            "⚠️ No se encontró el secreto GEMINI_API_KEY ni GOOGLE_API_KEY en Colab. "
            "Créalo en el ícono de llave 🔑 de la barra lateral izquierda."
        )


def get_llm_response(prompt: str) -> str:
    """Envía un prompt a Gemini y retorna el texto de la respuesta.

    Args:
        prompt: Instrucción completa a enviar al modelo.

    Returns:
        Texto de la respuesta del modelo.
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text
```

---
````

- [ ] **Step 2: Escribir la sección de paquetes built-in y de terceros (sección 13)**

````markdown
## 13. Paquetes built-in y de terceros

`math`, `statistics` y `random` vienen incluidos con Python:

```python
import math
import statistics

diametro_nm = 15.3
radio_nm = diametro_nm / 2
volumen_nm3 = (4 / 3) * math.pi * radio_nm ** 3
print(f"Volumen: {volumen_nm3:.2f} nm³")

rendimientos = [87, 92, 78, 90, 88, 81, 84, 95]
print(f"Rendimiento promedio: {statistics.mean(rendimientos):.1f}%")
print(f"Desviación estándar: {statistics.stdev(rendimientos):.2f}")
```

`pandas` y `matplotlib` son paquetes de terceros — cargan datos tabulares y los
grafican:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/bitacoras_laboratorio/experimentos_verano_2026.csv")
print(df.head())
print(df.groupby("material")["diametro_nm"].mean())
```

```python
df.groupby("material")["rendimiento_pct"].mean().plot(kind="bar")
plt.ylabel("Rendimiento promedio (%)")
plt.title("Rendimiento de síntesis por material")
plt.show()
```

**Ejercicio:** usa `get_llm_response` para pedirle al LLM que interprete la
gráfica anterior en una oración, pasándole como contexto los valores numéricos
de `df.groupby("material")["rendimiento_pct"].mean()` convertidos a texto.

📖 [Colecciones](https://ellibrodepython.com/colecciones-python)
````

- [ ] **Step 3: Escribir la sección de instalación con pip (sección 14)**

````markdown
## 14. Instalación de paquetes con `pip`

Ya usaste `%pip install -q google-genai beautifulsoup4` en la celda de setup de
esta parte. Fuera de Colab (en tu máquina local), instalarías paquetes nuevos así:

```bash
pip install nombre-del-paquete
```

En Colab se usa `%pip` (con el símbolo de porcentaje) en vez de `!pip` para que la
instalación quede correctamente vinculada al entorno de Python del notebook.

**Nota:** este proyecto ya tiene `google-genai` y `beautifulsoup4` en
`requirements.txt`/`environment.yml` si trabajas en VS Code con el entorno conda
`ia_logprog` — no necesitas instalarlos de nuevo ahí.
````

- [ ] **Step 4: Escribir la sección de PubChem REST (sección 15)**

````markdown
## 15. Consumir una API REST real: PubChem

[PubChem](https://pubchem.ncbi.nlm.nih.gov/) es una base de datos pública del NIH
(Instituto Nacional de Salud de EE.UU.) con información de compuestos químicos.
Su API PUG REST no requiere API key — puedes consultarla directo con `requests`.

```python
import requests

material = "gold"  # nombre en inglés, como lo espera la API

url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{material}/property/MolecularWeight,MolecularFormula/JSON"
response = requests.get(url)
datos = response.json()
print(datos)
```

Extrae los valores del diccionario anidado que retorna la API:

```python
propiedades = datos["PropertyTable"]["Properties"][0]
peso_molecular = propiedades["MolecularWeight"]
formula = propiedades["MolecularFormula"]

print(f"Fórmula: {formula}")
print(f"Peso molecular: {peso_molecular} g/mol")
```

Ahora combina el dato real con una consulta al LLM:

```python
prompt = f"""El material {formula} tiene un peso molecular de {peso_molecular} g/mol.
Explica en dos oraciones por qué el peso molecular es relevante al diseñar la
síntesis de nanopartículas de este material."""

print(get_llm_response(prompt))
```

**Ejercicio:** repite la consulta para `"silver"` y `"titanium dioxide"`, y compara
los tres pesos moleculares obtenidos.

📖 [Colecciones (diccionarios anidados)](https://ellibrodepython.com/colecciones-python)
````

- [ ] **Step 5: Escribir la sección de web scraping (sección 16)**

````markdown
## 16. Extraer texto de una página web con `BeautifulSoup`

A veces la información que necesitas no está en una API, sino en el HTML de una
página web — por ejemplo, un reporte técnico o una publicación sobre
nanomateriales publicada en línea. `BeautifulSoup` te ayuda a extraer el texto
limpio de esa página.

```python
from bs4 import BeautifulSoup
import requests

url = "https://pubchem.ncbi.nlm.nih.gov/compound/Gold"
response = requests.get(url)
print(response)  # <Response [200]> indica que la petición fue exitosa
```

```python
soup = BeautifulSoup(response.text, "html.parser")
parrafos = soup.find_all("p")

texto_combinado = ""
for parrafo in parrafos:
    texto_combinado += "\n" + parrafo.get_text()

print(texto_combinado[:500])  # primeros 500 caracteres
```

Ahora pídele al LLM que resuma los puntos clave del texto extraído:

```python
prompt = f"""Extrae los 3 puntos más relevantes del siguiente texto sobre un
material usado en nanotecnología:

Texto:
{texto_combinado[:3000]}
"""

print(get_llm_response(prompt))
```

**Nota:** la estructura HTML de una página puede cambiar con el tiempo, lo que
puede romper este código — es normal en web scraping y requiere revisar la página
si algo deja de funcionar.

📖 [Leer archivos](https://ellibrodepython.com/leer-archivos-python)
````

- [ ] **Step 6: Escribir la sección de cierre sobre genai.Client (sección 17)**

````markdown
## 17. Cómo funciona `genai.Client` por dentro

A lo largo de esta pieza usaste `get_llm_response`, que internamente llama a
`genai.Client`. Vale la pena entender sus piezas:

```python
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explica qué es un nanotubo de carbono en una oración.",
)
print(response.text)
```

- `model`: qué versión de Gemini usar. `gemini-2.5-flash` es rápido y económico
  para el tier gratuito.
- `contents`: tu prompt como texto.
- `response.text`: el texto de la respuesta — hay más información disponible en
  `response` (tokens usados, razón de término, etc.) si la necesitas.

Este es exactamente el mismo patrón que usa `TutorAgent` (`src/multiagent_core/tutor_agent.py`)
para responder tus preguntas del curso — ahora ya sabes cómo funciona por dentro.

---

Con esto terminan las 3 partes de este material complementario. Vuelve a la
[Parte 1](EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md) si quieres repasar
desde el inicio.
````

- [ ] **Step 7: Agregar el archivo a `convert_to_notebooks_smart.py`**

Agregar `"EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.md"` a `files_to_convert`, después de la Parte 2. La lista final debe quedar:

```python
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
```

- [ ] **Step 8: Regenerar notebooks y verificar**

Run: `python convert_to_notebooks_smart.py`
Expected: `Convertidos con exito: 12`.

- [ ] **Step 9: Correr la suite completa de tests**

Run: `pytest tests/ -v --tb=short`
Expected: PASS 100%.

- [ ] **Step 10: Commit**

```bash
git add EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.md convert_to_notebooks_smart.py notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.ipynb
git commit -m "feat: agregar EXTRA_PYTHON_IA_NANOTECNOLOGIA Parte 3 (Paquetes y APIs)"
```

---

### Task 5: Actualizar `requirements.txt`/`environment.yml` y documentación

**Files:**
- Modify: `requirements.txt` (agregar `beautifulsoup4`)
- Modify: `environment.yml` (agregar `beautifulsoup4`)
- Modify: `README.md` (mencionar el material extra)
- Modify: `CLAUDE.md` (mencionar el material extra en la sección de arquitectura/contenido)

**Interfaces:** ninguna — documentación y dependencias.

- [ ] **Step 1: Verificar si `beautifulsoup4`/`requests` ya están en `requirements.txt`**

```bash
grep -i "beautifulsoup\|requests" requirements.txt environment.yml
```

Si `requests` ya está (es dependencia transitiva común), no hace falta agregarlo. `beautifulsoup4` probablemente no está — agrégalo.

- [ ] **Step 2: Agregar `beautifulsoup4` a `requirements.txt`**

Junto a `chromadb`/`sentence-transformers` (sección de dependencias del proyecto), agregar:

```
beautifulsoup4>=4.12.0
```

- [ ] **Step 3: Agregar `beautifulsoup4` a `environment.yml`**

En la sección `pip:`, junto a `chromadb`:

```yaml
      - beautifulsoup4>=4.12.0
```

- [ ] **Step 4: Agregar sección al README.md**

Agregar después de la sección "🏗️ Estructura del Repositorio" (o donde ya exista una sección de estructura), una nueva sección:

```markdown
## 🐍 Material Complementario: Python + IA en Nanotecnología

Además de las 9 unidades principales, el repositorio incluye una pieza opcional
en 3 partes (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE{1,2,3}_*.md`), adaptada del
curso público ["AI Python for Beginners"](https://www.deeplearning.ai/courses/ai-python-for-beginners)
de DeepLearning.AI. Refuerza el patrón "Python como orquestador de llamadas a un
LLM" con ejemplos 100% de nanotecnología, en español, usando Gemini. No forma
parte de la secuencia evaluada del semestre — es material de práctica libre.
```

- [ ] **Step 5: Agregar nota en CLAUDE.md**

En la sección "## Convenciones del contenido pedagógico" de `CLAUDE.md`, agregar:

```markdown
- **Material complementario (`EXTRA_*.md`)**: piezas opcionales fuera de la secuencia U0-U8, no evaluadas, no sujetas al Hilo de Oro completo. `EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE{1,2,3}_*.md` es la primera: adaptación en 3 partes del curso público "AI Python for Beginners" de DeepLearning.AI, con el patrón Python+LLM y ejemplos de nanotecnología.
```

- [ ] **Step 6: Regenerar notebooks (por si acaso) y correr la suite completa**

```bash
python convert_to_notebooks_smart.py
pytest tests/ -v --tb=short
```

Expected: `Convertidos con exito: 12`, suite 100% verde.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt environment.yml README.md CLAUDE.md
git commit -m "docs: documentar material complementario EXTRA_PYTHON_IA_NANOTECNOLOGIA y agregar beautifulsoup4"
```

---

### Task 6: Auditoría de contenido y verificación final

**Files:** ninguno modificado — solo verificación y, si hace falta, ajustes menores a los 3 `.md` de las tareas anteriores.

**Interfaces:** ninguna.

- [ ] **Step 1: Regenerar el reporte de auditoría de contenido**

```python
from pathlib import Path
from src.multiagent_core.content_auditor_agent import ContentAuditorAgent

auditor = ContentAuditorAgent()
reporte = auditor.audit_all_units(Path("."))
Path("docs/superpowers/content_audit_report.md").write_text(reporte, encoding="utf-8")
```

- [ ] **Step 2: Revisar los hallazgos de las 3 partes nuevas**

Abrir `docs/superpowers/content_audit_report.md` y localizar las secciones
`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.md`,
`_PARTE2_DATOS_Y_ARCHIVOS.md`, `_PARTE3_PAQUETES_Y_APIS.md`. Se espera el
hallazgo "Ciclo del Hilo de Oro incompleto" en las 3 (no aplica — esta pieza no
sigue el ciclo Pseudocódigo→Mermaid→Python→pytest, es material de práctica
libre, ya documentado como excepción en Task 5 Step 5). Cualquier OTRO hallazgo
(docstring faltante, type hints incompletos, riesgo de seguridad, LaTeX
malformado) debe investigarse y corregirse en el `.md` correspondiente antes de
continuar — no descartarlo sin revisar.

- [ ] **Step 3: Verificación manual en Colab — Parte 1**

Abrir `notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.ipynb` en
Colab vía el badge del `.md`. Ejecutar la celda de setup, configurar el secreto
`GEMINI_API_KEY` si hace falta, y confirmar que la sección 3 (clasificación de
bitácoras con `for`) ejecuta sin error y produce 5 líneas de salida
(`Relevante`/`No relevante`).

- [ ] **Step 4: Verificación manual en Colab — Parte 2**

Abrir `notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.ipynb`
en Colab. Confirmar que la sección 10 (extracción de datos de
`sintesis_au_np.txt`) ejecuta sin error y produce una respuesta en formato JSON
reconocible (reactivo límite, rendimiento, diámetro).

- [ ] **Step 5: Verificación manual en Colab — Parte 3**

Abrir `notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.ipynb` en
Colab. Confirmar que la sección 15 (PubChem) ejecuta sin error y retorna un peso
molecular y fórmula reales, y que la sección 16 (web scraping) ejecuta sin error
(código `<Response [200]>` y texto extraído no vacío).

- [ ] **Step 6: Push a GitHub**

```bash
git push origin master
```

- [ ] **Step 7: Commit final si hubo ajustes de Step 2**

Si la auditoría de Step 2 requirió correcciones:

```bash
git add EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE*.md notebooks/EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE*.ipynb docs/superpowers/content_audit_report.md
git commit -m "fix: correcciones de auditoría de contenido en EXTRA_PYTHON_IA_NANOTECNOLOGIA"
git push origin master
```
