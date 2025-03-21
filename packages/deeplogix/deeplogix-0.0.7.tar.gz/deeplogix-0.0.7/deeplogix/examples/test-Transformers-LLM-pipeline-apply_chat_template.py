# https://huggingface.co/docs/transformers/v4.49.0/en/pipeline_tutorial#pipelines-for-inference
# https://huggingface.co/docs/transformers/main/en/chat_templating
from transformers import pipeline
import torch

AI_ANSWERS_LENGTH = 300

model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
#model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
#model_id="Qwen/Qwen2.5-3B-Instruct"

inputs = [
    {"role": "system", "content": "You are a poet chat bot"},
    {"role": "user", "content": "Write me a poem about cats"},
]

pipe = pipeline("text-generation", model=model_id, torch_dtype=torch.float16)
prompt = pipe.tokenizer.apply_chat_template(inputs, tokenize=False, add_generation_prompt=True)
outputs = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
print(outputs[0]["generated_text"])
