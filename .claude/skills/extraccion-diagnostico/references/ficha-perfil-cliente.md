# Ficha de perfil del cliente — v0.2

Contrato de datos de la etapa 1. Alimenta `aplica_si`, `se_instancia_por` y la
selección de alcance de la etapa 3. Actualizada con los hallazgos del piloto
Activos por Colombia (ago-2026).

---

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
