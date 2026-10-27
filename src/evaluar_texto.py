from src.cliente import consultar_modelo
from src.pipeline_texto import (
    procesar_texto,
    calcular_coincidencia,
)


CASOS = [
    {
        "consulta": (
            "Escribe exactamente «El cielo es azul.» en minúsculas "
            "y sin signos de puntuación ni comillas."
        ),
        "referencia": "El cielo es azul.",
    },
    {
        "consulta": "¿Qué es Python?",
        "referencia": (
            "Python es un lenguaje de programación interpretado."
        ),
    },
    {
        "consulta": (
            "¿Para qué sirve la fotosíntesis en las plantas?"
        ),
        "referencia": (
            "La fotosíntesis permite a las plantas producir "
            "alimento utilizando la luz."
        ),
    },
]


if __name__ == "__main__":
    completados = 0

    for numero, caso in enumerate(CASOS, start=1):
        print(f"\n=== CASO {numero} ===")
        print("Consulta:", caso["consulta"])
        print("Referencia:", caso["referencia"])

        try:
            respuesta = consultar_modelo(
                caso["consulta"],
                system_instruction=(
                    "Responde en español, con una sola oración breve "
                    "y sin formato Markdown."
                ),
            )

            referencia = caso["referencia"]

            coincidencia_cruda = calcular_coincidencia(
                referencia.split(),
                respuesta.split(),
            )

            tokens_referencia = procesar_texto(referencia)
            tokens_respuesta = procesar_texto(respuesta)

            coincidencia_procesada = calcular_coincidencia(
                tokens_referencia,
                tokens_respuesta,
            )

            print("Respuesta original:", respuesta)
            print("Tokens de referencia:", tokens_referencia)
            print("Tokens de respuesta:", tokens_respuesta)
            print(
                f"Coincidencia texto crudo: "
                f"{coincidencia_cruda:.1%}"
            )
            print(
                f"Coincidencia texto procesado: "
                f"{coincidencia_procesada:.1%}"
            )

            completados += 1

        except (TypeError, ValueError, RuntimeError) as error:
            print("No se pudo completar el caso:", error)

    print(f"\nCasos completados: {completados}/{len(CASOS)}")