from langchain_core.runnables import RunnableLambda

from .practica_fallback_basico import (
    procesar_principal,
    responder_respaldo,
)


def procesar_alternativa(datos):
    print("Se ejecuta el primer respaldo.")

    if datos["fallar_respaldo"]:
        raise ConnectionError("El primer respaldo también falló.")

    return "Respuesta alternativa para: " + datos["mensaje"]


if __name__ == "__main__":
    principal = RunnableLambda(procesar_principal)
    alternativa = RunnableLambda(procesar_alternativa)
    respaldo_final = RunnableLambda(responder_respaldo)

    protegido = principal.with_fallbacks(
        [alternativa, respaldo_final],
        exceptions_to_handle=(ConnectionError,),
    )

    casos = [
        {
            "nombre": "ÉXITO PRINCIPAL",
            "simular_fallo": False,
            "fallar_respaldo": False,
        },
        {
            "nombre": "PRIMER RESPALDO",
            "simular_fallo": True,
            "fallar_respaldo": False,
        },
        {
            "nombre": "RESPALDO FINAL",
            "simular_fallo": True,
            "fallar_respaldo": True,
        },
    ]

    for caso in casos:
        print("\n===", caso["nombre"], "===")

        resultado = protegido.invoke({
            "mensaje": "Falta un cartón de leche.",
            "simular_fallo": caso["simular_fallo"],
            "fallar_respaldo": caso["fallar_respaldo"],
        })

        print("Resultado:", resultado)

    print("\nEl programa llegó al final.")