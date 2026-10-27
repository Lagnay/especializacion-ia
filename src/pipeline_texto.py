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