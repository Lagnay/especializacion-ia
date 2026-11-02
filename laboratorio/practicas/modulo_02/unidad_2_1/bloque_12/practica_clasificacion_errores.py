def clasificar_estado(codigo):
    if codigo in (401, 403):
        raise ValueError(
            "Revisa la credencial o los permisos."
        )

    if codigo == 429:
        raise TimeoutError(
            "Límite de uso: revisar la cuota y la espera."
        )

    if codigo in (500, 502, 503, 504):
        raise TimeoutError(
            "Fallo del proveedor: podría ser temporal."
        )

    if 200 <= codigo < 300:
        return "Estado de éxito: continuar con la respuesta."

    raise RuntimeError(
        f"HTTP {codigo}: revisar la causa antes de reintentar."
    )


if __name__ == "__main__":
    for codigo in (200, 201, 401, 403, 429, 500, 502, 503, 504, 400, 404):
        print(f"\nProbando HTTP {codigo}")

        try:
            resultado = clasificar_estado(codigo)
            print(resultado)

        except ValueError as error:
            print("Sin reintento automático:", error)

        except TimeoutError as error:
            print("Candidato a reintento:", error)

        except RuntimeError as error:
            print("Requiere revisión:", error)