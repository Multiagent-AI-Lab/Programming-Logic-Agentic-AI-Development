# RÚBRICA GENERAL DEL SEMESTRE
**Curso:** Lógica de Programación y Desarrollo Agéntico con IA
**Institución:** UCEMICH — Ingeniería en Inteligencia Artificial y Nanotecnología
**Nivel:** Primer Semestre

---

## 📊 Ponderación de la Calificación Final

| Componente | Porcentaje | Descripción |
| :--- | :--- | :--- |
| Laboratorios (labs por unidad) | 35% | Entregables prácticos U1–U8, evaluados con la rúbrica genérica 4×4 de este documento |
| Exámenes | 25% | Evaluaciones escritas/prácticas por bloque de unidades (sin uso de IA) |
| Defensa oral del proyecto integrador | 20% | Evaluada con la rúbrica de defensa oral 5×4 de este documento (Unidad 8) |
| Participación y avance continuo | 10% | Asistencia a checkpoints, cumplimiento de entregas parciales |
| Documentación técnica (README, control de versiones) | 10% | Calidad del README, historial de commits, trazabilidad de uso de IA |

**Total: 100%**

---

## 🧩 Rúbrica Genérica de Laboratorio (4 criterios × 4 niveles)

Aplica como base a los laboratorios de todas las unidades (U1–U8). Cada unidad puede añadir criterios específicos adicionales en su propio MD.

| Criterio | Insuficiente (0-59) | En desarrollo (60-74) | Competente (75-89) | Sobresaliente (90-100) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Corrección lógica** | El código no ejecuta o produce resultados incorrectos en la mayoría de los casos. | Ejecuta pero falla en casos borde o entradas no triviales. | Ejecuta correctamente para el caso general y casos borde comunes. | Ejecuta correctamente en todos los casos, incluyendo validación explícita de entradas inválidas. |
| **2. Proceso (Hilo de Oro)** | No hay evidencia de pseudocódigo, diagrama ni pruebas previas al código. | Pseudocódigo o diagrama presentes pero desconectados del código final. | Pseudocódigo → Mermaid → Python coherentes entre sí. | Pseudocódigo → Mermaid → Python → pytest completo y trazable (TDD real: test antes que implementación). |
| **3. Calidad de código** | Sin type hints, nombres poco claros, código no sigue PEP 8. | Type hints parciales, nombres aceptables, algunas violaciones de estilo. | Type hints completos en funciones públicas, PEP 8 cumplido, funciones cohesivas. | Además de lo anterior: docstrings completos, sin números mágicos, manejo explícito de errores. |
| **4. Pruebas (pytest)** | Sin pruebas o pruebas que no ejecutan. | Pruebas presentes pero cobertura mínima (solo camino feliz). | Pruebas cubren camino feliz y al menos un caso borde/error. | Cobertura ≥80%, pruebas nombradas descriptivamente, incluye casos de error explícitos. |

**Cálculo de la calificación del laboratorio:** promedio simple de los 4 criterios, salvo que la unidad específica indique una ponderación distinta.

---

## 🎤 Rúbrica de Defensa Oral (5 criterios × 4 niveles) — Unidad 8

| Criterio | Insuficiente (0-59) | En desarrollo (60-74) | Competente (75-89) | Sobresaliente (90-100) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Dominio conceptual** | No puede explicar qué hace su propio código. | Explica el "qué" pero no el "por qué" de las decisiones de diseño. | Explica qué, cómo y por qué de las decisiones principales. | Explica además los trade-offs considerados y alternativas descartadas. |
| **2. Trazabilidad del uso de IA** | No documenta si usó IA ni cómo. | Menciona uso de IA sin evidencia (prompts, README). | Documenta prompts usados y qué auditó/corrigió del código generado. | Explica con precisión los límites de lo que la IA generó vs. lo que el alumno diseñó y validó. |
| **3. Respuesta a preguntas improvisadas** | No responde o responde con IA en el momento (prohibido en defensa). | Responde con ayuda extensa del docente. | Responde con precisión a preguntas directas sobre su código. | Responde con precisión y conecta la respuesta a conceptos de otras unidades. |
| **4. Calidad técnica del proyecto integrador (MAEC)** | Proyecto no ejecuta o incumple requisitos mínimos. | Ejecuta con errores menores o funcionalidad incompleta. | Ejecuta correctamente y cumple todos los requisitos del proyecto. | Además incluye pruebas, manejo de errores y documentación de nivel profesional. |
| **5. Comunicación técnica** | Explicación desorganizada, uso incorrecto de terminología. | Explicación comprensible pero con imprecisiones terminológicas. | Explicación clara, ordenada, con terminología técnica correcta. | Explicación clara, estructurada (contexto → problema → solución → resultado) y adaptada a la audiencia. |

---

## ❓ 5 Preguntas Modelo para Preparar la Defensa Oral

1. **¿Por qué elegiste esta estructura de datos (lista, diccionario, grafo) para modelar tu problema de nanotecnología, y qué alternativa consideraste?**
2. **Muéstrame en tu código dónde usaste IA (Copiloto) y explica qué tuviste que corregir o auditar de lo que generó.**
3. **Si el archivo de entrada tuviera un dato inválido o faltante, ¿qué pasaría con tu programa? Muéstramelo.**
4. **Explica el flujo completo de tu proyecto: pseudocódigo → diagrama → código → prueba. ¿En qué paso encontraste más errores y por qué?**
5. **¿Qué parte de tu proyecto integrador (MAEC) reutilizarías directamente en el curso de IA y Nanotecnología (segundo semestre), y qué cambiarías?**

---

## 📌 Notas de Aplicación

- Esta rúbrica genérica es la **base**; unidades individuales (U1–U8) pueden agregar criterios propios sin sustituir estos 4/5 criterios centrales.
- La política de IA por unidad (ver `lecciones/UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md`, sección de Política de IA) determina qué tan estrictamente se evalúa el criterio de "Trazabilidad del uso de IA": en U1–U3 se espera cero uso de IA en el código entregado.
- En exámenes y defensa oral, cualquier evidencia de uso de IA durante la evaluación implica calificación de 0 en el criterio correspondiente.

---

## 🤖 Flujo de Calificación para el Docente (OrchestratorAgent)

Para agilizar la calificación y mantener consistencia entre entregas, usa `OrchestratorAgent` desde terminal (o un script/notebook propio, no destinado al alumno):

```python
from pathlib import Path
from src.multiagent_core.orchestrator_agent import OrchestratorAgent

orchestrator = OrchestratorAgent()

# Lee el código entregado por el alumno desde su archivo
codigo_alumno = Path("entregas/alumno_x/solucion.py").read_text(encoding="utf-8")
test_file = Path("entregas/alumno_x/test_solucion.py")  # opcional

reporte = orchestrator.generate_pedagogical_report(
    codigo_alumno, unit_number=5, test_file_path=test_file
)
print(reporte)
```

El reporte generado incluye automáticamente:
- Auditoría de estilo (PEP 8) y seguridad (OWASP), omitida si la entrega es pseudocódigo.
- Diagrama de flujo Mermaid autogenerado (desde Python o desde pseudocódigo, según lo que el `OrchestratorAgent` detecte).
- Calificación contra los 4 criterios de la Rúbrica Genérica de Laboratorio de este documento.

Guarda el reporte como parte del expediente de la entrega:

```python
Path("entregas/alumno_x/reporte_evaluacion.md").write_text(reporte, encoding="utf-8")
```

Este flujo es **complementario, no sustituto**, del criterio "Proceso (Hilo de Oro)" de la rúbrica — ese criterio requiere revisión humana del pseudocódigo y diagrama entregados, ya que `EvaluatorAgent` no puede verificarlo automáticamente (ver `src/multiagent_core/evaluator_agent.py`, método `_evaluar_proceso`).
