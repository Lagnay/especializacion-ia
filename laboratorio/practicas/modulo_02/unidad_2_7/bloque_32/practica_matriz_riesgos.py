def puntaje_riesgo(probabilidad, impacto):
    for valor in (probabilidad, impacto):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError(
                "Probabilidad e impacto deben ser enteros."
            )

        if not 1 <= valor <= 5:
            raise ValueError(
                "Probabilidad e impacto deben estar entre 1 y 5."
            )

    return probabilidad * impacto


def categoria_riesgo(puntaje):
    if isinstance(puntaje, bool) or not isinstance(puntaje, int):
        raise TypeError("El puntaje debe ser un entero.")

    if not 1 <= puntaje <= 25:
        raise ValueError("El puntaje debe estar entre 1 y 25.")

    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"

    return "BAJO"


def esta_en_el_limite(probabilidad, impacto):
    actual = categoria_riesgo(
        puntaje_riesgo(probabilidad, impacto)
    )

    vecinos = [
        (probabilidad + 1, impacto),
        (probabilidad - 1, impacto),
        (probabilidad, impacto + 1),
        (probabilidad, impacto - 1),
    ]

    for p, i in vecinos:
        if not (1 <= p <= 5 and 1 <= i <= 5):
            continue

        if categoria_riesgo(puntaje_riesgo(p, i)) != actual:
            return True

    return False


if __name__ == "__main__":
    print(
        "Valores didácticos: no son la evaluación del laboratorio."
    )

    for p, i in [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]:
        puntaje = puntaje_riesgo(p, i)
        categoria = categoria_riesgo(puntaje)
        limite = esta_en_el_limite(p, i)

        print(
            f"P={p}, I={i} -> {puntaje}, {categoria}, "
            f"al límite: {limite}"
        )