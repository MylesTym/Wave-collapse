# core/tiles.py

# Define tile types and adjacency rules

TILES = {
    "grass": {
        "sprite": "assets/tiles/grass.png",
        "color": "green",
        "weight": 2.0,
        "rules": {
            "up": {"grass", "stone"},
            "down": {"grass", "stone"},
            "left": {"grass", "stone"},
            "right": {"grass", "stone"}
        }
    },
    "stone": {
        "sprite": "assets/tiles/stone.png",
        "color": "gray",
        "weight": 0.8,
        "rules": {
            "up": {"stone", "grass"},
            "down": {"stone", "grass"},
            "left": {"stone", "grass"},
            "right": {"stone", "grass"}
        }
    },
    "water": {
        "sprite": "assets/tiles/water.png",
        "color": "blue",
        "weight": 0.8,
        "rules": {
            "up": {"water", "grass"},
            "down": {"water", "grass"},
            "left": {"water", "grass"},
            "right": {"water", "grass"}
        }
    },
    "dirt": {
        "sprite": "assets/tiles/dirt.png",
        "color": "black",
        "weight": 1.0,
        "rules": {
            "up": {"dirt", "stone", "grass"},
            "down": {"dirt", "grass"},
            "left": {"dirt", "grass"},
            "right": {"dirt", "grass"}
        }
    }
}

# Utility functions
def get_tile_weight(tile_name):
    return TILES.get(tile_name, {}).get("weight", 1.0)

def weighted_random_choice(possible_tiles):
   
    import random
    
    if not possible_tiles:
        return None
    
    # Get weights for all possible tiles
    weights = [get_tile_weight(tile) for tile in possible_tiles]
    
    # Use weighted random choice
    return random.choices(possible_tiles, weights=weights, k=1)[0]