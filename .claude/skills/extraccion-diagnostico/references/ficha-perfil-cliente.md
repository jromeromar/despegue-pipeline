# Ficha de perfil del cliente — v0.3

Contrato de datos de la etapa 1. Alimenta `aplica_si`, `se_instancia_por` y la
selección de alcance de la etapa 3. Actualizada con los hallazgos del piloto
Activos por Colombia (ago-2026) y de la sesión Bifteki (ago-2026), que costó la
sección de nombres propios.

---

## _meta — de dónde salió la ficha

| Campo | Tipo | Notas |
|---|---|---|
| `cliente` | texto | El nombre con el que viaja el expediente. Misma cadena que `marca.grafia`: si difieren, alguien corrigió una y olvidó la otra. |
| `fuentes` | [texto] | Una entrada por sesión: fecha, duración y quién habló. |
| `extraido_por` | texto | La etapa que la produjo. |
| `regla` | texto | La regla madre, escrita en el archivo para que se lea sola. |
| `version_ficha` | texto | Contra qué versión de este contrato se extrajo. |
| `marca` | objeto | La grafía de la marca comercial y su estado (**nuevo v0.2.2** — ver abajo). |
| `razon_social` | objeto | La grafía de la razón social y su estado, misma forma que `marca` (**nuevo v0.3**). Es un dato distinto: «BIFTEKI S.A.S.» no es «Gosen casa de Comidas». Si la sesión no la dijo, `grafia: "no_capturado"` con `estado: "por_confirmar"`. |

## Nombres propios: grafía, estado y variantes (v0.3)

Las transcripciones automáticas transcriben fonéticamente, y la ficha es donde una
grafía equivocada empieza su viaje hasta la propuesta que el cliente lee. Lo que
trajo la sesión Bifteki (18-ago-2026):

| lo que era | lo que trajo la transcripción |
|---|---|
| la marca «Gosen casa de Comidas» (Gosen es un apellido) | «Gocé en casa de comidas» · «G o SEN casa de comidas» |
| la telefonista | «Sharina» · «Yanina» · «¿Te dices Danina?» — tres grafías en los primeros ocho segundos |
| el sistema «Pixo Gestión» | «It's pizza» · «BXO» · «Pitso» · «Bitso» |
| «Ropofy» | «Robofive» |

Cuatro clases de nombre propio y un mismo patrón: **grafía + estado + variantes
literales**. Cuatro lugares donde se declara:

| dónde | forma |
|---|---|
| `_meta.marca` | objeto `{ grafia, estado, variantes_en_transcripcion, fuente_escrita? }` |
| `_meta.razon_social` | el mismo objeto |
| `B_estructura.personas_declaradas[]` | los campos `grafia_estado` y `variantes_en_transcripcion` (+ `fuente_escrita?`) junto a `nombre` |
| `D_stack.sistemas[]` | los mismos dos campos junto a `nombre` |

**Por qué el campo se llama distinto según dónde esté.** En `marca` y
`razon_social` el estado es del objeto entero y se llama `estado`. En personas y
sistemas el nombre es un string dentro de una fila que **ya usa `estado` para otra
cosa** (un sistema es `activo · abandonado · apagado`): ahí el campo es
`grafia_estado`, para que no se pisen.

Cómo se ve, con el caso Bifteki:

```
"_meta": {
  "cliente": "Gosen casa de Comidas",
  "marca": {
    "grafia": "Gosen casa de Comidas",
    "estado": "por_confirmar",
    "variantes_en_transcripcion": ["Gocé en casa de comidas", "G o SEN casa de comidas"]
  },
  "razon_social": {
    "grafia": "BIFTEKI S.A.S.",
    "estado": "confirmada",
    "variantes_en_transcripcion": ["Bifteki", "BIFTEKI S.A.S."],
    "fuente_escrita": "factura de venta compartida en la sesión"
  }
}

"personas_declaradas": [
  { "nombre": "Sharina", "funcion": "asesor", "cargo": "Telefonista", "presente": true,
    "grafia_estado": "por_confirmar",
    "variantes_en_transcripcion": ["Sharina", "Yanina", "Danina"] }
]

"sistemas": [
  { "nombre": "Pixo Gestión", "rol": "software de gestión del local", "estado": "activo",
    "grafia_estado": "por_confirmar",
    "variantes_en_transcripcion": ["It's pizza", "BXO", "Pitso", "Bitso"] }
]
```

### Los campos

| Campo | Notas |
|---|---|
| `grafia` (en `_meta`) / `nombre` (en las filas) | La grafía que viaja a los entregables. Es la mejor que hay hoy, no necesariamente la correcta: eso lo dice el estado. |
| `estado` / `grafia_estado` | `confirmada` — alguien de la empresa la escribió y **se vio escrita**. · `por_confirmar` — solo se oyó en la sesión: una transcripción automática no es evidencia de ortografía. |
| `variantes_en_transcripcion` | [texto] — las grafías literales que trae la transcripción, copiadas tal cual y **sin corregirlas**. Con estado `por_confirmar` tiene **al menos una entrada**: algo se oyó, y eso es la prueba de la duda. Si la transcripción es consistente, la entrada es esa única grafía. **Cambia respecto de v0.2.2**, donde se permitía `[]`. Única excepción: cuando la grafía es `"no_capturado"` —el nombre nunca salió en la sesión— va `[]`, porque no hay nada que probar. |
| `fuente_escrita` | Obligatorio cuando el estado es `confirmada`: **dónde se vio escrita**, concreto — «firma del correo de Santiago Odasso», «factura de venta», «el sitio bifteki.co», «el contrato firmado». Sin fuente no hay confirmación. |

### Qué NO confirma una grafía

- **Oírla en la sesión**, por clara que suene o por muchas veces que se repita.
- **El título de la grabación o de la invitación de Teams** — «Sesión estratégica
  Ropofy - BIFTEKI S.A.S. - Santiago Odasso». Parece fuente escrita y es la trampa
  más fácil de pisar: lo escribió quien creó la reunión, que casi siempre es
  Ropofy. Confirma cómo lo escribe Ropofy, no cómo lo escribe el cliente.
- **Que la grafía se vea bien o suene lógica.** Elegir la variante que "tiene más
  sentido" es inferir, y no se hace ni siquiera cuando el error es obvio.

### Reglas duras

1. `_meta.cliente` y `_meta.marca.grafia` son la misma cadena. Si difieren, alguien
   corrigió una y olvidó la otra.
2. El nombre de pila que solo se oyó va `por_confirmar`, y **el apellido va
   `por_confirmar` casi siempre**: es lo que la transcripción falla más y lo que
   más se imprime.
3. Ninguna etapa posterior arregla un nombre. La corrección se hace en la ficha,
   en la **compuerta de confirmación de nombres** al cierre de la etapa 1 (ver
   `SKILL.md`), y desde ahí se propaga sola a diagnóstico y propuesta.
4. Ningún script juzga ortografía. `validar_ficha.py` verifica consistencia y
   completitud (bloque I); si el apellido está bien escrito lo decide un humano
   (criterio J2).

### Fichas anteriores a v0.3

Las fichas < v0.3 no llevan `razon_social` ni los campos de personas y sistemas;
las < v0.2.2 tampoco llevan `marca`. El validador **advierte y no bloquea** cuando
la `version_ficha` declarada es anterior: son fichas históricas válidas y el
contrato no se reescribe hacia atrás. Al reprocesarlas se agregan los campos — y
una ficha migrada sale `por_confirmar`, porque migrar no es confirmar: nadie
volvió a mirar la fuente escrita.

## A. Líneas de negocio

Arreglo. Una entrada por línea de ingreso.

| Campo | Tipo | Notas |
|---|---|---|
| `nombre` | texto | |
| `sujeto_del_embudo` | enum | **demandante** (busca comprar/arrendar/contratar) · **oferente** (ofrece un activo: propietario, vendedor de cartera, donante). Cambia el journey completo. |
| `naturaleza` | enum | transaccional · recurrente · mixta |
| `control_del_activo` | enum | **propio** · **tercero_privado** · **tercero_institucional** · **no_aplica**. Decide qué se puede automatizar: agendamiento, precios, disponibilidad. |
| `comparte_base_contactos` | bool | |
| `etapas` | [texto] | Nombres reales del cliente, no los del guión |
| `dependencias_externas_del_proceso` | [objeto] | `{ etapa, tercero, que_controla, sla_real }`. Ej: solicitud de llaves → SAE → disponibilidad → 7-10 días. |
| `mecanismo_de_cierre` | enum | venta_directa · subasta · licitacion · contrato_recurrente. Dos mecanismos = dos pipelines aunque la línea parezca una. |
| `estado_del_catalogo` | objeto | `{ items_publicados_sin_precio: bool, motivo }`. Inventario incompleto por diseño genera carga comercial propia. |
| `ciclo_dias` | número | |
| `momento_de_cobro` | enum | **nuevo v0.4** — `al_pedir` · `contra_entrega` · `mixto` · `no_capturado`. Decide arquitectura, no configuración: la ruta de comercio electrónico de la plataforma exige un pago real registrado, así que un negocio que cobra contra entrega va por el pipeline de Oportunidades. Sin este dato la etapa 3 elige a ciegas entre dos arquitecturas distintas. |
| `ticket_inicial` / `ingreso_recurrente` | moneda | |
| `es_principal` | bool | |

**Canales de distribución no son líneas.** Un MLS de brokers o una red de
afiliados se registra en D (stack) y en B (funciones), no aquí.

## B. Estructura organizacional

| Campo | Tipo | Notas |
|---|---|---|
| `niveles_jerarquicos` | enum | 1 · 2 · 3 · 4+ |
| `funciones_presentes` | multi | captador · asesor · closer · coordinador · aprobador_comercial · revisor_legal · **cumplimiento** · **habilitador_de_activo** · **externo_afiliado** · postventa_administracion · sistema |
| `mapeo_funcion_cargo` | mapa | función → cargo real |
| `personas_por_funcion` | mapa | |
| `personas_declaradas` | [objeto] | `{ nombre, funcion, cargo, presente, grafia_estado, variantes_en_transcripcion, fuente_escrita? }`. Los tres últimos son **nuevos v0.3**: el nombre de una persona es un nombre propio y la transcripción lo destroza igual que la marca (ver §Nombres propios). |
| `puntos_de_aprobacion` | [texto] | Qué requiere autorización explícita para avanzar |
| `dependencias_jerarquicas_externas` | [objeto] | Cadenas de decisión que salen de la empresa. Ej: comercial propio → territorial propia → comercial del tercero → territorial del tercero. Cada eslabón externo es un carril del BPMN que el cliente no controla. |
| `indicadores_impuestos_externamente` | [objeto] | `{ quien_lo_impone, que_mide, que_comportamiento_induce }`. Un indicador externo mal diseñado puede estar destruyendo pipeline (ver F-17). |

Notas sobre las funciones nuevas:
- **cumplimiento**: gateways regulatorios (Sagrilaft, KYC, habeas data). No son
  aprobación comercial; tienen SLA y consecuencias legales propias.
- **habilitador_de_activo**: no aprueba ni supervisa — su disponibilidad
  condiciona el proceso (territorial con llaves, técnico que alista, tasador).
- **externo_afiliado**: brokers, aliados o franquicias que necesitan acceso
  parcial al sistema.

## C. Distribución territorial

| Campo | Tipo |
|---|---|
| `opera_territorios` | bool + [lista] |
| `sedes` | número |
| `asignacion_por_territorio` | bool |
| `el_territorio_condiciona_el_activo` | bool — la disponibilidad del activo depende de una función territorial (llaves, inspección, entrega) |

## D. Stack e integraciones

Tipificado, no texto libre. Tipos: CRM · ERP/contable · facturación · portales o
marketplaces · telefonía · WhatsApp (personal / Business App / API) · firma
electrónica · pasarela de pago · agenda · **plataforma_propia** · **bot_propio**.

Por sistema:

| Campo | Notas |
|---|---|
| `nombre` | |
| `es_fuente_de_verdad` | bool |
| `debe_integrarse` | obligatoria · deseable · no |
| `integrable` | **si · con_esfuerzo · no** — "no" existe: sistemas de terceros con políticas de seguridad que impiden conexión. Se registra la evidencia. |
| `estado` | activo · abandonado · apagado — un bot apagado o un CRM abandonado es historia relevante: dice qué ya falló y por qué. |
| `grafia_estado` | **nuevo v0.3** — `confirmada` · `por_confirmar`, para el nombre del sistema. Es el campo que faltaba: el SKILL.md ya exigía tratar los nombres de sistemas como la marca y no había dónde ponerlo. Caso real: «It's pizza», «BXO», «Pitso» y «Bitso» eran el mismo Pixo Gestión. |
| `variantes_en_transcripcion` | **nuevo v0.3** — [texto] con las grafías literales de la transcripción, sin corregir. Ver §Nombres propios para las reglas. |

**Canal WhatsApp y voz** (nuevo v0.2.1 — determina qué se puede prometer):

| campo | valores |
|---|---|
| `whatsapp_estado` | `app_business` · `api` · `coexistencia` — **decide si las llamadas por WhatsApp son posibles** (R-09) |
| `whatsapp_limite_conversaciones` | tier de la WABA; el canal de voz exige ≥ 2.000/24 h |
| `numeros_publicados` | [{ numero, tipo: fijo/movil, donde_esta_publicado, antiguedad }] — lo impreso en avisos, vitrinas y contratos no se apaga |
| `numero_dedicado_por_canal` | bool — si ya atribuye por número distinto (señal de madurez) |
| `llamadas_medidas` | `automatico` · `manual` · `no` — `manual` es C-04, el ábaco |
| `decision_del_numero` | `mantener_en_app` · `migrar_a_api` · `numero_nuevo_para_whatsapp` — el triángulo del número (modulo-gestion §E): se resuelve en la sesión, no en la implementación |

**Catálogo del negocio** (si el cliente vende sobre un inventario: inmuebles,
vehículos, cupos, programas):

| Campo | Notas |
|---|---|
| `catalogo_estructurado` | **si · parcial · no** — si los ítems tienen atributos consultables (tipo, zona, rango de precio) por API o exportación periódica. Decide si aplican los componentes de coincidencia (ej: `nutricion-nueva-oportunidad-catalogo`). "Parcial" = los atributos existen pero viven en Excel o en el sistema de un tercero. |
| `donde_vive` | sistema del stack que es fuente de verdad del catálogo |
| `items_activos` | número aproximado — dimensiona el valor de las alertas de coincidencia |

## E. Multiplicadores derivados

`se_instancia_por` de un componente puede resolverse contra:
`linea_negocio` · `sujeto_del_embudo` · `funcion` · `territorio` ·
`control_del_activo` · combinaciones de las anteriores · `unico`.

## F. Calidad de la extracción

| Campo | Notas |
|---|---|
| `datos_en_conflicto` | [{tema, objeto_a, version_a, objeto_b, version_b, impacto, estado}] — dos personas que se contradicen sobre un mismo hecho. **Antes de declarar conflicto, verificar que hablan del mismo objeto**: la mayoría de las contradicciones aparentes son dos respuestas ciertas sobre cosas distintas (la pauta vs. el sitio web, la línea de ventas vs. la de arriendos). Por eso el campo exige `objeto_a` y `objeto_b`: si difieren, no es conflicto, son dos datos y ambos se registran. |
| `funciones_sin_representacion` | [texto] — funciones mencionadas cuyo responsable no estuvo en la sesión. Cada una es un carril del BPMN diseñado a ciegas. |
| `decisor_presente` | bool — si quien aprueba el gasto estuvo en la sesión y estará en la presentación. Cuando es falso (patrón recurrente: "la doctora", las territoriales), la propuesta se diseña para **lectura autónoma primero**: el lienzo debe cargar el pitch completo sin narrador, porque la decisión real ocurre asíncrona. |
| `datos_economicos_capturados` | checklist contra los 21 datos duros del guión. Decide el **modo de la propuesta** (ver catálogo de fugas §5): con datos → modo A, fugas en dinero y escenarios; sin datos → modo B, fugas en volumen, solicitud de datos como paso del cierre. |
| `linea_base_caso_exito` | snapshot de los datos duros con fuente y periodo, congelado a la fecha del diagnóstico. Es el "antes" del caso de éxito; el "después" lo miden los tableros del plan implementado (regla V9 del schema). |
