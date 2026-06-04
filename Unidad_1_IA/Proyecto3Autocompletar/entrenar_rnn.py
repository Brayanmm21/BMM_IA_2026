import os
import json
import numpy as np
import tensorflow as tf

tf.keras.utils.set_random_seed(42)

# ==============================
# CARGAR DATASET
# ==============================

with open("dataset.c", "r", encoding="utf-8") as archivo:
    corpus = archivo.read()

caracteres = sorted(set(corpus))

char_a_numero = {caracter: indice for indice, caracter in enumerate(caracteres)}
numero_a_char = {indice: caracter for caracter, indice in char_a_numero.items()}

vocabulario = len(caracteres)

print("Caracteres únicos:", vocabulario)
print("Total de caracteres:", len(corpus))

# ==============================
# CODIFICAR TEXTO
# ==============================

secuencia_completa = np.array(
    [char_a_numero[caracter] for caracter in corpus],
    dtype=np.int64
)

tamano_bloque = 64

entradas = []
salidas = []

for i in range(0, len(secuencia_completa) - tamano_bloque):
    entradas.append(secuencia_completa[i:i + tamano_bloque])
    salidas.append(secuencia_completa[i + 1:i + tamano_bloque + 1])

X = np.array(entradas)
Y = np.array(salidas)

print("X:", X.shape)
print("Y:", Y.shape)

# ==============================
# CREAR MODELO RNN VANILLA
# ==============================

modelo = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(tamano_bloque,)),
    tf.keras.layers.Embedding(vocabulario, 64),
    tf.keras.layers.SimpleRNN(
        128,
        activation="tanh",
        return_sequences=True
    ),
    tf.keras.layers.TimeDistributed(
        tf.keras.layers.Dense(vocabulario)
    )
])

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
)

modelo.summary()

# ==============================
# ENTRENAR
# ==============================

print("\nEntrenando modelo RNN...")

modelo.fit(
    X,
    Y,
    epochs=100,
    batch_size=32,
    verbose=1
)

# ==============================
# GUARDAR MODELO Y VOCABULARIO
# ==============================

os.makedirs("modelo", exist_ok=True)

modelo.save("modelo/asistente_codigo.keras")

datos_vocabulario = {
    "tamano_bloque": tamano_bloque,
    "caracteres": caracteres
}

with open("modelo/vocabulario.json", "w", encoding="utf-8") as archivo:
    json.dump(datos_vocabulario, archivo, ensure_ascii=False, indent=4)

print("\nModelo entrenado y guardado correctamente.")