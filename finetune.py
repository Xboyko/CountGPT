from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import Dataset
import json

print("Loading base model (Llama 3.1 8B, 4-bit)...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=2048,
    load_in_4bit=True,
)

print("Attaching LoRA adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

print("Loading your training data...")
examples = []
with open("training_data.jsonl", "r") as f:
    for line in f:
        line = line.strip()
        if line:
            examples.append(json.loads(line))

print(f"Loaded {len(examples)} examples")

texts = []
for ex in examples:
    text = f"### Instruction:\n{ex['instruction']}\n\n### Response:\n{ex['output']}<|end_of_text|>"
    texts.append(text)

dataset = Dataset.from_dict({"text": texts})

print("Starting training...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        logging_steps=1,
        output_dir="training_output",
        optim="adamw_8bit",
    ),
)

trainer.train()

print("Saving your fine-tuned model...")
model.save_pretrained("countgpt_model")
tokenizer.save_pretrained("countgpt_model")
print("Done!")