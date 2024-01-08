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

logger = get_logger()

def pick_one_from_arr(arr):
    return arr[random.randint(0, len(arr)-1)]
        
@agent_registry.register("conversation")
class ConversationAgent(BaseAgent):
    doing_conversation=False
    conversation_turn_last=0
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
                # if self.name == "Code Reviewer":
                #logger.debug(prompt, "Prompt", Fore.CYAN)
                response = await self.llm.agenerate_response(prompt)
                # print("chatgpt response")
                # print(response)
                # print("===============")
                # logging.info(f"{self.name}'s request result:"
                #              f" {response.content}")
                
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
        if conversation_info["doing_conversation"]:
            #대화 남은 턴 처리
            self.doing_conversation=True
            if conversation_info["first"]:
                self.conversation_turn_last=conversation_info['conversation_turn_last']
            else:
                self.conversation_turn_last-=1
            
            
            await asyncio.sleep(5)
            
            chat_counterpart=conversation_info["to"]
            
            if self.conversation_turn_last==0: #대화가 끝났으면
                content='{{"to": "{}", "text": "conversation_finish", "action": "Conversation"}}'.format(conversation_info["to"])
            
            else: # 대화가 안끝났으면, 말하는 사람과 듣는 사람 구분하여 메세지 전달                
                if conversation_info["speaker"]:
                    chat_message=f"Hi {chat_counterpart},  I am {self.name}. How are you?"
                    content='{{"to": "{}", "text": "{}", "action": "Conversation", "speaking": "{}"}}'.format(chat_counterpart, chat_message,  True)
                    
                else:
                    content='{{"to": "{}", "text": "", "action": "Conversation", "speaking": "{}"}}'.format(chat_counterpart, False)
        else:
            move_list=['{"to": "Shop", "action": "MoveTo"}', 
                   '{"to": "Bike Store", "action": "MoveTo"}', 
                   '{"to": "Park", "action": "MoveTo"}']
        
            action_list = [f'{{"last_time": "50 minutes", "action": "{item}"}}' for item in action_list]

            if random.random() < 0.0:    
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
