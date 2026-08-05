# DOCUMENTO MAESTRO: Análisis Completo y Plan de Implementación
## Curso: Lógica de Programación y Desarrollo Agéntico con IA
## UCEMICH — Ingeniería en IA y Nanotecnología — 1er Semestre 2026-2027
### Versión 3.0 Completa | Agosto 2026

---

# PARTE 1: CONTEXTO ESTRATÉGICO

## 1.1 Posicionamiento del Curso en la Trayectoria

Este curso es el PISO 1 de un edificio de dos pisos:

  PISO 2: IA y Nanotecnología
    - Agentes reales (CrewAI, smolagents), simulación molecular, RAG
    - Se asume dominio completo de Python
    CONSTRUIDO SOBRE...
  PISO 1: Lógica de Programación (ESTE CURSO)
    - Fundamentos Python desde cero
    - Hábitos de ingeniería (CLI, Git, pytest)
    - Preview agéntico: qué son agentes, qué es MCP

Contrato de egreso:
"Sé programar en Python. Entiendo cómo funciona una IA.
He construido y probado un mini-agente. Estoy listo para IA y Nanotecnología."

## 1.2 Parámetros Confirmados del Curso

| Parámetro | Valor |
|---|---|
| Nivel de entrada | Cero conocimiento de programación |
| OS | Windows (primario) — comandos en PowerShell |
| Modalidad | Presencial (opción híbrida/online con Colab) |
| Herramientas | IDLE → VS Code → Antigravity IDE + Google Colab |
| GitHub | GitHub Education (Copilot gratuito desde U4) |
| Pseudocódigo | Escrito a mano, sintaxis UCEMICH (NO PseInt software) |
| Diagramas | Mermaid (manual + FlowchartAgent automático) |
| Referencia principal | https://ellibrodepython.com/ (por unidad) |
| TDD | Obligatorio: test fallido primero |
| Política IA | Sin IA U1-U3 → Copiloto U4-U6 → Arquitecto U7-U8 |
| Unidad 0 | Incluida como unidad oficial numerada |

---

# PARTE 2: DIAGNÓSTICO PEDAGÓGICO — ALUMNO CERO-CONOCIMIENTO

## 2.1 Semáforo por Unidad

| Unidad | OK cero-conocimiento | Problema principal |
|---|---|---|
| U1 | Sí (conceptual) | Falta aviso política sin IA |
| U2 | NO | pytest antes de ver una función; pseudocódigo = 0 menciones |
| U3 | PARCIAL | Primer código = lista anidada compleja |
| U4 | Sí | Falta protocolo explícito del primer uso de IA |
| U5 | NO | RK4 antes de un for simple; banderas = 0 menciones |
| U6 | PARCIAL | Lambda, *args, **kwargs completamente ausentes |
| U7 | Sí | La más completa. Solo necesita rúbrica |
| U8 | Sí (como meta) | Sin plantilla README ni rúbrica de defensa |

## 2.2 Las 8 Evidencias de Desajuste (con datos reales del código)

1. NO EXISTE "Hello World": El primer código Python (U3) son coordenadas
   moleculares con List[List[float]], type hints y química. Un alumno de
   primer semestre no tiene ninguno de estos conocimientos previos.

2. U2 TIENE 0 LLAMADAS A print(): Va directo a pytest, OWASP y formulación
   formal. Un alumno no puede entender "prueba unitaria" sin haber visto
   una función primero.

3. PSEUDOCÓDIGO = 0 MENCIONES en los 8 MDs: El programa v2 sección 2.2
   lo exige explícitamente. No está en ninguna unidad.

4. U5 USA RK4 PARA ENSEÑAR UN for: Runge-Kutta de 4to orden requiere
   cálculo diferencial (3er-4to semestre). No hay ni un solo ejemplo de
   for o while de 3-5 líneas antes de RK4.

5. BANDERAS (flags) = 0 MENCIONES en U5: El programa v2 sección 5.1
   dice "contadores, acumuladores y BANDERAS". Contadores y acumuladores
   sí están, pero banderas no existen.

6. LAMBDA, *ARGS, **KWARGS = 0 EN U6: El programa v2 sección 6.2 los
   exige explícitamente. Completamente ausentes del MD.

7. RÚBRICAS = 0 EN TODOS LOS ARCHIVOS: Con banco de 113 preguntas,
   el alumno sabe qué se preguntará pero no cómo se evaluará.

8. POLÍTICA DE IA INVISIBLE EN MATERIALES: La regla "sin IA en U1-U3"
   existe en el programa v2 pero no hay ningún aviso en los MDs de U1, U2, U3.

## 2.3 Métricas Cuantitativas del Contenido Actual

| Unidad | Palabras | Bloques Python | Analogías | Preguntas examen |
|---|---|---|---|---|
| U1 | 7,655 | 3 | 4 | 4 |
| U2 | 9,593 | 9 | 6 | 18 |
| U3 | 10,861 | 18 | 0 | 18 |
| U4 | 8,351 | 16 | 3 | 17 |
| U5 | 9,197 | 4 | 4 | 17 |
| U6 | 9,366 | 4 | 6 | 19 |
| U7 | 9,742 | 5 | 5 | 17 |
| U8 | 9,988 | 5 | 1 | 3 |
| TOTAL | 74,753 | 64 | 29 | 113 |

Observaciones clave:
- U3 tiene 0 analogías (la unidad más densa en código y más difícil de entrada)
- U8 solo tiene 3 preguntas de examen (insuficiente para el proyecto integrador)
- U5 tiene solo 4 bloques Python para 4 semanas (necesita escalera básica urgente)

---

# PARTE 3: COBERTURA DEL PROGRAMA v2 VS MATERIALES ACTUALES

## 3.1 Brechas Curriculares Exactas (sin esto el programa no se cumple)

BRECHA B1 — U2.2 PSEUDOCÓDIGO (AUSENTE TOTAL):
  Programa v2 dice: "pseudocódigo estructurado"
  Estado: 0 menciones. Falta sintaxis del curso, tabla de convenciones,
  prueba de escritorio y flujo Pseudocódigo → Mermaid → Python → pytest.

BRECHA B2 — U5.1 BANDERAS (AUSENTE TOTAL):
  Programa v2 dice: "contadores, acumuladores y BANDERAS"
  Estado: 0 menciones de banderas/flags. También falta escalera básica.

BRECHA B3 — U6.2 LAMBDA/*ARGS/**KWARGS (AUSENTE TOTAL):
  Programa v2 dice: "funciones lambda, argumentos opcionales, empaquetamiento"
  Estado: completamente ausente del MD de U6.

BRECHA B4 — U8.3 README Y GITHUB (INCOMPLETO):
  Programa v2 dice: "documentación técnica y README del repositorio en GitHub"
  Estado: no hay plantilla ni guía de GitHub para el proyecto final.

BRECHA B5 — U8.4 RÚBRICA DEFENSA ORAL (INCOMPLETO):
  Programa v2 dice: "defensa oral, 20% de la calificación"
  Estado: no hay criterios, rúbrica ni preguntas modelo.

BRECHA B6 — POLÍTICA DE IA INVISIBLE:
  Sección 6.1 del programa define la política por entregable.
  En los MDs de U1, U2 y U3 no hay ningún aviso visible.

BRECHA B7 — SISTEMA DE EVALUACIÓN NO INTEGRADO EN MDs:
  35% labs, 25% exámenes, 20% defensa, 10%+10% no aparecen
  en ningún MD ni README.

---

# PARTE 4: FORTALEZAS A PRESERVAR (NO CAMBIAR)

FlowchartAgent (AST → Mermaid):
  ÚNICO EN EL MERCADO. No existe en ningún otro curso introductorio
  de primer semestre en México/Latinoamérica. Es el diferenciador
  tecnológico más potente del proyecto.

MCP en primer semestre:
  VANGUARDIA ABSOLUTA. La mayoría de universidades no tienen MCP
  ni en últimos semestres. Prepara al alumno para el mercado 2026-2030.

Política progresiva de IA:
  Manual → Copiloto → Arquitecto es la progresión pedagógica correcta.

Contexto nanotecnológico:
  Motivación real e identidad del programa de la carrera.

CodeAuditorAgent + OWASP:
  Seguridad desde el primer semestre. Práctica inusual y valiosa.

Analogías didácticas (conservar todas):
  - Mansión/habitaciones → filesystem (U1)
  - Piloto automático → Vibe Coding (U1)
  - Bloques LEGO → tokens (U1)
  - Álbum fotográfico → Git (U1)
  - Río con compuertas → if/elif/else (U4)
  - Pista atletismo vs lluvia → for vs while (U5)

Notebooks existentes (77-93 KB cada uno):
  Base sólida generada. U1: 77.1 KB | U2: 93.2 KB | U3: 92.6 KB
  U4: 81.3 KB | U5: 79.2 KB | U6: 84.6 KB | U7: 85.2 KB | U8: 87.7 KB

---

# PARTE 5: ESTADO ACTUAL DEL SISTEMA DE AGENTES

TutorAgent (4.3 KB) — USA KEYWORD MATCHING (limitado)
  Problema: no entiende preguntas con sinónimos o formulaciones alternativas.
  Pendiente: reemplazar con ChromaDB embeddings.

CodeAuditorAgent (6.9 KB) — BIEN IMPLEMENTADO
  Audita PEP8, OWASP y estructura con AST. Conservar.

FlowchartAgent (6.1 KB) — ÚNICO Y EXCELENTE
  Genera Mermaid desde AST de funciones Python. Conservar.

NotebookCompilerAgent (6.1 KB) — BIEN IMPLEMENTADO
  Convierte MD a .ipynb. Conservar.

AGENTES NUEVOS A IMPLEMENTAR:
  OrchestratorAgent: coordina los 4 existentes + EvaluatorAgent.
    Input: código del alumno + N° de unidad
    Output: reporte pedagógico unificado en Markdown

  EvaluatorAgent: califica contra rúbrica de la unidad.
    Retroalimentación inmediata y específica por criterio.

  PseudocodeAgent: convierte entre pseudocódigo y Python.
    Pseudocódigo UCEMICH → Mermaid
    Python AST → Pseudocódigo estilo UCEMICH
    Pseudocódigo → Esqueleto Python (type hints + docstring)

---

# PARTE 6: DISEÑO PEDAGÓGICO ORIGINAL

## 6.1 Filosofía: Pensar → Codificar → Orquestar

PENSAR    → Pseudocódigo escrito + Diagrama Mermaid
CODIFICAR → Python manual (U1-U3) → Python + Copiloto (U4-U6)
ORQUESTAR → Conexión con LLMs y agentes (preview del siguiente curso)

## 6.2 Plantilla TAPECA (todas las unidades)

| T | Teoría | Concepto + contexto nano + analogía |
| A | Algoritmo | Pseudocódigo + Mermaid |
| P | Python | Código graduado 3 niveles |
| E | Evaluación | Rúbrica + banco de preguntas |
| C | Copiloto | Política IA + ejemplo de prompt de calidad |
| A | Agente | Conexión con LLMs y sistemas agénticos |

## 6.3 El Hilo de Oro

Pseudocódigo → Mermaid → Python → pytest
(aplicar en cada concepto nuevo del curso)

## 6.4 Convención de Pseudocódigo UCEMICH 2026

INICIO / FIN
LEER variable
ESCRIBIR "texto", variable
variable <- expresión
SI condición ENTONCES ... SINO ... FIN_SI
PARA i DESDE inicio HASTA fin HACER ... FIN_PARA
MIENTRAS condición HACER ... FIN_MIENTRAS
FUNCIÓN nombre(parámetros) ... RETORNAR valor ... FIN_FUNCIÓN

## 6.5 Política de IA por Unidad

| Unidades | Nivel permitido |
|---|---|
| U1, U2, U3 | SIN IA para código. Solo consultas conceptuales |
| U4, U5, U6 | GitHub Copilot habilitado. Documentar prompt en README |
| U7, U8 | IA como herramienta principal. Alumno audita y defiende |
| Examen | CERO IA. Solo lectura, corrección y trazabilidad manual |
| Defensa oral | CERO IA |

---

# PARTE 7: PLAN DE IMPLEMENTACIÓN EXACTO (5 DÍAS)

## DÍA 1 — FASE 1: Infraestructura Base

[ ] 1.1 Actualizar environment.yml:
    name: ia_logprog, python=3.11, jupyterlab, numpy, networkx,
    matplotlib, pytest, ipytest, mcp, fastmcp, chromadb,
    google-generativeai, rich, pydantic

[ ] 1.2 Crear UNIDAD_0_ENTORNO_Y_PRIMER_PROGRAMA.md:
    - Herramientas y cuándo usar cada una (IDLE/VSCode/Colab/Antigravity)
    - Instalación Windows paso a paso (Python 3.11 + Add to PATH)
    - Primer programa en IDLE: print("Bienvenido a UCEMICH")
    - conda env create -f environment.yml + conda activate ia_logprog
    - GitHub Education: education.github.com/students
    - Guía de PowerShell básico (dir, cd, mkdir, python)
    - Política de IA del semestre (tabla completa)
    - Checklist de verificación del entorno (10 ítems)
    - Link: /introduccion-python · /hola-mundo-python

[ ] 1.3 Crear CHEATSHEET_PYTHON_LOGPROG.md:
    Tipos, control flujo, funciones, errores comunes,
    comandos PowerShell, links ellibrodepython.com por tema

[ ] 1.4 Crear RUBRICA_GENERAL.md:
    Porcentajes del semestre, rúbrica genérica 4×4,
    rúbrica defensa oral 5×4, 5 preguntas modelo defensa

[ ] 1.5 Crear data/ con:
    nanoparticulas_ejemplo.csv (20 filas: radio_nm, material, temp_K, morfologia)
    molecula_agua.json (coordenadas H2O con metadata)
    red_cristalina_Au.json (grafo nodos/aristas para U7)
    data/README.md (descripción y cómo cargar cada dataset)

## DÍA 2 — FASE 2: MDs U1-U4

[ ] U1: Aviso [!IMPORTANT] política sin IA + sección PowerShell Windows
        + links ellibrodepython al final de cada sección teórica

[ ] U2: Sección 2.2 COMPLETA — pseudocódigo:
        Tabla de convenciones UCEMICH, ejemplo volumen nanopartícula
        en pseudocódigo, diagrama Mermaid, traducción a Python, pytest,
        tabla de prueba de escritorio
        + link /python-built-in

[ ] U3: Sección 3.0 — entrada gradual ANTES del primer código avanzado:
        print simple → variable → variable con cálculo
        Metodología 4 pasos: ecuación → código
        + links /entero-en-python · /float-python · /booleano-python · /cadenas-python

[ ] U4: Aviso [!TIP] hito primer uso copiloto
        Protocolo 4 pasos para usar IA con rigor
        Plantilla documentación IA en README del entregable
        + links /if-python · /match-python

## DÍA 3 — FASE 2: MDs U5-U8

[ ] U5: Sección 5.1 COMPLETA con BANDERAS:
        Contador + acumulador + bandera (ejemplo con radios de nanopartículas)
        Escalera básica ANTES del RK4:
          Peldaño 1: for simple con print (5 líneas)
          Peldaño 2: while simple de enfriamiento
          Peldaño 3: contador + acumulador + bandera combinados
          Peldaño 4 (ya existe): Euler → RK4 → AgenticLoop
        + links /for-python · /while-python · /range-python · /break-python

[ ] U6: Sección 6.2 COMPLETA:
        Lambda con ordenamiento de nanomateriales
        Argumentos opcionales con valor por defecto
        *args para número variable de posicionales
        **kwargs con conexión explícita a JSON de MCP
        + links /funciones-en-python · /lambda-python · /alcance-variables-python

[ ] U8: Plantilla README.md obligatoria del proyecto MAEC
        Rúbrica defensa oral (5 criterios × 4 niveles)
        5 preguntas modelo que el alumno debe preparar
        Checklist de entrega pre-defensa

## DÍA 4 — FASE 3: Sistema de Agentes (TDD)

[ ] Crear tests PRIMERO (TDD — test fallido antes del código):
    tests/test_orchestrator_agent.py
    tests/test_evaluator_agent.py
    tests/test_pseudocode_agent.py

[ ] Implementar OrchestratorAgent:
    src/multiagent_core/orchestrator_agent.py
    Coordina: CodeAuditorAgent + FlowchartAgent + TutorAgent + EvaluatorAgent
    Output: reporte pedagógico unificado Markdown

[ ] Implementar EvaluatorAgent:
    src/multiagent_core/evaluator_agent.py
    Califica código contra rúbrica de la unidad correspondiente

[ ] Implementar PseudocodeAgent:
    src/multiagent_core/pseudocode_agent.py
    Pseudocódigo UCEMICH → Mermaid
    Python AST → Pseudocódigo UCEMICH
    Pseudocódigo → Esqueleto Python

[ ] Actualizar TutorAgent v2:
    src/multiagent_core/tutor_agent.py
    ChromaDB embeddings para búsqueda semántica real
    Cita la sección exacta del MD donde está la respuesta

## DÍA 5 — FASE 4: Pulido Final

[ ] Actualizar todos los notebooks (badge Colab + celda instalación):
    import sys
    if 'google.colab' in sys.modules:
        pip install -q mcp fastmcp chromadb rich

[ ] Añadir links ellibrodepython.com al final de cada sección
    teórica en todos los MDs y notebooks (tabla de mapeo en Parte 7.2)

[ ] Actualizar README.md:
    Guía de herramientas (cuándo usar IDLE vs VSCode vs Colab vs Antigravity)
    Cómo activar GitHub Education y Copilot
    Cómo usar los 7 agentes desde terminal
    Mapa del semestre (semana × unidad × lab)

[ ] Añadir rúbrica al final de cada MD (4 criterios × 4 niveles)

[ ] Ejecutar y verificar:
    conda activate ia_logprog
    pytest tests\ -v --tb=short
    Meta: 100% de tests pasando

---

# PARTE 8: REFERENCIAS DEL CURSO

| Recurso | URL | Uso |
|---|---|---|
| El Libro de Python | https://ellibrodepython.com/ | Referencia principal en español, por unidad |
| Aprende Python | https://aprendepython.es/ | Referencia secundaria en español |
| OWASP LLM Top 10 | https://owasp.org/www-project-top-10-for-large-language-model-applications/ | U2 — Seguridad |
| MCP Specification | https://modelcontextprotocol.io/ | U6 — MCP y Function Calling |
| Google ADK Docs | https://google.github.io/adk-docs/ | U8 — Proyecto agéntico |

---

# PARTE 9: PRINCIPIOS NO NEGOCIABLES

1. TDD: Test fallido primero. Cero código de producción sin test previo.
2. Escalera de acceso: Cada unidad empieza con el ejemplo más simple.
3. Hilo de oro: Pseudocódigo → Mermaid → Python → pytest en cada concepto.
4. Política de IA visible: Aviso al inicio de U1, U2 y U3.
5. Windows first: PowerShell primero (nota con equivalente bash).
6. Colab ready: Badge y celda condicional en cada notebook.
7. ellibrodepython: Link al final de cada sección teórica.
8. Contexto nano: Cada ejemplo usa datos de nanotecnología.
9. Semillas curriculares: Cada unidad planta lo que IA Nanotecnología profundiza.
10. Fortalezas preservadas: FlowchartAgent, MCP, política progresiva de IA,
    CodeAuditorAgent+OWASP y analogías didácticas NO se modifican sin razón.

---
Documento Maestro v3.0 — Análisis completo + Plan de implementación
Antigravity AI — Agosto 2026 — UCEMICH
Sesiones: 5e66527f (anterior) + b709eb3f (actual)
