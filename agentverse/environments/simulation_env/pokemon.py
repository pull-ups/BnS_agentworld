import asyncio
import datetime
import random
import json
from typing import Any, Dict, List, Optional, Set

# from agentverse.agents.agent import Agent
from agentverse.agents.simulation_agent.conversation import BaseAgent
from agentverse.logging import logger

# from agentverse.environments.simulation_env.rules.base import Rule
from agentverse.environments.simulation_env.rules.base import SimulationRule as Rule
from agentverse.message import Message

from .. import env_registry as EnvironmentRegistry
from ..base import BaseEnvironment

def serialize_tuple_list(tuple_list):
    flat_list = []
    for tup in tuple_list:
        flat_list.extend(tup)
    return flat_list


def get_message_with_idx(self, messages, idx):
    for message in messages:
        if message.sender==self.agents[idx].name:
            return message
        


def get_already_in_conversation_pair(self):
    # Message(content='{"to": "Bike Store", "action": "MoveTo"}', sender='May', receiver={'Birch', 'May'}, sender_agent=None, tool_response=[]), 
    # Message(content='{"to": "Park", "action": "MoveTo"}', sender='Birch', receiver={'Birch', 'May'}, sender_agent=None, tool_response=[]), 
    # Message(content='{"to": "Maxie", "text": "Hi Maxie,  I am Steven. How are you?", "action": "Conversation", "speaking": "True"}', sender='Steven', receiver={'Steven', 'Maxie'}, sender_agent=None, tool_response=[]), 
    # Message(content='{"to": "Steven", "text": "", "action": "Conversation", "speaking": "False"}', sender='Maxie', receiver={'Steven', 'Maxie'}, sender_agent=None, tool_response=[])]
    agent_to_idx = {agent.name: i for i, agent in enumerate(self.agents)}
    
    conversation_pairs = set()    
    already_in_conversation_agent_ids_pair=[]
    for message in self.last_messages:
        if message.content != None:
            message_content=json.loads(message.content)
            if message_content["action"]=="Conversation":
                #import pdb; pdb.set_trace()
                speaker=message.sender
                speaker_idx=agent_to_idx[speaker]
                listener=message_content["to"]
                listener_idx=agent_to_idx[listener]
                conversation_pairs=tuple(sorted([speaker_idx, listener_idx]))
                if conversation_pairs not in already_in_conversation_agent_ids_pair:
                    already_in_conversation_agent_ids_pair.append(conversation_pairs)
    return already_in_conversation_agent_ids_pair


def get_conversation_pair(environment, nearbyNPCs, already_in_conversation_agent_ids_pair, prob=1.0):
    #주변 npc중에서 대화중이지 않은 npc들을 뽑아서 대화시키기
    already_in_conversation_agent_ids=serialize_tuple_list(already_in_conversation_agent_ids_pair)
    
    agent_to_idx = {agent.name: i for i, agent in enumerate(environment.agents)}
    temp=[]
    for i in range(len(nearbyNPCs)):
        temp.append([agent_to_idx[_] for _ in nearbyNPCs[i]])
    nearbyNPCs=temp
    
    adj_matrix = [[0 for i in range(len(nearbyNPCs))] for j in range(len(nearbyNPCs))]
    for i in range(len(nearbyNPCs)):
        for j in nearbyNPCs[i]:
            adj_matrix[i][j]=1
       
    """
    Finds pairs of NPCs engaged in conversation based on the adjacency matrix and a probability.
    
    :param adj_matrix: A 4x4 matrix where adj_matrix[i][j] == 1 indicates that NPCs i and j are together.
    :param prob: Probability of engaging in a conversation when together.
    :return: A list of pairs (tuples) indicating which NPCs are engaged in conversation.
    """
    num_npcs = len(adj_matrix)
    conversations = []

    # Find NPCs that are together
    for i in range(num_npcs):
        for j in range(i + 1, num_npcs):
            if adj_matrix[i][j] == 1:
                # Check if either NPC is already engaged in a conversation
                already_in_convo = any(i in pair or j in pair for pair in conversations)
                already_in_convo_previous_turn = i in already_in_conversation_agent_ids or j in already_in_conversation_agent_ids
                if not already_in_convo and not already_in_convo_previous_turn and random.random() < prob:
                    conversations.append((i, j))

    return conversations

def switch_values(input_value, value_pair):
    if input_value == value_pair[0]:
        return value_pair[1]
    elif input_value == value_pair[1]:
        return value_pair[0]
    else:
        return "Invalid input"


@EnvironmentRegistry.register("pokemon")
class PokemonEnvironment(BaseEnvironment):
    """
    An environment for Pokémon demo.

    Args:
        agents: List of agents
        locations: A dict of locations to agents within them
        rule: Rule for the environment
        max_turns: Maximum number of turns
        cnt_turn: Current turn number
        last_messages: Messages from last turn
        rule_params: Variables set by the rule
    """

    agents: List[BaseAgent]
    #sngwon
    #locations_to_agents: Dict[str, Set[str]]
    locations_to_agents: Dict[str, Optional[Set[str]]]
    #/sngwon
    # locations_descriptions: Dict[str, str]
    time: datetime.datetime = datetime.datetime(2021, 1, 1, 8, 0, 0)
    rule: Rule
    max_turns: int = 10
    cnt_turn: int = 0
    last_messages: List[Message] = []
    rule_params: Dict = {}

    def __init__(self, rule, locations, **kwargs):
        rule_config = rule
        order_config = rule_config.get("order", {"type": "sequential"})
        visibility_config = rule_config.get("visibility", {"type": "all"})
        selector_config = rule_config.get("selector", {"type": "basic"})
        updater_config = rule_config.get("updater", {"type": "basic"})
        describer_config = rule_config.get("describer", {"type": "basic"})
        rule = Rule(
            order_config,
            visibility_config,
            selector_config,
            updater_config,
            describer_config,
        )
        locations_to_agents = {}
        # locations_descriptions = {}
        locations_config = locations
        for loc in locations_config:
            #sngwon
            #locations_to_agents[loc["name"]] = set(loc["init_agents"])
            
            if loc["init_agents"]==[None]:
                locations_to_agents[loc["name"]] = set()
            else:
                locations_to_agents[loc["name"]] = set(loc["init_agents"])
            #/sngwon
            # locations_descriptions[loc["name"]] = loc["description"]
        super().__init__(
            rule=rule,
            locations_to_agents=locations_to_agents,
            # locations_descriptions=locations_descriptions,
            **kwargs,
        )

    async def step(
        self,
        is_player: bool = False,
        player_content: str = None,
        receiver: str = None,
        receiver_id: Optional[int] = None,
        agent_ids: Optional[List[int]] = None,
        llm: str = None,
        model_dict: Optional[List[Any]] = None,
    ) -> List[Message]:
        """Run one step of the environment"""

        # Get the next agent index
        # time.sleep(8)
        # return [Message(content="Test", sender="May", receiver=["May"])]
        if llm is not None:
            if is_player:
                return await self._respond_to_player_local(player_content, receiver, receiver_id)
            else:
                return await self._routine_step_local(agent_ids)
        else:
            if is_player:
                return await self._respond_to_player(player_content, receiver, receiver_id)
            else:
                return await self._routine_step(agent_ids)


    async def _routine_step_local(self, agent_ids) -> List[Message]:
        #sngwonprint
        # print("last message")
        # print(self.last_messages)
        
        
        self.rule.update_visible_agents(self)
        env_descriptions = self.rule.get_env_description(self)
        nearbyNPCs=self.rule.get_nearbyNPCs(self)
        
        # agent_ids = self.rule.get_next_agent_idx(self)

        # Generate current environment description
        
        #[(0, 1), (2, 3)]
        #대화중이었던 사람들
        already_in_conversation_agent_ids_pair=get_already_in_conversation_pair(self)
        
        #대화를 시작하는 사람들
        conversation_start_agent_ids_pair=get_conversation_pair(self, nearbyNPCs, already_in_conversation_agent_ids_pair, prob=0.5)
        # print("already_conversation" , already_in_conversation_agent_ids_pair)
        # print("start_conversation", conversation_start_agent_ids_pair)        
        
        
        #conversation_info={"doing_conversation":False}
        #conversation_info={"doing_conversation":True, "to": Birch, "speaker": True, "listener": False}
        conversation_infos=[{"doing_conversation":False} for i in range(len(self.agents))]
        
        #1. 기존에 대화중인 애들 정보 업대이트
        for conversation_pair in already_in_conversation_agent_ids_pair:
            conversation_idx_1, conversation_idx_2 =conversation_pair[0], conversation_pair[1]
            last_message_1, last_message_2 = get_message_with_idx(self, self.last_messages, conversation_idx_1), get_message_with_idx(self, self.last_messages, conversation_idx_2)
            
            # Message(content='{"to": "Steven",
            #                   "text": "Hi Steven,  I am May. How are you?",
            #                   "action": "Conversation",
            #                   "speaking": "True"}', sender='May', receiver={'Steven', 'May'}, sender_agent=None, tool_response=[])
            for (agent_idx, message) in [(conversation_idx_1, last_message_1), (conversation_idx_2, last_message_2)]:
                message_content=json.loads(message.content)
                conversation_infos[agent_idx]["doing_conversation"]=True
                conversation_infos[agent_idx]["to"]=message_content["to"]

                if message_content["speaking"]=="True":
                    conversation_infos[agent_idx]["speaker"]=False
                elif message_content["speaking"]=="False":
                    conversation_infos[agent_idx]["speaker"]=True
                else:
                    print("Invalid speaking value")

        #2. 지금 대화를 시작하는 애들 정보 업데이트
            
        
        for conversation_pair in conversation_start_agent_ids_pair:
            #대화 턴 설정!!
            dialog_turn=random.randint(4,6)
            
            
            counterpart_idx=switch_values(agent_idx, conversation_pair)
            if agent_idx in conversation_pair:
                conversation_infos[agent_idx]["doing_conversation"]=True
                conversation_infos[agent_idx]["to"]=self.agents[counterpart_idx].name
                conversation_infos[agent_idx]["conversation_turn_last"]=dialog_turn
                if agent_idx < counterpart_idx:
                    #자기가 번호가 낮으면 speaker
                    conversation_infos[agent_idx]["speaker"]=True
                    conversation_infos[agent_idx]["listener"]=False
                else:
                    conversation_infos[agent_idx]["speaker"]=False
                    conversation_infos[agent_idx]["listener"]=True




        # info_from_envs={
        #     "env_descriptions":env_descriptions,
        #     "nearbyNPCs":nearbyNPCs
        #     "conversation":
        # }
        info_from_envs=[{"env_description":env_descriptions[i],"nearbyNPCs":nearbyNPCs[i], "conversation_info": conversation_infos[i]} for i in range(len(env_descriptions))]

        # Generate the next message
        messages = await asyncio.gather(
            
            # *[self.agents[i].astep_local(env_descriptions[i]) for i in agent_ids]
            *[self.agents[i].astep_local(info_from_envs[i]) for i in agent_ids]
        )

        # messages = self.get_test_messages()

        # Some rules will select certain messages from all the messages
        selected_messages = self.rule.select_message(self, messages)

        # Update the memory of the agents
        self.last_messages = selected_messages
        self.rule.update_memory(self)
        self.print_messages(selected_messages)

        self.cnt_turn += 1
        self.time += datetime.timedelta(minutes=5)

        return selected_messages


    async def _routine_step(self, agent_ids) -> List[Message]:
        self.rule.update_visible_agents(self)

        # agent_ids = self.rule.get_next_agent_idx(self)

        # Generate current environment description
        env_descriptions = self.rule.get_env_description(self)

        # Generate the next message
        messages = await asyncio.gather(
            *[self.agents[i].astep(env_descriptions[i]) for i in agent_ids]
        )
        # messages = self.get_test_messages()

        # Some rules will select certain messages from all the messages
        selected_messages = self.rule.select_message(self, messages)

        # Update the memory of the agents
        self.last_messages = selected_messages
        self.rule.update_memory(self)
        self.print_messages(selected_messages)

        self.cnt_turn += 1
        self.time += datetime.timedelta(minutes=5)

        return selected_messages

    async def _respond_to_player(
        self,
        player_content: str = None,
        receiver: str = None,
        receiver_id: Optional[int] = None,
    ) -> List[Message]:
        if receiver_id is None:
            for agent in self.agents:
                if agent.name == receiver:
                    receiver_id = agent.agent_id
                    break
        agent_ids = [receiver_id]
        agent_name = receiver
        player_message = Message(
            sender="Brenden", content=player_content, receiver=[agent_name]
        )

        # Update the set of visible agents for each agent
        self.rule.update_visible_agents(self)

        # Generate current environment description
        env_descriptions = self.rule.get_env_description(self, player_content)

        # Generate the next message
        messages = await asyncio.gather(
            *[self.agents[i].astep(env_descriptions[i]) for i in agent_ids]
        )

        # Some rules will select certain messages from all the messages
        # selected_messages = self.rule.select_message(self, messages)

        # Update the memory of the agents
        self.last_messages = [player_message, *messages]
        self.rule.update_memory(self)
        self.print_messages(messages)

        self.cnt_turn += 1

        return messages

    def update_state(self, agent_location: Dict[str, str]):
        for agent_name, location in agent_location.items():
            # original_location = self.get_agent_to_location()[agent_name]
            # self.locations_to_agents[original_location].remove(agent_name)
            self.locations_to_agents[location].add(agent_name)

    def get_agent_to_location(self) -> Dict[str, str]:
        ret = {}
        for location, agent_names in self.locations_to_agents.items():
            for agent in agent_names:
                ret[agent] = location
        return ret

    def print_messages(self, messages: List[Message]) -> None:
        for message in messages:
            if message is not None:
                logger.info(f"{message.sender}: {message.content}")

    def reset(self) -> None:
        """Reset the environment"""
        self.cnt_turn = 0
        self.rule.reset()
        for agent in self.agents:
            agent.reset()

    def is_done(self) -> bool:
        """Check if the environment is done"""
        return self.cnt_turn >= self.max_turns

    def get_test_messages(self) -> List[Message]:
        messages = [
            Message(
                content='{"to": "Birch", "action": "Speak", "text": "Hi!!!"}',
                sender="May",
                receiver={"May", "Birch"},
                tool_response=[],
            ),
            Message(
                content='{"to": "May", "text": "Good morning, May! How is your research going?", "action": "Speak"}',
                sender="Birch",
                receiver={"May", "Birch"},
                tool_response=[],
            ),
            Message(
                content='{"to": "Pokémon Center", "action": "MoveTo"}',
                sender="Steven",
                receiver={"Steven"},
                tool_response=[],
            ),
            Message(
                content='{"to": "Shop", "last_time": "10 minutes", "action": "MoveTo"}',
                sender="Maxie",
                receiver={"Maxie"},
                tool_response=[],
            ),
            Message(
                content='{"to": "Pok\\u00e9mon Center", "action": "MoveTo"}',
                sender="Archie",
                receiver={"Archie"},
                tool_response=[],
            ),
            Message(
                content='{"to": "Shop", "action": "MoveTo"}',
                sender="Joseph",
                receiver={"Joseph"},
                tool_response=[],
            ),
        ]
        return messages
