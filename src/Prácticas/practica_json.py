import json

respuesta_json = '{"texto": "Hola, soy una respuesta generada", "detalles": {"modelo": "nombre-del-modelo", "tokens": 12}}'
respuesta = json.loads(respuesta_json)

print(respuesta["texto"])
print(respuesta["detalles"]["modelo"])