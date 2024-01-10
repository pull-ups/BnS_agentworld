from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Set, List, Dict
from agentverse.simulation import Simulation
from agentverse.message import Message
import time

import os

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


class ReactionPlanRequest(BaseModel):
    agent_ids: List[int]
    situation: str
    reactions: List[str]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

task_dir="/home/sngwon/workspace/AgentVerse/agentverse/tasks/simulation"
agent_verse = Simulation.from_task("pokemon", tasks_dir=task_dir)



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
    

    #print([r.dict() for r in response])
    return [r.dict() for r in response]


@app.post("/reaction")
def reaction(message: ReactionRequest):
    response = agent_verse.reaction(agent_ids=message.agent_ids, situation=message.situation, llm="local")
    print("==response of Reaction==")
    print(response)
    return [r.dict() for r in response]



# class ReactionPlanRequest(BaseModel):
#     agent_ids: List[int]
#     situation: str
#     reactions: List[str]

@app.post("/reactionplan")
def reactionplan(message: ReactionPlanRequest):
    
    response = agent_verse.reactionplan(agent_ids=message.agent_ids, situation=message.situation, reactions=message.reactions, llm="local")
    print("==response of ReactionPlan==")
    print(response)
    return [r.dict() for r in response]






@app.post("/update_location")
def update_location(message: UpdateRequest):
    agent_verse.update_state(message.agent_locations)
    return {"message": "Update location complete"}


