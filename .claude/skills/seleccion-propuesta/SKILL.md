---
name: seleccion-propuesta
description: Etapa 3 de la cadena diagnóstico → propuesta de Ropofy. Toma el diagnostico.json (etapa 2) y la ficha.json (etapa 1), selecciona de la librería compilada los componentes que aplican al cliente, calcula instancias por eje, arma el carril de integraciones, deriva la complejidad y el precio por tramos, y produce propuesta.json — el único puente hacia el renderizador del lienzo. Usar cuando el usuario pida "armar la propuesta", "correr la etapa 3", "seleccionar componentes", "calcular el precio", "generar el propuesta.json" o entregue un diagnóstico validado y pida el siguiente paso.
---

# Etapa 3 — Selección y propuesta

Convierte juicios (diagnóstico) en una oferta concreta (propuesta.json). Es la
etapa más mecánica de la cadena: casi todo son reglas ya escritas (V1–V11 del
schema, matriz de fronteras, catálogo). El criterio humano entra en pocos
puntos y están marcados.

**Regla de la etapa: produce DATOS, jamás HTML.** Ni colores, ni coordenadas,
ni markup. Si el lienzo necesita algo que no está aquí, falta un campo en el
contrato — no se parcha en el renderizador.

## Compuertas de entrada (obligatorias)

```
python3 <skill-1>/scripts/validar_ficha.py ficha-<cliente>.json
python3 <skill-2>/scripts/validar_diagnostico.py diagnostico-<cliente>.json <catalogo>
```

Ambas deben pasar. Además se necesita la librería compilada:

```
python3 scripts/compilar_libreria.py references/modulos componentes.json
```

**Origen de la librería, en orden de preferencia:** (1) los `modulo-*.md` del
Proyecto o del contexto de trabajo si existen ahí más recientes; (2) los de
`references/modulos/` empacados en esta skill — son el snapshot de la versión
con la que se empaquetó (el hash `_meta.version` lo delata). Cuando la
librería cambie, esta skill se reempaqueta: es UN comando, y mantiene la
regla de que la selección jamás corre sobre librería desactualizada sin
saberlo. Si la compilación falla (ids duplicados, V11 violado), la librería
se corrige ANTES de seleccionar — nunca se selecciona sobre librería rota.

**Los .md de los módulos no son solo insumo del compilador**: contienen el
detalle que el JSON no lleva (prerequisitos, restricciones R-08/R-09, notas
de terceros, la regla del copy). Al evaluar `aplica_si` de un componente
dudoso, leer su bloque completo en el módulo, no solo la fila compilada.

## Proceso

1. **Filtrar por `aplica_si`**: recorrer los 81 componentes evaluando su
   condición contra la ficha. Lo que no aplica va a `no_aplican` CON su razón
   en lenguaje del cliente ("ya tienen sitio con catálogo", "no se capturó si
   cobran anticipo"). Nada desaparece en silencio.
2. **Respetar lo que el cliente ya tiene**: si la ficha muestra capacidad
   instalada equivalente (números dedicados propios, catálogo publicado), el
   componente se marca `no_aplican` con razón "ya lo resuelven con X" — se
   respeta y se lee, no se reinstala ni se cobra.
3. **Calcular instancias**: NUNCA a mano ni con el modelo. El reparto de
   responsabilidades es: **el modelo decide QUÉ aplica** (`aplica_si` es
   semántico), **Python decide CUÁNTO** — correr
   `python3 scripts/calcular_condicion.py propuesta.json ficha.json`, que
   deriva los ejes de la ficha y asigna instancias por componente.
   ADVERTENCIA conocida: la regla uniforme infla cuando varias líneas
   comparten configuración. Si el consultor lo sabe, fija `instancias` a mano
   Y marca `instancias_fijadas_por_consultor: true` — el script respeta el
   ajuste y lo reporta. Máximas teóricas: no usar para prometer fechas.
4. **Carril de integraciones**: todo componente `tipo: integracion` no nativo
   (V11) y todo costo variable de plataforma va al carril con su etiqueta:
   `incluido` · `consumo_variable` · `licencia_del_cliente` ·
   `desarrollo_a_cotizar`. La evaluación técnica de lo no nativo SÍ viaja en
   el plan; la integración misma jamás.
5. **Cuotas por plan**: aplicar las de la matriz de fronteras (formularios,
   agendas, campañas, piezas redactadas). Recordar la regla global del copy:
   Ropofy da punto de partida metodológico; el texto final lo proporciona o
   aprueba el cliente — la propuesta debe decirlo en advertencias.
6. **Complejidad y precio**: los calcula el MISMO script del paso 3
   (`calcular_condicion.py`): multiplicador por plan desde la selección,
   factor por tramos y `precio = base_plan × factor`, todo escrito en
   `condicion_comercial`. Base y tramos son política de negocio: vienen dados,
   el script se niega a inventarlos. El multiplicador es INTERNO: panel del
   consultor, nunca texto del cliente.
7. **Armar el as-is con su cifra en el campo, no en la prosa**: en
   `por_donde_pasan` (contrato v0.5, C2) cada fila es un objeto
   `{quien, nota, detalle[]}` — el rol en `quien`, qué hace en `nota`, y el
   contexto (cómo lo gestionan, quién hace qué) en `detalle`, `[]` si no hay;
   el dato duro va en `dato_destacado` opcional. En los otros dos ejes, cada fila de
   `as_is` es `[etiqueta, nota]`, y si la fila tiene un dato duro se agrega el
   tercer elemento `{"cifra": "306", "unidad": "leads/mes"}`. La cifra se
   **copia** de la nota (no se calcula, no se redondea, no se trae de otra
   parte); la unidad se nombra como la usa el cliente. La nota lleva **una sola
   cifra**: si la frase trae dos números, se reescribe o se parte en dos filas,
   porque el lienzo no puede saber cuál destacar. Fila sin dato duro: dos
   elementos y nada más.
8. **Escribir el resumen sin repetir el as-is (C1)**: `resumen` es
   `{parrafo (2–3 frases), bullets (3 o 4)}` y su contenido permitido es solo:
   qué hace la empresa, industria, zona, años, propuesta de valor, contexto de
   la sesión y el problema resumido. **Ningún canal, sistema, rol ni cifra que
   ya esté en el as-is puede reaparecer** — el validador lo verifica por
   tokens. El resumen dice quiénes son y qué les duele; el as-is dice por
   dónde entra, quién lo gestiona y dónde queda.
9. **Frase de plan al negocio (C3)**: el bloque `planes` lleva por plan la
   `frontera` copiada TEXTUAL (el validador exige match exacto) y una `frase`
   que la traduce a los hechos de la ficha de ESTE cliente. Prohibido nombrar
   en la frase una capacidad que no esté en los `componentes` de la propuesta
   («agenda y firma» en un negocio que no los lleva es la falla que motivó el
   cambio).
10. **Síntesis y engranaje por componente (C4, C5)**: cada componente lleva
   `sintesis` (≤ 90 caracteres, una sola idea, sin jerga — el detalle se
   levanta en la sesión de especificaciones) y `conecta_con` con los ids de la
   MISMA propuesta que alimenta funcionalmente. Sin autorreferencia, sin
   ciclos de longitud 2, y `[]` si no engrana con nada — no se fuerza.
11. **Brecha fuera de alcance (C6)**: si el techo del plan recomendado
   (madurez `p`) es < 100, redactar por módulo con déficit el `por_que`, el
   `responsable` (cliente · tercero · regulatorio) y `que_puede_hacer`
   (acción concreta fuera del CRM), más el `por_que` global, y correr
   `python3 scripts/calcular_brecha.py propuesta.json` — **los puntos los
   escribe el script**, y elimina el bloque entero si el techo es 100. Es el
   cambio más importante de la sesión de Jorge: en vez de un techo
   inexplicado, el cliente se lleva la hoja de ruta de lo que le toca a él.
12. **Armar el panel interno (C7, C9)**: `preguntas_para_el_consultor`
   (reemplaza a `datos_que_faltan`: preguntas redactadas para hacerse en voz
   alta, con su por qué y el campo de la ficha que completan), `no_aplican`,
   `multiplicador_calculado`, `desglose_interno` y `sesiones` viven SOLO en
   `panel_interno`. TRAMPA CONOCIDA: `calcular_condicion.py` (que no se toca)
   escribe `multiplicador_calculado` en el nivel superior y
   `desglose_interno` dentro de `condicion_comercial` — tras correrlo, MOVER
   ambos a `panel_interno` sin editar un solo número; el validador falla si
   quedan duplicados fuera. No emitir fecha de arranque estimado.
13. **Benchmark sin muestra (C8)**: `benchmark = {por_modulo (los 7),
   fuente}` y la fuente se redacta «diagnósticos de PYMES en Colombia y
   Argentina, antes de implementar Ropofy» — sin el n, sin ningún dígito.
14. **Advertencias atomizadas (C10)**: una idea por elemento, ≤ 140
   caracteres, en viñeta. Si una mezcla dos condiciones, se parte. La regla
   del copy sigue siendo obligatoria.
15. **Heredar sin recalcular**: fugas, madurez, nota, modo, silencios y
   advertencias vienen del diagnóstico tal cual. Esta etapa agrega — las
   condiciones de arranque, la razón de los no_aplican — pero no re-juzga.
   Se hereda también el **estado de los nombres propios** que fijó la compuerta
   de la etapa 1: `cliente_grafia_estado`, `razon_social` y
   `nombres_por_confirmar` con los nombres que esta propuesta imprime y siguen
   sin confirmar. Una grafía dudosa **no se corrige aquí**: se corrige en la
   ficha y se rehace la cadena. Corregirla en la propuesta es inventar.
16. **Salida**: `propuesta-<cliente>.json` (`_contrato: "propuesta v0.5"`) validada con
   `scripts/validar_propuesta.py` antes de entregar. Escribir **`libreria_hash`**
   con el `_meta.version` de la librería compilada que se acaba de usar: es la
   procedencia de la propuesta y lo que permite validarla dentro de un año, cuando
   la librería haya cambiado, sin editarla ni romper la validación (schema §9).

## Puntos de criterio humano (los únicos)

- **Plan recomendado**: la regla base es "el plan cuya madurez resultante
  cierra la fuga dominante", pero la lectura de apetito del cliente es del
  consultor. Registrar la razón en `plan_recomendado.por_que`.
- **Condición comercial**: descuento y vigencia los fija el consultor en el
  lienzo, no esta etapa. Aquí solo viajan los límites de política.
- **Instancias compartidas**: si el consultor ya sabe que dos líneas comparten
  pipeline, puede fijar `instancias` manualmente — dejando `inst_por` original
  como rastro.

## Trampas conocidas

**Vender el catálogo completo.** La selección existe para EXCLUIR: una
propuesta donde aplica todo es señal de que `aplica_si` no se evaluó. El
lienzo de un cliente solo trae lo suyo.

**Colar componentes por la fuga que cierran.** El flujo correcto es
ficha→aplica, no fuga→quiero cerrarla→aplica. Si el componente que cierra la
dominante no aplica al cliente (p.ej. exige catálogo estructurado y no lo hay),
la dominante se ataca con el que sigue — y se registra en advertencias.

**El precio delatando la fórmula.** Nunca exponer base × factor al cliente:
el precio del cliente es un número entero limpio. El desglose vive en el
bloque `condicion_comercial.desglose_interno`.

**Dejar la cifra del as-is suelta en la prosa.** El renderizador no interpreta
texto: si la fila no declara su dato en el tercer elemento, el número que el
lienzo muestre saldrá de escarbar dígitos de la nota, y escarbar acierta poco.
Casos reales: la fila "Pedix" mostró un 4 que venía de «zonas fuera del radio de
4 km», y "Comanda impresa" mostró 3 y 4 que venían de «ítems de 3 o 4 sectores».
Ninguno era un dato malo: eran datos sin campo. La regla operativa es doble —
una sola cifra por nota, y la cifra que el lienzo destaca va declarada y tiene
que aparecer en la nota que la respalda. Un número sin frase que lo sostenga no
entra a la propuesta.

**Repetir el as-is en el resumen.** Es la redundancia que Jorge marcó en el
lienzo: el canal, el sistema o la cifra que ya viven en el as-is no vuelven al
resumen. El validador compara tokens y falla.

**Prometer en la frase del plan lo que no está en la selección.** La frontera
es invariante; la frase la traduce con los hechos y componentes de ESTE
cliente. Nombrar «agenda y firma» donde no se venden es la falla original.

**Escribir los puntos de la brecha a mano.** Los textos son del consultor; los
puntos, de `calcular_brecha.py` (déficit × 100/28, resto mayor). El validador
recalcula y compara.

**Dejar lo interno al alcance del lienzo.** `no_aplican`, el multiplicador, el
desglose, las sesiones y las preguntas pendientes viven en `panel_interno` y
solo ahí. Nada de ese bloque se renderiza al cliente.

**Exponer el n del benchmark.** La fuente se redacta sin tamaño de muestra: un
dígito en `benchmark.fuente` es error de validación.

**Prometer sobre instancias infladas.** El multiplicador calculado sirve para
tramificar el precio, no para comprometer alcance por línea. La frase segura:
"hasta N configuraciones según se confirme en el arranque".

## Checklist antes de entregar

- [ ] Compuertas corridas (ficha + diagnóstico válidos, librería compilada sin errores)
- [ ] Todo componente de la propuesta existe en componentes.json y tiene plan válido
- [ ] Cero componentes con `plan_minimo: null` dentro de los planes (V11)
- [ ] `no_aplican` con razón en lenguaje del cliente
- [ ] Carril de integraciones con etiqueta de costo cada una
- [ ] Multiplicador aritméticamente correcto por plan
- [ ] Fugas/madurez/nota idénticas al diagnóstico (herencia sin edición)
- [ ] `cliente_grafia_estado`, `razon_social` y `nombres_por_confirmar` heredados de la ficha, sin corregir grafías aquí
- [ ] `resumen` = {parrafo 2–3 frases, bullets 3–4} sin repetir tokens del as-is
- [ ] `por_donde_pasan` jerárquico: {quien, nota, detalle[]}; los otros dos ejes como pares/tríos
- [ ] `planes` con las tres fronteras textuales y frases que solo nombran capacidades de la selección
- [ ] Cada componente con `sintesis` (≤ 90) y `conecta_con` (ids propios, sin ciclos de 2)
- [ ] Brecha: textos del consultor + puntos de `calcular_brecha.py`; omitida entera si el techo es 100
- [ ] `panel_interno` completo y sin duplicados fuera (multiplicador y desglose MOVIDOS tras calcular_condicion.py)
- [ ] `benchmark.fuente` sin dígitos; `por_modulo` con los 7
- [ ] Advertencias de una idea, ≤ 140 caracteres
- [ ] Sin fecha de arranque estimado
- [ ] Cada fila del as-is con dato duro declara `{cifra, unidad}` en su campo, y esa cifra aparece literal en su nota
- [ ] Ninguna nota del as-is con más de una cifra (si trae dos, se reescribe o se parte la fila)
- [ ] Cero HTML, cero colores, cero coordenadas
- [ ] Instancias, multiplicador y precios los escribió `calcular_condicion.py`, no el modelo
- [ ] Ajustes manuales de instancias marcados con `instancias_fijadas_por_consultor`
- [ ] `libreria_hash` escrito con el hash de la librería usada (obligatorio desde v0.4)
- [ ] `validar_propuesta.py` pasa (exit 0) — y si reporta «histórica», la propuesta se emitió contra otra librería: verificar que era lo esperado

## Referencias

- `references/schema-propuesta.md` — el contrato de salida completo.
- `references/schema-componente.md` — V1–V11 y los campos de la librería.
- `references/matriz-fronteras.md` — cuotas y frases por plan.
- `examples/propuesta-ejemplo-activos.json` — propuesta real multilínea (contrato v0.5): resumen estructurado, planes con frase, síntesis y engranaje por componente, brecha fuera de alcance y panel interno.
- `examples/componentes-ejemplo.json` — librería compilada de referencia (81 componentes).
