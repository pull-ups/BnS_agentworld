from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Dict
from copy import deepcopy

from . import describer_registry as DescriberRegistry
from .base import BaseDescriber

if TYPE_CHECKING:
    from agentverse.environments.pokemon import PokemonEnvironment


@DescriberRegistry.register("pokemon")
class PokemonDescriber(BaseDescriber):
    def get_env_description(
        self,
        environment: PokemonEnvironment,
        player_content: str = "",
    ) -> List[str]:
        time = environment.time
        if player_content == "":
            agent_to_location = environment.get_agent_to_location()
            descriptions = []
            for agent in environment.agents:
                description = ""
                if agent.name not in agent_to_location:
                    # Agent is on the way to a location
                    descriptions.append("")
                    continue
                location = agent_to_location[agent.name]
                agents_in_same_loc = deepcopy(environment.locations_to_agents[location])
                agents_in_same_loc.remove(agent.name)
                agents_in_same_loc = list(agents_in_same_loc)
                description += f"It is now {time}. You are at {location}."
                if len(agents_in_same_loc) == 0:
                    description += " There is no one else here."
                elif len(agents_in_same_loc) == 1:
                    description += f" {agents_in_same_loc[0]} is also here."
                else:
                    other_agents = ", ".join(agents_in_same_loc)
                    description += f" {other_agents} are also here."
                # description += " The locations you can go to include: \n"
                # for loc, dsec in environment.locations_descriptions.items():
                #     description += f"{loc}: {dsec}\n"
                descriptions.append(description)
            return descriptions
        else:
            description = ""
            description += f"It is now {time}. Brendan is talking to you.\n"
            description += f"[Brendan]: {player_content}\n"
            return [description for _ in range(len(environment.agents))]
    
    def get_nearbyNPCs(
        self,
        environment: PokemonEnvironment,
    ) -> List[str]:
        agent_to_idx = {agent.name: i for i, agent in enumerate(environment.agents)}
        agent_to_location = environment.get_agent_to_location()
        agents_in_same_loc_arr=[]
        for agent in environment.agents:
            agents_in_same_loc = []
            if agent.name not in agent_to_location:
                # Agent is on the way to a location
                agents_in_same_loc_arr.append([])
                continue
            location = agent_to_location[agent.name]
            agents_in_same_loc = deepcopy(environment.locations_to_agents[location])
            agents_in_same_loc.remove(agent.name)
            agents_in_same_loc = list(agents_in_same_loc)
            
            agents_in_same_loc_arr.append(agents_in_same_loc)
            #agents_in_same_loc_arr.append([agent_to_idx[i] for i in agents_in_same_loc])
        return agents_in_same_loc_arr
                    