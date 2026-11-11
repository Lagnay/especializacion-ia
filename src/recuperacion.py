import argparse
import os
import re

from httpx import TransportError
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.cliente import consultar_modelo
from src.corpus_rag import fragmentar_corpus
from src.indexar_corpus import (
    DIMENSIONES,
    MODELO_EMBEDDINGS,
    RUTA_INDICE,
    nombre_coleccion,
)


def recuperar_fragmentos(pregunta, k=3):
    if not pregunta.strip():
        raise ValueError("Escribe una pregunta con contenido.")
    if k < 1:
        raise ValueError("k debe ser al menos 1.")

    if not (RUTA_INDICE / "chroma.sqlite3").is_file():
        raise FileNotFoundError(
            "Crea el índice con python -m src.indexar_corpus --ejecutar."
        )

    load_dotenv(RUTA_INDICE.parent / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY en el entorno o en .env.")

    modelo = GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDINGS,
        output_dimensionality=DIMENSIONES,
        api_key=api_key,
        vertexai=False,
    )

    fragmentos = fragmentar_corpus()
    try:
        indice = Chroma(
            collection_name=nombre_coleccion(fragmentos),
            persist_directory=str(RUTA_INDICE),
            embedding_function=modelo,
            create_collection_if_not_exists=False,
            client_settings=Settings(anonymized_telemetry=False),
        )
    except NotFoundError as error:
        raise FileNotFoundError(
            "La colección del corpus actual aún no está indexada."
        ) from error

    if len(indice.get(include=[])["ids"]) != len(fragmentos):
        raise ValueError("El índice está incompleto. Ejecuta la indexación de nuevo.")

    recuperador = indice.as_retriever(search_kwargs={"k": k})
    try:
        return recuperador.invoke(pregunta)
    except Exception as error:
        if isinstance(error, TransportError) or isinstance(
            error.__cause__, TransportError
        ):
            raise ConnectionError(
                "Se interrumpió la conexión al generar el embedding. "
                "Repite la consulta."
            ) from error
        raise


def formatear_contexto(documentos):
    bloques = []
    citas = {}

    for numero, documento in enumerate(documentos, start=1):
        bloques.append(f"[{numero}] {documento.page_content}")
        citas[numero] = documento.metadata["fuente"]

    return "\n\n".join(bloques), citas


def construir_prompt(pregunta, k=3):
    documentos = recuperar_fragmentos(pregunta, k=k)
    contexto, citas = formatear_contexto(documentos)

    prompt = (
        "Responde usando únicamente los fragmentos del contexto. "
        "Cita cada afirmación con el número del fragmento, como [1]. "
        "Si el contexto no alcanza, di que no tienes información suficiente.\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Pregunta: {pregunta}\n\n"
        "Respuesta:"
    )
    return prompt, citas


def resolver_citas(respuesta, citas):
    grupos = re.findall(
        r"\[\s*([0-9]+(?:\s*,\s*[0-9]+)*)\s*\]",
        respuesta,
    )
    fuentes = {}

    for grupo in grupos:
        for referencia in grupo.split(","):
            numero = int(referencia)
            fuentes[numero] = citas.get(numero)

    return fuentes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recupera contexto para una pregunta.")
    parser.add_argument("pregunta")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--responder", action="store_true")
    args = parser.parse_args()

    try:
        prompt, citas = construir_prompt(args.pregunta, k=args.k)
    except (FileNotFoundError, ConnectionError, ValueError) as error:
        parser.exit(1, f"{error}\n")

    print(prompt)
    print("\nCitas:", citas)

    if args.responder:
        try:
            respuesta = consultar_modelo(prompt)
        except (ValueError, RuntimeError) as error:
            parser.exit(1, f"{error}\n")

        print("\n=== Respuesta de Gemini ===")
        print(respuesta)

        fuentes = resolver_citas(respuesta, citas)
        if fuentes:
            print("\n=== Fuentes citadas ===")
            for numero, fuente in fuentes.items():
                print(f"[{numero}] {fuente or 'Cita fuera del contexto'}")
        else:
            print("\nLa respuesta no incluye citas.")