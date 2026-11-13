import time
import argparse
import json
import os

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from src.recuperacion import preparar_prompt


@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()

    try:
        yield
    finally:
        tiempos[etapa] = time.perf_counter() - inicio


def registrar_consulta(pregunta, embeddings, indice, modelo, k=3):
    if not isinstance(pregunta, str):
        raise TypeError("La pregunta debe ser texto.")

    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k debe ser un entero positivo.")

    momento = datetime.now(timezone.utc).isoformat()
    tiempos = {}
    inicio_total = time.perf_counter()

    with medir(tiempos, "embed_query"):
        vector = embeddings.embed_query(pregunta)

    with medir(tiempos, "busqueda_vectorial"):
        documentos = indice.similarity_search_by_vector(
            vector,
            k=k,
        )

    prompt, citas = preparar_prompt(pregunta, documentos)

    with medir(tiempos, "generacion"):
        respuesta = modelo.invoke(prompt)

    total = time.perf_counter() - inicio_total

    tokens = (
        dict(respuesta.usage_metadata)
        if respuesta.usage_metadata
        else None
    )

    return {
        "timestamp": momento,
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {
            etapa: segundos * 1000
            for etapa, segundos in tiempos.items()
        },
        "tiempo_total_ms": total * 1000,
        "suma_etapas_ms": sum(tiempos.values()) * 1000,
        "tokens": tokens,
        "respuesta": str(respuesta.text),
        "prompt": prompt,
        "fuentes_contexto": citas,
        "ids_recuperados": [
            documento.id
            for documento in documentos
        ],
    }


MODELO_GENERACION = "gemini-3.5-flash-lite"
RUTA_REGISTRO = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "modulo_02"
    / "unidad_2_5"
    / "bloque_28"
    / "registros_latencia_costo.jsonl"
)


def construir_componentes():
    from chromadb.config import Settings
    from chromadb.errors import NotFoundError
    from dotenv import load_dotenv
    from langchain_chroma import Chroma
    from langchain_google_genai import (
        ChatGoogleGenerativeAI,
        GoogleGenerativeAIEmbeddings,
    )
    from src.corpus_rag import fragmentar_corpus
    from src.indexar_corpus import (
        DIMENSIONES,
        MODELO_EMBEDDINGS,
        RUTA_INDICE,
        nombre_coleccion,
    )

    if not (RUTA_INDICE / "chroma.sqlite3").is_file():
        raise FileNotFoundError(
            "Falta el índice. Ejecuta la indexación primero."
        )

    load_dotenv(RUTA_INDICE.parent / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY.")

    fragmentos = fragmentar_corpus()
    coleccion = nombre_coleccion(fragmentos)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDINGS,
        output_dimensionality=DIMENSIONES,
        api_key=api_key,
        vertexai=False,
    )

    try:
        indice = Chroma(
            collection_name=coleccion,
            persist_directory=str(RUTA_INDICE),
            embedding_function=None,
            create_collection_if_not_exists=False,
            client_settings=Settings(anonymized_telemetry=False),
        )
    except NotFoundError as error:
        raise FileNotFoundError(
            "La colección del corpus actual no está indexada."
        ) from error

    esperados = {
        f"fragmento-{numero:03d}"
        for numero in range(1, len(fragmentos) + 1)
    }
    guardados = set(indice.get(include=[])["ids"])

    if guardados != esperados:
        raise ValueError(
            "Los identificadores del índice no coinciden con el corpus."
        )

    modelo = ChatGoogleGenerativeAI(
        model=MODELO_GENERACION,
        api_key=api_key,
        vertexai=False,
        timeout=30,
        max_retries=1,
    )

    configuracion = {
        "modelo_generacion": MODELO_GENERACION,
        "modelo_embeddings": MODELO_EMBEDDINGS,
        "dimensiones": DIMENSIONES,
        "coleccion": coleccion,
        "chunk_size": 240,
        "chunk_overlap": 35,
        "timeout_generacion_s": 30,
        "intentos_generacion": 1,
    }

    return embeddings, indice, modelo, configuracion


def guardar_registro(registro, ruta):
    linea = json.dumps(
        registro,
        ensure_ascii=False,
        allow_nan=False,
    )
    ruta.parent.mkdir(parents=True, exist_ok=True)

    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(linea + "\n")


def main():
    from src.casos_recuperacion import CASOS_RECUPERACION
    from src.corpus_rag import fragmentar_corpus

    casos = {
        caso["id"]: caso
        for caso in CASOS_RECUPERACION
    }

    parser = argparse.ArgumentParser(
        description="Registra latencia y consumo del flujo RAG."
    )
    parser.add_argument("--ejecutar", action="store_true")
    parser.add_argument("--caso", choices=casos, default="R01")
    parser.add_argument(
        "--k",
        type=int,
        choices=range(1, len(fragmentar_corpus()) + 1),
        default=3,
    )
    args = parser.parse_args()
    caso = casos[args.caso]

    print("Caso:", caso["id"])
    print("Pregunta:", caso["pregunta"])
    print("Fragmentos solicitados:", args.k)
    print("Registro:", RUTA_REGISTRO)

    if not args.ejecutar:
        print(
            "Modo de preparación: no se realizaron consultas "
            "ni se guardó un registro."
        )
        print("Añade --ejecutar para medir una consulta real.")
        return

    try:
        embeddings, indice, modelo, configuracion = construir_componentes()

        registro = registrar_consulta(
            caso["pregunta"],
            embeddings,
            indice,
            modelo,
            k=args.k,
        )
        registro["caso_id"] = caso["id"]
        registro["origen"] = "consulta_real"
        registro["configuracion"] = configuracion

        print(
            json.dumps(
                registro,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
        )
        guardar_registro(registro, RUTA_REGISTRO)

    except Exception as error:
        parser.exit(
            1,
            f"No se completó la ejecución o su guardado: {error}\n",
        )

    print("Registro guardado en:", RUTA_REGISTRO)


if __name__ == "__main__":
    main()