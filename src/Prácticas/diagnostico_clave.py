import os

import requests
from dotenv import dotenv_values


def comprobar_clave(clave):
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash-lite:generateContent"
    )

    respuesta_http = requests.post(
        url,
        headers={"x-goog-api-key": clave},
        json={
            "contents": [
                {"parts": [{"text": "Responde únicamente: OK"}]}
            ]
        },
        timeout=30
    )

    print("Estado HTTP:", respuesta_http.status_code)
    print("Petición aceptada:", respuesta_http.status_code == 200)


clave_entorno = os.getenv("GEMINI_API_KEY")
clave_archivo = dotenv_values(".env").get("GEMINI_API_KEY")

print("PRUEBA CON EL VALOR DEL ENTORNO")
comprobar_clave(clave_entorno)

print("PRUEBA CON EL VALOR DEL ARCHIVO .env")
comprobar_clave(clave_archivo)