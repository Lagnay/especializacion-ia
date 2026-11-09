from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)


if __name__ == "__main__":
    texto = (
        "El cliente realiza hasta 3 intentos ante un TimeoutError, "
        "con espera creciente entre intentos.\n\n"
        "Los errores de autenticación no se reintentan: "
        "se comunican como ValueError sin nuevas solicitudes.\n\n"
        "El costo de referencia se acumula en la sesión "
        "mientras el programa continúa en ejecución."
    )

    estrategias = [
        (
            "FIJO",
            CharacterTextSplitter(
                separator="",
                chunk_size=110,
                chunk_overlap=0,
            ),
        ),
        (
            "RECURSIVO",
            RecursiveCharacterTextSplitter(
                chunk_size=110,
                chunk_overlap=0,
            ),
        ),
    ]

    for nombre, divisor in estrategias:
        fragmentos = divisor.split_text(texto)

        print(f"\n=== {nombre} ===")

        for numero, fragmento in enumerate(fragmentos, start=1):
            print(
                f"\nFragmento {numero}: "
                f"{len(fragmento)} caracteres"
            )
            print(fragmento)

        print("\nCantidad de fragmentos:", len(fragmentos))

        texto_continuo = (
        "Si falla la red el cliente registra el error y espera "
        "antes de volver a intentar la solicitud."
    )

    for solapamiento in (0, 12):
        divisor = RecursiveCharacterTextSplitter(
            chunk_size=45,
            chunk_overlap=solapamiento,
        )

        print(f"\n=== SOLAPAMIENTO {solapamiento} ===")

        for numero, fragmento in enumerate(
            divisor.split_text(texto_continuo), start=1
        ):
            print(f"{numero}. {fragmento}")