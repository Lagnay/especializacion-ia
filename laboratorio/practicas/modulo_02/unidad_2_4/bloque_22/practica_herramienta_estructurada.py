from langchain_core.tools import tool
from pydantic import ValidationError

from .practica_argumentos_herramienta import (
    ArgumentosConsultaPedido,
)


PEDIDOS = {
    "P-301": {
        "actual": "en preparación",
        "historial": ["recibido", "en preparación"],
    },
    "P-302": {
        "actual": "despachado",
        "historial": [
            "recibido",
            "en preparación",
            "despachado",
        ],
    },
}


@tool(
    "consultar_pedido_con_historial",
    args_schema=ArgumentosConsultaPedido,
)
def consultar_pedido_detallado(
    pedido_id: str,
    incluir_historial: bool = False,
) -> str:
    """Consulta el estado de un pedido ficticio y, si se solicita, su historial de estados."""
    identificador = pedido_id.strip().upper()
    pedido = PEDIDOS.get(identificador)

    if pedido is None:
        return "Pedido no encontrado en el registro ficticio."

    texto_estado = (
        f"Estado ficticio de {identificador}: "
        f"{pedido['actual']}."
    )

    if not incluir_historial:
        return texto_estado

    historial = " -> ".join(pedido["historial"])

    return f"{texto_estado} Historial: {historial}."


if __name__ == "__main__":
    casos = [
        (
            "SIN HISTORIAL",
            {"pedido_id": "P-301"},
        ),
        (
            "CON HISTORIAL",
            {
                "pedido_id": "P-301",
                "incluir_historial": True,
            },
        ),
        (
            "PEDIDO INEXISTENTE",
            {
                "pedido_id": "P-999",
                "incluir_historial": True,
            },
        ),
        (
            "BOOLEANO INVALIDO",
            {
                "pedido_id": "P-301",
                "incluir_historial": "tal vez",
            },
        ),
        (
            "CAMPO OBLIGATORIO AUSENTE",
            {"incluir_historial": True},
        ),
    ]

    print(
        "Nombre de herramienta:",
        consultar_pedido_detallado.name,
    )

    for nombre, datos in casos:
        print("\n===", nombre, "===")

        try:
            resultado = consultar_pedido_detallado.invoke(datos)
            print(resultado)

        except ValidationError as error:
            print(
                "Error controlado:",
                error.errors()[0]["type"],
            )