import heapq
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .world_state import WorldState
from .actions import Action


@dataclass
class PlanNode:
    world_state: WorldState
    action: Optional[Action]
    parent: Optional['PlanNode']
    g_cost: float  # Cost from start to this node
    h_cost: float  # Heuristic cost to goal
    f_cost: float  # Total cost (g + h)
    
    def __lt__(self, other):
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost


class GOAPPlanner:
  
    
    def __init__(self, max_iterations: int = 300):
      
        self.max_iterations = max_iterations
    
    def plan(self, current_state: WorldState, goal: Dict[str, Any], 
             available_actions: List[Action], agent) -> List[Action]:
     
        # Quick check: is goal already satisfied?
        if current_state.meets_conditions(goal):
            return []
        
        # Initialize search
        open_set = []
        closed_set = set()
        
        # Create start node
        start_node = PlanNode(
            world_state=current_state.copy(),
            action=None,
            parent=None,
            g_cost=0.0,
            h_cost=self._calculate_heuristic(current_state, goal),
            f_cost=0.0
        )
        start_node.f_cost = start_node.g_cost + start_node.h_cost
        
        heapq.heappush(open_set, start_node)
        iterations = 0
        
        # A* search loop
        while open_set and iterations < self.max_iterations:
            iterations += 1
            
            # Get node with lowest cost
            current_node = heapq.heappop(open_set)
            
            # Check if goal is achieved
            if current_node.world_state.meets_conditions(goal):
                return self._reconstruct_plan(current_node)
            
            # Add to closed set
            state_key = self._get_state_key(current_node.world_state)
            if state_key in closed_set:
                continue
            closed_set.add(state_key)
            
            # Try each available action
            for action in available_actions:
                if not action.is_valid(current_node.world_state, agent):
                    continue
                
                # Create new state after applying action
                new_state = current_node.world_state.copy()
                self._apply_action_effects(new_state, action)
                
                # Check if we've seen this state before
                new_state_key = self._get_state_key(new_state)
                if new_state_key in closed_set:
                    continue
                
                # Calculate costs
                action_cost = action.get_cost(current_node.world_state, agent)
                g_cost = current_node.g_cost + action_cost
                h_cost = self._calculate_heuristic(new_state, goal)
                f_cost = g_cost + h_cost
                
                # Create new node
                new_node = PlanNode(
                    world_state=new_state,
                    action=action,
                    parent=current_node,
                    g_cost=g_cost,
                    h_cost=h_cost,
                    f_cost=f_cost
                )
                
                heapq.heappush(open_set, new_node)
        
        # No plan found
        return []
    
    def _calculate_heuristic(self, state: WorldState, goal: Dict[str, Any]) -> float:
      
        unmet_conditions = 0
        for key, target_value in goal.items():
            current_value = state.get(key)
            if current_value != target_value:
                unmet_conditions += 1
        
        return float(unmet_conditions)
    
    def _apply_action_effects(self, state: WorldState, action: Action):
        
        for key, value in action.effects.items():
            state.set(key, value)
    
    def _get_state_key(self, state: WorldState) -> str:
       
        # Create sorted string of state items for consistent comparison
        items = sorted(state.items())
        return str(items)
    
    def _reconstruct_plan(self, goal_node: PlanNode) -> List[Action]:
      
        plan = []
        current = goal_node
        
        # Walk backwards through parent chain
        while current.parent is not None:
            plan.append(current.action)
            current = current.parent
        
        # Reverse to get start-to-goal order
        plan.reverse()
        return plan
    
    def can_achieve_goal(self, current_state: WorldState, goal: Dict[str, Any], 
                        available_actions: List[Action], agent) -> bool:
      
        # Already achieved?
        if current_state.meets_conditions(goal):
            return True
        
        # Simple check: do we have actions that produce needed effects?
        for goal_key, goal_value in goal.items():
            if current_state.get(goal_key) != goal_value:
                # Look for action that can produce this effect
                can_produce = False
                for action in available_actions:
                    if (action.is_valid(current_state, agent) and 
                        goal_key in action.effects and 
                        action.effects[goal_key] == goal_value):
                        can_produce = True
                        break
                
                if not can_produce:
                    return False
        
        return True
    
    def get_plan_cost(self, plan: List[Action], start_state: WorldState, agent) -> float:
        
        total_cost = 0.0
        current_state = start_state.copy()
        
        for action in plan:
            total_cost += action.get_cost(current_state, agent)
            self._apply_action_effects(current_state, action)
        
        return total_cost