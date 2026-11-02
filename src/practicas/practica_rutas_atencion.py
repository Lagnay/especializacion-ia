from unittest.mock import MagicMock

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

from src.cadena_reclamos import construir_cadena


def construir_rutas(modelo):
    plantilla_pregunta = PromptTemplate.from_template(
        "Prepara una respuesta breve para esta consulta. "
        "Información confirmada para este ejercicio ficticio: "
        "para solicitar una factura, el cliente debe escribir al "
        "canal de soporte de la tienda e indicar el número del pedido. "
        "Usa únicamente esa información para responder. "
        "Si no cubre la consulta, indica que necesitas más información. "
        "No inventes enlaces, direcciones, políticas ni plazos. "
        "Devuelve únicamente el borrador de respuesta.\n\n"
        "Consulta:\n{mensaje}"
    )

    plantilla_sugerencia = PromptTemplate.from_template(
        "Prepara una respuesta breve y cordial a esta sugerencia. "
        "Agradece la propuesta y reconoce qué mejora plantea. "
        "No afirmes que se registró o evaluó ni que se implementará. "
        "No inventes procesos internos ni plazos. "
        "Devuelve únicamente el borrador de respuesta.\n\n"
        "Sugerencia:\n{mensaje}"
    )

    return {
        "pregunta": (
            plantilla_pregunta | modelo | StrOutputParser()
        ),
        "queja": construir_cadena(modelo),
        "sugerencia": (
            plantilla_sugerencia | modelo | StrOutputParser()
        ),
        "desconocida": RunnableLambda(
            lambda datos: (
                "¿Podrías explicar qué necesitas? "
                "Puedes hacer una consulta, describir un problema "
                "o proponer una mejora."
            )
        ),
    }


if __name__ == "__main__":
    casos = [
        {
            "categoria": "pregunta",
            "mensaje": "¿Cómo solicito mi factura?",
            "respuestas": [
                AIMessage(
                    content="Respuesta simulada sobre la factura."
                ),
            ],
        },
        {
            "categoria": "queja",
            "mensaje": "Faltó un cartón de leche en mi pedido.",
            "respuestas": [
                AIMessage(content="Análisis simulado del faltante."),
                AIMessage(content="Plan simulado de atención."),
                AIMessage(content="Borrador simulado para la queja."),
            ],
        },
        {
            "categoria": "sugerencia",
            "mensaje": "Me gustaría elegir el horario de entrega.",
            "respuestas": [
                AIMessage(
                    content="Respuesta simulada a la sugerencia."
                ),
            ],
        },
        {
            "categoria": "desconocida",
            "mensaje": "Hola.",
            "respuestas": [],
        },
    ]

    for caso in casos:
        modelo_falso = MagicMock()
        modelo_falso.side_effect = caso["respuestas"]

        rutas = construir_rutas(modelo_falso)
        ruta = rutas[caso["categoria"]]

        respuesta = ruta.invoke({
            "mensaje": caso["mensaje"],
        })

        print("Categoría:", caso["categoria"])
        print("Respuesta:", respuesta)
        print("Llamadas simuladas:", modelo_falso.call_count)
        print()