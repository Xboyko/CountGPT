from unsloth import FastLanguageModel

print("Loading base model + your fine-tuned adapters...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="countgpt_model",
    max_seq_length=2048,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)

question = "Draft a POA&M entry for a Moderate-severity finding on a DoD system."

prompt = f"### Instruction:\n{question}\n\n### Response:\n"

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=300, temperature=0.7)

response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\n=== MODEL'S ANSWER ===\n")
print(response)
