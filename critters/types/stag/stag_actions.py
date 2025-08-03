import random
import math
from typing import Tuple, Optional, List
from ...actions import Action, ActionState
from ...world_state import WorldState


class WanderAction(Action):
    """Action for stag to wander to a random nearby location."""
    
    def __init__(self, max_wander_distance: int = 5):
        super().__init__("Wander", cost=2.0)
        self.max_wander_distance = max_wander_distance
        self.target_position: Optional[Tuple[int, int]] = None
        self.path = []
        self.path_index = 0
        self.movement_speed = 60.0
        self.last_movement_dir = (0, 0)
        
        self.add_effect('activity', 'wandering')
    
    def get_cost(self, world_state: WorldState, agent) -> float:
        return self.cost
    
    def is_valid(self, world_state: WorldState, agent) -> bool:
        current_pos = world_state.get('grid_position', (0, 0))
        energy = world_state.get('energy', 100)
        
        if energy < 20:
            return False
        
        self.target_position = self._find_wander_target(current_pos, agent)
        return self.target_position is not None
    
    def _find_wander_target(self, current_pos: Tuple[int, int], agent) -> Optional[Tuple[int, int]]:
        """Find a random walkable position within wander distance."""
        attempts = 0
        max_attempts = 20
        
        while attempts < max_attempts:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(2, self.max_wander_distance)
            
            dx = int(distance * math.cos(angle))
            dy = int(distance * math.sin(angle))
            
            target_x = current_pos[0] + dx
            target_y = current_pos[1] + dy
            
            if agent.map_interface.is_walkable(target_x, target_y):
                return (target_x, target_y)
            
            attempts += 1
        
        return None
    
    def start(self, agent) -> bool:
        if not super().start(agent):
            return False
        
        current_pos = agent.get_position()
        
        if self.target_position is None:
            self.state = ActionState.FAILURE
            return False
        
        self.path = agent.pathfinder.find_path(current_pos, self.target_position)
        
        if not self.path or len(self.path) < 2:
            self.state = ActionState.FAILURE
            return False
        
        self.path_index = 1
        self.last_movement_dir = (0, 0)
        
        if hasattr(agent, 'animation_system'):
            agent.animation_system.set_animation("walk")
        
        return True
    
    def update(self, agent, dt: float) -> ActionState:
        if self.state != ActionState.RUNNING:
            return self.state
        
        if self.path_index >= len(self.path):
            agent.set_position(self.target_position)
            if hasattr(agent, 'animation_system'):
                agent.animation_system.set_animation("idle")
            self.state = ActionState.SUCCESS
            return self.state
        
        current_world_pos = agent.get_world_position()
        target_grid = self.path[self.path_index]
        target_world_pos = agent.map_interface.grid_to_world(*target_grid)
        
        dx = target_world_pos[0] - current_world_pos[0]
        dy = target_world_pos[1] - current_world_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 8:
            self.path_index += 1
            agent.world_state.set('grid_position', target_grid)
            agent.world_state.set('world_position', target_world_pos)
        else:
            if distance > 0:
                move_x = (dx / distance) * self.movement_speed * dt
                move_y = (dy / distance) * self.movement_speed * dt
                new_pos = (current_world_pos[0] + move_x, current_world_pos[1] + move_y)
                agent.world_state.set('world_position', new_pos)
                
                new_grid_pos = agent.map_interface.world_to_grid(*new_pos)
                agent.world_state.set('grid_position', new_grid_pos)
                
                # Only update animation direction if movement direction changed significantly
                if hasattr(agent, 'animation_system'):
                    current_dir = (dx, dy)
                    if (abs(current_dir[0] - self.last_movement_dir[0]) > 0.1 or 
                        abs(current_dir[1] - self.last_movement_dir[1]) > 0.1):
                        direction = agent.animation_system.get_direction_from_movement(dx, dy)
                        agent.animation_system.set_animation("walk", direction)
                        self.last_movement_dir = current_dir
        
        current_energy = agent.world_state.get('energy', 100)
        energy_cost = 5 * dt
        new_energy = max(0, current_energy - energy_cost)
        agent.world_state.set('energy', new_energy)
        
        if new_energy < 30:
            agent.world_state.set('energy_low', True)
        else:
            agent.world_state.set('energy_low', False)
        
        return self.state


class FleeAction(Action):
    """Action for stag to flee from a threat at high speed."""
    
    def __init__(self, flee_distance: int = 8):
        super().__init__("Flee", cost=1.0)
        self.flee_distance = flee_distance
        self.target_position: Optional[Tuple[int, int]] = None
        self.threat_position: Optional[Tuple[int, int]] = None
        self.path = []
        self.path_index = 0
        self.movement_speed = 120.0
        self.last_movement_dir = (0, 0)
        
        self.add_effect('activity', 'fleeing')
    
    def get_cost(self, world_state: WorldState, agent) -> float:
        return self.cost
    
    def is_valid(self, world_state: WorldState, agent) -> bool:
        current_pos = world_state.get('grid_position', (0, 0))
        energy = world_state.get('energy', 100)
        
        if energy < 10:
            return False
        
        nearby_threats = self._detect_nearby_threats(current_pos, agent)
        if not nearby_threats:
            return False
        
        self.threat_position = nearby_threats[0]
        self.target_position = self._find_flee_target(current_pos, self.threat_position, agent)
        return self.target_position is not None
    
    def _detect_nearby_threats(self, current_pos: Tuple[int, int], agent) -> List[Tuple[int, int]]:
        """Simple threat detection - can be expanded later."""
        threats = []
        threat_range = 6
        
        for dx in range(-threat_range, threat_range + 1):
            for dy in range(-threat_range, threat_range + 1):
                check_x = current_pos[0] + dx
                check_y = current_pos[1] + dy
                
                if (abs(dx) + abs(dy) <= threat_range and 
                    agent.map_interface.is_valid_position(check_x, check_y)):
                    pass
        
        return threats
    
    def _find_flee_target(self, current_pos: Tuple[int, int], 
                         threat_pos: Tuple[int, int], agent) -> Optional[Tuple[int, int]]:
        """Find a position away from the threat."""
        threat_dx = current_pos[0] - threat_pos[0]
        threat_dy = current_pos[1] - threat_pos[1]
        
        if threat_dx == 0 and threat_dy == 0:
            threat_dx = random.choice([-1, 1])
            threat_dy = random.choice([-1, 1])
        
        flee_length = math.sqrt(threat_dx * threat_dx + threat_dy * threat_dy)
        if flee_length > 0:
            flee_dx = (threat_dx / flee_length) * self.flee_distance
            flee_dy = (threat_dy / flee_length) * self.flee_distance
        else:
            flee_dx = self.flee_distance
            flee_dy = 0
        
        target_x = int(current_pos[0] + flee_dx)
        target_y = int(current_pos[1] + flee_dy)
        
        if agent.map_interface.is_walkable(target_x, target_y):
            return (target_x, target_y)
        
        for offset in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            test_x = target_x + offset[0]
            test_y = target_y + offset[1]
            if agent.map_interface.is_walkable(test_x, test_y):
                return (test_x, test_y)
        
        return None
    
    def start(self, agent) -> bool:
        if not super().start(agent):
            return False
        
        current_pos = agent.get_position()
        
        if self.target_position is None:
            self.state = ActionState.FAILURE
            return False
        
        self.path = agent.pathfinder.find_path(current_pos, self.target_position)
        
        if not self.path or len(self.path) < 2:
            self.state = ActionState.FAILURE
            return False
        
        self.path_index = 1
        self.last_movement_dir = (0, 0)
        
        if hasattr(agent, 'animation_system'):
            agent.animation_system.set_animation("run")
        
        return True
    
    def update(self, agent, dt: float) -> ActionState:
        if self.state != ActionState.RUNNING:
            return self.state
        
        if self.path_index >= len(self.path):
            agent.set_position(self.target_position)
            if hasattr(agent, 'animation_system'):
                agent.animation_system.set_animation("idle")
            self.state = ActionState.SUCCESS
            return self.state
        
        current_world_pos = agent.get_world_position()
        target_grid = self.path[self.path_index]
        target_world_pos = agent.map_interface.grid_to_world(*target_grid)
        
        dx = target_world_pos[0] - current_world_pos[0]
        dy = target_world_pos[1] - current_world_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 8:
            self.path_index += 1
            agent.world_state.set('grid_position', target_grid)
            agent.world_state.set('world_position', target_world_pos)
        else:
            if distance > 0:
                move_x = (dx / distance) * self.movement_speed * dt
                move_y = (dy / distance) * self.movement_speed * dt
                new_pos = (current_world_pos[0] + move_x, current_world_pos[1] + move_y)
                agent.world_state.set('world_position', new_pos)
                
                new_grid_pos = agent.map_interface.world_to_grid(*new_pos)
                agent.world_state.set('grid_position', new_grid_pos)
                
                # Only update animation direction if movement direction changed significantly
                if hasattr(agent, 'animation_system'):
                    current_dir = (dx, dy)
                    if (abs(current_dir[0] - self.last_movement_dir[0]) > 0.1 or 
                        abs(current_dir[1] - self.last_movement_dir[1]) > 0.1):
                        direction = agent.animation_system.get_direction_from_movement(dx, dy)
                        agent.animation_system.set_animation("run", direction)
                        self.last_movement_dir = current_dir
        
        current_energy = agent.world_state.get('energy', 100)
        energy_cost = 15 * dt
        new_energy = max(0, current_energy - energy_cost)
        agent.world_state.set('energy', new_energy)
        
        if new_energy < 30:
            agent.world_state.set('energy_low', True)
        else:
            agent.world_state.set('energy_low', False)
        
        return self.state


class StagRestAction(Action):
    """Stag-specific rest action that restores energy and health."""
    
    def __init__(self, rest_duration: float = 4.0):
        super().__init__("StagRest", cost=0.5)
        self.duration = rest_duration
        
        self.add_precondition('energy_low', True)
        self.add_effect('energy_low', False)
        self.add_effect('activity', 'resting')
    
    def get_cost(self, world_state: WorldState, agent) -> float:
        return self.cost
    
    def is_valid(self, world_state: WorldState, agent) -> bool:
        return world_state.meets_conditions(self.preconditions)
    
    def start(self, agent) -> bool:
        if not super().start(agent):
            return False
        
        if hasattr(agent, 'animation_system'):
            agent.animation_system.set_animation("idle")
        
        return True
    
    def update(self, agent, dt: float) -> ActionState:
        if self.state != ActionState.RUNNING:
            return self.state
        
        self.start_time += dt
        
        current_energy = agent.world_state.get('energy', 0)
        current_health = agent.world_state.get('health', 100)
        
        energy_restore = 20 * dt
        health_restore = 5 * dt
        
        agent.world_state.set('energy', min(100, current_energy + energy_restore))
        agent.world_state.set('health', min(100, current_health + health_restore))
        
        new_energy = agent.world_state.get('energy', 0)
        if new_energy >= 80:
            agent.world_state.set('energy_low', False)
            agent.world_state.set('activity', 'idle')
        
        new_energy = agent.world_state.get('energy', 0)
        if new_energy >= 80:
            agent.world_state.set('energy_low', False)
        
        if self.start_time >= self.duration:
            self.state = ActionState.SUCCESS
        
        return self.state
    