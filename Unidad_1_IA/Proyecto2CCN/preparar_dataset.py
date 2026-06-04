from PIL import Image
import os
import shutil

origen = "C:/dataset_animales"
destino = "C:/dataset_animales_35x35"

clases = {
    "Frog": "ranas",
    "Bird": "pajaros",
    "Whale": "ballenas",
    "Monkey": "changos",
    "Spider": "aranas"
}

os.makedirs(destino, exist_ok=True)

for clase_original, clase_nueva in clases.items():
    carpeta_destino = os.path.join(destino, clase_nueva)
    os.makedirs(carpeta_destino, exist_ok=True)

    contador = 0

    for raiz, carpetas, archivos in os.walk(origen):
        if clase_original.lower() in raiz.lower():
            for archivo in archivos:
                if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
                    ruta_img = os.path.join(raiz, archivo)

                    try:
                        img = Image.open(ruta_img).convert("RGB")
                        img = img.resize((35, 35))

                        nombre_nuevo = f"{clase_nueva}_{contador:05d}.jpg"
                        img.save(os.path.join(carpeta_destino, nombre_nuevo))

                        contador += 1
                    except:
                        print("Error con:", ruta_img)

    print(f"{clase_nueva}: {contador} imágenes procesadas")