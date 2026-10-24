# Laboratorio de integración con IA

Repositorio de práctica de la Especialización en Desarrollo con IA Generativa. Incluye un módulo Python que consulta la API de Gemini, extrae el texto generado, valida la entrada y maneja errores previsibles, además de ejercicios de aprendizaje.

## Requisitos

- Git y acceso a Internet para obtener el repositorio y sus dependencias.
- Python instalado. Entorno comprobado: Windows con Python 3.14.7. La compatibilidad con otros sistemas y versiones está pendiente de comprobación.

## Instalación en Windows — PowerShell

Requiere Git y Python instalados. Entorno comprobado:
Windows con Python 3.14.7.

Los siguientes comandos crean una carpeta de trabajo dentro
del perfil del usuario. La carpeta de destino del clon
`especializacion-ia` no debe existir previamente.
Si se elige otro nombre, debe utilizarse también al entrar
en ella.

```powershell
if (Get-Command deactivate -ErrorAction SilentlyContinue) {
    deactivate
}

New-Item -ItemType Directory -Path "$env:USERPROFILE\proyectos-ia" -Force
Set-Location -LiteralPath "$env:USERPROFILE\proyectos-ia"

git clone https://github.com/Lagnay/especializacion-ia.git especializacion-ia
Set-Location -LiteralPath ".\especializacion-ia"

python --version
python -m venv venv

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

La política de ejecución se configura solamente para esta
sesión de PowerShell. Al abrir otra terminal puede ser
necesario repetir ese comando antes de activar el entorno.

Continúa con «Configuración de Gemini» y después con «Uso».

## Instalación en macOS / Linux / WSL

Procedimiento de referencia, pendiente de comprobación.
Requiere Git y Python 3 con soporte para entornos virtuales.

El entorno verificado utiliza Python 3.14.7 en Windows;
no se garantiza compatibilidad con cualquier versión
de Python ni se ha comprobado esta instalación en otros sistemas.

En WSL, trabajar dentro del sistema de archivos de Linux
y crear un entorno propio, separado del de Windows.

La carpeta de destino `especializacion-ia` no debe existir.
Si se elige otro nombre al clonar, utilizarlo también al entrar.

```bash
if command -v deactivate >/dev/null 2>&1; then
    deactivate
fi

mkdir -p "$HOME/proyectos-ia"
cd "$HOME/proyectos-ia"

git clone https://github.com/Lagnay/especializacion-ia.git especializacion-ia
cd especializacion-ia

python3 --version
python3 -m venv venv
source venv/bin/activate

python -m pip install -r requirements.txt
```

Continúa con «Configuración de Gemini» y después con «Uso».
Los comandos que comienzan con `python` en las secciones
siguientes se ejecutan con este entorno virtual activo.

## Configuración de Gemini

Se necesita una credencial propia de Gemini API.

Desde la raíz del repositorio, crear `.env` a partir de
la plantilla, únicamente si todavía no existe.

En Windows — PowerShell:

```powershell
if (-not (Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}
```

En macOS / Linux / WSL, si `.env` todavía no existe:

```bash
cp .env.example .env
```

Abrir `.env` con un editor y reemplazar el valor ficticio
de `GEMINI_API_KEY` por la credencial propia. Guardar el archivo.

En Windows puede abrirse con `notepad .env`. Si el comando
de Visual Studio Code está disponible, también puede
utilizarse `code .env`.

La credencial real permanece únicamente en la configuración
local. `.env.example` conserva un valor ficticio.

## Uso

Desde la raíz del repositorio, con el entorno virtual activo
y la credencial configurada en `.env`, ejecutar:

```powershell
python -m src.main
```

El programa envía la pregunta de ejemplo definida en `src/main.py`
y muestra el texto generado, el consumo de tokens y una estimación
a tarifas de pago. Esta estimación no representa necesariamente
un cargo: depende del nivel de servicio utilizado.

Las funciones reutilizables se encuentran en `src/consumir_gemini.py`.
La respuesta y su consumo pueden variar entre ejecuciones.

### Cliente modular con reintentos

Para ejecutar el cliente que clasifica errores y reintenta
ante fallos considerados temporales:

```powershell
python -m src.cliente
```

Realiza una consulta real a Gemini y muestra el texto generado.
Permite hasta tres intentos, con esperas exponenciales y una
pequeña variación aleatoria (jitter), limitadas a 30 segundos
por pausa. Los errores de entrada y los estados
HTTP 401 y 403 se comunican sin reintentar.

Cada respuesta recibida con datos de consumo permite calcular
y mostrar un costo de referencia, acumulado durante el proceso
actual. El acumulado se reinicia al ejecutar nuevamente el
programa. Se utilizan tarifas de referencia del laboratorio
fechadas el 16-10-2026; el importe no representa necesariamente
un cargo real.

Para utilizarlo desde otro módulo:

```python
from src.cliente import consultar_modelo

respuesta = consultar_modelo("¿Cuál es la capital de Chile?")
```
Para comprobar el cliente con respuestas simuladas, desde
la raíz del repositorio y con el entorno virtual activo:

```powershell
python -m tests.comprobar_cliente
```

Esta comprobación verifica éxito inmediato, recuperación,
agotamiento de intentos, estados HTTP 401 y 403 y rechazo
de preguntas inválidas. Muestra el resultado de cada escenario
y la cantidad de peticiones realizadas, sin conectarse a Gemini.

## Pruebas locales del módulo

Desde la raíz del repositorio y con el entorno virtual activo:

```powershell
python -m tests.comprobar_extraccion
python -m tests.comprobar_json_invalido
python -m tests.comprobar_timeout
```

Estas pruebas comprueban extracción y manejo de fallos preparados o simulados; no envían peticiones a Gemini. La ejecución indicada en «Uso» comprueba la conexión real.

## Comprobación

Con el entorno activo:

```sh
python -c "import sys; print(sys.executable); print('Entorno virtual:', sys.prefix != sys.base_prefix)"
python -m pip check
python -c "import requests; from google import genai; from dotenv import load_dotenv; print('Importaciones OK')"
```

El ejecutable debe pertenecer al entorno creado. Se esperan `Entorno virtual: True`, `No broken requirements found.` e `Importaciones OK`.

Estas comprobaciones no requieren credenciales ni envían solicitudes al proveedor. `python-dotenv` es el paquete instalado, `dotenv` el módulo importado y `load_dotenv` una de sus funciones.

## Banco de prompts

Desde la raíz del repositorio, con el entorno activo
y la credencial configurada:

```powershell
python -m prompts.test_consistencia
```

Realiza nueve consultas reales y actualiza
`prompts/registro_resultados.json`.

Para probar solamente el resumen:

```powershell
python -m prompts.test_consistencia resumir_mensaje
```

Realiza tres consultas y actualiza
`prompts/registro_resultados_parcial.json`.

Estas ejecuciones modifican los registros guardados.
Los resultados pueden variar entre pruebas.

## Comprobación de seguridad

Desde la raíz del repositorio:

```powershell
git ls-files -- .env .env.example requirements.txt
git check-ignore -v -- .env venv/Scripts/python.exe
git --no-pager log --all --oneline -- .env
git status -sb
```

Deben aparecer `.env.example` y `requirements.txt` como
versionados, pero no `.env`. Las reglas de exclusión deben
cubrir `.env` y `venv`. La consulta del historial de `.env`
no debe devolver commits.

Una instalación y ejecución principal sin modificar archivos
versionados debe dejar limpio el estado de Git. Reejecutar
el banco de prompts puede mostrar cambios esperados
en sus registros.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `src/` | Módulos de la aplicación y programa principal |
| `src/practicas/` | Ejercicios y versiones utilizadas durante el aprendizaje |
| `tests/` | Scripts de comprobación local del módulo |
| `prompts/` | Banco de prompts, validación y registros de resultados |
| `docs/` | Documentación, diagramas y evidencias |
| `requirements.txt` | Paquetes y versiones del entorno |
| `.env.example` | Plantilla de configuración sin credenciales reales |

El entorno `venv/` y la configuración local `.env` están excluidos de Git. Cada instalación debe crear su propio entorno; las credenciales no se publican.

## Documentación y evidencias

[Consultar el índice de documentación y evidencias](docs/INDICE_README.md).