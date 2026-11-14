def estimar_costo_de_etiquetar(
    num_ejemplos,
    minutos_por_ejemplo,
    costo_por_hora,
):
    horas = num_ejemplos * minutos_por_ejemplo / 60
    costo = horas * costo_por_hora
    return horas, costo


if __name__ == "__main__":
    print("=== COMPARACIÓN DE TAMAÑOS ===")
    print("Supuesto: 5 minutos por ejemplo y 25 USD por hora.")

    for cantidad in (16, 200):
        horas, costo = estimar_costo_de_etiquetar(
            cantidad,
            minutos_por_ejemplo=5,
            costo_por_hora=25,
        )
        print(
            f"{cantidad} ejemplos: "
            f"{horas:.2f} horas | {costo:.2f} USD"
        )

    print("\n=== ETIQUETADO CON SEGUNDA REVISIÓN ===")
    print("Supuesto: 500 ejemplos y 20 USD por hora.")

    cantidad = 500
    ejemplos_a_revisar = 100  # El 20 % de los 500 ejemplos.

    horas_base, costo_base = estimar_costo_de_etiquetar(
        cantidad,
        minutos_por_ejemplo=4,
        costo_por_hora=20,
    )
    horas_revision, costo_revision = estimar_costo_de_etiquetar(
        ejemplos_a_revisar,
        minutos_por_ejemplo=2,
        costo_por_hora=20,
    )

    total_horas = horas_base + horas_revision
    total_costo = costo_base + costo_revision

    print(f"Base: {horas_base:.2f} horas | {costo_base:.2f} USD")
    print(
        f"Revisión: {horas_revision:.2f} horas | "
        f"{costo_revision:.2f} USD"
    )
    print(f"Total: {total_horas:.2f} horas | {total_costo:.2f} USD")
    print(f"Jornadas de 8 horas: {total_horas / 8:.1f}")