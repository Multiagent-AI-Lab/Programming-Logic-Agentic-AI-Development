# EXTRA: Python + IA aplicado a Nanotecnología — Parte 1: Fundamentos

**Curso:** Lógica de Programación y Desarrollo Agéntico con IA  
**Institución:** Universidad de la Ciénega del Estado de Michoacán de Ocampo (UCEMICH)  
**Profesor:** Luis José Yudico Anaya  
**Carrera:** Ingeniería en Nanotecnología  
**Nivel:** Primer Semestre  

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

**Continúa en la Parte 2: Datos y Archivos** (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.ipynb`, disponible en `notebooks/`).
