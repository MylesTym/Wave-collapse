
from PIL import Image
import os

# Config
tileset_path = "assets/basic_package.png"
output_folder = "assets/tiles"
tile_size = 48

tileset = Image.open(tileset_path)
tileset_width, tileset_height = tileset.size
columns = tileset_width // tile_size
rows = tileset_height // tile_size

index = 0 
for row in range(rows):
    for col in range(columns):
        tile = tileset.crop((
            col * tile_size,
            row * tile_size,
            (col + 1) * tile_size,
            (row + 1) * tile_size
        ))
        tile.save(os.path.join(output_folder, f"tile_{index}.png"))
        index += 1
print(f"Sliced {index} tiles into ' {output_folder}'")