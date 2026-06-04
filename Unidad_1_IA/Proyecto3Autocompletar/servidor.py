import json
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify

app = Flask(__name__)

modelo = None
char_a_numero = {}
numero_a_char = {}
tamano_bloque = 64


def cargar_modelo():
    global modelo, char_a_numero, numero_a_char, tamano_bloque

    with open("modelo/vocabulario.json", "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    tamano_bloque = datos["tamano_bloque"]
    caracteres = datos["caracteres"]

    char_a_numero = {caracter: indice for indice, caracter in enumerate(caracteres)}
    numero_a_char = {indice: caracter for caracter, indice in char_a_numero.items()}

    modelo = tf.keras.models.load_model("modelo/asistente_codigo.keras")

    print("Modelo RNN cargado correctamente.")


def generar_sugerencia(texto, cantidad=80, temperatura=0.35):
    ids = []

    for caracter in texto:
        ids.append(char_a_numero.get(caracter, char_a_numero.get(" ", 0)))

    if len(ids) == 0:
        ids = [char_a_numero.get(" ", 0)]

    for _ in range(cantidad):
        entrada = ids[-tamano_bloque:]

        if len(entrada) < tamano_bloque:
            relleno = [char_a_numero.get(" ", 0)] * (tamano_bloque - len(entrada))
            entrada = relleno + entrada

        entrada = np.array([entrada], dtype=np.int32)

        prediccion = modelo.predict(entrada, verbose=0)
        logits = prediccion[0, -1, :]

        logits = logits / temperatura
        logits = logits - np.max(logits)

        probabilidades = np.exp(logits) / np.sum(np.exp(logits))
        siguiente_id = np.random.choice(len(probabilidades), p=probabilidades)

        ids.append(int(siguiente_id))

        caracter_generado = numero_a_char[int(siguiente_id)]

        if caracter_generado in [";", "}", "\n"]:
            break

    texto_completo = "".join(numero_a_char.get(i, "") for i in ids)
    sugerencia = texto_completo[len(texto):]

    return sugerencia


@app.route("/api/autocompletar", methods=["POST"])
def autocompletar():
    datos = request.get_json() or {}

    texto = datos.get("texto", "")
    cantidad = int(datos.get("cantidad", 80))
    temperatura = float(datos.get("temperatura", 0.35))

    if texto.strip() == "":
        return jsonify({
            "estado": "error",
            "mensaje": "Debes enviar el campo texto."
        }), 400

    sugerencia = generar_sugerencia(texto, cantidad, temperatura)

    return jsonify({
        "estado": "ok",
        "entrada": texto,
        "sugerencia": sugerencia,
        "codigo_completo": texto + sugerencia
    })


if __name__ == "__main__":
    cargar_modelo()
    app.run(host="127.0.0.1", port=5000, debug=False)