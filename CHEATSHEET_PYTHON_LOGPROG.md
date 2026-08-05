# CHEATSHEET — Python para Lógica de Programación
**Curso:** Lógica de Programación y Desarrollo Agéntico con IA — UCEMICH
Referencia rápida de sintaxis. Para la explicación conceptual completa de cada tema, ver la unidad correspondiente y el link a [ellibrodepython.com](https://ellibrodepython.com/) al final de cada bloque.

---

## 🔢 Tipos de Datos

| Tipo | Ejemplo | Notas |
| :--- | :--- | :--- |
| `int` | `radio = 5` | Enteros, sin límite de tamaño en Python |
| `float` | `temp = 298.15` | Punto flotante, cuidado con comparaciones exactas (`==`) |
| `str` | `material = "Au"` | Comillas simples o dobles, indistinto |
| `bool` | `es_estable = True` | Solo `True` / `False` (mayúscula inicial) |
| `list` | `radios = [1.2, 3.4, 5.6]` | Mutable, ordenada, permite duplicados |
| `tuple` | `coord = (0.0, 1.5, 2.0)` | Inmutable, útil para coordenadas fijas |
| `dict` | `atomo = {"id": "O1", "carga": -0.8}` | Pares clave-valor |

Conversión entre tipos: `int("5")`, `float("3.14")`, `str(42)`, `bool(0)` → `False`.

📖 [Tipos de datos en Python](https://ellibrodepython.com/tipos-de-datos-en-python)

---

## 🔀 Control de Flujo

```python
# Condicional
if radio_nm > 50:
    categoria = "macro"
elif radio_nm > 1:
    categoria = "nano"
else:
    categoria = "atomico"

# Bucle for (número conocido de iteraciones)
for material in ["Au", "Ag", "TiO2"]:
    print(material)

# Bucle while (condición de parada)
temperatura = 373
while temperatura > 298:
    temperatura -= 5

# Bandera (flag) — señal booleana de estado
encontrado = False
for r in radios:
    if r > 100:
        encontrado = True
        break
```

📖 [If en Python](https://ellibrodepython.com/if-python) · [For en Python](https://ellibrodepython.com/for-python) · [While en Python](https://ellibrodepython.com/while-python)

---

## 🧩 Funciones

```python
def calcular_volumen(radio_nm: float) -> float:
    """Calcula el volumen de una nanopartícula esférica.

    Args:
        radio_nm: Radio en nanómetros.

    Returns:
        Volumen en nm³.
    """
    return (4 / 3) * 3.14159 * radio_nm ** 3

# Argumento opcional (valor por defecto)
def resumen(material: str, unidades: str = "nm") -> str:
    return f"{material} en {unidades}"

# *args: número variable de posicionales
def suma_radios(*radios: float) -> float:
    return sum(radios)

# **kwargs: número variable de nombrados (típico en llamadas MCP/tools)
def crear_particula(**propiedades) -> dict:
    return propiedades

# Lambda: función anónima de una línea
ordenar_por_radio = lambda p: p["radio_nm"]
```

📖 [Funciones en Python](https://ellibrodepython.com/funciones-en-python) · [Lambda](https://ellibrodepython.com/lambda-python)

---

## ⚠️ Errores Comunes

| Error | Causa típica | Solución |
| :--- | :--- | :--- |
| `IndentationError` | Mezclar tabs y espacios, o indentación inconsistente | Usar siempre 4 espacios, configurar el editor |
| `NameError` | Usar una variable antes de definirla o typo en el nombre | Verificar ortografía y orden de ejecución |
| `TypeError` | Operar entre tipos incompatibles (`"5" + 5`) | Convertir tipos explícitamente (`int("5") + 5`) |
| `IndexError` | Acceder a un índice de lista fuera de rango | Verificar `len(lista)` antes de indexar |
| `KeyError` | Acceder a una clave inexistente en un diccionario | Usar `dict.get("clave", valor_default)` |
| `ZeroDivisionError` | División entre cero | Validar el denominador antes de dividir |
| `ModuleNotFoundError` | Paquete no instalado en el entorno activo | `conda activate ia_logprog` antes de correr el script |

📖 [Excepciones en Python](https://ellibrodepython.com/excepciones-en-python)

---

## 💻 Comandos PowerShell Esenciales (Windows)

| Comando | Equivalente Unix | Descripción |
| :--- | :--- | :--- |
| `dir` (o `ls`) | `ls` | Lista archivos del directorio actual |
| `cd ruta` | `cd ruta` | Cambia de directorio |
| `mkdir nombre` | `mkdir nombre` | Crea una carpeta |
| `Get-Content archivo.txt` (o `cat`) | `cat` | Muestra el contenido de un archivo |
| `python script.py` | `python3 script.py` | Ejecuta un script de Python |
| `conda activate ia_logprog` | igual | Activa el entorno del curso |
| `pytest` | igual | Corre las pruebas unitarias |

---

## 🔗 Mapa de Links por Tema (ellibrodepython.com)

| Tema | Unidad | Link |
| :--- | :--- | :--- |
| Introducción a Python | U0 | [/introduccion-python](https://ellibrodepython.com/introduccion-python) |
| Hola mundo | U0 | [/hola-mundo-python](https://ellibrodepython.com/hola-mundo-python) |
| Tipos built-in | U2 | [/python-built-in](https://ellibrodepython.com/python-built-in) |
| Enteros | U3 | [/entero-en-python](https://ellibrodepython.com/entero-en-python) |
| Flotantes | U3 | [/float-python](https://ellibrodepython.com/float-python) |
| Booleanos | U3 | [/booleano-python](https://ellibrodepython.com/booleano-python) |
| Cadenas | U3 | [/cadenas-python](https://ellibrodepython.com/cadenas-python) |
| If / elif / else | U4 | [/if-python](https://ellibrodepython.com/if-python) |
| Match (pattern matching) | U4 | [/match-python](https://ellibrodepython.com/match-python) |
| For | U5 | [/for-python](https://ellibrodepython.com/for-python) |
| While | U5 | [/while-python](https://ellibrodepython.com/while-python) |
| Range | U5 | [/range-python](https://ellibrodepython.com/range-python) |
| Break / continue | U5 | [/break-python](https://ellibrodepython.com/break-python) |
| Funciones | U6 | [/funciones-en-python](https://ellibrodepython.com/funciones-en-python) |
| Lambda | U6 | [/lambda-python](https://ellibrodepython.com/lambda-python) |
| Alcance de variables | U6 | [/alcance-variables-python](https://ellibrodepython.com/alcance-variables-python) |
