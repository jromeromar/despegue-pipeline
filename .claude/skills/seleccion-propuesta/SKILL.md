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
7. **Heredar sin recalcular**: fugas, madurez, nota, modo, silencios y
   advertencias vienen del diagnóstico tal cual. Esta etapa agrega — las
   condiciones de arranque, la razón de los no_aplican — pero no re-juzga.
8. **Salida**: `propuesta-<cliente>.json` validada con
   `scripts/validar_propuesta.py` antes de entregar.

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
- [ ] Cero HTML, cero colores, cero coordenadas
- [ ] Instancias, multiplicador y precios los escribió `calcular_condicion.py`, no el modelo
- [ ] Ajustes manuales de instancias marcados con `instancias_fijadas_por_consultor`
- [ ] `validar_propuesta.py` pasa (exit 0)

## Referencias

- `references/schema-propuesta.md` — el contrato de salida completo.
- `references/schema-componente.md` — V1–V11 y los campos de la librería.
- `references/matriz-fronteras.md` — cuotas y frases por plan.
- `examples/propuesta-ejemplo-activos.json` — propuesta real multilínea con carril de integraciones, no_aplican y tercero institucional.
- `examples/componentes-ejemplo.json` — librería compilada de referencia (81 componentes).
