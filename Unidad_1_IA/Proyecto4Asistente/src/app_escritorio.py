import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import json
import os
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from rag_hibrido import consultar_rag_hibrido


historial_latencias = []

preguntas_eval = [
    "¿Cuáles son las tres entidades federativas con mayor índice de homicidios dolosos según los datos más recientes incluidos en el corpus?",
    "¿Qué organizaciones, cárteles o grupos delictivos se mencionan con mayor frecuencia operando en la región de Tierra Caliente?",
    "¿Cuáles son las cifras oficiales reportadas sobre el desplazamiento forzado interno a causa de la violencia durante el último sexenio documentado?",
    "Según los documentos, ¿cuáles son las principales causas socioeconómicas que los autores asocian directamente al incremento de la violencia urbana?",
    "Contrasta las estrategias de seguridad pública mencionadas en el corpus. ¿Qué diferencias de enfoque existen entre la militarización y las políticas de prevención social?",
    "¿Cómo ha evolucionado la tasa de delitos de extorsión a nivel nacional y qué sectores económicos se reportan como los más afectados?",
    "¿Existe alguna diferencia significativa documentada en los tipos de violencia que experimentan las zonas rurales en comparación con las zonas metropolitanas?",
    "Con base en las posturas de las ONGs y las fuentes gubernamentales presentes en los textos, ¿cuáles son las principales contradicciones o discrepancias en el registro de víctimas?",
    "¿Qué impacto específico tiene la violencia documentada sobre la tasa de deserción escolar en las zonas de alto conflicto?",
    "A partir de las conclusiones de los autores en el corpus, ¿qué vacíos de información, subregistros o falta de datos fiables se identifican como el principal obstáculo para medir la violencia real en el país?"
]


def guardar_historial(pregunta, respuesta, fuentes, relevantes, metricas):
    os.makedirs("resultados", exist_ok=True)
    ruta = "resultados/historial_consultas.json"

    nueva = {
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pregunta": pregunta,
        "respuesta": respuesta,
        "fuentes_recuperadas": fuentes,
        "fuentes_relevantes": relevantes,
        "metricas": metricas
    }

    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                historial = json.load(f)
        except json.JSONDecodeError:
            historial = []
    else:
        historial = []

    historial.append(nueva)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=4)


def limpiar_cajas():
    respuesta_texto.delete("1.0", tk.END)
    fuentes_texto.delete("1.0", tk.END)
    contexto_texto.delete("1.0", tk.END)
    metricas_texto.delete("1.0", tk.END)


def actualizar_grafica():
    ax.clear()

    if len(historial_latencias) == 0:
        ax.text(0.5, 0.5, "Sin consultas todavía", ha="center", va="center")
    else:
        consultas = [f"Q{i+1}" for i in range(len(historial_latencias))]
        tiempos = [m.get("latencia_total_seg", 0) for m in historial_latencias]

        ax.bar(consultas, tiempos)
        ax.set_title("Latencia total por consulta")
        ax.set_xlabel("Consulta")
        ax.set_ylabel("Segundos")
        ax.grid(axis="y", alpha=0.3)

    canvas_grafica.draw()


def mostrar_resultado(pregunta, respuesta, fuentes_mostrar, metricas, numero):
    respuesta_texto.insert(
        tk.END,
        f"\n{'='*80}\nCONSULTA {numero}\n"
        f"PREGUNTA:\n{pregunta}\n\n"
        f"RESPUESTA DEL TUTOR:\n{respuesta}\n"
    )

    metricas_texto.insert(
        tk.END,
        f"\nConsulta {numero}\n"
        f"Tiempo búsqueda FAISS: {metricas.get('latencia_busqueda_faiss_seg', 0)} s\n"
        f"Tiempo generación LLM: {metricas.get('latencia_generacion_llm_seg', 0)} s\n"
        f"Tiempo total: {metricas.get('latencia_total_seg', 0)} s\n"
        f"Top-K: {metricas.get('top_k', 0)}\n"
        f"Chunks recuperados: {metricas.get('chunks_recuperados', 0)}\n"
        f"Chunks relevantes: {metricas.get('chunks_relevantes', 0)}\n"
        f"Modelo: {metricas.get('modelo_generador', 'N/A')}\n"
        f"Modo: {metricas.get('modo_respuesta', 'N/A')}\n"
        f"Keywords: {', '.join(metricas.get('keywords', []))}\n"
        f"{'-'*45}\n"
    )

    fuentes_texto.insert(tk.END, f"\nPREGUNTA: {pregunta}\n")

    for f in fuentes_mostrar:
        fuentes_texto.insert(
            tk.END,
            f"Fuente {f.get('numero')} | PDF: {f.get('pdf')} | "
            f"Página: {f.get('pagina')} | Coincidencias: {f.get('coincidencias')}\n"
        )

    contexto_texto.insert(
        tk.END,
        f"\n{'='*80}\nPREGUNTA: {pregunta}\n{'='*80}\n"
    )

    for f in fuentes_mostrar:
        contexto_texto.insert(
            tk.END,
            f"\nFUENTE {f.get('numero')} | {f.get('pdf')} | Página {f.get('pagina')}\n"
            f"{'-'*70}\n"
            f"{f.get('texto')}\n"
        )


def ejecutar_lista_preguntas(lista_preguntas):
    if not lista_preguntas:
        messagebox.showwarning("Aviso", "No hay preguntas para ejecutar.")
        return

    limpiar_cajas()
    boton_consultar.config(state=tk.DISABLED)
    boton_multiples.config(state=tk.DISABLED)
    boton_banco.config(state=tk.DISABLED)

    def tarea():
        total = len(lista_preguntas)

        for i, pregunta in enumerate(lista_preguntas, start=1):
            etiqueta_estado.config(text=f"Ejecutando pregunta {i} de {total}...")

            try:
                respuesta, fuentes, relevantes, metricas = consultar_rag_hibrido(pregunta)

                if len(relevantes) > 0:
                    fuentes_mostrar = relevantes
                else:
                    fuentes_mostrar = fuentes

                historial_latencias.append(metricas)
                guardar_historial(pregunta, respuesta, fuentes, relevantes, metricas)

                mostrar_resultado(pregunta, respuesta, fuentes_mostrar, metricas, i)
                actualizar_grafica()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        etiqueta_estado.config(text=f"Proceso terminado. Se ejecutaron {total} preguntas.")

        boton_consultar.config(state=tk.NORMAL)
        boton_multiples.config(state=tk.NORMAL)
        boton_banco.config(state=tk.NORMAL)

    threading.Thread(target=tarea).start()


def ejecutar_una_pregunta():
    pregunta = entrada_pregunta.get("1.0", tk.END).strip()

    if pregunta == "":
        messagebox.showwarning("Aviso", "Escribe una pregunta primero.")
        return

    ejecutar_lista_preguntas([pregunta])


def ejecutar_preguntas_escritas():
    texto = entrada_pregunta.get("1.0", tk.END).strip()

    if texto == "":
        messagebox.showwarning("Aviso", "Escribe varias preguntas, una por línea.")
        return

    preguntas = [linea.strip() for linea in texto.split("\n") if linea.strip()]
    ejecutar_lista_preguntas(preguntas)


def ejecutar_banco():
    ejecutar_lista_preguntas(preguntas_eval)


def cargar_pregunta(pregunta):
    entrada_pregunta.delete("1.0", tk.END)
    entrada_pregunta.insert(tk.END, pregunta)


def limpiar_todo():
    entrada_pregunta.delete("1.0", tk.END)
    limpiar_cajas()
    etiqueta_estado.config(text="Listo para consultar.")


ventana = tk.Tk()
ventana.title("Tutor Analítico Híbrido - RAG + Fine-Tuning")
ventana.geometry("1450x900")
ventana.configure(bg="#0F172A")

COLOR_FONDO = "#0F172A"
COLOR_PANEL = "#1E293B"
COLOR_TEXTO = "#F8FAFC"
COLOR_SUBTEXTO = "#CBD5E1"
COLOR_AZUL = "#2563EB"
COLOR_VERDE = "#16A34A"
COLOR_MORADO = "#7C3AED"
COLOR_GRIS = "#475569"
COLOR_BLANCO = "#FFFFFF"

header = tk.Frame(ventana, bg=COLOR_FONDO)
header.pack(fill="x", padx=25, pady=(18, 10))

tk.Label(
    header,
    text="Tutor Analítico Híbrido",
    font=("Arial", 28, "bold"),
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO
).pack(anchor="w")

tk.Label(
    header,
    text="RAG + Fine-Tuning LoRA | Seguridad pública y violencia en México",
    font=("Arial", 13),
    bg=COLOR_FONDO,
    fg=COLOR_SUBTEXTO
).pack(anchor="w", pady=(4, 0))

panel_superior = tk.Frame(ventana, bg=COLOR_PANEL)
panel_superior.pack(fill="x", padx=25, pady=10)

tk.Label(
    panel_superior,
    text="Pregunta o lista de preguntas",
    font=("Arial", 13, "bold"),
    bg=COLOR_PANEL,
    fg=COLOR_TEXTO
).pack(anchor="w", padx=15, pady=(12, 5))

tk.Label(
    panel_superior,
    text="Puedes escribir una sola pregunta o varias preguntas, una por línea.",
    font=("Arial", 10),
    bg=COLOR_PANEL,
    fg=COLOR_SUBTEXTO
).pack(anchor="w", padx=15)

entrada_pregunta = scrolledtext.ScrolledText(
    panel_superior,
    height=5,
    font=("Arial", 12),
    bg=COLOR_BLANCO,
    fg="#111827",
    relief="flat",
    wrap=tk.WORD
)
entrada_pregunta.pack(fill="x", padx=15, pady=(5, 12))

frame_botones = tk.Frame(panel_superior, bg=COLOR_PANEL)
frame_botones.pack(fill="x", padx=15, pady=(0, 15))

boton_consultar = tk.Button(
    frame_botones,
    text="Ejecutar 1 pregunta",
    font=("Arial", 11, "bold"),
    bg=COLOR_AZUL,
    fg="white",
    relief="flat",
    padx=15,
    pady=8,
    command=ejecutar_una_pregunta
)
boton_consultar.pack(side="left")

boton_multiples = tk.Button(
    frame_botones,
    text="Ejecutar preguntas escritas",
    font=("Arial", 11, "bold"),
    bg=COLOR_VERDE,
    fg="white",
    relief="flat",
    padx=15,
    pady=8,
    command=ejecutar_preguntas_escritas
)
boton_multiples.pack(side="left", padx=8)

boton_banco = tk.Button(
    frame_botones,
    text="Ejecutar banco Q1-Q10",
    font=("Arial", 11, "bold"),
    bg=COLOR_MORADO,
    fg="white",
    relief="flat",
    padx=15,
    pady=8,
    command=ejecutar_banco
)
boton_banco.pack(side="left", padx=8)

tk.Button(
    frame_botones,
    text="Limpiar",
    font=("Arial", 11, "bold"),
    bg=COLOR_GRIS,
    fg="white",
    relief="flat",
    padx=15,
    pady=8,
    command=limpiar_todo
).pack(side="left", padx=8)

etiqueta_estado = tk.Label(
    frame_botones,
    text="Listo para consultar.",
    font=("Arial", 11),
    bg=COLOR_PANEL,
    fg=COLOR_SUBTEXTO
)
etiqueta_estado.pack(side="left", padx=15)

panel_preguntas = tk.Frame(ventana, bg=COLOR_FONDO)
panel_preguntas.pack(fill="x", padx=25, pady=(0, 10))

tk.Label(
    panel_preguntas,
    text="Banco de preguntas de evaluación",
    font=("Arial", 12, "bold"),
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO
).pack(anchor="w")

frame_preguntas = tk.Frame(panel_preguntas, bg=COLOR_FONDO)
frame_preguntas.pack(fill="x", pady=5)

for i, pregunta in enumerate(preguntas_eval, start=1):
    tk.Button(
        frame_preguntas,
        text=f"Q{i}",
        font=("Arial", 10, "bold"),
        bg="#334155",
        fg="white",
        relief="flat",
        padx=10,
        pady=5,
        command=lambda p=pregunta: cargar_pregunta(p)
    ).pack(side="left", padx=3)

contenedor = tk.Frame(ventana, bg=COLOR_FONDO)
contenedor.pack(fill="both", expand=True, padx=25, pady=(0, 20))

panel_izquierdo = tk.Frame(contenedor, bg="#F8FAFC")
panel_izquierdo.pack(side="left", fill="both", expand=True, padx=(0, 8))

panel_centro = tk.Frame(contenedor, bg="#F8FAFC")
panel_centro.pack(side="left", fill="both", expand=True, padx=8)

panel_derecho = tk.Frame(contenedor, bg="#F8FAFC")
panel_derecho.pack(side="right", fill="both", expand=True, padx=(8, 0))

tk.Label(
    panel_izquierdo,
    text="Respuesta académica del tutor",
    font=("Arial", 15, "bold"),
    bg="#F8FAFC",
    fg="#111827"
).pack(anchor="w", padx=15, pady=(15, 5))

respuesta_texto = scrolledtext.ScrolledText(
    panel_izquierdo,
    font=("Arial", 10),
    bg=COLOR_BLANCO,
    fg="#111827",
    relief="flat",
    wrap=tk.WORD
)
respuesta_texto.pack(fill="both", expand=True, padx=15, pady=(0, 15))

tk.Label(
    panel_centro,
    text="Métricas y gráfica",
    font=("Arial", 15, "bold"),
    bg="#F8FAFC",
    fg="#111827"
).pack(anchor="w", padx=15, pady=(15, 5))

metricas_texto = scrolledtext.ScrolledText(
    panel_centro,
    height=8,
    font=("Arial", 10),
    bg=COLOR_BLANCO,
    fg="#111827",
    relief="flat",
    wrap=tk.WORD
)
metricas_texto.pack(fill="x", padx=15, pady=(0, 10))

figura = Figure(figsize=(4, 3), dpi=100)
ax = figura.add_subplot(111)
canvas_grafica = FigureCanvasTkAgg(figura, master=panel_centro)
canvas_grafica.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
actualizar_grafica()

tk.Label(
    panel_derecho,
    text="PDFs, páginas y chunks recuperados",
    font=("Arial", 15, "bold"),
    bg="#F8FAFC",
    fg="#111827"
).pack(anchor="w", padx=15, pady=(15, 5))

fuentes_texto = scrolledtext.ScrolledText(
    panel_derecho,
    height=8,
    font=("Arial", 10),
    bg=COLOR_BLANCO,
    fg="#111827",
    relief="flat",
    wrap=tk.WORD
)
fuentes_texto.pack(fill="x", padx=15, pady=(0, 10))

tk.Label(
    panel_derecho,
    text="Texto recuperado como evidencia",
    font=("Arial", 13, "bold"),
    bg="#F8FAFC",
    fg="#111827"
).pack(anchor="w", padx=15, pady=(0, 5))

contexto_texto = scrolledtext.ScrolledText(
    panel_derecho,
    font=("Arial", 9),
    bg=COLOR_BLANCO,
    fg="#111827",
    relief="flat",
    wrap=tk.WORD
)
contexto_texto.pack(fill="both", expand=True, padx=15, pady=(0, 15))

ventana.mainloop()
