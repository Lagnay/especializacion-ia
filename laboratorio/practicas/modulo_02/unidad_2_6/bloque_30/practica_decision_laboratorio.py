from src.decision_personalizacion import recomendar_estrategia


# Evaluación del laboratorio revisada el 14 de noviembre de 2026.
# Las respuestas representan esa revisión; deben reconsiderarse
# si cambian los requisitos o aparece evidencia nueva.
RESPUESTAS_LABORATORIO = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": False,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False,
}


if __name__ == "__main__":
    puntos, candidatas = recomendar_estrategia(
        RESPUESTAS_LABORATORIO
    )

    print("=== CASO ACTUAL ===")
    print("Puntos:", puntos)
    print("Candidatas:", candidatas)

    # Escenario hipotético, no resultado observado:
    # una nueva muestra alcanzara el umbral de fallos de formato.
    variante = dict(RESPUESTAS_LABORATORIO)
    variante["problema_de_formato_o_tono"] = True

    puntos_variante, candidatas_variante = recomendar_estrategia(
        variante
    )

    print("\n=== HIPÓTESIS: PROBLEMA DE FORMATO ===")
    print("Puntos:", puntos_variante)
    print("Candidatas:", candidatas_variante)