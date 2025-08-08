# core/wfc.py

import random
from core.tiles import TILES
from core.tiles import weighted_random_choice
from core.cell import Cell

def create_grid(w, h, tile_names, terrain_constraint_func=None, terrain_data=None):
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            # Assign elevation from terrain_data if available
            elevation = terrain_data.get_height(x, y) if terrain_data else None
            # Apply terrain constraints if provided
            if terrain_constraint_func:
                terrain_valid_tiles = terrain_constraint_func(x, y)
                constrained_tiles = [tile for tile in tile_names if tile in terrain_valid_tiles]
                if not constrained_tiles:
                    constrained_tiles = tile_names
                cell = Cell(constrained_tiles, elevation)
            else:
                cell = Cell(tile_names, elevation)
            row.append(cell)
        grid.append(row)
    return grid

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
#####

def collapse_cell(cell):
    if not cell.options:
        print(f"Error: Trying to collapse cell with no options: {cell.options}")
        cell.collapsed = False
        return
    
    selected_tile = weighted_random_choice(cell.options)

    if selected_tile is None:
        print(f"Error: weighted_random_choice returned None for options: {cell.options}")
        cell.collapsed = False
        return
    
    cell.collapsed = True
    cell.options = [selected_tile]

#####
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
###
def propagate(grid, use_8_directions=True):
    w, h = len(grid[0]), len(grid)
    
    # Single-pass propagation instead of infinite loop
    for y in range(h):
        for x in range(w):
            cell = grid[y][x]
            if not cell.collapsed:
                continue
            
            if not cell.options or cell.options[0] is None:
                continue

            tile_name = cell.options[0]
            rules = TILES[tile_name]["rules"]
            
            for dir_name, nx, ny in get_neighbors(x, y, w, h, use_8_directions):
                neighbor = grid[ny][nx]
                if neighbor.collapsed:
                    continue
                
                valid = rules[dir_name]
                new_opts = [opt for opt in neighbor.options if opt in valid]
                
                if len(new_opts) > 0 and len(new_opts) < len(neighbor.options):
                    neighbor.options = new_opts
                    
                    if len(new_opts) == 1:
                        collapse_cell(neighbor)
#####
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
    max_iterations = len(grid) * len(grid[0]) * 10 # Safety limit
    iteration = 0

    while iteration < max_iterations:
        pos = get_lowest_entropy_cell(grid)
        if not pos:
            break
        x, y = pos
        collapse_cell(grid[y][x])
        propagate(grid, use_8_directions)
        render_fn(grid)
        iteration += 1
    if iteration >= max_iterations:
        print("Warning: Maxium iterations reached. Generation may be incomplete.")

def is_fully_collapsed(grid):
    for row in grid:
        for cell in row:
            if not cell.collapsed:
                return False
    return True
