from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ArgumentosConsultaPedido(BaseModel):
    pedido_id: str = Field(
        description=(
            "Identificador del pedido ficticio, "
            "por ejemplo P-301."
        ),
    )

    incluir_historial: bool = Field(
        default=False,
        description=(
            "Indica si se necesita el historial de estados "
            "además del estado actual."
        ),
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