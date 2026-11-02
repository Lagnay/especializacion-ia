from unittest.mock import MagicMock

from langchain_core.messages import AIMessage
from langchain_core.runnables import (
    RunnableBranch,
    RunnablePassthrough,
)

from .practica_clasificacion_mensajes import (
    construir_paso_clasificacion,
)
from .practica_runnable_branch import (
    atender_queja,
    atender_sugerencia,
    atender_pregunta,
    atender_desconocida,
)


if __name__ == "__main__":
    modelo_falso = MagicMock()

    paso_clasificacion = construir_paso_clasificacion(
        modelo_falso
    )

    bifurcacion = RunnableBranch(
        (
            lambda datos: datos["categoria"] == "queja",
            atender_queja,
        ),
        (
            lambda datos: datos["categoria"] == "sugerencia",
            atender_sugerencia,
        ),
        (
            lambda datos: datos["categoria"] == "pregunta",
            atender_pregunta,
        ),
        atender_desconocida,
    )

    cadena = (
        RunnablePassthrough.assign(
            categoria=paso_clasificacion
        )
        | RunnablePassthrough.assign(
            respuesta=bifurcacion
        )
    )

    casos = [
        {
            "mensaje": "Faltó un cartón de leche.",
            "etiqueta": " Queja.\n",
        },
        {
            "mensaje": "Me gustaría elegir el horario de entrega.",
            "etiqueta": "SUGERENCIA",
        },
        {
            "mensaje": "¿Cómo solicito mi factura?",
            "etiqueta": "pregunta",
        },
        {
            "mensaje": "Hola.",
            "etiqueta": "desconocida",
        },
        {
            "mensaje": "Necesito ayuda.",
            "etiqueta": "queja urgente",
        },
    ]

    for caso in casos:
        modelo_falso.return_value = AIMessage(
            content=caso["etiqueta"]
        )

        resultado = cadena.invoke({
            "mensaje": caso["mensaje"],
        })

        print("Etiqueta normalizada:", repr(resultado["categoria"]))
        print(resultado["respuesta"])
        print()

    print("Llamadas simuladas:", modelo_falso.call_count)