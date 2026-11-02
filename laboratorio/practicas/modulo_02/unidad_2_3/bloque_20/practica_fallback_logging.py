import logging

from langchain_core.runnables import RunnableLambda

from .practica_fallback_basico import (
    procesar_principal,
    responder_respaldo,
)


logger = logging.getLogger(__name__)


def responder_y_registrar(datos):
    logger.warning(
        "El paso principal falló: %s",
        datos["error"],
    )

    return responder_respaldo(datos)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    principal = RunnableLambda(procesar_principal)
    respaldo = RunnableLambda(responder_y_registrar)

    protegido = principal.with_fallbacks(
        [respaldo],
        exceptions_to_handle=(ConnectionError,),
        exception_key="error",
    )

    for simular_fallo in [False, True]:
        print("\nSimular fallo:", simular_fallo)

        resultado = protegido.invoke({
            "mensaje": "Falta un cartón de leche.",
            "simular_fallo": simular_fallo,
        })

        print("Resultado:", resultado)

    print("\nEl programa llegó al final.")