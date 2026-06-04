import os
import random
import shutil

origen = "C:/dataset_animales_35x35"
destino = "C:/dataset_balanceado_35x35"
limite = 500

os.makedirs(destino, exist_ok=True)

for clase in os.listdir(origen):
    carpeta_origen = os.path.join(origen, clase)
    carpeta_destino = os.path.join(destino, clase)

    os.makedirs(carpeta_destino, exist_ok=True)

    imagenes = [
        img for img in os.listdir(carpeta_origen)
        if img.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    seleccionadas = random.sample(imagenes, min(limite, len(imagenes)))

    for img in seleccionadas:
        shutil.copy(
            os.path.join(carpeta_origen, img),
            os.path.join(carpeta_destino, img)
        )

    print(clase, len(seleccionadas))