import os

import requests
from dotenv import load_dotenv


load_dotenv()

def armar_peticion(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.5-flash-lite"

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
    respuesta_http = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=30
    )

    respuesta_http.raise_for_status()
    return respuesta_http.json()

def extraer_texto(datos):
    return datos["candidates"][0]["content"]["parts"][0]["text"]

def obtener_dato_de_prueba(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.5-flash-lite"

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

    respuesta_http = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=30
    )

    respuesta_http.raise_for_status()
    datos = respuesta_http.json()
    return datos["candidates"][0]["content"]["parts"][0]["text"]

def obtener_dato_de_prueba_refactorizado(pregunta):
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)

pregunta_prueba = (
    "Confirma en una frase corta que esta conexión funciona, "
    "explicándome qué es el alma según la ciencia y la filosofía."
)

print("=== VERSIÓN ORIGINAL ===")
resultado_original = obtener_dato_de_prueba(pregunta_prueba)
print(resultado_original)

print("\n=== VERSIÓN REFACTORIZADA ===")
resultado_refactorizado = obtener_dato_de_prueba_refactorizado(
    pregunta_prueba
)
print(resultado_refactorizado)