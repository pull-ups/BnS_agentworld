import sys
sys.path.append("/home/sngwon/workspace/AgentVerse/test")
from llm import generator_instance

def some_function_in_test1():
    
    messages = [{"role": "user", "content": "Hi?"}]

    
    generated_text = generator_instance.generate(messages) + "in test1"
    return generated_text
    