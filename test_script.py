#!/usr/bin/env python3

from critters import WorldState, GOAPAgent, WFCMapInterface, GOAPPlanner
from critters.actions import Action, MoveToAction

def test_imports():
    print("Testing imports...")
    print("All imports successful")
    return True

def test_world_state():
    print("Testing WorldState...")
    
    state = WorldState()
    state.set('position', (5, 3))
    state.set('energy', 100)
    state.set('hungry', False)
    
    assert state.get('position') == (5, 3)
    assert state.get('energy') == 100
    assert state.get('hungry') == False
    
    conditions = {'energy': 100, 'hungry': False}
    assert state.meets_conditions(conditions)
    
    conditions = {'energy': 50, 'hungry': False}
    assert not state.meets_conditions(conditions)
    
    state_copy = state.copy()
    state_copy.set('energy', 50)
    assert state.get('energy') == 100
    assert state_copy.get('energy') == 50
    
    print("WorldState tests passed")

def test_map_interface():
    print("Testing WFCMapInterface...")
    
    test_map = [
        ['grass', 'tree', 'grass'],
        ['stone', 'grass', 'water'],
        ['grass', 'grass', 'tree']
    ]
    
    map_interface = WFCMapInterface(test_map, tile_size=64)
    
    assert map_interface.width == 3
    assert map_interface.height == 3
    
    assert map_interface.get_tile_type(0, 0) == 'grass'
    assert map_interface.get_tile_type(1, 0) == 'tree'
    
    assert map_interface.is_walkable(0, 0)
    assert not map_interface.is_walkable(2, 1)
    
    world_pos = map_interface.grid_to_world(1, 1)
    assert world_pos == (64.0, 64.0)
    
    grid_pos = map_interface.world_to_grid(64.0, 64.0)
    assert grid_pos == (1, 1)
    
    print("WFCMapInterface tests passed")

def test_actions():
    print("Testing Actions...")
    
    action = Action("TestAction", cost=2.0)
    action.add_precondition('energy', 100)
    action.add_effect('task_done', True)
    
    state = WorldState()
    state.set('energy', 100)
    
    assert action.is_valid(state, None)
    assert action.get_cost(state, None) == 2.0
    
    state.set('energy', 50)
    assert not action.is_valid(state, None)
    
    move_action = MoveToAction((5, 5))
    assert move_action.target_position == (5, 5)
    assert 'grid_position' in move_action.effects
    
    print("Actions tests passed")

def test_planner():
    print("Testing GOAPPlanner...")
    
    planner = GOAPPlanner()
    
    state = WorldState()
    state.set('task_done', True)
    goal = {'task_done': True}
    actions = []
    
    plan = planner.plan(state, goal, actions, None)
    assert plan == []
    
    state.set('task_done', False)
    action = Action("DoTask")
    action.add_effect('task_done', True)
    actions = [action]
    
    plan = planner.plan(state, goal, actions, None)
    assert len(plan) == 1
    assert plan[0] == action
    
    print("GOAPPlanner tests passed")

def main():
    print("GOAP System Test")
    
    if not test_imports():
        print("Import tests failed")
        return
    
    try:
        test_world_state()
        test_map_interface()
        test_actions()
        test_planner()
        
        print("All tests passed")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()