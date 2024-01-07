from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Set, List, Dict
from agentverse.simulation import Simulation
from agentverse.message import Message
import time

#compile setting
import os
# os.environ["TORCH_USE_CUDA_DSA"]="1"
# os.environ["CUDA_LAUNCH_BLOCKING"]="1"

def get_cur_time():
    import datetime
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")        

cur_time=get_cur_time()
dir=f"./stdout/{cur_time}.txt"
def filewrite(dir, content):
    with open(dir, "a") as f:
        f.write(str(content))
        f.write("\n")
        
class UserRequest(BaseModel):
    content: str = Field(default="")
    sender: str = Field(default="Brendan")
    receiver: str
    receiver_id: int


class RoutineRequest(BaseModel):
    agent_ids: List[int]


class UpdateRequest(BaseModel):
    agent_locations: Dict[str, str]

class ReactionRequest(BaseModel):
    agent_ids: List[int]
    situation: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#/home/sngwon/workspace/AgentVerse/agentverse_command/../agentverse/tasks/simulation/pokemon"
task_dir="/home/sngwon/workspace/AgentVerse/agentverse/tasks/simulation"
agent_verse = Simulation.from_task("pokemon", tasks_dir=task_dir)



# ###llm
# import GPUtil
# GPUtil.showUtilization()
# from transformers import AutoModelForCausalLM, AutoTokenizer

# print("model load start")
# model_1 = AutoModelForCausalLM.from_pretrained("/home/sngwon/workspace/NC/lit-gpt/checkpoints/mistralai/Mistral-7B-Instruct-v0.2",  device_map="cuda:0", load_in_8bit=True)
# model_2 = AutoModelForCausalLM.from_pretrained("/home/sngwon/workspace/NC/lit-gpt/checkpoints/mistralai/Mistral-7B-Instruct-v0.2",  device_map="cuda:1", load_in_8bit=True)
# model_3 = AutoModelForCausalLM.from_pretrained("/home/sngwon/workspace/NC/lit-gpt/checkpoints/mistralai/Mistral-7B-Instruct-v0.2",  device_map="cuda:2", load_in_8bit=True)
# print("model load end")

# tokenizer = AutoTokenizer.from_pretrained("/home/sngwon/workspace/NC/lit-gpt/checkpoints/mistralai/Mistral-7B-Instruct-v0.2")
# model_dict={
#     "model_1":model_1,
#     "model_2":model_2,
#     "model_3":model_3,
#     "tokenizer":tokenizer
# }








@app.get("/")
def health_check():
    filewrite(dir, "health check")
    return {"status": "ok"}


@app.post("/chat")
def chat(message: UserRequest):
    content = message.content

    receiver = message.receiver
    receiver_id = message.receiver_id
    response = agent_verse.next(
        is_player=True,
        player_content=content,
        receiver=receiver,
        receiver_id=receiver_id,
        llm="local"
    )

    
    return response[0].dict()


@app.post("/make_decision")
def update(message: RoutineRequest):
    print(("Shouldupdate"))
    print(message)
    #response = agent_verse.next(is_player=False, agent_ids=message.agent_ids)
    response = agent_verse.next(is_player=False, agent_ids=message.agent_ids, llm="local")
    #response = agent_verse.next(is_player=False, agent_ids=message.agent_ids, llm="local", model_dict=model_dict)

    #print([r.dict() for r in response])
    return [r.dict() for r in response]


@app.post("/reaction")
def reaction(message: ReactionRequest):
    return {"message": "Update location complete"}









@app.post("/update_location")
def update_location(message: UpdateRequest):
    agent_verse.update_state(message.agent_locations)
    return {"message": "Update location complete"}


