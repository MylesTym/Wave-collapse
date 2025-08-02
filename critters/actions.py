from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import math
from .world_state import WorldState

class ActionState(Enum):
    INACTIVE = 0
    RUNNING = 1
    SUCCESS = 2
    FAILURE = 3

class Action:

    def __init__(self, name: str, cost: float = 1.0):
        self.name = name
        self.cost = cost
        self.state = ActionState.INACTIVE

        self.preconditions: Dict[str, Any] = {}
        self.effects: Dict[str, Any] = {}

        self.start_time = 0.0
        self.duration = 0.0
    
    def set_preconditions(self, conditions: Dict[str, Any]) -> 'Action':
        self.preconditions = conditions.copy()
        return self
    
    def set_effects(self, effects: Dict[str, Any]) -> 'Action':
        self.effects = effects.copy()
        return self
    
    def add_precondition(self, key: str, value: Any) -> 'Action':
        self.preconditions[key] = value
        return self
    
    def add_effect(self, key: str, value: Any) -> 'Action':
        self.effects[key] = value
        return self
    
    def is_valid(self, world_state: WorldState, agent) -> bool:
        return world_state.meets_conditions(self.preconditions)
    
    def get_cost(self, world_state: WorldState, agent) -> float:
        return self.cost
    
    def start(self, agent) -> bool:
        if not self.is_valid(agent.world_state, agent):
            self.state = ActionState.FAILURE
            return False
        
        self.state = ActionState.RUNNING
        self.start_time = 0.0
        return True
    
    def update(self, agent, dt: float) -> ActionState:
        if self.state != ActionState.RUNNING:
            return self.state
        self.start_time += dt

        if self.duration > 0:
            if self.start_time >= self.duration:
                self._apply_effects(agent)
                self.state = ActionState.SUCCESS
        else:
            self._apply_effects(agent)
            self.state = ActionState.SUCCESS

            return self.state

    def stop(self, agent):
        self.state = ActionState.INACTIVE

    def _apply_effects(self, agent):
        for key, value in self.effects.items():
            agent.world_state.set(key, value)
        
    def has_failed(self) -> bool:
        return self.state == ActionState.FAILURE
    
    def is_complete(self) -> bool:
        return self.state == ActionState.SUCCESS
    
    def is_running(self) -> bool:
        return self.state == ActionState.RUNNING
    
    def get_progress(self) -> float:
        if self.duration <= 0:
            return 1.0 if self.state == ActionState.SUCCESS else 0.0
        
        if self.state == ActionState.SUCCESS:
            return 1.0
        elif self.state == ActionState.RUNNING:
            return min(self.start_time / self.duration, 1.0)
        else: 
            return 0.0
        
    def reset(self):
        self.state = ActionState.INACTIVE
        self.start_time = 0.0

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Action('{self.name}', cost={self.cost}, state={self.state.name})"
    

class MoveToAction(Action):

    def __init__(self, target_position: Tuple[int, int], movement_speed: float = 100.0):
        super().__init__(f"MoveTo_{target_position}")
        self.target_position = target_position
        self.movement_speed = movement_speed
        self.path = []
        self.path_index = 0

        self.add_effect('grid_position', target_position)
    
    def get_cost(self, world_state: WorldState, agent) -> float:
        current_pos = world_state.get('grid_position', (0, 0))
        distance = abs(current_pos[0] - self.target_position[0]) + abs(current_pos[1] - self.target_position[1])
        return distance * 1.0
    
    def is_valid(self, world_state: WorldState, agent) -> bool:
        current_pos = world_state.get('grid_position', (0, 0))

        if current_pos == self.target_position:
            return False
        
        if not agent.map_interface.is_walkable(*self.target_position):
            return False
        
        return agent.can_reach_position(self.target_position)
    
    def start(self, agent) -> bool:
        if not super().start(agent):
            return False
        
        current_pos = agent.get_position()
        self.path = agent.pathfinder.find_path(current_pos, self.target_position)

        if not self.path:
            self.state = ActionState.FAILURE
            return False
        
        self.path_index = 1
        return True
    
    def update(self, agent, dt: float) -> ActionState:
        if self.state != ActionState.RUNNING:
            return self.state
        if self.path_index >= len(self.path):
            agent.set_position(self.target_position)
            self.state = ActionState.SUCCESS
            return self.state
        
        current_world_pos = agent.get_world_position()
        target_grid = self.path[self.path_index]
        target_world_pos = agent.map_interface.grid_to_world(*target_grid)

        dx = target_world_pos[0] - current_world_pos[0]
        dy = target_world_pos[1] - current_world_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 5:
            self.path_index += 1
            agent.world_state.set('grid_position', target_grid)
        
        else: 
            if distance > 0:
                move_x = (dx / distance) * self.movement_speed * dt
                move_y = (dy / distance) * self.movement_speed * dt
                new_pos = (current_world_pos[0] + move_x, current_world_pos[1] + move_y)
                agent.world_state.set('world_position', new_pos)

        return self.state

class HarvestResourceAction(Action):

    def __init__(self, resource_type: str, resource_position: Tuple[int, int], harvest_time: float = 3.0):
        super().__init__(f"Harvest_{resource_type}", cost=3.0)
        self.resource_type = resource_type
        self.resource_position = resource_position
        self.duration = harvest_time

        self.add_precondition('grid_position', resource_position)
        self.add_effect(f'has_{resource_type}', True)
        self.add_effect(f'{resource_type}_count', 1)

    def is_valid(self, world_state: WorldState, agent) -> bool:
        if not super().is_valid(world_state, agent):
            return False
        
        return agent.map_interface.has_resource(*self.resource_position, self.resource_type)

    def _apply_effects(self, agent):
        for key, value in self.effects.items():
            if key.endswith('_count'):
                current = agent.world_state.get(key, 0)
                agent.world_state.set(key, current + value)
            else:
                agent.world_state.set(key, value)

class RestAction(Action):

    def __init__(self, rest_time: float = 5.0):
        super().__init__("Rest", cost=1.0)
        self.duration = rest_time
        self.add_precondition('energy_low', True)

        self.add_effect('energy', 100)
        self.add_effect('energy_low', False)

class IdleAction(Action):
    def __init__(self, idle_time: float = 1.0):
        super().__init__("Idle", cost=0.1)
        self.duration = idle_time

    def is_valid(self, world_state: WorldState, agent) -> bool:
        return True
    
class WorkAction(Action):

    def __init__(self, work_type: str, work_time: float = 10.0, energy_cost: int = 20):
        super().__init__(f"Work_{work_type}", cost=5.0)
        self.work_type = work_type
        self.duration = work_time
        self.energy_cost = energy_cost

        self.add_precondition('energy_low', False)

        self.add_effect(f'{work_type}_work_done', True)
    
    def _apply_effects(self, agent):
        super()._apply_effects(agent)

        current_energy = agent.world_state.get('energy', 100)
        new_energy = max(0, current_energy - self.energy_cost)
        agent.world_state.set('energy', new_energy)

        if new_energy < 30:
            agent.world_state.set('energy_low', True)

class ConsumeItemAction(Action):
    def __init__(self, item_type: str, effect_key: str, effect_value: Any):
        super().__init__(f"Consume_{item_type}", cost=1.0)
        self.item_type = item_type

        self.add_precondition(f'has_{item_type}', True)

        self.add_effect(f'has_{item_type}', False)
        self.add_effect(effect_key, effect_value)

    def _apply_effects(self, agent):
        count_key = f'{self.item_type}_count'
        current_count = agent.world_state.get(count_key, 0)
        new_count = max(0, current_count - 1)
        agent.world_state.set(count_key, new_count)

        has_item = new_count > 0
        agent.world_state.set(f'has_{self.item_type}', has_item)

        for key, value in self.effects.items():
            if not key.startswith('has_'):
                agent.world_state.set(key, value)

    
# Utility functions for creating common actions

def create_movement_action(target: Tuple[int, int], speed: float = 100.0) -> MoveToAction:
    """Create a movement action to a specific position."""
    return MoveToAction(target, speed)

def create_harvest_action(resource_type: str, position: Tuple[int, int], time: float = 3.0) -> HarvestResourceAction:
    """Create a harvest action for a specific resource."""
    return HarvestResourceAction(resource_type, position, time)

def create_work_action(work_type: str, time: float = 10.0, energy_cost: int = 20) -> WorkAction:
    """Create a work action of a specific type."""
    return WorkAction(work_type, time, energy_cost)

def create_rest_action(time: float = 5.0) -> RestAction:
    """Create a rest action."""
    return RestAction(time)

def create_consume_action(item: str, effect_key: str, effect_value: Any) -> ConsumeItemAction:
    """Create a consume item action."""
    return ConsumeItemAction(item, effect_key, effect_value)