from typing import Dict, List, Tuple, Set, Any, Optional

class WFCMapInterface:

    def __init__(self, wfc_map_data: List[List[Any]], tile_size: int = 64):
        self.map_data = wfc_map_data
        self.tile_size = tile_size
        self.width = len(wfc_map_data[0]) if wfc_map_data else 0
        self.height = len(wfc_map_data) if wfc_map_data else 0

        # Cache frequently used data
        self._resource_cache = None
        self._walkable_cache = None
    
    def get_tile_at(self, grid_x: int, grid_y: int) -> Any:
        if self.is_valid_position(grid_x, grid_y):
            return self.map_data[grid_y][grid_x]
        return None
    
    def get_tile_type(self, grid_x: int, grid_y: int) -> str:
        tile = self.get_tile_at(grid_x, grid_y)
        if tile is None:
            return "void"
        if hasattr(tile, 'collapsed') and tile.collapsed and hasattr(tile, 'options'):
            return tile.options[0].lower()
        elif hasattr(tile, 'name'):
            return tile.name.lower()
        elif hasattr(tile, 'tile_type'):
            return tile.tile_type.lower()
        elif isinstance(tile, str):
            return tile.lower()
        elif isinstance(tile, dict) and 'type' in tile:
            return tile['type'].lower()
        else:
            return str(tile).lower()
    
    def is_valid_position(self, grid_x: int, grid_y: int) -> bool:
        return 0 <= grid_x < self.width and 0 <= grid_y < self.height
    
    def is_walkable(self, grid_x: int, grid_y: int) -> bool:
        if not self.is_valid_position(grid_x, grid_y):
            return False
        tile_type = self.get_tile_type(grid_x, grid_y)

        walkable_types = {
            'grass', 'dirt', 'path', 'stone', 'floor', 'ground',
            'sand', 'shrub'
        }
        return any(walkable in tile_type for walkable in walkable_types)

    def has_resource(self, grid_x: int, grid_y: int, resource_type: str) -> bool:

        tile_type = self.get_tile_type(grid_x, grid_y)

        resource_mappings = {
            'wood': ['tree', 'forest', 'lumber'],
            'stone': ['rock', 'stone', 'quarry'],
            'water': ['water', 'lake', 'river'],
            'food': ['wheat', 'berry',],
            'ore': ['ore', 'metal', 'iron']
        }
        resource_keywords = resource_mappings.get(resource_type.lower(), [])
        return any(keyword in tile_type for keyword in resource_keywords)
    
    def find_resources(self, resource_type: str) -> List[Tuple[int, int]]:
        if self._resource_cache is None:
            self._build_resource_cache()
        return self._resource_cache.get(resource_type.lower(), [])
    
    def find_nearest_resource(self, start_pos: Tuple[int, int], resource_type: str) -> Optional[Tuple[int, int]]:
        resources = self.find_resources(resource_type)
        if not resources:
            return None
        start_x, start_y = start_pos
        min_distance = float('inf')
        nearest = None

        for res_x, res_y in resources:
            distance = abs(res_x - start_x) + abs(res_y - start_y)
            if distance < min_distance:
                min_distance = distance
                nearest= (res_x, res_y)

        return nearest
    
    def get_walkable_neighbors(self, grid_x: int, grid_y: int) -> List[Tuple[int, int]]:
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = grid_x + dx, grid_y + dy
            if self.is_walkable(new_x, new_y):
                neighbors.append((new_x, new_y))

        return neighbors
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        world_x = grid_x * self.tile_size
        world_y = grid_y * self.tile_size
        return (float(world_x), float(world_y))
    
    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        return (grid_x, grid_y)
    
    def get_area_tiles(self, center: Tuple[int, int], radius: int) -> List[Tuple[int, int]]:
        center_x, center_y = center
        tiles = []

        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius +1):
                if self.is_valid_position(x, y):
                    if abs(x - center_x) + abs(y - center_y) <= radius:
                        tiles.append((x, y))
        
        return tiles
    
    def _build_resource_cache(self):
        self._resource_cache = {
            'wood': [],
            'stone': [],
            'water': [],
            'food': [],
            'ore': []
        }
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.get_tile_type(x, y)

                for resource_type in self._resource_cache.keys():
                    if self.has_resource(x, y, resource_type):
                        self._resource_cache[resource_type].append((x, y))

    def clear_cache(self):
        self._resource_cache = None
        self._walkable_cache = None