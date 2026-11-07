from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ArgumentosReembolso(BaseModel):
    numero_pedido: str = Field(
        description="Identificador del pedido ficticio.",
    )
    monto: int = Field(
        gt=0,
        strict=True,
        description="Monto del reembolso en pesos enteros positivos.",
    )


def pedir_aprobacion(mensaje: str) -> bool:
    try:
        respuesta = input(mensaje)
    except EOFError:
        return False

    return respuesta.strip().lower() == "s"


@tool(args_schema=ArgumentosReembolso)
def simular_reembolso(numero_pedido: str, monto: int) -> str:
    """Simula un reembolso en pesos enteros, previa aprobación humana."""
    aprobado = pedir_aprobacion(
        f"SIMULACIÓN: reembolso de {monto} pesos "
        f"para el pedido {numero_pedido}. "
        "¿Aprobar? (s/n): "
    )

    if not aprobado:
        return "Simulación rechazada: no se ejecutó la acción."

    print("Ejecutando únicamente la simulación local.")

    return (
        f"Reembolso simulado de {monto} pesos "
        f"para el pedido {numero_pedido}. "
        "No se movió dinero."
    )


if __name__ == "__main__":
    resultado = simular_reembolso.invoke({
        "numero_pedido": "P-301",
        "monto": 1500,
    })

    print("Resultado:", resultado)
    print("El programa llegó al final.")