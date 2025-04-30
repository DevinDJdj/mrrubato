#logic for training a custom model.  
#huggingface-cli download meta-llama/Meta-Llama-3.1-8B-Instruct --local-dir /mnt/c/devinpiano/testing/models/Meta-Llama-3.1-8B-Instruct

#sudo apt install python3.11
#pip install bitsandbytes
#pip install unsloth
#pip install "unsloth[cu121-torch240] @ git+https://github.com/unslothai/unsloth.git"
#pip install -U transformers accelerate

#./server/ollama/train.py

#> pip install datasets
#> pip install trl


dataset = [
    {"instruction": "Translate to French: Hello, how are you?", "output": "Bonjour, comment allez-vous?"},
{"instruction": "Summarize this text: [Your long text here]", "output": "[Your summary here]"},
# Add more examples...
]


from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained(
"meta-llama/Llama-3.1-8b-hf",
trust_remote_code=True,
load_in_4bit=True,
)

from transformers import TrainingArguments
training_args = TrainingArguments(
output_dir="./results",
num_train_epochs=3,
per_device_train_batch_size=4,
warmup_steps=500,
weight_decay=0.01,
logging_dir="./logs",
)


from unsloth import FastTrainer
trainer = FastTrainer(
model=model,
args=training_args,
train_dataset=dataset,
tokenizer=tokenizer,
)
trainer.train()

model.save_pretrained("./fine_tuned_model") # Local saving
tokenizer.save_pretrained("./fine_tuned_model")

# Push the fine-tuned model to Hugging Face Hub (Optional):
# model.push_to_hub("your_name/fine_tuned_model", token = "...")
# tokenizer.push_to_hub("your_name/fine_tuned_model", token = "...")

# Save to 16bit GGUF
model.save_pretrained_gguf("model", tokenizer, quantization_method = "f16")

#ollama create model_name -f ./model/Modelfile


from transformers import pipeline

generator = pipeline("text-generation", model="./fine_tuned_model")
result = generator("Translate to French: Good morning!")
print(result[0]['generated_text'])
