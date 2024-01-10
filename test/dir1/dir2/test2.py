import sys
sys.path.append("/home/sngwon/workspace/AgentVerse/test")
from llm import generator_instance

def some_function_in_test2():
    
    messages = [{"role": "user", "content": "explain about python"}]
    
    generated_text = generator_instance.generate("text") + "in test2"
    return generated_text