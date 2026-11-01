import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Falta configurar GEMINI_API_KEY.")

    plantilla_analisis = PromptTemplate.from_template(
        "Extrae y organiza la información del siguiente reclamo. "
        "Usa únicamente lo indicado en el mensaje.\n\n"
        "Presenta cuatro secciones:\n"
        "1. Hechos informados: lo que relata el cliente, "
        "sin presentarlo como verificado por la empresa.\n"
        "2. Solicitudes: qué pide que haga la empresa.\n"
        "3. Preferencias: solución preferida, disponibilidad "
        "horaria y canal de contacto.\n"
        "4. Estado de verificación: distingue las afirmaciones "
        "del cliente de las comprobaciones de la empresa. "
        "Indica qué confirmaciones de la empresa no constan. "
        "Un relato detallado no demuestra que la empresa "
        "haya verificado los hechos o aprobado una solución.\n\n"
        "Conserva quién realiza o debe realizar cada acción. "
        "Distingue una disponibilidad horaria de una cita confirmada "
        "y una solución solicitada de una solución aprobada. "
        "No propongas causas posibles ni acciones de investigación. "
        "No inventes políticas, compensaciones ni fechas. "
        "No redactes todavía una respuesta para el cliente. "
        "Responde directamente con las cuatro secciones.\n\n"
        "Mensaje del cliente:\n{mensaje}"
    )

    plantilla_planificacion = PromptTemplate.from_template(
        "Prepara un plan interno para atender el reclamo "
        "descrito en el siguiente análisis.\n\n"
        "Organiza tu salida en tres secciones:\n"
        "1. Ficha del caso: conserva el identificador del pedido, "
        "los hechos relevantes, las solicitudes y las preferencias "
        "que necesitará quien redacte la respuesta al cliente.\n"
        "2. Acciones propuestas: indica en orden qué debería "
        "verificar o gestionar soporte para atender el reclamo.\n"
        "3. Límites y pendientes: señala qué requiere verificación "
        "o autorización antes de poder confirmarse al cliente.\n\n"
        "Puedes proponer revisar registros y coordinar gestiones, "
        "pero no afirmes que esas acciones ya se realizaron. "
        "No des por aprobados entregas, reembolsos ni compensaciones. "
        "No inventes políticas, existencias, costos o plazos. "
        "Conserva la diferencia entre disponibilidad del cliente "
        "y entrega confirmada. "
        "No des por adjuntados o recibidos documentos "
        "que el cliente solamente menciona. "
        "Si propones consultar registros o documentos cuya "
        "existencia no consta, indica que se revisen "
        "si están disponibles. "
        "No inventes requisitos de autorización ni responsables. "
        "Cuando se desconozca una política, señala que debe "
        "consultarse la política aplicable, sin definir su contenido. "
        "No redactes todavía el mensaje para el cliente.\n\n"
        "Análisis del reclamo:\n{analisis}"
    )

    plantilla_redaccion = PromptTemplate.from_template(
        "Prepara un borrador breve de respuesta al cliente, "
        "en español y con tono cordial y claro.\n\n"
        "Usa el plan interno para identificar los pasos propuestos, "
        "pero contrasta sus afirmaciones con el mensaje original. "
        "El mensaje original tiene prioridad como fuente sobre "
        "lo que el cliente dijo. El plan no demuestra que la empresa "
        "haya realizado gestiones o aprobado soluciones.\n\n"
        "Reconoce el problema informado y las solicitudes del cliente. "
        "Conserva sus preferencias relevantes. "
        "Explica qué necesita verificarse antes de confirmar "
        "una solución, sin copiar todo el plan interno. "
        "No afirmes que se recibieron documentos, se verificó el pago "
        "o se registró el reclamo si eso no consta. "
        "No conviertas las acciones propuestas en acciones realizadas "
        "ni en compromisos confirmados. "
        "No prometas entregas, reembolsos, envío de factura o plazos. "
        "No inventes políticas ni requisitos de autorización. "
        "Distingue la disponibilidad horaria del cliente "
        "de una entrega confirmada. "
        "Devuelve únicamente el borrador para el cliente.\n\n"
        "Mensaje original:\n{mensaje}\n\n"
        "Plan interno propuesto:\n{plan}"
    )

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        api_key=api_key,
        vertexai=False,
        timeout=30,
        max_retries=0,
    )

    parser = StrOutputParser()

    paso_analisis = plantilla_analisis | modelo | parser
    paso_planificacion = plantilla_planificacion | modelo | parser
    paso_redaccion = plantilla_redaccion | modelo | parser

    datos = {
        "mensaje": (
            "El lunes hice el pedido P-104 con cuatro paquetes "
            "de arroz y dos cartones de leche. La entrega estaba "
            "programada para el martes entre las 16 y las 18, "
            "pero llegó el miércoles a las 11. Recibí los cuatro "
            "paquetes de arroz y solamente un cartón de leche. "
            "Los productos recibidos están en buen estado. "
            "Según mi comprobante, pagué el pedido completo. "
            "Escribí a soporte el miércoles y todavía no recibo "
            "respuesta. Necesito que revisen la leche faltante "
            "y que me envíen la factura por correo. Prefiero "
            "recibir el producto faltante antes que un reembolso. "
            "Puedo recibir entregas entre las 18 y las 20, "
            "pero necesito que me confirmen antes. "
            "Prefiero que me contacten por escrito."
        ),
    }

    cadena = (
        RunnablePassthrough.assign(
            analisis=paso_analisis
        )
        | RunnablePassthrough.assign(
            plan=paso_planificacion
        )
        | paso_redaccion
    )

    borrador = cadena.invoke(datos)

    print("=== BORRADOR PARA REVISIÓN ===")
    print(borrador)