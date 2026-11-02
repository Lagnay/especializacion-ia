from unittest.mock import MagicMock

from langchain_core.messages import AIMessage
from langchain_core.runnables import (
    RunnableBranch,
    RunnablePassthrough,
)

from src.practicas.practica_clasificacion_mensajes import (
    construir_paso_clasificacion,
)
from src.practicas.practica_rutas_atencion import (
    construir_rutas,
)


def construir_flujo_atencion(modelo):
    paso_clasificacion = construir_paso_clasificacion(modelo)
    rutas = construir_rutas(modelo)

    bifurcacion = RunnableBranch(
        (
            lambda datos: datos["categoria"] == "queja",
            rutas["queja"],
        ),
        (
            lambda datos: datos["categoria"] == "sugerencia",
            rutas["sugerencia"],
        ),
        (
            lambda datos: datos["categoria"] == "pregunta",
            rutas["pregunta"],
        ),
        rutas["desconocida"],
    )

    return (
        RunnablePassthrough.assign(
            categoria=paso_clasificacion
        )
        | RunnablePassthrough.assign(
            respuesta=bifurcacion
        )
    )


if __name__ == "__main__":
    casos = [
        {
            "mensaje": "Faltó un cartón de leche en mi pedido.",
            "respuestas": [
                AIMessage(content=" Queja.\n"),
                AIMessage(content="Análisis simulado del faltante."),
                AIMessage(content="Plan simulado de atención."),
                AIMessage(content="Borrador simulado para la queja."),
            ],
        },
        {
            "mensaje": "Me gustaría elegir el horario de entrega.",
            "respuestas": [
                AIMessage(content="SUGERENCIA"),
                AIMessage(
                    content="Respuesta simulada a la sugerencia."
                ),
            ],
        },
        {
            "mensaje": "¿Cómo solicito mi factura?",
            "respuestas": [
                AIMessage(content="pregunta"),
                AIMessage(
                    content="Respuesta simulada sobre la factura."
                ),
            ],
        },
        {
            "mensaje": "Hola.",
            "respuestas": [
                AIMessage(content="desconocida"),
            ],
        },
        {
            "mensaje": "Necesito ayuda.",
            "respuestas": [
                AIMessage(content="queja urgente"),
            ],
        },
    ]

    for caso in casos:
        modelo_falso = MagicMock()
        modelo_falso.side_effect = caso["respuestas"]

        flujo = construir_flujo_atencion(modelo_falso)

        resultado = flujo.invoke({
            "mensaje": caso["mensaje"],
        })

        print("Mensaje:", resultado["mensaje"])
        print("Etiqueta normalizada:", repr(resultado["categoria"]))
        print("Respuesta:", resultado["respuesta"])
        print("Llamadas simuladas:", modelo_falso.call_count)
        print()