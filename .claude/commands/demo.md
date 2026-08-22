---
description: Corre la etapa 0 — transcripción de demo → prospecto.json + qa-demo.json con compuerta de validación
argument-hint: <cliente> [archivo de transcripción, opcional si hay uno solo con sufijo -demo en entrada/]
allowed-tools: Bash, Read, Write, Glob
---

Procesa la demo comercial del cliente **$1**.

Rutas de este proyecto (no cambiarlas):
- S0 = .claude/skills/extraccion-demo
- Transcripción: $2 si se dio; si no, el archivo con sufijo `-demo` de
  clientes/$1/entrada/ (si hay ambigüedad o ninguno lo lleva, pregunta cuál
  antes de arrancar — extraer una sesión estratégica con esta skill produce
  un prospecto falso).

Recuerda las reglas de la casa del CLAUDE.md: los scripts calculan, los
validadores bloquean, las etapas no se contaminan. Esta etapa corre completa,
sin paradas interactivas.

## Etapa 0 — Extracción de la demo

1. Lee S0/SKILL.md y S0/references/schema-prospecto.md COMPLETOS. El guion
   vigente contra el que se audita la ejecución es
   S0/references/guion-demo-v4.1.md (19 bloques: 0, 1.1-1.5, 2-11, FT, 12, 13).
   Si la demo es anterior, registrar `version_guion` v3 o v2026 (13 bloques)
   y auditar contra el guion que corresponda — el mapa canónico está en
   GUION_BLOQUES de S0/scripts/validar_prospecto.py.
2. Extrae el texto de la transcripción (docx → texto plano en /tmp/demo-$1.txt).
   Antes de extraer, resuelve el `_meta`: hablantes reales, ruido del ASR y
   dónde termina la demo efectiva (el audio ambiente posterior no se procesa
   como demo; se registra con fuente `audio_ambiente` y jamás se cita ante el
   cliente).
3. Escribe clientes/$1/salida/prospecto-$1-<fecha>.json. Reglas madre: lo no
   dicho = "no_capturado" con motivo de ausencia; TODO dato lleva fuente y los
   de fuente ejecutivo_* / cliente_asintio / cliente_forzado_por_menu son
   hipótesis, nunca datos del cliente.
4. COMPUERTA: !`python3` S0/scripts/validar_prospecto.py clientes/$1/salida/prospecto-$1-<fecha>.json
   Exit 1 bloquea: se corrige el archivo, jamás se relaja el contrato. Las
   advertencias se reportan textuales.
5. QA (los scores los escribe el script, nunca el modelo):
   !`python3` S0/scripts/qa_demo.py clientes/$1/salida/prospecto-$1-<fecha>.json -o clientes/$1/salida/qa-demo-$1-<fecha>.json

## Entrega final, siempre en este formato

1. Tabla de los dos archivos con su ruta y su línea de validación.
2. agenda_diagnostico priorizada: bloqueantes primero, luego altas.
3. Brief previo listo para WhatsApp: solo ítems con momento: brief_previo,
   redactados como mensaje, excluyendo lo ya declarado en la demo.
4. bloqueos_para_avanzar + hipótesis a verificar en pantalla.
5. Resumen del QA: score global, semáforo, top-3 acciones de coaching.
