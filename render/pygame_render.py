import pygame
from core.tiles import TILES

TILE_SIZE = 40  # size of each tile in pixels

def render(grid):
    pygame.init()

    width, height = len(grid[0]), len(grid)

    screen = pygame.display.set_mode((width * TILE_SIZE, height * TILE_SIZE))
    pygame.display.set_caption("Wave Function Collapse - Pygame Render")

    # Preload tile images and scale them
    TILE_IMAGES = {}
    for tile_name, tile_info in TILES.items():
        try:
            image = pygame.image.load(tile_info["sprite"]).convert_alpha()
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            TILE_IMAGES[tile_name] = image
        except pygame.error as e:
            print(f"Failed to load image for tile '{tile_name}': {e}")
            TILE_IMAGES[tile_name] = None

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((50, 50, 50))  # background color

        for y in range(height):
            for x in range(width):
                cell = grid[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if cell.collapsed:
                    tile_name = cell.options[0]
                    image = TILE_IMAGES.get(tile_name)
                    if image:
                        screen.blit(image, rect)
                    else:
                        # fallback: draw magenta rect if image missing
                        pygame.draw.rect(screen, (255, 0, 255), rect)
                else:
                    # uncollapsed cell: gray rectangle
                    pygame.draw.rect(screen, (100, 100, 100), rect)

        pygame.display.flip()
        clock.tick(30)  # limit to 30 FPS

    pygame.quit()
