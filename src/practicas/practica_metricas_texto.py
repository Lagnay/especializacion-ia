from src.pipeline_texto import procesar_texto, vectorizar


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta coincidencias entre palabras, incluidas sus repeticiones."""
    conteo_referencia = vectorizar(tokens_referencia)
    conteo_respuesta = vectorizar(tokens_respuesta)

    interseccion = conteo_referencia & conteo_respuesta

    return sum(interseccion.values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 por coincidencias de palabras."""
    if not tokens_referencia or not tokens_respuesta:
        return {
            "precision": 0.0,
            "cobertura": 0.0,
            "f1": 0.0,
        }

    coincidencias = contar_coincidencias(
        tokens_referencia,
        tokens_respuesta,
    )

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }


if __name__ == "__main__":
    referencia = "El gato duerme en el sofá."
    respuesta = "El gato duerme en el sillón todo el día."

    tokens_referencia = procesar_texto(referencia)
    tokens_respuesta = procesar_texto(respuesta)

    coincidencias = contar_coincidencias(
        tokens_referencia,
        tokens_respuesta,
    )

    print("Tokens de referencia:", tokens_referencia)
    print("Tokens de respuesta:", tokens_respuesta)
    print("Cantidad en la referencia:", len(tokens_referencia))
    print("Cantidad en la respuesta:", len(tokens_respuesta))
    print("Coincidencias:", coincidencias)

    metricas = calcular_precision_cobertura_f1(
        tokens_referencia,
        tokens_respuesta,
    )

    print(f"Precisión: {metricas['precision']:.2f}")
    print(f"Cobertura: {metricas['cobertura']:.2f}")
    print(f"F1: {metricas['f1']:.2f}")

    casos = [
        {
            "nombre": "SINÓNIMOS",
            "referencia": "El auto es veloz.",
            "respuesta": "El coche es rápido.",
        },
        {
            "nombre": "NEGACIÓN",
            "referencia": "El local abre los domingos.",
            "respuesta": "El local no abre los domingos.",
        },
        {
            "nombre": "CAMBIO DE PROTAGONISTAS",
            "referencia": "El perro persiguió al gato.",
            "respuesta": "El gato persiguió al perro.",
        },
    ]

    for caso in casos:
        tokens_referencia = procesar_texto(caso["referencia"])
        tokens_respuesta = procesar_texto(caso["respuesta"])

        metricas = calcular_precision_cobertura_f1(
            tokens_referencia,
            tokens_respuesta,
        )

        print(f"\n=== {caso['nombre']} ===")
        print("Referencia:", caso["referencia"])
        print("Respuesta:", caso["respuesta"])
        print(f"Precisión: {metricas['precision']:.2f}")
        print(f"Cobertura: {metricas['cobertura']:.2f}")
        print(f"F1: {metricas['f1']:.2f}")