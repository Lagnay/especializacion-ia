from collections import Counter


# Mensajes ficticios de evaluación, separados del dataset del bloque 29.
PARES_CLASIFICACION = [
    (
        "¿Pueden corregir el cobro duplicado de mi compra?",
        "queja",
    ),
    (
        "Mi entrega estaba confirmada para ayer y todavía no llega.",
        "queja",
    ),
    (
        "Compré arroz integral, pero recibí arroz blanco.",
        "queja",
    ),
    (
        "El envase de leche llegó abierto y necesito una solución.",
        "queja",
    ),
    (
        "Faltó un producto de mi compra; además sugiero revisar "
        "los pedidos antes de enviarlos.",
        "queja",
    ),
    (
        "Sería útil poder buscar productos por marca.",
        "sugerencia",
    ),
    (
        "Propongo mostrar el precio por kilo junto al precio del envase.",
        "sugerencia",
    ),
    (
        "¿Podrían incorporar una opción para repetir una compra anterior?",
        "sugerencia",
    ),
    (
        "Me gustaría que hubiera una sección de productos de temporada.",
        "sugerencia",
    ),
    (
        "Sugiero añadir fotografías de los ingredientes de cada producto.",
        "sugerencia",
    ),
    (
        "¿Dónde puedo ver el estado de mi compra?",
        "pregunta",
    ),
    (
        "¿Qué medios de pago aceptan?",
        "pregunta",
    ),
    (
        "¿Qué datos necesitan para emitir una factura?",
        "pregunta",
    ),
    (
        "¿En qué horario atienden?",
        "pregunta",
    ),
    (
        "¿Tienen arroz integral disponible?",
        "pregunta",
    ),
    (
        "Gracias, eso era todo.",
        "desconocida",
    ),
    (
        "Hola, buenas tardes.",
        "desconocida",
    ),
    (
        "De acuerdo.",
        "desconocida",
    ),
    (
        "P-582.",
        "desconocida",
    ),
    (
        "Necesito algo.",
        "desconocida",
    ),
]


CASOS_CLASIFICACION = [
    {
        "id": f"C{numero:02d}",
        "mensaje": mensaje,
        "categoria_esperada": categoria,
    }
    for numero, (mensaje, categoria) in enumerate(
        PARES_CLASIFICACION,
        start=1,
    )
]


if __name__ == "__main__":
    balance = Counter(
        caso["categoria_esperada"]
        for caso in CASOS_CLASIFICACION
    )

    print("Casos preparados:", len(CASOS_CLASIFICACION))

    for categoria, cantidad in sorted(balance.items()):
        print(f"{categoria}: {cantidad}")

    print("\nPreparación local, sin consultas.")