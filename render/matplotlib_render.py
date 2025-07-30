# render/matplotlib_render.py

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from core.tiles import TILES

def render(grid):
    h, w = len(grid), len(grid[0])
    color_grid = np.zeros((h, w, 3))

    for y in range(h):
        for x in range(w):
            cell = grid[y][x]
            if cell.collapsed:
                tile = TILES[cell.options[0]]
                color = mcolors.to_rgb(tile["color"])
            else:
                color = (0.3, 0.3, 0.3)
            color_grid[y, x] = color

    plt.figure(figsize=(5, 5))
    plt.imshow(color_grid)
    plt.axis('off')
    plt.show()
