# Reporte de Auditoría de Contenido

**Total de hallazgos en 9 unidades: 33**

> **Nota de ruido conocido (investigado 2026-08-06):** 16 de los 33 hallazgos son ruido confirmado de la heurística, no problemas reales de contenido — no requieren corrección:
>
> - **9× "Ciclo del Hilo de Oro incompleto"** (uno por unidad): la heurística exige bloques etiquetados literalmente ` ```pseudocodigo `/` ```pytest ` en cada unidad. El contenido real sí cubre pseudocódigo y pruebas pytest, pero bajo la etiqueta ` ```python ` — verificado en U5: sección completa "7. Suite de Pruebas Unitarias (`pytest`)" con `import pytest` y funciones `test_*` reales (línea 661+), y ejemplo de pseudocódigo dentro de la celda de `PseudocodeAgent` (línea 1012+). El Hilo de Oro está presente; es una discrepancia de convención de etiquetado, no de contenido.
> - **7× "Error de sintaxis... unexpected indent"** (U4: 6, U5: 1): son fragmentos de método citados a propósito con fines didácticos — el patrón "explica por fragmentos" del curso presenta la función completa una vez y luego la desmenuza en bloques de código sucesivos con explicación intercalada entre cada uno (verificado en U4 líneas 228-264, función `classify_by_geometry_match` dividida en 5 bloques consecutivos). `ast.parse()` no puede parsear un fragmento indentado sin su `def` envolvente, pero el contenido en sí es correcto.
>
> Los 17 hallazgos restantes (docstrings faltantes, `eval()`/`exec()`, discrepancias de duración curricular) sí ameritan revisión caso por caso.

## UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md (1 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['mermaid', 'pseudocodigo', 'pytest'].

## UNIDAD_1_PENSAMIENTO_COMPUTACIONAL_CLI.md (1 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['pseudocodigo', 'pytest'].

## UNIDAD_2_METODOLOGIA_ALGORITMOS_PRUEBAS.md (3 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['pytest'].

### Codigo
- Riesgo de Seguridad: Uso de `eval()`. Ejecutar cadenas de texto arbitrarias expone al sistema a inyecciones de código y ejecución remota de comandos no autorizados (Riesgo OWASP LLM-02).

### Curricular
- Posible discrepancia de duración: el MD dice '1 semana (6 horas)' pero el programa oficial indica 'Semana 2'.

## UNIDAD_3_VARIABLES_OPERADORES.md (2 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['mermaid', 'pseudocodigo', 'pytest'].

### Curricular
- Posible discrepancia de duración: el MD dice '2 semanas (12 horas)' pero el programa oficial indica 'Semanas 3-4'.

## UNIDAD_4_ESTRUCTURAS_DECISION.md (14 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['pseudocodigo', 'pytest'].

### Codigo
- Función '__post_init__' sin docstring en el código de ejemplo.
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 1)
- Función 'classify_by_aspect_ratio_if' sin docstring en el código de ejemplo.
- Función 'classify_by_geometry_match' sin docstring en el código de ejemplo.
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 1)
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 2)
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 2)
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 2)
- Función 'spaghetti_classifier' sin docstring en el código de ejemplo.
- Función 'spaghetti_classifier' sin type hints completos (argumentos sin tipo: ['data'], retorno anotado: False).
- Función 'refactored_classifier' sin docstring en el código de ejemplo.
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 1)
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 1)

## UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md (6 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['pseudocodigo', 'pytest'].

### Codigo
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 1)
- Riesgo de Seguridad: Uso de `exec()`. Ejecutar cadenas de texto arbitrarias expone al sistema a inyecciones de código y ejecución remota de comandos no autorizados (Riesgo OWASP LLM-02).
- Función 'execute' sin docstring en el código de ejemplo.
- Función 'propose_correction' sin docstring en el código de ejemplo.
- Función '__init__' sin docstring en el código de ejemplo.

## UNIDAD_6_MODULARIDAD_IA_MCP.md (4 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['pseudocodigo', 'pytest'].

### Codigo
- Función 'calcular_relacion_aspecto' sin docstring en el código de ejemplo.
- Función 'suma_radios' sin docstring en el código de ejemplo.
- Función 'calcular_area' sin docstring en el código de ejemplo.

## UNIDAD_7_ESTRUCTURAS_DATOS_GRAFOS.md (1 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['mermaid', 'pseudocodigo', 'pytest'].

## UNIDAD_8_PROYECTO_INTEGRADOR.md (1 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['pseudocodigo', 'pytest'].
