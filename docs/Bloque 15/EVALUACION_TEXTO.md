# Bloque 15 — Pipeline y evaluación de texto

## Objetivo

Construí un pipeline reutilizable de limpieza, tokenización,
conteo y comparación de texto. Lo apliqué a tres respuestas
reales del cliente Gemini, con referencias definidas previamente.

## Configuración y ejecución

- Fecha: 26-10-2026.
- Modelo: gemini-3.5-flash-lite.
- Cliente: `src/cliente.py`.
- Procesamiento: `src/pipeline_texto.py`.
- Evaluación: `src/evaluar_texto.py`.
- Pruebas: `tests/test_pipeline_texto.py`.

Desde la raíz del repositorio:

```powershell
python -m src.evaluar_texto
```

La ejecución realiza consultas reales y consume cuota.
Las credenciales permanecen en `.env`, excluido de Git.

## Resultados

- Casos completados: 3/3.
- Caso 1, cambio de formato: 50.0 % → 100.0 %.
- Caso 2, definición de Python: 85.7 % → 85.7 %.
- Caso 3, fotosíntesis: 45.5 % → 50.0 %.
- Costo acumulado de referencia: 0.000165500 USD.

El costo utiliza las tarifas de referencia del laboratorio
fechadas el 16-10-2026; no confirma un cargo real.

## Interpretación

El primer caso es una comprobación controlada de normalización:
la consulta pide cambiar el formato de una frase conocida.
Permite observar el efecto de la limpieza, pero no constituye
una evaluación independiente de conocimientos del modelo.

En el segundo caso, seis de las siete palabras únicas de
referencia aparecen en la respuesta. No aparece «interpretado».

En el tercero, «La» y «la» se unifican al normalizar la referencia:
las palabras compartidas siguen siendo cinco, pero las palabras
únicas de referencia pasan de once a diez. «Producir» y
«produzcan» permanecen como unidades distintas.

La métrica mide coincidencia léxica. No determina equivalencia
semántica, veracidad ni calidad global. Tampoco considera
el orden o las repeticiones ni penaliza información adicional.

## Pruebas automatizadas

```powershell
python -m pytest tests -v
```

Resultado observado: 27 casos aprobados, incluidos los ocho
del pipeline. Estas pruebas no consultan Gemini.

## Salida completa de la evaluación

```
python -m src.evaluar_texto

=== CASO 1 ===
Consulta: Escribe exactamente «El cielo es azul.» en minúsculas y sin signos de puntuación ni comillas.
Referencia: El cielo es azul.
Costo de referencia de la operación: 0.000021400 USD
Acumulado de la sesión: 0.000021400 USD
Respuesta original: el cielo es azul
Tokens de referencia: ['el', 'cielo', 'es', 'azul']
Tokens de respuesta: ['el', 'cielo', 'es', 'azul']
Coincidencia texto crudo: 50.0%
Coincidencia texto procesado: 100.0%

=== CASO 2 ===
Consulta: ¿Qué es Python?
Referencia: Python es un lenguaje de programación interpretado.
Costo de referencia de la operación: 0.000081000 USD
Acumulado de la sesión: 0.000102400 USD
Respuesta original: Python es un lenguaje de programación de alto nivel, versátil y fácil de aprender que se utiliza ampliamente en el desarrollo de software y la inteligencia artificial.
Tokens de referencia: ['python', 'es', 'un', 'lenguaje', 'de', 'programación', 'interpretado']
Tokens de respuesta: ['python', 'es', 'un', 'lenguaje', 'de', 'programación', 'de', 'alto', 'nivel', 'versátil', 'y', 'fácil', 'de', 'aprender', 'que', 'se', 'utiliza', 'ampliamente', 'en', 'el', 'desarrollo', 'de', 'software', 'y', 'la', 'inteligencia', 'artificial']
Coincidencia texto crudo: 85.7%
Coincidencia texto procesado: 85.7%

=== CASO 3 ===
Consulta: ¿Para qué sirve la fotosíntesis en las plantas?
Referencia: La fotosíntesis permite a las plantas producir alimento utilizando la luz.
Costo de referencia de la operación: 0.000063100 USD
Acumulado de la sesión: 0.000165500 USD
Respuesta original: La fotosíntesis sirve para que las plantas produzcan su propio alimento y liberen oxígeno al medio ambiente.
Tokens de referencia: ['la', 'fotosíntesis', 'permite', 'a', 'las', 'plantas', 'producir', 'alimento', 'utilizando', 'la', 'luz']
Tokens de respuesta: ['la', 'fotosíntesis', 'sirve', 'para', 'que', 'las', 'plantas', 'produzcan', 'su', 'propio', 'alimento', 'y', 'liberen', 'oxígeno', 'al', 'medio', 'ambiente']
Coincidencia texto crudo: 45.5%
Coincidencia texto procesado: 50.0%

Casos completados: 3/3
```