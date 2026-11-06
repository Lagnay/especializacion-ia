import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from .practica_agente_actual import construir_agente_actual


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

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

    agente = construir_agente_actual(modelo)

    config_1 = {
        "configurable": {
            "thread_id": "cliente_1",
        },
        "recursion_limit": 12,
    }
    config_2 = {
        "configurable": {
            "thread_id": "cliente_2",
        },
        "recursion_limit": 12,
    }

    consultas = [
        (
            "CLIENTE 1 - TURNO 1",
            config_1,
            "¿Cuál es el estado del pedido P-301? "
            "Incluye su historial de estados.",
        ),
        (
            "CLIENTE 1 - TURNO 2",
            config_1,
            "¿Y ese mismo pedido ya fue entregado?",
        ),
        (
            "CLIENTE 2 - SESION NUEVA",
            config_2,
            "¿Qué pedido te mencioné antes?",
        ),
    ]

    for titulo, config, pregunta in consultas:
        cantidad_previa = len(
            agente.get_state(config).values.get("messages", [])
        )

        print("\n===", titulo, "===")
        print("Entrada:", pregunta)
        print("Mensajes previos:", cantidad_previa)

        try:
            resultado = agente.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": pregunta,
                        }
                    ]
                },
                config=config,
            )

        except Exception:
            logger.exception(
                "No se pudo completar %s.",
                titulo,
            )
            break

        nuevos = resultado["messages"][cantidad_previa:]

        for mensaje in nuevos:
            if isinstance(mensaje, AIMessage):
                for llamada in mensaje.tool_calls:
                    print("Herramienta:", llamada["name"])
                    print("Argumentos:", llamada["args"])

            elif isinstance(mensaje, ToolMessage):
                print("Observación:", mensaje.content)

        print(
            "Respuesta:",
            StrOutputParser().invoke(
                resultado["messages"][-1]
            ),
        )

    print("\n=== HISTORIALES GUARDADOS ===")

    for config in [config_1, config_2]:
        mensajes = (
            agente.get_state(config).values.get("messages", [])
        )
        preguntas = [
            mensaje.content
            for mensaje in mensajes
            if mensaje.type == "human"
        ]

        print("Sesión:", config["configurable"]["thread_id"])
        print("Cantidad de mensajes:", len(mensajes))
        print("Mensajes del usuario:", preguntas)