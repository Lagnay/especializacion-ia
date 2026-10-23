import time
from typing import Any, Callable

import requests

from src.consumir_gemini import armar_peticion, extraer_texto


def clasificar_estado(codigo):
    if codigo in (401, 403):
        raise ValueError(
            "Revisa la credencial o los permisos."
        )

    if codigo == 429:
        raise TimeoutError(
            "Límite de uso: revisar la cuota y la espera."
        )

    if codigo in (500, 502, 503, 504):
        raise TimeoutError(
            "Fallo del proveedor: podría ser temporal."
        )

    if 200 <= codigo < 300:
        return "Estado de éxito: continuar con la respuesta."

    raise RuntimeError(
        f"HTTP {codigo}: revisar la causa antes de reintentar."
    )


def enviar_peticion_clasificada(url, headers, body):
    try:
        respuesta_http = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30,
        )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ) as error:
        raise TimeoutError(
            "No se pudo completar la conexión con el proveedor."
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            "Ocurrió otro problema al enviar la petición."
        ) from error

    clasificar_estado(respuesta_http.status_code)

    try:
        return respuesta_http.json()

    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError(
            "La respuesta del proveedor no contiene JSON válido."
        ) from error


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,
) -> Any:
    if intentos < 1:
        raise ValueError("Debe permitirse al menos un intento.")

    for intento in range(1, intentos + 1):
        try:
            return funcion()

        except TimeoutError:
            if intento == intentos:
                raise

            print(
                f"Intento {intento} de {intentos} fallido. "
                f"Esperando {espera_segundos} segundos..."
            )
            time.sleep(espera_segundos)


def consultar_modelo(pregunta, system_instruction=None):
    url, headers, body = armar_peticion(
        pregunta,
        system_instruction=system_instruction,
    )

    try:
        datos = con_reintento(
            lambda: enviar_peticion_clasificada(
                url,
                headers,
                body,
            )
        )

    except TimeoutError as error:
        raise RuntimeError(
            "El servicio no pudo completar la consulta "
            "tras varios intentos. Intenta más tarde."
        ) from error

    return extraer_texto(datos)

if __name__ == "__main__":
    try:
        texto = consultar_modelo(
            "¿Cuál es la capital de Chile?",
            system_instruction=(
                "Responde únicamente con el nombre de la ciudad."
            ),
        )
        print("Respuesta:", texto)

    except (TypeError, ValueError, RuntimeError) as error:
        print("No se pudo completar la consulta:", error)