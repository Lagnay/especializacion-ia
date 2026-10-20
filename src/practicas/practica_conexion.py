import requests


def obtener_datos(url):
    respuesta_http = requests.get(url, timeout=5)
    datos = respuesta_http.json()
    return datos


url_rota = "https://servicio-de-prueba.invalid/datos"

print("Antes de la petición")

try:
    resultado = obtener_datos(url_rota)
except requests.exceptions.ConnectionError as error:
    resultado = None
    print("No se pudo conectar con el servicio.")
    print("Detalle técnico:", error)

print("Resultado:", resultado)
print("Fin del programa")