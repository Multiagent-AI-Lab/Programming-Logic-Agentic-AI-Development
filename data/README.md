# `data/` — Datasets de Nanotecnología del Curso

Datasets de referencia usados en los ejemplos y laboratorios de las Unidades 3, 5 y 7. Todos usan contexto de nanotecnología consistente con el resto del material del curso.

---

## `nanoparticulas_ejemplo.csv`

20 filas de nanopartículas metálicas y de óxidos comunes en síntesis coloidal.

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `radio_nm` | float | Radio de la nanopartícula en nanómetros |
| `material` | str | Material: `Au`, `Ag`, `TiO2`, `Fe3O4`, `ZnO` |
| `temp_K` | int | Temperatura de síntesis en Kelvin |
| `morfologia` | str | Forma: `esferica`, `cubica`, `rod` |

**Carga con pandas:**
```python
import pandas as pd

df = pd.read_csv("data/nanoparticulas_ejemplo.csv")
print(df.head())
print(df.groupby("material")["radio_nm"].mean())
```

Uso sugerido: U3 (variables/operadores sobre columnas numéricas), U5 (contadores/acumuladores/banderas al iterar filas, p. ej. contar partículas por encima de un radio umbral).

---

## `molecula_agua.json`

Coordenadas atómicas de una molécula de H₂O en geometría de equilibrio, con metadata de carga parcial por átomo y los dos enlaces O–H.

**Carga con json:**
```python
import json

with open("data/molecula_agua.json", encoding="utf-8") as f:
    agua = json.load(f)

for atomo in agua["atomos"]:
    print(atomo["id"], atomo["elemento"], atomo["coordenadas"])
```

Uso sugerido: U3 (introducción a estructuras anidadas dict/list antes de listas de coordenadas más complejas).

---

## `red_cristalina_Au.json`

Fragmento de red cristalina FCC (cúbica centrada en las caras) de oro: 6 nodos (átomos) y 7 aristas (enlaces metálicos). El esquema de campos (`element`, `coordinates`, `charge` en nodos; `bond_type`, `energy_kcal_mol` en aristas) es compatible directamente con la clase `CrystalLatticeGraph` de `UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.md`.

**Carga con json + networkx:**
```python
import json
import networkx as nx

with open("data/red_cristalina_Au.json", encoding="utf-8") as f:
    red = json.load(f)

G = nx.Graph()
for nodo in red["nodos"]:
    G.add_node(nodo["id"], element=nodo["element"],
               coordinates=tuple(nodo["coordinates"]), charge=nodo["charge"])
for arista in red["aristas"]:
    G.add_edge(arista["atomo_a"], arista["atomo_b"],
               bond_type=arista["bond_type"], energy_kcal_mol=arista["energy_kcal_mol"])

print(nx.shortest_path(G, "Au1", "Au6"))
```

Uso sugerido: U7 (grafos de conocimiento con NetworkX, cálculo de caminos mínimos de transferencia energética con Dijkstra).
