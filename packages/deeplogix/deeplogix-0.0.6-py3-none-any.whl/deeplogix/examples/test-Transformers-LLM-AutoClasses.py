# https://huggingface.co/docs/transformers/v4.49.0/en/model_doc/auto#auto-classes
from transformers import AutoModelForCausalLM, AutoTokenizer

AI_ANSWERS_LENGTH = 300

model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
#model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
#model_id="Qwen/Qwen2.5-3B-Instruct"

model = AutoModelForCausalLM.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)

try:
    while True:
        inputs = tokenizer(input("\nYour question >>> "), return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=AI_ANSWERS_LENGTH)
        print(f"\nA.I. answer >>> {tokenizer.decode(*outputs)}")
except KeyboardInterrupt:
    print("\nExit.")
