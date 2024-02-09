#pip install -q peft==0.4.0 bitsandbytes==0.40.2 transformers==4.31.0 trl==0.4.7
#pip install scipy
#pip install tensorboard

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import LoraConfig, PeftModel
from trl import SFTTrainer


exec(compile(source=open('bitsandbytes_params.py').read(), filename='bitsandbytes_params.py', mode='exec'))
exec(compile(source=open('qlora_params.py').read(), filename='qlora_params.py', mode='exec'))
exec(compile(source=open('training_arguments_params.py').read(), filename='training_arguments_params.py', mode='exec'))
exec(compile(source=open('sft_params.py').read(), filename='sft_params.py', mode='exec'))
exec(compile(source=open('model_names_params.py').read(), filename='model_names_params.py', mode='exec'))
exec(compile(source=open('loaders.py').read(), filename='loaders.py', mode='exec'))
exec(compile(source=open('training.py').read(), filename='training.py', mode='exec'))
exec(compile(source=open('testing.py').read(), filename='testing.py', mode='exec'))


