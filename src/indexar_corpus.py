import argparse
import json
import os
from hashlib import sha256
from pathlib import Path

from chromadb.config import Settings
from chromadb.errors import NotFoundError
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.corpus_rag import fragmentar_corpus


RUTA_INDICE = Path(__file__).resolve().parents[1] / "vectorstore"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"
DIMENSIONES = 3072


def nombre_coleccion(fragmentos):
    contenido = {
        "modelo": MODELO_EMBEDDINGS,
        "dimensiones": DIMENSIONES,
        "fragmentos": [
            {"texto": fragmento.page_content, "metadatos": fragmento.metadata}
            for fragmento in fragmentos
        ],
    }
    datos = json.dumps(contenido, sort_keys=True).encode("utf-8")
    huella = sha256(datos).hexdigest()[:16]
    return f"proyecto-{huella}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexa el corpus del proyecto.")
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument("--ejecutar", action="store_true", help="Genera embeddings.")
    modos.add_argument("--verificar", action="store_true", help="Lee el índice.")
    argumentos = parser.parse_args()

    fragmentos = fragmentar_corpus()
    coleccion = nombre_coleccion(fragmentos)
    ids = [f"fragmento-{n:03d}" for n in range(1, len(fragmentos) + 1)]

    print("Colección:", coleccion)
    print("Fragmentos esperados:", len(fragmentos))

    if not argumentos.ejecutar and not argumentos.verificar:
        parser.exit(0, "Modo de preparación: no se llamó a Gemini.\n")

    if argumentos.verificar and not (RUTA_INDICE / "chroma.sqlite3").is_file():
        parser.exit(1, "El índice todavía no existe. Ejecuta primero --ejecutar.\n")

    modelo = None
    if argumentos.ejecutar:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            parser.exit(1, "Falta GEMINI_API_KEY en el entorno o en .env.\n")

        modelo = GoogleGenerativeAIEmbeddings(
            model=MODELO_EMBEDDINGS,
            output_dimensionality=DIMENSIONES,
            api_key=api_key,
            vertexai=False,
        )

    try:
        indice = Chroma(
            collection_name=coleccion,
            persist_directory=str(RUTA_INDICE),
            embedding_function=modelo,
            create_collection_if_not_exists=argumentos.ejecutar,
            client_settings=Settings(anonymized_telemetry=False),
        )
    except NotFoundError:
        parser.exit(1, "La colección de este corpus todavía no está indexada.\n")

    if argumentos.ejecutar:
        existentes = set(indice.get(include=[])["ids"])
        pendientes = [
            (identificador, fragmento)
            for identificador, fragmento in zip(ids, fragmentos, strict=True)
            if identificador not in existentes
        ]

        print("Fragmentos nuevos por indexar:", len(pendientes))

        if pendientes:
            indice.add_documents(
                [fragmento for _, fragmento in pendientes],
                ids=[identificador for identificador, _ in pendientes],
            )

    guardados = indice.get(include=["embeddings"])
    vectores = guardados["embeddings"]

    if set(guardados["ids"]) != set(ids):
        parser.exit(1, "Los fragmentos guardados no coinciden con el corpus.\n")

    if vectores is None or vectores.shape != (len(ids), DIMENSIONES):
        parser.exit(1, "La cantidad o dimensión de los vectores no coincide.\n")

    print("Fragmentos guardados:", len(guardados["ids"]))
    print("Dimensiones por vector:", DIMENSIONES)
    print("Índice:", RUTA_INDICE)