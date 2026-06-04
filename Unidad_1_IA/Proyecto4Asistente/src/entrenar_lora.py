import os
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType


MODELO_BASE = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
DATASET = "data/finetuning_dataset_train_2000.jsonl"
SALIDA = "modelo_finetuned"

os.makedirs(SALIDA, exist_ok=True)

print("Cargando dataset...")
dataset = load_dataset(
    "json",
    data_files=DATASET,
    split="train"
)

print("Cargando tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


def formatear_ejemplo(ejemplo):
    instruccion = ejemplo.get("instruction", "")
    entrada = ejemplo.get("input", "")
    salida = ejemplo.get("output", "")

    texto = f"""### Instrucción:
{instruccion}

### Entrada:
{entrada}

### Respuesta:
{salida}"""

    tokens = tokenizer(
        texto,
        truncation=True,
        padding="max_length",
        max_length=256
    )

    tokens["labels"] = tokens["input_ids"].copy()

    return tokens


print("Tokenizando dataset...")
dataset_tokenizado = dataset.map(
    formatear_ejemplo,
    remove_columns=dataset.column_names
)

print("Cargando modelo base...")
modelo = AutoModelForCausalLM.from_pretrained(
    MODELO_BASE,
    device_map="cpu",
    low_cpu_mem_usage=True
)

modelo.config.pad_token_id = tokenizer.pad_token_id

print("Aplicando configuración LoRA...")
config_lora = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

modelo = get_peft_model(modelo, config_lora)
modelo.print_trainable_parameters()

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

argumentos = TrainingArguments(
    output_dir=SALIDA,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    num_train_epochs=1,
    learning_rate=2e-4,
    logging_steps=20,
    save_strategy="epoch",
    fp16=False,
    report_to="none"
)

print("Iniciando entrenamiento LoRA...")
trainer = Trainer(
    model=modelo,
    args=argumentos,
    train_dataset=dataset_tokenizado,
    data_collator=data_collator
)

trainer.train()

print("Guardando modelo LoRA...")
modelo.save_pretrained(SALIDA)
tokenizer.save_pretrained(SALIDA)

print("Fine-Tuning LoRA terminado.")
print("Adaptador guardado en:", SALIDA)