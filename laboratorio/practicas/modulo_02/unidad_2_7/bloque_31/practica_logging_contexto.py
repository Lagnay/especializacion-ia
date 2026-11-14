import hashlib
import logging
import sys
from uuid import uuid4

from .practica_logging_json import JsonFormatter
from .practica_trace_id import trace_id_var


logger = logging.getLogger("laboratorio.bloque31.contexto")


class JsonFormatterConContexto(JsonFormatter):
    def format(self, record):
        record.trace_id = trace_id_var.get()
        return super().format(record)


def huella(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def registrar_documento(documento):
    logger.info(
        "documento_inspeccionado",
        extra={
            "extra_data": {
                "documento_len": len(documento),
                "documento_sha256": huella(documento),
            },
        },
    )


def procesar(pregunta, documento):
    token = trace_id_var.set("trace-" + uuid4().hex)

    try:
        logger.info(
            "consulta_recibida",
            extra={
                "extra_data": {
                    "pregunta_len": len(pregunta),
                },
            },
        )

        registrar_documento(documento)
    finally:
        trace_id_var.reset(token)


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatterConContexto())
    logger.handlers = [handler]

    pregunta = "¿Cuántos intentos permite el cliente?"
    documento = "El cliente permite hasta tres intentos por consulta."

    # Dos consultas simuladas con el mismo texto de ejemplo.
    for _ in range(2):
        procesar(pregunta, documento)
        logger.info("fuera_de_consulta")