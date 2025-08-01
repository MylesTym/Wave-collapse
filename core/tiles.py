# core/tiles.py

# Define tile types and adjacency rules

TILES = {
    "grass": {
        "sprite": "assets/tiles/grass.png",
        "color": "green",
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
        "rules": {
            "up": {"dirt", "stone", "grass"},
            "down": {"dirt", "grass"},
            "left": {"dirt", "grass"},
            "right": {"dirt", "grass"}
        }
    }
}