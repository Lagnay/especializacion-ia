import json
import re
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.corpus_rag import fragmentar_corpus
from src.logging_rag import registrar_evento
from src.indexar_corpus import RUTA_INDICE
from src.registro_rag import construir_componentes


RUTA_SIMULADA = (
    Path(__file__).resolve().parents[1]
    / "vectorstore/gate2_simulado"
)
PREGUNTA_ENSAYO = "¿Cuántos intentos permite el cliente REST?"


def responder_simulado(mensajes):
    referencia = re.search(
        r"\[(\d+)\] El cliente REST permite hasta tres intentos por consulta\.",
        mensajes[1].content,
    )

    if referencia is None:
        raise ValueError(
            "Falta el fragmento requerido para este ensayo."
        )

    return AIMessage(content=(
        "El cliente REST permite hasta tres intentos "
        f"por consulta [{referencia.group(1)}]."
    ))


@contextmanager
def abrir_componentes_simulados(ruta=None):
    ruta = RUTA_SIMULADA if ruta is None else Path(ruta)
    fragmentos = fragmentar_corpus()

    datos = {
        "modelo": "DeterministicFakeEmbedding",
        "dimensiones": 16,
        "fragmentos": [
            {"texto": d.page_content, "metadatos": d.metadata}
            for d in fragmentos
        ],
    }
    huella = sha256(
        json.dumps(datos, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    nombre = "simulado-" + huella

    with chromadb.PersistentClient(
        path=str(ruta),
        settings=Settings(anonymized_telemetry=False),
    ) as cliente:
        indice = Chroma(
            client=cliente,
            collection_name=nombre,
            embedding_function=DeterministicFakeEmbedding(
                size=16
            ),
        )

        ids = [
            f"fragmento-{n:03d}"
            for n in range(1, len(fragmentos) + 1)
        ]
        existentes = set(indice.get(include=[])["ids"])

        if existentes - set(ids):
            raise ValueError(
                "El índice simulado contiene IDs inesperados."
            )

        pendientes = [
            (identificador, documento)
            for identificador, documento in zip(
                ids, fragmentos, strict=True
            )
            if identificador not in existentes
        ]

        if pendientes:
            indice.add_documents(
                [documento for _, documento in pendientes],
                ids=[
                    identificador
                    for identificador, _ in pendientes
                ],
            )

        if set(indice.get(include=[])["ids"]) != set(ids):
            raise ValueError(
                "El índice simulado quedó incompleto."
            )

        informacion = {
            "coleccion": nombre,
            "fragmentos": len(fragmentos),
            "dimensiones": 16,
            "estado_indice": (
                "creado" if not existentes
                else "completado" if pendientes
                else "reutilizado"
            ),
            "k": len(fragmentos),
        }

        recuperador = indice.as_retriever(
            search_kwargs={"k": len(fragmentos)}
        )

        def recuperar(pregunta):
            registrar_evento(
                "indice_disponible",
                **informacion,
            )
            return recuperador.invoke(pregunta)

        yield (
            recuperar,
            RunnableLambda(responder_simulado),
            informacion,
        )


@contextmanager
def abrir_componentes_reales(k=3):
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k debe ser un entero positivo.")

    if not (RUTA_INDICE / "chroma.sqlite3").is_file():
        raise FileNotFoundError(
            "Falta el índice real. Ejecuta la indexación primero."
        )

    with chromadb.PersistentClient(
        path=str(RUTA_INDICE),
        settings=Settings(anonymized_telemetry=False),
    ) as cliente:
        embeddings, indice, modelo, configuracion = (
            construir_componentes(cliente_chroma=cliente)
        )

        informacion = {
            "coleccion": configuracion["coleccion"],
            "fragmentos": len(fragmentar_corpus()),
            "dimensiones": configuracion["dimensiones"],
            "modelo_embeddings": configuracion["modelo_embeddings"],
            "modelo_generacion": configuracion["modelo_generacion"],
            "estado_indice": "reutilizado",
            "k": k,
        }

        def recuperar(pregunta):
            registrar_evento(
                "indice_disponible",
                **informacion,
            )
            vector = embeddings.embed_query(pregunta)
            return indice.similarity_search_by_vector(
                vector,
                k=k,
            )

        yield recuperar, modelo, informacion