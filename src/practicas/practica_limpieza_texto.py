import re

from collections import Counter


def limpiar_texto(texto: str) -> str:
    """Normaliza el texto: minúsculas y sin puntuación."""
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def tokenizar(texto_limpio: str) -> list[str]:
    """Separa el texto limpio en tokens por espacios en blanco."""
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Limpia el texto y devuelve sus tokens."""
    texto_limpio = limpiar_texto(texto)
    return tokenizar(texto_limpio)


def vectorizar(tokens: list[str]) -> Counter:
    """Cuenta cuántas veces aparece cada token."""
    return Counter(tokens)


def calcular_coincidencia(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> float:
    """Calcula la proporción de palabras únicas de referencia presentes."""
    referencia_unica = set(tokens_referencia)
    respuesta_unica = set(tokens_respuesta)

    if not referencia_unica:
        return 0.0

    comunes = referencia_unica & respuesta_unica

    return len(comunes) / len(referencia_unica)


if __name__ == "__main__":
    texto_original = "  ¡Hola,   MUNDO!  "
    referencia = "hola mundo"

    texto_limpio = limpiar_texto(texto_original)

    print("Coincidencia original:", texto_original == referencia)
    print("Texto limpio:", texto_limpio)
    print("Coincidencia después:", texto_limpio == referencia)

    tokens = tokenizar(texto_limpio)
    tokens_pipeline = procesar_texto(texto_original)

    print("Tokens:", tokens)
    print("Tokens mediante el pipeline:", tokens_pipeline)

    texto_para_contar = "El gato, el perro y el gato corren."

    tokens_para_contar = procesar_texto(texto_para_contar)
    conteo = vectorizar(tokens_para_contar)

    print("\nTokens para contar:", tokens_para_contar)
    print("Conteo:", conteo)
    print("Apariciones de 'el':", conteo["el"])

    referencia_comparacion = "El cielo es azul."
    respuesta_comparacion = "el cielo es azul"

    coincidencia_cruda = calcular_coincidencia(
        referencia_comparacion.split(),
        respuesta_comparacion.split(),
    )

    coincidencia_procesada = calcular_coincidencia(
        procesar_texto(referencia_comparacion),
        procesar_texto(respuesta_comparacion),
    )

    print(f"\nCoincidencia sin limpieza: {coincidencia_cruda:.0%}")
    print(f"Coincidencia con pipeline: {coincidencia_procesada:.0%}")

    referencia_orden = "El perro persiguió al gato."
    respuesta_orden = "El gato persiguió al perro."

    tokens_ref_orden = procesar_texto(referencia_orden)
    tokens_resp_orden = procesar_texto(respuesta_orden)

    coincidencia_orden = calcular_coincidencia(
        tokens_ref_orden,
        tokens_resp_orden,
    )

    print(f"\nCoincidencia con cambio de orden: {coincidencia_orden:.0%}")
    print(
        "Mismos conteos:",
        vectorizar(tokens_ref_orden) == vectorizar(tokens_resp_orden),
    )

    referencia_repeticion = "El gato."
    respuesta_repeticion = "El gato, el gato."

    tokens_ref_repeticion = procesar_texto(referencia_repeticion)
    tokens_resp_repeticion = procesar_texto(respuesta_repeticion)

    coincidencia_repeticion = calcular_coincidencia(
        tokens_ref_repeticion,
        tokens_resp_repeticion,
    )

    print(
        f"\nCoincidencia con repeticiones: "
        f"{coincidencia_repeticion:.0%}"
    )
    print("Conteo de referencia:", vectorizar(tokens_ref_repeticion))
    print("Conteo de respuesta:", vectorizar(tokens_resp_repeticion))