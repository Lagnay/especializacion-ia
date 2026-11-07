from datetime import datetime, timezone

from langchain_core.tools import tool

from .practica_aprobacion_basica import ArgumentosReembolso
from .practica_aprobacion_timeout import esperar_aprobacion


registro_aprobaciones = []


@tool(args_schema=ArgumentosReembolso)
def simular_reembolso(numero_pedido: str, monto: int) -> str:
    """Simula un reembolso en pesos enteros, previa aprobación humana."""
    aprobado = esperar_aprobacion(
        f"SIMULACIÓN: ¿aprobar un reembolso de {monto} pesos "
        f"para el pedido {numero_pedido}?"
    )

    registro_aprobaciones.append({
        "herramienta": "simular_reembolso",
        "argumentos": {
            "numero_pedido": numero_pedido,
            "monto": monto,
        },
        "aprobado": aprobado,
        "momento": datetime.now(timezone.utc).isoformat(),
    })

    if not aprobado:
        return "Reembolso simulado no autorizado: no se ejecutó."

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
    print("Registro:", registro_aprobaciones)
    print("El programa llegó al final.")