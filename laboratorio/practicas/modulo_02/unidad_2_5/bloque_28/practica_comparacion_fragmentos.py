from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.corpus_rag import CORPUS


if __name__ == "__main__":
    caracteres_originales = sum(
        len(documento.page_content)
        for documento in CORPUS
    )
    print("Caracteres en documentos:", caracteres_originales)

    for tamano in (160, 240):
        divisor = RecursiveCharacterTextSplitter(
            chunk_size=tamano,
            chunk_overlap=35,
        )
        fragmentos = divisor.split_documents(CORPUS)

        caracteres_fragmentados = sum(
            len(fragmento.page_content)
            for fragmento in fragmentos
        )

        print(f"\n=== TAMAÑO: {tamano} ===")
        print("Fragmentos:", len(fragmentos))
        print("Caracteres sumados:", caracteres_fragmentados)

        for numero, fragmento in enumerate(fragmentos, start=1):
            print(
                f"\n{numero}. {fragmento.metadata['tema']} "
                f"({len(fragmento.page_content)} caracteres)"
            )
            print(fragmento.page_content)