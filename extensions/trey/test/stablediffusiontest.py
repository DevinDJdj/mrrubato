#> pip install diffusers transformers accelerate layout
#https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/sd_xl_base_1.0.safetensors
#https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors?download=true
#> hf download stabilityai/stable-diffusion-xl-base-1.0 --local-dir ./models/stablediffusion
#LLM Generate
#~60 words limit..
#alternative..
#https://huggingface.co/stabilityai/stable-diffusion-3.5-large-turbo
#VRAM 16GB
#https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5
#VRAM 6GB

import torch
from diffusers import StableDiffusionXLPipeline

# Path to the directory containing the full model structure
local_model_path = "./models/stablediffusion/sd_xl_base_1.0.safetensors"
save_directory = "./models/stablediffusion_complete"
print("Loading Stable Diffusion XL model...")
#pipeline = StableDiffusionXLPipeline.from_single_file(
#    f"{local_model_path}",
pipeline = StableDiffusionXLPipeline.from_pretrained(
    f"{save_directory}",
    torch_dtype=torch.float16,
#    variant="fp16",          # Use if your folder contains fp16 weights
    use_safetensors=True,    # Safely load tensors
    local_files_only=True    # Uncomment once!!??
)
pipeline.to("cuda")

#pipeline.save_pretrained(save_directory)
# Run the model on GPU
pipeline = pipeline.to("cuda")

prompt = "A photograph of a horse on a highway road at sunset"

print("Generating image from prompt...")
image = pipeline(prompt=prompt).images[0]
image.save("stablediffusiontest.png")
print("Image saved as stablediffusiontest.png")