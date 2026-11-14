import logging
import sys
from uuid import uuid4

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.documents import Document
from langchain_core.language_models.fake import FakeListLLM
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableLambda

from .practica_logging_contexto import JsonFormatterConContexto
from .practica_trace_id import trace_id_var


logger = logging.getLogger("laboratorio.bloque31.cadena")


class RecuperadorSimulado(BaseRetriever):
    def _get_relevant_documents(self, query, *, run_manager):
        return [
            Document(
                page_content="El cliente permite hasta tres intentos.",
                metadata={"fuente": "ejemplo_local"},
            )
        ]


class HandlerDeCadena(BaseCallbackHandler):
    raise_error = True

    def __init__(self):
        self.raiz = None
        self.vinculos = []

    def registrar(self, evento, run_id, parent_run_id, **datos):
        logger.info(
            evento,
            extra={
                "extra_data": {
                    "run_id": str(run_id),
                    "parent_run_id": (
                        str(parent_run_id) if parent_run_id else None
                    ),
                    **datos,
                },
            },
        )

    def on_chain_start(
        self, serialized, inputs, *, run_id, parent_run_id=None, **kwargs
    ):
        if parent_run_id is None:
            self.raiz = run_id
            self.registrar("cadena_inicio", run_id, parent_run_id)

    def on_chain_end(
        self, outputs, *, run_id, parent_run_id=None, **kwargs
    ):
        if parent_run_id is None:
            self.registrar("cadena_fin", run_id, parent_run_id)

    def on_retriever_start(
        self, serialized, query, *, run_id, parent_run_id=None,
        metadata=None, **kwargs
    ):
        self.vinculos.append(
            ("recuperador", parent_run_id, (metadata or {}).get("trace_id"))
        )
        self.registrar(
            "recuperacion_inicio", run_id, parent_run_id,
            pregunta_len=len(query)
        )

    def on_retriever_end(
        self, documents, *, run_id, parent_run_id=None, **kwargs
    ):
        self.registrar(
            "recuperacion_fin", run_id, parent_run_id,
            n_documentos=len(documents)
        )

    def on_llm_start(
        self, serialized, prompts, *, run_id, parent_run_id=None,
        metadata=None, **kwargs
    ):
        self.vinculos.append(
            ("modelo", parent_run_id, (metadata or {}).get("trace_id"))
        )
        self.registrar(
            "llm_inicio", run_id, parent_run_id,
            n_prompts=len(prompts)
        )

    def on_llm_end(
        self, response, *, run_id, parent_run_id=None, **kwargs
    ):
        self.registrar(
            "llm_fin", run_id, parent_run_id,
            respuesta_len=len(response.generations[0][0].text)
        )


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.propagate = False

    salida = logging.StreamHandler(sys.stdout)
    salida.setFormatter(JsonFormatterConContexto())
    logger.handlers = [salida]

    recuperador = RecuperadorSimulado()
    a_texto = RunnableLambda(
        lambda documentos: "\n\n".join(
            documento.page_content for documento in documentos
        )
    )
    modelo = FakeListLLM(responses=["Respuesta simulada."])
    cadena = recuperador | a_texto | modelo

    handler = HandlerDeCadena()
    identificador = "trace-" + uuid4().hex
    token = trace_id_var.set(identificador)

    try:
        resultado = cadena.invoke(
            "¿Cuántos intentos permite el cliente?",
            config={
                "callbacks": [handler],
                "metadata": {"trace_id": identificador},
            },
        )
    finally:
        trace_id_var.reset(token)

    print("Resultado:", resultado)

    for etapa, padre, traza in handler.vinculos:
        print(
            f"{etapa}: hijo de la cadena = {padre == handler.raiz}; "
            f"trace_id recibido = {traza == identificador}"
        )

    print("Contexto al terminar:", trace_id_var.get())