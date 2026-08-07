# Reporte de Auditoría de Contenido

**Total de hallazgos en 9 unidades: 31**

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

## UNIDAD_5_CICLOS_BUCLES_AGENTICOS.md (4 hallazgos)

### Pedagogico
- Ciclo del Hilo de Oro incompleto (Pseudocódigo → Mermaid → Python → pytest): faltan bloques de tipo ['pseudocodigo', 'pytest'].

### Codigo
- Error de sintaxis crítica al parsear código para análisis de seguridad: unexpected indent (<unknown>, line 1)
- Riesgo de Seguridad: Uso de `exec()`. Ejecutar cadenas de texto arbitrarias expone al sistema a inyecciones de código y ejecución remota de comandos no autorizados (Riesgo OWASP LLM-02).
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
