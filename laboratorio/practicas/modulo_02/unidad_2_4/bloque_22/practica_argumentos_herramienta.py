from pydantic import BaseModel, Field, ValidationError


class ArgumentosConsultaPedido(BaseModel):
    pedido_id: str = Field(
        description=(
            "Identificador del pedido ficticio, "
            "por ejemplo P-301."
        ),
    )

    incluir_historial: bool = Field(
        default=False,
        description=(
            "Indica si se necesita el historial de estados "
            "además del estado actual."
        ),
    )


if __name__ == "__main__":
    casos = [
        {"pedido_id": "P-301"},
        {
            "pedido_id": "P-301",
            "incluir_historial": True,
        },
        {
            "pedido_id": "P-301",
            "incluir_historial": "true",
        },
        {
            "pedido_id": "P-301",
            "incluir_historial": "tal vez",
        },
        {},
    ]

    for numero, datos in enumerate(casos, start=1):
        print("\nCaso", numero)

        try:
            argumentos = ArgumentosConsultaPedido.model_validate(
                datos
            )

            print(
                "Datos validados:",
                argumentos.model_dump(),
            )

        except ValidationError as error:
            print(
                "Error controlado:",
                error.errors()[0]["type"],
            )