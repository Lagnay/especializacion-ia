PREGUNTAS = (
    "informacion_cambia_seguido",
    "problema_de_formato_o_tono",
    "dataset_grande_y_de_calidad",
    "presupuesto_limitado_o_iterar_rapido",
    "necesita_multiples_variantes",
)


def recomendar_estrategia(respuestas: dict[str, bool]):
    if not isinstance(respuestas, dict):
        raise TypeError("Las respuestas deben ser un diccionario.")

    if set(respuestas) != set(PREGUNTAS):
        raise ValueError(
            "Debes responder exactamente las cinco preguntas del método."
        )

    for clave, valor in respuestas.items():
        if not isinstance(valor, bool):
            raise TypeError(
                f"La respuesta de {clave} debe ser True o False."
            )

    puntos = {
        "RAG": 0,
        "Fine-tuning completo": 0,
        "PEFT": 0,
    }

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3

    if respuestas["problema_de_formato_o_tono"]:
        puntos["Fine-tuning completo"] += 1
        puntos["PEFT"] += 2

    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1

    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1

    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    maximo = max(puntos.values())
    candidatas = [
        tecnica
        for tecnica, puntaje in puntos.items()
        if puntaje == maximo
    ]

    return puntos, candidatas