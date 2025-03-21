# https://huggingface.co/stabilityai/stable-diffusion-3.5-large
import datetime
import torch
from diffusers import StableDiffusion3Pipeline

prompt = "Elon Musk holds sign with text Hello DeepLogix"
model_id = "stabilityai/stable-diffusion-3.5-large"

pipe = StableDiffusion3Pipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)

result = pipe(
    prompt,
    num_images_per_prompt = 1,
    height=512,
    width=512,
    num_inference_steps = 10,
    guidance_scale = 3.5,
)

image = result.images[0]
image.save(f"stable-diffusion-result-{(datetime.datetime.now()).strftime('%Y-%m-%d-%H-%M-%S')}.png")
