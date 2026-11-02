import time
from concurrent.futures import ThreadPoolExecutor

import requests

import src.cliente as cliente
from src.consumir_gemini import armar_peticion


def enviar_una_vez(numero):
    url, headers, body = armar_peticion(
        f"Prueba de conexión número {numero}.",
        system_instruction="Responde únicamente OK.",
    )

    inicio = time.perf_counter()

    try:
        respuesta = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30,
            allow_redirects=False,
        )
        return numero, respuesta, time.perf_counter() - inicio, None

    except requests.exceptions.RequestException as error:
        return (
            numero,
            None,
            time.perf_counter() - inicio,
            type(error).__name__,
        )


if __name__ == "__main__":
    total_consultas = 20
    consultas_por_lote = 5
    estados = []
    errores_transporte = 0
    inicio_ensayo = time.perf_counter()

    with ThreadPoolExecutor(max_workers=5) as ejecutor:
        for primera in range(1, total_consultas + 1, consultas_por_lote):
            ultima = min(
                primera + consultas_por_lote,
                total_consultas + 1,
            )
            print(f"\n=== LOTE: CONSULTAS {primera} A {ultima - 1} ===")

            resultados = list(
                ejecutor.map(enviar_una_vez, range(primera, ultima))
            )

            for numero, respuesta, duracion, error in resultados:
                if respuesta is None:
                    errores_transporte += 1
                    print(
                        f"Consulta {numero}: {error}; "
                        f"tiempo: {duracion:.3f} s"
                    )
                    continue

                codigo = respuesta.status_code
                estados.append(codigo)
                print(
                    f"Consulta {numero}: HTTP {codigo}; "
                    f"tiempo: {duracion:.3f} s"
                )

                if 200 <= codigo < 300:
                    try:
                        datos = respuesta.json()
                        cliente.registrar_costo(datos)
                        print("Respuesta:", cliente.extraer_texto(datos))

                    except (
                        requests.exceptions.JSONDecodeError,
                        TypeError,
                        ValueError,
                        RuntimeError,
                    ) as error:
                        print(
                            "No se pudo procesar la respuesta:",
                            type(error).__name__,
                        )

                elif codigo == 429:
                    print(
                        "Retry-After:",
                        respuesta.headers.get("Retry-After", "No informado"),
                    )

            if 429 in estados:
                print("HTTP 429 observado; no se iniciarán más lotes.")
                break

    duracion_total = time.perf_counter() - inicio_ensayo

    print("\n=== RESUMEN ===")
    print("Peticiones intentadas:", len(estados) + errores_transporte)
    print("Estados HTTP:", estados)
    print("Respuestas HTTP 429:", estados.count(429))
    print("Errores de transporte:", errores_transporte)
    print(f"Duración total: {duracion_total:.3f} segundos")
    print(
        "Costo acumulado de referencia: "
        f"{cliente.costo_total_sesion:.9f} USD"
    )
    print("El ensayo llegó al final.")