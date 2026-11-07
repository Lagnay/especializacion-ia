from datetime import datetime, timezone
from pathlib import Path

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.supervision import esperar_aprobacion
from src.trazas_agente import registrar_traza


RUTA_APROBACIONES = Path(
    "docs/modulo_02/unidad_2_4/bloque_23/aprobaciones.jsonl"
)


class ArgumentosReembolso(BaseModel):
    numero_pedido: str = Field(
        description="Identificador del pedido ficticio.",
    )
    monto: int = Field(
        gt=0,
        strict=True,
        description="Monto en pesos enteros positivos.",
    )


@tool(args_schema=ArgumentosReembolso)
def simular_reembolso(numero_pedido: str, monto: int) -> dict:
    """Simula un reembolso, previa aprobación humana. No mueve dinero."""
    aprobado = esperar_aprobacion(
        f"SIMULACIÓN: ¿aprobar un reembolso de {monto} pesos "
        f"para el pedido {numero_pedido}?",
        tiempo_limite_segundos=30,
    )

    decision = {
        "herramienta": "simular_reembolso",
        "argumentos": {
            "numero_pedido": numero_pedido,
            "monto": monto,
        },
        "aprobado": aprobado,
        "momento": datetime.now(timezone.utc).isoformat(),
    }

    registrar_traza(decision, RUTA_APROBACIONES)

    if not aprobado:
        return {
            "estado": "no_autorizado",
            "detalle": "No se ejecutó el reembolso simulado.",
            "aprobacion": decision,
        }

    return {
        "estado": "simulado",
        "detalle": (
            f"Reembolso simulado de {monto} pesos "
            f"para el pedido {numero_pedido}. "
            "No se movió dinero."
        ),
        "aprobacion": decision,
    }