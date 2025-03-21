# https://huggingface.co/black-forest-labs/FLUX.1-dev
import datetime
import torch
from diffusers import FluxPipeline

prompt = "Elon Musk holds sign with text Hello DeepLogix"
model_id = "black-forest-labs/FLUX.1-dev"

pipe = FluxPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)

result = pipe(
    prompt,
    height=512,
    width=512,
    guidance_scale=3.5,
    num_inference_steps=10,
    max_sequence_length=512,
)

image = result.images[0]
image.save(f"flux-result-{(datetime.datetime.now()).strftime('%Y-%m-%d-%H-%M-%S')}.png")
