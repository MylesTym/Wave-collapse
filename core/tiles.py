# core/tiles.py

# Define tile types and adjacency rules

TILES = {
    "grass": {
        "sprite": "assets/tiles/grass.png",
        "color": "green",
        "rules": {
            "up": {"grass", "road"},
            "down": {"grass", "road"},
            "left": {"grass", "road"},
            "right": {"grass", "road"}
        }
    },
    "road": {
        "sprite": "assets/tiles/road.png",
        "color": "gray",
        "rules": {
            "up": {"road", "grass"},
            "down": {"road", "grass"},
            "left": {"road", "grass"},
            "right": {"road", "grass"}
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
    "wall": {
        "sprite": "assets/tiles/wall.png",
        "color": "black",
        "rules": {
            "up": {"wall", "road", "grass"},
            "down": {"wall", "grass"},
            "left": {"Wall", "grass"},
            "right": {"wall", "grass"}
        }
    }
}