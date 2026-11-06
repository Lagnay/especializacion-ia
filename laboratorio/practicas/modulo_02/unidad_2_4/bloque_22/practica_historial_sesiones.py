from langchain_core.chat_history import (
    InMemoryChatMessageHistory,
)


historiales = {}


def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()

    return historiales[session_id]


def cerrar_sesion(session_id: str):
    historiales.pop(session_id, None)


if __name__ == "__main__":
    historial_1 = obtener_historial("cliente_1")
    historial_1.add_user_message(
        "Estoy consultando el pedido P-301."
    )
    historial_1.add_ai_message(
        "El pedido P-301 está en preparación."
    )

    historial_2 = obtener_historial("cliente_2")
    historial_2.add_user_message(
        "Estoy consultando el pedido P-302."
    )
    historial_2.add_ai_message(
        "El pedido P-302 está despachado."
    )

    print("Mensajes de cliente_1:", len(historial_1.messages))
    print("Mensajes de cliente_2:", len(historial_2.messages))

    recuperado = obtener_historial("cliente_1")

    print(
        "Se recupera el mismo objeto:",
        recuperado is historial_1,
    )

    recuperado.add_user_message(
        "¿Y ese pedido ya fue entregado?"
    )
    recuperado.add_ai_message(
        "Su estado registrado sigue siendo en preparación."
    )

    for session_id in ["cliente_1", "cliente_2"]:
        historial = obtener_historial(session_id)

        print("\n===", session_id, "===")
        print("Cantidad de mensajes:", len(historial.messages))

        for mensaje in historial.messages:
            print(mensaje.type + ":", mensaje.content)

    cerrar_sesion("cliente_1")
    cerrar_sesion("cliente_1")

    print(
        "\nCliente 1 sigue en el registro:",
        "cliente_1" in historiales,
    )
    print(
        "Mensajes de cliente_2:",
        len(obtener_historial("cliente_2").messages),
    )