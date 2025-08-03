#!/usr/bin/env python3

import pygame
import sys
from critters import WFCMapInterface
from critters.types.stag import StagAgent

def create_test_map():
    """Create a simple test map for the stag."""
    test_map = [
        ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
        ['grass', 'tree', 'grass', 'grass', 'grass', 'grass', 'tree', 'grass'],
        ['grass', 'grass', 'grass', 'stone', 'grass', 'grass', 'grass', 'grass'],
        ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
        ['grass', 'stone', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
        ['grass', 'grass', 'grass', 'grass', 'tree', 'grass', 'grass', 'grass'],
        ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
        ['grass', 'tree', 'grass', 'grass', 'grass', 'grass', 'tree', 'grass']
    ]
    return test_map

def test_stag_creation():
    """Test basic stag creation and initialization."""
    print("Testing stag creation...")
    
    test_map = create_test_map()
    map_interface = WFCMapInterface(test_map, tile_size=64)
    
    try:
        stag = StagAgent((3, 3), map_interface)
        print(f"Stag created successfully: {stag}")
        print(f"Initial energy: {stag.get_energy()}")
        print(f"Initial activity: {stag.get_activity()}")
        print(f"Available actions: {len(stag.available_actions)}")
        return stag, map_interface
    except Exception as e:
        print(f"Stag creation failed: {e}")
        return None, None

def test_stag_planning():
    """Test GOAP planning functionality."""
    print("Testing stag planning...")
    
    stag, map_interface = test_stag_creation()
    if not stag:
        return False
    
    try:
        print(f"Current goal: {stag.current_goal}")
        stag.force_replan()
        print(f"Plan length: {len(stag.current_plan)}")
        if stag.current_plan:
            print(f"First action: {stag.current_plan[0].name}")
        return True
    except Exception as e:
        print(f"Planning test failed: {e}")
        return False

def run_visual_test():
    """Run visual test with pygame window."""
    print("Starting visual test...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Stag Agent Test")
    clock = pygame.time.Clock()
    
    test_map = create_test_map()
    map_interface = WFCMapInterface(test_map, tile_size=64)
    
    try:
        stag = StagAgent((3, 3), map_interface)
        stag.enable_debug(True)
    except Exception as e:
        print(f"Failed to create stag: {e}")
        pygame.quit()
        return
    
    camera_offset = (0, 0)
    running = True
    test_time = 0
    
    while running and test_time < 30:
        dt = clock.tick(60) / 1000.0
        test_time += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    stag.enable_debug(not stag.debug_mode)
                elif event.key == pygame.K_r:
                    stag.force_replan()
        
        stag.update(dt)
        
        screen.fill((34, 139, 34))
        
        for y in range(map_interface.height):
            for x in range(map_interface.width):
                tile_type = map_interface.get_tile_type(x, y)
                world_pos = map_interface.grid_to_world(x, y)
                screen_x = int(world_pos[0] - camera_offset[0])
                screen_y = int(world_pos[1] - camera_offset[1])
                
                color = (34, 139, 34)
                if tile_type == 'tree':
                    color = (0, 100, 0)
                elif tile_type == 'stone':
                    color = (128, 128, 128)
                
                pygame.draw.rect(screen, color, (screen_x, screen_y, 64, 64))
                pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, 64, 64), 1)
        
        stag.render(screen, camera_offset)
        
        font = pygame.font.Font(None, 36)
        info_text = f"Time: {test_time:.1f}s | Energy: {stag.get_energy():.0f} | Activity: {stag.get_activity()}"
        text = font.render(info_text, True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        control_text = "Controls: ESC=Quit, D=Debug, R=Replan"
        control_surface = font.render(control_text, True, (255, 255, 255))
        screen.blit(control_surface, (10, screen.get_height() - 40))
        
        pygame.display.flip()
    
    pygame.quit()
    print("Visual test completed")

def main():
    """Run all stag agent tests."""
    print("Stag Agent Test Suite")
    print("=" * 30)
    
    if not test_stag_creation()[0]:
        print("Basic creation test failed")
        return
    
    if not test_stag_planning():
        print("Planning test failed")
        return
    
    print("Basic tests passed")
    
    try:
        run_visual_test()
    except Exception as e:
        print(f"Visual test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()