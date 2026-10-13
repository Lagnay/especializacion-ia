# Laboratorio de integración con IA

Repositorio de práctica de la Especialización en Desarrollo con IA Generativa. Contiene la estructura base y las dependencias para trabajar con HTTP y la API de Gemini; todavía no incluye una aplicación ejecutable.

## Requisitos

- Git y acceso a Internet para obtener el repositorio y sus dependencias.
- Python instalado. Entorno comprobado: Windows con Python 3.14.7. La compatibilidad con otros sistemas y versiones está pendiente de comprobación.

## Instalación en Windows — PowerShell

En una terminal sin otro entorno virtual activo, clonar en una carpeta nueva:

```powershell
git clone https://github.com/Lagnay/especializacion-ia.git especializacion-ia
cd especializacion-ia
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea el script de activación, ejecutar `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`, activar el entorno y continuar la instalación.

## Instalación en macOS / Linux / WSL

Procedimiento de referencia, pendiente de comprobación con las versiones registradas. Requiere Git y Python 3 con soporte para venv. En WSL, utilizar una carpeta del sistema de archivos de Linux y crear un entorno nuevo, separado del de Windows.

En una terminal sin otro entorno activo:

```bash
git clone https://github.com/Lagnay/especializacion-ia.git especializacion-ia
cd especializacion-ia
python3 --version
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Configuración de Gemini

Crear un archivo local `.env` tomando `.env.example` como referencia y completar `GEMINI_API_KEY` con una credencial propia. Si `.env` ya existe, conservar su contenido y comprobar el nombre de la variable. La clave real sólo se guarda en la configuración local; `.env.example` mantiene un valor ficticio.

## Comprobación

Con el entorno activo:

```sh
python -c "import sys; print(sys.executable); print('Entorno virtual:', sys.prefix != sys.base_prefix)"
python -m pip check
python -c "import requests; from google import genai; from dotenv import load_dotenv; print('Importaciones OK')"
```

El ejecutable debe pertenecer al entorno creado. Se esperan `Entorno virtual: True`, `No broken requirements found.` e `Importaciones OK`.

Estas comprobaciones no requieren credenciales ni envían solicitudes al proveedor. `python-dotenv` es el paquete instalado, `dotenv` el módulo importado y `load_dotenv` una de sus funciones.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `src/` | Código fuente |
| `tests/` | Pruebas |
| `docs/` | Documentación y resultados de verificación |
| `requirements.txt` | Paquetes y versiones del entorno |
| `.env.example` | Plantilla de configuración sin credenciales reales |

El entorno `venv/` y la configuración local `.env` están excluidos de Git. Cada instalación debe crear su propio entorno; las credenciales no se publican.

## Verificación registrada

[Reconstrucción local en Windows](docs/VERIFICACION_ENTORNO.md): instalación desde una copia del repositorio publicado, seguida de comprobaciones de dependencias e importaciones.
