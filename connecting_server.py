from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Set, List, Dict
from agentverse.simulation import Simulation
from agentverse.message import Message
import time
import requests
import json
#compile setting
import os
from fastapi import FastAPI

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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

@app.get("/")
def root():
    return {"message": "Hello World"}




@app.post("/chat")
def chat(message: UserRequest):
    url = 'http://10.1.1.41:10002/chat'
    data=message.dict()
    response = requests.post(url, json=data)
    
    decoded_str = response.content.decode('utf-8')
    data = json.loads(decoded_str)
    
    return data




@app.post("/make_decision")
def update(message: RoutineRequest):
    url = 'http://10.1.1.41:10002/make_decision'
    data=message.dict()
    print(data["agent_ids"])
    
    response = requests.post(url, json=data)
    
    decoded_str = response.content.decode('utf-8')

    # Loading string as JSON
    data = json.loads(decoded_str)

    # Converting 'receiver' lists to sets
    for item in data:
        item['receiver'] = set(item['receiver'])
    return data


@app.post("/reaction")
def reaction(message: ReactionRequest):
    url = 'http://10.1.1.41:10002/reaction'
    data=message.dict()
    response = requests.post(url, json=data)
    
    decoded_str = response.content.decode('utf-8')

    data = json.loads(decoded_str)


    return data


@app.post("/update_location")
def update_location(message: UpdateRequest):
    url = 'http://10.1.1.41:10002/update_location'
    data=message.dict()
    response = requests.post(url, json=data)
    #print("in update_location")
    #print(response)