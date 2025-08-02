from typing import Dict, Any
from copy import deepcopy

class WorldState:

    def __init__(self, initial_state: Dict[str, Any] = None):
        self.state = initial_state.copy() if initial_state else {}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self.state[key] = value
    
    def has(self, key: str) -> bool:
        return key in self.state
    
    def remove(self, key: str) -> bool:
        if key in self.state:
            del self.state[key]
            return True
        return False
    
    def copy(self) -> 'WorldState':
        return WorldState(deepcopy(self.state))
    
    def meets_coditions(self, conditions: Dict[str, Any]) -> bool:
        for key, expected_value in conditions.items():
            if self.get(key) != expected_value:
                return False
            
        return True
    
    def update(self, other_state: 'WorldState') -> None:
        self.state.update(other_state.state)

    def update_dict(self, state_dict: Dict[str, Any]) -> None:
        self.state.update(state_dict)

    def clear(self) -> None:
        self.state.clear()

    def keys(self):
        return self.state.keys()
    
    def values(self):
        return self.state.values()
    
    def items(self):
        return self.state.items()
    
    def __str__(self) -> str:
        return f"WorldState({self.state})"
    
    def __repr__(self) -> str:
        return f"WorldState({repr(self.state)})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, WorldState):
            return False
        return self.state == other.state
    
    def __len__(self) -> int:
        return len(self.state)
