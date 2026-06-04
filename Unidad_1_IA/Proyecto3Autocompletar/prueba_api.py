import requests

url = "http://127.0.0.1:5000/api/autocompletar"

datos = {
    "texto": "int funcion_prom",
    "cantidad": 80,
    "temperatura": 0.30
}

respuesta = requests.post(url, json=datos)

if respuesta.status_code == 200:
    resultado = respuesta.json()

    print("\n===== RESPUESTA DE LA API =====\n")
    print("Estado:", resultado["estado"])
    print("Entrada:", resultado["entrada"])
    print("Sugerencia:", resultado["sugerencia"])
    print("\n===== CODIGO COMPLETO =====\n")
    print(resultado["codigo_completo"])
else:
    print("Error:", respuesta.status_code)
    print(respuesta.text)