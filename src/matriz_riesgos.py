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


MIS_RIESGOS = [
    {
        "id": "R01",
        "riesgo": "Responder con un resumen desactualizado del código.",
        "probabilidad": 3,
        "impacto": 3,
        "justificacion": (
            "El código evoluciona y el corpus se mantiene manualmente. "
            "Una divergencia podría enseñar un comportamiento incorrecto."
        ),
        "mitigacion": (
            "La colección identifica el contenido y la configuración "
            "indexados (Bloque 24), pero no detecta por sí sola cambios "
            "en los archivos mencionados como fuentes."
        ),
        "supervision": (
            "Revisar el resumen contra el código antes de actualizar "
            "el corpus y volver a indexarlo."
        ),
        "pendiente": (
            "La revisión manual debe repetirse cuando cambien las "
            "fuentes o el corpus. No existe una comprobación "
            "automática de equivalencia entre ambos."
        ),
    },
    {
        "id": "R02",
        "riesgo": "Usar un prompt modificado sin revisar sus cambios.",
        "probabilidad": 3,
        "impacto": 3,
        "justificacion": (
            "Actualmente las instrucciones pueden editarse directamente. "
            "Un cambio puede afectar el uso del contexto y las citas "
            "en todas las consultas posteriores."
        ),
        "mitigacion": (
            "Registro de versiones con texto, huella y procedencia "
            "de validación. Grafo con aprobación humana, comprobación "
            "de la huella completa y bloqueo de solicitudes ya "
            "resueltas (Bloque 32)."
        ),
        "supervision": (
            "Revisar el texto y sus diferencias antes de autorizar "
            "la versión propuesta."
        ),
        "pendiente": (
            "La aprobación selecciona una versión en el estado local "
            "de la solicitud. Todavía no controla automáticamente "
            "la instrucción utilizada por el flujo RAG existente."
        ),
    },
    {
        "id": "R03",
        "riesgo": "Obedecer instrucciones incluidas en un documento.",
        "probabilidad": 2,
        "impacto": 3,
        "justificacion": (
            "El corpus actual es controlado, lo que limita la exposición. "
            "Las pruebas muestran que existen instrucciones maliciosas "
            "que no coinciden con los patrones del detector."
        ),
        "mitigacion": (
            "Filtrado de patrones, separación de roles, delimitación "
            "del contexto y omisión de la generación cuando no queda "
            "contexto aceptado (Bloque 31)."
        ),
        "supervision": (
            "Revisar la procedencia y el contenido antes de incorporar "
            "documentos externos al corpus."
        ),
        "pendiente": (
            "Mantener explícito que el filtro no garantiza detectar "
            "todos los ataques."
        ),
    },
    {
        "id": "R04",
        "riesgo": (
            "Guardar datos personales al reutilizar el registro "
            "detallado con consultas reales de clientes."
        ),
        "probabilidad": 2,
        "impacto": 3,
        "justificacion": (
            "Los ejemplos actuales son ficticios. El riesgo aparecería "
            "si se reutilizara el registro del Bloque 28 con datos "
            "personales, porque conserva pregunta, prompt y respuesta."
        ),
        "mitigacion": (
            "El flujo instrumentado registra longitudes, huellas y "
            "metadatos seleccionados en lugar del contenido completo "
            "(Bloque 31). Esto no modifica los registros del Bloque 28."
        ),
        "supervision": (
            "Revisar los campos registrados y los archivos antes de "
            "usar datos personales o compartir nuevas evidencias."
        ),
        "pendiente": (
            "Conservar el uso de datos ficticios en las prácticas "
            "que guardan contenido completo."
        ),
    },
    {
        "id": "R05",
        "riesgo": "Interrumpir una evaluación al superar la cuota.",
        "probabilidad": 4,
        "impacto": 2,
        "justificacion": (
            "Ocurrió en el Bloque 30: la cuota interrumpió el caso C16. "
            "El impacto fue una demora; se conservaron las primeras "
            "quince respuestas y luego se completaron las cinco restantes."
        ),
        "mitigacion": (
            "Guardado por caso, registro del error y reanudación sin "
            "repetir respuestas completadas (Bloque 30)."
        ),
        "supervision": (
            "Revisar el error y los casos pendientes antes de reanudar "
            "el lote, sin borrar las respuestas guardadas."
        ),
        "pendiente": (
            "No interpretar el límite observado como una cuota "
            "universal para todos los modelos y planes."
        ),
    },
]


if __name__ == "__main__":
    print("Estimaciones cualitativas del laboratorio.")
    print("No representan frecuencias medidas ni riesgos eliminados.")

    ordenados = sorted(
        MIS_RIESGOS,
        key=lambda riesgo: puntaje_riesgo(
            riesgo["probabilidad"], riesgo["impacto"]
        ),
        reverse=True,
    )

    for riesgo in ordenados:
        probabilidad = riesgo["probabilidad"]
        impacto = riesgo["impacto"]
        puntaje = puntaje_riesgo(probabilidad, impacto)
        categoria = categoria_riesgo(puntaje)
        limite = esta_en_el_limite(probabilidad, impacto)

        print(
            f"\n{riesgo['id']} | P={probabilidad} | I={impacto} "
            f"| puntaje={puntaje} | {categoria} | al límite={limite}"
        )
        print("Riesgo:", riesgo["riesgo"])
        print("Justificación:", riesgo["justificacion"])
        print("Control existente:", riesgo["mitigacion"])
        print("Supervisión:", riesgo["supervision"])
        print("Pendiente o condición:", riesgo["pendiente"])