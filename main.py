from core.tiles import TILES
from core.wfc import create_grid, get_lowest_entropy_cell, collapse_cell, propagate
from render.pygame_render import render
import matplotlib.pyplot as plt

def main():
    width, height = 40, 40
    tile_names = list(TILES.keys())
    grid = create_grid(width, height, tile_names)  # pass tile_names, not TILES

    while True:
        pos = get_lowest_entropy_cell(grid)  # returns (x, y) or None
        if not pos:
            print("Collapse Complete.")
            break
        x, y = pos
        collapse_cell(grid[y][x])  # collapse the cell at that position
        propagate(grid)            # propagate constraints on whole grid

    render(grid)
    plt.show()

if __name__ == "__main__":
    main()
