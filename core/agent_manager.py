from typing import List, Tuple, Optional
from critters import GOAPAgent

class AgentManager:
    def __init__(self):
        self.agents = []
    
    def register_agent(self, agent):
        if agent not in self.agents:
            self.agents.append(agent)
    
    def unregister_agent(self, agent):
        if agent in self.agents:
            self.agents.remove(agent)
    
    def get_all_agents(self) -> List[GOAPAgent]:
        return self.agents.copy()
    
    def get_agents_in_range(self, position: Tuple[int, int], range_distance: int, exclude_agent=None) -> List[GOAPAgent]:
        nearby_agents = []
        for agent in self.agents:
            if agent == exclude_agent:
                continue
            try:
                agent_pos = agent.get_position()
                if agent_pos is None:
                    continue
                distance = abs(position[0] - agent_pos[0]) + abs(position[1] - agent_pos[1])  # Manhattan distance
                if distance <= range_distance:
                    nearby_agents.append(agent)
            except (AttributeError, TypeError):
                continue
            return nearby_agents
    
    def get_agents_in_range_by_species(self, position: Tuple[int, int], range_distance: int, species: str, exclude_agent=None) -> List[GOAPAgent]:
        nearby_agents = self.get_agents_in_range(position, range_distance, exclude_agent)
        filtered_agents = []

        for agent in nearby_agents:
            try: 
                if agent.world_state and agent.world_state.get('species') == species:
                    filtered_agents.append(agent)
            except (ArithmeticError, TypeError):

                continue
        return filtered_agents