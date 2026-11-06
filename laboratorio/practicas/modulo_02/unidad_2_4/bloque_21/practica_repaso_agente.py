from langchain_core.agents import AgentAction

from src.herramientas_tienda import consultar_estado_pedido


if __name__ == "__main__":
    accion = AgentAction(
        tool="consultar_estado_pedido",
        tool_input={"pedido_id": " P-999 "},
        log="Acción creada manualmente para el repaso local.",
    )

    observacion = consultar_estado_pedido.invoke(
        accion.tool_input
    )

    pasos = [
        (accion, observacion),
    ]

    print("Tipo de acción:", type(accion).__name__)

    for accion, observacion in pasos:
        print("Herramienta:", accion.tool)
        print("Argumentos:", accion.tool_input)
        print("Observación:", observacion)

    usadas = [
        accion.tool
        for accion, _ in pasos
    ]

    print("Herramientas registradas:", usadas)