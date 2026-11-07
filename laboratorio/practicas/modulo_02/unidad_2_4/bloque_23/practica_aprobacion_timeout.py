import sys
from time import monotonic, sleep


def esperar_aprobacion(
    mensaje: str,
    tiempo_limite_segundos: float = 5,
) -> bool:
    if tiempo_limite_segundos <= 0:
        raise ValueError("El tiempo límite debe ser positivo.")

    if not sys.stdin.isatty():
        print("Se requiere una terminal interactiva: no aprobado.")
        return False

    if sys.platform != "win32":
        import select
        import termios

        # Descarta entradas anteriores a esta solicitud.
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

        print(mensaje)
        print(
            f"Escribe s o n y pulsa Enter antes de "
            f"{tiempo_limite_segundos} segundos.",
            flush=True,
        )

        limite = monotonic() + tiempo_limite_segundos
        disponibles, _, _ = select.select(
            [sys.stdin], [], [], tiempo_limite_segundos
        )

        if not disponibles or monotonic() >= limite:
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            print("Tiempo agotado: acción no aprobada.")
            return False

        return sys.stdin.readline().strip().lower() == "s"

    import msvcrt

    # Descarta teclas escritas antes de mostrar la solicitud.
    while msvcrt.kbhit():
        msvcrt.getwch()

    print(mensaje)
    print(
        f"Pulsa s o n, sin Enter. "
        f"Dispones de {tiempo_limite_segundos} segundos.",
        flush=True,
    )

    limite = monotonic() + tiempo_limite_segundos

    while monotonic() < limite:
        if msvcrt.kbhit():
            tecla = msvcrt.getwch()

            # Las teclas especiales producen dos códigos.
            if tecla in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue

            if monotonic() >= limite:
                break

            tecla = tecla.lower()

            if tecla in ("s", "n"):
                print("Respuesta:", tecla)
                return tecla == "s"

        sleep(0.05)

    print("Tiempo agotado: acción no aprobada.")
    return False


if __name__ == "__main__":
    aprobado = esperar_aprobacion(
        "SIMULACIÓN: ¿aprobar un reembolso de 1500 pesos "
        "para el pedido P-301?"
    )

    print("Aprobado:", aprobado)
    print("El programa llegó al final.")