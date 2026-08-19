# Expediente de referencia — Activos por Colombia (AYC)

Caso terminado de la cadena completa, acordado como referencia del repo. Es el
único expediente de cliente que vive aquí; el resto vive en OneDrive y el repo
los ignora (`clientes/` está en `.gitignore`).

| Archivo | Etapa | Contrato con el que se emitió |
|---|---|---|
| `ficha-activos.json` | 1 · extracción | ficha **v0.3** (migrada desde v0.2.1) |
| `diagnostico-activos.json` | 2 · evaluación | diagnóstico v0.1 |
| `propuesta-activos-v1.json` | 3 · selección | propuesta **v0.3** · librería **`639f4fc256`** (81 componentes) |

## Procedencia de la propuesta v1

`propuesta-activos-v1.json` se emitió contra la librería **`639f4fc256`**. Este
README es donde vive ese dato: **no se metió dentro del JSON emitido**, porque una
propuesta emitida no se edita (regla 7 de la casa — el expediente del cliente es
su historial).

La librería avanzó después: la corrección C2 del catálogo de habilidades IA
dividió `gestion-chatbot-precalificacion` y la C4 renombró
`reactivacion-precalificacion-ia`. Esta propuesta referencia esos dos ids, que ya
no existen en la librería viva. **Eso no es un defecto de la propuesta: es su
fecha.** Validarla contra la librería actual la reporta como *histórica* y sale
con 0:

```
python3 .claude/skills/seleccion-propuesta/scripts/validar_propuesta.py \
  ejemplos/expediente-activos/propuesta-activos-v1.json \
  libreria/componentes.json \
  ejemplos/expediente-activos/diagnostico-activos.json
```

Se valida su estructura, su aritmética y su herencia del diagnóstico; los ids del
alcance no se verifican contra una librería que no es la suya. El mecanismo está
contratado en `schema-propuesta.md` §Reglas duras 9 (`libreria_hash`).

**Si su alcance sigue vigente, se emite `-v2`** contra la librería nueva. La v1 no
se edita ni se borra.

## Las dos etapas anteriores

`ficha-activos.json` está migrada al contrato v0.3 (nombres propios con grafía,
estado y variantes). Como es una ficha **migrada y no reprocesada** contra la
transcripción, todos sus nombres propios quedan `por_confirmar`: migrar no
confirma nada. Por eso su validador sale con 0 y una advertencia `I9`.
