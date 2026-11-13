import time

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding

from src.corpus_rag import fragmentar_corpus
from .practica_medicion_etapas import medir


if __name__ == "__main__":
    modelo = DeterministicFakeEmbedding(size=16)

    cliente = chromadb.EphemeralClient(
        settings=Settings(anonymized_telemetry=False)
    )

    indice = Chroma(
        client=cliente,
        collection_name="practica_medicion_b28",
        embedding_function=modelo,
    )

    fragmentos = fragmentar_corpus()
    indice.add_documents(
        fragmentos,
        ids=[
            f"prueba-{numero:03d}"
            for numero in range(1, len(fragmentos) + 1)
        ],
    )

    pregunta = "¿Qué hace el cliente si se agotan los tiempos de espera?"
    tiempos = {}

    inicio_total = time.perf_counter()

    with medir(tiempos, "embedding_local"):
        vector = modelo.embed_query(pregunta)

    with medir(tiempos, "busqueda_vectorial"):
        recuperados = indice.similarity_search_by_vector(
            vector,
            k=3,
        )

    total = time.perf_counter() - inicio_total

    print("Pregunta:", pregunta)
    print("Dimensiones de prueba:", len(vector))
    print("Fragmentos recuperados:", len(recuperados))

    for etapa, segundos in tiempos.items():
        print(f"{etapa}: {segundos * 1000:.2f} ms")

    print(
        f"Suma de etapas: "
        f"{sum(tiempos.values()) * 1000:.2f} ms"
    )
    print(
        f"Tiempo total transcurrido: "
        f"{total * 1000:.2f} ms"
    )