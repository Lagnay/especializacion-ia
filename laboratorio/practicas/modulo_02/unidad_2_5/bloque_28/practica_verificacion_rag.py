import subprocess

from src.corpus_rag import fragmentar_corpus
from src.indexar_corpus import RUTA_INDICE


def verificar_preparacion():
    problemas = []

    fragmentos = fragmentar_corpus()
    textos = [
        fragmento.page_content
        for fragmento in fragmentos
    ]

    if not fragmentos:
        problemas.append("El corpus no produjo fragmentos.")

    if any(not texto.strip() for texto in textos):
        problemas.append("Hay fragmentos vacíos.")

    if len(textos) != len(set(textos)):
        problemas.append("Hay fragmentos con texto duplicado.")

    if any(
        not fragmento.metadata.get("fuente")
        for fragmento in fragmentos
    ):
        problemas.append("Hay fragmentos sin metadata de fuente.")

    if not (RUTA_INDICE / "chroma.sqlite3").is_file():
        problemas.append("No se encontró la base del índice.")

    comprobacion = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "--",
            "vectorstore/chroma.sqlite3",
        ],
        cwd=RUTA_INDICE.parent,
        capture_output=True,
        text=True,
    )

    if comprobacion.returncode == 1:
        problemas.append("Git no está ignorando la base vectorial.")
    elif comprobacion.returncode != 0:
        problemas.append(
            "No se pudo comprobar la exclusión de Git: "
            + comprobacion.stderr.strip()
        )

    return problemas


if __name__ == "__main__":
    problemas = verificar_preparacion()

    if problemas:
        print("Preparación con problemas:")
        for problema in problemas:
            print("-", problema)
        raise SystemExit(1)

    print(
        "Preparación local OK: corpus, fuentes, "
        "base presente y exclusión de Git."
    )