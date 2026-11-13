from src.corpus_rag import fragmentar_corpus
from src.recuperacion import formatear_contexto


# Tarifas ficticias en USD por mil tokens.
TARIFA_ENTRADA = 0.0001
TARIFA_SALIDA = 0.0004


def aproximar_tokens(texto):
    """Aproximación didáctica: cuatro caracteres por token."""
    return len(texto) // 4


def calcular_costo(
    tokens_entrada,
    tokens_salida,
    tarifa_entrada,
    tarifa_salida,
):
    """Estima USD utilizando tarifas por mil tokens."""
    costo_entrada = (tokens_entrada / 1000) * tarifa_entrada
    costo_salida = (tokens_salida / 1000) * tarifa_salida
    return costo_entrada + costo_salida


if __name__ == "__main__":
    pregunta = "¿Qué hace el cliente si se agotan los tiempos de espera?"

    fragmentos = fragmentar_corpus()[:3]
    contexto, _ = formatear_contexto(fragmentos)

    prompt = (
        "Responde usando únicamente los fragmentos del contexto. "
        "Cita cada afirmación con el número del fragmento, como [1]. "
        "Si el contexto no alcanza, di que no tienes información suficiente.\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Pregunta: {pregunta}\n\n"
        "Respuesta:"
    )

    tokens_pregunta = aproximar_tokens(pregunta)
    tokens_prompt = aproximar_tokens(prompt)

    # Mantenemos la misma salida para aislar el efecto de la entrada.
    tokens_salida_estimados = 60

    costo_pregunta = calcular_costo(
        tokens_pregunta,
        tokens_salida_estimados,
        TARIFA_ENTRADA,
        TARIFA_SALIDA,
    )
    costo_prompt = calcular_costo(
        tokens_prompt,
        tokens_salida_estimados,
        TARIFA_ENTRADA,
        TARIFA_SALIDA,
    )

    print("Pregunta sola:")
    print("Caracteres:", len(pregunta))
    print("Tokens aproximados:", tokens_pregunta)
    print(
        f"Costo estimado con salida fija: "
        f"{costo_pregunta:.8f} USD"
    )

    print("\nPrompt con tres fragmentos:")
    print("Caracteres:", len(prompt))
    print("Tokens aproximados:", tokens_prompt)
    print(
        f"Costo estimado con salida fija: "
        f"{costo_prompt:.8f} USD"
    )

    print(
        f"\nAumento de caracteres: "
        f"{len(prompt) / len(pregunta):.2f}x"
    )
    print(
        f"Aumento del costo estimado: "
        f"{costo_prompt / costo_pregunta:.2f}x"
    )