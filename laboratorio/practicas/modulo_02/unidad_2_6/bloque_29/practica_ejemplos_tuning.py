import json

from google.genai import types


PARES_EJEMPLO = [
    (
        "TimeoutError: la conexión tardó demasiado en responder.",
        {
            "categoria": "red",
            "accion_sugerida": "reintentar con backoff exponencial",
        },
    ),
    (
        "HTTP 401: la credencial de acceso no es válida.",
        {
            "categoria": "autenticacion",
            "accion_sugerida": "revisar la credencial antes de reintentar",
        },
    ),
    (
        "HTTP 429: se superó el límite de peticiones por minuto.",
        {
            "categoria": "cuota",
            "accion_sugerida": "esperar y revisar el límite antes de reintentar",
        },
    ),
]


def construir_ejemplos():
    return [
        types.TuningExample(
            text_input=entrada,
            output=json.dumps(salida, ensure_ascii=False),
        )
        for entrada, salida in PARES_EJEMPLO
    ]


if __name__ == "__main__":
    ejemplos = construir_ejemplos()
    print("Ejemplos preparados:", len(ejemplos))

    for numero, ejemplo in enumerate(ejemplos, start=1):
        print(f"\n=== EJEMPLO {numero} ===")
        print("Entrada:", ejemplo.text_input)
        print("Salida esperada:", ejemplo.output)
        print("Tipo de output:", type(ejemplo.output).__name__)

        salida = json.loads(ejemplo.output)
        print("Categoría al leer el JSON:", salida["categoria"])

    print("\nNo se creó ningún cliente ni se envió un trabajo.")