---
description: Corre la cadena completa transcripción → ficha → diagnóstico → propuesta.json con compuertas de validación entre etapas
argument-hint: <cliente> [archivo de transcripción, opcional si hay uno solo en entrada/]
allowed-tools: Bash, Read, Write, Glob
---

Corre el pipeline de diagnóstico Ropofy para el cliente **$1**.

Rutas de este proyecto (no cambiarlas):
- S1 = .claude/skills/extraccion-diagnostico
- S2 = .claude/skills/evaluacion-modular
- S3 = .claude/skills/seleccion-propuesta
- POLITICA = politica-comercial.json (si falta o está incompleta: DETENTE y pídela)
- Transcripción: $2 si se dio; si no, los archivos de clientes/$1/entrada/ (si hay ambigüedad, pregunta cuáles antes de arrancar).

Recuerda las reglas de la casa del CLAUDE.md: los scripts calculan, los
validadores bloquean, las etapas no se contaminan.

## Etapa 1 — Extracción
1. Lee S1/SKILL.md y S1/references/ficha-perfil-cliente.md completos.
2. Extrae el texto de la transcripción (docx → texto plano en /tmp/trans-$1.txt).
3. Escribe clientes/$1/salida/ficha-$1.json (regla madre: lo no dicho = "no_capturado").
4. COMPUERTA 1: !`python3` S1/scripts/validar_ficha.py clientes/$1/salida/ficha-$1.json /tmp/trans-$1.txt
5. Auto-revisión J1–J6 (S1/references/criterios-evaluacion.md): una línea por
   criterio — pasa / duda concreta.

## Etapa 2 — Evaluación
1. Lee S2/SKILL.md, S2/references/catalogo-fugas.md COMPLETO y el schema.
2. Compuerta de entrada: revalida la ficha (S1/scripts/validar_ficha.py).
3. Escribe clientes/$1/salida/diagnostico-$1.json: fugas solo con ids del catálogo, UNA
   dominante, madurez de 7 módulos con por_que citando la ficha, silencios
   leídos como madurez, cero doble conteo.
4. Nota SIEMPRE por script: python3 S2/scripts/calcular_nota.py clientes/$1/salida/diagnostico-$1.json
5. COMPUERTA 2: python3 S2/scripts/validar_diagnostico.py clientes/$1/salida/diagnostico-$1.json S2/references/catalogo-fugas.md clientes/$1/salida/ficha-$1.json
   (los ⚠ de citas se revisan a mano; los ✖ se corrigen siempre)

## Etapa 3 — Selección y propuesta
1. Lee S3/SKILL.md y S3/references/schema-propuesta.md; ten los módulos de
   S3/references/modulos/ a la vista para los aplica_si dudosos.
2. Compila la librería: python3 S3/scripts/compilar_libreria.py S3/references/modulos libreria/componentes.json
   Si falla: detente, librería rota no se selecciona.
3. Compuertas de entrada: revalida ficha Y diagnóstico.
4. Escribe clientes/$1/salida/propuesta-$1-v1.json:
   - aplica_si evaluado componente por componente (decisión semántica tuya).
   - no_aplican con razón en lenguaje del cliente, jamás ids internos.
   - Carril de integraciones con etiqueta de costo (V11: lo no nativo no viaja
     en el plan; su evaluación técnica sí).
   - Hereda fugas/madurez/nota/modo del diagnóstico SIN editar.
   - Copia base_por_plan, tramos_factor y límite desde POLITICA a
     condicion_comercial; deja precio_por_plan vacío.
   - plan_recomendado con por_que (regla base: el plan cuya madurez cierra la
     dominante).
   - Instancias compartidas conocidas: fíjalas a mano con
     instancias_fijadas_por_consultor: true.
5. Números SIEMPRE por script: python3 S3/scripts/calcular_condicion.py clientes/$1/salida/propuesta-$1-v1.json clientes/$1/salida/ficha-$1.json
6. COMPUERTA 3: python3 S3/scripts/validar_propuesta.py clientes/$1/salida/propuesta-$1-v1.json libreria/componentes.json clientes/$1/salida/diagnostico-$1.json

## Entrega (formato fijo)
1. Tabla de los 3 JSON con su línea de validación (✔/✖) y ruta.
2. "Agenda de la segunda llamada": los no_capturado priorizados — primero los
   que cambian plan o precio.
3. "Decisiones humanas pendientes": plan recomendado (tu propuesta y por qué),
   ajustes manuales de instancias, advertencias en pie.
4. NO generes HTML ni lienzo: el renderizador consume propuesta.json en otra app.
