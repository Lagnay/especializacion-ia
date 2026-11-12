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


if __name__ == "__main__":
    pregunta = (
        "¿Cuántos intentos permite el cliente "
        "y cómo espera entre ellos?"
    )

    # Estos dos fragmentos contienen las partes de la respuesta.
    ids_relevantes = {"fragmento-001", "fragmento-002"}

    # Orden simulado para estudiar las métricas.
    # Cada identificador aparece una sola vez.
    ranking = [
        "fragmento-004",
        "fragmento-001",
        "fragmento-006",
        "fragmento-002",
        "fragmento-005",
    ]

    print("Pregunta:", pregunta)

    for k in range(1, 6):
        recuperados = ranking[:k]

        precision = calcular_precision(recuperados, ids_relevantes)
        recall = calcular_recall(recuperados, ids_relevantes)
        f1 = calcular_f1(precision, recall)

        print(
            f"k={k}: "
            f"precision={precision:.3f} "
            f"recall={recall:.3f} "
            f"F1={f1:.3f}"
        )