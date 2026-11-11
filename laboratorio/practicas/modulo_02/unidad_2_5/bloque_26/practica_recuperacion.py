from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding

from src.corpus_rag import fragmentar_corpus


def formatear_contexto(documentos):
    bloques = []
    citas = {}

    for numero, documento in enumerate(documentos, start=1):
        bloques.append(f"[{numero}] {documento.page_content}")
        citas[numero] = documento.metadata["fuente"]

    return "\n\n".join(bloques), citas


if __name__ == "__main__":
    indice = Chroma.from_documents(
        fragmentar_corpus(),
        embedding=DeterministicFakeEmbedding(size=16),
        collection_name="demo-recuperacion-b26",
        client_settings=Settings(anonymized_telemetry=False),
    )

    pregunta = "¿Qué hace el programa cuando la conexión tarda demasiado?"
    print("Pregunta:", pregunta)

    print("\n=== Distancias ===")
    for documento, distancia in indice.similarity_search_with_score(
        pregunta, k=3
    ):
        print(f"{distancia:.4f} | {documento.metadata['tema']}")

    recuperador = indice.as_retriever(search_kwargs={"k": 3})
    documentos = recuperador.invoke(pregunta)
    contexto, citas = formatear_contexto(documentos)

    print("\n=== Contexto numerado ===")
    print(contexto)
    print("\nCitas:", citas)