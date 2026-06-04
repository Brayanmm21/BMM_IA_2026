import json
import random
import os

os.makedirs("data", exist_ok=True)

SALIDA_GRANDE = "data/finetuning_dataset_50000.jsonl"
SALIDA_ENTRENAR = "data/finetuning_dataset_train_2000.jsonl"

TOTAL_GRANDE = 50000
TOTAL_ENTRENAR = 2000

temas = [
    "homicidios en México",
    "extorsión",
    "desplazamiento forzado",
    "violencia urbana",
    "violencia rural",
    "zonas metropolitanas",
    "víctimas",
    "subregistro",
    "cifra negra",
    "seguridad pública",
    "militarización",
    "prevención social",
    "delitos de alto impacto",
    "ENVIPE",
    "ENSU",
    "INEGI",
    "Observatorio Nacional Ciudadano",
    "fuentes gubernamentales",
    "violencia contra mujeres",
    "limitaciones del corpus",
    "RAG",
    "LoRA",
    "Fine-Tuning",
    "FAISS",
    "embeddings",
    "corpus documental"
]

plantillas = [
    "¿Qué dice el corpus sobre {tema}?",
    "Explica de forma académica el tema de {tema}.",
    "¿Qué evidencia documental existe sobre {tema}?",
    "Resume los hallazgos relacionados con {tema}.",
    "¿Qué limitaciones existen para analizar {tema}?",
    "¿Cómo debe responder el tutor sobre {tema}?",
    "¿Qué debe hacer el tutor si la evidencia sobre {tema} es parcial?",
    "¿Qué debe hacer el tutor si no hay evidencia suficiente sobre {tema}?",
    "Analiza {tema} usando únicamente el corpus.",
    "¿Cómo evitaría el tutor inventar información sobre {tema}?"
]

respuestas = [
    "El tutor debe responder únicamente con la evidencia recuperada del corpus. Si la información es parcial, debe indicarlo claramente.",
    "La respuesta debe mantener tono académico, neutral y objetivo, sin inventar cifras, entidades, causas ni conclusiones.",
    "Si el corpus contiene evidencia relacionada, el tutor debe formular una respuesta breve, clara y limitada a los fragmentos recuperados.",
    "Cuando la información no sea suficiente, el tutor debe explicar que la respuesta es parcial y que se requieren más documentos.",
    "El tutor debe evitar conocimiento externo y basarse en documentos recuperados mediante RAG.",
    "El sistema debe distinguir entre evidencia directa, evidencia parcial y ausencia de evidencia.",
    "La respuesta debe ser clara, respetuosa, académica y sin exagerar lo que permite el corpus.",
    "Si la pregunta es sobre el funcionamiento del sistema, el tutor debe explicar RAG, FAISS, embeddings y LoRA.",
    "Si la pregunta es sobre documentos del corpus, el tutor debe revisar la carpeta corpus y responder con los archivos disponibles.",
    "Si la pregunta es ambigua, el tutor debe responder con la información más relacionada y aclarar los límites."
]

preguntas_sistema = [
    ("¿Cómo evita el tutor inventar respuestas?",
     "El tutor evita inventar usando RAG: primero recupera fragmentos reales del corpus con FAISS y después formula la respuesta con base en esa evidencia. Si la información es insuficiente, lo indica en lugar de inventar."),
    ("¿Qué es RAG?",
     "RAG significa Retrieval-Augmented Generation. Es una técnica que recupera información documental antes de generar una respuesta."),
    ("¿Qué es LoRA?",
     "LoRA es una técnica de Fine-Tuning eficiente que ajusta el comportamiento del modelo sin reentrenar todos sus parámetros."),
    ("¿Qué modelo utiliza el tutor?",
     "El tutor utiliza un modelo base ajustado mediante LoRA y una base vectorial FAISS para recuperar información del corpus."),
    ("¿Por qué puede equivocarse el tutor?",
     "Puede equivocarse si el corpus no contiene información suficiente, si la búsqueda recupera fragmentos poco relacionados o si la pregunta requiere información externa."),
    ("¿Qué pasa si el corpus no tiene información?",
     "El tutor debe indicar que no hay evidencia suficiente y evitar inventar datos."),
    ("¿Qué PDFs fueron utilizados por el tutor?",
     "El tutor debe responder revisando directamente los documentos disponibles en la carpeta corpus."),
    ("¿Qué presidente tuvo mejores resultados contra la violencia?",
     "El corpus no proporciona una comparación explícita y suficiente entre presidentes. No es correcto afirmar un resultado sin evidencia documental directa."),
    ("¿Cuál es la causa concreta de la violencia en México?",
     "La violencia en México debe tratarse como un fenómeno multicausal. Si el corpus no señala una causa única, el tutor debe evitar presentar una sola causa como definitiva."),
    ("¿Cómo ha evolucionado la violencia?",
     "El tutor debe responder con base en los indicadores recuperados del corpus y aclarar si la evidencia solo permite una respuesta parcial.")
]

ejemplos = []

for p, r in preguntas_sistema:
    ejemplos.append({
        "instruction": p,
        "input": "",
        "output": r
    })

while len(ejemplos) < TOTAL_GRANDE:
    tema = random.choice(temas)
    pregunta = random.choice(plantillas).format(tema=tema)
    respuesta = random.choice(respuestas)

    ejemplos.append({
        "instruction": pregunta,
        "input": "",
        "output": respuesta
    })

random.shuffle(ejemplos)

with open(SALIDA_GRANDE, "w", encoding="utf-8") as f:
    for e in ejemplos:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

with open(SALIDA_ENTRENAR, "w", encoding="utf-8") as f:
    for e in ejemplos[:TOTAL_ENTRENAR]:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print("Dataset grande creado:", SALIDA_GRANDE)
print("Dataset para entrenar creado:", SALIDA_ENTRENAR)
print("Total grande:", TOTAL_GRANDE)
print("Total entrenamiento:", TOTAL_ENTRENAR)
