import pygame
from core.tiles import TILES

# Isometric tile dimensions
TILE_WIDTH = 32       # Base tile width
TILE_HEIGHT = 16      # Base tile height (typically half of width for isometric)
TILE_SPRITE_HEIGHT = 32  # Actual sprite height (may be taller for 3D effect)
CAMERA_SPEED = 5      # pixels per frame when moving camera

def grid_to_screen(grid_x, grid_y, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT, offset_x=0, offset_y=0):
    """Convert grid coordinates to isometric screen coordinates with camera offset"""
    screen_x = (grid_x - grid_y) * (tile_width // 2) + offset_x
    screen_y = (grid_x + grid_y) * (tile_height // 2) + offset_y
    return screen_x, screen_y

def screen_to_grid(screen_x, screen_y, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT, offset_x=0, offset_y=0):
    """Convert screen coordinates back to grid coordinates"""
    adjusted_x = screen_x - offset_x
    adjusted_y = screen_y - offset_y
    grid_x = (adjusted_x / (tile_width // 2) + adjusted_y / (tile_height // 2)) / 2
    grid_y = (adjusted_y / (tile_height // 2) - adjusted_x / (tile_width // 2)) / 2
    return int(grid_x), int(grid_y)

def calculate_camera_offset(grid_width, grid_height, screen_width, screen_height):
    """Calculate camera offset and bounds for the isometric grid"""
    # Calculate the bounds of the isometric grid
    min_x = -(grid_height - 1) * (TILE_WIDTH // 2)
    max_x = (grid_width - 1) * (TILE_WIDTH // 2)
    min_y = 0
    max_y = (grid_width + grid_height - 2) * (TILE_HEIGHT // 2)
    
    # Calculate grid dimensions
    grid_pixel_width = max_x - min_x
    grid_pixel_height = max_y - min_y
    
    # Center the grid (default position)
    default_offset_x = (screen_width - grid_pixel_width) // 2 - min_x
    default_offset_y = (screen_height - grid_pixel_height) // 2
    
    # Calculate camera bounds (how far camera can move)
    max_offset_x = -min_x  # Leftmost position
    min_offset_x = screen_width - max_x - TILE_WIDTH  # Rightmost position
    max_offset_y = 0  # Topmost position
    min_offset_y = screen_height - max_y - TILE_SPRITE_HEIGHT  # Bottommost position
    
    return default_offset_x, default_offset_y, min_offset_x, max_offset_x, min_offset_y, max_offset_y

def handle_camera_movement(keys, camera_x, camera_y, min_x, max_x, min_y, max_y):
    """Handle camera movement with bounds checking"""
    new_camera_x = camera_x
    new_camera_y = camera_y
    
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        new_camera_x = min(camera_x + CAMERA_SPEED, max_x)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        new_camera_x = max(camera_x - CAMERA_SPEED, min_x)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_camera_y = min(camera_y + CAMERA_SPEED, max_y)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_camera_y = max(camera_y - CAMERA_SPEED, min_y)
    
    return new_camera_x, new_camera_y

def get_render_order(grid, camera_offset_x, camera_offset_y, screen_width, screen_height):
    height, width = len(grid), len(grid[0])
    tiles = []
    
    # Calculate camera center in grid coordinates
    screen_center_x = screen_width / 2
    screen_center_y = screen_height / 2
    camera_center_x, camera_center_y = screen_to_grid(screen_center_x, screen_center_y, offset_x=camera_offset_x, offset_y=camera_offset_y)
    
    cull_radius = 50

    for y in range(height):
        for x in range(width):
            distance = abs(x - camera_center_x) + abs(y - camera_center_y)
            if distance <= cull_radius:
                tiles.append((x, y))
    
    tiles.sort(key=lambda pos: (pos[0] + pos[1], pos[1]))
    return tiles

def calculate_tile_elevation(grid, x, y):
    """Calculate elevation based on surrounding tiles"""
    height = 0
    neighbors = []
    
    # Get surrounding tiles (8 directions)
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                if grid[ny][nx].collapsed:
                    neighbors.append(grid[ny][nx].options[0])
    
    # Elevation rules
    current_tile = grid[y][x].options[0]
    
    if current_tile == 'grass':
        grass_count = neighbors.count('grass')
        if grass_count >= 5:
            height = -5
    elif current_tile == 'water':
        height = 10
    elif current_tile == 'stone':
        stone_count = neighbors.count('stone')
        height = -stone_count * 3
    
    return height

def load_isometric_tiles():
    """Load and properly scale isometric tile sprites"""
    TILE_IMAGES = {}
    
    for tile_name, tile_info in TILES.items():
        try:
            # Load original image
            original_image = pygame.image.load(tile_info["sprite"]).convert_alpha()
            
            # Scale to proper isometric dimensions
            # Width stays same, but we preserve aspect ratio for height
            scaled_image = pygame.transform.scale(original_image, (TILE_WIDTH, TILE_SPRITE_HEIGHT))
            
            TILE_IMAGES[tile_name] = scaled_image
            
        except pygame.error as e:
            print(f"Failed to load image for tile '{tile_name}': {e}")
            # Create a fallback diamond-shaped tile
            fallback_surface = pygame.Surface((TILE_WIDTH, TILE_SPRITE_HEIGHT), pygame.SRCALPHA)
            
            # Draw a simple diamond shape as fallback
            diamond_points = [
                (TILE_WIDTH // 2, 0),                    # Top
                (TILE_WIDTH - 1, TILE_HEIGHT),          # Right
                (TILE_WIDTH // 2, TILE_SPRITE_HEIGHT - 1), # Bottom
                (0, TILE_HEIGHT)                         # Left
            ]
            
            # Use tile color from TILES definition
            color = pygame.Color(tile_info.get("color", "gray"))
            pygame.draw.polygon(fallback_surface, color, diamond_points)
            
            TILE_IMAGES[tile_name] = fallback_surface
    
    return TILE_IMAGES

# Cache for tile images to avoid reloading every frame
_TILE_IMAGES_CACHE = None

def render(grid, screen=None, camera_offset=None):
    global _TILE_IMAGES_CACHE
    
    # If no screen provided, run in standalone mode
    if screen is None:
        pygame.init()

        width, height = len(grid[0]), len(grid)
        screen_width, screen_height = 800, 600
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Wave Function Collapse - Isometric Render")

        # Initialize camera for standalone mode
        default_x, default_y, min_x, max_x, min_y, max_y = calculate_camera_offset(
            width, height, screen_width, screen_height
        )
        camera_offset_x, camera_offset_y = default_x, default_y

        # Load tile images
        TILE_IMAGES = load_isometric_tiles()

        clock = pygame.time.Clock()
        running = True

        # Standalone mode with camera movement
        while running:
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Handle camera movement in standalone mode
            camera_offset_x, camera_offset_y = handle_camera_movement(
                keys, camera_offset_x, camera_offset_y, min_x, max_x, min_y, max_y
            )

            # Render frame
            _render_frame(grid, screen, (camera_offset_x, camera_offset_y), TILE_IMAGES)
            
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
    
    else:
        # Integration mode - render single frame
        # Cache tile images for better performance
        if _TILE_IMAGES_CACHE is None:
            _TILE_IMAGES_CACHE = load_isometric_tiles()
        
        _render_frame(grid, screen, camera_offset, _TILE_IMAGES_CACHE)

def _render_frame(grid, screen, camera_offset, tile_images):
    """Internal function to render a single frame"""
    camera_offset_x, camera_offset_y = camera_offset
    screen_width, screen_height = screen.get_size()
    
    screen.fill((50, 50, 50))  # background color

    # Get tiles in proper rendering order
    render_order = get_render_order(grid, camera_offset_x, camera_offset_y, screen_width, screen_height)
        
    for x, y in render_order:
        cell = grid[y][x]
        screen_x, screen_y = grid_to_screen(x, y, offset_x=camera_offset_x, offset_y=camera_offset_y)
        # Adjust Y position for taller sprites
        adjusted_y = screen_y - (TILE_SPRITE_HEIGHT - TILE_HEIGHT)
        rect = pygame.Rect(screen_x, adjusted_y, TILE_WIDTH, TILE_SPRITE_HEIGHT)
        
        if cell.collapsed:
            tile_name = cell.options[0]
            image = tile_images.get(tile_name)
            if image:
                elevation = calculate_tile_elevation(grid, x, y)
                adjusted_y = screen_y - (TILE_SPRITE_HEIGHT - TILE_HEIGHT) + elevation
                rect = pygame.Rect(screen_x, adjusted_y, TILE_WIDTH, TILE_SPRITE_HEIGHT)
                screen.blit(image, rect)
            else:
                # fallback: draw magenta rect if image missing
                pygame.draw.rect(screen, (255, 0, 255), rect)
        else:
            # uncollapsed cell: gray rectangle
            pygame.draw.rect(screen, (100, 100, 100), rect)