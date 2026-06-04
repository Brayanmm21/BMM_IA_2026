from rag_hibrido import consultar_rag_hibrido


def linea(titulo="", caracter="=", ancho=80):
    if titulo:
        print("\n" + caracter * ancho)
        print(f" {titulo}")
        print(caracter * ancho)
    else:
        print(caracter * ancho)


def mostrar_respuesta(pregunta, respuesta, fuentes, relevantes, metricas):
    fuentes_mostrar = relevantes if relevantes else fuentes

    linea("CONSULTA DEL USUARIO")
    print(pregunta)

    linea("RESPUESTA DEL TUTOR")
    print(respuesta)

    linea("FUENTES DOCUMENTALES RECUPERADAS")

    if not fuentes_mostrar:
        print("No se recuperaron fuentes documentales.")
    else:
        for i, f in enumerate(fuentes_mostrar, start=1):
            print(f"\n[{i}] {f.get('pdf', 'Documento')}")
            print(f"    Página: {f.get('pagina', '?')}")
            print(f"    Coincidencias: {f.get('coincidencias', 0)}")

            texto = f.get("texto", "").replace("\n", " ").strip()
            if len(texto) > 350:
                texto = texto[:350] + "..."

            print(f"    Fragmento: {texto}")

    linea("MÉTRICAS DEL SISTEMA")
    print(f"Modo de respuesta: {metricas.get('modo_respuesta', 'N/A')}")
    print(f"Modelo generador: {metricas.get('modelo_generador', 'N/A')}")
    print(f"Top-K: {metricas.get('top_k', 0)}")
    print(f"Chunks recuperados: {metricas.get('chunks_recuperados', 0)}")
    print(f"Chunks relevantes: {metricas.get('chunks_relevantes', 0)}")
    print(f"Latencia FAISS: {metricas.get('latencia_busqueda_faiss_seg', 0)} s")
    print(f"Latencia generación: {metricas.get('latencia_generacion_llm_seg', 0)} s")
    print(f"Latencia total: {metricas.get('latencia_total_seg', 0)} s")

    keywords = metricas.get("keywords", [])
    if keywords:
        print(f"Palabras clave: {', '.join(keywords)}")

    linea(caracter="-")


print("\n" + "=" * 80)
print(" OBSERVATORIO INTELIGENTE DE SEGURIDAD")
print(" Tutor RAG para análisis de violencia y seguridad pública en México")
print("=" * 80)
print("Escribe una pregunta o escribe 'salir' para terminar.")
print("Ejemplos:")
print("- ¿Cuántos documentos hay en el corpus?")
print("- ¿Qué efectos económicos genera la extorsión?")
print("=" * 80)

while True:
    pregunta = input("\nPregunta: ").strip()

    if pregunta.lower() in ["salir", "exit", "quit"]:
        print("\nCerrando tutor. Hasta luego.")
        break

    if not pregunta:
        print("Escribe una pregunta válida.")
        continue

    try:
        respuesta, fuentes, relevantes, metricas = consultar_rag_hibrido(pregunta)
        mostrar_respuesta(pregunta, respuesta, fuentes, relevantes, metricas)

    except Exception as e:
        print("\nOcurrió un error al procesar la consulta:")
        print(e)