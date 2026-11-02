def normalizar_categoria(texto):
    return texto.strip().lower().removesuffix(".").strip()


if __name__ == "__main__":
    ejemplos = [
        " Queja \n",
        "SUGERENCIA",
        "pregunta.",
        " Queja . \n",
        "No estoy seguro",
        "queja urgente",
        "",
    ]

    for texto in ejemplos:
        resultado = normalizar_categoria(texto)
        print(repr(texto), "->", repr(resultado))