import pygame
from typing import Tuple
from ...agent import GOAPAgent
from ...animation import AnimationSystem
from ...planner import GOAPPlanner
from ...actions import ActionState


class StagAgent(GOAPAgent):
    
    def __init__(self, start_position: Tuple[int, int], map_interface, agent_manager, terrain_data, asset_path: str = "assets"):
        super().__init__(f"stag_{start_position[0]}_{start_position[1]}", start_position, map_interface, agent_manager, asset_path)
        
        self.terrain_data = terrain_data
        self.animation_system = AnimationSystem("stag", asset_path)
        self.planner = GOAPPlanner()
        
        self._initialize_stag_state()
        self._setup_stag_actions()
        self._setup_stag_goals()
    
    def _initialize_stag_state(self):
        self.world_state.set('energy', 100)
        self.world_state.set('energy_low', False)
        self.world_state.set('health', 100)
        self.world_state.set('awareness', 100)
        self.world_state.set('activity', 'idle')
        self.world_state.set('threatened', False)
        self.world_state.set('species', 'stag')
    
    def _setup_stag_actions(self):
        from .stag_actions import WanderAction, FleeAction, StagRestAction, GuardAction
        
        self.add_action(WanderAction(max_wander_distance=15))
        self.add_action(StagRestAction(rest_duration=5.0))
        self.add_action(FleeAction(flee_distance=10))
        self.add_action(GuardAction(guard_duration=3.0))
    
    def _setup_stag_goals(self):
        goals = [
            {'activity': 'wandering'},
            {'energy_low': False},
            {'threatened': False}
        ]
        self.set_goals(goals)
        
        if goals:
            self.current_goal = goals[0]
    
    def _update_current_action(self, dt: float):
        if not self.current_action:
            return
        
        from ...actions import ActionState
        action_state = self.current_action.update(self, dt)
        
        if action_state == ActionState.SUCCESS:
            print(f"Action {self.current_action.name} completed successfully")
            if self.current_plan and self.current_plan[0] == self.current_action:
                self.current_plan.pop(0)
            self.current_action = None
        elif action_state == ActionState.FAILURE:
            print(f"Action {self.current_action.name} failed")
            self.current_plan = []
            self.current_action = None
    
    def _replan(self):
        # Always check for goal changes first
        self._select_next_goal()
        
        if not self.current_goal:
            return
        
        print(f"Current world state: {dict(self.world_state.items())}")
        print(f"Selected goal: {self.current_goal}")
        print(f"Available actions: {[a.name for a in self.available_actions]}")
        
        # Test each action validity
        for action in self.available_actions:
            valid = action.is_valid(self.world_state, self)
            print(f"Action {action.name} valid: {valid}")
        
        # Test if actions can achieve the goal directly
        for action in self.available_actions:
            if action.is_valid(self.world_state, self):
                print(f"Valid action {action.name}:")
                print(f"  Preconditions: {action.preconditions}")
                print(f"  Effects: {action.effects}")
                
                # Check if effects match goal
                goal_met = True
                for goal_key, goal_value in self.current_goal.items():
                    if goal_key not in action.effects or action.effects[goal_key] != goal_value:
                        goal_met = False
                        break
                print(f"  Can achieve goal: {goal_met}")
        
        self.current_plan = self.planner.plan(
            self.world_state,
            self.current_goal,
            self.available_actions,
            self
        )
        self.current_action = None
        
        print(f"Stag {self.agent_id}: Planning for goal {self.current_goal}")
        print(f"Plan: {[action.name for action in self.current_plan]}")
    
    def _select_next_goal(self):
        threatened = self.world_state.get('threatened', False)
        energy_low = self.world_state.get('energy_low', False)
        current_activity = self.world_state.get('activity', 'idle')
        
        if threatened:
            self.current_goal = {'threatened': False}
            print(f"Threatened, setting guard goal: {self.current_goal}")
        elif energy_low:
            self.current_goal = {'energy_low': False}
            print(f"Energy is low, setting rest goal: {self.current_goal}")
        else:
            # Only set wandering goal if not already wandering
            if current_activity != 'wandering':
                self.current_goal = {'activity': 'wandering'}
                print(f"Energy OK, setting wander goal: {self.current_goal}")
            else:
                # Already wandering, maybe set a different goal or keep current
                self.current_goal = {'activity': 'wandering'}
    
    def update(self, dt: float):
        if not self.planning_enabled:
            return
        
        from ...actions import ActionState
        
        self.animation_system.update(dt)
        self.replan_timer += dt
        
        # Update current action
        if self.current_action:
            print(f"Updating action: {self.current_action.name}, state: {self.current_action.state}")
            action_state = self.current_action.update(self, dt)
            
            if action_state == ActionState.SUCCESS:
                print(f"Action {self.current_action.name} completed successfully")
                if self.current_plan and self.current_plan[0] == self.current_plan:
                    self.current_plan.pop(0)
                self.current_action = None
            elif action_state == ActionState.FAILURE:
                print(f"Action {self.current_action.name} failed")
                self.current_plan = []
                self.current_action = None
        else:
            print("No current action")
        
        # Check if we need to replan
        if self._should_replan():
            print("Replanning...")
            self._replan()
            self.replan_timer = 0.0
        
        # Start next action if needed
        if not self.current_action and self.current_plan:
            print(f"No current action but have plan: {[a.name for a in self.current_plan]}")
            action = self.current_plan[0]
            print(f"Starting action: {action.name}")
            
            self.current_action = action
            success = action.start(self)
            print(f"Action start result: {success}, state: {action.state}")
            
            if not success or action.state == ActionState.FAILURE:
                print(f"Action failed to start, removing from plan")
                self.current_plan.pop(0)
                self.current_action = None
        elif not self.current_action:
            print("No current action and no plan")
        
        print(f"Position: {self.get_position()}, World: {self.get_world_position()}")
        
        if self.debug_mode:
            self._update_debug_info()
    
    def get_current_tile_elevation(self, grid_x: int, grid_y: int):
        if (0 <= grid_x < self.terrain_data.width and 0 <= grid_y < self.terrain_data.height):
            return self.terrain_data.get_height(grid_x, grid_y)
        return 0
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        from render.pygame_render import TILE_SPRITE_HEIGHT, TILE_HEIGHT
        
        world_pos = self.get_world_position()
        
        # Convert world coordinates to fractional grid coordinates
        grid_x = world_pos[0] / 64.0
        grid_y = world_pos[1] / 64.0
        
        # Get current tile position for elevation calculation
        current_tile_x = int(grid_x)
        current_tile_y = int(grid_y)
        
        # Get elevation of current tile
        elevation = self.get_current_tile_elevation(current_tile_x, current_tile_y)
        
        # Apply isometric projection formula  
        screen_x = (grid_x - grid_y) * (32 // 2) + camera_offset[0]
        screen_y = (grid_x + grid_y) * (16 // 2) + camera_offset[1]
        
        # Use exact same positioning as tiles, then adjust for stag height
        stag_height_offset = -30  # Adjust this value to position stag correctly
        adjusted_y = screen_y - (TILE_SPRITE_HEIGHT - TILE_HEIGHT) + elevation + stag_height_offset

        if self.animation_system:
            current_sprite = self.animation_system.get_current_sprite()
            sprite_rect = current_sprite.get_rect()
            sprite_rect.centerx = int(screen_x)
            sprite_rect.centery = int(adjusted_y)
            screen.blit(current_sprite, sprite_rect)
        else:
            pygame.draw.circle(screen, (255, 0, 0), (int(screen_x), int(adjusted_y)), 16)
            
        if self.debug_mode:
            self._render_debug_info(screen, camera_offset, elevation)      
            
        
    def _render_debug_info(self, screen: pygame.Surface, camera_offset: Tuple[int, int], elevation: int = 0):
        if not pygame.font.get_init():
            return
        
        font = pygame.font.Font(None, 20)
        world_pos = self.get_world_position()
        
        # Convert world coordinates to fractional grid coordinates
        grid_x = world_pos[0] / 64.0
        grid_y = world_pos[1] / 64.0
        
        # Apply isometric projection formula
        screen_x = (grid_x - grid_y) * (32 // 2) + camera_offset[0]
        screen_y = (grid_x + grid_y) * (16 // 2) + camera_offset[1]
        
        # Apply elevation to debug text position
        text_x = int(screen_x)
        text_y = int(screen_y - 50 + elevation)
        
        energy = self.world_state.get('energy', 100)
        awareness = self.world_state.get('awareness', 100)
        activity = self.world_state.get('activity', 'idle')
        
        info_text = f"E:{int(energy)} AW:{int(awareness)} A:{activity}"
        text = font.render(info_text, True, (255, 255, 255))
        screen.blit(text, (text_x - text.get_width() // 2, text_y))
        
        if self.current_action:
            action_text = font.render(self.current_action.name, True, (255, 255, 0))
            screen.blit(action_text, (text_x - action_text.get_width() // 2, text_y + 20))
    
    def get_energy(self) -> float:
        return self.world_state.get('energy', 100)
    
    def get_health(self) -> float:
        return self.world_state.get('health', 100)
    
    def get_awareness_modifier(self) -> float:
        if not self.agent_manager:
            return 1.0
        nearby_stags = self.agent_manager.get_agents_in_range_by_species(
            self.get_position(),
            range_distance = 8,
            species='stag',
            exclude_agent=self
        )
        if nearby_stags:
            return 0.2
        return 1.0
    
    def get_activity(self) -> str:
        return self.world_state.get('activity', 'idle')
    
    def is_energy_low(self) -> bool:
        return self.world_state.get('energy_low', False)
    
    def damage(self, amount: float):
        current_health = self.world_state.get('health', 100)
        new_health = max(0, current_health - amount)
        self.world_state.set('health', new_health)
    
    def set_threatened(self, threatened: bool, threat_position: Tuple[int, int] = None):
        self.world_state.set('threatened', threatened)
        if threat_position:
            self.world_state.set('threat_position', threat_position)