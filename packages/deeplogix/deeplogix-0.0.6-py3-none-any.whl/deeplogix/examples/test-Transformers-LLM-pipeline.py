# https://huggingface.co/docs/transformers/v4.49.0/en/pipeline_tutorial#pipelines-for-inference
from transformers import pipeline

AI_ANSWERS_LENGTH = 300

model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
#model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
#model_id="Qwen/Qwen2.5-3B-Instruct"

pipe = pipeline("text-generation", model=model_id)

try:
    while True:
        inputs = input("\nYour question >>> ");
        outputs = pipe(inputs, max_new_tokens=AI_ANSWERS_LENGTH, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
        print(f"\nA.I. answer >>> {outputs[0]['generated_text']}")
except KeyboardInterrupt:
    print("\nExit.")
