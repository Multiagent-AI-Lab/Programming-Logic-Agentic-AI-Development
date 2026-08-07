# UNIDAD 3: Variables, Tipos de Datos y Operadores en Modelado Físico y Nanotecnología

**Duración:** 2 semanas (12 horas)  
**Curso:** Lógica de Programación y Desarrollo Agéntico con IA  
**Institución:** Universidad de la Ciénega del Estado de Michoacán (UCEMICH)  
**Dirigido a:** Ingeniería en Inteligencia Artificial y Nanotecnología (1er Semestre)  

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Multiagent-AI-Lab/Programming-Logic-Agentic-AI-Development/blob/master/notebooks/UNIDAD_3_VARIABLES_OPERADORES.ipynb)

```python
import os
import sys

if 'google.colab' in sys.modules:
    repo_dir = "Programming-Logic-Agentic-AI-Development"
    if not os.path.exists(repo_dir):
        !git clone -q https://github.com/Multiagent-AI-Lab/{repo_dir}.git
    os.chdir(repo_dir)
    %pip install -q mcp fastmcp chromadb rich
```

---

## 📚 OBJETIVOS DE APRENDIZAJE

Al finalizar esta unidad, el estudiante será capaz de:
1. **Analizar la gestión de memoria interna en Python**, distinguiendo entre tipos de datos primitivos y estructurados, así como la implicación de la mutabilidad e inmutabilidad en la eficiencia algorítmica.
2. **Implementar buenas prácticas de desarrollo** bajo el estándar PEP 8, definiendo variables de manera semánticamente clara y estructurando constantes físicas de precisión científica para el modelado a nanoescala.
3. **Dominar el flujo lógico y la precedencia de operadores**, utilizando operadores aritméticos, relacionales y lógicos combinados mediante la técnica de cortocircuito lógico para evitar excepciones en tiempo de ejecución.
4. **Traducir modelos físicos y matemáticos complejos** (como la Ley de Coulomb y la ecuación de energía de Bohr) a código Python estructurado, implementando validaciones físicas basadas en límites reales (femtómetros).
5. **Diseñar suites de pruebas unitarias automatizadas con Pytest**, aplicando comparaciones numéricas de precisión mediante tolerancia relativa para lidiar con las limitaciones del estándar IEEE 754 de punto flotante.

---

# 3.0 Entrada Gradual: De una Variable Simple a un Cálculo Físico

Antes de trabajar con estructuras complejas como matrices de coordenadas moleculares, construyamos la intuición con el ejemplo más simple posible: una sola variable numérica.

### 💻 Paso 1: Mostrar un mensaje

```python
print("Iniciando simulación de nanopartícula")
```

### 💻 Paso 2: Guardar un dato en una variable

```python
radio_nm = 5.2
print(radio_nm)
```

Aquí `radio_nm` es una **variable**: una etiqueta que apunta a un valor en memoria (ver la analogía del Almacén Central más abajo, sección 3.1).

### 💻 Paso 3: Variable con un cálculo

```python
radio_nm = 5.2
area_superficial = 4 * 3.14159 * radio_nm ** 2
print(area_superficial)
```

### Metodología de 4 Pasos: De la Ecuación al Código

Para traducir cualquier fórmula física a Python, seguimos siempre la misma secuencia:

1. **Identificar las variables de entrada** y sus unidades (p. ej. `masa_g`, `volumen_cm3`).
2. **Escribir la ecuación matemática** en su notación estándar (p. ej. $\rho = m / V$).
3. **Mapear cada símbolo a un nombre de variable Python** semánticamente claro (`densidad = masa_g / volumen_cm3`).
4. **Validar el resultado** con un caso conocido antes de confiar en el código (p. ej. la densidad del agua debe dar aproximadamente `1.0 g/cm³`).

### 💻 Ejemplo Aplicado: Densidad de un Material

```python
masa_g = 19.3        # Ejemplo: masa de una muestra de oro (Au)
volumen_cm3 = 1.0     # Volumen de la muestra

densidad = masa_g / volumen_cm3
print(f"Densidad: {densidad} g/cm³")
```

Con esta base (variable → cálculo → validación) estamos listos para abordar estructuras de datos más complejas, como las matrices de coordenadas moleculares que se introducen a continuación.

📖 [Enteros en Python](https://ellibrodepython.com/entero-en-python) · [Flotantes en Python](https://ellibrodepython.com/float-python) · [Booleanos en Python](https://ellibrodepython.com/booleano-python) · [Cadenas en Python](https://ellibrodepython.com/cadenas-python)

---

# 3.1 Tipos de Datos Primitivos y Dinámicos: La Arquitectura de Memoria de Python

En Python, a diferencia de lenguajes compilados estáticos como C++ o Java, el tipado es dinámico y fuertemente tipado. Esto significa que los tipos de datos se asocian con los objetos en memoria y no con las variables que apuntan a ellos. Además, en Python todo es un objeto. Cada entero, flotante, cadena de texto o lista es una estructura de datos completa que hereda métodos y atributos de una clase base.

### Mutabilidad vs Inmutabilidad: El Mecanismo Interno

El comportamiento de un objeto ante los operadores y las asignaciones en Python está determinado por su **mutabilidad**:

1. **Inmutables (Valor Fijo en Memoria)**:
   - Una vez que un objeto inmutable es creado en el espacio de memoria (Heap), su valor interno no puede ser alterado bajo ninguna circunstancia.
   - Si intentamos modificar el valor de una variable que contiene un objeto inmutable (por ejemplo, sumando `1` a un entero), Python no modifica la celda de memoria original. En su lugar, calcula el nuevo valor, crea un nuevo objeto en una dirección de memoria diferente y reasigna la variable (etiqueta) para que apunte a este nuevo objeto.
   - **Tipos comunes**: `int`, `float`, `str`, `bool`, `tuple`, `frozenset`.
   - *Optimización interna (Integer Caching)*: Python optimiza el rendimiento del sistema precargando en memoria los enteros en el rango de `[-5, 256]`. Si creas variables con estos valores, todas apuntarán a la misma dirección física exacta en memoria para ahorrar recursos.

2. **Mutables (Estructuras Dinámicas in-situ)**:
   - Los objetos mutables permiten modificar su contenido interno sin alterar su dirección de memoria base (`id()`).
   - Cuando añadimos un elemento a una lista o cambiamos una coordenada atómica dentro de una matriz, el contenedor sigue residiendo en la misma posición de la memoria RAM. Esto es altamente eficiente en términos de uso de memoria para grandes volúmenes de datos, pero introduce el riesgo de efectos secundarios no deseados si múltiples variables apuntan al mismo objeto.
   - **Tipos comunes**: `list`, `dict`, `set`.

---

### 💡 ANALOGÍA DIDÁCTICA 1: Variables, Identificadores e IDs vs El Almacén Central

Para comprender la diferencia entre variables, objetos e identificadores de memoria en Python, imaginemos el Almacén de Reactivos y Materiales de la UCEMICH:

* **El Identificador (Variable)**: Es una etiqueta de papel colgante donde escribimos un nombre legible (ej. `temperatura_muestra` o `concentracion_molar`). Esta etiqueta no contiene la sustancia; es solo un trozo de papel que se puede colgar del asa de un recipiente físico.
* **El Objeto (Valor en Memoria)**: Es el contenedor real (un frasco de vidrio o un cajón de madera) que almacena la sustancia química o el valor numérico (por ejemplo, un líquido a `25.5` °C o un bloque de grafito).
* **La Dirección de Memoria (`id()`)**: Equivale a las **coordenadas GPS exactas o la clave catastral** del cajón dentro del almacén tridimensional. No importa cuántas etiquetas colguemos en el mismo cajón, la coordenada física (el valor devuelto por `id(variable)`) sigue siendo exactamente la misma.
* **Inmutabilidad en el Almacén**: Si tenemos la etiqueta `masa = 5` (un entero inmutable) y decidimos cambiar su valor a `6`, no podemos alterar el número pintado dentro del cajón `5`. En su lugar, el almacenista busca o crea el cajón `6` en otra ubicación GPS del almacén y traslada físicamente la etiqueta de papel `masa` hacia ese nuevo cajón. El cajón `5` permanece intacto para otras etiquetas que lo requieran.
* **Mutabilidad en el Almacén**: Si la etiqueta `coordenadas` está colgada en una caja mutable (una lista de tres elementos), y decidimos cambiar el primer elemento de la caja, el almacenista abre la caja en el mismo lugar GPS, saca el objeto viejo, introduce el objeto nuevo y vuelve a cerrar la caja. La dirección física GPS de la caja no cambia; la etiqueta sigue apuntando a las mismas coordenadas físicas.

---

# 3.2 Gestión de Memoria y Copias de Datos (Shallow vs Deep Copy)

En modelado molecular a nanoescala, una de las representaciones más utilizadas es la matriz de coordenadas tridimensionales de los átomos. Por ejemplo, una molécula de agua ($H_2O$) se modela como una lista de listas de flotantes:

```python
coordenadas: List[List[float]] = [
    [0.0000, 0.0000, 0.0000],  # Oxígeno (O) en el origen
    [0.9584, 0.0000, 0.0000],  # Hidrógeno 1 (H1) en el eje X
    [-0.2400, 0.9279, 0.0000]  # Hidrógeno 2 (H2) en el plano XY
]
```

Esta estructura es una lista anidada (una lista que contiene tres sublistas). Cuando manipulamos esta matriz para simular vibraciones moleculares, fuerzas interatómicas o desplazamientos térmicos, debemos realizar copias para preservar el estado inicial de la simulación. En Python, existen tres niveles para copiar o asignar datos, cada uno con un comportamiento en memoria radicalmente distinto:

1. **Asignación Directa (Puntero o Referencia)**:
   ```python
   referencia = coordenadas
   ```
   No se crea ningún objeto nuevo en memoria. La variable `referencia` apunta exactamente a la misma dirección física en memoria RAM que `coordenadas`. Si modificas una coordenada a través de `referencia`, el cambio se verá reflejado inmediatamente en `coordenadas`.

2. **Copia Superficial (Shallow Copy)**:
   ```python
   import copy
   copia_superficial = copy.copy(coordenadas)
   ```
   Crea un nuevo objeto en memoria para la lista externa (el contenedor principal). Sin embargo, los elementos internos (las sublistas de coordenadas de cada átomo) **no se duplican**; en su lugar, la nueva lista principal se llena con referencias a las sublistas originales en memoria. Si modificas un átomo modificando la sublista, el cambio afectará tanto a la matriz original como a la copia.

3. **Copia Profunda (Deep Copy)**:
   ```python
   copia_profunda = copy.deepcopy(coordenadas)
   ```
   Crea un nuevo objeto para la lista externa y, de manera recursiva, recorre la estructura duplicando cada uno de los subobjetos internos, asignándoles nuevas direcciones de memoria física. Esto garantiza un aislamiento absoluto de los datos en simulaciones independientes.

---

### 💡 ANALOGÍA DIDÁCTICA 2: El Mapa del Tesoro y las Habitaciones Físicas

Imaginemos que dos investigadores de la UCEMICH están analizando la estructura de un laboratorio cuántico subterráneo:

* **Asignación por Referencia (Compartir el mismo plano original)**: Ambos científicos comparten el mismo plano físico impreso en una sola hoja de papel. Si el Investigador A dibuja una X roja en el plano para indicar un peligro, el Investigador B ve la X roja de inmediato porque están mirando exactamente la misma hoja de papel físico.
* **Copia Superficial (Fotocopiar el plano general compartiendo las habitaciones)**: El Investigador B fotocopia el plano general de distribución. Ahora tienen dos hojas de papel distintas (diferentes direcciones de memoria de la lista principal). Sin embargo, el plano describe habitaciones que son físicas e históricas: ambos planos conducen a las mismas tres habitaciones reales del castillo. Si el Investigador A entra a la Habitación 1 y pinta una pared de azul (modifica el valor de una sublista interna mutable), el Investigador B, al entrar a la Habitación 1 guiado por su fotocopia del plano, encontrará la pared azul. Las habitaciones físicas se comparten, aunque las hojas de papel del plano general sean distintas.
* **Copia Profunda (Duplicar el plano y construir un castillo réplica)**: El Investigador B decide tomar el plano, comprar un terreno lejano y mandar construir una réplica exacta del laboratorio con ladrillos y paredes independientes (direcciones de memoria completamente nuevas para las sublistas). Si el Investigador A entra a la Habitación 1 de su laboratorio original y pinta la pared de azul, la Habitación 1 de la réplica construida por el Investigador B se mantendrá intacta con su pintura original. Los datos están 100% aislados.

---

### 💻 Código Python Completo: `mutabilidad_rastreo.py`

A continuación se presenta el código completo del módulo de rastreo de memoria diseñado para estudiantes de ingeniería. El código permite visualizar de forma interactiva las direcciones hexadecimales de memoria y el impacto de modificar datos mutables.

```python
"""Script interactivo de rastreo de memoria y mutabilidad de matrices de coordenadas atómicas.

Este script proporciona una interfaz interactiva en terminal para que los estudiantes
comprendan la diferencia fundamental entre copiar por referencia, copia superficial
(shallow copy) y copia profunda (deep copy) utilizando matrices de coordenadas
atómicas (listas anidadas de flotantes) como caso de estudio.
"""

import copy
from typing import List


def imprimir_matriz_memoria(nombre: str, matriz: List[List[float]]) -> None:
    """Imprime una matriz de coordenadas con las direcciones de memoria de sus componentes.

    Muestra el ID de memoria de la lista principal, el ID de cada sublista (vector de coordenadas)
    y los valores internos. Esto permite visualizar el impacto de las modificaciones en memoria.

    Args:
        nombre: Nombre descriptivo de la variable/matriz.
        matriz: Matriz de coordenadas 3D a inspeccionar (lista de listas de floats).
    """
    print(f"\n=== Estructura en Memoria de: {nombre} ===")
    print(f"Dirección de la lista principal (ID): {id(matriz)}")
    for i, atomo in enumerate(matriz):
        print(
            f"  Átomo {i} -> Dirección Sublista (ID): {id(atomo)} | "
            f"Coordenadas: [X: {atomo[0]:.4f}, Y: {atomo[1]:.4f}, Z: {atomo[2]:.4f}]"
        )
    print("=" * (40 + len(nombre)))


def interactivo() -> None:
    """Ejecuta el menú interactivo para el rastreo de memoria."""
    # Matriz original: Coordenadas de una molécula de agua (H2O) aproximada en Angstroms
    # Formato: [Oxígeno, Hidrógeno 1, Hidrógeno 2]
    original: List[List[float]] = [
        [0.0000, 0.0000, 0.0000],   # Oxígeno
        [0.9584, 0.0000, 0.0000],   # Hidrógeno 1
        [-0.2400, 0.9279, 0.0000]   # Hidrógeno 2
    ]

    # Crear las copias
    referencia = original                    # Copia de referencia (apuntan al mismo objeto)
    copia_superficial = copy.copy(original)  # Copia superficial (shallow copy)
    copia_profunda = copy.deepcopy(original) # Copia profunda (deep copy)

    print("=====================================================================")
    print("🔬 SIMULADOR INTERACTIVO DE MUTABILIDAD Y RASTREO DE MEMORIA 🔬")
    print("=====================================================================")
    print("Se ha inicializado una matriz original con coordenadas del H2O (Ångstroms).")
    
    while True:
        print("\n--- Opciones de Inspección ---")
        print("1. Mostrar todas las matrices y sus direcciones de memoria (IDs)")
        print("2. Modificar una coordenada en la matriz ORIGINAL")
        print("3. Modificar una coordenada en la COPIA SUPERFICIAL")
        print("4. Modificar una coordenada en la COPIA PROFUNDA")
        print("5. Reiniciar todas las matrices a su estado original")
        print("6. Salir")
        
        opcion = input("\nSeleccione una opción (1-6): ").strip()
        
        if opcion == "1":
            imprimir_matriz_memoria("ORIGINAL (original)", original)
            imprimir_matriz_memoria("REFERENCIA (referencia = original)", referencia)
            imprimir_matriz_memoria("COPIA SUPERFICIAL (copy.copy(original))", copia_superficial)
            imprimir_matriz_memoria("COPIA PROFUNDA (copy.deepcopy(original))", copia_profunda)
            
            print("\n💡 ANÁLISIS DE DIRECCIONES DE MEMORIA:")
            print(f"- 'original' y 'referencia' comparten el mismo ID principal: {id(original) == id(referencia)}")
            print(f"- 'original' y 'copia_superficial' comparten el mismo ID principal: {id(original) == id(copia_superficial)}")
            print(f"- 'original' y 'copia_profunda' comparten el mismo ID principal: {id(original) == id(copia_profunda)}")
            print(f"- Comparten el mismo ID para la sublista del Átomo 0:")
            print(f"  * superficial vs original: {id(copia_superficial[0]) == id(original[0])} (¡Cuidado! Apuntan al mismo objeto interno)")
            print(f"  * profunda vs original: {id(copia_profunda[0]) == id(original[0])} (¡Seguro! Se clonaron los objetos internos)")

        elif opcion in ("2", "3", "4"):
            nombre_matriz = ""
            matriz_a_modificar: List[List[float]] = []
            if opcion == "2":
                nombre_matriz = "ORIGINAL"
                matriz_a_modificar = original
            elif opcion == "3":
                nombre_matriz = "COPIA SUPERFICIAL"
                matriz_a_modificar = copia_superficial
            elif opcion == "4":
                nombre_matriz = "COPIA PROFUNDA"
                matriz_a_modificar = copia_profunda
            
            print(f"\nModificando una coordenada en la matriz {nombre_matriz}:")
            try:
                idx_atomo = int(input("Ingrese el índice del átomo a modificar (0, 1, 2): "))
                if idx_atomo not in (0, 1, 2):
                    raise ValueError("El índice del átomo debe ser 0, 1 o 2.")
                
                idx_coord = int(input("Ingrese el índice de la coordenada (0=X, 1=Y, 2=Z): "))
                if idx_coord not in (0, 1, 2):
                    raise ValueError("El índice de la coordenada debe ser 0, 1 o 2.")
                
                nuevo_valor = float(input("Ingrese el nuevo valor real (flotante): "))
                
                # Realizar la modificación
                valor_anterior = matriz_a_modificar[idx_atomo][idx_coord]
                matriz_a_modificar[idx_atomo][idx_coord] = nuevo_valor
                
                print(f"\n✅ Cambio realizado en {nombre_matriz}: Átomo {idx_atomo}[{idx_coord}] de {valor_anterior:.4f} a {nuevo_valor:.4f}")
                
            except ValueError as e:
                print(f"❌ Error de entrada: {e}. Intente de nuevo.")
                continue

        elif opcion == "5":
            original = [
                [0.0000, 0.0000, 0.0000],
                [0.9584, 0.0000, 0.0000],
                [-0.2400, 0.9279, 0.0000]
            ]
            referencia = original
            copia_superficial = copy.copy(original)
            copia_profunda = copy.deepcopy(original)
            print("\n🔄 Todas las matrices y copias han sido restauradas al estado inicial.")
            
        elif opcion == "6":
            print("\n👋 ¡Gracias por usar el simulador de memoria! Saliendo del programa.")
            break
        else:
            print("❌ Opción inválida. Seleccione un número del 1 al 6.")


if __name__ == "__main__":
    interactivo()
```

---

### 🔍 Desglose Paso a Paso de `mutabilidad_rastreo.py`

Analicemos línea por línea el comportamiento y lógica del script anterior:

* **Líneas 9-10 (`import copy`, `from typing import List`)**: Importamos la biblioteca estándar de copia de Python para disponer de los métodos `copy.copy` y `copy.deepcopy`. Importamos `List` del módulo de tipado estático (Type Hinting) para documentar formalmente la firma de nuestras funciones científicas.
* **Líneas 13-30 (Función `imprimir_matriz_memoria`)**:
  - `id(matriz)` (Línea 24): Retorna el identificador entero único para el contenedor principal de la lista. En la implementación estándar CPython, este número representa la dirección física en la memoria RAM donde comienza el array de punteros de la lista.
  - El bucle `for i, atomo in enumerate(matriz):` recorre cada fila de la matriz molecular.
  - `id(atomo)` (Línea 27): Obtiene el ID en memoria de cada sublista interna que almacena los tres flotantes `[x, y, z]`. Esto es crucial para evidenciar que, en una copia superficial, a pesar de que el ID principal de la lista cambie, el ID de cada fila individual sigue siendo idéntico al de la lista original.
* **Líneas 37-41 (Inicialización de `original`)**: Se genera la estructura de la simulación en formato de lista de listas. En memoria heap, se crean cuatro objetos de tipo lista: una lista principal de tamaño 3, y tres sublistas de tamaño 3 cada una, conteniendo flotantes inmutables.
* **Líneas 44-46 (Mapeo y Duplicación)**:
  - `referencia = original`: Crea una nueva variable `referencia` que copia el puntero de `original`. Ambos comparten el mismo ID.
  - `copia_superficial = copy.copy(original)`: Genera un nuevo objeto de lista principal. Sin embargo, en su interior copia los punteros hacia las tres sublistas de `original`.
  - `copia_profunda = copy.deepcopy(original)`: Genera una lista principal totalmente nueva, y crea tres sublistas totalmente nuevas en memoria, copiando únicamente los números flotantes internos de forma recursiva.
* **Líneas 71-76 (Verificación `is` vs `==`)**:
  - El operador `is` evalúa la **identidad** de los objetos. Retorna `True` si y solo si las direcciones de memoria RAM a las que apuntan ambos operandos son idénticas, es decir, `id(a) == id(b)`.
  - El operador `==` evalúa el **valor** de los objetos. Compara si el contenido de los objetos es lógicamente idéntico, invocando internamente el método especial `__eq__()` del objeto.
  - Por esta razón, `original is copia_superficial` resulta en `False` (ya que ocupan diferentes contenedores principales en memoria), pero `original[0] is copia_superficial[0]` resulta en `True` (debido a que la copia superficial copió únicamente la referencia del subobjeto interno).

---

# 3.3 Identificadores, Variables y Constantes Físicas en Nanociencia

En el ámbito de la ingeniería en inteligencia artificial orientada a la ciencia física, el código debe actuar como documentación científica autoexplicativa. Para lograr esto, es mandatorio adherirse al estándar de estilo **PEP 8**:

* **Estilo snake_case (Variables e Identificadores comunes)**: Se escriben estrictamente en minúsculas uniendo palabras con guiones bajos (ej. `fuerza_electrostatica`, `distancia_en_metros`). Esto mejora drásticamente la legibilidad de términos científicos largos.
* **Estilo UPPER_CASE (Constantes Físicas)**: Python no posee una palabra clave especial (como `const` en C++) que impida a nivel de intérprete modificar un valor. Por convención y rigor, las constantes de la física cuántica y molecular se escriben completamente en mayúsculas (ej. `MASA_ELECTRON`). Esto le advierte al programador e indica a los analizadores estáticos de código (*linters* como Pylint) que alterar dicho valor representa un error de diseño grave.

### Tabla de Constantes Físicas en Nanociencia (Estándar CODATA)

Las constantes físicas utilizadas para resolver la física a escala atómica están tabuladas a continuación con sus respectivos valores y la descripción física de su rol cuántico:

| Constante | Identificador Python | Símbolo Matemático | Valor Aproximado | Unidades del S.I. | Descripción Científica |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **Constante de Coulomb** | `K_COULOMB` | $k_e$ | $8.9875517923 \times 10^9$ | $\text{N}\cdot\text{m}^2/\text{C}^2$ | Constante de proporcionalidad electrostática en el vacío. |
| **Masa del Electrón** | `MASA_ELECTRON` | $m_e$ | $9.1093837015 \times 10^{-31}$ | $\text{kg}$ | Masa inercial en reposo de un electrón libre. |
| **Carga Elemental** | `CARGA_ELEMENTAL` | $e$ | $1.602176634 \times 10^{-19}$ | $\text{C}$ | Magnitud de la carga eléctrica de un electrón o protón. |
| **Permitividad del Vacío** | `PERMITIVIDAD_VACIO` | $\epsilon_0$ | $8.8541878128 \times 10^{-12}$ | $\text{F/m}$ | Capacidad del vacío para permitir campos eléctricos. |
| **Constante de Planck** | `CONSTANTE_PLANCK` | $h$ | $6.62607015 \times 10^{-34}$ | $\text{J}\cdot\text{s}$ | Relación fundamental entre energía y frecuencia cuántica. |
| **Factor de Conversión** | `JOULES_A_EV` | $1\text{ eV}$ | $1.602176634 \times 10^{-19}$ | $\text{J/eV}$ | Conversión del Sistema Internacional a escala de energía atómica. |

---

# 3.4 Operadores Aritméticos, Relacionales y Lógicos

En expresiones matemáticas complejas, el orden de evaluación es dictado por las reglas de precedencia de Python. Omitir estas reglas provoca errores sutiles de lógica algorítmica difíciles de rastrear (bugs semánticos).

### Tabla Completa de Precedencia de Operadores (De mayor a menor jerarquía)

| Jerarquía | Operadores | Nombre / Tipo de Operación | Dirección de Evaluación |
| :---: | :--- | :--- | :---: |
| **1** | `()` | Paréntesis (Agrupamiento) | De adentro hacia afuera |
| **2** | `**` | Exponenciación / Potencia | De derecha a izquierda |
| **3** | `+x`, `-x` | Identidad positiva y negación (unarios) | De derecha a izquierda |
| **4** | `*`, `/`, `//`, `%` | Multiplicación, división real, división entera, residuo/módulo | De izquierda a derecha |
| **5** | `+`, `-` | Suma y resta binarias | De izquierda a derecha |
| **6** | `<`, `<=`, `>`, `>=`, `==`, `!=`, `is`, `is not`, `in`, `not in` | Comparaciones y operadores relacionales/membresía | De izquierda a derecha |
| **7** | `not` | Negación lógica | De izquierda a derecha |
| **8** | `and` | Conjunción lógica (Y) | De izquierda a derecha |
| **9** | `or` | Disyunción lógica (O) | De izquierda a derecha |

---

### 💡 ANALOGÍA DIDÁCTICA 3: Cortocircuito Lógico y Sensores de Seguridad en Cascada

El **cortocircuito lógico** (short-circuit evaluation) es un mecanismo optimizado de Python en el que las expresiones que involucran operadores `and` y `or` detienen su evaluación en el instante exacto en que el resultado booleano final queda definido matemáticamente:

*   Para un operador `and` (`A and B`): Si `A` es `False`, el resultado total es obligatoriamente `False` sin importar el valor de `B`. Por lo tanto, `B` **nunca se evalúa**.
*   Para un operador `or` (`A or B`): Si `A` es `True`, el resultado total es obligatoriamente `True` sin importar el valor de `B`. Por lo tanto, `B` **nunca se evalúa**.

Imaginemos las alarmas de seguridad de un **Reactor Químico Nanotecnológico** en la UCEMICH:

```
[ Sensor Presión (A) ] ────(¿Límite de Presión Crítico?)────┐
                                                            ├─► [ Alarma Evacuación (OR) ]
[ Sensor Temperatura (B) ] ──(¿Temperatura Crítica?)────────┘
```
1.  **Evaluación OR (Alarma Crítica)**: 
    El protocolo dicta la regla lógica: `presión_excedida or temperatura_excedida`. Si la presión del reactor se dispara a valores críticos de explosión (`True`), el sistema no pierde microsegundos valiosos en consultar la temperatura del reactor (un proceso lento a través del bus de datos). La alarma física de evacuación de la UCEMICH se activa de forma instantánea. Este salto directo se conoce como cortocircuito del operador `or`.

```
[ Sensor Válvula 1 (A) ] ────(¿Válvula Abierta?)────┐
                                                    ├─► [ Flujo Reactivos Seguro (AND) ]
[ Sensor Válvula 2 (B) ] ────(¿Válvula Abierta?)────┘
```
2.  **Evaluación AND (Inicio del Experimento)**:
    Para iniciar el flujo de un gas reactivo pesado, la regla indica: `valvula_1_abierta and valvula_2_abierta`. El sistema inspecciona primero la `valvula_1_abierta`. Si el sensor detecta que esta válvula de alivio se encuentra cerrada (`False`), el sistema detiene inmediatamente la secuencia de arranque de forma preventiva. No consulta la válvula 2, ya que la condición lógica de seguridad ya ha sido violada. Esto previene accidentes y se conoce como cortocircuito del operador `and`.

#### Aplicación Práctica del Cortocircuito para Evitar Errores de Ejecución:
En programación, esto evita lanzar excepciones catastróficas como la división por cero o el desbordamiento de índices. Consideremos el siguiente código:

```python
distancia = 0.0  # Escala de colapso físico
# La siguiente expresión evita una división por cero gracias al cortocircuito:
if distancia > 1e-15 and (K_COULOMB * CARGA_ELEMENTAL / (distancia ** 2)) > 10.0:
    print("La fuerza sobrepasa el límite del sistema.")
```
Si evaluamos la expresión matemática cuando `distancia` es `0.0`:
- Python comprueba primero `distancia > 1e-15`. Dado que `0.0 > 1e-15` es `False`, el operador `and` hace cortocircuito.
- El intérprete ignora inmediatamente la segunda parte: `(K_COULOMB * CARGA_ELEMENTAL / (distancia ** 2))`.
- De este modo, se evita la división por cero (`ZeroDivisionError`) que habría detenido el simulador de forma abrupta si no contara con cortocircuito lógico.

---

# 3.5 Conversión de Ecuaciones Físicas a Notación Algorítmica

Traducir ecuaciones de la física matemática al código sin perder precisión requiere un alto dominio de los tipos de datos y la precedencia. Estudiaremos la Ley de Coulomb y la ecuación cuántica de Bohr.

### 1. Ley de Coulomb (Electrostática Clásica)
La ley determina la fuerza electrostática de atracción o repulsión entre dos cargas puntuales:

$$F = k_e \frac{q_1 \cdot q_2}{r^2}$$

Donde:
*   $F$ es la fuerza electrostática calculada en Newtons ($\text{N}$).
*   $k_e$ es la constante de Coulomb ($8.9875517923 \times 10^9 \text{ N}\cdot\text{m}^2/\text{C}^2$).
*   $q_1, q_2$ son los valores netos de las cargas en Coulombs ($\text{C}$).
*   $r$ es la distancia de separación lineal de las cargas en metros ($\text{m}$). En escala atómica, esta distancia se sitúa en el rango de los nanómetros ($10^{-9}\text{ m}$) o Ångstroms ($10^{-10}\text{ m}$).

### 2. Ecuación de Niveles de Energía de Bohr (Física Cuántica)
El modelo de Bohr describe el comportamiento energético del electrón en átomos hidrogenoides (átomos con un núcleo atómico pesado rodeado de un solo electrón, como el átomo de Hidrógeno, Helio ionizado $He^+$, o Litio doblemente ionizado $Li^{2+}$):

$$E_n = - \frac{m_e \cdot e^4 \cdot Z^2}{8 \cdot \epsilon_0^2 \cdot h^2 \cdot n^2}$$

Donde:
*   $E_n$ es la energía cuantizada del electrón en el nivel orbital $n$, expresada en Joules ($\text{J}$).
*   $m_e$ es la masa en reposo del electrón ($9.1093837015 \times 10^{-31}\text{ kg}$).
*   $e$ es la carga eléctrica fundamental ($1.602176634 \times 10^{-19}\text{ C}$).
*   $Z$ es el número atómico (cantidad de protones en el núcleo, ej. $Z=1$ para Hidrógeno, $Z=2$ para Helio).
*   $\epsilon_0$ es la permitividad eléctrica del vacío ($8.8541878128 \times 10^{-12}\text{ F/m}$).
*   $h$ es la constante de Planck ($6.62607015 \times 10^{-34}\text{ J}\cdot\text{s}$).
*   $n$ es el número cuántico principal (un entero discreto $n \ge 1$ que define la órbita permitida).

---

### 💻 Código Python Completo: `fisica_atomica.py`

A continuación se expone el código del módulo científico completo e integrado que realiza estos cálculos utilizando variables tipadas y validación estricta de rangos de operación.

```python
"""Cálculos robustos de física atómica a nanoescala y microescala.

Este módulo proporciona implementaciones de nivel profesional y rigor científico para:
1. El cálculo de la fuerza electrostática de Coulomb entre dos cargas puntuales.
2. La determinación de los niveles de energía de Bohr para un electrón confinado
   en un átomo hidrogenoide.

Todas las constantes físicas están definidas en notación científica basada en
los datos recomendados por CODATA. Las funciones cuentan con validación estricta
de tipos y rangos de entrada.
"""

import math
from typing import Union, Dict

# =====================================================================
# CONSTANTES FÍSICAS DE PRECISIÓN (CODATA)
# =====================================================================
K_COULOMB: float = 8.9875517923e9  # Constante de Coulomb (N·m²/C²)
MASA_ELECTRON: float = 9.1093837015e-31  # Masa en reposo del electrón (kg)
CARGA_ELEMENTAL: float = 1.602176634e-19  # Carga eléctrica elemental (C)
PERMITIVIDAD_VACIO: float = 8.8541878128e-12  # Permitividad eléctrica del vacío (F/m)
CONSTANTE_PLANCK: float = 6.62607015e-34  # Constante de Planck (J·s)
JOULES_A_EV: float = 1.602176634e-19  # Factor de conversión de Joules a Electronvoltios


def calcular_fuerza_coulomb(q1: float, q2: float, distancia: float) -> float:
    """Calcula la fuerza electrostática de Coulomb entre dos cargas.

    Aplica la ley de Coulomb: F = k_e * (q1 * q2) / r^2.
    Una fuerza de valor negativo representa una fuerza atractiva (cargas de signo opuesto),
    y una fuerza de valor positivo representa una fuerza repulsiva (cargas del mismo signo).

    Args:
        q1: Carga de la partícula 1 en Coulombs.
        q2: Carga de la partícula 2 en Coulombs.
        distancia: Distancia de separación física en metros (debe ser >= 1e-15 m).

    Returns:
        Fuerza electrostática ejercida entre las cargas en Newtons (N).

    Raises:
        TypeError: Si alguno de los argumentos no es numérico (int o float).
        ValueError: Si la distancia es menor a la escala del femtómetro (1e-15 m),
            lo cual representa límites físicos y evita problemas numéricos de división por cero.
    """
    if not isinstance(q1, (int, float)) or not isinstance(q2, (int, float)) or not isinstance(distancia, (int, float)):
        raise TypeError("Todos los argumentos de entrada deben ser de tipo numérico (int o float).")
    
    # Límite físico: no podemos aproximar cargas a menos de un protón/neutrón
    # para cálculos clásicos sin colapsar las ecuaciones
    LIMITE_DISTANCIA: float = 1.0e-15  # 1 femtómetro
    if distancia < LIMITE_DISTANCIA:
        raise ValueError(
            f"La distancia ({distancia:.3e} m) es inferior al límite físico clásico de "
            f"{LIMITE_DISTANCIA:.3e} m (escala del femtómetro). Esto evita inestabilidad numérica."
        )

    # Cálculo explícito de la fuerza con precedencia correcta
    fuerza: float = K_COULOMB * (q1 * q2) / (distancia ** 2)
    return fuerza


def calcular_energia_bohr(n: int, z: int = 1) -> Dict[str, float]:
    """Calcula los niveles de energía de Bohr para un electrón en un átomo hidrogenoide.

    Utiliza la fórmula del modelo de Bohr basada en constantes fundamentales:
        E_n = - (m_e * e^4 * Z^2) / (8 * epsilon_0^2 * h^2 * n^2)

    Un átomo hidrogenoide es un átomo que contiene un único electrón (H, He+, Li2+, etc.).

    Args:
        n: Número cuántico principal. Debe ser un entero positivo (n >= 1).
        z: Número atómico (cantidad de protones). Debe ser un entero positivo (Z >= 1).

    Returns:
        Un diccionario con la energía calculada en dos unidades:
        - "joules": Energía del electrón en Joules (J).
        - "electronvoltios": Energía del electrón en electronvoltios (eV).

    Raises:
        TypeError: Si 'n' o 'z' no son de tipo entero (int).
        ValueError: Si 'n' o 'z' son menores a 1.
    """
    # Validación estricta de tipos
    if not isinstance(n, int):
        raise TypeError(f"El número cuántico principal 'n' debe ser entero, se recibió: {type(n).__name__}")
    if not isinstance(z, int):
        raise TypeError(f"El número atómico 'z' debe ser entero, se recibió: {type(z).__name__}")

    # Validación estricta de valores físicos permitidos
    if n < 1:
        raise ValueError(f"El número cuántico principal 'n' debe ser mayor o igual a 1. Recibido: {n}")
    if z < 1:
        raise ValueError(f"El número atómico 'z' debe ser mayor o igual a 1. Recibido: {z}")

    # Cálculo paso a paso para evitar errores de precedencia y overflow
    numerador: float = MASA_ELECTRON * (CARGA_ELEMENTAL ** 4) * (z ** 2)
    denominador: float = 8.0 * (PERMITIVIDAD_VACIO ** 2) * (CONSTANTE_PLANCK ** 2) * (n ** 2)
    
    energia_joules: float = - (numerador / denominador)
    energia_ev: float = energia_joules / JOULES_A_EV

    return {
        "joules": energia_joules,
        "electronvoltios": energia_ev
    }
```

---

### 🔍 Desglose Paso a Paso de `fisica_atomica.py`

* **Líneas 19-24 (Definición de Constantes CODATA)**: Definimos las constantes en formato de precisión flotante. Se emplea la notación científica literal `e` para representar potencias de 10 de base exponencial rápida de CPU (ej. `8.9875517923e9` es $8.9875517923 \times 10^9$).
* **Líneas 27-61 (Función `calcular_fuerza_coulomb`)**:
  - `isinstance(q1, (int, float))` (Línea 47): Valida que los tres argumentos numéricos de entrada sean enteros o flotantes antes de iniciar la computación aritmética. Si la verificación lógica falla, se lanza una excepción de tipo `TypeError` para alertar al sistema de control de la simulación.
  - **La validación del límite físico de distancia en femtómetros (Líneas 52-57)**: 
    - Un femtómetro ($1.0 \times 10^{-15}\text{ m}$) es la escala espacial típica del diámetro del núcleo de un átomo de hidrógeno. Por debajo de esta distancia, la repulsión nuclear fuerte y los efectos cuánticos de entrelazamiento impiden que los electrones sigan el modelo de Coulomb clásico.
    - Algorítmicamente, si `distancia` se acerca a cero, su cuadrado `distancia ** 2` se aproxima exponencialmente a cero (por ejemplo, a $10^{-30}$ o $10^{-32}$), lo cual puede desencadenar errores catastróficos de subdesbordamiento de bits (*underflow*) o, en el límite, una división por cero. El control con `ValueError` detiene el cálculo de forma controlada antes de violar las leyes de la física y de la matemática de punto flotante.
  - `fuerza = K_COULOMB * (q1 * q2) / (distancia ** 2)` (Línea 60): Python evalúa en primer lugar la exponenciación `distancia ** 2` debido a que tiene la prioridad más alta, seguido por la multiplicación y la división del término, de izquierda a derecha.
* **Líneas 64-108 (Función `calcular_energia_bohr`)**:
  - `isinstance(n, int)` e `isinstance(z, int)` (Líneas 86-89): Fuerza a que los números cuánticos principal $n$ y atómico $Z$ sean variables enteras estrictas. El modelo de Bohr postula que las órbitas de los electrones son estacionarias y discretas; por ende, un $n$ flotante (ej. $1.5$) carece por completo de sentido físico.
  - `numerador` y `denominador` (Líneas 98-99): Desglosar la ecuación compleja en dos variables independientes previene la introducción de errores sutiles en la jerarquía de los operadores. Nótese que `CARGA_ELEMENTAL ** 4` y `PERMITIVIDAD_VACIO ** 2` se ejecutan primero en cada subgrupo.
  - `energia_joules` (Línea 101): Multiplica el cociente por `-1`, representando que el electrón se halla ligado al potencial del núcleo del átomo.
  - `energia_ev = energia_joules / JOULES_A_EV` (Línea 102): Convierte los Joules a electronvoltios aplicando el factor de conversión ($1\text{ eV} = 1.602176634 \times 10^{-19}\text{ J}$).

---

### 🧪 Suite de Pruebas Unitarias Completa: `test_fisica_atomica.py`

Las simulaciones de nanotecnología operan en escalas espaciales y de energía extremadamente pequeñas. Probar estas operaciones aritméticas utilizando un marco de pruebas como **Pytest** garantiza la resiliencia y estabilidad del algoritmo.

```python
"""Suite de pruebas unitarias robusta para el módulo fisica_atomica.

Verifica la correctitud y precisión de los cálculos en escalas extremas
(Ångstroms, nanómetros), notación científica y control de excepciones.
"""

import math
import pytest
from fisica_atomica import (
    calcular_fuerza_coulomb,
    calcular_energia_bohr,
    CARGA_ELEMENTAL,
)

# =====================================================================
# PRUEBAS PARA LA FUERZA DE COULOMB
# =====================================================================

def test_fuerza_coulomb_escala_nanometro():
    """Verifica el cálculo de la fuerza electrostática a escala de 1 nanómetro."""
    q_sodio = CARGA_ELEMENTAL      # +1e (Ion Na+)
    q_cloro = -CARGA_ELEMENTAL     # -1e (Ion Cl-)
    distancia = 1e-9               # 1 nm
    
    # F = k_e * (e * -e) / r^2
    # F = 8.98755e9 * (-2.567e-38) / 1e-18 = -2.307e-10 N (Atracción)
    fuerza = calcular_fuerza_coulomb(q_sodio, q_cloro, distancia)
    
    assert fuerza < 0, "Las cargas opuestas deben atraerse (fuerza negativa)"
    assert math.isclose(fuerza, -2.307077e-10, rel_tol=1e-5), "El cálculo a escala de nanómetro no es preciso"


def test_fuerza_coulomb_escala_angstrom():
    """Verifica el cálculo de la fuerza electrostática a escala de 1 Angstrom (0.1 nm)."""
    q_proton = CARGA_ELEMENTAL
    q_electron = -CARGA_ELEMENTAL
    distancia = 1e-10              # 1 Angstrom
    
    # F = 8.98755e9 * (-2.567e-38) / 1e-20 = -2.307e-8 N
    fuerza = calcular_fuerza_coulomb(q_proton, q_electron, distancia)
    
    assert fuerza < 0
    assert math.isclose(fuerza, -2.307077e-8, rel_tol=1e-5), "El cálculo a escala de Angstrom no es preciso"


def test_fuerza_coulomb_repulsiva():
    """Verifica que cargas iguales produzcan una fuerza repulsiva (fuerza positiva)."""
    q1 = CARGA_ELEMENTAL
    q2 = CARGA_ELEMENTAL
    distancia = 2e-10              # 2 Angstroms
    
    fuerza = calcular_fuerza_coulomb(q1, q2, distancia)
    
    assert fuerza > 0, "Las cargas del mismo signo deben repelerse (fuerza positiva)"
    assert math.isclose(fuerza, 5.76769e-9, rel_tol=1e-5)


def test_fuerza_coulomb_limites_excepciones():
    """Comprueba el comportamiento ante valores de entrada no válidos o extremos."""
    # Distancia igual a cero (debe lanzar ValueError)
    with pytest.raises(ValueError) as excinfo:
        calcular_fuerza_coulomb(CARGA_ELEMENTAL, -CARGA_ELEMENTAL, 0.0)
    assert "inferior al límite físico clásico" in str(excinfo.value)

    # Distancia extremadamente pequeña (< 1 femtómetro, ej: 1e-16 m)
    with pytest.raises(ValueError):
        calcular_fuerza_coulomb(CARGA_ELEMENTAL, -CARGA_ELEMENTAL, 1e-16)

    # Tipos no válidos (debe lanzar TypeError)
    with pytest.raises(TypeError):
        # q1 es str en lugar de float
        calcular_fuerza_coulomb("carga", -CARGA_ELEMENTAL, 1e-9)  # type: ignore

    with pytest.raises(TypeError):
        # distancia es str
        calcular_fuerza_coulomb(CARGA_ELEMENTAL, -CARGA_ELEMENTAL, "1 nm")  # type: ignore


# =====================================================================
# PRUEBAS PARA LOS NIVELES DE ENERGÍA DE BOHR
# =====================================================================

def test_energia_bohr_hidrogeno_estado_fundamental():
    """Verifica que para Z=1 y n=1 la energía sea ~-13.6 eV (~-2.18e-18 J)."""
    energia = calcular_energia_bohr(n=1, z=1)
    
    # Comprobar en eV (Valor esperado ~-13.60569 eV)
    assert math.isclose(energia["electronvoltios"], -13.60569, rel_tol=1e-5)
    # Comprobar en Joules (Valor esperado ~-2.179872e-18 J)
    assert math.isclose(energia["joules"], -2.179872e-18, rel_tol=1e-5)


def test_energia_bohr_niveles_excitados():
    """Verifica la tendencia de la energía en n=2 y n=3 para hidrógeno."""
    e1 = calcular_energia_bohr(n=1, z=1)["electronvoltios"]
    e2 = calcular_energia_bohr(n=2, z=1)["electronvoltios"]
    e3 = calcular_energia_bohr(n=3, z=1)["electronvoltios"]
    
    # E_n = E_1 / n^2. E2 = -13.60569 / 4 = -3.40142 eV
    assert math.isclose(e2, -3.40142, rel_tol=1e-5)
    # E3 = -13.60569 / 9 = -1.51174 eV
    assert math.isclose(e3, -1.51174, rel_tol=1e-5)
    
    # La energía debe aumentar (hacerse menos negativa, más cercana a cero)
    assert e1 < e2 < e3 < 0.0


def test_energia_bohr_atomos_hidrogenoides():
    """Verifica la energía para Helio ionizado (Z=2) y Litio doblemente ionizado (Z=3)."""
    # Helio+ (Z=2, n=1): E = -13.60569 * 2^2 / 1^2 = -54.42277 eV
    e_he = calcular_energia_bohr(n=1, z=2)["electronvoltios"]
    assert math.isclose(e_he, -54.42277, rel_tol=1e-5)
    
    # Litio2+ (Z=3, n=2): E = -13.60569 * 3^2 / 2^2 = -30.61280 eV
    e_li = calcular_energia_bohr(n=2, z=3)["electronvoltios"]
    assert math.isclose(e_li, -30.61280, rel_tol=1e-5)


def test_energia_bohr_excepciones():
    """Comprueba el control de excepciones de tipo y valor para la ecuación de Bohr."""
    # n no es entero (debe lanzar TypeError)
    with pytest.raises(TypeError):
        calcular_energia_bohr(n=1.5, z=1)  # type: ignore
        
    # z no es entero
    with pytest.raises(TypeError):
        calcular_energia_bohr(n=1, z="1")  # type: ignore

    # n < 1 (debe lanzar ValueError)
    with pytest.raises(ValueError):
        calcular_energia_bohr(n=0, z=1)

    with pytest.raises(ValueError):
        calcular_energia_bohr(n=-2, z=1)

    # z < 1 (debe lanzar ValueError)
    with pytest.raises(ValueError):
        calcular_energia_bohr(n=1, z=0)
        
    with pytest.raises(ValueError):
        calcular_energia_bohr(n=1, z=-1)
```

---

### 🔍 Desglose Paso a Paso de la Suite de Pruebas Unitarias

* **Líneas 19-31 (`test_fuerza_coulomb_escala_nanometro`)**: Define una prueba a escala molecular de un enlace iónico (Na+ y Cl-) separados a una distancia física de $1\text{ nm}$ ($10^{-9}\text{ m}$).
* **La Importancia de `math.isclose()` en Simulaciones Científicas**:
  En computación cuántica y nanotecnología, no es viable utilizar el operador de igualdad directa `==` para evaluar números reales (flotantes). La memoria almacena los números fraccionarios en base binaria (Estándar IEEE 754), provocando pequeños errores de redondeo decimal. Por ejemplo, en Python `0.1 + 0.2 == 0.3` resulta en `False`, ya que la suma binaria produce exactamente `0.30000000000000004`.
  - La función `math.isclose(a, b, rel_tol)` evalúa si la diferencia absoluta entre `a` y `b` se halla dentro de un margen relativo definido:
    
    $$|a - b| \le \text{rel\_tol} \times \max(|a|, |b|)$$
    
  - Al especificar `rel_tol=1e-5`, exigimos que ambos resultados coincidan con una precisión mínima del $99.999\%$ (tolerancia relativa de cinco cifras significativas), suficiente para validar cálculos cuánticos.
* **Líneas 58-77 (Validación de Excepciones)**:
  - `with pytest.raises(ValueError) as excinfo:` (Línea 61): Este bloque de control le indica a Pytest que el código situado debajo **debe** fallar arrojando una excepción `ValueError`. Si la función se ejecuta con éxito o falla con una excepción diferente, la prueba unitaria fallará.
  - `assert "inferior al límite físico clásico" in str(excinfo.value)` (Línea 63): Inspecciona el mensaje de error textual devuelto por el objeto de excepción (`excinfo.value`), garantizando que la causa del fallo sea exactamente la validación física en femtómetros que definimos en el módulo de producción.

---

# 3.6 Banco de Preguntas de Examen de Opción Múltiple (15 Preguntas)

A continuación se despliega el banco de reactivos para evaluación teórica, diseñado con distractores complejos basados en errores comunes de programación y modelado físico:

### Pregunta 1
**En Python, el operador `is` evalúa si dos variables son idénticas en memoria, mientras que `==` compara sus valores. Si ejecutamos el siguiente fragmento:**
```python
import copy
a = [[1, 2], [3, 4]]
b = copy.copy(a)
```
**¿Cuál de las siguientes afirmaciones es VERDADERA?**
*   A) `a is b` evalúa como `True` y `a[0] is b[0]` evalúa como `True`.
*   B) `a is b` evalúa como `False` y `a[0] is b[0]` evalúa como `False`.
*   C) `a is b` evalúa como `False` and `a[0] is b[0]` evalúa como `True`.
*   D) `a is b` evalúa como `True` y `a[0] is b[0]` evalúa como `False`.

**Justificación Didáctica**:
*   **Respuesta Correcta: C**. `copy.copy` realiza una copia superficial. Esto significa que crea una nueva lista para el contenedor externo (por lo que `a` y `b` tienen diferentes direcciones de memoria y `a is b` es `False`). Sin embargo, no duplica las sublistas internas, sino que copia sus referencias. Por tanto, las sublistas internas son compartidas y `a[0] is b[0]` evalúa como `True`.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque `a` y `b` no comparten el contenedor externo principal. La copia superficial crea un nuevo objeto para el contenedor de la lista de primer nivel.
    *   **B es incorrecta** porque `a[0] is b[0]` no es `False`. Al ser una copia superficial, las listas anidadas no se replican en memoria; se copian los mismos punteros que apuntan a los subobjetos de `a`.
    *   **D es incorrecta** debido a que invierte ambos estados de verdad. El contenedor de primer nivel es diferente, mientras que los internos son el mismo objeto físico.

---

### Pregunta 2
**El modelo de optimización de CPython cuenta con un mecanismo llamado "Integer Caching" (caché de enteros pequeños). Si ejecutamos en consola interactiva:**
```python
x = 256
y = 256
z = 257
w = 257
print(x is y, z is w)
```
**¿Cuál será la salida en consola en la implementación estándar de CPython?**
*   A) `True True`
*   B) `True False`
*   C) `False True`
*   D) `False False`

**Justificación Didáctica**:
*   **Respuesta Correcta: B**. CPython precarga e indexa en memoria fija de solo lectura todos los objetos enteros en el rango cerrado de `[-5, 256]`. Por ende, cualquier asignación de variables con valores dentro de este rango apuntará exactamente al mismo objeto compartido (dando `x is y -> True`). El valor `257` se encuentra fuera de este rango de caché, lo que causa que Python asigne dos objetos enteros independientes en memoria Heap para `z` y `w` (dando `z is w -> False`).
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque considera que el caché de enteros es infinito, lo cual consumiría memoria de forma ineficiente. `257` genera objetos distintos.
    *   **C es incorrecta** porque asume erróneamente que `256` genera dos objetos independientes y que `257` se almacena en caché.
    *   **D es incorrecta** dado que niega el funcionamiento del mecanismo de optimización para enteros menores o iguales a `256`.

---

### Pregunta 3
**Dada la siguiente expresión matemática que modela la aceleración de un electrón en un campo eléctrico uniforme: $a = \frac{e \cdot E}{m_e}$. ¿Cuál es la forma algorítmica explícita y sintácticamente correcta de escribirla en Python respetando la precedencia de operadores y las convenciones PEP 8?**
*   A) `aceleracion = CARGA_ELEMENTAL * campo_electrico / MASA_ELECTRON`
*   B) `Aceleracion = cargaElemental * CampoElectrico / MasaElectron`
*   C) `aceleracion = CARGA_ELEMENTAL * (campo_electrico / MASA_ELECTRON)`
*   D) `ACELERACION = CARGA_ELEMENTAL * CAMPO_ELECTRICO / MASA_ELECTRON`

**Justificación Didáctica**:
*   **Respuesta Correcta: A**. Esta opción cumple estrictamente con el estándar PEP 8: las constantes físicas científicas van en mayúsculas sostenidas (`CARGA_ELEMENTAL`, `MASA_ELECTRON`), la variable calculada va en minúsculas (`aceleracion`), y el cálculo `*` y `/` se evalúa de izquierda a derecha de forma eficiente sin requerir paréntesis redundantes.
*   *Análisis de Distractores*:
    *   **B es incorrecta** porque utiliza la notación de variables en camelCase (`cargaElemental`, `CampoElectrico`), la cual viola las normas de estilo PEP 8 para Python y nombra de forma incorrecta las constantes físicas.
    *   **C es incorrecta** porque introduce paréntesis de agrupamiento redundantes en `(campo_electrico / MASA_ELECTRON)`. Aunque matemáticamente es equivalente, entorpece la legibilidad del código.
    *   **D es incorrecta** porque define la variable de salida en mayúsculas sostenidas (`ACELERACION`). Las variables comunes que cambian a lo largo del flujo del programa no deben nombrarse como constantes.

---

### Pregunta 4
**Considere la siguiente expresión lógica evaluada por Python en una sola línea:**
```python
resultado = False and (10 / 0 == 0) or True
```
**¿Qué sucede al ejecutar esta línea de código y cuál es el valor final de la variable `resultado`?**
*   A) Lanza un error de ejecución `ZeroDivisionError` debido a la presencia de `10 / 0`.
*   B) Se ejecuta correctamente sin errores y `resultado` toma el valor de `False`.
*   C) Se ejecuta correctamente sin errores y `resultado` toma el valor de `True`.
*   D) Lanza un error de tipo `TypeError` porque no se puede comparar una división con un booleano.

**Justificación Didáctica**:
*   **Respuesta Correcta: C**. Python evalúa la expresión lógica de izquierda a derecha aplicando la regla del cortocircuito lógico.
    1. Evalúa el término de la conjunción: `False and (10 / 0 == 0)`.
    2. Como el primer operando de `and` es `False`, la expresión de la conjunción hace cortocircuito y se evalúa como `False` de inmediato, sin llegar a ejecutar el segundo operando `(10 / 0 == 0)`. Esto evita el error de división por cero.
    3. Luego evalúa el operador `or`: `False or True`. Al ser uno de los operandos `True`, el resultado final de la expresión es `True`.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque asume que Python evalúa toda la expresión de forma secuencial sin aplicar el comportamiento de cortocircuito lógico.
    *   **B es incorrecta** porque, aunque predice correctamente que no hay error, define erróneamente el valor final de la disyunción como `False`.
    *   **D es incorrecta** dado que la división se resolvería teóricamente como un flotante antes de la comparación relacional `==`, por lo que no causaría un error de tipo, y el cortocircuito evita su ejecución de todos modos.

---

### Pregunta 5
**En el desarrollo de un algoritmo cuántico, se requiere almacenar un conjunto de niveles de energía invariantes (que no deben ser modificados). ¿Cuál es la estructura de datos integrada en Python recomendada por su naturaleza de inmutabilidad y eficiencia de indexación?**
*   A) `list`
*   B) `dict`
*   C) `set`
*   D) `tuple`

**Justificación Didáctica**:
*   **Respuesta Correcta: D**. Las tuplas (`tuple`) son secuencias ordenadas de datos de naturaleza **inmutable**. Esto garantiza que los niveles de energía atómica no puedan ser sobrescritos por error durante la ejecución del programa, y su estructura interna optimiza el acceso por índice en memoria de solo lectura.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque las listas (`list`) son mutables por definición. Si se utilizan para constantes o valores de referencia estables, corren el riesgo de ser modificadas in-situ.
    *   **B es incorrecta** porque los diccionarios (`dict`) son estructuras de mapeo clave-valor altamente mutables, no estructuradas para representar secuencias ordenadas inmutables sencillas.
    *   **C es incorrecta** porque los conjuntos (`set`) son mutables y no tienen un orden indexado, imposibilitando el acceso directo a un nivel de energía específico por su índice orbital.

---

### Pregunta 6
**Al realizar operaciones matemáticas con números flotantes a escala cuántica (como la constante de Planck reducida), ¿cuál es el motivo principal por el que se prefiere usar `math.isclose(a, b, rel_tol=1e-5)` sobre `a == b` en las pruebas unitarias?**
*   A) `math.isclose` convierte internamente las variables a enteros de 128 bits para una precisión absoluta.
*   B) Los números de punto flotante en Python están sujetos a imprecisiones físicas de redondeo binario (IEEE 754).
*   C) El operador `==` consume más memoria RAM en la CPU del sistema que la función `math.isclose`.
*   D) `math.isclose` redondea ambos números al entero más cercano antes de realizar la comparación.

**Justificación Didáctica**:
*   **Respuesta Correcta: B**. Las computadoras no representan fracciones decimales de forma matemática perfecta. El estándar IEEE 754 de punto flotante utiliza potencias binarias finitas para aproximar los números reales. Esto genera pequeños errores acumulativos de precisión que hacen inviable comparar flotantes mediante `==`. `math.isclose` resuelve esto admitiendo una tolerancia relativa paramétrica.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque Python no maneja tipos de datos nativos enteros de 128 bits para conversiones rápidas en la biblioteca estándar de matemáticas.
    *   **C es incorrecta** debido a que la diferencia en consumo de memoria o ciclos de CPU entre ambos métodos es insignificante y no justifica la decisión arquitectónica en pruebas unitarias.
    *   **D es incorrecta** porque comparar números aproximados a enteros desvirtuaría los cálculos a nanoescala, donde las diferencias flotantes pequeñas (como $10^{-34}$) son críticas.

---

### Pregunta 7
**¿Cuál de las siguientes expresiones aritméticas en Python retornará un valor flotante (`float`) a pesar de operar únicamente con números de tipo entero (`int`)?**
*   A) `2 ** 3`
*   B) `10 // 3`
*   C) `15 / 5`
*   D) `12 % 5`

**Justificación Didáctica**:
*   **Respuesta Correcta: C**. En Python 3, el operador de división real o clásica `/` siempre retorna un resultado de tipo de punto flotante (`float`), incluso si el dividendo es exactamente divisible por el divisor (en este caso, `15 / 5` devuelve `3.0`).
*   *Análisis de Distractores*:
    *   **A es incorrecta** ya que el operador de exponenciación `**` aplicado a base y exponente enteros retorna un valor entero (`2 ** 3` devuelve el entero `8`).
    *   **B es incorrecta** debido a que el operador `//` ejecuta la división entera (truncada hacia el suelo), retornando un valor entero (`10 // 3` devuelve el entero `3`).
    *   **D es incorrecta** porque el operador módulo `%` calcula el residuo entero de la división de enteros, devolviendo un entero (`12 % 5` devuelve el entero `2`).

---

### Pregunta 8
**Si intentamos ejecutar la siguiente secuencia de instrucciones en la consola de Python:**
```python
simulacion = (2.3, 4.5, [0.0, 1.0])
simulacion[2][0] = 9.9
```
**¿Qué comportamiento se observará en el intérprete?**
*   A) Se lanza un error `TypeError: 'tuple' object does not support item assignment` de forma inmediata.
*   B) La tupla se modifica correctamente quedando como `(2.3, 4.5, [9.9, 1.0])`.
*   C) Python crea una nueva tupla automáticamente en otra dirección de memoria y borra la anterior.
*   D) Lanza un error de valor `ValueError` porque no se pueden anidar listas dentro de tuplas.

**Justificación Didáctica**:
*   **Respuesta Correcta: B**. Aunque la tupla es una estructura inmutable, almacena en su tercer elemento la dirección de memoria de una lista (que es mutable). Modificar un elemento interno de la lista (`simulacion[2][0] = 9.9`) altera el contenido interno del objeto lista, pero **no altera** la dirección de memoria del objeto lista en sí. Dado que la tupla mantiene intacta la referencia al objeto lista, la operación es perfectamente válida en Python.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque no estamos modificando la tupla de forma directa (por ejemplo, haciendo `simulacion[2] = 9.9`). La tupla no sufre alteración en sus referencias directas.
    *   **C es incorrecta** dado que Python no crea de forma implícita copias ni reasignaciones en la memoria para estructuras mixtas sin una instrucción directa del desarrollador.
    *   **D es incorrecta** porque es completamente legal en Python anidar cualquier tipo de objeto mutable dentro de una estructura inmutable.

---

### Pregunta 9
**¿Cuál es la salida de consola de la siguiente línea de código en Python?**
```python
print(2 + 3 * 4 ** 2 // 2)
```
**¿Qué concepto de programación justifica esta salida?**
*   A) La salida es `40` y se justifica por la evaluación lineal estricta de izquierda a derecha.
*   B) La salida es `26` y se justifica por la precedencia: primero la potencia `**`, luego la multiplicación `*` y división entera `//`, y finalmente la suma `+`.
*   C) La salida es `160` y se justifica por la precedencia: primero la suma `+`, luego la potencia y la división.
*   D) La salida es `32` y se justifica por la evaluación directa de derecha a izquierda.

**Justificación Didáctica**:
*   **Respuesta Correcta: B**. Siguiendo la tabla de precedencia de operadores:
    1. Se calcula la potencia: `4 ** 2` que resulta en `16`. La expresión queda: `2 + 3 * 16 // 2`.
    2. Al tener la misma prioridad la multiplicación `*` y la división entera `//`, se evalúan de izquierda a derecha:
       - `3 * 16` resulta en `48`.
       - `48 // 2` resulta en `24`.
    3. Finalmente se realiza la suma: `2 + 24` que resulta en el entero `26`.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque evaluar linealmente daría: `2 + 3 = 5`, `5 * 4 = 20`, `20 ** 2 = 400`, `400 // 2 = 200`.
    *   **C es incorrecta** porque viola las reglas estándar de prioridad algebraica y computacional al evaluar la suma en primer lugar.
    *   **D es incorrecta** porque no corresponde al resultado matemático de evaluar la expresión con la precedencia definida en Python.

---

### Pregunta 10
**Considere la función `calcular_fuerza_coulomb` definida anteriormente. Si la invocamos enviando los siguientes parámetros:**
```python
calcular_fuerza_coulomb(CARGA_ELEMENTAL, -CARGA_ELEMENTAL, 5e-16)
```
**¿Qué comportamiento presentará el algoritmo?**
*   A) Retorna un valor de fuerza electrostática muy grande y negativo de forma correcta.
*   B) Lanza una excepción de tipo `TypeError` porque el valor de la distancia está en notación científica.
*   C) Lanza una excepción de tipo `ValueError` debido a que la distancia de $0.5\text{ fm}$ es inferior al límite de $1.0\text{ fm}$.
*   D) Entra en un bucle infinito al intentar dividir por un flotante extremadamente pequeño.

**Justificación Didáctica**:
*   **Respuesta Correcta: C**. La distancia proporcionada (`5e-16` m, que equivale a $0.5$ femtómetros) es menor que el límite clásico inferior establecido en el código (`1.0e-15` m). Por lo tanto, la validación interna `if distancia < LIMITE_DISTANCIA:` evalúa como `True` y lanza un error `ValueError` para advertir del colapso del modelo clásico de Coulomb.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque asume que la función calcula la fuerza sin validar los límites físicos, lo que llevaría a una inestabilidad de la física clásica en el núcleo.
    *   **B es incorrecta** porque la notación científica literal (ej. `5e-16`) es interpretada de forma nativa por Python como un número real de tipo `float` válido.
    *   **D es incorrecta** porque una operación aritmética común no genera bucles infinitos en la ejecución de la CPU; a lo sumo arrojaría un desbordamiento numérico instantáneo si no hubiera validación.

---

### Pregunta 11
**En Python, los identificadores de variables no pueden comenzar con ciertos caracteres. ¿Cuál de los siguientes es un identificador de variable VÁLIDO según el intérprete de Python?**
*   A) `3er_nivel_energia`
*   B) `lambda`
*   C) `_energia_potencial`
*   D) `constante-planck`

**Justificación Didáctica**:
*   **Respuesta Correcta: C**. Los identificadores en Python pueden comenzar con una letra o con un guion bajo (`_`). El identificador `_energia_potencial` es sintácticamente válido y se utiliza habitualmente en programación para denotar variables internas o privadas en una clase o módulo.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque los nombres de las variables no pueden comenzar con un carácter numérico (`3`).
    *   **B es incorrecta** porque `lambda` es una palabra reservada del lenguaje Python (utilizada para definir funciones anónimas) y no puede ser empleada como un identificador común.
    *   **D es incorrecta** porque contiene el guion intermedio (`-`), el cual es interpretado por el compilador como el operador aritmético de sustracción (resta), rompiendo la sintaxis.

---

### Pregunta 12
**¿Qué se entiende por "mutabilidad in-situ" en la gestión de memoria de colecciones de datos en Python?**
*   A) La capacidad de redimensionar la memoria RAM asignada al proceso del sistema de forma dinámica.
*   B) La facultad de cambiar el valor de los elementos internos de un objeto sin que cambie su dirección física de memoria `id()`.
*   C) La propiedad que permite a los tipos de datos cambiar de float a int de manera automática en tiempo de cálculo.
*   D) La duplicación del objeto contenedor en una nueva celda de memoria cada vez que se añade un elemento.

**Justificación Didáctica**:
*   **Respuesta Correcta: B**. La mutabilidad in-situ (o modificación en el lugar) significa que las colecciones mutables (como las listas) permiten que sus celdas internas apunten a nuevos objetos, mientras que la lista contenedora principal sigue residiendo en la misma dirección de memoria RAM (su `id()` no varía).
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque la gestión física del direccionamiento del proceso de memoria es controlada por el sistema operativo y no es a lo que se refiere la mutabilidad de datos de Python.
    *   **C es incorrecta** porque describe el concepto de conversión de tipos dinámicos o coerción de tipos, no la mutabilidad física del contenedor de memoria.
    *   **D es incorrecta** porque esa descripción corresponde más al comportamiento al intentar emular mutabilidad en estructuras inmutables (donde sí se crea un objeto nuevo).

---

### Pregunta 13
**Al simular la órbita de Bohr, calculamos la energía en Joules y deseamos convertirla a Electronvoltios (eV). Si tenemos la variable `energia_j = -2.179872e-18` y la constante `JOULES_A_EV = 1.602176634e-19`. ¿Qué operación algorítmica realiza la conversión matemática correcta?**
*   A) `energia_ev = energia_j * JOULES_A_EV`
*   B) `energia_ev = energia_j / JOULES_A_EV`
*   C) `energia_ev = JOULES_A_EV / energia_j`
*   D) `energia_ev = energia_j ** JOULES_A_EV`

**Justificación Didáctica**:
*   **Respuesta Correcta: B**. Dado que un electronvoltio equivale a $1.602176634 \times 10^{-19}$ Joules, para pasar una cantidad expresada en la unidad más grande (Joules) a la unidad de escala cuántica (eV), debemos dividir la energía de Joules entre la constante de conversión.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque multiplicar por una constante del orden de $10^{-19}$ resultaría en un valor infinitesimal (cercano a $10^{-37}$), lo cual es físicamente incoherente para la energía cuántica en eV (que debe rondar los $-13.6\text{ eV}$).
    *   **C es incorrecta** porque invierte los términos del cociente, calculando cuántos Joules atómicos caben en un nivel de energía individual.
    *   **D es incorrecta** porque aplicar exponenciación cuántica con bases tan pequeñas no representa ningún modelo físico real de conversión.

---

### Pregunta 14
**Considere la siguiente prueba unitaria escrita con Pytest:**
```python
def test_operacion():
    with pytest.raises(TypeError):
        res = 5 + "10"
```
**¿Cómo interpreta Pytest esta prueba y cuál será el veredicto del reporte de testing?**
*   A) La prueba falla porque sumar un entero y una cadena de texto es un error de sintaxis que Pytest no puede procesar.
*   B) La prueba pasa exitosamente porque el bloque de código arroja exactamente la excepción `TypeError`.
*   C) La prueba falla porque el programador debe capturar la excepción con un bloque `try-except` tradicional.
*   D) La prueba pasa exitosamente porque la suma implícitamente convierte la cadena `"10"` al entero `10` dando `15`.

**Justificación Didáctica**:
*   **Respuesta Correcta: B**. En Python, realizar la operación de adición entre un entero (`int`) y una cadena (`str`) lanza un `TypeError` en tiempo de ejecución. Dado que la prueba unitaria utiliza el manejador de contexto `with pytest.raises(TypeError):`, le indica a Pytest que el error es esperado. Como la excepción ocurre, Pytest determina que el comportamiento bajo prueba es seguro ante entradas incorrectas y marca el test como exitoso (PASSED).
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque esto no es un error de sintaxis (sintaxis inválida detectada al parsear el archivo), sino un error de tipo en tiempo de ejecución, el cual Pytest procesa sin ningún inconveniente.
    *   **C es incorrecta** porque en testing automatizado, la aserción y control de excepciones mediante gestores de contexto de Pytest es la práctica de desarrollo estándar y no requiere de bloques try-except manuales.
    *   **D es incorrecta** porque Python es un lenguaje fuertemente tipado y jamás realiza la coerción implícita de una cadena a un tipo numérico durante operaciones de suma.

---

### Pregunta 15
**Si declaramos la variable `a = [1, 2, 3]` y posteriormente realizamos la asignación `b = a`. Si modificamos el valor del segundo elemento mediante `b[1] = 99`, ¿qué valores tendrán las variables `a` y `b` al finalizar la ejecución?**
*   A) `a` tendrá `[1, 2, 3]` y `b` tendrá `[1, 99, 3]`.
*   B) `a` tendrá `[1, 99, 3]` y `b` tendrá `[1, 2, 3]`.
*   C) Tanto `a` como `b` apuntarán al mismo objeto cuyo valor es `[1, 99, 3]`.
*   D) Python lanzará un error indicando que las listas son objetos inmutables que no admiten reasignación de elementos individuales.

**Justificación Didáctica**:
*   **Respuesta Correcta: C**. La instrucción `b = a` realiza una asignación por referencia directa. Ambas variables apuntan exactamente a la misma dirección física de memoria RAM en el Heap. Cualquier cambio realizado sobre los elementos de `b` alterará el objeto compartido en memoria, de modo que al consultar `a` o `b`, ambas variables retornarán el mismo contenido modificado `[1, 99, 3]`.
*   *Análisis de Distractores*:
    *   **A es incorrecta** porque asume erróneamente que la asignación simple `=` realiza una copia profunda independiente de los elementos.
    *   **B es incorrecta** ya que invierte el comportamiento, presumiendo que la lista original se altera pero la copia de referencia no.
    *   **D es incorrecta** debido a que las listas en Python son colecciones dinámicas y mutables por definición, admitiendo la asignación y modificación in-situ de elementos por índice de forma directa.

---

# 3.7 Problemas Numéricos y Lógicos Resueltos

A continuación se plantean y resuelven a detalle tres problemas prácticos típicos de las áreas de física atómica y algoritmia científica.

### Problema 1: Cálculo de Fuerza de Coulomb entre dos protones en un Núcleo Atómico
**Enunciado**: Calcule la fuerza electrostática de repulsión que experimentan dos protones separados a una distancia de $2.0 \text{ Ångstroms}$ ($2.0 \times 10^{-10}\text{ m}$) dentro del núcleo de una molécula y exprese el cálculo mediante el desarrollo paso a paso del código Python que lo resuelve.

**Desglose Físico y Matemático**:
La Ley de Coulomb es:

$$F = k_e \frac{q_1 \cdot q_2}{r^2}$$

Datos:
*   $k_e = 8.9875517923 \times 10^9 \text{ N}\cdot\text{m}^2/\text{C}^2$
*   $q_1 = q_2 = e = 1.602176634 \times 10^{-19} \text{ C}$ (Carga elemental positiva del protón)
*   $r = 2.0 \times 10^{-10} \text{ m}$

**Resolución Matemática Paso a Paso**:
1. Multiplicación de las cargas:
   $$q_1 \cdot q_2 = (1.602176634 \times 10^{-19}\text{ C})^2 \approx 2.56697 \times 10^{-38} \text{ C}^2$$
2. Elevación de la distancia al cuadrado:
   $$r^2 = (2.0 \times 10^{-10}\text{ m})^2 = 4.0 \times 10^{-20} \text{ m}^2$$
3. Dividir el producto de las cargas entre el cuadrado de la distancia:
   $$\frac{q_1 \cdot q_2}{r^2} = \frac{2.56697 \times 10^{-38}}{4.0 \times 10^{-20}} \approx 6.417425 \times 10^{-19} \text{ C}^2/\text{m}^2$$
4. Multiplicación por la constante de Coulomb ($k_e$):
   $$F = (8.9875517923 \times 10^9) \times (6.417425 \times 10^{-19}) \approx 5.76769 \times 10^{-9} \text{ Newtons}$$

El signo es positivo, indicando una **fuerza repulsiva** (cargas de igual signo).

**Traducción y Solución en Código Python**:
```python
# Definición de variables con PEP 8
K_COULOMB = 8.9875517923e9
CARGA_ELEMENTAL = 1.602176634e-19
distancia = 2.0e-10  # 2 Ångstroms en metros

# Cálculo aplicando precedencia estricta
fuerza_coulomb = K_COULOMB * (CARGA_ELEMENTAL * CARGA_ELEMENTAL) / (distancia ** 2)

# Salida formateada
print(f"Fuerza resultante: {fuerza_coulomb:.5e} N")
# Salida esperada: Fuerza resultante: 5.76769e-09 N
```

---

### Problema 2: Cálculo del Nivel de Energía de Bohr para un Electrón de Helio Ionizado
**Enunciado**: El Helio ionizado ($He^+$) es un átomo hidrogenoide con número atómico $Z=2$ (contiene dos protones en el núcleo y un solo electrón orbital). Calcule el nivel de energía del electrón en su órbita excitada $n=2$ utilizando la constante de Bohr y exprese los pasos computacionales correspondientes en Python.

**Desglose Físico y Matemático**:
La ecuación cuántica de la energía de Bohr es:

$$E_n = - \frac{m_e \cdot e^4 \cdot Z^2}{8 \cdot \epsilon_0^2 \cdot h^2 \cdot n^2}$$

Datos del problema:
*   $Z = 2$ (Número atómico del Helio)
*   $n = 2$ (Segundo nivel de energía cuántica)
*   $m_e = 9.1093837015 \times 10^{-31}\text{ kg}$
*   $e = 1.602176634 \times 10^{-19}\text{ C}$
*   $\epsilon_0 = 8.8541878128 \times 10^{-12}\text{ F/m}$
*   $h = 6.62607015 \times 10^{-34}\text{ J}\cdot\text{s}$

**Resolución Matemática Paso a Paso**:
1. Calcular el numerador:
   $$\text{Numerador} = m_e \cdot e^4 \cdot Z^2 = (9.1093837015 \times 10^{-31}) \times (1.602176634 \times 10^{-19})^4 \times (2)^2$$
   $$e^4 \approx 6.58935 \times 10^{-76} \text{ C}^4$$
   $$\text{Numerador} \approx (9.1093837015 \times 10^{-31}) \times (6.58935 \times 10^{-76}) \times 4 \approx 2.400977 \times 10^{-105}$$
2. Calcular el denominador:
   $$\text{Denominador} = 8.0 \cdot \epsilon_0^2 \cdot h^2 \cdot n^2$$
   $$\epsilon_0^2 \approx 7.83966 \times 10^{-23} \text{ F}^2/\text{m}^2$$
   $$h^2 \approx 4.39048 \times 10^{-67} \text{ J}^2\cdot\text{s}^2$$
   $$n^2 = 4$$
   $$\text{Denominador} = 8.0 \times (7.83966 \times 10^{-23}) \times (4.39048 \times 10^{-67}) \times 4 \approx 1.101487 \times 10^{-88}$$
3. Cociente de la energía en Joules:
   $$E_2 = - \frac{2.400977 \times 10^{-105}}{1.101487 \times 10^{-88}} \approx -2.179872 \times 10^{-17} \text{ Joules}$$
4. Conversión a electronvoltios ($\text{eV}$):
   $$E_2 \text{ (eV)} = \frac{-2.179872 \times 10^{-17} \text{ J}}{1.602176634 \times 10^{-19} \text{ J/eV}} \approx -136.0569 \text{ eV}$$
   *(Nota: Como $E_n = E_1 \cdot \frac{Z^2}{n^2}$, y para hidrógeno $E_1 \approx -13.6\text{ eV}$, para $He^+$ con $Z=2, n=2$ tenemos $E_2 = -13.6 \times \frac{4}{4} = -13.6\text{ eV}$. El cálculo detallado utilizando las constantes físicas extendidas confirma el rigor del modelo cuántico)*.

**Traducción y Solución en Código Python**:
```python
# Constantes físicas CODATA
MASA_ELECTRON = 9.1093837015e-31
CARGA_ELEMENTAL = 1.602176634e-19
PERMITIVIDAD_VACIO = 8.8541878128e-12
CONSTANTE_PLANCK = 6.62607015e-34
JOULES_A_EV = 1.602176634e-19

# Datos de la órbita del Helio Ionizado
n_quantum = 2
z_atomic = 2

# Computación algorítmica por partes
num = MASA_ELECTRON * (CARGA_ELEMENTAL ** 4) * (z_atomic ** 2)
den = 8.0 * (PERMITIVIDAD_VACIO ** 2) * (CONSTANTE_PLANCK ** 2) * (n_quantum ** 2)

energia_j = - (num / den)
energia_ev = energia_j / JOULES_A_EV

print(f"Energía en Joules: {energia_j:.6e} J")
print(f"Energía en eV: {energia_ev:.4f} eV")
# Salida esperada:
# Energía en Joules: -2.179872e-18 J
# Energía en eV: -13.6057 eV
```

---

### Problema 3: Evaluación Lógica con Cortocircuitos de Expresiones Booleanas Complejas
**Enunciado**: Analice y determine paso a paso el resultado de la siguiente expresión booleana en Python. Considere las prioridades de precedencia de operadores lógicos, relacionales y aritméticos:

```python
x = 10
y = 20
z = 0

resultado = (x + 10 == y or y / z > 2) and not (z != 0 and x / z > 1)
```

**Desglose Algorítmico Paso a Paso**:
1.  **Evaluación de los paréntesis internos de izquierda a derecha**:
    *   Primer paréntesis: `(x + 10 == y or y / z > 2)`.
        *   Evaluamos la expresión aritmética: `x + 10` se convierte en `10 + 10 = 20`.
        *   Evaluamos la comparación relacional: `20 == y` es `20 == 20`, lo cual da `True`.
        *   La expresión interna queda como: `True or y / z > 2`.
        *   **Mecanismo de Cortocircuito en `or`**: Como el primer elemento de la disyunción es `True`, Python detiene la evaluación de este paréntesis de inmediato. Ignora el término `y / z > 2`, evitando así un error fatal `ZeroDivisionError` debido a la división entre `z` (que vale `0`).
        *   Resultado del primer paréntesis: `True`.
    *   Segundo paréntesis: `(z != 0 and x / z > 1)`.
        *   Evaluamos la primera comparación relacional: `z != 0` es `0 != 0`, lo cual es `False`.
        *   La expresión interna queda como: `False and x / z > 1`.
        *   **Mecanismo de Cortocircuito en `and`**: Como el primer elemento de la conjunción es `False`, Python hace cortocircuito y detiene la evaluación. Ignora el término `x / z > 1` (evitando nuevamente una división por cero).
        *   Resultado del segundo paréntesis: `False`.
2.  **Sustitución de los paréntesis en la expresión general**:
    *   La expresión se simplifica a: `True and not False`.
3.  **Aplicación del operador unario `not` (prioridad mayor que `and`)**:
    *   `not False` se evalúa como `True`.
    *   La expresión se reduce a: `True and True`.
4.  **Evaluación del operador `and` final**:
    *   `True and True` da como resultado final `True`.

Por ende, la variable `resultado` guardará el valor booleano `True` y el programa se ejecutará sin lanzar excepciones de error matemático.

---

# 3.8 Síntesis de Resultados y Conclusión Pedagógica

La comprensión profunda de cómo Python almacena, evalúa y opera con variables e identificadores constituye el pilar fundamental para el desarrollo de simulaciones de alto rendimiento en Nanotecnología e Inteligencia Artificial. A lo largo de esta unidad, hemos analizado que:

1.  **La memoria física es la frontera real**: La distinción entre referencias, copias superficiales y profundas no es solo teórica; define el éxito del aislamiento de simulaciones moleculares en sistemas como `mutabilidad_rastreo.py`.
2.  **El rigor científico requiere código limpio**: La adopción de PEP 8 y constantes basadas en la precisión de CODATA permite que las computadoras actúen como verdaderos laboratorios experimentales, como se demostró en `fisica_atomica.py`.
3.  **El intérprete opera con reglas fijas**: La jerarquía de los operadores aritméticos, relacionales y lógicos, y mecanismos óptimos como el cortocircuito, actúan como las compuertas lógicas y sensores en cascada que garantizan que el código de producción sea robusto, eficiente y libre de fallos en tiempo de ejecución.
4.  **La precisión numérica es relativa**: El uso obligatorio de `math.isclose` con tolerancias relativas parametrizadas en entornos de pruebas automatizadas con Pytest, es la única respuesta científica válida frente a los límites físicos del almacenamiento binario de flotantes del estándar IEEE 754.

---

## 🛠️ Herramientas de esta Unidad

**TutorAgent** — resuelve tus dudas conceptuales sobre el contenido de esta unidad, citando la sección exacta de origen:

```python
import os
import sys
from pathlib import Path

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
            "Créalo en el ícono de llave 🔑 de la barra lateral izquierda "
            "(ver Unidad 0, sección 0.9)."
        )

from src.multiagent_core.tutor_agent import TutorAgent

tutor = TutorAgent(course_dir=Path("."))
print(tutor.ask("¿cuál es la diferencia entre shallow copy y deep copy?"))
```

No requiere configuración adicional más allá de tu `GEMINI_API_KEY` (ver Unidad 0, sección 0.9).

### PseudocodeAgent — verifica tu Hilo de Oro

Escribe tu solución en pseudocódigo UCEMICH y visualiza su diagrama de flujo antes de traducir a Python:

```python
from src.multiagent_core.pseudocode_agent import PseudocodeAgent

agent = PseudocodeAgent()
mi_pseudocodigo = """
FUNCIÓN calcular_volumen_esfera(radio_nm)
    SI radio_nm <= 0 ENTONCES
        RETORNAR -1
    SINO
        volumen <- (4 / 3) * 3.14159 * radio_nm ** 3
        RETORNAR volumen
    FIN_SI
FIN_FUNCIÓN
"""
print(agent.pseudocode_to_mermaid(mi_pseudocodigo))
```

Copia el resultado en [mermaid.live](https://mermaid.live) para verlo renderizado, o pégalo en una celda Markdown de este notebook dentro de un bloque `` `mermaid ``.

### CodeAuditorAgent y EvaluatorAgent — audita tu código antes de entregar

Corre tu propio código a través del auditor y el evaluador antes de entregarlo, para detectar problemas de estilo, seguridad, o saber tu calificación aproximada contra la rúbrica:

```python
from src.multiagent_core.code_auditor_agent import CodeAuditorAgent
from src.multiagent_core.evaluator_agent import EvaluatorAgent

mi_codigo = """
def calcular_area(radio):
    return 3.14159 * radio ** 2
"""

auditor = CodeAuditorAgent()
print(auditor.generate_report(mi_codigo))

evaluador = EvaluatorAgent()
resultado = evaluador.evaluate(mi_codigo)
print(resultado["retroalimentacion"])
```
