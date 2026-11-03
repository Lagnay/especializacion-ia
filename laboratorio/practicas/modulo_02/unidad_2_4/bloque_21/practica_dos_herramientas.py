from langchain_core.tools import tool

from .practica_herramienta_stock import consultar_stock


@tool
def consultar_estado_pedido(pedido_id: str) -> str:
    """Consulta el estado de un pedido del registro ficticio a partir de su identificador.

    Usar cuando el usuario pregunta por el estado de un pedido como P-301.
    """
    pedidos = {
        "P-301": "en preparación",
        "P-302": "despachado",
    }

    identificador = pedido_id.strip().upper()

    try:
        estado = pedidos[identificador]

    except KeyError:
        return "Pedido no encontrado en el registro ficticio."

    return f"Estado ficticio de {identificador}: {estado}."


if __name__ == "__main__":
    herramientas = [
        consultar_stock,
        consultar_estado_pedido,
    ]

    for herramienta in herramientas:
        print("Herramienta disponible:", herramienta.name)

    print(consultar_stock.invoke({
        "producto": "arroz",
    }))

    print(consultar_estado_pedido.invoke({
        "pedido_id": "p-301",
    }))

    print(consultar_estado_pedido.invoke({
        "pedido_id": "P-999",
    }))