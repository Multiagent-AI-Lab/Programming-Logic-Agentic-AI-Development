# Unidad 7: Estructuras de Datos Complejas y Modelado de Grafos en Nanotecnología

Esta unidad presenta el diseño, implementación y validación de estructuras de datos complejas para la simulación molecular y el modelado de redes cristalinas en el contexto de la nanotecnología. Se hace uso de matrices multidimensionales de NumPy para la simulación en malla, NetworkX para el modelado de contactos interatómicos como grafos de conocimiento, y la suite de pruebas unitarias pytest para garantizar la robustez del software de producción.

<!-- Reemplaza <org>/<repo> por la ruta real del repositorio en GitHub al publicarlo -->
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<org>/<repo>/blob/main/notebooks/UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.ipynb)

```python
import sys
if 'google.colab' in sys.modules:
    %pip install -q mcp fastmcp chromadb rich
```

---

## Introducción y Contexto Pedagógico

En la Ingeniería en Nanotecnología, el estudio de los sistemas a escala nanométrica (de $10^{-9}$ metros) requiere herramientas computacionales robustas para simular fenómenos moleculares, predecir el comportamiento de nuevos materiales y modelar redes cristalinas. En este nivel, los átomos individuales y sus interacciones químicas determinan las propiedades macroscópicas del material (mecánicas, eléctricas, térmicas, ópticas).

Para representar y manipular computacionalmente estas entidades, el programador científico debe seleccionar y dominar estructuras de datos adecuadas. En esta unidad, exploraremos tres enfoques fundamentales de organización de datos:
1. **Estructuras de datos básicas de Python (listas y diccionarios)**, que sirven como punto de partida para almacenar datos heterogéneos y dinámicos.
2. **Matrices multidimensionales optimizadas (NumPy)**, esenciales para discretizar campos de fuerza continuos y densidades electrónicas en mallas tridimensionales.
3. **Grafos (NetworkX)**, la estructura de datos matemática por excelencia para modelar la conectividad química (nodos como átomos, aristas como enlaces) y analizar propiedades de transporte de energía o electrones.

A través de esta lección, no solo aprenderás la sintaxis de programación en Python, sino la justificación física y matemática detrás de cada línea de código, vinculando la informática directamente con tu formación como nanotecnólogo en la UCEMICH.

---

## 1. Analogías Didácticas de Estructuras de Datos

Para comprender cómo operan estas estructuras en memoria y cuándo elegir cada una, analizaremos tres analogías del mundo real.

### Analogía 1: Listas y Diccionarios (Lista de Compras vs. Directorio Telefónico)

Imagine que va al supermercado con una **lista de compras** escrita en un papel.
* **La Lista de Compras (Listas en Python):** Los artículos están enumerados uno detrás de otro. Si quiere saber qué es lo primero que debe comprar, mira la posición 0. Si quiere encontrar "leche" en una lista desordenada, no le queda más remedio que leer la lista línea por línea, empezando por el principio hasta llegar al final. En computación, esto se conoce como búsqueda secuencial con una complejidad de tiempo lineal $O(N)$. Las listas son ideales cuando el orden secuencial de los elementos importa y cuando las adiciones y eliminaciones ocurren con frecuencia al final de la colección.
* **El Directorio Telefónico (Diccionarios en Python):** Ahora piense en un directorio telefónico clásico. Si desea buscar el número de "Héctor", no lee todo el libro desde la página uno. En su lugar, utiliza el índice alfabético para ir directamente a la sección de la letra "H" y ubicar "Héctor". El nombre actúa como una **clave (key)** y el número de teléfono como el **valor (value)**. Gracias a una función interna llamada *tabla hash*, Python puede encontrar cualquier clave en el diccionario casi de forma instantánea, sin importar si el directorio tiene 10 nombres o 10 millones de nombres. Su complejidad de tiempo promedio es constante $O(1)$.
* **Aplicación en Nanotecnología:** Si necesitamos guardar una secuencia ordenada de pasos experimentales para una síntesis sol-gel, utilizaremos una **lista**. Pero si deseamos almacenar las propiedades de un conjunto de nanopartículas (donde cada nanopartícula tiene un identificador único y un valor de diámetro), utilizaremos un **diccionario**, donde la clave será el ID de la nanopartícula y el valor su tamaño.

```python
# Ejemplo de Lista: Pasos de síntesis (secuencia lineal)
pasos_sintesis = ["Medir reactivos", "Disolver en etanol", "Calentar a 80°C", "Centrifugar"]

# Ejemplo de Diccionario: Propiedades de elementos químicos (búsqueda directa)
elementos_quimicos = {
    "H": {"nombre": "Hidrógeno", "masa_atomica": 1.008, "radio_covalente": 0.31},
    "C": {"nombre": "Carbono", "masa_atomica": 12.011, "radio_covalente": 0.76},
    "O": {"nombre": "Oxígeno", "masa_atomica": 15.999, "radio_covalente": 0.66}
}
```

### Analogía 2: NumPy (Cuadrícula de Píxeles u Organización de Siembra)

Imagine la pantalla de su teléfono móvil o una fotografía digital.
* **La Cuadrícula de Píxeles:** Si acerca la vista a una imagen, verá que está compuesta por una cuadrícula regular bidimensional de pequeños cuadros llamados píxeles. Cada píxel tiene una coordenada específica $(x, y)$ y un valor de color (rojo, verde, azul). Modificar una imagen de manera manual con listas de listas de Python requeriría ciclos `for` anidados muy lentos. NumPy funciona como el procesador de una tarjeta gráfica: permite aplicar operaciones matemáticas directamente sobre toda la cuadrícula en una sola instrucción (operaciones vectorizadas), lo que acelera el procesamiento miles de veces.
* **Organización de Siembra en el Valle de Sahuayo:** Piense en una parcela de cultivo perfectamente nivelada y organizada en surcos lineales y postes espaciados uniformemente. Cada intersección de la rejilla tiene una planta. Si quiere medir la humedad del suelo de cada planta, puede modelar la parcela como una matriz de NumPy bidimensional. Si desea simular el efecto de la evaporación solar en toda la parcela, no calcula el efecto planta por planta; en su lugar, aplica una constante de evaporación restándola directamente de toda la matriz: `humedad_suelo = humedad_suelo - tasa_evaporacion`.
* **Aplicación en Nanotecnología:** En simulaciones cuánticas o moleculares, no podemos medir propiedades en infinitos puntos del espacio continuo. Por ello, discretizamos un volumen tridimensional en una malla regular (como una pila tridimensional de píxeles, llamados *vóxeles*). Cada punto de la malla almacena el valor de la densidad electrónica $\rho(\mathbf{r})$. NumPy nos permite almacenar este bloque tridimensional en memoria contigua y realizar cálculos físicos ultrarrápidos sobre toda la estructura.

### Analogía 3: Grafos NetworkX (Mapas de Carreteras entre Ciudades)

Imagine que está planeando un viaje por carretera en el occidente de Michoacán.
* **El Mapa de Carreteras:** En este mapa, las ciudades (como Sahuayo, Jiquilpan, Zamora y Morelia) son puntos discretos en el espacio. Las carreteras físicas que conectan directamente estas ciudades son líneas conductoras de tránsito. En la teoría de grafos, las ciudades se denominan **nodos (nodes)** y las carreteras se denominan **aristas o enlaces (edges)**. Cada carretera tiene un peso o costo asociado, que puede ser la distancia física en kilómetros o el tiempo de viaje en minutos. Para viajar de Sahuayo a Morelia, puede haber múltiples caminos; el algoritmo de camino mínimo busca la combinación de carreteras que minimice el costo total del viaje.
* **Aplicación en Nanotecnología:** En una red cristalina de grafeno, los átomos de Carbono son los nodos. Los enlaces covalentes que unen los átomos de Carbono son las aristas. Si introducimos una perturbación térmica (calor) o un electrón en un átomo específico, esa energía se propagará a través de los enlaces químicos. Al modelar el cristal como un grafo con NetworkX, podemos determinar las rutas de conducción de calor o electricidad más eficientes aplicando algoritmos de caminos mínimos sobre la topología molecular.

---

## 2. Simulación Molecular en Mallas Tridimensionales (NumPy)

En simulaciones de dinámica molecular y teoría del funcional de la densidad (DFT), el espacio continuo se discretiza en una malla tridimensional para evaluar propiedades físicas locales. A continuación, se detalla el sustento matemático y la implementación de la clase `MolecularMeshSimulator`.

### Sustento Matemático de la Discretización Espacial

Consideremos una caja de simulación molecular tridimensional con longitudes físicas $L_x$, $L_y$ y $L_z$ (en Ångstroms, $\text{Å}$). Discretizamos esta caja utilizando $N_x$, $N_y$ y $N_z$ puntos a lo largo de cada eje de coordenadas, respectivamente.

El espaciamiento físico entre puntos consecutivos de la malla se define como la tupla de espaciamientos espaciales:
$$\Delta x = \text{spacing}_x, \quad \Delta y = \text{spacing}_y, \quad \Delta z = \text{spacing}_z$$

Cualquier punto en la malla indexada por los enteros $(i, j, k)$, donde $0 \le i < N_x$, $0 \le j < N_y$, y $0 \le k < N_z$, posee coordenadas físicas reales en el espacio tridimensional dadas por la relación:
$$x_i = i \cdot \Delta x$$
$$y_j = j \cdot \Delta y$$
$$z_k = k \cdot \Delta z$$

Si queremos aproximar una propiedad macroscópica a partir de los valores locales en cada celda discreta, como por ejemplo la carga eléctrica o densidad de masa total en el volumen, debemos calcular la **integral de volumen discreta**. Para un espacio continuo, la integral está dada por:
$$I = \iiint_V \rho(x, y, z) \, dx \, dy \, dz$$

Utilizando una aproximación de suma de Riemann de primer orden en tres dimensiones, la integral discreta se calcula como:
$$I \approx \sum_{i=0}^{N_x-1} \sum_{j=0}^{N_y-1} \sum_{k=0}^{N_z-1} \rho(i, j, k) \cdot dV$$

Donde el diferencial de volumen de cada elemento (vóxel) es constante y se calcula multiplicando el espaciamiento de la malla en las tres direcciones físicas:
$$dV = \Delta x \cdot \Delta y \cdot \Delta z$$

Esta suma de Riemann tridimensional es implementada de forma altamente eficiente en NumPy sumando todos los elementos de la matriz 3D y multiplicando por el factor volumétrico $dV$.

### Implementación en Python: `MolecularMeshSimulator`

A continuación se presenta el código de la simulación en malla utilizando NumPy, tipado estático (`typing`) y validaciones rigurosas para asegurar que no ocurran errores de división o dimensiones físicas inconsistentes.

```python
import numpy as np
import numpy.typing as npt
from typing import Dict, List, Tuple, Any, Optional

class MolecularMeshSimulator:
    """Simulador de malla de simulación molecular utilizando NumPy.

    Esta clase permite inicializar, manipular y consultar una malla tridimensional
    que representa propiedades físicas discretizadas en un espacio nanotecnológico.

    Attributes:
        dimensions (Tuple[int, int, int]): Número de puntos de malla en los ejes X, Y y Z (nx, ny, nz).
        spacing (Tuple[float, float, float]): Espaciamiento físico entre puntos de malla en Angstroms (Å) (dx, dy, dz).
        grid (npt.NDArray[np.float64]): Matriz 3D de NumPy que almacena los valores de la propiedad física.
        metadata (Dict[str, Any]): Metadatos de la simulación para trazabilidad.
    """

    def __init__(
        self,
        dimensions: Tuple[int, int, int],
        spacing: Tuple[float, float, float],
        initial_value: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Inicializa el simulador de malla molecular con dimensiones y espaciamiento.

        Args:
            dimensions: Tupla con el número de puntos de malla (nx, ny, nz).
            spacing: Tupla con el espaciamiento físico (dx, dy, dz) en Ångstroms.
            initial_value: Valor inicial para todos los puntos de la malla.
            metadata: Diccionario opcional con metadatos asociados.

        Raises:
            ValueError: Si alguna dimensión es menor o igual a cero, o si el espaciamiento
                no es estrictamente positivo.
            TypeError: Si los tipos de datos de entrada no corresponden a los indicados.
        """
        # Validación de tipo y valor para dimensiones
        if not isinstance(dimensions, tuple) or len(dimensions) != 3:
            raise TypeError("Las dimensiones deben ser una tupla de exactamente 3 enteros.")
        if not all(isinstance(d, int) and d > 0 for d in dimensions):
            raise ValueError("Las dimensiones de la malla deben ser enteros estrictamente mayores a cero.")
        
        # Validación de tipo y valor para espaciamiento físico
        if not isinstance(spacing, tuple) or len(spacing) != 3:
            raise TypeError("El espaciamiento debe ser una tupla de exactamente 3 flotantes.")
        if not all(isinstance(s, (int, float)) and s > 0.0 for s in spacing):
            raise ValueError("El espaciamiento físico en cada eje debe ser numérico y estrictamente mayor a cero (dx, dy, dz > 0).")

        # Asignación de atributos con conversión de tipos garantizada
        self.dimensions: Tuple[int, int, int] = dimensions
        self.spacing: Tuple[float, float, float] = (float(spacing[0]), float(spacing[1]), float(spacing[2]))
        
        # Creación de la cuadrícula tridimensional optimizada en memoria contigua
        self.grid: npt.NDArray[np.float64] = np.full(dimensions, fill_value=initial_value, dtype=np.float64)
        self.metadata: Dict[str, Any] = metadata if metadata is not None else {}

    def set_value_at(self, coords: Tuple[int, int, int], value: float) -> None:
        """Establece el valor de la propiedad física en un punto de malla específico.

        Args:
            coords: Tupla de índices enteros (i, j, k) dentro del rango de la malla.
            value: Valor flotante de la propiedad a asignar (e.g., densidad electrónica).

        Raises:
            IndexError: Si las coordenadas están fuera de los límites de la malla.
            TypeError: Si las coordenadas no son enteros de Python.
        """
        if not isinstance(coords, tuple) or len(coords) != 3:
            raise TypeError("Las coordenadas de malla deben ser una tupla de exactamente 3 enteros.")
        if not all(isinstance(c, int) for c in coords):
            raise TypeError("Los índices de coordenadas de la malla deben ser enteros.")
        
        i, j, k = coords
        nx, ny, nz = self.dimensions
        
        # Validación de límites espaciales del arreglo NumPy
        if not (0 <= i < nx and 0 <= j < ny and 0 <= k < nz):
            raise IndexError(f"Coordenadas de malla {coords} fuera de los límites definidos ({nx}, {ny}, {nz}).")

        self.grid[i, j, k] = float(value)

    def get_value_at(self, coords: Tuple[int, int, int]) -> float:
        """Obtiene el valor de la propiedad física en coordenadas de malla discretas.

        Args:
            coords: Tupla de índices enteros (i, j, k).

        Returns:
            El valor numérico almacenado en el punto de malla indicado.

        Raises:
            IndexError: Si las coordenadas exceden las dimensiones de la malla.
            TypeError: Si las coordenadas no son enteros.
        """
        if not isinstance(coords, tuple) or len(coords) != 3:
            raise TypeError("Las coordenadas deben ser una tupla de exactamente 3 enteros.")
        if not all(isinstance(c, int) for c in coords):
            raise TypeError("Los índices de coordenadas deben ser enteros.")
            
        i, j, k = coords
        nx, ny, nz = self.dimensions
        if not (0 <= i < nx and 0 <= j < ny and 0 <= k < nz):
            raise IndexError(f"Coordenadas {coords} fuera de los límites de la malla ({nx}, {ny}, {nz}).")
            
        return float(self.grid[i, j, k])

    def get_physical_coordinates(self, coords: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Calcula la posición espacial real (en Å) a partir de los índices discretos de la malla.

        Args:
            coords: Tupla de índices discretos de la malla (i, j, k).

        Returns:
            Una tupla (x, y, z) que representa la coordenada física real en el espacio continuo.

        Raises:
            IndexError: Si las coordenadas discretas exceden los límites de la malla.
        """
        i, j, k = coords
        nx, ny, nz = self.dimensions
        if not (0 <= i < nx and 0 <= j < ny and 0 <= k < nz):
            raise IndexError(f"Coordenadas {coords} fuera de límites para conversión física.")
            
        x = i * self.spacing[0]
        y = j * self.spacing[1]
        z = k * self.spacing[2]
        return (x, y, z)

    def calculate_total_density(self) -> float:
        """Calcula la integral discreta de la densidad sobre todo el volumen de simulación.

        Utiliza el diferencial de volumen dV = dx * dy * dz y realiza la suma tridimensional
        acelerada mediante vectorización de NumPy.

        Returns:
            La integral numérica de la propiedad almacenada en el volumen.
        """
        dv = self.spacing[0] * self.spacing[1] * self.spacing[2]
        # np.sum calcula la suma de todos los elementos en el arreglo de forma optimizada
        return float(np.sum(self.grid) * dv)
```

### Desglose Paso a Paso del Código de la Malla

1. **Importación de Módulos:**
   * `numpy` (importado como `np`) es la biblioteca estándar para el cálculo científico. Permite manipular arreglos multidimensionales en código compillado C de forma transparente.
   * `numpy.typing` proporciona soporte para tipos estáticos en arreglos de NumPy (`npt.NDArray`), lo que ayuda a evitar errores lógicos de dimensiones durante la fase de desarrollo.
2. **Definición del Constructor (`__init__`):**
   * El constructor acepta `dimensions` como una tupla tridimensional. Primero valida que contenga 3 elementos y que todos sean enteros positivos. Si el usuario ingresa dimensiones inválidas (por ejemplo, números negativos o tipos flotantes), el código lanza inmediatamente un `ValueError` o `TypeError` para evitar fallas silenciosas posteriores.
   * Lo mismo ocurre con `spacing`, que representa el ancho físico de cada celda. Debe ser mayor que cero, pues un espaciamiento de cero conduciría a un volumen de simulación de tamaño nulo, arruinando cálculos físicos posteriores.
   * `np.full` crea un arreglo de NumPy de tamaño especificado por `dimensions`, rellenado con `initial_value` de tipo flotante de precisión doble (`np.float64`).
3. **Control de Acceso con validación estricta de límites (`set_value_at` y `get_value_at`):**
   * Antes de modificar o recuperar un valor de la malla, el código verifica de manera proactiva si las coordenadas dadas están dentro del rango $[0, N_x-1]$, $[0, N_y-1]$ y $[0, N_z-1]$. Si no es así, lanza un `IndexError`. Esto es crucial porque NumPy permite indexación negativa en Python (por ejemplo, `-1` accede al último elemento), pero en mallas físicas estructuradas, la indexación negativa suele indicar un error en la lógica de simulación espacial del programador.
4. **Cálculo de Coordenadas Físicas (`get_physical_coordinates`):**
   * Convierte la posición entera y discreta $(i, j, k)$ en coordenadas espaciales continuas expresadas en Ångstroms multiplicando cada índice por su correspondiente espaciamiento en el eje respectivo.
5. **Integral Discreta (`calculate_total_density`):**
   * Multiplica la suma de todos los elementos del arreglo por el diferencial de volumen $dV$. En lugar de utilizar bucles anidados en Python (los cuales consumirían mucho tiempo de procesador en mallas grandes), el método aprovecha `np.sum(self.grid)`, delegando la iteración interna al código altamente optimizado en lenguaje C de NumPy.

---

## 3. Modelado de Redes Cristalinas como Grafos de Conocimiento (NetworkX)

Las estructuras cristalinas (como grafeno, nanotubos de carbono o redes organometálicas - MOFs) se representan óptimamente mediante grafos. En este enfoque, los nodos representan átomos individuales que contienen metadatos (como símbolo químico, carga parcial y posición) y las aristas representan enlaces covalentes o de coordinación con propiedades físicas (longitud de enlace y energía de enlace).

### Sustento Matemático y Fórmulas LaTeX

#### Distancia Euclidiana Tridimensional
Cuando agregamos un enlace entre dos átomos $A$ y $B$, sus coordenadas en el espacio tridimensional cartesiano se definen como:
$$\mathbf{p}_A = (x_A, y_A, z_A), \quad \mathbf{p}_B = (x_B, y_B, z_B)$$

La distancia geométrica real en línea recta entre ambos núcleos atómicos (longitud de enlace $d_{AB}$) se calcula aplicando la fórmula de la distancia euclidiana tridimensional en $\mathbb{R}^3$:
$$d_{AB} = \|\mathbf{p}_A - \mathbf{p}_B\|_2 = \sqrt{(x_A - x_B)^2 + (y_A - y_B)^2 + (z_A - z_B)^2}$$

En el código Python, esta fórmula matemática se evalúa numéricamente restando los vectores de coordenadas de los átomos y calculando la norma del vector resultante utilizando `np.linalg.norm(coord_a - coord_b)`.

#### Definición de Pesos del Grafo para Caminos Mínimos
En la física de materiales, deseamos analizar cómo fluye la energía térmica (fonones) o la carga eléctrica (electrones) a través del esqueleto atómico del cristal.
Los enlaces químicos más fuertes (con alta energía de enlace, expresada en $\text{kcal/mol}$) ofrecen un canal de comunicación de menor resistencia física para la propagación de energía. Por el contrario, enlaces débiles o fuerzas de dispersión de van der Waals representan canales de alta resistencia.

Para utilizar algoritmos estándar de búsqueda de caminos óptimos como el **Algoritmo de Dijkstra** (el cual minimiza la suma de pesos de las aristas), debemos definir una métrica de costo o resistencia que sea inversamente proporcional a la energía física del enlace químico.

Por tanto, definimos el peso computacional $W_{AB}$ de la arista que conecta los átomos $A$ y $B$ como:
$$W_{AB} = \frac{1}{E_{AB}}$$

Donde:
* $E_{AB}$ representa la energía de disociación del enlace químico en $\text{kcal/mol}$.
* Si el enlace es fuerte (alta energía $E_{AB}$), el peso del enlace $W_{AB}$ será muy pequeño, lo que significa que el algoritmo de Dijkstra lo seleccionará preferentemente como una ruta rápida de "baja resistencia".
* Para evitar indeterminaciones matemáticas por división por cero en el caso de enlaces con energía nula, introducimos un valor umbral de tolerancia ($\epsilon = 10^{-3}$):
  $$W_{AB} = \frac{1}{\max(E_{AB}, 10^{-3})}$$

El algoritmo de Dijkstra encontrará el camino entre dos átomos que minimice la suma acumulada de estas resistencias:
$$\text{Costo del Camino} = \sum_{(u, v) \in \text{Ruta}} W_{uv}$$

Al minimizar esta suma de resistencias recíprocas, estamos encontrando físicamente la trayectoria de conducción energética más eficiente a lo largo de la molécula o material bidimensional.

### Implementación en Python: `CrystalLatticeGraph`

A continuación, se detalla la clase que encapsula la API de NetworkX para crear el modelo estructural cristalino y realizar cálculos topológicos.

```python
import networkx as nx

class CrystalLatticeGraph:
    """Representa y analiza la red cristalina molecular mediante grafos de conocimiento.

    Nodos corresponden a átomos con metadatos y las aristas a enlaces químicos.
    Facilita el análisis de conectividad y cálculo de caminos mínimos de transferencia energética.
    """

    def __init__(self, name: str = "Red Cristalina Genérica") -> None:
        """Inicializa un grafo de red cristalina vacío.

        Args:
            name: Nombre identificador del cristal (e.g., 'Grafeno', 'MOF-5').
        """
        self.name: str = name
        # Inicializa un grafo no dirigido de NetworkX
        self.graph: nx.Graph = nx.Graph()

    def add_atom(
        self,
        atom_id: str,
        element: str,
        coordinates: Tuple[float, float, float],
        charge: float = 0.0
    ) -> None:
        """Agrega un átomo (nodo) a la red cristalina con sus atributos físicos.

        Args:
            atom_id: Identificador único del átomo (e.g., 'C1', 'O2').
            element: Símbolo químico del elemento (e.g., 'C', 'H', 'Fe').
            coordinates: Tupla de posición (x, y, z) en Ångstroms.
            charge: Carga eléctrica parcial neta sobre el átomo.

        Raises:
            ValueError: Si el identificador del átomo está vacío o las coordenadas son inválidas.
            TypeError: Si los tipos de datos no coinciden con los esperados.
        """
        if not isinstance(atom_id, str) or not atom_id.strip():
            raise ValueError("El identificador del átomo debe ser una cadena de texto no vacía.")
        if not isinstance(coordinates, tuple) or len(coordinates) != 3:
            raise ValueError("Las coordenadas espaciales deben ser una tupla de exactamente 3 flotantes.")
        if not all(isinstance(c, (int, float)) for c in coordinates):
            raise TypeError("Todos los componentes de las coordenadas tridimensionales deben ser numéricos.")
        
        # Inserción del nodo con diccionario de propiedades en el grafo
        self.graph.add_node(
            atom_id,
            element=element,
            coordinates=(float(coordinates[0]), float(coordinates[1]), float(coordinates[2])),
            charge=float(charge)
        )

    def add_bond(
        self,
        atom_a: str,
        atom_b: str,
        bond_type: str = "covalente",
        energy_kcal_mol: float = 80.0
    ) -> None:
        """Agrega un enlace químico (arista) entre dos átomos existentes en el grafo.

        Calcula dinámicamente la distancia euclidiana tridimensional para guardarla
        como longitud de enlace en las propiedades de la arista.

        Args:
            atom_a: Identificador del primer átomo.
            atom_b: Identificador del segundo átomo.
            bond_type: Tipo de enlace (e.g., 'covalente', 'ionico', 'coordinacion').
            energy_kcal_mol: Energía teórica de disociación de enlace en kcal/mol.

        Raises:
            KeyError: Si alguno de los átomos no ha sido previamente añadido al grafo.
            ValueError: Si la energía del enlace es negativa.
        """
        # Verificación estricta de la presencia de los nodos en el grafo
        if not self.graph.has_node(atom_a):
            raise KeyError(f"El átomo de origen '{atom_a}' no existe en el grafo de la red cristalina.")
        if not self.graph.has_node(atom_b):
            raise KeyError(f"El átomo de destino '{atom_b}' no existe en el grafo de la red cristalina.")
        if energy_kcal_mol < 0.0:
            raise ValueError("La energía de enlace no puede ser un valor negativo.")

        # Obtener coordenadas físicas de los nodos para el cálculo matemático
        coord_a = np.array(self.graph.nodes[atom_a]['coordinates'])
        coord_b = np.array(self.graph.nodes[atom_b]['coordinates'])
        
        # Aplicación de la fórmula de distancia euclidiana mediante álgebra lineal de NumPy
        bond_length = float(np.linalg.norm(coord_a - coord_b))

        # Cálculo de la resistencia física del enlace (peso de Dijkstra)
        # Se introduce un factor mínimo epsilon de 1e-3 para evitar la división entre cero.
        weight = 1.0 / max(energy_kcal_mol, 1e-3)

        # Inserción de la arista con propiedades
        self.graph.add_edge(
            atom_a,
            atom_b,
            bond_type=bond_type,
            bond_length_angstrom=bond_length,
            energy_kcal_mol=float(energy_kcal_mol),
            weight=weight
        )

    def find_shortest_path(self, start_atom: str, end_atom: str) -> Tuple[List[str], float]:
        """Encuentra el camino de mínima resistencia (máxima conductividad de energía) entre dos átomos.

        Utiliza el algoritmo de Dijkstra provisto por NetworkX basado en el peso
        calculado de manera inversamente proporcional a la energía de enlace.

        Args:
            start_atom: Identificador del átomo de origen.
            end_atom: Identificador del átomo de destino.

        Returns:
            Una tupla con:
                - La lista ordenada de átomos que representan el camino óptimo.
                - La resistencia del camino (suma de los pesos de Dijkstra a lo largo de la ruta).

        Raises:
            KeyError: Si los átomos de origen o destino no existen.
            nx.NetworkXNoPath: Si no existe ninguna conexión o camino físico entre ambos átomos.
        """
        if not self.graph.has_node(start_atom):
            raise KeyError(f"El átomo de origen '{start_atom}' no existe en el grafo.")
        if not self.graph.has_node(end_atom):
            raise KeyError(f"El átomo de destino '{end_atom}' no existe en el grafo.")

        # Invocación de los algoritmos de Dijkstra integrados en NetworkX
        path = nx.shortest_path(
            self.graph,
            source=start_atom,
            target=end_atom,
            weight='weight'
        )
        path_length = nx.shortest_path_length(
            self.graph,
            source=start_atom,
            target=end_atom,
            weight='weight'
        )
        return path, float(path_length)

    def get_adjacency_dict(self) -> Dict[str, List[str]]:
        """Exporta la estructura topológica del grafo a un diccionario de adyacencia clásico de Python.

        Returns:
            Un diccionario cuyas llaves son los IDs de los átomos y los valores son listas
            de IDs de los átomos vecinos directamente conectados por enlaces químicos.
        """
        # neighbors de NetworkX devuelve un iterador de nodos adyacentes
        return {node: list(self.graph.neighbors(node)) for node in self.graph.nodes}
```

### Desglose Paso a Paso del Código del Grafo Cristalino

1. **Creación del Grafo No Dirigido (`nx.Graph`):**
   * En nanotecnología, la mayoría de los enlaces covalentes son bidireccionales en términos de conductividad espacial, por lo que se utiliza un grafo no dirigido (`nx.Graph`).
2. **Inserción de Átomos con Metadatos (`add_atom`):**
   * Al agregar un átomo, no solo especificamos su identificador único (e.g. `'C1'`). También almacenamos información física dentro del nodo como atributos: el tipo de elemento, su posición cartesiana real tridimensional en el espacio y su carga parcial. Esto nos permite simular campos de potencial electrostático más adelante.
3. **Cálculo Dinámico de Longitudes de Enlace (`add_bond`):**
   * Este método requiere que ambos átomos ya existan en el grafo (de lo contrario, se lanza `KeyError`).
   * Extrae las coordenadas físicas de ambos átomos desde el grafo de NetworkX, calcula el vector de diferencia y obtiene su norma mediante `np.linalg.norm`. Esto automatiza la determinación de la distancia de enlace en lugar de forzar al usuario a medirla manualmente.
   * Calcula e inserta el atributo `weight` como la inversa de la energía de enlace.
4. **Cálculo del Camino de Mínima Resistencia (`find_shortest_path`):**
   * Utiliza la función `nx.shortest_path` de NetworkX, que implementa internamente el algoritmo de Dijkstra. Si se especifica el parámetro `weight='weight'`, el algoritmo no busca el camino con el menor número de enlaces, sino el camino que minimice la suma de los valores de resistencia (`weight`).
5. **Exportación de la Lista de Adyacencia (`get_adjacency_dict`):**
   * Utiliza una comprensión de diccionario para iterar sobre todos los nodos del grafo y generar una lista de vecinos para cada uno. Esta función es muy útil para depurar de forma visual las conexiones atómicas sin tener que examinar todo el objeto de datos del grafo.

---

## 4. Pruebas Unitarias Robustas (Suite con pytest)

Para validar la consistencia lógica del código de simulación molecular y el modelado de grafos, implementamos una suite completa de pruebas unitarias utilizando el marco `pytest`.

El uso de pruebas unitarias es fundamental en la ciencia de datos y la ingeniería nanotecnológica por tres razones principales:
1. **Evitar la Regresión:** Asegura que al optimizar el código matemático no rompamos funcionalidades lógicas básicas.
2. **Validación de Excepciones:** Garantiza que el código falle con elegancia lanzando excepciones predecibles ante datos físicos absurdos (como espaciamientos negativos o átomos inexistentes).
3. **Manejo de Errores de Coma Flotante:** Las computadoras representan números decimales en binario, lo que introduce pequeñas imprecisiones de redondeo. Usamos `pytest.approx` para comparar flotantes de manera tolerante a estos mínimos errores numéricos inherentes al hardware.

### Código de Pruebas: `test_structures.py`

Guarde el siguiente código en un archivo de pruebas para verificar la robustez de ambas clases.

```python
import pytest

# ==============================================================================
# Pruebas Unitarias para MolecularMeshSimulator
# ==============================================================================

def test_molecular_mesh_initialization() -> None:
    """Verifica que la inicialización de la malla molecular sea consistente.

    Comprueba que las dimensiones, espaciamientos físicos, forma interna de la
    matriz de NumPy y valores iniciales se establezcan correctamente en la memoria.
    """
    dims = (10, 10, 10)
    spacing = (0.5, 0.5, 0.5)
    simulator = MolecularMeshSimulator(dimensions=dims, spacing=spacing, initial_value=1.5)
    
    assert simulator.dimensions == dims
    assert simulator.spacing == (0.5, 0.5, 0.5)
    assert simulator.grid.shape == dims
    assert np.all(simulator.grid == 1.5)


def test_molecular_mesh_invalid_inputs() -> None:
    """Verifica que se lancen excepciones adecuadas ante entradas lógicas erróneas.

    Debe lanzar ValueError si se introducen coordenadas negativas o espaciamientos nulos,
    y TypeError si se proporcionan tipos incorrectos en los argumentos.
    """
    # Dimensiones con valores negativos (Físicamente imposible)
    with pytest.raises(ValueError):
        MolecularMeshSimulator(dimensions=(-1, 10, 10), spacing=(1.0, 1.0, 1.0))
        
    # Tipo de datos erróneo para el parámetro dimensiones
    with pytest.raises(TypeError):
        MolecularMeshSimulator(dimensions=("10", 10, 10), spacing=(1.0, 1.0, 1.0)) # type: ignore
        
    # Espaciamiento de malla igual a cero (Causaría volumen molecular cero)
    with pytest.raises(ValueError):
        MolecularMeshSimulator(dimensions=(5, 5, 5), spacing=(0.0, 1.0, 1.0))


def test_molecular_mesh_set_get_value() -> None:
    """Valida la asignación y extracción precisa de valores en la malla molecular.

    Asegura que el método set_value_at modifique el punto de malla exacto y que
    se lance una excepción de fuera de límite si se intenta acceder a una coordenada inexistente.
    """
    simulator = MolecularMeshSimulator(dimensions=(4, 4, 4), spacing=(1.0, 1.0, 1.0))
    coords = (1, 2, 3)
    val = 42.17
    
    simulator.set_value_at(coords, val)
    assert simulator.get_value_at(coords) == val
    
    # Coordenadas fuera del límite máximo (Tamaño es 4, por lo que los índices van de 0 a 3)
    with pytest.raises(IndexError):
        simulator.set_value_at((4, 0, 0), 10.0)


def test_molecular_mesh_coordinates_physical() -> None:
    """Valida la conversión matemática de índices de malla discretos a Ångstroms físicos.

    Comprueba que el cálculo de la posición espacial de cada punto de la malla siga la
    relación lineal de espaciamiento multiplicativo.
    """
    simulator = MolecularMeshSimulator(dimensions=(5, 5, 5), spacing=(0.2, 0.3, 0.4))
    idx = (2, 3, 4)
    # x = 2 * 0.2 = 0.4 Å
    # y = 3 * 0.3 = 0.9 Å
    # z = 4 * 0.4 = 1.6 Å
    expected_phys = (0.4, 0.9, 1.6)
    assert simulator.get_physical_coordinates(idx) == pytest.approx(expected_phys)


def test_molecular_mesh_total_density() -> None:
    """Verifica la integral discreta de la densidad de malla.

    Comprueba la precisión de la suma de Riemann tridimensional.
    Para una malla de 2x2x2 con valores uniformes de 2.0 y espaciamiento de 0.5 Å:
    - Volumen elemental (dV) = 0.5 * 0.5 * 0.5 = 0.125 Å³
    - Total de celdas = 8
    - Suma total = 8 * 2.0 = 16.0
    - Integral = 16.0 * 0.125 = 2.0
    """
    simulator = MolecularMeshSimulator(dimensions=(2, 2, 2), spacing=(0.5, 0.5, 0.5), initial_value=2.0)
    assert simulator.calculate_total_density() == pytest.approx(2.0)


# ==============================================================================
# Pruebas Unitarias para CrystalLatticeGraph
# ==============================================================================

def test_crystal_lattice_graph_building() -> None:
    """Prueba la construcción del grafo molecular añadiendo átomos (nodos) y enlaces (aristas).

    Valida que los metadatos de los átomos se conserven y que la longitud del enlace
    se calcule dinámicamente usando la distancia euclidiana tridimensional.
    """
    lattice = CrystalLatticeGraph(name="NanoDiamante")
    
    # Adición de dos átomos de carbono
    lattice.add_atom("C1", element="C", coordinates=(0.0, 0.0, 0.0), charge=0.0)
    lattice.add_atom("C2", element="C", coordinates=(1.54, 0.0, 0.0), charge=0.0)
    
    assert "C1" in lattice.graph.nodes
    assert "C2" in lattice.graph.nodes
    assert lattice.graph.nodes["C1"]["element"] == "C"

    # Enlace entre los átomos
    lattice.add_bond("C1", "C2", bond_type="covalente_simple", energy_kcal_mol=83.0)
    
    assert lattice.graph.has_edge("C1", "C2")
    bond_data = lattice.graph.edges["C1", "C2"]
    # La distancia física calculada debe ser exactamente 1.54 Å
    assert bond_data["bond_length_angstrom"] == pytest.approx(1.54)
    assert bond_data["energy_kcal_mol"] == 83.0


def test_crystal_lattice_missing_node_bond() -> None:
    """Garantiza la imposibilidad de enlazar átomos inexistentes.

    Si se intenta conectar un átomo que no ha sido añadido previamente al grafo,
    el método debe lanzar un error de tipo KeyError.
    """
    lattice = CrystalLatticeGraph()
    lattice.add_atom("C1", element="C", coordinates=(0.0, 0.0, 0.0))
    
    with pytest.raises(KeyError):
        lattice.add_bond("C1", "C_INEXISTENTE")


def test_crystal_lattice_shortest_path() -> None:
    """Verifica la determinación de caminos mínimos basados en la resistencia física.

    En una cadena lineal C1 - C2 - C3:
    - Enlace C1-C2 de alta energía (100 kcal/mol -> Resistencia 0.01)
    - Enlace C2-C3 de alta energía (100 kcal/mol -> Resistencia 0.01)
    El camino óptimo entre C1 y C3 debe pasar obligatoriamente por C2 con una resistencia acumulada de 0.02.
    """
    lattice = CrystalLatticeGraph(name="Cadena Carbonada")
    
    lattice.add_atom("C1", element="C", coordinates=(0.0, 0.0, 0.0))
    lattice.add_atom("C2", element="C", coordinates=(1.2, 0.0, 0.0))
    lattice.add_atom("C3", element="C", coordinates=(2.4, 0.0, 0.0))
    
    lattice.add_bond("C1", "C2", energy_kcal_mol=100.0)
    lattice.add_bond("C2", "C3", energy_kcal_mol=100.0)
    
    path, weight = lattice.find_shortest_path("C1", "C3")
    assert path == ["C1", "C2", "C3"]
    assert weight == pytest.approx(0.02)


def test_crystal_lattice_adjacency_dict() -> None:
    """Valida la correcta generación y exportación del diccionario de adyacencia física.

    Asegura que las conexiones no dirigidas del cristal se mapeen de forma recíproca.
    """
    lattice = CrystalLatticeGraph()
    lattice.add_atom("C1", element="C", coordinates=(0.0, 0.0, 0.0))
    lattice.add_atom("C2", element="C", coordinates=(1.0, 0.0, 0.0))
    lattice.add_bond("C1", "C2")
    
    adj = lattice.get_adjacency_dict()
    assert "C1" in adj
    assert adj["C1"] == ["C2"]
    assert adj["C2"] == ["C1"]
```

---

## 5. Simulación Práctica de Integración y Síntesis de Resultados

Para demostrar cómo interactúan las estructuras de datos vectorizadas en mallas y las topologías de grafos, implementaremos una simulación integrada completa.
En este escenario, modelaremos una nanocadena de átomos de plata (Ag), evaluaremos su topología de enlace en un grafo, calcularemos el camino de menor resistencia para la conducción de electrones, y mapearemos la distribución espacial de la densidad electrónica a lo largo de la cadena dentro de una malla tridimensional de simulación.

### Código del Script de Integración

```python
def ejecutar_simulacion_completa() -> None:
    """Ejecuta una simulación completa que integra el grafo cristalino y la malla NumPy.

    Modelará una nanocadena de Plata (Ag) y evaluará sus propiedades de conducción
    y distribución electrónica volumétrica.
    """
    print("======================================================================")
    print("INICIANDO SIMULACIÓN INTEGRADA DE NANOPROPIEDADES - UCEMICH")
    print("======================================================================\n")

    # 1. CONSTRUCCIÓN DE LA TOPOLOGÍA CRISTALINA (GRAFO)
    print("[Fase 1] Inicializando el Grafo de Conexiones Atómicas...")
    nanocadena = CrystalLatticeGraph(name="Nanocadena de Plata Ag-3")
    
    # Coordenadas tridimensionales físicas de los átomos (en Ångstroms)
    # Se simula una estructura lineal a lo largo del eje X con perturbación en Z
    coord_ag1 = (0.5, 1.0, 1.0)
    coord_ag2 = (2.0, 1.1, 1.0)
    coord_ag3 = (3.5, 0.9, 1.2)
    
    nanocadena.add_atom("Ag1", element="Ag", coordinates=coord_ag1, charge=0.15)
    nanocadena.add_atom("Ag2", element="Ag", coordinates=coord_ag2, charge=-0.30)
    nanocadena.add_atom("Ag3", element="Ag", coordinates=coord_ag3, charge=0.15)
    
    # Creación de enlaces covalentes/metálicos con distintas energías de enlace
    # Enlace Ag1-Ag2 es fuerte (alta energía); Enlace Ag2-Ag3 es más débil
    nanocadena.add_bond("Ag1", "Ag2", bond_type="metálico", energy_kcal_mol=45.0)
    nanocadena.add_bond("Ag2", "Ag3", bond_type="metálico", energy_kcal_mol=30.0)
    
    # Obtener el camino mínimo conductor desde Ag1 hasta Ag3
    camino, costo = nanocadena.find_shortest_path("Ag1", "Ag3")
    print(f" -> Camino de conducción eléctrica óptimo: {' -> '.join(camino)}")
    print(f" -> Costo computacional del camino (resistencia acumulada): {costo:.5f}\n")

    # 2. DISCRETIZACIÓN DE DENSIDAD ELECTRÓNICA EN MALLA (NumPy)
    print("[Fase 2] Inicializando la Malla 3D para Densidades Electrónicas...")
    # Creamos una caja de simulación de 5x4x4 puntos de malla con espaciamiento de 1.0 Å
    dimensiones_caja = (5, 4, 4)
    espaciamiento_Å = (1.0, 1.0, 1.0)
    
    simulador_malla = MolecularMeshSimulator(
        dimensions=dimensiones_caja,
        spacing=espaciamiento_Å,
        initial_value=0.01  # Densidad de fondo constante
    )
    
    # Mapeo espacial de la densidad electrónica
    # Asignamos valores altos en los puntos de malla más cercanos a las posiciones reales de los átomos
    # Átomo Ag1 (0.5, 1.0, 1.0) -> se aproxima al punto discreto (0, 1, 1) en la malla
    simulador_malla.set_value_at((0, 1, 1), 1.85)
    # Átomo Ag2 (2.0, 1.1, 1.0) -> se mapea en (2, 1, 1)
    simulador_malla.set_value_at((2, 1, 1), 2.10)
    # Átomo Ag3 (3.5, 0.9, 1.2) -> se mapea en (3, 1, 1) (redondeo de coordenadas)
    simulador_malla.set_value_at((3, 1, 1), 1.90)

    # Calcular la integral numérica volumétrica del sistema
    densidad_total = simulador_malla.calculate_total_density()
    print(f" -> Densidad electrónica integrada en toda la caja: {densidad_total:.4f} e⁻/Å³")
    
    # Consultar y mostrar metadatos físicos de un punto específico
    valor_centro = simulador_malla.get_value_at((2, 1, 1))
    coords_reales = simulador_malla.get_physical_coordinates((2, 1, 1))
    print(f" -> Densidad en el centro de la nanocadena {coords_reales} Å: {valor_centro:.2f} e⁻/Å³\n")
    
    print("======================================================================")
    print("SIMULACIÓN CONCLUIDA CON ÉXITO")
    print("======================================================================")

if __name__ == "__main__":
    ejecutar_simulacion_completa()
```

### Síntesis de Resultados Obtenidos

Al ejecutar esta simulación integrada, podemos extraer las siguientes conclusiones científicas y computacionales:
1. **Modelado Topológico:** El camino óptimo para la conductividad es lineal $\text{Ag1} \to \text{Ag2} \to \text{Ag3}$. La resistencia del camino es de $\approx 0.0555$ unidades de costo. Si agregáramos una carretera directa $\text{Ag1} \to \text{Ag3}$ pero con una energía de interacción muy baja (por ejemplo, $1.0\text{ kcal/mol}$ por fuerzas de dispersión), Dijkstra seguiría seleccionando el camino de paso a través del átomo central debido a que la suma de resistencias a través de enlaces metálicos fuertes es menor ($1/45 + 1/30 \approx 0.055 \ll 1/1 = 1.0$).
2. **Conservación de la Propiedad Física:** La densidad integrada de la malla da un valor aproximado de la carga total en el espacio continuo. El diferencial volumétrico $dV = 1.0\text{ Å} \times 1.0\text{ Å} \times 1.0\text{ Å} = 1.0\text{ Å}^3$. Al sumar los valores de fondo ($0.01$ en la mayoría de los $80$ puntos de malla) y las tres contribuciones locales de carga de los núcleos, la integral refleja adecuadamente la distribución electrónica del nanomaterial simulado.

---

## 6. Banco de Evaluación Didáctica

A continuación, se presenta un conjunto de 15 preguntas de examen diseñadas específicamente para consolidar los conocimientos adquiridos sobre estructuras de datos, programación científica y su aplicación en nanotecnología. Cada pregunta incluye justificaciones rigurosas de la opción válida y de cada uno de los distractores.

---

### Pregunta 1
**Enunciado:** Si en Python se requiere almacenar un listado estructurado de los símbolos químicos de los elementos que componen un nanotubo dopado para poder iterar en su orden exacto de síntesis química, ¿cuál estructura de datos es la más apropiada y cuál es su complejidad temporal promedio para buscar un elemento por índice?
* A) Diccionario; búsqueda en $O(1)$.
* B) Lista; búsqueda en $O(1)$.
* C) Conjunto (Set); búsqueda en $O(N)$.
* D) Lista; búsqueda en $O(N)$.

**Respuesta Correcta:** B

* **Justificación de la opción válida (B):** Las listas en Python mantienen un orden de inserción secuencial exacto. Al estar implementadas internamente como arreglos dinámicos en memoria contigua, acceder a cualquier posición mediante un índice (por ejemplo, `lista[3]`) se resuelve directamente calculando el desplazamiento de memoria (offset) en un tiempo constante, es decir, complejidad de tiempo $O(1)$.
* **Justificación del distractor A:** Aunque los diccionarios permiten búsquedas rápidas en tiempo $O(1)$, estas se realizan mediante una clave hash (como una cadena de texto), no mediante una secuencia de índices ordenados para iteración en el orden exacto del flujo experimental de síntesis.
* **Justificación del distractor C:** Los conjuntos en Python (`sets`) son colecciones desordenadas de elementos únicos. No permiten acceder a elementos por índice y su búsqueda promedio es de $O(1)$, no $O(N)$.
* **Justificación del distractor D:** La lista es correcta, pero el acceso a un elemento a través de su índice directo es de complejidad $O(1)$. Una búsqueda de tipo $O(N)$ (lineal) ocurriría si buscáramos un valor sin conocer su índice, barriendo toda la estructura.

---

### Pregunta 2
**Enunciado:** Al inicializar un objeto `MolecularMeshSimulator` con dimensiones `dimensions = (10, 20, 30)` y espaciamiento físico `spacing = (0.5, 0.5, 0.5)` en Ångstroms, ¿cuántos puntos de malla se crean en la matriz de NumPy y cuál es el volumen físico real total de la caja de simulación discreta?
* A) 6,000 puntos; volumen de $750.0\text{ Å}^3$.
* B) 60 puntos; volumen de $6,000.0\text{ Å}^3$.
* C) 6,000 puntos; volumen de $6,000.0\text{ Å}^3$.
* D) 60 puntos; volumen de $750.0\text{ Å}^3$.

**Respuesta Correcta:** A

* **Justificación de la opción válida (A):** El número total de puntos discretos se calcula multiplicando las dimensiones en los tres ejes: $10 \times 20 \times 30 = 6,000$ celdas de almacenamiento. El volumen total aproximado de la caja es el producto de su tamaño físico en cada eje. Las longitudes de los ejes son: $L_x = 10 \times 0.5 = 5.0\text{ Å}$, $L_y = 20 \times 0.5 = 10.0\text{ Å}$, $L_z = 30 \times 0.5 = 15.0\text{ Å}$. El volumen físico es $5.0 \times 10.0 \times 15.0 = 750.0\text{ Å}^3$.
* **Justificación del distractor B:** Sumar las dimensiones en los tres ejes en lugar de multiplicarlas da $10+20+30 = 60$, lo cual es un error computacional conceptual. Adicionalmente, el volumen de $6,000.0$ no considera el factor multiplicativo del espaciamiento.
* **Justificación del distractor C:** El número de puntos de malla es correcto, pero el volumen no ha sido multiplicado por el diferencial físico $(\Delta x \cdot \Delta y \cdot \Delta z = 0.125\text{ Å}^3)$, dando un volumen de simulación físicamente sobredimensionado.
* **Justificación del distractor D:** Presenta el error del número de puntos calculado mediante la suma de dimensiones, aunque el volumen matemático sea el correcto.

---

### Pregunta 3
**Enunciado:** En la clase `CrystalLatticeGraph`, definimos el peso de una arista para el algoritmo de Dijkstra de manera inversamente proporcional a la energía de enlace: $W_{ab} = 1.0 / E_{ab}$. ¿Cuál es el significado físico de esta definición al buscar el camino mínimo en la red?
* A) Que el camino de Dijkstra priorizará el transporte a través de los enlaces más débiles porque ofrecen menos peso computacional.
* B) Que el camino óptimo simulará la trayectoria que minimiza la distancia geométrica real en línea recta entre átomos.
* C) Que el algoritmo seleccionará preferentemente los enlaces con mayor energía química, modelando la ruta de menor resistencia para la energía.
* D) Que el algoritmo no tomará en cuenta la conectividad física de la estructura, basándose únicamente en las cargas eléctricas.

**Respuesta Correcta:** C

* **Justificación de la opción válida (C):** Al definir el peso como $1/E_{ab}$, un valor de energía física grande resulta en un peso computacional muy pequeño. Como el algoritmo de Dijkstra minimiza la suma acumulada de pesos, seleccionará prioritariamente aquellas trayectorias que contengan los enlaces más fuertes (menor peso), simulando adecuadamente el camino físico por donde la transferencia energética es más veloz y menos resistiva.
* **Justificación del distractor A:** Es una contradicción física y lógica. Los enlaces más débiles tienen un peso computacional $W_{ab}$ más alto, por lo que Dijkstra los evitará a menos que no haya ninguna otra alternativa de conexión.
* **Justificación del distractor B:** El camino mínimo de Dijkstra no calcula caminos en base a la longitud de enlace física en Ångstroms, sino a partir de la suma acumulativa de la resistencia definida por la energía de enlace química.
* **Justificación del distractor D:** NetworkX requiere estrictamente la existencia de aristas (enlaces) y nodos (átomos) en el grafo. Las cargas eléctricas de los nodos no intervienen en el cálculo del algoritmo de Dijkstra.

---

### Pregunta 4
**Enunciado:** Si un átomo de carbono se encuentra en la posición discreta de la malla $(i=8, j=2, k=5)$ en un simulador con espaciamiento de malla $(dx=0.25, dy=0.1, dz=0.4)$ en Ångstroms, ¿cuáles son sus coordenadas físicas reales $(x, y, z)$ en el espacio continuo?
* A) $(2.0\text{ Å}, 0.2\text{ Å}, 2.0\text{ Å})$
* B) $(32.0\text{ Å}, 20.0\text{ Å}, 12.5\text{ Å})$
* C) $(8.0\text{ Å}, 2.0\text{ Å}, 5.0\text{ Å})$
* D) $(2.0\text{ Å}, 0.2\text{ Å}, 1.25\text{ Å})$

**Respuesta Correcta:** A

* **Justificación de la opción válida (A):** Las posiciones físicas se calculan multiplicando los índices discretos por el espaciamiento: $x = 8 \times 0.25 = 2.0\text{ Å}$; $y = 2 \times 0.10 = 0.2\text{ Å}$; $z = 5 \times 0.40 = 2.0\text{ Å}$. Esto concuerda con las coordenadas espaciales reales.
* **Justificación del distractor B:** Este cálculo se realizó dividiendo incorrectamente los índices entre el espaciamiento (por ejemplo, $8 / 0.25 = 32.0$), lo cual subvierte la relación dimensional de la discretización.
* **Justificación del distractor C:** Estas son simplemente las coordenadas discretas de la malla, ignorando por completo la conversión de escala física por el factor de espaciamiento.
* **Justificación del distractor D:** La coordenada $z$ está mal calculada ($5 \times 0.25$ en lugar de $5 \times 0.40$), reflejando un error al confundir los factores de espaciamiento entre los ejes.

---

### Pregunta 5
**Enunciado:** Al escribir pruebas unitarias con `pytest` para cálculos nanotecnológicos que involucran operaciones de coma flotante (como distancias moleculares o volúmenes), ¿por qué es incorrecto utilizar la comparación directa simple `assert valor_calculado == valor_esperado`?
* A) Porque las variables en Python son inmutables y no permiten operaciones de comparación directa en pruebas unitarias.
* B) Debido a que `pytest` exige que todas las comparaciones se realicen únicamente con datos de tipo entero.
* C) Debido a imprecisiones inevitables en la representación binaria interna de los números decimales (coma flotante), lo que requiere usar tolerancias con `pytest.approx`.
* D) Porque la comparación directa consume mucha más memoria RAM y ralentiza drásticamente la ejecución de la prueba unitaria.

**Respuesta Correcta:** C

* **Justificación de la opción válida (C):** Los microprocesadores representan los números de punto flotante en sistema binario bajo el estándar IEEE 754. Esto provoca que números sencillos en base decimal (como $0.1$ o $0.2$) no tengan una representación binaria exacta finita, introduciendo ligeros errores de redondeo en el bit menos significativo. Al comparar directamente, por ejemplo, $0.1 + 0.2 == 0.3$, Python devolverá `False`. La función `pytest.approx` introduce un rango de tolerancia para acomodar estas microimprecisiones de hardware sin fallar la aserción lógica del test.
* **Justificación del distractor A:** Las variables numéricas son mutables en sus contenedores y se pueden comparar directamente. El problema no es de inmutabilidad, sino de precisión aritmética a nivel de hardware.
* **Justificación del distractor B:** Las suites de pruebas en Python permiten comparar y validar cualquier tipo de dato disponible en el lenguaje.
* **Justificación del distractor D:** La diferencia en consumo de memoria y tiempo de CPU entre una comparación directa y `pytest.approx` es infinitesimal e irrelevante en una suite de pruebas científicas.

---

### Pregunta 6
**Enunciado:** Si intentamos inicializar la malla molecular pasándole un espaciamiento de malla con un valor negativo en el eje Y: `spacing = (0.2, -0.1, 0.5)`, ¿cómo responde el código robusto desarrollado en `MolecularMeshSimulator`?
* A) El constructor ignora el signo negativo y convierte el espaciamiento a su valor absoluto de forma automática.
* B) Lanza un error de tipo `TypeError` porque el espaciamiento negativo no se puede almacenar como float.
* C) Lanza un error de valor `ValueError` debido a que el espaciamiento en cada eje debe ser estrictamente positivo.
* D) Inicializa la malla con éxito, pero la función de integral dará una masa negativa.

**Respuesta Correcta:** C

* **Justificación de la opción válida (C):** De acuerdo con el código robusto del constructor de `MolecularMeshSimulator`, hay una línea de validación de negocio físico que evalúa si todos los elementos del espaciamiento son estrictamente mayores a cero: `if not all(isinstance(s, (int, float)) and s > 0.0 for s in spacing): raise ValueError(...)`. Por lo tanto, un espaciamiento de $-0.1$ dispara inmediatamente esta salvaguarda lanzando un `ValueError`.
* **Justificación del distractor A:** Corregir en silencio errores conceptuales graves (como un espaciamiento físico negativo) es una mala práctica de programación científica que oculta fallos lógicos en el flujo del software.
* **Justificación del distractor B:** El tipo de dato $-0.1$ sigue siendo numérico (`float`), por lo que no viola el tipo de datos del objeto, sino su valor de pertinencia física.
* **Justificación del distractor D:** Si el código no tuviera validaciones, esto ocurriría; sin embargo, al contar con aserciones en el constructor, la inicialización se detiene antes de generar la cuadrícula de datos.

---

### Pregunta 7
**Enunciado:** ¿Cuál es la ventaja computacional fundamental de almacenar un diccionario de adyacencia del grafo atómico en comparación con una lista de enlaces para la búsqueda recurrente de vecinos de un átomo?
* A) El diccionario permite saber si dos átomos están enlazados en un tiempo promedio constante $O(1)$, mientras que una lista de aristas requiere una búsqueda lineal de complejidad $O(M)$, donde $M$ es el número de enlaces.
* B) El diccionario consume menos espacio físico en el disco duro al serializar los datos del material.
* C) La lista de enlaces no permite almacenar atributos químicos adicionales en las conexiones.
* D) El diccionario es compatible únicamente con arreglos de NumPy vectorizados.

**Respuesta Correcta:** A

* **Justificación de la opción válida (A):** En un diccionario de adyacencia de la forma `{nodo: [vecinos]}`, consultar los vecinos directamente conectados a un átomo consiste en evaluar una llave en una tabla hash, lo cual es una operación sumamente rápida de costo constante $O(1)$. En cambio, buscar en una lista simple de aristas requiere iterar sobre toda la colección de enlaces de inicio a fin en el peor de los casos, lo que escala linealmente con el tamaño de la estructura.
* **Justificación del distractor B:** En términos de memoria interna, los diccionarios en Python consumen ligeramente más memoria debido al espacio libre reservado en la tabla hash para minimizar colisiones de direccionamiento.
* **Justificación del distractor C:** Las listas de enlaces pueden contener perfectamente tuplas con diccionarios anidados de atributos de enlace.
* **Justificación del distractor D:** Los diccionarios son estructuras nativas de Python y operan de forma independiente a la biblioteca de cálculo matricial NumPy.

---

### Pregunta 8
**Enunciado:** Durante la simulación, ¿qué excepción específica de NetworkX se produce al intentar buscar la ruta más corta para el transporte de energía utilizando `find_shortest_path` si los átomos de origen y destino no están conectados en absoluto por ninguna red de enlaces químicos?
* A) `KeyError`
* B) `NetworkXNoPath`
* C) `ValueError`
* D) `IndexError`

**Respuesta Correcta:** B

* **Justificación de la opción válida (B):** La biblioteca NetworkX define excepciones personalizadas para el flujo de análisis topológico. Si dos nodos del grafo existen pero pertenecen a componentes conexos aislados del cristal, no existe ningún camino físico que los una, por lo que la función `shortest_path` lanza la excepción `networkx.exception.NetworkXNoPath`.
* **Justificación del distractor A:** Un `KeyError` se lanzaría si uno o ambos átomos proporcionados en los argumentos no existieran en absoluto como nodos en la estructura del grafo.
* **Justificación del distractor C:** El error `ValueError` se reserva para argumentos con tipos de datos válidos pero con contenidos numéricos ilógicos en el contexto del constructor o cálculos geométricos.
* **Justificación del distractor D:** El error `IndexError` se lanza al intentar acceder a posiciones fuera del rango índice en arreglos ordenados secuencialmente, no en grafos.

---

### Pregunta 9
**Enunciado:** Si el simulador de malla molecular tiene un valor uniforme de densidad electrónica de $0.05\text{ e}^-/\text{Å}^3$ en todos sus puntos y la integral de volumen discreta devuelve exactamente $1.0\text{ e}^-$, ¿cuál es el volumen físico de la celda molecular simulada si las dimensiones son $(4, 5, 2)$?
* A) $40.0\text{ Å}^3$
* B) $2.0\text{ Å}^3$
* C) $20.0\text{ Å}^3$
* D) $80.0\text{ Å}^3$

**Respuesta Correcta:** C

* **Justificación de la opción válida (C):** La integral discreta de la densidad uniforme se aproxima como: $I = \text{Densidad} \times \text{Volumen Total} = \rho \times V_{\text{total}}$.
Tenemos $I = 1.0\text{ e}^-$ y $\rho = 0.05\text{ e}^-/\text{Å}^3$.
Despejamos el volumen: $V_{\text{total}} = I / \rho = 1.0 / 0.05 = 20.0\text{ Å}^3$.
* **Justificación del distractor A:** Este valor representa el número total de celdas discretas ($4 \times 5 \times 2 = 40$), lo cual no equivale al volumen físico a menos que el volumen elemental de cada celda $dV$ sea exactamente $1.0\text{ Å}^3$.
* **Justificación del distractor B:** Corresponde a un error de cálculo aritmético simple en la división de los valores físicos proporcionados.
* **Justificación del distractor D:** Es el resultado de multiplicar directamente las dimensiones por la densidad ($40 \times 2$ o similar), lo cual no tiene validez física.

---

### Pregunta 10
**Enunciado:** ¿Por qué la manipulación de mallas tridimensionales con matrices de NumPy es preferible al uso de listas anidadas tridimensionales de Python nativo `list[list[list[float]]]` para simulaciones a gran escala?
* A) NumPy permite almacenar tipos de datos dinámicos mezclados en la misma malla para mayor flexibilidad.
* B) Las listas nativas consumen menos memoria RAM y tienen mayor velocidad de compilación.
* C) NumPy almacena los datos en bloques contiguos de memoria de tipo homogéneo y utiliza operaciones vectorizadas escritas en C, evitando la sobrecarga de ciclos iterativos y punteros de Python.
* D) NetworkX requiere obligatoriamente matrices de NumPy para realizar análisis topológico de enlaces.

**Respuesta Correcta:** C

* **Justificación de la opción válida (C):** Python nativo representa las listas como arreglos de punteros a objetos en memoria desorganizada (el montón o heap). Esto implica que una lista 3D anidada requiere desreferenciar múltiples punteros por cada lectura, además de la sobrecarga del intérprete de Python en los bucles. NumPy reserva un bloque plano y contiguo de memoria de bytes homogéneos y ejecuta las operaciones numéricas en código compilado C/Fortran directo, permitiendo la vectorización y el uso eficiente de la memoria caché del procesador.
* **Justificación del distractor A:** Por el contrario, NumPy requiere tipos homogéneos (como `np.float64`) para lograr eficiencia. Permitir tipos heterogéneos anularía sus optimizaciones en memoria.
* **Justificación del distractor B:** Las listas nativas consumen considerablemente más memoria RAM debido a la sobrecarga de envolver cada número float en un objeto completo de Python (`PyObject`).
* **Justificación del distractor D:** NetworkX es una biblioteca independiente que acepta listas de adyacencia nativas u objetos de grafos propios, no depende exclusivamente de NumPy para modelar estructuras de datos de red.

---

### Pregunta 11
**Enunciado:** Al invocar el método `add_bond("C1", "C2", energy_kcal_mol=80.0)` en un cristal cúbico, el método calcula automáticamente la longitud de arista. ¿Cuál es el resultado de la longitud calculada si el átomo `C1` se posiciona en $(0.0, 0.0, 0.0)$ y el átomo `C2` en $(1.0, 2.0, 2.0)$ en Ångstroms?
* A) $5.0\text{ Å}$
* B) $3.0\text{ Å}$
* C) $9.0\text{ Å}$
* D) $1.73\text{ Å}$

**Respuesta Correcta:** B

* **Justificación de la opción válida (B):** Aplicando la fórmula de la distancia euclidiana tridimensional para los puntos dados:
  $$d = \sqrt{(1.0 - 0.0)^2 + (2.0 - 0.0)^2 + (2.0 - 0.0)^2}$$
  $$d = \sqrt{1.0 + 4.0 + 4.0} = \sqrt{9.0} = 3.0\text{ Å}$$
  Por tanto, la distancia calculada guardada en la arista es exactamente $3.0\text{ Å}$.
* **Justificación del distractor A:** Resulta de un error al no aplicar la raíz cuadrada tras sumar los cuadrados ($1 + 4 + 4 = 9$, pero mal evaluado como 25) o de operaciones incorrectas en los componentes cartesianos.
* **Justificación del distractor C:** Es el valor obtenido antes de aplicar la operación de raíz cuadrada, es decir, el cuadrado de la distancia ($d^2 = 9.0$).
* **Justificación del distractor D:** Corresponde a la distancia euclidiana de un vector unitario tridimensional clásico $(1, 1, 1)$, que es $\sqrt{3} \approx 1.73\text{ Å}$.

---

### Pregunta 12
**Enunciado:** Si en pytest queremos asegurar que un bloque de código lance de manera controlada una excepción de tipo `KeyError` al buscar un átomo inexistente en la red, ¿cuál es el mecanismo sintáctico correcto para estructurar la prueba unitaria?
* A) `assert CrystalLatticeGraph.find_shortest_path("AtomoInexistente") == KeyError`
* B) Utilizar el bloque de contexto `with pytest.raises(KeyError):` antes de invocar la función de búsqueda de caminos óptimos.
* C) Capturar el error con `try/except KeyError` y retornar un booleano `True` en la aserción final.
* D) `pytest` no permite verificar excepciones de forma nativa, por lo que se debe evitar que el código falle durante el testeo.

**Respuesta Correcta:** B

* **Justificación de la opción válida (B):** La API de `pytest` provee el administrador de contexto `with pytest.raises(Excepcion):`. Cualquier código ejecutado dentro de este bloque que dispare la excepción indicada será interceptado de forma exitosa por pytest, considerando la prueba como válida. Si la excepción no ocurre o es de otro tipo, la prueba fallará.
* **Justificación del distractor A:** La aserción convencional compara valores devueltos por funciones. Una excepción interrumpe la ejecución normal del flujo de control, por lo que el `assert` lineal nunca llegaría a ejecutarse si el error ocurre en la llamada.
* **Justificación del distractor C:** Aunque el bloque `try/except` nativo funciona, es redundante y añade complejidad visual innecesaria a la suite de pruebas unitarias, violando los principios de claridad del código.
* **Justificación del distractor D:** Es falso. Validar excepciones es una característica clave del desarrollo guiado por pruebas (TDD) en el que se basa pytest.

---

### Pregunta 13
**Enunciado:** ¿Cuál es la complejidad temporal en el peor de los casos al ejecutar el algoritmo de Dijkstra en NetworkX para encontrar la ruta de menor resistencia energética en un grafo molecular con $V$ átomos y $E$ enlaces químicos utilizando colas de prioridad eficientes (Min-Heap)?
* A) $O(V^2)$
* B) $O(E \log V)$
* C) $O(V + E)$
* D) $O(1)$

**Respuesta Correcta:** B

* **Justificación de la opción válida (B):** Al emplear un montículo binario (binary heap) como cola de prioridad para recuperar el nodo con menor costo en cada iteración del algoritmo de Dijkstra, las operaciones de extracción y actualización de distancias toman un tiempo logarítmico con respecto a los nodos. La complejidad global resultante es de $O((V + E) \log V)$, que para grafos conectados típicos de redes cristalinas se simplifica comúnmente a $O(E \log V)$.
* **Justificación del distractor A:** $O(V^2)$ es la complejidad del algoritmo de Dijkstra original sin implementar colas de prioridad optimizadas (búsqueda lineal del mínimo en cada paso), ineficiente para sistemas cristalinos grandes con miles de átomos.
* **Justificación del distractor C:** $O(V + E)$ corresponde a algoritmos de búsqueda no pesados como Búsqueda en Anchura (BFS), pero no resuelve caminos óptimos en grafos con pesos heterogéneos de enlaces químicos.
* **Justificación del distractor D:** No existe un algoritmo físico para la búsqueda de caminos mínimos de complejidad constante $O(1)$, pues la estructura molecular debe ser necesariamente explorada en su topología.

---

### Pregunta 14
**Enunciado:** Al mapear un cristal de grafeno (capa bidimensional monocapa de carbono), ¿cuántos enlaces químicos directos (vecinos inmediatos en el grafo) se esperan obtener para un átomo de carbono que no esté ubicado en los bordes de la nanoestructura?
* A) 4 vecinos.
* B) 3 vecinos.
* C) 6 vecinos.
* D) 2 vecinos.

**Respuesta Correcta:** B

* **Justificación de la opción válida (B):** La hibridación atómica del grafeno es de tipo $sp^2$. Esto significa que cada átomo de Carbono en la red hexagonal interna se enlaza covalentemente de forma directa con otros 3 átomos de Carbono circundantes (ángulos de enlace de $120^{\circ}$). En consecuencia, en el grafo químico, cada nodo central poseerá exactamente un grado de conectividad de 3.
* **Justificación del distractor A:** La conectividad 4 corresponde a la hibridación cristalina $sp^3$ típica de la estructura tridimensional del diamante, no del grafeno bidimensional.
* **Justificación del distractor C:** Aunque el anillo elemental del grafeno es un hexágono (6 carbonos), cada nodo individual comparte fronteras y tiene solo 3 enlaces vecinos directos.
* **Justificación del distractor D:** Una conectividad de 2 correspondería a una cadena polimérica lineal pura de carbonos (como los cumulenos) u otras configuraciones de menor estabilidad estructural.

---

### Pregunta 15
**Enunciado:** ¿Cuál es el propósito del tipado estático (como `npt.NDArray[np.float64]` o `Tuple[int, int, int]`) incorporado en el desarrollo de este simulador científico de nanotecnología?
* A) Indicarle al procesador de la computadora que compile el código de Python directamente a lenguaje binario de máquina en tiempo de ejecución.
* B) Garantizar que las variables no consuman espacio en la memoria virtual del sistema operativo.
* C) Proveer documentación explícita y permitir que herramientas de análisis estático (como `mypy`) detecten errores lógicos de tipo y dimensiones de datos antes de que se ejecute la simulación física.
* D) Obligar a la computadora a ejecutar todas las operaciones matemáticas exclusivamente en la tarjeta gráfica (GPU).

**Respuesta Correcta:** C

* **Justificación de la opción válida (C):** El tipado estático en Python (Type Hints) no altera el comportamiento dinámico del código en tiempo de ejecución. Su valor fundamental radica en que actúa como una forma de documentación de código vivo y permite a los analizadores estáticos de código identificar errores conceptuales graves (como pasar un flotante en lugar de un entero para un índice discreto de malla) en la etapa de desarrollo, ahorrando horas de depuración en simulación.
* **Justificación del distractor A:** Python es un lenguaje interpretado. Los type hints no actúan como compiladores nativos directos a código de máquina.
* **Justificación del distractor B:** Las anotaciones de tipo no reducen el consumo físico de memoria; de hecho, añaden una pequeña sobrecarga sintáctica en la estructura del código fuente para legibilidad humana y de herramientas de control.
* **Justificación del distractor D:** NumPy opera por defecto en la CPU central. Para delegar operaciones matemáticas a la GPU, se requieren bibliotecas específicas adicionales como CuPy o PyTorch, independientes de las sugerencias de tipo de Python.

---

## 7. Rúbrica de Evaluación

Esta unidad se evalúa con la **Rúbrica Genérica de Laboratorio** (4 criterios × 4 niveles) definida en `RUBRICA_GENERAL.md`. Criterios específicos de Unidad 7:

| Criterio adicional | Insuficiente | En desarrollo | Competente | Sobresaliente |
| :--- | :--- | :--- | :--- | :--- |
| **Modelado con grafos (NetworkX)** | No logra representar el problema como nodos/aristas. | Representa nodos y aristas pero sin metadatos físicos relevantes (elemento, carga, energía de enlace). | Modela correctamente el grafo con metadatos físicos completos. | Además implementa y justifica el algoritmo de camino mínimo (Dijkstra) aplicado al contexto físico del problema. |
| **Simulación con NumPy (mallas)** | No ejecuta o produce dimensiones incorrectas. | Ejecuta con la forma de malla correcta pero sin validar límites físicos. | Ejecuta correctamente y valida límites (índices dentro de rango, valores físicos coherentes). | Además optimiza el uso de operaciones vectorizadas de NumPy frente a loops explícitos. |

---

## 🛠️ Herramientas de esta Unidad

**TutorAgent** — resuelve tus dudas conceptuales sobre el contenido de esta unidad, citando la sección exacta de origen:

```python
from pathlib import Path
from src.multiagent_core.tutor_agent import TutorAgent

tutor = TutorAgent(course_dir=Path("."))
print(tutor.ask("¿cómo se calcula el camino mínimo en un grafo de red cristalina con NetworkX?"))
```

No requiere configuración adicional más allá de tu `GEMINI_API_KEY` (ver Unidad 0, sección 0.9).
