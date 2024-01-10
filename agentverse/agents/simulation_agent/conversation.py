from __future__ import annotations
from colorama import Fore
import random
import time
import asyncio

# import logging
from agentverse.logging import get_logger
import bdb
from string import Template
from typing import TYPE_CHECKING, List

from agentverse.message import Message

# from . import agent_registry
# from .base import BaseAgent
from agentverse.agents import agent_registry
from agentverse.agents.base import BaseAgent
from .nc_templates import get_prompt_talkplayer, get_prompt_talknpc_init, get_prompt_talknpc



import asyncio
import functools
import openai
import json
import time


from glob import glob
from tqdm import tqdm
from threading import Thread

# ------------------------------------------------
# constant
# ------------------------------------------------
GPT_TIMEOUT = 60


# ------------------------------------------------
# utils
# ------------------------------------------------
def parse_NPC_response(text):
    "Jinsoyun (speaking): Lusung, you stand before me now, your presence unchanged, as stubborn as ev"
    try:
        if "(speaking):" in text:
            text=text.split("(speaking):")[1]
        elif ":" in text[:30]:
            text=text.split(":")[1]
        return text
    except:
        return text

def cut_sentence(text):
    if len(text) < 200:
        return text
        
    """
    Extracts the first three sentences from a given text.
    Sentences are assumed to end with '.', '!', or '?'.
    Ellipses '...' are treated as a single period.
    """
    # Replacing ellipses with a single period to avoid counting them as multiple sentence ends
    cleaned_text = text.replace("...", ".")

    # Initialize variables
    sentences = []
    sentence = ""
    sentence_count = 0

    # Iterate over each character in the text
    for char in cleaned_text:
        sentence += char
        # Check if the character is a sentence-ending punctuation
        if char in '.!?':
            sentence_count += 1
            # Add the sentence to the list and reset the sentence variable
            sentences.append(sentence.strip())
            sentence = ""
            # Break if three sentences are found
            if sentence_count == 3:
                break

    return ' '.join(sentences)


def make_json_compatible(input_string):
    # Replace problematic characters with escaped versions
    # Escaping double quotes, backslashes, and control characters like newlines
    output_string = input_string.replace('\\', '\\\\')  # Escape backslashes
    output_string = output_string.replace('"', '\\"')   # Escape double quotes
    output_string = output_string.replace('\n', '\\n')  # Escape newlines
    output_string = output_string.replace('\r', '\\r')  # Escape carriage returns
    output_string = output_string.replace('\t', '\\t')  # Escape tabs
    # Add more replacements as needed for other control characters
    return output_string

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception(f'function [{func.__name__}] timeout [{timeout} seconds] exceeded!')]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

def get_npc_log_path(args, npc_name):
    return args.npc_info_map[npc_name]["log"]

def get_npc_url(args, host, npc_name):
    port = args.npc_info_map[npc_name]["port"]
    url = args.url_format.format(host=host, port=port)
    return url



def get_response_data(args, model, prompt, openai_api_base):
    
    content = [
        {"role": "user", "content": prompt},
    ]
    openai_api_key = "EMPTY"
    openai_api_base = "http://localhost:8000/v1" if openai_api_base is None else openai_api_base
    client = openai.OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    _t = None
    # try:
    _t = time.time()
    if is_instruct(model):
        response = call_gpt(args, model, client, stream=args.stream, prompt=content)
    else:
        response = call_gpt(args, model, client, stream=args.stream, messages=content)
    _t = time.time() - _t
    # except Exception as e:
    #     print('timeout occur', str(e))
    #     raise e

    data = {
        "response": response,
        "elapsed_time": _t,
    }
    return data


def is_instruct(model): return "instruct" in model

@timeout(GPT_TIMEOUT)
def call_gpt(args, model, client, **kwargs):
    if is_instruct(model) and ("gpt" in model):
        response = client.completions.create(model=model, **kwargs, **args.gpt_kwargs)
    else:
        response = client.chat.completions.create(model=model, **kwargs, **args.gpt_kwargs)
    return response

# ------------------------------------------------

class args: # hard coded
    model = "mistralai/Mistral-7B-Instruct-v0.2"
    system_prompt = "You are a helpful assistant."

    gpt_kwargs = {
        "max_tokens": 100,
        "temperature": 0.6,
        "top_p": 0.95,
        "n": 1,
        "stop": ["<|eot|>", "</s>", ". "],
    }
    stream = False
    max_trial = 5
    max_worker = 8

    openai_api_key = "None"

    url_format = "http://{host}:{port}/v1"
    npc_info_map = {
        "Jinsoyun": {
            "model": "Jinsoyun",
            "host": "node32",
            "port": "4200",
            "log": "./logs/npc_0.log",
        },
        "Lusung": {
            "model": "Lusung",
            "host": "node32",
            "port": "4201",
            "log": "./logs/npc_1.log",
        },
        "Yura": {
            "model": "Yura",
            "host": "node32",
            "port": "4202",
            "log": "./logs/npc_2.log",
        },
        "HongSokyun": {
            "model": "HongSokyun",
            "host": "node32",
            "port": "4203",
            "log": "./logs/npc_3.log",
        },
    }

def llm_local_inference(character_name, prompt):
    host=args.npc_info_map[character_name]["host"]
    model=args.npc_info_map[character_name]["model"]
    npc_url = get_npc_url(args, host, character_name)    
    
    data, i, errors, elapsed_time = {}, 0, [], None
    response = None
    while i < args.max_trial:
        try:
            data = get_response_data(args, model, prompt, openai_api_base=npc_url)
            response = data["response"]
            elapsed_time = data["elapsed_time"]
            break
        except Exception as e:
            errors.append(e)
            print(e)
            # raise e
            i += 1
    output = response.choices[0].message.content.strip()
    return output

logger = get_logger()

def pick_one_from_arr(arr):
    return arr[random.randint(0, len(arr)-1)]
        
@agent_registry.register("conversation")
class ConversationAgent(BaseAgent):
    doing_conversation=False
    conversation_turn_last=0
    dialog_history=[]

   
    
    
    def step(self, env_description: str = "") -> Message:
        prompt = self._fill_prompt_template(env_description)

        parsed_response = None
        for i in range(self.max_retry):
            try:
                response = self.llm.generate_response(prompt)
                parsed_response = self.output_parser.parse(response)
                

                break
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(e)
                logger.warn("Retrying...")
                continue

        if parsed_response is None:
            logger.error(f"{self.name} failed to generate valid response.")

        message = Message(
            content=""
            if parsed_response is None
            else parsed_response.return_values["output"],
            sender=self.name,
            receiver=self.get_receiver(),
        )
        return message

    async def astep(self, env_description: str = "") -> Message:
        """Asynchronous version of step"""
        prompt = self._fill_prompt_template(env_description)
        # print("===============")
        parsed_response = None
        for i in range(self.max_retry):
            try:
                response = await self.llm.agenerate_response(prompt)                
                parsed_response = self.output_parser.parse(response)
                break
            except (KeyboardInterrupt, bdb.BdbQuit):
                raise
            except Exception as e:
                logger.error(e)
                logger.warn("Retrying...")
                continue

        if parsed_response is None:
            logger.error(f"{self.name} failed to generate valid response.")

        message = Message(
            content=""
            if parsed_response is None
            else parsed_response.return_values["output"],
            sender=self.name,
            receiver=self.get_receiver(),
        )
        # print("==in agents/simulation_agent/conversation.py, message==")
        # print(message)
        # print(type(message))
        # print("===============")
        return message

    #async def astep_local(self, env_description: str = "") -> Message:
    async def astep_local(self, info_from_env: dict = "") -> Message:
        env_description=info_from_env["env_description"]
        nearbyNPCs=info_from_env["nearbyNPCs"]
        conversation_info=info_from_env["conversation_info"]


        prompt = self._fill_prompt_template(env_description)
        action_list=self.action_list
        #conversation_info={"doing_conversation":True, "to": Birch, "speaker": True, "listener": False}
        
        #대화중이면 action=Cnversation, 아니면 action=MoveTo or SomethingAction
        print(f"Memory of {self.name}")
        print(self.dialog_history)
                                 
        if conversation_info["doing_conversation"]:
            #대화 남은 턴 처리
            self.doing_conversation=True
            if conversation_info["first"]:
                self.conversation_turn_last=conversation_info['conversation_turn_last']
            else:
                self.conversation_turn_last-=1
            
            
            # await asyncio.sleep(5)
            
            chat_counterpart=conversation_info["to"]
            
            if self.conversation_turn_last==0: #대화가 끝났으면
                content='{{"to": "{}", "text": "conversation_finish", "action": "Conversation"}}'.format(conversation_info["to"])
            
            else: # 대화가 안끝났으면, 말하는 사람과 듣는 사람 구분하여 메세지 전달   
                
                if conversation_info["speaker"]:
                    ##local llm 
                    character_name=self.name
                    #처음인지 아닌지에 따라 prompt 다르게
                    if conversation_info["first"]:
                        prompt=get_prompt_talknpc_init(name=character_name, location="Jiwan's Peak", name_other=chat_counterpart, relationship="")
                    else:
                        prompt=get_prompt_talknpc(name=character_name, location="Jiwan's Peak", name_other=chat_counterpart, relationship="", conversation_log=self.dialog_history)
                    
                    output=llm_local_inference(character_name, prompt)
                    
                    output=cut_sentence(output) # 3문장으로 자르기
                    output=parse_NPC_response(output) # (speaking): 제거
                    output=make_json_compatible(output) # json 형식으로 변환
                    
                    # output : Jinsoyun (speaking): Jinsoyun. Nice to meet you, Miles. You seem like a curious soul. I sense a spark in you, unlike others.
                    chat_message=output
                    #chat_message=f"Hi {chat_counterpart},  I am {self.name}. How are you?"
                    content='{{"to": "{}", "text": "{}", "action": "Conversation", "speaking": "{}"}}'.format(chat_counterpart, chat_message,  True)
                    
                else:
                    content='{{"to": "{}", "text": "", "action": "Conversation", "speaking": "{}"}}'.format(chat_counterpart, False)
        else:
            move_list=['{"to": "Shop", "action": "MoveTo"}', 
                   '{"to": "Bike Store", "action": "MoveTo"}', 
                   '{"to": "Park", "action": "MoveTo"}']
        
            action_list = [f'{{"last_time": "50 minutes", "action": "{item}"}}' for item in action_list]

            if random.random() < 0.2:    
                content=pick_one_from_arr(action_list)
            else:
                content=pick_one_from_arr(move_list)
                 
                   
        

        #response = await self.llm.agenerate_response_local(prompt)
        #parsed_response = self.output_parser.parse_local(response)

   
        message = Message(
            content=content,
            sender=self.name,
            receiver=self.get_receiver(),
        )
        #sngwonprint
        #print(self.name, message)
        
        return message


    async def astep_respondtoplayer(self, env_description: str = "") -> Message:
        """Asynchronous version of step"""
        prompt = self._fill_prompt_template(env_description)
        # print("===============")
        parsed_response = None
        
        character_name=self.name
        print("========in astep_respondtoplayer======")
        print(prompt)
        print("===================================")
        output=llm_local_inference(character_name, prompt)
        print("========output======")
        print(output)
        
        # for i in range(self.max_retry):
        #     try:
        #         response = await self.llm.agenerate_response(prompt)                
        #         parsed_response = self.output_parser.parse(response)
        #         break
        #     except (KeyboardInterrupt, bdb.BdbQuit):
        #         raise
        #     except Exception as e:
        #         logger.error(e)
        #         logger.warn("Retrying...")
        #         continue

        # if parsed_response is None:
        #     logger.error(f"{self.name} failed to generate valid response.")

        message = Message(
            content=""
            if parsed_response is None
            else parsed_response.return_values["output"],
            sender=self.name,
            receiver=self.get_receiver(),
        )
        # print("==in agents/simulation_agent/conversation.py, message==")
        # print(message)
        # print(type(message))
        # print("===============")
        return message





    async def areaction_local(self, info_from_env: dict = "") -> Message:
        env_description=info_from_env["env_description"]
        situation=info_from_env["situation"]
        

        prompt = self._fill_prompt_template(env_description)
        
        await asyncio.sleep(15)
        
        content='{{"text": "Reacting to {}", "plan":"1. A, 2. B, 3. C", "action": "Reaction"}}'.format(situation)

        
        message = Message(
            content=content,
            sender=self.name,
            receiver=self.get_receiver(),
        )

        return message









    def _fill_prompt_template(self, env_description: str = "") -> str:
        """Fill the placeholders in the prompt template

        In the conversation agent, three placeholders are supported:
        - ${agent_name}: the name of the agent
        - ${env_description}: the description of the environment
        - ${role_description}: the description of the role of the agent
        - ${chat_history}: the chat history of the agent
        """
        input_arguments = {
            "agent_name": self.name,
            "env_description": env_description,
            "role_description": self.role_description,
            "chat_history": self.memory.to_string(add_sender_prefix=True),
        }
        return Template(self.prompt_template).safe_substitute(input_arguments)

    def add_message_to_memory(self, messages: List[Message]) -> None:
        self.memory.add_message(messages)

    def reset(self) -> None:
        """Reset the agent"""
        self.memory.reset()
        # TODO: reset receiver
