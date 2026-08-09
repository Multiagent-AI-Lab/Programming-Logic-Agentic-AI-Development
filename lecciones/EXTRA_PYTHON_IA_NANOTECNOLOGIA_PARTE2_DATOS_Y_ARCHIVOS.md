# EXTRA: Python + IA aplicado a Nanotecnología — Parte 2: Datos y Archivos

Continuación de la Parte 1: Fundamentos (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.ipynb`, disponible en `notebooks/`).
Esta parte es autocontenida — no necesitas haber ejecutado la Parte 1 en esta sesión.

**Contenido de esta parte:** manejo de excepciones, lectura de archivos de texto,
funciones propias, `*args`/`**kwargs`.

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

Define `get_llm_response`, igual que en la Parte 1:

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

**Continúa en la Parte 3: Paquetes y APIs** (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE3_PAQUETES_Y_APIS.ipynb`, disponible en `notebooks/`).
