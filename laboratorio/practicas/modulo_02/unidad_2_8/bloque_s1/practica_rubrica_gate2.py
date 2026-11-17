PESOS = {
    "pipeline_funcional": 0.25,
    "recuperacion_citacion": 0.15,
    "costo_latencia": 0.10,
    "personalizacion": 0.15,
    "observabilidad": 0.15,
    "seguridad_gobernanza": 0.20,
}


def evaluar_gate(puntajes, controles, umbral=80):
    promedio = sum(
        puntajes[dimension] * peso
        for dimension, peso in PESOS.items()
    )

    pendientes = [
        nombre
        for nombre, cumple in controles.items()
        if cumple is not True
    ]

    aprueba = promedio >= umbral and not pendientes
    return promedio, pendientes, aprueba


if __name__ == "__main__":
    print("Valores didácticos: no son la nota del laboratorio.")
    print("Suma de pesos:", sum(PESOS.values()))

    puntajes = {
        "pipeline_funcional": 95,
        "recuperacion_citacion": 90,
        "costo_latencia": 85,
        "personalizacion": 88,
        "observabilidad": 92,
        "seguridad_gobernanza": 80,
    }

    controles_ok = {
        "pipeline_completo": True,
        "respuestas_con_fuentes": True,
        "logs_sin_contenido_sensible": True,
        "supervision_funciona": True,
    }

    controles_con_fallo = {
        **controles_ok,
        "logs_sin_contenido_sensible": False,
    }

    puntajes_bajos = {
        nombre: valor - 15
        for nombre, valor in puntajes.items()
    }

    casos = [
        (
            "PROMEDIO ALTO, UN CONTROL FALLA",
            puntajes,
            controles_con_fallo,
        ),
        (
            "PROMEDIO ALTO, CONTROLES OK",
            puntajes,
            controles_ok,
        ),
        (
            "PROMEDIO BAJO, CONTROLES OK",
            puntajes_bajos,
            controles_ok,
        ),
    ]

    for titulo, notas, controles in casos:
        promedio, pendientes, aprueba = evaluar_gate(
            notas, controles
        )

        print(f"\n=== {titulo} ===")
        print(f"Promedio: {promedio:.1f}")
        print("Controles pendientes:", pendientes)
        print("Aprueba:", aprueba)