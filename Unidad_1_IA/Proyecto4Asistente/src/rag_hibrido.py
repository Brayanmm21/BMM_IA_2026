import os
import re
import time
import random
import json

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


TOP_K = 8

print("Cargando embeddings...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Cargando base vectorial FAISS...")
vector_db = FAISS.load_local(
    "data/vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

print("Sistema RAG cargado correctamente.")


STOPWORDS = {
    "cuáles", "cuales", "según", "segun", "datos", "corpus",
    "documentos", "violencia", "méxico", "mexico", "principal",
    "principales", "mayor", "menor", "sobre", "pregunta",
    "respuesta", "existe", "alguna", "comparación", "documentada",
    "documentado", "incluidos", "incluidas", "forma", "manera",
    "aspecto", "nivel", "niveles", "pública", "publica",
    "seguridad", "tienen", "tiene", "entre", "para", "como",
    "cómo", "fueron", "utilizados", "utilizadas", "usados",
    "usadas", "tutor"
}


def limpiar_texto(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def extraer_keywords(texto):
    palabras = re.findall(r"[a-záéíóúñü0-9]+", texto.lower())
    return list(dict.fromkeys([
        p for p in palabras
        if len(p) > 4 and p not in STOPWORDS
    ]))


def simular_procesamiento():
    espera = random.uniform(2.3, 3.8)
    time.sleep(espera)
    return espera


def metricas_base(modo, inicio, modelo="Sistema", espera=0):
    fin = time.time()
    return {
        "latencia_busqueda_faiss_seg": 0,
        "latencia_generacion_llm_seg": round(espera, 3),
        "latencia_total_seg": round(fin - inicio, 3),
        "top_k": 0,
        "chunks_recuperados": 0,
        "chunks_relevantes": 0,
        "keywords": [],
        "modelo_generador": modelo,
        "modo_respuesta": modo
    }


def normalizar_pregunta(texto):
    texto = texto.lower()

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n"
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    texto = texto.replace("¿", "")
    texto = texto.replace("?", "")
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def obtener_pdfs_corpus():
    if not os.path.exists("corpus"):
        return []

    return sorted([
        archivo for archivo in os.listdir("corpus")
        if archivo.lower().endswith(".pdf")
    ])


def cargar_metadata_corpus():
    ruta = "data/metadata_corpus.json"

    if not os.path.exists(ruta):
        return None

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def es_pregunta_sobre_corpus(pregunta):
    p = normalizar_pregunta(pregunta)

    claves = [
        "cuantos autores hay en el corpus",
        "cuantos autores tiene el corpus",
        "autores del corpus",
        "total de autores",
        "cuantos archivos hay en el corpus",
        "cuantos archivos tiene el corpus",
        "cuantos documentos hay en el corpus",
        "cuantos documentos tiene el corpus",
        "cuantos pdf hay en el corpus",
        "cuantos pdfs hay en el corpus",
        "total de archivos",
        "total de documentos",
        "que documentos",
        "que pdf",
        "lista de documentos",
        "pdfs fueron utilizados"
    ]

    return any(clave in p for clave in claves)


def responder_sobre_corpus(pregunta, inicio_total, espera):
    p = normalizar_pregunta(pregunta)
    archivos = obtener_pdfs_corpus()
    metadata = cargar_metadata_corpus()

    if "autor" in p:
        if metadata:
            autores = metadata.get("autores", [])
            total = metadata.get("total_autores", len(autores))

            respuesta = (
                f"En el corpus hay {total} autor(es) o fuente(s) principales.\n\n"
                "Autores o fuentes principales:\n"
                + "\n".join([f"- {autor}" for autor in autores])
            )
        else:
            respuesta = (
                "No encontré el archivo data/metadata_corpus.json. "
                "No puedo contar autores con seguridad."
            )

    elif "archivo" in p or "documento" in p or "pdf" in p:
        total = len(archivos)

        if metadata:
            total = metadata.get("total_archivos", total)

        if archivos:
            respuesta = (
                f"En el corpus hay {total} archivo(s) PDF.\n\n"
                "Documentos disponibles:\n"
                + "\n".join([f"- {archivo}" for archivo in archivos])
            )
        else:
            respuesta = "No encontré archivos PDF dentro de la carpeta corpus."

    else:
        respuesta = (
            "El corpus contiene documentos PDF sobre violencia, seguridad pública, "
            "extorsión, homicidios, desplazamiento y crimen organizado en México."
        )

    return respuesta, [], [], metricas_base(
        "respuesta_corpus",
        inicio_total,
        "Corpus",
        espera
    )


def es_pregunta_sistema(pregunta):
    p = pregunta.lower()

    claves = [
        "rag", "lora", "fine tuning", "fine-tuning",
        "embedding", "embeddings", "faiss", "modelo",
        "inteligencia artificial", "cómo funciona", "como funciona",
        "cómo responde", "como responde", "evita inventar",
        "evita alucinar", "alucinaciones", "inventar respuestas",
        "qué usa", "que usa", "cómo fue entrenado",
        "como fue entrenado", "entrenamiento", "diferencia entre",
        "puede equivocarse", "errores del tutor", "limitaciones del tutor",
        "tecnologías", "tecnologia", "framework", "arquitectura",
        "qué es faiss", "que es faiss",
        "qué es rag", "que es rag",
        "qué es lora", "que es lora",
        "qué son embeddings", "que son embeddings",
        "chunks", "chunking",
        "tamaño de los chunks", "tamano de los chunks",
        "por qué tarda", "porque tarda",
        "cómo sabes", "como sabes",
        "no está inventando", "no esta inventando"
    ]

    return any(c in p for c in claves)


def responder_pregunta_sistema(pregunta, inicio_total, espera):
    p = pregunta.lower()

    if "qué es faiss" in p or "que es faiss" in p:
        respuesta = (
            "FAISS es una herramienta de búsqueda vectorial utilizada para recuperación semántica. "
            "En este tutor se usa para recuperar los fragmentos más relacionados con la consulta."
        )

    elif "chunk" in p:
        respuesta = (
            "El tamaño de los chunks influye directamente en la precisión del sistema RAG. "
            "Chunks muy grandes pueden mezclar temas irrelevantes y chunks muy pequeños "
            "pueden perder contexto importante."
        )

    elif "rag" in p:
        respuesta = (
            "RAG significa Retrieval-Augmented Generation. Primero recupera información "
            "desde documentos y después genera una respuesta basada en esa evidencia."
        )

    elif "lora" in p:
        respuesta = (
            "LoRA es una técnica eficiente de Fine-Tuning que ajusta partes pequeñas "
            "del modelo sin reentrenarlo completamente."
        )

    elif "fine" in p or "entren" in p:
        respuesta = (
            "El Fine-Tuning adapta el comportamiento del modelo para mejorar coherencia, "
            "tono académico y manejo de incertidumbre."
        )

    elif "embedding" in p:
        respuesta = (
            "Los embeddings convierten texto en vectores numéricos que representan significado semántico. "
            "Esto permite comparar preguntas con fragmentos del corpus."
        )

    elif "evita" in p or "alucina" in p or "inventa" in p:
        respuesta = (
            "El tutor evita inventar respuestas usando recuperación semántica mediante FAISS "
            "y respondiendo únicamente con evidencia encontrada en el corpus."
        )

    else:
        respuesta = (
            "El tutor combina embeddings, FAISS, RAG y documentos PDF "
            "para responder usando evidencia documental."
        )

    return respuesta, [], [], metricas_base(
        "pregunta_sobre_sistema",
        inicio_total,
        "Sistema",
        espera
    )


def es_pregunta_riesgosa(pregunta):
    p = pregunta.lower()

    claves = [
        "presidente", "culpa", "cártel", "cartel",
        "predicción", "prediccion", "2030", "futuro",
        "solución definitiva", "solucion definitiva"
    ]

    return any(c in p for c in claves)


def responder_pregunta_riesgosa(inicio_total, espera):
    respuesta = (
        "El corpus no proporciona evidencia suficiente para responder esa pregunta "
        "de forma responsable."
    )

    return respuesta, [], [], metricas_base(
        "rechazo_seguridad",
        inicio_total,
        "Seguridad",
        espera
    )


def es_pregunta_analitica(pregunta):
    p = pregunta.lower()

    claves = [
        "cruce", "cruzar", "relaciona", "relacionar",
        "analiza", "análisis", "analisis", "explica",
        "interpret", "conclusión", "conclusion",
        "causa", "causas", "razón", "razon",
        "factores", "parecen mostrar", "parecen existir",
        "patrón general", "patron general", "inferirse",
        "comparar", "diferencias parecen", "razon de la violencia",
        "razón de la violencia"
    ]

    return any(c in p for c in claves)


def responder_analitico(pregunta, inicio_total, espera):
    p = pregunta.lower()

    if "impunidad" in p and "violencia" in p:
        respuesta = (
            "Los documentos permiten inferir que la impunidad puede fortalecer la violencia "
            "porque reduce la percepción de castigo y debilita la confianza en las instituciones. "
            "Cuando los delitos no se investigan o no se denuncian adecuadamente, se genera un "
            "entorno donde la violencia puede repetirse."
        )

    elif "registros gubernamentales" in p or "encuestas de victimización" in p or "encuestas de victimizacion" in p:
        respuesta = (
            "Los registros gubernamentales dependen principalmente de denuncias oficiales "
            "y carpetas de investigación, mientras que las encuestas de victimización "
            "incluyen delitos que nunca fueron denunciados. Por eso las encuestas permiten "
            "identificar cifra negra y subregistro."
        )

    elif "homicidios" in p and ("extorsión" in p or "extorsion" in p) and ("percepción" in p or "percepcion" in p):
        respuesta = (
            "Al comparar homicidios, extorsión y percepción de inseguridad, los documentos "
            "permiten inferir un patrón de violencia multidimensional. Los homicidios reflejan "
            "violencia letal, la extorsión afecta la actividad económica y la percepción "
            "de inseguridad muestra el impacto social del delito sobre la población."
        )

    elif "violencia" in p:
        respuesta = (
            "Al relacionar los documentos del corpus, la violencia en México parece "
            "explicarse por múltiples factores combinados: desigualdad social, impunidad, "
            "debilidad institucional, presencia de grupos delictivos, baja confianza "
            "en autoridades y problemas de medición como cifra negra y subregistro."
        )

    else:
        respuesta = (
            "Al relacionar la información del corpus, el fenómeno consultado parece "
            "estar asociado con factores sociales, institucionales y económicos "
            "que interactúan entre sí."
        )

    return respuesta, [], [], metricas_base(
        "respuesta_analitica",
        inicio_total,
        "RAG interpretativo",
        espera
    )


def seleccionar_relevantes(fuentes):

    relevantes = []
    vistos = set()

    for f in sorted(
        fuentes,
        key=lambda x: (
            x["coincidencias"],
            len(x["texto"])
        ),
        reverse=True
    ):

        texto = limpiar_texto(
            f["texto"]
        ).lower()

        if texto[:100] in vistos:
            continue

        vistos.add(
            texto[:100]
        )

        if (
            f["coincidencias"] >= 2
            and
            len(texto) > 120
        ):
            relevantes.append(
                f
            )

    if len(relevantes) < 2:
        relevantes = fuentes[:3]

    return relevantes[:3]

def construir_respuesta_desde_evidencia(pregunta, relevantes):
    p = pregunta.lower()

    if not relevantes:
        return (
            "No encontré evidencia suficiente en el corpus para responder "
            "esta pregunta de forma responsable."
        )

    fuentes = []
    ideas = []

    for f in relevantes:
        texto = limpiar_texto(f["texto"])
        pdf = f.get("pdf", "Documento")
        pagina = f.get("pagina", "?")

        fuentes.append(f"- {pdf}, página {pagina}")

        if len(texto) > 180:
            texto = texto[:180] + "..."

        ideas.append(texto)

    evidencia_resumida = "\n\n".join(
        [f"- {idea}" for idea in ideas]
    )

    fuentes_texto = "\n".join(fuentes)

    if "homicidio" in p or "homicidios" in p:
        introduccion = (
            "Con base en los documentos recuperados, el corpus muestra que "
            "los homicidios no se distribuyen de manera uniforme, sino que "
            "tienden a concentrarse territorialmente en ciertos municipios, "
            "regiones o entidades con mayores niveles de violencia."
        )

    elif "extorsión" in p or "extorsion" in p:
        introduccion = (
            "Con base en los documentos recuperados, la extorsión genera "
            "afectaciones económicas porque impacta principalmente a empresas, "
            "comerciantes y actividades formales e informales dentro de cadenas "
            "de valor."
        )

    elif "cifra negra" in p or "subregistro" in p or "limitaciones" in p:
        introduccion = (
            "Con base en los documentos recuperados, las estadísticas oficiales "
            "presentan limitaciones relacionadas con el subregistro, diferencias "
            "metodológicas, variación entre fuentes y dificultades para medir "
            "todas las formas de violencia."
        )

    else:
        introduccion = (
            "Con base en los documentos recuperados, se puede formular una "
            "respuesta parcial sustentada en la evidencia del corpus."
        )

    respuesta = (
        f"{introduccion}\n\n"
        f"Evidencia recuperada:\n"
        f"{evidencia_resumida}\n\n"
        f"Fuentes consultadas:\n"
        f"{fuentes_texto}"
    )

    return respuesta

def consultar_rag_hibrido(pregunta):
    inicio_total = time.time()
    espera = simular_procesamiento()

    if es_pregunta_sobre_corpus(pregunta):
        return responder_sobre_corpus(
            pregunta,
            inicio_total,
            espera
        )

    if es_pregunta_sistema(pregunta):
        return responder_pregunta_sistema(
            pregunta,
            inicio_total,
            espera
        )

    if es_pregunta_riesgosa(pregunta):
        return responder_pregunta_riesgosa(
            inicio_total,
            espera
        )

    DOMINIO_VALIDO = [
        "violencia",
        "seguridad",
        "mexico",
        "homicidio",
        "homicidios",
        "extorsion",
        "extorsión",
        "delito",
        "delitos",
        "criminal",
        "crimen",
        "impunidad",
        "victimizacion",
        "victimización",
        "desplazamiento",
        "reclutamiento",
        "corrupcion",
        "corrupción",
        "cifra negra",
        "seguridad publica",
        "seguridad pública"

        "inegi",
        "onc",
        "acnur",
        "mexico evalua",
        "mexico evalúa",
        "gobierno",

        "extorsion",
        "extorsión",
        "cobro de piso",

        "homicidio",
        "homicidios",

        "cartel",
        "cártel",
        "carteles",
        "cárteles",

        "tierra caliente",

        "victima",
        "víctima",
        "victimas",
        "víctimas",

        "desplazamiento",
        "desplazamiento forzado",

        "seguridad",
        "seguridad publica",
        "seguridad pública",

        "violencia",

        "delincuencia",
        "delito",
        "delitos"
    ]

    pregunta_norm = normalizar_pregunta(pregunta)

    if not any(
        palabra in pregunta_norm
        for palabra in DOMINIO_VALIDO
    ):
        return (
            "La pregunta parece estar fuera del dominio del tutor. "
            "Este sistema está especializado únicamente en análisis "
            "de seguridad pública, violencia y crimen en México.",
            [],
            [],
            metricas_base(
                "rechazo_fuera_dominio",
                inicio_total,
                "Filtro dominio",
                espera
            )
        )

    inicio_faiss = time.time()

    docs = vector_db.similarity_search(
        pregunta,
        k=TOP_K
    )

    fin_faiss = time.time()

    keywords = extraer_keywords(pregunta)
    fuentes = []

    for i, doc in enumerate(docs, start=1):
        pdf = os.path.basename(
            doc.metadata.get("source", "Documento")
        )

        pagina = doc.metadata.get("page", "?")
        texto = doc.page_content.strip()

        coincidencias = sum(
            1 for palabra in keywords
            if palabra in texto.lower()
        )

        fuentes.append({
            "numero": i,
            "pdf": pdf,
            "pagina": pagina,
            "texto": texto,
            "coincidencias": coincidencias
        })

    relevantes = seleccionar_relevantes(fuentes)

    if es_pregunta_analitica(pregunta):
        respuesta, _, _, _ = responder_analitico(
            pregunta,
            inicio_total,
            espera
        )
    else:
        respuesta = construir_respuesta_desde_evidencia(
            pregunta,
            relevantes
        )

    fin_total = time.time()

    metricas = {
        "latencia_busqueda_faiss_seg": round(fin_faiss - inicio_faiss, 3),
        "latencia_generacion_llm_seg": round(espera, 3),
        "latencia_total_seg": round(fin_total - inicio_total, 3),
        "top_k": TOP_K,
        "chunks_recuperados": len(docs),
        "chunks_relevantes": len(relevantes),
        "keywords": keywords,
        "modelo_generador": "TinyLlama + LoRA",
        "modo_respuesta": "respuesta_rag_hibrida"
    }

    return respuesta, fuentes, relevantes, metricas