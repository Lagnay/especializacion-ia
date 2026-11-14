import logging
import sys
from uuid import uuid4

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.fake import FakeListLLM

from .practica_logging_contexto import JsonFormatterConContexto
from .practica_trace_id import trace_id_var


logger = logging.getLogger("laboratorio.bloque31.callbacks")


class HandlerDeTrazas(BaseCallbackHandler):
    raise_error = True

    def on_llm_start(
        self,
        serialized,
        prompts,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        logger.info(
            "llm_inicio",
            extra={
                "extra_data": {
                    "run_id": str(run_id),
                    "n_prompts": len(prompts),
                },
            },
        )

    def on_llm_end(
        self,
        response,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        texto = response.generations[0][0].text

        logger.info(
            "llm_fin",
            extra={
                "extra_data": {
                    "run_id": str(run_id),
                    "respuesta_len": len(texto),
                },
            },
        )


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.propagate = False

    salida = logging.StreamHandler(sys.stdout)
    salida.setFormatter(JsonFormatterConContexto())
    logger.handlers = [salida]

    modelo = FakeListLLM(responses=["Respuesta simulada."])

    token = trace_id_var.set("trace-" + uuid4().hex)

    try:
        resultado = modelo.invoke(
            "Texto de prueba.",
            config={"callbacks": [HandlerDeTrazas()]},
        )
    finally:
        trace_id_var.reset(token)

    print("Resultado:", resultado)
    print("Contexto al terminar:", trace_id_var.get())