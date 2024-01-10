import time
from transformers import AutoModelForCausalLM, AutoTokenizer

# llm.py
class Generate:
    def __init__(self):
        print("Loading LLM...")
        dir="/home/sngwon/workspace/NC/lit-gpt/checkpoints/mistralai/Mistral-7B-Instruct-v0.2"
        self.model = AutoModelForCausalLM.from_pretrained(dir, load_in_8bit=True)
        self.tokenizer = AutoTokenizer.from_pretrained(dir)
        self.device = "cuda:0"
        self.model.to(self.device)
        print("Loading LLM finish")
    def generate(self, messages):
        encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(self.device)
        generated_ids = model.generate(model_inputs, max_new_tokens=10, do_sample=True)
        decoded = tokenizer.batch_decode(generated_ids) 
        
        return decoded[0]
    
    
    
generator_instance = Generate()








