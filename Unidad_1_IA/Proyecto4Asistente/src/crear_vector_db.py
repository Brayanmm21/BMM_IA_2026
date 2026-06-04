import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

CARPETA_CORPUS = "corpus"
SALIDA_DB = "data/vector_db"

os.makedirs("data", exist_ok=True)

print("Cargando PDFs...")

loader = PyPDFDirectoryLoader(CARPETA_CORPUS)
docs = loader.load()

print(f"Documentos cargados: {len(docs)}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=250,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_documents(docs)

print(f"Chunks generados: {len(chunks)}")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

vector_db = FAISS.from_documents(
    chunks,
    embeddings
)

vector_db.save_local(SALIDA_DB)

print(f"Base vectorial creada correctamente en {SALIDA_DB}")
