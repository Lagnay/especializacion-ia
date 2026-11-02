from langchain_core.runnables import RunnableLambda


def procesar_principal(datos):
    print("Se ejecuta el paso principal.")

    if datos["simular_fallo"]:
        raise ConnectionError("Fallo de conexión simulado.")

    return "Respuesta principal para: " + datos["mensaje"]


def responder_respaldo(datos):
    print("Se ejecuta la alternativa de respaldo.")

    return (
        "No pude completar la consulta en este momento. "
        "Puedes intentarlo de nuevo más tarde."
    )


if __name__ == "__main__":
    principal = RunnableLambda(procesar_principal)
    respaldo = RunnableLambda(responder_respaldo)

    protegido = principal.with_fallbacks(
        [respaldo],
        exceptions_to_handle=(ConnectionError,),
    )

    for simular_fallo in [False, True]:
        print("\nSimular fallo:", simular_fallo)

        resultado = protegido.invoke({
            "mensaje": "Falta un cartón de leche.",
            "simular_fallo": simular_fallo,
        })

        print("Resultado:", resultado)

    print("\nEl programa llegó al final.")