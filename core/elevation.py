import random
import math

# Basic constraints
SEA_LEVEL = 8
MIN_HEIGHT = 0
MAX_HEIGHT = 25
STEEP_SLOPE_THRESHOLD = 4

def simple_noise(x, y, scale=0.1):
    # basic noise function-- will update later
    value = (
        math.sin(x * scale) * math.cos(y * scale) +
        math.sin(x * scale * 2) * math.cos(y * scale * 2) * 0.5 +
        math.sin(x * scale * 4) * math.cos(y * scale * 4) * 0.25
    )
    # Normalize
    normalized = (value + 1.75) / 3.5
    return (max(0, min(1, normalized)))

def generate_heightmap(width, height):
    # Generate basic heightmap from nois
    heightmap = []

    for y in range(height):
        row = []
        for x in range(width):
            # noise value (0-1)
            noise_value = simple_noise(x, y, scale=0.1)

            # convert to height range
            elevation = int(noise_value * MAX_HEIGHT)
            row.append(elevation)
        heightmap.append(row)
    return heightmap

def calculate_slopes(heightmap):
    # calculate slope
    height = len(heightmap)
    width = len(heightmap[0])
    slopes = []

    for y in range(height):
        row = []
        for x in range(width):
            is_steep = False
            current_height =heightmap[y][x]
            # check all 8 neighbors
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    nx, ny = x + dx, y + dy
                    # check bounds
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor_height = heightmap[ny][nx]
                        height_diff = abs(current_height - neighbor_height)

                        if height_diff >= STEEP_SLOPE_THRESHOLD:
                            is_steep = True
                            break
                if is_steep:
                    break

            row.append(is_steep)
        slopes.append(row)

    return slopes

def get_elevation_constraints(x, y, heightmap, slopes=None):
    # Get valid tiles
    if slopes is None:
        slopes = calculate_slopes(heightmap)

    elevation = heightmap[y][x]
    is_steep = slopes[y][x]
    valid_tiles = []

    #### Basic rules ####
    # water
    if elevation <= SEA_LEVEL:
        valid_tiles.append('water')

    # stone
    if is_steep:
        valid_tiles.append('stone')
    
    # Grass
    if elevation > SEA_LEVEL - 2:
        valid_tiles.append('grass')
    
    # dirt
    if SEA_LEVEL - 1 <= elevation <= MAX_HEIGHT - 5:
        valid_tiles.append('dirt')
    
    # shrub
    if elevation >= SEA_LEVEL + 3:
        valid_tiles.append('shrub')
    
    # at least one return
    if not valid_tiles:
        valid_tiles = ['grass']

    return valid_tiles

def print_heightmap_debug(heightmap):
    # Debugging to console
    print("Heightmap (0-25):")
    for row in heightmap:
        line = ""
        for height in row:
            if height <= SEA_LEVEL:
                line += "~"  # Water
            elif height > MAX_HEIGHT - 5:
                line += "^"  # High elevation
            else:
                line += "."  # Normal elevation
        print(line)

def print_slopes_debug(slopes):
    # Debugging to console
    print("Slopes (* = steep):")
    for row in slopes:
        line = ""
        for is_steep in row:
            line += "*" if is_steep else "."
        print(line)

def create_terrain_data(width, height):
    # terrain data for WFC

    heightmap = generate_heightmap(width, height)
    slopes = calculate_slopes(heightmap)

    return {
        'heightmap': heightmap,
        'slopes': slopes,
        'sea_level': SEA_LEVEL,
        'get_constraints': lambda x, y: get_elevation_constraints(x, y, heightmap, slopes)
    }