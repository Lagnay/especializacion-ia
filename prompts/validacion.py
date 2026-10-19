def validar_salida(datos, prompt):
    if not isinstance(datos, dict):
        raise ValueError("La salida debe ser un diccionario.")

    tipos_permitidos = {
        "string": (str,),
        "integer": (int,),
        "number": (int, float),
    }

    esquema = prompt["response_schema"]

    for campo in esquema["required"]:
        if campo not in datos:
            raise ValueError(f"Falta el campo obligatorio: {campo}.")

        valor = datos[campo]
        reglas = esquema["properties"][campo]
        tipo = reglas["type"]

        if tipo not in tipos_permitidos:
            raise ValueError(f"Tipo no implementado en el validador: {tipo}.")

        if type(valor) not in tipos_permitidos[tipo]:
            raise ValueError(
                f"El campo '{campo}' debe ser de tipo '{tipo}'."
            )

        if tipo == "string" and not valor.strip():
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")

        if "enum" in reglas and valor not in reglas["enum"]:
            raise ValueError(f"Valor no permitido en '{campo}'.")

        if "minimum" in reglas and not valor >= reglas["minimum"]:
            raise ValueError(f"'{campo}' está por debajo del mínimo.")

        if "maximum" in reglas and not valor <= reglas["maximum"]:
            raise ValueError(f"'{campo}' supera el máximo.")

    for campo, maximo in prompt.get("limites_palabras", {}).items():
        cantidad = len(datos[campo].split())

        if cantidad > maximo:
            raise ValueError(
                f"'{campo}' tiene {cantidad} palabras; "
                f"el máximo es {maximo}."
            )

    return datos