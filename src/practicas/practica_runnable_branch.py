from langchain_core.runnables import RunnableBranch


def atender_queja(datos):
    return "Ruta QUEJA: " + datos["mensaje"]


def atender_sugerencia(datos):
    return "Ruta SUGERENCIA: " + datos["mensaje"]


def atender_pregunta(datos):
    return "Ruta PREGUNTA: " + datos["mensaje"]


def atender_desconocida(datos):
    return "Ruta DESCONOCIDA: " + datos["mensaje"]


if __name__ == "__main__":
    bifurcacion = RunnableBranch(
        (
            lambda datos: datos["categoria"] == "queja",
            atender_queja,
        ),
        (
            lambda datos: datos["categoria"] == "sugerencia",
            atender_sugerencia,
        ),
        (
            lambda datos: datos["categoria"] == "pregunta",
            atender_pregunta,
        ),
        atender_desconocida,
    )

    casos = [
        {
            "categoria": "queja",
            "mensaje": "Faltó un cartón de leche.",
        },
        {
            "categoria": "sugerencia",
            "mensaje": "Me gustaría elegir el horario de entrega.",
        },
        {
            "categoria": "pregunta",
            "mensaje": "¿Cómo solicito mi factura?",
        },
        {
            "categoria": "desconocida",
            "mensaje": "Hola.",
        },
    ]

    for caso in casos:
        print("Categoría:", caso["categoria"])
        print(bifurcacion.invoke(caso))
        print()