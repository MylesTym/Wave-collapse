# core/wfc.py

import random
from core.tiles import TILES
from core.tiles import weighted_random_choice
from core.cell import Cell

def create_grid(w, h, tile_names):
    return [[Cell(tile_names) for _ in range(w)] for _ in range(h)]

def get_lowest_entropy_cell(grid):
    min_entropy = float('inf')
    candidates = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if not cell.collapsed:
                entropy = len(cell.options)
                if entropy < min_entropy:
                    min_entropy = entropy
                    candidates = [(x, y)]
                elif entropy == min_entropy:
                    candidates.append((x, y))
    return random.choice(candidates) if candidates else None

def collapse_cell(cell):
    cell.collapsed = True
    selected_tile = weighted_random_choice(cell.options)
    cell.options = [selected_tile]

def get_neighbors(x, y, w, h, use_8_directions=True):
    if use_8_directions:
        directions = {
            "up":    (0, -1),
            "down":  (0, 1),
            "left":  (-1, 0),
            "right": (1, 0),
            "up_left": (-1, -1),
            "up_right": (1, -1),
            "down_left": (-1, 1),
            "down_right": (1, 1)
        }
    else:
        directions = {
            "up": (0, -1),
            "down": (0, 1),
            "left": ( -1, 0),
            "right": (1, 0)
        }
    
    for dir, (dx, dy) in directions.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            yield dir, nx, ny

def propagate(grid, use_8_directions=True):
    w, h = len(grid[0]), len(grid)
    changed = True
    while changed:
        changed = False
        for y in range(h):
            for x in range(w):
                cell = grid[y][x]
                if not cell.collapsed:
                    continue
                tile_name = cell.options[0]
                rules = TILES[tile_name]["rules"]

                for dir, nx, ny in get_neighbors(x, y, w, h, use_8_directions):
                    neighbor = grid[ny][nx]
                    if neighbor.collapsed:
                        continue
                    valid = rules[dir]
                    new_opts = [opt for opt in neighbor.options if opt in valid]
                    if set(new_opts) != set(neighbor.options):
                        neighbor.options = new_opts
                        changed = True
                        if len(new_opts) == 1:
                            collapse_cell(neighbor)

def step(grid, render_fn, use_8_directions=True):
    pos = get_lowest_entropy_cell(grid)
    if pos:
        x, y = pos
        collapse_cell(grid[y][x])
        propagate(grid, use_8_directions)
        render_fn(grid)
    else:
        print("Collapse Complete.")

def run_full_collapse(grid, render_fn, use_8_directions=True):
    while True:
        pos = get_lowest_entropy_cell(grid)
        if not pos:
            break
        x, y = pos
        collapse_cell(grid[y][x])
        propagate(grid)
    render_fn(grid)

def is_fully_collapsed(grid, use_8_directions):
    for row in grid:
        for cell in row:
            if not cell.collapsed:
                return False
    return True
