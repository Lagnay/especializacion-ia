CASOS_RECUPERACION = [
    {
        "id": "R01",
        "pregunta": "¿Cuántos intentos permite el cliente REST por consulta?",
        "ids_relevantes": {"fragmento-001"},
    },
    {
        "id": "R02",
        "pregunta": "¿Qué tipos de fallos pueden activar un reintento?",
        "ids_relevantes": {"fragmento-001"},
    },
    {
        "id": "R03",
        "pregunta": (
            "¿Desde cuánto comienza la espera entre intentos, "
            "cómo varía y cuál es su máximo?"
        ),
        "ids_relevantes": {"fragmento-002"},
    },
    {
        "id": "R04",
        "pregunta": "¿Qué hace el cliente cuando también falla el último intento?",
        "ids_relevantes": {"fragmento-002"},
    },
    {
        "id": "R05",
        "pregunta": (
            "¿Cómo trata el cliente los estados HTTP 401 y 403 "
            "y los reintenta automáticamente?"
        ),
        "ids_relevantes": {"fragmento-003"},
    },
    {
        "id": "R06",
        "pregunta": (
            "¿Con qué datos se estima el costo de una consulta "
            "y cómo se acumula?"
        ),
        "ids_relevantes": {"fragmento-004"},
    },
    {
        "id": "R07",
        "pregunta": "¿Cómo se separan los historiales de distintas conversaciones?",
        "ids_relevantes": {"fragmento-005"},
    },
    {
        "id": "R08",
        "pregunta": "¿Se conserva la memoria del agente después de cerrar el proceso?",
        "ids_relevantes": {"fragmento-005"},
    },
    {
        "id": "R09",
        "pregunta": "¿Qué condiciones debe cumplir el monto del reembolso simulado?",
        "ids_relevantes": {"fragmento-006"},
    },
    {
        "id": "R10",
        "pregunta": (
            "¿Qué ocurre con el reembolso simulado si se rechaza "
            "la aprobación o se agota el tiempo para responder?"
        ),
        "ids_relevantes": {"fragmento-006"},
    },
    {
        "id": "R11",
        "pregunta": (
            "¿Cuántos intentos permite el cliente "
            "y cómo cambia la espera entre ellos?"
        ),
        "ids_relevantes": {"fragmento-001", "fragmento-002"},
    },
    {
        "id": "R12",
        "pregunta": "¿Cuál es el número de teléfono del soporte de esta tienda?",
        "ids_relevantes": set(),
    },
]


if __name__ == "__main__":
    from src.corpus_rag import fragmentar_corpus

    ids_disponibles = {
        f"fragmento-{numero:03d}"
        for numero, _ in enumerate(fragmentar_corpus(), start=1)
    }

    identificadores = [caso["id"] for caso in CASOS_RECUPERACION]
    if len(identificadores) != len(set(identificadores)):
        raise ValueError("Hay identificadores de casos repetidos.")

    for caso in CASOS_RECUPERACION:
        if not caso["ids_relevantes"].issubset(ids_disponibles):
            raise ValueError(
                f"El caso {caso['id']} referencia fragmentos inexistentes."
            )

    con_respuesta = sum(
        bool(caso["ids_relevantes"])
        for caso in CASOS_RECUPERACION
    )

    print("Casos preparados:", len(CASOS_RECUPERACION))
    print("Con fragmentos relevantes:", con_respuesta)
    print("Sin respuesta en el corpus:", len(CASOS_RECUPERACION) - con_respuesta)
    print("Identificadores y referencias comprobados.")
    print("No se realizaron consultas a Gemini.")