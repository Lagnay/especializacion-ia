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


def calcular_metricas(
    texto_referencia: str,
    texto_respuesta: str,
) -> dict[str, float]:
    """Procesa dos textos y calcula sus métricas de coincidencia."""
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)

    return calcular_precision_cobertura_f1(
        tokens_referencia,
        tokens_respuesta,
    )


def resumir_metricas(resultados: list[dict]) -> dict[str, float]:
    """Calcula el promedio de cada métrica entre los casos recibidos."""
    if not resultados:
        return {
            "precision_promedio": 0.0,
            "cobertura_promedio": 0.0,
            "f1_promedio": 0.0,
        }

    cantidad = len(resultados)

    return {
        "precision_promedio": sum(
            caso["precision"] for caso in resultados
        ) / cantidad,
        "cobertura_promedio": sum(
            caso["cobertura"] for caso in resultados
        ) / cantidad,
        "f1_promedio": sum(
            caso["f1"] for caso in resultados
        ) / cantidad,
    }