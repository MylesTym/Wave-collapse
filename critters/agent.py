from typing import Dict, List, Any, Optional, Tuple
import pygame
from .world_state import WorldState
from .map_interface import WFCMapInterface
from .pathfinding import AStarPathfinder

class GOAPAgent:

    def __init__(self, agent_id: str, start_position: Tuple[int, int],
                 map_interface: WFCMapInterface, sprite_path: str = None):
        self.agent_id = agent_id
        self.map_interface = map_interface
        self.pathfinder = AStarPathfinder(map_interface)

        # World state
        self.world_state = WorldState()
        self._initialize_world_state(start_position)

        # Goap components
        self.available_actions = []
        self.goals = []
        self.current_goal = {}
        self.current_plan = []
        self.current_action = None

        # Planning
        self.replan_timer = 0.0
        self.replan_interval = 2.9
        self.planning_enabled = True

        # Rendering 
        self.sprite = None
        self.sprite_rect = pygame.Rect(0, 0, 32, 32)
        self.load_sprite(sprite_path)

        # Debug info
        self.debug_mode = False
        self.debug_info = {}
    
    def _initialize_world_state(self, start_position: Tuple[int, int]):
        # Initial values
        self.world_state.set('grid_position', start_position)
        world_pos = self.map_interface.grid_to_world(*start_position)
        self.world_state.set('world_position', world_pos)
        self.world_state.set('agent_id', self.agent_id)
        self.world_state.set('health', 100)
        self.world_state.set('energy', 100)
        self.world_state.set('is_busy', False)
        self.world_state.set('last_action_time', 0.0)
    
    def load_sprite(self, sprite_path: str = None):
        if sprite_path and pygame.get_init():
            try:
                self.sprite = pygame.image.load(sprite_path)
                self.sprite_rect = self.sprite.get_rect()
            except pygame.error:
                print(f"Warning: could not load sprite from {sprite_path}")
                self.sprite = None
        if self.sprite is None:
            if pygame.get_init():
                self.sprite = pygame.Surface((32, 32))
                self.sprite.fill((0, 255, 0))
                self.sprite_rect = self.sprite.get_rect()
    
    def add_action(self, action):
        if action not in self.available_actions:
            self.available_actions.append(action)
    
    def remove_action(self, action):
        if action in self.available_actions:
            self.available_actions.remove(action)
        
    def set_goals(self, goals: List[Dict[str, Any]]):
        self.goals = goals.copy()
        if goals and not self.current_goal:
            self.current_goal = goals[0]

    def add_goal(self, goal: Dict[str, Any]):
        if goal not in self.goals:
            self.goals.append(goal)

    def set_current_goal(self, goal: Dict[str, Any]):
        self.current_goal = goal
        self.current_plan = []
        self.current_action = None

    def update(self, dt: float):
        if not self.planning_enabled:
            return
        self.replan_timer += dt

        if self.current_action:
            self._update_current_action(dt)

        if self._should_replan():
            self._replan()
            self.replan_timer = 0.0

        if not self.current_action and self.current_plan:
            self._start_next_action()

        if self.debug_mode:
            self._update_debug_info()   

    def _update_current_action(self, dt: float):
        ## update currently executing action ## 
        pass

    def _should_replan(self) -> bool:
        if self.replan_timer >= self.replan_interval:
            return True

        if not self.current_plan:
            return True

        if self.current_action and hasattr(self.current_action, 'has_failed'):
            if self.current_action.has_failed():
                return True
        
        if self.current_goal and self.world_state.meets_conditions(self.current_goal):
            return True
        
        return False
    
    def _replan(self):
        ## New plan to acheive current goal ##

        if not self.current_goal or self.world_state.meets_conditions(self.current_goal):
            self._select_next_goal()
        
        if not self.current_goal:
            return
        
        self.current_plan = []
        self.current_action = None

        if self.debug_mode:
            print (f"Agent {self.agent_id}: Planning for goal {self.current_goal}")
    
    def _select_next_goal(self):
        if not self.goals:
            self.current_goal = {}
            return
        
        for goal in self.goals:
            if not self.world_state.meets_conditions(goal):
                self.current_goal = goal
                return
            
        self.current_goal = self.goals[0] if self.goals else {}
    
    def _start_next_action(self):
        if self.current_plan:
            self.current_action = self.current_plan.pop(0)

            if self.debug_mode:
                print(f"Agent {self.agent_id}: starting action {self.current_action}")
    
    def _update_debug_info(self):
        self.debug_info = {
            'position': self.world_state.get('grid_position'),
            'current_goal': self.current_goal,
            'plan_length': len(self.current_plan),
            'current_action': str(self.current_action) if self.current_action else None,
            'energy': self.world_state.get('energy'),
            'health': self.world_state.get('health')
        }

    def get_position(self) -> Tuple[int, int]:
        return self.world_state.get('grid_position', (0, 0))
    
    def get_world_position(self) -> Tuple[float, float]:
        return self.world_state.get('world_position', (0.0, 0.0))
    
    def set_position(self, grid_position: Tuple[int, int]):
        self.world_state.set('grid_position', grid_position)
        world_pos = self.map_interface.grid_to_world(*grid_position)
        self.world_state.set('world_position', world_pos)

    def can_reach_position(self, target_position: Tuple[int, int]) -> bool:
        current_pos = self.get_position()
        path = self.pathfinder.find_path(current_pos, target_position)
        return len(path) > 0
    
    def get_distance_to(self, target_position: Tuple[int, int]) -> float:
        current_pos = self.get_position()
        return abs(current_pos[0] - target_position[0]) + abs(current_pos[1] - target_position[1])
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int ,int] = (0, 0)):
        if not self.sprite:
            return
        world_pos = self.get_world_position()
        screen_x = int(world_pos[0] - camera_offset[0])
        screen_y = int(world_pos[1] - camera_offset[1])

        self.sprite_rect.centerx = screen_x
        self.sprite_rect.centery = screen_y
        screen.blit(self.sprite, self.sprite_rect)

        if self.debug_mode:
            self._render_debug_info(screen, camera_offset)

    def _render_debug_info(self, screen: pygame.Surface, camera_offset: Tuple[int, int]):
        if not pygame.font.get_init():
            return
        
        font = pygame.font.Font(None, 20)
        world_pos = self.get_world_position()
        text_x = int(world_pos[0] - camera_offset[0])
        text_y = int(world_pos[1] - camera_offset[1] - 40)

        if self.current_action:
            text = font.render(str(self.current_action), True, (255, 255, 255))
            screen.blit(text, (text_x - text.get_width() // 2, text_y))
            text_y -= 20

        if self.current_goal:
            goal_text = f"Goal: {list(self.current_goal.keys())[0] if self.current_goal else 'None'}"
            text = font.render(goal_text, True, (255, 255, 0))
            screen.blit(text, (text_x - text.get_width() // 2, text_y))

    def enable_debug(self, enabled: bool = True):
        self.debug_mode = enabled
    
    def get_debug_info(self) -> Dict[str, Any]:
        return self.debug_info.copy()
    
    def pause_planning(self):
        self.planning_enabled = False
    
    def resume_planning(self):
        self.planning_enabled = True
    
    def force_replan(self):
        self.replan_timer = self.replan_interval

    def __str__(self) -> str:
        pos = self.get_position()
        return f"Agent({self.agent_id}) at {pos}"
    
    def __repr__(self) -> str:
        return f"GOAPAgent(id='{self.agent_id}', pos ={self.get_position()}, goal={self.current_goal})"