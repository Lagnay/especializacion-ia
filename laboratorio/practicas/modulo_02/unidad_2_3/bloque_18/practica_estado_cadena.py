from langchain_core.runnables import RunnablePassthrough


if __name__ == "__main__":
    entrada = {
        "mensaje": "Falta un cartón de leche.",
    }

    agregar_analisis = RunnablePassthrough.assign(
        analisis=lambda estado: (
            "Análisis de: " + estado["mensaje"]
        )
    )

    agregar_plan = RunnablePassthrough.assign(
        plan=lambda estado: (
            "Plan basado en: " + estado["analisis"]
        )
    )

    flujo = agregar_analisis | agregar_plan

    estado_final = flujo.invoke(entrada)

    print("Mensaje:", estado_final["mensaje"])
    print("Análisis:", estado_final["analisis"])
    print("Plan:", estado_final["plan"])

    print("Entrada original:", entrada)