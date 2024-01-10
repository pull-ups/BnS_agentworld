from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import asyncio
import time
NPC_names=["Jinsoyun", "Lusung"]
params_dict={}
base_model_name = "/home/sngwon/workspace/NC/lit-gpt/checkpoints/mistralai/Mistral-7B-Instruct-v0.2"


def get_prompt(inputs, generation_type):
    name, other_name, location, text = inputs["name"], inputs["other_name"], inputs["location"], inputs["text"]
    
    dialog_1turn_prompt=f"""<s> [INST] I want you to act like {name}. I want you to respond and answer like {name}, using the tone, manner and vocabulary {name} would use. You must know all of the knowledge of {name}. 

The status of you is as follows:
Location: {location}
Status: {name} is casually chatting with {other_name}.


The interactions are as follows:
{other_name} (speaking): Hi {name}, {text}<|eot|>
[/INST]"""
    if generation_type=="dialog_1turn":
        return dialog_1turn_prompt





class Generate:
    
    model_dict={}
    def __init__(self):
        print("Loading LLM...")
        self.load_models()
        print("Loading LLM finish")
        
    def load_models(self):
        for i, name in enumerate(NPC_names):
            device="cuda:{}".format(i)
            checkpoint_file=f"/home/sngwon/workspace/NC/lit-gpt/out/converted/NC_v3/{name}/converted.ckpt"
            model = AutoModelForCausalLM.from_pretrained(base_model_name).to(device)
            model.load_state_dict(torch.load(checkpoint_file))
            
            self.model_dict[f"model{i}"]=model
            print(f"model {i} load finish")
        for i, name in enumerate(NPC_names):
            tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            self.model_dict[f"tokenizer{i}"]=tokenizer
  
    
    async def agenerate(self, index, inputs, generation_type):
        device="cuda:{}".format(index)
        model=self.model_dict[f"model{index}"]
        tokenizer=self.model_dict[f"tokenizer{index}"]
        
        
        start=time.time()
        prompt=get_prompt(inputs, generation_type)
        model_inputs = tokenizer([prompt], return_tensors="pt").to(device)
        generated_ids = model.generate(**model_inputs, max_new_tokens=100, do_sample=True)
        #response=tokenizer.batch_decode(generated_ids)[0].split("[/INST]")[1]
        #if "<|eot|>\n" in response:
        #    response=response.split("<|eot|>\n")[0]
        
        print(f"in {index}, response: {generated_ids}, time: {time.time()-start}")
        
        
        return generated_ids
        

async def step():
    start=time.time()
    messages = await asyncio.gather(
            *[local_llms.agenerate(i, inputs[i], "dialog_1turn") for i in range(2)]
        )
    print("messages")
    print(messages)
    print(time.time()-start, "seconds")
    return messages



if __name__=="__main__":
    local_llms=Generate()
    input_info1={
        "name": "Jinsoyun",
        "other_name": "Seungwon",
        "location": "Coffee Shop - Afternoon",
        "text": "How are you?"
    }
    input_info2={
        "name": "Lusung",
        "other_name": "Seungwon",
        "location": "Coffee Shop - Afternoon",
        "text": "How are you?"
    }
    inputs=[input_info1, input_info2]
    start=time.time()
    # response=local_llms.generate(0, input_info1, "dialog_1turn")
    # print(response)
    
    result = asyncio.run(step())
    print("result", result)