# core/tiles.py

# Define tile types and adjacency rules

TILES = {
    "grass": {
        "color": "green",
        "rules": {
            "up": {"grass", "road"},
            "down": {"grass", "road"},
            "left": {"grass", "road"},
            "right": {"grass", "road"}
        }
    },
    "road": {
        "color": "gray",
        "rules": {
            "up": {"road", "grass"},
            "down": {"road", "grass"},
            "left": {"road", "grass"},
            "right": {"road", "grass"}
        }
    },
    "water": {
        "color": "blue",
        "rules": {
            "up": {"water", "grass"},
            "down": {"water", "grass"},
            "left": {"water", "grass"},
            "right": {"water", "grass"}
        }
    },
    "wall": {
        "color": "black",
        "rules": {
            "up": {"wall", "road", "grass"},
            "down": {"wall", "grass"},
            "left": {"Wall", "grass"},
            "right": {"wall", "grass"}
        }
    }
}