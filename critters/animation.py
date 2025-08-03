import pygame
import os
from typing import Dict, List, Optional


class AnimationSystem:
    """Generic animation system for all NPCs following the standard naming convention."""
    
    def __init__(self, npc_type: str, asset_base_path: str = "assets"):
        """
        Initialize animation system for an NPC type.
        
        Args:
            npc_type: Name of NPC (e.g., "stag", "deer", "villager")
            asset_base_path: Base path to assets folder
        """
        self.npc_type = npc_type
        self.asset_path = os.path.join(asset_base_path, npc_type)
        self.animations: Dict[str, Dict[str, pygame.Surface]] = {}
        
        self.current_state = "idle"
        self.current_direction = "SE"
        self.frame_index = 0
        self.animation_timer = 0.0
        self.frame_duration = 0.2
        
        self.directions = ["NW", "NE", "SE", "SW"]
        self.states = ["idle", "run", "walk"]
        
        self.load_animations()
    
    def load_animations(self):
        """Load all animation sprites for this NPC type."""
        print(f"Loading animations for {self.npc_type} from {self.asset_path}")
        
        for direction in self.directions:
            self.animations[direction] = {}
            
            for state in self.states:
                filename = f"{self.npc_type}_{direction}_{state}.png"
                filepath = os.path.join(self.asset_path, filename)
                
                print(f"Trying to load: {filepath}")
                
                if os.path.exists(filepath):
                    try:
                        sprite_sheet = pygame.image.load(filepath).convert_alpha()
                        frames = self._extract_frames_from_sheet(sprite_sheet)
                        self.animations[direction][state] = frames
                        print(f"Successfully loaded: {filename} with {len(frames)} frames")
                    except pygame.error as e:
                        print(f"Error loading {filepath}: {e}")
                        self.animations[direction][state] = [self._create_fallback_sprite()]
                else:
                    print(f"Animation file not found: {filepath}")
                    self.animations[direction][state] = [self._create_fallback_sprite()]
    
    def _extract_frames_from_sheet(self, sprite_sheet, frame_width=32, frame_height=32):
        """Extract individual frames from a sprite sheet."""
        frames = []
        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()
        
        # Calculate number of frames
        cols = sheet_width // frame_width
        rows = sheet_height // frame_height
        
        for row in range(rows):
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
                
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0), (x, y, frame_width, frame_height))
                frames.append(frame)
        
        # If no frames extracted, return the whole image as one frame
        if not frames:
            frames = [sprite_sheet]
        
        return frames
    
    def _create_fallback_sprite(self) -> pygame.Surface:
        """Create a simple fallback sprite if file loading fails."""
        surface = pygame.Surface((32, 32))
        surface.fill((100, 100, 100))
        return surface
    
    def set_animation(self, state: str, direction: Optional[str] = None):
        """
        Set current animation state and optionally direction.
        
        Args:
            state: Animation state (idle, run, walk)
            direction: Direction (NW, NE, SE, SW)
        """
        if direction and direction in self.directions:
            self.current_direction = direction
        
        if state in self.states and state != self.current_state:
            self.current_state = state
            self.frame_index = 0
            self.animation_timer = 0.0
    
    def update(self, dt: float):
        """
        Update animation timing.
        
        Args:
            dt: Delta time in seconds
        """
        self.animation_timer += dt
        
        if self.animation_timer >= self.frame_duration:
            current_frames = self.get_current_frames()
            if current_frames and len(current_frames) > 1:
                self.frame_index = (self.frame_index + 1) % len(current_frames)
            self.animation_timer = 0.0
    
    def get_current_frames(self) -> list:
        """Get the current animation frame list."""
        if (self.current_direction in self.animations and 
            self.current_state in self.animations[self.current_direction]):
            return self.animations[self.current_direction][self.current_state]
        return [self._create_fallback_sprite()]
    
    def get_current_sprite(self) -> pygame.Surface:
        """
        Get the current animation sprite.
        
        Returns:
            Current sprite to render
        """
        current_frames = self.get_current_frames()
        if current_frames:
            frame_index = min(self.frame_index, len(current_frames) - 1)
            return current_frames[frame_index]
        
        return self._create_fallback_sprite()
    
    def get_direction_from_movement(self, dx: float, dy: float) -> str:
       
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            print(f"No significant movement, keeping current direction: {self.current_direction}")
            return self.current_direction
        
        #print(f"Movement vector: dx={dx:.3f}, dy={dy:.3f}")
        
        # Use magnitude to determine primary direction
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        # If one component is much larger, bias toward cardinal directions
        if abs_dy > abs_dx * 2:  # Mostly vertical movement
            if dy > 0:
                result = "SE" if dx >= 0 else "SW"
            else:
                result = "NE" if dx >= 0 else "NW"
        elif abs_dx > abs_dy * 2:  # Mostly horizontal movement
            if dx > 0:
                result = "SE" if dy >= 0 else "NE"
            else:
                result = "SW" if dy >= 0 else "NW"
        else:  # Diagonal movement
            if dx > 0 and dy > 0:
                result = "SE"
            elif dx > 0 and dy < 0:
                result = "NE"
            elif dx < 0 and dy < 0:
                result = "NW"
            else:  # dx < 0 and dy > 0
                result = "SW"
        
        #print(f"Calculated direction: {result} (abs_dx={abs_dx:.2f}, abs_dy={abs_dy:.2f})")
        return result
    
    def set_frame_duration(self, duration: float):
        """Set animation frame duration."""
        self.frame_duration = max(0.05, duration)
    
    def has_animation(self, state: str, direction: str) -> bool:
        """Check if a specific animation exists."""
        return (direction in self.animations and 
                state in self.animations[direction])
    
    def get_sprite_rect(self) -> pygame.Rect:
        """Get rect for current sprite."""
        sprite = self.get_current_sprite()
        return sprite.get_rect()