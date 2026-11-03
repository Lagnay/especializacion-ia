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


if __name__ == "__main__":
    print("Nombre:", consultar_stock.name)
    print("Argumentos:", consultar_stock.args)

    print(consultar_stock.invoke({
        "producto": "Arroz",
    }))

    print(consultar_stock.invoke({
        "producto": "pan",
    }))