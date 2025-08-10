from core.tiles import TILES
from core.wfc import create_grid, get_lowest_entropy_cell, collapse_cell, propagate
from render.pygame_render import render
from critters.types.stag import StagAgent
from critters import WFCMapInterface
import pygame
from render.pygame_render import handle_camera_movement, calculate_camera_offset
from core.agent_manager import AgentManager
from core.terrain import generate_complete_terrain

def main():
    width, height = 60, 60

    print("Generating terrain data...")
    terrain_result = generate_complete_terrain(width, height)
    terrain_data = terrain_result['terrain_data']
    constraint_function = terrain_result['constraint_function']

    tile_names = list(TILES.keys())
    grid = create_grid(width, height, tile_names, constraint_function, terrain_data)

    # Debug: Print elevation values for a sample of cells
    print('Sample elevations:')
    for y in range(0, height, max(1, height // 10)):
        for x in range(0, width, max(1, width // 10)):
            print(f'Cell ({x},{y}) elevation: {grid[y][x].elevation}')

    agent_manager = AgentManager()
    print(f'Grid size: {width} x {height}')

    print("Generating WFC map...")
    max_iterations = width * height
    iteration = 0

    while iteration < max_iterations:
        pos = get_lowest_entropy_cell(grid)
        if not pos:
            print("Collapse Complete.")
            break
        x, y = pos
        collapse_cell(grid[y][x])
        propagate(grid)
        iteration += 1

    # Debug: Count collapsed cells after WFC
    collapsed_count = sum(cell.collapsed for row in grid for cell in row)
    print(f'Collapsed cells: {collapsed_count} / {width * height}')
    # Debug: Print collapsed status and tile type for every cell
    for y in range(height):
            # Debug: Print entropy (number of options) for every cell before WFC
            print('Cell entropy before WFC:')
            for y in range(height):
                for x in range(width):
                    cell = grid[y][x]
                    entropy = len(cell.options) if hasattr(cell, 'options') else 'None'
                    print(f"Cell ({x},{y}) entropy: {entropy}")
    for x in range(width):
            cell = grid[y][x]
            if hasattr(cell, 'collapsed'):
                if cell.collapsed:
                    tile_type = cell.options[0] if hasattr(cell, 'options') and cell.options else 'None'
                    print(f"Cell ({x},{y}) COLLAPSED: {tile_type}")
                else:
                    print(f"Cell ({x},{y}) NOT COLLAPSED: options={cell.options if hasattr(cell, 'options') else 'None'}")
            else:
                print(f"Cell ({x},{y}) has no 'collapsed' attribute")
    agent_manager = AgentManager()
    
    print("Generating WFC map...")
    max_iterations = width * height
    iteration = 0

    while iteration < max_iterations:
        pos = get_lowest_entropy_cell(grid)
        if not pos:
            print("Collapse Complete.")
            break
        x, y = pos
        collapse_cell(grid[y][x])
        propagate(grid)
        iteration += 1

    if iteration >= max_iterations:
        print(f"WFC stopped after {max_iterations} iterations - continuing with partial result")
    else:
        print(f"WFC completed successfully after {iteration} iterations")

    print("Initializing pygame...")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("WFC Map with Stag")
    clock = pygame.time.Clock()
    
    print("Creating map interface and stag...")
    map_interface = WFCMapInterface(grid, tile_size=64)
    stag1 = StagAgent((width//2, height//2), map_interface, agent_manager, terrain_data)
    stag2 = StagAgent((width//2 + 3, height//2 + 3), map_interface, agent_manager, terrain_data)
    stag1.enable_debug(True)
    stag2.enable_debug(True)
    
    grid_width, grid_height = len(grid[0]), len(grid)
    screen_width, screen_height = screen.get_size()
    
    default_x, default_y, min_x, max_x, min_y, max_y = calculate_camera_offset(
        grid_width, grid_height, screen_width, screen_height
    )
    
    camera_offset = [default_x, default_y]
    
    print("Starting main game loop...")
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()
        
        camera_offset[0], camera_offset[1] = handle_camera_movement(
            keys, camera_offset[0], camera_offset[1], min_x, max_x, min_y, max_y
        )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        stag1.update(dt)
        stag2.update(dt)

        screen.fill((0, 0, 0))
        render(grid, screen, camera_offset)
        stag1.render(screen, camera_offset)
        stag2.render(screen, camera_offset)

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()