import os
import csv
import json
from datetime import datetime

from rag_hibrido import consultar_rag_hibrido

RUTA_RESULTADOS = "resultados"
RUTA_CSV = "resultados/evaluacion_rag.csv"
RUTA_JSON = "resultados/evaluacion_rag.json"

preguntas = [
    {"id": "Q1", "nivel": "Nivel 1", "pregunta": "¿Cuáles son las tres entidades federativas con mayor índice de homicidios dolosos según los datos más recientes incluidos en el corpus?"},
    {"id": "Q2", "nivel": "Nivel 1", "pregunta": "¿Qué organizaciones, cárteles o grupos delictivos se mencionan con mayor frecuencia operando en la región de Tierra Caliente?"},
    {"id": "Q3", "nivel": "Nivel 1", "pregunta": "¿Cuáles son las cifras oficiales reportadas sobre el desplazamiento forzado interno a causa de la violencia durante el último sexenio documentado?"},
    {"id": "Q4", "nivel": "Nivel 2", "pregunta": "Según los documentos, ¿cuáles son las principales causas socioeconómicas que los autores asocian directamente al incremento de la violencia urbana?"},
    {"id": "Q5", "nivel": "Nivel 2", "pregunta": "Contrasta las estrategias de seguridad pública mencionadas en el corpus. ¿Qué diferencias de enfoque existen entre la militarización y las políticas de prevención social?"},
    {"id": "Q6", "nivel": "Nivel 2", "pregunta": "¿Cómo ha evolucionado la tasa de delitos de extorsión a nivel nacional y qué sectores económicos se reportan como los más afectados?"},
    {"id": "Q7", "nivel": "Nivel 2", "pregunta": "¿Existe alguna diferencia significativa documentada en los tipos de violencia que experimentan las zonas rurales en comparación con las zonas metropolitanas?"},
    {"id": "Q8", "nivel": "Nivel 3", "pregunta": "Con base en las posturas de las ONGs y las fuentes gubernamentales presentes en los textos, ¿cuáles son las principales contradicciones o discrepancias en el registro de víctimas?"},
    {"id": "Q9", "nivel": "Nivel 3", "pregunta": "¿Qué impacto específico tiene la violencia documentada sobre la tasa de deserción escolar en las zonas de alto conflicto?"},
    {"id": "Q10", "nivel": "Nivel 3", "pregunta": "A partir de las conclusiones de los autores en el corpus, ¿qué vacíos de información, subregistros o falta de datos fiables se identifican como el principal obstáculo para medir la violencia real en el país?"}
]

os.makedirs(RUTA_RESULTADOS, exist_ok=True)

resultados = []

print("=" * 80)
print("EVALUACIÓN RAG + LLAMA 3.2")
print("=" * 80)

for item in preguntas:
    print(f"\nEvaluando {item['id']}...")
    print(item["pregunta"])

    respuesta, fuentes, relevantes, metricas = consultar_rag_hibrido(item["pregunta"])

    resultado = {
        "id": item["id"],
        "nivel": item["nivel"],
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pregunta": item["pregunta"],
        "respuesta": respuesta,
        "fuentes_recuperadas": fuentes,
        "fuentes_relevantes": relevantes,
        "metricas": metricas
    }

    resultados.append(resultado)

    print("\nRESPUESTA:")
    print(respuesta)
    print("\nChunks recuperados:", metricas["chunks_recuperados"])
    print("Chunks relevantes:", metricas["chunks_relevantes"])
    print("Latencia total:", metricas["latencia_total_seg"], "segundos")
    print("-" * 80)

with open(RUTA_JSON, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

with open(RUTA_CSV, "w", newline="", encoding="utf-8") as f:
    campos = [
        "id",
        "nivel",
        "fecha_hora",
        "pregunta",
        "respuesta",
        "fuentes_relevantes",
        "latencia_busqueda_faiss_seg",
        "latencia_generacion_llm_seg",
        "latencia_total_seg",
        "top_k",
        "chunks_recuperados",
        "chunks_relevantes",
        "keywords"
    ]

    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()

    for r in resultados:
        writer.writerow({
            "id": r["id"],
            "nivel": r["nivel"],
            "fecha_hora": r["fecha_hora"],
            "pregunta": r["pregunta"],
            "respuesta": r["respuesta"],
            "fuentes_relevantes": json.dumps(r["fuentes_relevantes"], ensure_ascii=False),
            "latencia_busqueda_faiss_seg": r["metricas"]["latencia_busqueda_faiss_seg"],
            "latencia_generacion_llm_seg": r["metricas"]["latencia_generacion_llm_seg"],
            "latencia_total_seg": r["metricas"]["latencia_total_seg"],
            "top_k": r["metricas"]["top_k"],
            "chunks_recuperados": r["metricas"]["chunks_recuperados"],
            "chunks_relevantes": r["metricas"]["chunks_relevantes"],
            "keywords": json.dumps(r["metricas"]["keywords"], ensure_ascii=False)
        })

print("\nEvaluación terminada.")
print("CSV guardado en:", RUTA_CSV)
print("JSON guardado en:", RUTA_JSON)
