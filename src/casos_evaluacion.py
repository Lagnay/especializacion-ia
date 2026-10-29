CASOS_ORIGINALES = [
    {
        "id": "C01",
        "tipo": "formato_controlado",
        "consulta": (
            "Escribe exactamente «El cielo es azul.» en minúsculas "
            "y sin signos de puntuación ni comillas."
        ),
        "referencia": "el cielo es azul",
        "aspectos_esperados": [
            "Reproducir el contenido solicitado.",
            "Utilizar minúsculas.",
            "No añadir puntuación, comillas ni explicaciones.",
        ],
    },
    {
        "id": "C02",
        "tipo": "conocimiento_general",
        "consulta": "¿Qué es Python?",
        "referencia": (
            "Python es un lenguaje de programación interpretado."
        ),
        "aspectos_esperados": [
            "Identificar Python como un lenguaje de programación.",
            "Ofrecer una descripción pertinente a la pregunta.",
        ],
    },
    {
        "id": "C03",
        "tipo": "conocimiento_general",
        "consulta": (
            "¿Para qué sirve la fotosíntesis en las plantas?"
        ),
        "referencia": (
            "La fotosíntesis permite a las plantas producir "
            "alimento utilizando la luz."
        ),
        "aspectos_esperados": [
            "Explicar que permite a las plantas producir alimento.",
            "Relacionar el proceso con el aprovechamiento de la luz.",
        ],
    },
]


CASOS_ADICIONALES = [
    {
        "id": "C04",
        "tipo": "extraccion",
        "contexto": (
            "El pedido incluye cuatro paquetes de arroz "
            "y se retira el viernes."
        ),
        "pregunta": (
            "¿Cuántos paquetes incluye el pedido "
            "y qué día se retira?"
        ),
        "referencia": (
            "El pedido incluye cuatro paquetes de arroz "
            "y se retira el viernes."
        ),
        "aspectos_esperados": [
            "Cantidad: cuatro paquetes.",
            "Día de retiro: viernes.",
        ],
    },
    {
        "id": "C05",
        "tipo": "informacion_ausente",
        "contexto": (
            "El pedido incluye cuatro paquetes de arroz "
            "y se retira el viernes."
        ),
        "pregunta": "¿A qué hora se retira el pedido?",
        "referencia": (
            "La información proporcionada no indica "
            "una hora de retiro."
        ),
        "aspectos_esperados": [
            "Reconocer que la hora no está indicada.",
            "No inventar una hora de retiro.",
        ],
    },
    {
        "id": "C06",
        "tipo": "negacion",
        "contexto": (
            "Hay leche y arroz disponibles. "
            "No queda pan."
        ),
        "pregunta": (
            "¿Hay pan disponible y qué otros productos "
            "se pueden comprar?"
        ),
        "referencia": (
            "No queda pan; hay leche y arroz disponibles."
        ),
        "aspectos_esperados": [
            "Pan: no disponible.",
            "Leche: disponible.",
            "Arroz: disponible.",
        ],
    },
    {
        "id": "C07",
        "tipo": "fecha",
        "contexto": (
            "El pedido se recibió el 12 de mayo. "
            "Su retiro se acordó para el 15 de mayo."
        ),
        "pregunta": "¿En qué fecha se retira el pedido?",
        "referencia": "El pedido se retira el 15 de mayo.",
        "aspectos_esperados": [
            "Fecha de retiro: 15 de mayo.",
            "Distinguir la fecha de recepción de la de retiro.",
        ],
    },
    {
        "id": "C08",
        "tipo": "condicion",
        "contexto": (
            "El envío es gratuito para compras de al menos "
            "30000 pesos. Esta compra suma 28000 pesos."
        ),
        "pregunta": (
            "¿Esta compra cumple la condición para obtener "
            "envío gratuito? Explica por qué."
        ),
        "referencia": (
            "No cumple: suma 28000 pesos y el mínimo "
            "para envío gratuito es 30000 pesos."
        ),
        "aspectos_esperados": [
            "Indicar que no cumple la condición.",
            "Explicar que 28000 es menor que 30000.",
        ],
    },
    {
        "id": "C09",
        "tipo": "calculo",
        "contexto": (
            "Se compran tres panes de 1200 pesos cada uno "
            "y se paga con 5000 pesos."
        ),
        "pregunta": "¿Cuál es el total y cuánto vuelto corresponde?",
        "referencia": (
            "El total es 3600 pesos y el vuelto es 1400 pesos."
        ),
        "aspectos_esperados": [
            "Total: 3600 pesos.",
            "Vuelto: 1400 pesos.",
        ],
    },
    {
        "id": "C10",
        "tipo": "parafrasis",
        "contexto": "El automóvil se desplaza a gran velocidad.",
        "pregunta": (
            "Expresa la misma idea con otras palabras, "
            "sin añadir información."
        ),
        "referencia": "El auto es veloz.",
        "aspectos_esperados": [
            "Expresar que el automóvil es rápido.",
            "Reformular conservando el sentido.",
            "No añadir otras características del automóvil.",
        ],
    },
    {
        "id": "C11",
        "tipo": "participantes",
        "contexto": "Laura entregó una caja a Marcos.",
        "pregunta": "¿Quién entregó la caja y quién la recibió?",
        "referencia": (
            "Laura entregó la caja y Marcos la recibió."
        ),
        "aspectos_esperados": [
            "Laura: persona que entrega.",
            "Marcos: persona que recibe.",
        ],
    },
    {
        "id": "C12",
        "tipo": "excepcion",
        "contexto": (
            "La tienda acepta devoluciones dentro de 30 días, "
            "excepto de alimentos, que no se pueden devolver. "
            "El producto es arroz comprado hace 10 días."
        ),
        "pregunta": (
            "Según esta política, ¿se puede devolver el arroz? "
            "Explica por qué."
        ),
        "referencia": (
            "No se puede devolver porque es un alimento, "
            "aunque se compró hace 10 días."
        ),
        "aspectos_esperados": [
            "Indicar que no se puede devolver.",
            "Aplicar la excepción para alimentos.",
        ],
    },
    {
        "id": "C13",
        "tipo": "informacion_ausente",
        "contexto": (
            "La ficha indica que el local abre a las 9:00 "
            "y cierra a las 18:00."
        ),
        "pregunta": "¿Cuál es el teléfono del local?",
        "referencia": (
            "La ficha no proporciona el teléfono del local."
        ),
        "aspectos_esperados": [
            "Reconocer que no se proporciona el teléfono.",
            "No inventar un número de teléfono.",
        ],
    },
    {
        "id": "C14",
        "tipo": "resumen",
        "contexto": (
            "El pedido debía entregarse el lunes, pero llegó "
            "el miércoles, con dos días de retraso. "
            "La clienta tuvo que reorganizar su tarde para recibirlo "
            "y revisó cada artículo al abrir la caja. "
            "El embalaje tenía una esquina doblada, aunque el producto "
            "estaba intacto y funcionaba correctamente. "
            "Encontró el comprobante de despacho dentro de la caja, "
            "pero no la factura. "
            "Por eso solicitó que le enviaran la factura "
            "por correo electrónico. "
            "También comentó que el repartidor fue amable "
            "y que pudo guardar el producto sin dificultades."
        ),
        "pregunta": (
                "Resume el caso en un máximo de 25 palabras; "
                "asegurate de incluir el estado del producto, "
                "el retraso y la solicitud de la clienta."
        ),
        "referencia": (
            "El pedido llegó dos días tarde; el producto estaba "
            "intacto y la clienta pidió la factura por correo electrónico."
        ),
        "aspectos_esperados": [
            "Conservar el retraso de dos días.",
            "Conservar que el producto estaba intacto.",
            "Conservar la solicitud de factura por correo.",
            "Utilizar un máximo de 25 palabras.",
            "Omitir detalles secundarios sin inventar información.",
        ],
    },
    {
        "id": "C15",
        "tipo": "actualizacion",
        "contexto": (
            "La lista inicial de compras contiene pan, leche "
            "y arroz. Después se cancela la leche."
        ),
        "pregunta": "¿Qué productos quedan en la lista?",
        "referencia": "Quedan pan y arroz.",
        "aspectos_esperados": [
            "Incluir pan.",
            "Incluir arroz.",
            "Excluir la leche cancelada.",
        ],
    },
    {
        "id": "C16",
        "tipo": "unidades",
        "contexto": (
            "El pedido contiene dos cajas. "
            "Cada caja contiene seis botellas."
        ),
        "pregunta": "¿Cuántas botellas contiene el pedido en total?",
        "referencia": "El pedido contiene doce botellas.",
        "aspectos_esperados": [
            "Total: doce botellas.",
            "Distinguir botellas de cajas.",
        ],
    },
    {
        "id": "C17",
        "tipo": "comparacion",
        "contexto": (
            "El plan A incluye dos visitas al mes. "
            "El plan B incluye cuatro visitas al mes."
        ),
        "pregunta": (
            "¿Qué plan incluye más visitas y cuántas más "
            "incluye respecto del otro?"
        ),
        "referencia": (
            "El plan B incluye dos visitas mensuales más "
            "que el plan A."
        ),
        "aspectos_esperados": [
            "Identificar el plan B.",
            "Diferencia: dos visitas al mes.",
        ],
    },
    {
        "id": "C18",
        "tipo": "secuencia",
        "contexto": (
            "El procedimiento indica revisar primero la conexión "
            "del cable y después reiniciar el equipo."
        ),
        "pregunta": (
            "Según el procedimiento, ¿qué debe hacerse "
            "antes de reiniciar el equipo?"
        ),
        "referencia": (
            "Antes de reiniciar el equipo debe revisarse "
            "la conexión del cable."
        ),
        "aspectos_esperados": [
            "Identificar la revisión de la conexión del cable.",
            "Mantener el orden indicado.",
        ],
    },
    {
        "id": "C19",
        "tipo": "contexto_contradictorio",
        "contexto": (
            "La ficha A del pedido 42 indica que se retira el lunes. "
            "La ficha B del mismo pedido indica que se retira el martes."
        ),
        "pregunta": "¿Qué día debo retirar el pedido 42?",
        "referencia": (
            "Debe confirmarse el día de retiro: una ficha indica "
            "lunes y la otra martes."
        ),
        "aspectos_esperados": [
            "Reconocer la discrepancia entre lunes y martes.",
            "No presentar uno de los días como confirmado.",
            "Indicar que hace falta aclarar cuál información es válida.",
        ],
    },
    {
        "id": "C20",
        "tipo": "significado_en_contexto",
        "contexto": (
            "En este catálogo ficticio, Luna es una marca de arroz "
            "y Sol es una marca de leche."
        ),
        "pregunta": "¿Qué representa Luna y a qué corresponde?",
        "referencia": "Luna es una marca de arroz.",
        "aspectos_esperados": [
            "Identificar Luna como una marca.",
            "Relacionarla con arroz.",
            "Utilizar el significado establecido en el contexto.",
        ],
    },
]


def preparar_consulta(caso: dict) -> str:
    """Devuelve la consulta original o construye una con contexto."""
    if "consulta" in caso:
        return caso["consulta"]

    return (
        "Responde usando únicamente la información del contexto. "
        "Si falta un dato necesario, indícalo sin inventarlo.\n\n"
        f"Contexto ficticio:\n{caso['contexto']}\n\n"
        f"Pregunta:\n{caso['pregunta']}"
    )


CASOS_EVALUACION = CASOS_ORIGINALES + CASOS_ADICIONALES