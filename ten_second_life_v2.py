#!/usr/bin/env python3
"""
10 Second Life: Echoes of a Short World - Version 2.0
A complete redesign with 10 engaging levels and clear progression

Each level introduces one new concept and builds on previous ones.
Clean, simple architecture focused on fun and clarity.
"""

import pygame
import json
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
LIFE_DURATION = 10.0  # 10 seconds per life

# Colors
COLORS = {
    'background': (20, 25, 40),
    'ui_panel': (40, 45, 60),
    'text': (220, 220, 220),
    'success': (100, 255, 100),
    'danger': (255, 100, 100),
    'warning': (255, 200, 100),
    'player': (100, 150, 255),
    'orb': (255, 255, 100),
    'key': (255, 215, 0),
    'door': (139, 69, 19),
    'coin': (255, 215, 0),
    'npc': (150, 100, 255),
    'switch': (100, 255, 150),
    'wall': (80, 80, 80),
    'torch': (255, 100, 50),
    'ice': (150, 200, 255),
    'enemy': (255, 50, 50),
    'crystal': (200, 100, 255)
}

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing" 
    DEATH = "death"
    LEVEL_COMPLETE = "level_complete"
    VICTORY = "victory"

@dataclass
class GameProgress:
    """Tracks overall game progress"""
    current_level: int = 1
    levels_completed: List[int] = None
    total_lives_used: int = 0
    
    def __post_init__(self):
        if self.levels_completed is None:
            self.levels_completed = []

class GameObject:
    """Base class for all game objects"""
    def __init__(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
    
    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Player(GameObject):
    """Enhanced player character with realistic graphics"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 24, 32, COLORS['player'])
        self.speed = 200
        self.inventory = None
        self.start_x = x
        self.start_y = y
        self.animation_time = 0
        self.walking = False
        self.facing_right = True
        self.step_sound_timer = 0
    
    def update(self, dt: float, keys):
        old_x, old_y = self.x, self.y
        self.walking = False
        
        # Movement with direction tracking
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
            self.facing_right = False
            self.walking = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
            self.facing_right = True
            self.walking = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * dt
            self.walking = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * dt
            self.walking = True
        
        # Keep player on screen
        self.x = max(0, min(WINDOW_WIDTH - self.width, self.x))
        self.y = max(0, min(WINDOW_HEIGHT - self.height, self.y))
        
        # Update animation
        if self.walking:
            self.animation_time += dt * 8  # Animation speed
            # Play step sounds
            self.step_sound_timer += dt
            if self.step_sound_timer > 0.4:  # Every 400ms
                pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=self.create_step_sound()))
                self.step_sound_timer = 0
        
        self.update_rect()
    
    def create_step_sound(self):
        """Create a simple step sound"""
        import array
        duration = 0.1
        sample_rate = 22050
        frames = int(duration * sample_rate)
        sound_array = array.array('h', [0] * frames)
        
        for i in range(frames):
            t = float(i) / sample_rate
            # Simple thump sound
            wave = int(8000 * math.sin(2 * math.pi * 100 * t) * math.exp(-t * 15))
            sound_array[i] = wave
        
        return sound_array
    
    def reset_position(self):
        self.x = self.start_x
        self.y = self.start_y
        self.inventory = None
        self.animation_time = 0
        self.walking = False
        self.update_rect()
    
    def draw(self, screen):
        # Draw realistic person character
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Body (torso)
        body_rect = pygame.Rect(self.x + 6, self.y + 12, 12, 16)
        pygame.draw.ellipse(screen, (100, 150, 200), body_rect)
        
        # Head
        head_center = (center_x, self.y + 8)
        pygame.draw.circle(screen, (255, 220, 177), head_center, 6)  # Skin color
        
        # Eyes
        eye_offset = 2 if self.facing_right else -2
        pygame.draw.circle(screen, (0, 0, 0), (center_x - 2 + eye_offset, self.y + 6), 1)
        pygame.draw.circle(screen, (0, 0, 0), (center_x + 2 + eye_offset, self.y + 6), 1)
        
        # Arms with walking animation
        arm_swing = math.sin(self.animation_time) * 3 if self.walking else 0
        # Left arm
        arm1_start = (self.x + 4, self.y + 16)
        arm1_end = (self.x + 2, self.y + 22 + arm_swing)
        pygame.draw.line(screen, (255, 220, 177), arm1_start, arm1_end, 3)
        # Right arm  
        arm2_start = (self.x + 20, self.y + 16)
        arm2_end = (self.x + 22, self.y + 22 - arm_swing)
        pygame.draw.line(screen, (255, 220, 177), arm2_start, arm2_end, 3)
        
        # Legs with walking animation
        leg_swing = math.sin(self.animation_time + math.pi) * 4 if self.walking else 0
        # Left leg
        leg1_start = (self.x + 8, self.y + 26)
        leg1_end = (self.x + 6 + leg_swing, self.y + 32)
        pygame.draw.line(screen, (50, 50, 150), leg1_start, leg1_end, 4)  # Blue pants
        # Right leg
        leg2_start = (self.x + 16, self.y + 26)
        leg2_end = (self.x + 18 - leg_swing, self.y + 32)
        pygame.draw.line(screen, (50, 50, 150), leg2_start, leg2_end, 4)
        
        # Draw inventory item if holding something
        if self.inventory:
            item_x = self.x + (20 if self.facing_right else 0)
            item_y = self.y + 18
            
            if self.inventory == 'key':
                # Draw key in hand
                pygame.draw.rect(screen, (255, 215, 0), (item_x, item_y, 8, 3))
                pygame.draw.circle(screen, (255, 215, 0), (item_x + 8, item_y + 1), 3)
            elif self.inventory == 'coin':
                # Draw coin in hand
                pygame.draw.circle(screen, (255, 215, 0), (item_x + 4, item_y + 2), 4)
                pygame.draw.circle(screen, (255, 235, 100), (item_x + 4, item_y + 2), 2)
        
        # Subtle glow around character
        glow_surf = pygame.Surface((self.width + 8, self.height + 8), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (100, 150, 255, 30), (0, 0, self.width + 8, self.height + 8))
        screen.blit(glow_surf, (self.x - 4, self.y - 4))

class Item(GameObject):
    """Enhanced collectible items with realistic graphics and sounds"""
    def __init__(self, x: int, y: int, item_type: str):
        color = COLORS.get(item_type, COLORS['orb'])
        super().__init__(x, y, 20, 20, color)
        self.type = item_type
        self.collected = False
        self.glow_time = 0
        self.sparkle_timer = 0
    
    def update(self, dt: float):
        self.glow_time += dt * 3
        self.sparkle_timer += dt
    
    def collect(self):
        """Collect the item with sound effect"""
        if not self.collected:
            self.collected = True
            self.play_collect_sound()
    
    def play_collect_sound(self):
        """Play collection sound effect"""
        try:
            import array
            duration = 0.3
            sample_rate = 22050
            frames = int(duration * sample_rate)
            sound_array = array.array('h', [0] * frames)
            
            for i in range(frames):
                t = float(i) / sample_rate
                if self.type == 'orb':
                    # Magical chime for orb
                    wave = int(12000 * math.sin(2 * math.pi * 440 * t) * math.exp(-t * 3))
                    wave += int(8000 * math.sin(2 * math.pi * 880 * t) * math.exp(-t * 4))
                elif self.type == 'key':
                    # Metallic clink for key
                    wave = int(10000 * math.sin(2 * math.pi * 800 * t) * math.exp(-t * 5))
                    wave += int(6000 * math.sin(2 * math.pi * 1200 * t) * math.exp(-t * 8))
                elif self.type == 'coin':
                    # Coin ding sound
                    wave = int(15000 * math.sin(2 * math.pi * 1000 * t) * math.exp(-t * 2))
                    wave += int(10000 * math.sin(2 * math.pi * 1500 * t) * math.exp(-t * 3))
                else:
                    # Default pickup sound
                    wave = int(10000 * math.sin(2 * math.pi * 600 * t) * math.exp(-t * 4))
                
                sound_array[i] = wave
            
            sound = pygame.mixer.Sound(buffer=sound_array)
            sound.set_volume(0.7)
            sound.play()
        except:
            pass  # Silently fail if sound creation fails
    
    def draw(self, screen):
        if not self.collected:
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Enhanced glow effect
            glow_intensity = 0.8 + 0.4 * math.sin(self.glow_time)
            glow_radius = int(15 + 5 * math.sin(self.glow_time * 1.5))
            
            # Multiple glow layers for depth
            for i in range(3):
                alpha = int(40 * glow_intensity * (3 - i) / 3)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha), 
                                 (glow_radius, glow_radius), glow_radius - i * 3)
                screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))
            
            # Draw specific item types
            if self.type == 'orb':
                # Magical orb with inner light
                pygame.draw.circle(screen, self.color, (center_x, center_y), 8)
                pygame.draw.circle(screen, (255, 255, 200), (center_x - 2, center_y - 2), 4)
                pygame.draw.circle(screen, (255, 255, 255), (center_x - 3, center_y - 3), 2)
                
            elif self.type == 'key':
                # Detailed golden key
                # Key shaft
                pygame.draw.rect(screen, (255, 215, 0), (center_x - 6, center_y - 1, 10, 3))
                # Key head
                pygame.draw.circle(screen, (255, 215, 0), (center_x + 5, center_y), 4)
                pygame.draw.circle(screen, (255, 235, 100), (center_x + 5, center_y), 2)
                # Key teeth
                pygame.draw.rect(screen, (255, 215, 0), (center_x - 4, center_y + 1, 2, 3))
                pygame.draw.rect(screen, (255, 215, 0), (center_x - 1, center_y + 1, 2, 2))
                
            elif self.type == 'coin':
                # Shiny golden coin
                pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), 8)
                pygame.draw.circle(screen, (255, 235, 100), (center_x, center_y), 6)
                pygame.draw.circle(screen, (255, 245, 150), (center_x - 2, center_y - 2), 3)
                # Add sparkle effect
                if int(self.sparkle_timer * 10) % 20 < 10:
                    pygame.draw.circle(screen, (255, 255, 255), (center_x + 3, center_y - 3), 1)
            
            else:
                # Default item appearance
                pygame.draw.circle(screen, self.color, (center_x, center_y), 8)

class Door(GameObject):
    """Enhanced doors with realistic graphics and sounds"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 30, 50, COLORS['door'])
        self.is_open = False
        self.requires_key = True
    
    def open_door(self):
        """Open the door with sound effect"""
        if not self.is_open:
            self.is_open = True
            self.play_door_sound()
    
    def play_door_sound(self):
        """Play door opening sound"""
        try:
            import array
            duration = 0.8
            sample_rate = 22050
            frames = int(duration * sample_rate)
            sound_array = array.array('h', [0] * frames)
            
            for i in range(frames):
                t = float(i) / sample_rate
                # Creaking wood sound
                creak_freq = 150 + 30 * math.sin(2 * math.pi * 2 * t)
                wave = int(8000 * math.sin(2 * math.pi * creak_freq * t) * math.exp(-t * 1.5))
                # Add some noise for realism
                noise = int(2000 * (random.random() - 0.5) * math.exp(-t * 2))
                sound_array[i] = wave + noise
            
            sound = pygame.mixer.Sound(buffer=sound_array)
            sound.set_volume(0.6)
            sound.play()
        except:
            pass
    
    def draw(self, screen):
        if not self.is_open:
            # Enhanced door graphics
            # Door frame
            frame_rect = pygame.Rect(self.x - 2, self.y - 2, self.width + 4, self.height + 4)
            pygame.draw.rect(screen, (80, 60, 40), frame_rect)
            
            # Door body with wood texture
            door_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(screen, (101, 67, 33), door_rect)
            
            # Wood grain lines
            for i in range(0, self.height, 8):
                line_y = self.y + i
                pygame.draw.line(screen, (90, 60, 30), (self.x + 2, line_y), (self.x + self.width - 2, line_y), 1)
            
            # Door panels
            panel1 = pygame.Rect(self.x + 3, self.y + 5, self.width - 6, self.height//2 - 8)
            panel2 = pygame.Rect(self.x + 3, self.y + self.height//2 + 3, self.width - 6, self.height//2 - 8)
            pygame.draw.rect(screen, (101, 67, 33), panel1, 2)
            pygame.draw.rect(screen, (101, 67, 33), panel2, 2)
            
            # Door handle
            handle_center = (self.x + self.width - 6, self.y + self.height//2)
            pygame.draw.circle(screen, (184, 134, 11), handle_center, 4)
            pygame.draw.circle(screen, (200, 150, 20), handle_center, 2)

class NPC(GameObject):
    """Non-player characters"""
    def __init__(self, x: int, y: int, name: str, dialogue: List[str]):
        super().__init__(x, y, 25, 25, COLORS['npc'])
        self.name = name
        self.dialogue = dialogue
        self.talked_to = False
    
    def draw(self, screen):
        super().draw(screen)
        # Draw name above NPC
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, COLORS['text'])
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y - 15))
        screen.blit(text, text_rect)

class Level:
    """Base class for all levels"""
    def __init__(self, number: int, title: str, objective: str):
        self.number = number
        self.title = title
        self.objective = objective
        self.completed = False
        self.objects = []
        self.items = []
        self.npcs = []
        self.doors = []
        self.walls = []
    
    def setup(self):
        """Override in subclasses to set up level-specific content"""
        pass
    
    def update(self, dt: float, player: Player) -> bool:
        """Update level logic. Return True if level is complete."""
        for item in self.items:
            item.update(dt)
        return False
    
    def handle_interaction(self, player: Player) -> Optional[str]:
        """Handle player interactions. Return message if any."""
        return None
    
    def draw(self, screen):
        """Draw all level objects"""
        for wall in self.walls:
            wall.draw(screen)
        for door in self.doors:
            door.draw(screen)
        for item in self.items:
            item.draw(screen)
        for npc in self.npcs:
            npc.draw(screen)

class Level1_FirstSteps(Level):
    """Level 1: Learn basic movement and interaction"""
    def __init__(self):
        super().__init__(1, "First Steps", "Collect the glowing orb to begin your journey")
        self.setup()
    
    def setup(self):
        # Place a glowing orb in the center
        orb = Item(WINDOW_WIDTH//2 - 7, WINDOW_HEIGHT//2 - 7, 'orb')
        self.items.append(orb)
    
    def update(self, dt: float, player: Player) -> bool:
        super().update(dt, player)
        # Check if orb is collected
        for item in self.items:
            if not item.collected and player.rect.colliderect(item.rect):
                item.collected = True
                return True  # Level complete
        return False
    
    def handle_interaction(self, player: Player) -> Optional[str]:
        # Auto-collect orb on contact
        return None

class Level2_TheDoor(Level):
    """Level 2: Preparation Opens Opportunities"""
    def __init__(self):
        super().__init__(2, "The Door", "Find the key and unlock the door")
        self.lesson = "Opportunities exist everywhere, but preparation is the key that opens doors to success. Education, skills, and readiness unlock possibilities in life."
        self.setup()
    
    def setup(self):
        # Place key on left side
        key = Item(100, WINDOW_HEIGHT//2, 'key')
        self.items.append(key)
        
        # Place door on right side
        door = Door(WINDOW_WIDTH - 100, WINDOW_HEIGHT//2 - 25)
        self.doors.append(door)
    
    def update(self, dt: float, player: Player) -> bool:
        super().update(dt, player)
        
        # Check if key is collected
        for item in self.items:
            if not item.collected and player.rect.colliderect(item.rect):
                item.collect()
                player.inventory = 'key'
        
        # Check if door is opened and player walks through
        for door in self.doors:
            if door.is_open and player.rect.colliderect(door.rect):
                return True  # Level complete
        
        return False
    
    def handle_interaction(self, player: Player) -> Optional[str]:
        # Check door interaction
        for door in self.doors:
            if player.rect.colliderect(door.rect) and not door.is_open:
                if player.inventory == 'key':
                    door.open_door()
                    player.inventory = None
                    return "Door unlocked! Walk through to continue."
                else:
                    return "This door is locked. Find the key first!"
        return None

class Level3_TimePressure(Level):
    """Level 3: Urgency Creates Focus"""
    def __init__(self):
        super().__init__(3, "Time Pressure", "Collect all 3 coins before time runs out!")
        self.lesson = "Deadlines force us to prioritize and focus on what truly matters. Time pressure can be a powerful motivator that helps us achieve more than we thought possible."
        self.coins_needed = 3
        self.coins_collected = 0
        self.setup()
    
    def setup(self):
        # Place 3 coins in different locations
        coin1 = Item(150, 200, 'coin')
        coin2 = Item(WINDOW_WIDTH - 150, 300, 'coin')
        coin3 = Item(WINDOW_WIDTH//2, 500, 'coin')
        
        self.items.extend([coin1, coin2, coin3])
    
    def update(self, dt: float, player: Player) -> bool:
        super().update(dt, player)
        
        # Check coin collection
        for item in self.items:
            if not item.collected and player.rect.colliderect(item.rect):
                item.collect()
                self.coins_collected += 1
                
                # Play encouraging sound for each coin
                if self.coins_collected == self.coins_needed:
                    # Victory sound when all coins collected
                    self.play_victory_sound()
        
        # Level complete when all coins collected
        return self.coins_collected >= self.coins_needed
    
    def play_victory_sound(self):
        """Play victory fanfare"""
        try:
            import array
            duration = 1.0
            sample_rate = 22050
            frames = int(duration * sample_rate)
            sound_array = array.array('h', [0] * frames)
            
            # Victory chord progression
            notes = [261.63, 329.63, 392.00, 523.25]  # C major chord
            
            for i in range(frames):
                t = float(i) / sample_rate
                wave = 0
                for j, freq in enumerate(notes):
                    delay = j * 0.1
                    if t > delay:
                        note_t = t - delay
                        amplitude = 8000 * math.exp(-note_t * 2)
                        wave += amplitude * math.sin(2 * math.pi * freq * note_t)
                
                sound_array[i] = int(wave / len(notes))
            
            sound = pygame.mixer.Sound(buffer=sound_array)
            sound.set_volume(0.8)
            sound.play()
        except:
            pass
    
    def get_progress_message(self) -> str:
        """Get current progress message"""
        remaining = self.coins_needed - self.coins_collected
        if remaining > 0:
            return f"Collect {remaining} more coin{'s' if remaining > 1 else ''}!"
        else:
            return "All coins collected! Well done!"
    
    def handle_interaction(self, player: Player) -> Optional[str]:
        return self.get_progress_message()

class TenSecondLifeGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("10 Second Life: Echoes of a Short World v2.0")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = GameState.MENU
        self.timer = 10.0
        self.lives_lived = 0
        self.current_level_num = 1
        self.message = ""
        self.message_timer = 0
        self.level_complete = False
        self.show_lesson = False
        self.lesson_timer = 0
        self.lesson_text = ""
        self.next_level_ready = False
        
        # Game objects
        self.player = Player(50, WINDOW_HEIGHT//2)
        self.current_level = None
        self.levels = {
            1: Level1_FirstSteps(),
            2: Level2_TheDoor(),
            3: Level3_TimePressure()
        }
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Load current level
        self.load_level(self.progress.current_level)
    
    def load_level(self, level_number: int):
        """Load a specific level"""
        if level_number in self.levels:
            self.current_level = self.levels[level_number]
            self.player.reset_position()
            self.life_timer = LIFE_DURATION
            self.message = f"Level {level_number}: {self.current_level.title}"
            self.message_timer = 3.0
    
    def start_new_life(self):
        """Start a new 10-second life"""
        self.state = GameState.PLAYING
        self.life_timer = LIFE_DURATION
        self.progress.total_lives_used += 1
        self.player.reset_position()
    
    def complete_level(self):
        """Handle level completion"""
        self.state = GameState.LEVEL_COMPLETE
        self.current_level.completed = True
        if self.progress.current_level not in self.progress.levels_completed:
            self.progress.levels_completed.append(self.progress.current_level)
        
        # Check if this was the final level
        if self.progress.current_level >= len(self.levels):
            self.state = GameState.VICTORY
        else:
            self.message = f"Level {self.progress.current_level} Complete!"
            self.message_timer = 3.0
    
    def next_level(self):
        """Advance to next level"""
        self.progress.current_level += 1
        if self.progress.current_level <= len(self.levels):
            self.load_level(self.progress.current_level)
            self.state = GameState.PLAYING
        else:
            self.state = GameState.VICTORY
    
    def update(self, dt: float):
        """Main game update loop"""
        if self.state == GameState.PLAYING:
            # Update timer
            self.life_timer -= dt
            if self.life_timer <= 0:
                self.state = GameState.DEATH
                return
            
            # Update player
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys)
            
            # Update current level
            if self.current_level:
                if self.current_level.update(dt, self.player):
                    self.complete_level()
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_new_life()
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_e or event.key == pygame.K_SPACE:
                        if self.current_level:
                            msg = self.current_level.handle_interaction(self.player)
                            if msg:
                                self.message = msg
                                self.message_timer = 2.0
                    elif event.key == pygame.K_r:
                        # Reset to beginning of current level
                        self.load_level(self.progress.current_level)
                        self.start_new_life()
                
                elif self.state == GameState.DEATH:
                    if event.key == pygame.K_SPACE:
                        self.start_new_life()
                    elif event.key == pygame.K_r:
                        self.load_level(self.progress.current_level)
                        self.start_new_life()
                
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_SPACE:
                        self.next_level()
    
    def draw_ui(self):
        """Draw user interface"""
        # Timer
        timer_text = f"Time: {self.life_timer:.1f}s"
        timer_color = COLORS['danger'] if self.life_timer < 3 else COLORS['text']
        timer_surface = self.font_medium.render(timer_text, True, timer_color)
        self.screen.blit(timer_surface, (10, 10))
        
        # Level info
        if self.current_level:
            level_text = f"Level {self.current_level.number}: {self.current_level.title}"
            level_surface = self.font_small.render(level_text, True, COLORS['text'])
            self.screen.blit(level_surface, (10, 50))
            
            # Objective
            obj_surface = self.font_small.render(self.current_level.objective, True, COLORS['warning'])
            self.screen.blit(obj_surface, (10, 75))
        
        # Lives used
        lives_text = f"Lives Used: {self.progress.total_lives_used}"
        lives_surface = self.font_small.render(lives_text, True, COLORS['text'])
        self.screen.blit(lives_surface, (WINDOW_WIDTH - 150, 10))
        
        # Player inventory
        if self.player.inventory:
            inv_text = f"Carrying: {self.player.inventory}"
            inv_surface = self.font_small.render(inv_text, True, COLORS['success'])
            self.screen.blit(inv_surface, (10, WINDOW_HEIGHT - 30))
        
        # Message
        if self.message:
            msg_surface = self.font_medium.render(self.message, True, COLORS['warning'])
            msg_rect = msg_surface.get_rect(center=(WINDOW_WIDTH//2, 150))
            # Background
            bg_rect = pygame.Rect(msg_rect.x - 10, msg_rect.y - 5, msg_rect.width + 20, msg_rect.height + 10)
            pygame.draw.rect(self.screen, COLORS['ui_panel'], bg_rect)
            self.screen.blit(msg_surface, msg_rect)
    
    def draw_menu(self):
        """Draw main menu"""
        title = self.font_large.render("10 Second Life", True, COLORS['text'])
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Echoes of a Short World v2.0", True, COLORS['warning'])
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60))
        self.screen.blit(subtitle, subtitle_rect)
        
        instruction = self.font_medium.render("Press SPACE to begin your journey", True, COLORS['success'])
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_death_screen(self):
        """Draw death screen"""
        death_text = self.font_large.render("Life Ended", True, COLORS['danger'])
        death_rect = death_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        self.screen.blit(death_text, death_rect)
        
        continue_text = self.font_medium.render("Press SPACE for new life", True, COLORS['text'])
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(continue_text, continue_rect)
        
        reset_text = self.font_small.render("Press R to reset level", True, COLORS['warning'])
        reset_rect = reset_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 30))
        self.screen.blit(reset_text, reset_rect)
    
    def draw_level_complete(self):
        """Draw level complete screen"""
        complete_text = self.font_large.render("Level Complete!", True, COLORS['success'])
        complete_rect = complete_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        self.screen.blit(complete_text, complete_rect)
        
        continue_text = self.font_medium.render("Press SPACE to continue", True, COLORS['text'])
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_victory(self):
        """Draw victory screen"""
        victory_text = self.font_large.render("Congratulations!", True, COLORS['success'])
        victory_rect = victory_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        self.screen.blit(victory_text, victory_rect)
        
        stats_text = f"Completed in {self.progress.total_lives_used} lives"
        stats_surface = self.font_medium.render(stats_text, True, COLORS['text'])
        stats_rect = stats_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(stats_surface, stats_rect)
    
    def draw(self):
        """Main draw method"""
        self.screen.fill(COLORS['background'])
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            if self.current_level:
                self.current_level.draw(self.screen)
            self.player.draw(self.screen)
            self.draw_ui()
        elif self.state == GameState.DEATH:
            if self.current_level:
                self.current_level.draw(self.screen)
            self.player.draw(self.screen)
            self.draw_death_screen()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete()
        elif self.state == GameState.VICTORY:
            self.draw_victory()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    game = TenSecondLifeGame()
    game.run()
