from langchain_core.tools import tool


@tool
def consultar_stock(producto: str) -> str:
    """Consulta las unidades disponibles de un producto del catálogo ficticio.

    Usar cuando el usuario pregunta cuánto stock queda de un producto.
    """
    stock = {
        "arroz": 12,
        "leche": 8,
    }

    producto_normalizado = producto.strip().lower()

    if producto_normalizado not in stock:
        return "Producto no encontrado en el catálogo ficticio."

    return (
        f"Stock ficticio de {producto_normalizado}: "
        f"{stock[producto_normalizado]} unidades."
    )


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