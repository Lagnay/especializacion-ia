BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_consulta",
        "system_instruction": (
            "Clasifica el mensaje del usuario. "
            "Responde únicamente con un objeto JSON válido, "
            "sin explicaciones ni bloques de Markdown. "
            "Incluye 'categoria' y 'confianza'. "
            "Las categorías permitidas son: "
            "'soporte_tecnico' para problemas técnicos, "
            "'compras' para consultas de compra y "
            "'otro' para los demás mensajes. "
            "La confianza debe ser un número entre 0 y 1."
        ),
        "ejemplo_usuario": (
            "Necesito restablecer mi contraseña, "
            "pero no recibo el correo de verificación."
        ),
        "response_schema": {
            "type": "object",
            "properties": {
                "categoria": {
                    "type": "string",
                    "enum": [
                        "soporte_tecnico",
                        "compras",
                        "otro",
                    ],
                },
                "confianza": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                },
            },
            "required": ["categoria", "confianza"],
        },
    },
    {
        "nombre": "extraer_pedido",
        "system_instruction": (
            "Extrae el producto y la cantidad solicitada "
            "del mensaje del usuario. "
            "Responde únicamente con un objeto JSON válido, "
            "sin explicaciones ni bloques de Markdown. "
            "Incluye 'producto', como texto, y 'cantidad', "
            "como número entero positivo. "
            "Conserva la unidad de cantidad indicada: "
            "si se piden paquetes, cuenta paquetes, "
            "sin convertirlos a kilos ni a otras unidades."
        ),
        "ejemplo_usuario": "Necesito 4 paquetes de arroz.",
        "response_schema": {
            "type": "object",
            "properties": {
                "producto": {
                    "type": "string",
                },
                "cantidad": {
                    "type": "integer",
                    "minimum": 1,
                },
            },
            "required": ["producto", "cantidad"],
        },
    },
    {
        "nombre": "resumir_mensaje",
        "limites_palabras": {"resumen": 23},
        "system_instruction": (
            "Resume el mensaje del usuario en español "
            "como una nota breve de registro. "
            "Procura usar entre 12 y 18 palabras; "
            "el límite absoluto es de 23 palabras. "
            "Prioriza los problemas y las gestiones solicitadas. "
            "Elimina introducciones, repeticiones y detalles secundarios. "
            "Conserva la intención original sin inventar hechos "
            "ni añadir recomendaciones. "
            "Responde únicamente con un objeto JSON "
            "que contenga la clave 'resumen'. "
            "Ejemplo de entrada: El mensajero no llegó. "
            "Llamé tres veces sin respuesta. "
            "Quiero reprogramar la entrega y recibir confirmación. "
            'Ejemplo de salida: {"resumen": '
            '"Entrega incumplida y llamadas sin respuesta; '
            'solicita reprogramación y confirmación."} '
            "Aplica ese estilo al mensaje del usuario."
        ),
        "ejemplo_usuario": (
            "Mi pedido llegó ayer con dos días de retraso, encima cuando hablé con atención al cliente, "
            "no me ayudaron y luego dejaron de contestar, fue terrible la experiencia. El producto está en buen estado, pero necesito "
            "saber qué puedo hacer para que me cubran el desgaste emocional, además de que me envíen la factura por correo."
        ),
        "response_schema": {
            "type": "object",
            "properties": {
                "resumen": {
                    "type": "string",
                    "description": (
                        "Nota breve de registro, preferiblemente "
                        "de 12 a 18 palabras y nunca más de 23."
                    ),
                },
            },
            "required": ["resumen"],
        },
    },
]