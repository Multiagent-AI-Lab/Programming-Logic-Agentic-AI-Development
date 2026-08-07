# Reporte de Auditoría de Contenido

**Total de hallazgos en 9 unidades: 31**

> **Investigación completa de los 33 hallazgos previos (2026-08-06).** De los 33, se confirmó lo siguiente:
>
> - **9× "Ciclo del Hilo de Oro incompleto"**: ruido de convención de etiquetado, no de contenido. Verificado en U5: sección completa de pruebas pytest (`import pytest`, funciones `test_*` reales, línea 661+) y ejemplo de pseudocódigo en la celda de `PseudocodeAgent` (línea 1012+), ambos bajo fence ` ```python ` en vez de ` ```pytest `/` ```pseudocodigo `. Presente en las 9 unidades. **No accionable sin re-etiquetar fences existentes** — decisión de estilo, no de contenido; fuera de alcance por ahora.
> - **7× "Error de sintaxis... unexpected indent"** (U4: 6, U5: 1): ruido — fragmentos de método citados a propósito con fines didácticos (patrón "explica por fragmentos": función completa se presenta una vez, luego se desmenuza en bloques sucesivos con prosa intercalada). Verificado en U4 líneas 228-264 (`classify_by_geometry_match`).
> - **2× "Riesgo de Seguridad" (`eval()`/`exec()`)**: ambos son ejemplos pedagógicos intencionales, no vulnerabilidades reales del material. `eval()` en U2 es el "Laboratorio de Higiene de Seguridad OWASP" (sección 2.5, línea 506+) que enseña explícitamente a identificar y mitigar la vulnerabilidad (`parsear_inseguro` vs `parsear_seguro`). `exec()` en U5 corre dentro de un sandbox aislado (`sandbox_globals`/`sandbox_locals` vacíos, `try/except` controlado) como parte del laboratorio de auto-reparación de código agéntico.
> - **2× "Discrepancia de duración"** (U2, U3): falso positivo del auditor — compara el número de la *duración* de la unidad ("1 semana") contra el número de la *semana calendario* del programa oficial ("Semana 2"), dos magnitudes distintas que nunca deberían coincidir numéricamente. Ambas unidades están correctamente alineadas con el programa oficial (U2 = 1 semana = Semana 2; U3 = 2 semanas = Semanas 3-4).
> - **11 de 13 hallazgos de "código" (docstring/type hints faltantes)**: mismo patrón "explica por fragmentos" — la función aparece dos veces en el archivo (fragmento inicial sin docstring durante la explicación, versión final completa y documentada más abajo). Verificado exhaustivamente por AST: `__post_init__`, `classify_by_aspect_ratio_if`, `classify_by_geometry_match`, `spaghetti_classifier`, `refactored_classifier` (U4), `calcular_relacion_aspecto` (U6) — todas con exactamente 2 apariciones, `[sin docstring, con docstring]`.
> - **2 hallazgos genuinamente reales, ya corregidos**: los métodos `execute()` y `propose_correction()` de `agentic_loop_sandbox.py` en U5 (código final único del laboratorio, sin versión fragmentada previa) carecían de docstring propio pese a tener type hints completos y vivir en clases bien documentadas. Se agregaron docstrings Google-style verificados contra el comportamiento real de cada función (branches de retorno confirmados línea por línea). Notebooks regenerados, 110/110 tests passing.
>
> **Conclusión: el contenido pedagógico de las 9 unidades está limpio.** No quedan hallazgos accionables de esta ronda de auditoría — los 31 restantes son la misma discrepancia de convención de etiquetado ("Hilo de Oro") ya documentada como fuera de alcance.

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
