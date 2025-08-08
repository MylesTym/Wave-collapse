# core/tiles.py

# Define tile types and adjacency rules

TILES = {
    "grass": {
        "sprite": "assets/tiles/grass.png",
        "color": "green",
        "weight": 2.0,
        "elevation_range": (2, 20),
        "rules": {
            "up": {"grass", "stone", "dirt", "water", "shrub"},
            "down": {"grass", "stone", "dirt", "water", "shrub"},
            "left": {"grass", "stone", "dirt", "water", "shrub"},
            "right": {"grass", "stone", "dirt", "water", "shrub"},
            "up_left": {"grass", "stone", "dirt", "water", "shrub"},
            "up_right": {"grass", "stone", "dirt", "water", "shrub"},
            "down_left": {"grass", "stone", "dirt", "water", "shrub"},
            "down_right": {"grass", "stone", "dirt", "water", "shrub"}
        }
    },
    "shrub": {
        "sprite": "assets/resources/plants/shrub.png",
        "color": "green",
        "weight": 4.0,
        "elevation_range": (5, 22),
        "rules": {
            "up": {"grass", "dirt", "shrub", "water"},
            "down": {"grass", "dirt", "shrub", "water"},
            "left": {"grass", "dirt", "shrub", "water"},
            "right": {"grass", "dirt", "shrub", "water"},
            "up_left": {"grass", "dirt", "shrub", "water"},
            "up_right": {"grass", "dirt", "shrub", "water"},
            "down_left": {"grass", "dirt", "shrub", "water"},
            "down_right": {"grass", "dirt", "shrub", "water"}
        }
    },
    "stone": {
        "sprite": "assets/tiles/stone.png",
        "color": "gray",
        "weight": 0.6,
        "elevation_range": (15, 30),
        "rules": {
            "up": {"stone", "dirt", "grass", "water", "dirt"},
            "down": {"stone", "dirt", "grass", "water", "dirt"},
            "left": {"stone", "dirt", "grass", "water", "dirt"},
            "right": {"stone", "dirt", "grass", "water", "dirt"},
            "up_left": {"stone", "dirt", "grass", "water", "dirt"},
            "up_right": {"stone", "dirt", "grass", "water", "dirt"},
            "down_left": {"stone", "dirt", "grass", "water", "dirt"},
            "down_right": {"stone", "dirt", "grass", "water", "dirt"}
        }
    },
    "water": {
        "sprite": "assets/tiles/water.png",
        "color": "blue",
        "weight": 2.9,
        "elevation_range": (0, 2),
        "rules": {
            "up": {"water", "grass", "dirt", "shrub","stone"},
            "down": {"water", "grass", "dirt", "shrub", "stone"},
            "left": {"water", "grass", "dirt", "shrub", "stone"},
            "left": {"water", "grass", "dirt", "shrub", "stone"},
            "right": {"water", "grass", "dirt", "shrub", "stone"},
            "up_left": {"water", "grass", "dirt", "shrub", "stone"},
            "up_right": {"water", "grass", "dirt", "shrub", "stone"},
            "down_left": {"water", "grass", "dirt", "shrub", "stone"},
            "down_right": {"water", "grass", "dirt", "shrub", "stone"}
        }
    },
    "dirt": {
        "sprite": "assets/tiles/dirt.png",
        "color": "black",
        "weight": 1.3,
        "elevation_range": (3, 18),
        "rules": {
            "up": {"dirt", "stone", "grass", "water", "shrub"},
            "down": {"dirt", "grass", "stone", "water", "shrub"},
            "left": {"dirt", "grass", "stone", "water", "shrub"},
            "right": {"dirt", "grass", "stone", "water", "shrub"},
            "up_left": {"dirt", "grass", "stone", "water", "shrub"},
            "up_right": {"dirt", "grass", "stone", "water", "shrub"},
            "down_left": {"dirt", "grass", "stone", "water" "shrub"},
            "down_right": {"dirt", "grass", "stone", "water", "shrub"}
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