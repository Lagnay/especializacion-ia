def recomendar_estrategia(respuestas):
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


if __name__ == "__main__":
    # Caso ficticio del curso, no diagnóstico de nuestro proyecto.
    respuestas = {
        "informacion_cambia_seguido": False,
        "problema_de_formato_o_tono": True,
        "dataset_grande_y_de_calidad": True,
        "presupuesto_limitado_o_iterar_rapido": False,
        "necesita_multiples_variantes": False,
    }

    puntos, candidatas = recomendar_estrategia(respuestas)

    print("Puntos:", puntos)
    print("Selección que oculta el empate:", max(puntos, key=puntos.get))
    print("Todas las candidatas:", candidatas)
    print("\n=== CAMBIAR UNA RESPUESTA A LA VEZ ===")

    for clave in respuestas:
        variante = dict(respuestas)
        variante[clave] = not variante[clave]

        puntos_variante, candidatas_variante = recomendar_estrategia(
            variante
        )

        cambio = (
            "CAMBIA"
            if set(candidatas_variante) != set(candidatas)
            else "igual"
        )

        print(
            f"{clave} = {variante[clave]} "
            f"-> {candidatas_variante} [{cambio}]"
        )

    print("\n=== CASO SIN EMPATE ===")

    respuestas_asistente = {
        "informacion_cambia_seguido": True,
        "problema_de_formato_o_tono": True,
        "dataset_grande_y_de_calidad": False,
        "presupuesto_limitado_o_iterar_rapido": True,
        "necesita_multiples_variantes": False,
    }

    puntos_asistente, candidatas_asistente = recomendar_estrategia(
        respuestas_asistente
    )

    print("Puntos:", puntos_asistente)
    print("Candidatas:", candidatas_asistente)