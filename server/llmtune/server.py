# 0. imports
#pip install torch
#pip install trl
#huggingface-cli login
#https://huggingface.co/settings/tokens

import torch
from transformers import GPT2Tokenizer

from transformers import AutoModelForCausalLM
from trl import AutoModelForCausalLMWithValueHead, PPOConfig, PPOTrainer




# .. Let's assume we have a trained model using `PPOTrainer` and `AutoModelForCausalLMWithValueHead`


# load the model from the Hub

model = AutoModelForCausalLM.from_pretrained("my-fine-tuned-model-ppo")

initial_model = "gpt2" #llama2
# 1. load a pretrained model
#model = AutoModelForCausalLMWithValueHead.from_pretrained("gpt2")
model_ref = AutoModelForCausalLMWithValueHead.from_pretrained("my-fine-tuned-model-ppo")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

# 2. initialize trainer
ppo_config = {"batch_size": 1}
config = PPOConfig(**ppo_config)
ppo_trainer = PPOTrainer(config, model, model_ref, tokenizer)

# 3. encode a query
query_txt = "This morning I went to the "
query_tensor = tokenizer.encode(query_txt, return_tensors="pt").to(model.pretrained_model.device)

# 4. generate model response
generation_kwargs = {
    "min_length": -1,
    "top_k": 0.0,
    "top_p": 1.0,
    "do_sample": True,
    "pad_token_id": tokenizer.eos_token_id,
    "max_new_tokens": 20,
}
response_tensor = ppo_trainer.generate([item for item in query_tensor], return_prompt=False, **generation_kwargs)
response_txt = tokenizer.decode(response_tensor[0])

# 5. define a reward for response
# (this could be any reward such as human feedback or output from another model)
reward = [torch.tensor(1.0, device=model.pretrained_model.device)]

# 6. train model with ppo
train_stats = ppo_trainer.step([query_tensor[0]], [response_tensor[0]], reward)

# push the model on the Hub
#model.push_to_hub("my-fine-tuned-model-ppo")

# or save it locally
model.save_pretrained("my-fine-tuned-model-ppo")
