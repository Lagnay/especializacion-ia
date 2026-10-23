import time


intentos_realizados = 0


def operacion_simulada():
    global intentos_realizados

    intentos_realizados += 1
    print(f"Ejecutando intento {intentos_realizados}")

    if intentos_realizados == 1:
        raise TimeoutError("Fallo temporal simulado.")

    return "Respuesta simulada recibida correctamente."


if __name__ == "__main__":
    try:
        resultado = operacion_simulada()

    except TimeoutError as error:
        print("Error detectado:", error)
        print("Esperando 2 segundos antes de reintentar...")
        time.sleep(2)

        resultado = operacion_simulada()

    print("Resultado:", resultado)
    print("El programa llegó al final.")