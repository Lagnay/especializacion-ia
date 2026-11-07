import json
from datetime import datetime, timezone
from pathlib import Path

from .practica_reembolso_supervisado import (
    registro_aprobaciones,
    simular_reembolso,
)


def registrar_traza(registro: dict, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)

    linea = json.dumps(registro, ensure_ascii=False)

    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(linea + "\n")


if __name__ == "__main__":
    ruta = Path(
        "docs/modulo_02/unidad_2_4/bloque_23/"
        "trazas_supervision.jsonl"
    )

    argumentos = {
        "numero_pedido": "P-301",
        "monto": 1500,
    }

    resultado = simular_reembolso.invoke(argumentos)

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": "practica_local",
        "origen": "invocacion_directa_sin_modelo",
        "entrada": (
            "Simular un reembolso de 1500 pesos "
            "para el pedido P-301."
        ),
        "acciones": [
            {
                "herramienta": simular_reembolso.name,
                "argumentos": argumentos,
                "aprobacion": registro_aprobaciones[-1],
                "observacion": resultado,
            }
        ],
        "resultado": resultado,
    }

    registrar_traza(registro, ruta)

    print("Resultado:", resultado)
    print("Traza guardada en:", ruta.resolve())
    print("El programa llegó al final.")