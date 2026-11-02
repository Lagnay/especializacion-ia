import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)

from src.cadena_reclamos import construir_cadena


def normalizar_categoria(texto):
    return texto.strip().lower().removesuffix(".").strip()


def construir_paso_clasificacion(modelo):
    plantilla = PromptTemplate.from_template(
        "Clasifica la intención principal del mensaje de un cliente.\n\n"
        "Categorías:\n"
        "- queja: informa un problema o incumplimiento "
        "y busca atención, aunque lo formule como una pregunta.\n"
        "- pregunta: solicita información sin plantear "
        "un problema concreto ni una propuesta de mejora.\n"
        "- sugerencia: propone una mejora.\n"
        "- desconocida: es un saludo, no contiene información "
        "suficiente o no permite identificar una intención clara.\n\n"
        "Si el mensaje combina un problema concreto que requiere "
        "atención con una propuesta de mejora, prioriza queja. "
        "Devuelve únicamente una de estas palabras: "
        "pregunta, queja, sugerencia o desconocida. "
        "No respondas al cliente ni expliques tu clasificación.\n\n"
        "Mensaje:\n{mensaje}"
    )

    return (
        plantilla
        | modelo
        | StrOutputParser()
        | normalizar_categoria
    )


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


def construir_cadena_con_enrutamiento(paso_clasificacion, rutas):
    """Conecta un clasificador con las rutas recibidas."""
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


def construir_flujo_atencion(modelo):
    """Construye el flujo completo sin ejecutarlo."""
    paso_clasificacion = construir_paso_clasificacion(modelo)
    rutas = construir_rutas(modelo)

    return construir_cadena_con_enrutamiento(
        paso_clasificacion,
        rutas,
    )


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Falta configurar GEMINI_API_KEY.")

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        api_key=api_key,
        vertexai=False,
        timeout=30,
        max_retries=0,
    )

    flujo = construir_flujo_atencion(modelo)

    casos = [
        {
            "esperada": "pregunta",
            "mensaje": (
                "¿Qué información debo indicar cuando solicito "
                "la factura de un pedido?"
            ),
        },
        {
            "esperada": "queja",
            "mensaje": (
                "El pedido P-205 debía llegar el martes "
                "y llegó el miércoles. Compré dos cartones "
                "de leche y recibí uno. Pagué el pedido completo "
                "y necesito la factura por correo. Prefiero "
                "recibir el producto faltante antes que un "
                "reembolso. Puedo recibir entregas de 18 a 20, "
                "previa confirmación. Por favor, contáctenme "
                "por escrito."
            ),
        },
        {
            "esperada": "sugerencia",
            "mensaje": (
                "Me gustaría que la tienda permitiera elegir "
                "una franja horaria al hacer el pedido."
            ),
        },
        {
            "esperada": "desconocida",
            "mensaje": "Hola, buenos días.",
        },
    ]

    for caso in casos:
        print("\n=== MENSAJE ===")
        print(caso["mensaje"])

        resultado = flujo.invoke({
            "mensaje": caso["mensaje"],
        })

        print("Categoría esperada:", caso["esperada"])
        print(
            "Etiqueta normalizada:",
            repr(resultado["categoria"]),
        )
        print(
            "Coincide con la esperada:",
            resultado["categoria"] == caso["esperada"],
        )
        print("Respuesta:", resultado["respuesta"])