# Schema de diagnostico.json — contrato de salida de la etapa 2

```
{
  "_meta": {
    "cliente": str,
    "ficha_fuente": str,            // archivo de ficha evaluado
    "version_catalogo": str,        // versión del catálogo de fugas usada
    "evaluado_por": str,
    "fecha": str
  },

  "modo": "A" | "B",                // heredado de la ficha, nunca recalculado

  "fugas": [
    {
      "id": str,                    // DEBE existir en el catálogo (F/C/R/O/FP/FO-xx)
      "titulo": str,                // en lenguaje del cliente, sin jerga
      "categoria": "fuga"|"ceguera"|"restriccion"|"friccion_propia"|"fuga_oferente",
      "dominante": bool,            // exactamente una en true
      "estado": "activa"|"mitigable"|"fuera_de_alcance",
      "evidencia_ficha": str,       // ruta del campo, ej. "F_calidad.volumenes.represados"
      "evidencia_textual": str,     // la cita «…» que la ficha ya trae
      "cuantificacion": {
        "valor": str,               // "3.900 conversaciones" | "sin métrica de visitas"
        "unidad": "volumen"|"proceso"|"dinero",   // dinero SOLO en modo A
        "vive_aqui": bool           // regla anti-doble-conteo: la cifra pertenece a esta fuga
      },
      "depende_de_tercero": str|null   // quién, si estado=mitigable
    }
  ],

  "madurez": [
    {
      "m": "Gestión"|"Atracción"|"Nutrición"|"Cierre"|"Reactivación"|"Referidos y Fidelización"|"Tableros",
      "hoy": 0-4,
      "por_que": str                // cita el hecho de la ficha; obligatorio
    }
  ],                                // los 7, siempre

  "nota": { "puntos": 0-100, "letra": "F"|"E"|"D"|"C"|"B"|"A" },

  "silencios": [
    { "modulo": str, "lectura": str }   // lo no mencionado, leído como madurez
  ],

  "advertencias": [ str ],          // condiciones de arranque que la etapa 3 debe respetar

  "datos_que_faltan_para_modo_A": [ str ]   // presente si modo=B
}
```

## Reglas duras

1. Todo `id` existe en el catálogo. Inventar ids es la falla capital de la etapa.
2. Exactamente una fuga con `dominante: true`.
3. `cuantificacion.unidad = "dinero"` solo si `modo = "A"`.
4. Los 7 módulos presentes en `madurez`, cada uno con `por_que` no vacío.
5. Una cifra vive en UNA fuga (`vive_aqui: true`); las demás la referencian sin sumarla.
6. Este archivo no menciona componentes, planes ni precios: eso es etapa 3.
