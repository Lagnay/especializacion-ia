def validar_pregunta(pregunta):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")

    return pregunta


try:
    pregunta_validada = validar_pregunta("¿Cuál es la capital de Escocia?")
    print("Pregunta aceptada:", pregunta_validada)
except ValueError as error:
    print("No se pudo preparar la consulta:", error)

print("El programa llegó al final.")