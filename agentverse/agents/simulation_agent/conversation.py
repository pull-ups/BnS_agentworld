from __future__ import annotations
from colorama import Fore
import random
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


@agent_registry.register("conversation")
class ConversationAgent(BaseAgent):
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
        # print("==in agents/simulation_agent/conversation.py, prompt==")
        # print(prompt)
        # print("===============")
        parsed_response = None
        for i in range(self.max_retry):
            try:
                # if self.name == "Code Reviewer":
                #logger.debug(prompt, "Prompt", Fore.CYAN)
                response = await self.llm.agenerate_response(prompt)
                # print("==in agents/simulation_agent/conversation.py, response==")
                # print(response)
                # print("===============")
                # logging.info(f"{self.name}'s request result:"
                #              f" {response.content}")
                parsed_response = self.output_parser.parse(response)
                
                
                
                print("==in agents/simulation_agent/conversation.py, response==")
                print(response)
                print(type(response))
                print("===============")  
                print("==in agents/simulation_agent/conversation.py, parsed_response==")
                print(parsed_response)
                print(type(parsed_response))
                print("===============")
                
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
        print("==in agents/simulation_agent/conversation.py, message==")
        print(message)
        print(type(message))
        print("===============")
        return message

    async def astep_local(self, env_description: str = "") -> Message:
        print("sngwon, astep_local==")
        """Asynchronous version of step"""
        prompt = self._fill_prompt_template(env_description)
        

        response = await self.llm.agenerate_response_local(prompt)
        print("==in agents/simulation_agent/conversation.py, response==")
        print(response)
        print("==============")
        
        arr=['{"to": "Shop", "action": "MoveTo"}', '{"to": "Bike Store", "action": "MoveTo"}', '{"to": "Park", "action": "MoveTo"}']
        
        
        content_from_local=random.choice(arr)
        message = Message(
            content=content_from_local,
            sender=self.name,
            receiver=self.get_receiver(),
        )
        print("==in agents/simulation_agent/conversation.py, message==")
        print(message)
        print(type(message))
        print("===============")
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
