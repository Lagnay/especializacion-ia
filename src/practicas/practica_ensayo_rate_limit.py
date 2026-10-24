from unittest.mock import patch

import src.cliente as cliente


if __name__ == "__main__":
    limite_consultas = 16
    se_observo_429 = False

    for numero in range(1, limite_consultas + 1):
        print(f"\n=== CONSULTA {numero} ===")

        with patch(
            "src.cliente.clasificar_estado",
            wraps=cliente.clasificar_estado,
        ) as clasificacion_observada:
            try:
                texto = cliente.consultar_modelo(
                    f"Prueba de conexión número {numero}.",
                    system_instruction="Responde únicamente OK.",
                )
                print("Respuesta:", texto)

            except (TypeError, ValueError) as error:
                print("Error de entrada o configuración:", error)
                break

            except RuntimeError as error:
                print("La consulta no se completó:", error)

            estados = []

            for llamada in clasificacion_observada.call_args_list:
                estados.append(llamada.args[0])

            print("Estados HTTP observados:", estados)

        if 429 in estados:
            se_observo_429 = True
            print("Se observó un HTTP 429 real.")
            break

    if not se_observo_429:
        print("\nNo se observó un HTTP 429 en este ensayo.")

    print(
        "\nCosto acumulado de referencia: "
        f"{cliente.costo_total_sesion:.9f} USD"
    )
    print("El ensayo llegó al final.")