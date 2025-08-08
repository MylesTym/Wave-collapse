# core/terrain.py
from core.elevation import create_terrain_data, SEA_LEVEL, MAX_HEIGHT

# Terrain-specific constants
SMOOTHING_PASSES = 2
RESOURCE_DENSITY_THRESHOLD = 0.6  # Minimum neighbor suitability for resources

class TerrainData:

    def __init__(self, elevation_data, width, height):
        self.width = width
        self.height = height
        
        # Store elevation system data
        self.heightmap = elevation_data['heightmap']
        self.slopes = elevation_data['slopes']
        self.sea_level = elevation_data['sea_level']
        self.base_constraints = elevation_data['get_constraints']
        
        # Terrain-specific data
        self.smoothed_heightmap = None
        self.resource_zones = [[False for _ in range(width)] for _ in range(height)]
        self.biome_zones = [[None for _ in range(width)] for _ in range(height)]
        self.constraint_cache = {}
    
    def get_height(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            # Use smoothed heightmap if available, otherwise original
            heightmap = self.smoothed_heightmap or self.heightmap
            return heightmap[y][x]
        return 0
    
    def is_resource_zone(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.resource_zones[y][x]
        return False
    
    def get_biome(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.biome_zones[y][x]
        return None

class TerrainGenerator:

    
    def apply_smoothing(self, terrain_data):
  
        # Start with original heightmap
        current_heightmap = [row[:] for row in terrain_data.heightmap]
        
        for _ in range(SMOOTHING_PASSES):
            new_heightmap = [[0 for _ in range(terrain_data.width)] 
                           for _ in range(terrain_data.height)]
            
            for y in range(terrain_data.height):
                for x in range(terrain_data.width):
                    total_height = 0
                    neighbor_count = 0
                    
                    # Get weighted average of neighbors
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < terrain_data.width and 0 <= ny < terrain_data.height:
                                weight = 3 if (dx == 0 and dy == 0) else 1  # Current cell has more weight
                                total_height += current_heightmap[ny][nx] * weight
                                neighbor_count += weight
                    
                    new_height = int(total_height / neighbor_count)
                    new_heightmap[y][x] = max(0, min(MAX_HEIGHT, new_height))
            
            current_heightmap = new_heightmap
        
        terrain_data.smoothed_heightmap = current_heightmap
    
    def determine_resource_zones(self, terrain_data):
    
        for y in range(terrain_data.height):
            for x in range(terrain_data.width):
                # Get base elevation constraints
                base_valid_tiles = terrain_data.base_constraints(x, y)
                
                # Resources can only go where shrubs are allowed by elevation
                if 'shrub' not in base_valid_tiles:
                    terrain_data.resource_zones[y][x] = False
                    continue
                
                # Additional terrain-based checks
                height = terrain_data.get_height(x, y)
                suitable_for_resources = (
                    self._has_suitable_neighbors(terrain_data, x, y) and
                    self._check_local_terrain_quality(terrain_data, x, y)
                )
                
                terrain_data.resource_zones[y][x] = suitable_for_resources
    
    def _has_suitable_neighbors(self, terrain_data, x, y):
    
        suitable_neighbors = 0
        total_neighbors = 0
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                if 0 <= nx < terrain_data.width and 0 <= ny < terrain_data.height:
                    # Get what tiles are valid at neighbor position
                    neighbor_constraints = terrain_data.base_constraints(nx, ny)
                    
                    # Count neighbors that can support vegetation
                    if 'grass' in neighbor_constraints or 'shrub' in neighbor_constraints:
                        suitable_neighbors += 1
                    total_neighbors += 1
        
        if total_neighbors == 0:
            return False
        
        return (suitable_neighbors / total_neighbors) >= RESOURCE_DENSITY_THRESHOLD
    
    def _check_local_terrain_quality(self, terrain_data, x, y):
   
        height = terrain_data.get_height(x, y)
        
        # Avoid areas that are too close to extreme elevations
        if height <= SEA_LEVEL + 1 or height >= MAX_HEIGHT - 2:
            return False
        
        # Check for elevation stability (not on dramatic slopes)
        height_variance = 0
        neighbor_count = 0
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < terrain_data.width and 0 <= ny < terrain_data.height:
                    neighbor_height = terrain_data.get_height(nx, ny)
                    height_variance += abs(height - neighbor_height)
                    neighbor_count += 1
        
        avg_variance = height_variance / max(neighbor_count, 1)
        return avg_variance < 3  # Relatively stable elevation
    
    def assign_basic_biomes(self, terrain_data):
      
        for y in range(terrain_data.height):
            for x in range(terrain_data.width):
                height = terrain_data.get_height(x, y)
                base_constraints = terrain_data.base_constraints(x, y)
                
                # Simple biome rules
                if 'water' in base_constraints and height <= SEA_LEVEL:
                    terrain_data.biome_zones[y][x] = 'aquatic'
                elif 'stone' in base_constraints:
                    terrain_data.biome_zones[y][x] = 'rocky'
                elif terrain_data.is_resource_zone(x, y):
                    terrain_data.biome_zones[y][x] = 'fertile'
                elif height > SEA_LEVEL + 8:
                    terrain_data.biome_zones[y][x] = 'highland'
                else:
                    terrain_data.biome_zones[y][x] = 'temperate'
    
    def generate_enhanced_terrain(self, width, height):
      
        # Get base elevation data
        elevation_data = create_terrain_data(width, height)
        
        # Create enhanced terrain data
        terrain_data = TerrainData(elevation_data, width, height)
        
        # Apply terrain enhancements
        self.apply_smoothing(terrain_data)
        self.determine_resource_zones(terrain_data)
        self.assign_basic_biomes(terrain_data)
        
        return terrain_data
####
def get_terrain_constraints(terrain_data, x, y):
    cache_key = f"{x},{y}"
    if cache_key in terrain_data.constraint_cache:
        return terrain_data.constraint_cache[cache_key]

    # Get base elevation constraints only
    base_constraints = terrain_data.base_constraints(x, y)
    all_tiles = ['grass', 'stone', 'dirt', 'water', 'shrub']
    height = terrain_data.get_height(x, y)
    from core.tiles import TILES
    terrain_constraints = []
    for tile in all_tiles:
        elev_range = TILES[tile].get('elevation_range', (0, 100))
        if elev_range[0] <= height <= elev_range[1]:
            terrain_constraints.append(tile)
    # Add extra weight to elevation-preferred tiles
    for preferred_tile in base_constraints:
        if preferred_tile in terrain_constraints:
            terrain_constraints.extend([preferred_tile] * 2)
    # Fallback: if no tiles match elevation, allow all
    if not terrain_constraints:
        terrain_constraints = all_tiles[:]
    terrain_data.constraint_cache[cache_key] = terrain_constraints
    return terrain_constraints
#####

def create_wfc_constraint_function(terrain_data):
 
    def constraint_function(x, y):
        return get_terrain_constraints(terrain_data, x, y)
    
    return constraint_function

def print_terrain_debug(terrain_data):
  
    print("Terrain Map:")
    print("~ = Water, . = Normal, ^ = High, * = Steep, R = Resource, F = Fertile")
    
    for y in range(terrain_data.height):
        line = ""
        for x in range(terrain_data.width):
            base_constraints = terrain_data.base_constraints(x, y)
            is_resource = terrain_data.is_resource_zone(x, y)
            biome = terrain_data.get_biome(x, y)
            
            if 'stone' in base_constraints and terrain_data.slopes[y][x]:
                line += "*"
            elif is_resource and biome == 'fertile':
                line += "F"
            elif is_resource:
                line += "R"
            elif 'water' in base_constraints:
                line += "~"
            elif terrain_data.get_height(x, y) > MAX_HEIGHT - 5:
                line += "^"
            else:
                line += "."
        print(line)

# Main interface function
def generate_complete_terrain(width, height):

    generator = TerrainGenerator()
    terrain_data = generator.generate_enhanced_terrain(width, height)
    
    # Create WFC constraint function
    constraint_function = create_wfc_constraint_function(terrain_data)
    
    return {
        'terrain_data': terrain_data,
        'constraint_function': constraint_function,
        'sea_level': SEA_LEVEL,
        'has_smoothing': terrain_data.smoothed_heightmap is not None,
        'resource_zones_count': sum(sum(row) for row in terrain_data.resource_zones)
    }