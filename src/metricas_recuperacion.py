def calcular_precision(
    ids_recuperados: list[str],
    ids_relevantes: set[str],
) -> float:
    if not ids_recuperados:
        return 0.0

    coincidencias = set(ids_recuperados) & ids_relevantes
    return len(coincidencias) / len(ids_recuperados)


def calcular_recall(
    ids_recuperados: list[str],
    ids_relevantes: set[str],
) -> float | None:
    if not ids_relevantes:
        return None

    coincidencias = set(ids_recuperados) & ids_relevantes
    return len(coincidencias) / len(ids_relevantes)


def calcular_f1(
    precision: float,
    recall: float | None,
) -> float | None:
    if recall is None:
        return None

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def calcular_metricas_recuperacion(
    ids_recuperados: list[str],
    ids_relevantes: set[str],
) -> dict[str, float | None]:
    """Calcula las métricas para una recuperación sin IDs repetidos."""
    if len(ids_recuperados) != len(set(ids_recuperados)):
        raise ValueError("Los identificadores recuperados no deben repetirse.")

    precision = calcular_precision(ids_recuperados, ids_relevantes)
    recall = calcular_recall(ids_recuperados, ids_relevantes)
    f1 = calcular_f1(precision, recall)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }