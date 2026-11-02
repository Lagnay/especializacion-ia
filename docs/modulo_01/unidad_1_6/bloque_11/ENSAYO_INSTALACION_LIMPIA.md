# Ensayo de instalación limpia — Gate 1

Fecha: 19-10-2026.

## Versión y entorno

- Repositorio: https://github.com/Lagnay/especializacion-ia.
- Commit probado: 3905f4b8e47f7688380f4b3e76fdbc1a310d3025.
- Sistema: Windows, PowerShell.
- Python: 3.14.7.
- Carpeta del ensayo:
  C:\Users\Dell\pruebas-curso\prueba-gate_1-19_10_2026.

## Procedimiento y resultados

1. Cloné el repositorio desde GitHub en una carpeta separada.
2. Creé y activé un entorno virtual nuevo.
3. Confirmé que el ejecutable pertenecía al entorno del clon.
4. Instalé los 26 paquetes mediante requirements.txt.
5. Ejecuté pip check: No broken requirements found.
6. Creé un .env local desde .env.example y configuré mi credencial.
7. Ejecuté python -m src.main y recibí una respuesta real:
   Edimburgo.
8. La respuesta informó 11 tokens de entrada, 3 de salida
   y 14 totales, con un costo de referencia de 0.000010800 USD.
9. Confirmé que .env y venv estaban ignorados.
10. El clon quedó limpio: ## main...origin/main.

## Hallazgos y documentación

Utilicé un nombre de carpeta diferente al del ejemplo.
Corregí el comando para entrar en la carpeta realmente clonada.

El README ya describía el recorrido principal. Después del
ensayo amplié sus instrucciones para explicitar ubicación,
creación de .env, comprobaciones de seguridad y ejecución
del banco de prompts.

No fue necesario modificar código ni agregar dependencias.

## Alcance

El ensayo se realizó en el mismo computador, utilizando
una copia y un entorno virtual nuevos.

La instalación aprovechó la caché local de pip. No comprobé
la descarga completa sin caché, otro computador ni otro
sistema operativo.

La consulta real fue ejecutada manualmente por mí.
No hubo verificación independiente de un compañero.