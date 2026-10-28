# Bloque 16 — Evaluación mediante precisión, cobertura y F1

## Ejecución realizada

El 27 de octubre de 2026 ejecuté tres consultas mediante mi cliente
de Gemini y comparé las respuestas con referencias escritas previamente.

El modelo configurado fue `gemini-3.5-flash-lite`.
La instrucción utilizada fue:

> Responde en español, con una sola oración breve y sin formato Markdown.

Se completaron los tres casos y no se registraron errores.

El registro conserva la fecha con zona horaria, el modelo configurado,
la instrucción, las consultas, las referencias, las respuestas completas
y las métricas sin redondear:

[Consultar el registro JSON](resultados_metricas_20261027_202048_949209.json).

## Resultados

Los valores de esta tabla están redondeados a tres decimales.

| Caso | Precisión | Cobertura | F1 |
| --- | ---: | ---: | ---: |
| Reproducir «El cielo es azul.» en minúsculas y sin puntuación | 1.000 | 1.000 | 1.000 |
| ¿Qué es Python? | 0.214 | 0.857 | 0.343 |
| ¿Para qué sirve la fotosíntesis en las plantas? | 0.259 | 0.636 | 0.368 |
| **Promedio por caso** | **0.491** | **0.831** | **0.570** |

Cada caso tiene el mismo peso en el promedio.
El F1 promedio se obtiene promediando los F1 individuales.

## Referencias y respuestas completas

### Caso 1 — Formato controlado

**Consulta:** Escribe exactamente «El cielo es azul.» en minúsculas y sin signos de puntuación ni comillas.

**Referencia:** El cielo es azul.

**Respuesta:**

> el cielo es azul

### Caso 2 — Python

**Consulta:** ¿Qué es Python?

**Referencia:** Python es un lenguaje de programación interpretado.

**Respuesta:**

> Python es un lenguaje de programación de alto nivel, versátil y fácil de aprender que se utiliza para el desarrollo de software, inteligencia artificial y análisis de datos.

### Caso 3 — Fotosíntesis

**Consulta:** ¿Para qué sirve la fotosíntesis en las plantas?

**Referencia:** La fotosíntesis permite a las plantas producir alimento utilizando la luz.

**Respuesta:**

> La fotosíntesis sirve para que las plantas transformen la luz solar, el agua y el dióxido de carbono en su propio alimento y oxígeno para el planeta.

## Interpretación

El primer caso es una comprobación controlada de formato:
después del procesamiento, la respuesta coincide con la referencia.

La respuesta sobre Python es más extensa que su referencia.
Comparte seis de las siete palabras de referencia, pero incorpora
muchas palabras adicionales: por eso su cobertura es alta y su
precisión léxica es baja. No incluye la palabra «interpretado».

En fotosíntesis hay siete coincidencias entre once palabras de
referencia y veintisiete palabras de respuesta. El contenido debe
revisarse leyendo ambos textos, además de consultar sus métricas.

El orden ascendente por F1 es: Python, fotosíntesis y cielo azul.
Este orden identifica menor coincidencia léxica; no demuestra
por sí mismo cuál respuesta es peor.

## Límites comprobados en la práctica

- Sinónimos: «El auto es veloz.» y «El coche es rápido.» obtienen
  F1 de 0.50 aunque expresan prácticamente lo mismo en ese contexto.
- Negación: añadir «no» a «El local abre los domingos.» cambia
  el significado, pero mantiene un F1 aproximado de 0.91.
- Cambio de protagonistas: «El perro persiguió al gato.» y
  «El gato persiguió al perro.» obtienen F1 de 1.00.

Las métricas cuentan palabras compartidas con sus repeticiones.
No verifican significado, orden ni veracidad.

## Reproducción

Desde la raíz del repositorio, con el entorno virtual activo:

```powershell
python -m src.evaluar_texto
```

Este comando consulta la API y guarda un archivo nuevo con fecha
y hora en esta carpeta. Las respuestas y métricas pueden variar.

Para analizar la ejecución documentada sin nuevas consultas:

```powershell
python -m src.resumir_evaluacion "docs/Bloque 16/resultados_metricas_20261027_202048_949209.json"
```

Para ejecutar las pruebas automatizadas de las métricas:

```powershell
python -m pytest tests/test_metricas_texto.py -v
```

Verificación realizada: 8 pruebas de métricas y 35 pruebas
en el conjunto completo, todas aprobadas.