import os

import requests
from dotenv import load_dotenv


load_dotenv()


def armar_peticion(pregunta, modelo="gemini-3.5-flash-lite"):
    if not isinstance(pregunta, str):
        raise TypeError("La pregunta debe ser texto.")

    if not pregunta.strip():
        raise ValueError(
            "La pregunta no puede estar vacía ni contener solo espacios."
        )
    
    api_key = os.getenv("GEMINI_API_KEY")

    url = (
    f"https://generativelanguage.googleapis.com/"
    f"v1beta/models/{modelo}:generateContent"
    )

    headers = {
        "x-goog-api-key": api_key
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    return url, headers, body

def enviar_peticion(url, headers, body):
    try:
        respuesta_http = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30
        )
    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "El servicio no respondió dentro del tiempo de espera."
            ) from error
    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "No se pudo establecer conexión con el servicio."
            ) from error
    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            "Ocurrió otro error al realizar la solicitud HTTP."
            ) from error

    try:
        respuesta_http.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise RuntimeError(
            f"El servicio devolvió un error HTTP "
            f"{respuesta_http.status_code}."
        ) from error
    
    try:
        return respuesta_http.json()
    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError(
            "La respuesta del servicio no contiene JSON válido."
        ) from error

def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except KeyError as error:
        raise RuntimeError(
            f"La respuesta no contiene el campo esperado: {error}."
        ) from error
    except IndexError as error:
        raise RuntimeError(
            "La respuesta no contiene candidatos o partes suficientes."
        ) from error

def calcular_costo(datos, precio_entrada, precio_salida, precio_cache):

    try:
        uso = datos["usageMetadata"]

        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]

    except KeyError as error:
        raise RuntimeError(
            f"Falta un campo necesario para calcular el costo: {error}."
        ) from error

    tokens_cache = uso.get("cachedContentTokenCount", 0)
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)

    if not 0 <= tokens_cache <= tokens_entrada:
        raise ValueError(
            "Los tokens en caché deben estar entre cero "
            "y el total de tokens de entrada."
        )
    tokens_entrada_sin_cache = tokens_entrada - tokens_cache
    tokens_salida_facturables = tokens_salida + tokens_razonamiento

    costo_entrada = tokens_entrada_sin_cache * precio_entrada
    costo_cache = tokens_cache * precio_cache
    costo_salida = tokens_salida_facturables * precio_salida

    return costo_entrada + costo_cache + costo_salida

def obtener_dato_de_prueba(pregunta):
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)

if __name__ == "__main__":
    try:
        resultado = obtener_dato_de_prueba("¿Cuál es la capital de Escocia?")
        print(resultado)
    except (TypeError, ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)

    print("El programa llegó al final.")
