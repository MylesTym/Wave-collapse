# core/tiles.py

# Define tile types and adjacency rules

TILES = {
    "grass": {
        "sprite": "assets/tiles/grass.png",
        "color": "green",
        "weight": 2.0,
        "rules": {
            "up": {"grass", "stone", "dirt"},
            "down": {"grass", "stone", "dirt"},
            "left": {"grass", "stone", "dirt"},
            "right": {"grass", "stone", "dirt"},
            "up_left": {"grass", "stone", "dirt"},
            "up_right": {"grass", "stone", "dirt"},
            "down_left": {"grass", "stone", "dirt"},
            "down_right": {"grass", "stone", "dirt"}
        }
    },
    "shrub": {
        "sprite": "assets/resources/plants/shrub.png",
        "color": "green",
        "weight": 4.0,
        "rules": {
            "up": {"grass", "dirt", "shrub"},
            "down": {"grass", "dirt", "shrub"},
            "left": {"grass", "dirt", "shrub"},
            "right": {"grass", "dirt", "shrub"},
            "up_left": {"grass", "dirt", "shrub"},
            "up_right": {"grass", "dirt", "shrub"},
            "down_left": {"grass", "dirt", "shrub"},
            "down_right": {"grass", "dirt", "shrub"}
        }
    },
    "stone": {
        "sprite": "assets/tiles/stone.png",
        "color": "gray",
        "weight": 0.6,
        "rules": {
            "up": {"stone", "dirt"},
            "down": {"stone", "dirt"},
            "left": {"stone", "dirt"},
            "right": {"stone", "dirt"},
            "up_left": {"stone", "dirt"},
            "up_right": {"stone", "dirt"},
            "down_left": {"stone", "dirt"},
            "down_right": {"stone", "dirt"}
        }
    },
    "water": {
        "sprite": "assets/tiles/water.png",
        "color": "blue",
        "weight": 2.9,
        "rules": {
            "up": {"water", "grass"},
            "down": {"water", "grass"},
            "left": {"water", "grass"},
            "right": {"water", "grass"},
            "up_left": {"water", "grass"},
            "up_right": {"water", "grass"},
            "down_left": {"water", "grass"},
            "down_right": {"water", "grass"}
        }
    },
    "dirt": {
        "sprite": "assets/tiles/dirt.png",
        "color": "black",
        "weight": 1.3,
        "rules": {
            "up": {"dirt", "stone", "grass", "water"},
            "down": {"dirt", "grass", "stone", "water"},
            "left": {"dirt", "grass", "stone", "water"},
            "right": {"dirt", "grass", "stone", "water"},
            "up_left": {"dirt", "grass", "stone", "water"},
            "up_right": {"dirt", "grass", "stone", "water"},
            "down_left": {"dirt", "grass", "stone", "water"},
            "down_right": {"dirt", "grass", "stone", "water"}
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