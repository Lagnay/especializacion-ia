import logging

from langchain_core.runnables import RunnableLambda

from src.practicas.practica_fallback_basico import (
    procesar_principal,
)
from src.practicas.practica_fallback_logging import (
    responder_y_registrar,
)


logger = logging.getLogger(__name__)


def preparar_datos(datos):
    print("Se ejecuta la preparación.")

    if datos["fallar_preparacion"]:
        raise ConnectionError(
            "Fallo simulado antes del paso protegido."
        )

    return datos


def ejecutar_seguro(flujo, datos):
    try:
        return flujo.invoke(datos)

    except Exception:
        logger.exception("No se pudo completar el flujo.")

        return (
            "No pude procesar tu mensaje en este momento. "
            "Intenta de nuevo más tarde."
        )


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

    flujo = RunnableLambda(preparar_datos) | protegido

    casos = [
        {
            "nombre": "ÉXITO",
            "simular_fallo": False,
            "fallar_preparacion": False,
        },
        {
            "nombre": "FALLO DEL PRINCIPAL",
            "simular_fallo": True,
            "fallar_preparacion": False,
        },
        {
            "nombre": "FALLO EN LA PREPARACIÓN",
            "simular_fallo": False,
            "fallar_preparacion": True,
        },
    ]

    for caso in casos:
        print("\n===", caso["nombre"], "===")

        resultado = ejecutar_seguro(
            flujo,
            {
                "mensaje": "Falta un cartón de leche.",
                "simular_fallo": caso["simular_fallo"],
                "fallar_preparacion": caso["fallar_preparacion"],
            },
        )

        print("Resultado:", resultado)

    print("\nEl programa llegó al final.")