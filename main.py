from core.tiles import TILES
from core.wfc import create_grid, get_lowest_entropy_cell, collapse_cell, propagate
from render.pygame_render import render
from critters.types.stag import StagAgent
from critters import WFCMapInterface
import pygame
from render.pygame_render import handle_camera_movement, calculate_camera_offset

def main():
    width, height = 60, 60
    tile_names = list(TILES.keys())
    grid = create_grid(width, height, tile_names)
    
    print("Generating WFC map...")
    while True:
        pos = get_lowest_entropy_cell(grid)
        if not pos:
            print("Collapse Complete.")
            break
        x, y = pos
        collapse_cell(grid[y][x])
        propagate(grid)
    
    print("Initializing pygame...")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("WFC Map with Stag")
    clock = pygame.time.Clock()
    
    print("Creating map interface and stag...")
    map_interface = WFCMapInterface(grid, tile_size=64)
    stag = StagAgent((width//2, height//2), map_interface)
    stag.enable_debug(True)
    
    # Initialize camera system
    grid_width, grid_height = len(grid[0]), len(grid)
    screen_width, screen_height = screen.get_size()
    
    default_x, default_y, min_x, max_x, min_y, max_y = calculate_camera_offset(
        grid_width, grid_height, screen_width, screen_height
    )
    
    # Use a list so it's mutable
    camera_offset = [default_x, default_y]
    
    print("Starting main game loop...")
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()  # Get current key states for camera movement
        
        # Handle camera movement
        camera_offset[0], camera_offset[1] = handle_camera_movement(
            keys, camera_offset[0], camera_offset[1], min_x, max_x, min_y, max_y
        )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        stag.update(dt)
        if hasattr(stag, 'animation_system'):
            print(f"Animation: {stag.animation_system.current_state}")
            print(f"Direction: {stag.animation_system.current_direction}")


        screen.fill((0, 0, 0))
        render(grid, screen, camera_offset)
        stag.render(screen, camera_offset)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()