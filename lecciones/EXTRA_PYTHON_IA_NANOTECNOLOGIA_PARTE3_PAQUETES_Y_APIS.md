# EXTRA: Python + IA aplicado a Nanotecnología — Parte 3: Paquetes y APIs

Continuación de la Parte 2: Datos y Archivos (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE2_DATOS_Y_ARCHIVOS.ipynb`, disponible en `notebooks/`).
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
    %pip install -q google-genai beautifulsoup4 lxml
```

Define `get_llm_response`, igual que en las partes anteriores:

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

Con `matplotlib` puedes graficar directamente ese resumen:

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

soup = BeautifulSoup(response.text, "html.parser")
parrafos = soup.find_all("p")
print(len(parrafos), "párrafos encontrados")
print("".join(p.get_text() for p in parrafos)[:200])
```

Si ejecutaste la celda anterior, verás algo como `Please enable Javascript...` y
0 párrafos reales: PubChem renderiza esta página con JavaScript en el navegador,
y `requests` solo descarga el HTML inicial (sin ejecutar JavaScript), así que el
contenido real nunca llega a `response.text`. **Este es precisamente el riesgo
que la nota de abajo advierte** — no todas las páginas son estáticas.

Para esta técnica necesitas una página que sirva su HTML completo desde el
servidor, sin depender de JavaScript. Wikipedia es un buen ejemplo:

```python
url = "https://en.wikipedia.org/wiki/Gold_nanoparticle"
response = requests.get(url)

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
si algo deja de funcionar. Wikipedia sirve bien para *practicar la técnica* de
extracción de texto, pero para un reporte científico formal la fuente confiable
sigue siendo PubChem — solo que, al ser una aplicación moderna renderizada con
JavaScript, requeriría herramientas adicionales (como `selenium`) para el HTML
de su página de compuesto.

### Extraer contenido real de PubChem con XML

En vez de renunciar a PubChem, hay una vía intermedia: su API REST también
sirve descripciones de compuestos en formato XML (no solo JSON, como en la
sección 15), y `BeautifulSoup` puede parsear XML igual que HTML:

```python
from bs4 import BeautifulSoup
import requests

url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/titanium%20dioxide/description/XML"
response = requests.get(url)

soup = BeautifulSoup(response.text, "xml")
descripciones = soup.find_all("Description")

for descripcion in descripciones:
    print(descripcion.get_text())
    print("---")
```

`features="xml"` (en vez de `"html.parser"`) le indica a `BeautifulSoup` que use
un parser de XML — requiere el paquete `lxml`, ya instalado en la celda de setup
de esta parte. El contenido es más breve que el de Wikipedia (PubChem prioriza
datos estructurados sobre prosa), pero es la fuente formal, sin depender de
JavaScript.

📖 [Leer archivos](https://ellibrodepython.com/leer-archivos-python)

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
Parte 1 (`EXTRA_PYTHON_IA_NANOTECNOLOGIA_PARTE1_FUNDAMENTOS.ipynb`, disponible
en `notebooks/`) si quieres repasar desde el inicio.
