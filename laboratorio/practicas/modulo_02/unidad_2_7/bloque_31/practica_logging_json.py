import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": datetime.fromtimestamp(
                record.created,
                timezone.utc,
            ).isoformat(timespec="seconds"),
            "level": record.levelname,
            "evento": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "datos": getattr(record, "extra_data", {}),
        }

        return json.dumps(payload, ensure_ascii=False)


if __name__ == "__main__":
    logger = logging.getLogger("laboratorio.bloque31.json")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]

    pregunta = "¿Dónde consulto mi pedido?"

    # Eventos simulados: no se ejecuta una recuperación real.
    logger.info(
        "consulta_recibida",
        extra={
            "trace_id": "trace-demo-001",
            "extra_data": {
                "pregunta_len": len(pregunta),
            },
        },
    )

    logger.info(
        "documentos_recuperados",
        extra={
            "trace_id": "trace-demo-001",
            "extra_data": {
                "n_documentos": 2,
            },
        },
    )