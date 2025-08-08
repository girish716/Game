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
    MENU = 1
    PLAYING = 2
    DEATH = 3
    LEVEL_COMPLETE = 4
    VICTORY = 5
    GAME_OVER = 6

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
    """Level 1: Taking Initiative"""
    def __init__(self):
        super().__init__(1, "First Steps", "Collect the glowing orb to begin your journey")
        self.lesson = "Success begins with taking the first step. Every journey starts with action. In life, the hardest part is often just getting started."
        self.setup()
    
    def setup(self):
        # Place a glowing orb in the center
        orb = Item(WINDOW_WIDTH//2 - 10, WINDOW_HEIGHT//2 - 10, 'orb')
        self.items.append(orb)
    
    def update(self, dt: float, player: Player) -> bool:
        super().update(dt, player)
        # Check if orb is collected
        for item in self.items:
            if not item.collected and player.rect.colliderect(item.rect):
                item.collect()  # Use proper collect method with sound
                return True  # Level complete
        return False
    
    def handle_interaction(self, player: Player) -> Optional[str]:
        # Auto-collect orb on contact, no manual interaction needed
        return "Walk into the orb to collect it!"

class Level2_TheDoor(Level):
    """Level 2: Preparation Opens Opportunities"""
    def __init__(self):
        super().__init__(2, "The Door", "Find the key and unlock the door")
        self.lesson = "Opportunities exist everywhere, but preparation is the key that opens doors to success. Education, skills, and readiness unlock possibilities in life."
        self.key_collected = False
        self.door_unlocked = False
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
                self.key_collected = True
        
        # Check if door is opened and player walks through
        for door in self.doors:
            if door.is_open and player.rect.colliderect(door.rect):
                return True  # Level complete
        
        return False
    
    def get_current_objective(self) -> str:
        """Get the current objective based on progress"""
        if not self.key_collected:
            return "Find and collect the golden key"
        elif not self.door_unlocked:
            return "Press SPACE near the door to unlock it"
        else:
            return "Walk through the open door to complete the level"
    
    def handle_interaction(self, player: Player) -> Optional[str]:
        # Check door interaction
        for door in self.doors:
            if player.rect.colliderect(door.rect) or self.is_near_door(player, door):
                if not door.is_open:
                    if player.inventory == 'key':
                        door.open_door()
                        player.inventory = None
                        self.door_unlocked = True
                        return "Door unlocked! Walk through to continue."
                    else:
                        return "This door is locked. Find the key first!"
                elif door.is_open:
                    return "Walk through the open door to complete the level!"
        return None
    
    def is_near_door(self, player: Player, door: Door) -> bool:
        """Check if player is near the door for interaction"""
        distance_x = abs(player.x - door.x)
        distance_y = abs(player.y - door.y)
        return distance_x < 60 and distance_y < 60

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
        
        # Global 3-lives system
        self.total_lives = 3  # Total lives for entire game
        self.lives_remaining = 3  # Current lives remaining
        self.show_motivation = False
        self.motivation_quote = ""
        
        # Motivational quotes for second chances
        self.motivation_quotes = [
            "Every master was once a disaster. Your second chance is your opportunity to shine!",
            "Failure is not the opposite of success, it's part of success. Try again with wisdom!",
            "The comeback is always stronger than the setback. You've got this!",
            "Success is not final, failure is not fatal. It's the courage to continue that counts.",
            "A second chance doesn't mean you're weak. It means you're strong enough to try again.",
            "Every expert was once a beginner. Every pro was once an amateur. Keep going!",
            "Your greatest glory lies not in never falling, but in rising every time you fall.",
            "Mistakes are proof that you are trying. Learn, adapt, and conquer!",
            "The phoenix rises from the ashes stronger than before. This is your moment!",
            "Champions are made from something deep inside - the will to win, the will to try again."
        ]
        
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
        self.load_level(self.current_level_num)
    
    def load_level(self, level_number: int):
        """Load a specific level"""
        if level_number in self.levels:
            self.current_level = self.levels[level_number]
            self.current_level_num = level_number
            self.player.reset_position()
            self.timer = 10.0
            self.level_complete = False
            self.show_lesson = False
            self.next_level_ready = False
    
    def handle_level_failure(self):
        """Handle when player fails a level (time runs out)"""
        self.lives_remaining -= 1
        
        if self.lives_remaining > 0:
            # Still have lives left - show motivational quote and continue
            self.motivation_quote = random.choice(self.motivation_quotes)
            self.show_motivation = True
            self.state = GameState.DEATH
        else:
            # No lives left - game over
            self.state = GameState.GAME_OVER
    
    def restart_level_completely(self):
        """Completely restart the current level (no progress preservation)"""
        # Recreate the current level to reset all progress
        if self.current_level_num == 1:
            self.levels[1] = Level1_FirstSteps()
        elif self.current_level_num == 2:
            self.levels[2] = Level2_TheDoor()
        elif self.current_level_num == 3:
            self.levels[3] = Level3_TimePressure()
        
        # Load the fresh level
        self.current_level = self.levels[self.current_level_num]
        
        # Reset player completely
        self.player.reset_position()
        self.player.inventory = None
        
        # Reset game state
        self.timer = 10.0
        self.lives_lived += 1
        self.show_motivation = False
        self.motivation_quote = ""
    
    def reset_entire_game(self):
        """Completely reset the entire game to initial state"""
        # Reset all game state
        self.current_level_num = 1
        self.lives_lived = 0
        self.timer = 10.0
        self.level_complete = False
        self.show_lesson = False
        self.lesson_timer = 0
        self.lesson_text = ""
        self.next_level_ready = False
        self.message = ""
        self.message_timer = 0
        
        # Reset global lives system
        self.lives_remaining = 3  # Reset to full 3 lives
        self.show_motivation = False
        self.motivation_quote = ""
        
        # Reset player completely
        self.player.reset_position()
        self.player.inventory = None
        
        # Recreate all levels to reset their state
        self.levels = {
            1: Level1_FirstSteps(),
            2: Level2_TheDoor(),
            3: Level3_TimePressure()
        }
        
        # Load Level 1
        self.load_level(1)
    
    def show_level_lesson(self):
        """Display the life lesson for the current level"""
        if self.current_level and hasattr(self.current_level, 'lesson'):
            self.lesson_text = self.current_level.lesson
            self.show_lesson = True
            self.lesson_timer = 5.0  # Show lesson for 5 seconds
            # Check if there's a next level
            next_level = self.current_level_num + 1
            if next_level in self.levels:
                self.next_level_ready = True
    
    def advance_to_next_level(self):
        """Advance to the next level"""
        next_level = self.current_level_num + 1
        if next_level in self.levels:
            self.load_level(next_level)
            self.state = GameState.PLAYING
        else:
            # No more levels - show victory
            self.state = GameState.VICTORY
    
    def restart_game(self):
        """Restart the entire game from Level 1"""
        # Reset all game state
        self.current_level_num = 1
        self.lives_lived = 0
        self.timer = 10.0
        self.level_complete = False
        self.show_lesson = False
        self.lesson_timer = 0
        self.lesson_text = ""
        self.next_level_ready = False
        self.message = ""
        self.message_timer = 0
        
        # Reset player
        self.player.reset_position()
        self.player.inventory = None
        
        # Recreate all levels to reset their state
        self.levels = {
            1: Level1_FirstSteps(),
            2: Level2_TheDoor(),
            3: Level3_TimePressure()
        }
        
        # Load Level 1
        self.load_level(1)
        self.state = GameState.PLAYING
    
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
            self.timer -= dt
            if self.timer <= 0:
                self.handle_level_failure()
                return
            
            # Update player
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys)
            
            # Update current level
            if self.current_level:
                if self.current_level.update(dt, self.player):
                    self.level_complete = True
                    self.show_level_lesson()
                    self.state = GameState.LEVEL_COMPLETE
        
        elif self.state == GameState.LEVEL_COMPLETE:
            # Handle lesson display - wait for user input instead of auto-advancing
            if self.show_lesson:
                # Lesson stays on screen until user presses SPACE
                pass
        
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
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.MENU:
                        self.running = False
                    else:
                        # Reset entire game when returning to menu from any state
                        self.reset_entire_game()
                        self.state = GameState.MENU
                
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                        self.timer = 10.0
                        self.lives_lived += 1
                    elif self.state == GameState.DEATH:
                        # Restart current level completely (no progress preservation)
                        self.restart_level_completely()
                        self.state = GameState.PLAYING
                    elif self.state == GameState.LEVEL_COMPLETE:
                        # Advance to next level or victory
                        if self.next_level_ready:
                            self.advance_to_next_level()
                        else:
                            self.state = GameState.VICTORY
                    elif self.state == GameState.VICTORY:
                        # Play again - restart the entire game
                        self.restart_game()
                    elif self.state == GameState.GAME_OVER:
                        # Return to main menu and completely reset game
                        self.reset_entire_game()
                        self.state = GameState.MENU
                    elif self.state == GameState.PLAYING and self.current_level:
                        # Use SPACE for interactions
                        interaction_result = self.current_level.handle_interaction(self.player)
                        if interaction_result:
                            self.message = interaction_result
                            self.message_timer = 2.0
                
                # E key removed - now using SPACE for all interactions
                
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_SPACE:
                        self.next_level()
    
    def draw_ui(self):
        """Draw game UI elements"""
        # Timer (circular)
        timer_center = (WINDOW_WIDTH - 60, 60)
        timer_radius = 30
        timer_progress = self.timer / 10.0
        
        # Timer background
        pygame.draw.circle(self.screen, (50, 50, 50), timer_center, timer_radius + 3)
        pygame.draw.circle(self.screen, (20, 20, 20), timer_center, timer_radius)
        
        # Timer fill (red when low)
        if timer_progress > 0.3:
            timer_color = (100, 200, 100)
        elif timer_progress > 0.1:
            timer_color = (200, 200, 100)
        else:
            timer_color = (200, 100, 100)
        
        # Draw timer arc
        if timer_progress > 0:
            end_angle = -90 + (360 * (1 - timer_progress))
            points = [timer_center]
            for angle in range(-90, int(end_angle) + 1, 5):
                x = timer_center[0] + timer_radius * math.cos(math.radians(angle))
                y = timer_center[1] + timer_radius * math.sin(math.radians(angle))
                points.append((x, y))
            if len(points) > 2:
                pygame.draw.polygon(self.screen, timer_color, points)
        
        # Timer text
        timer_text = f"{int(self.timer)}"
        text_surface = self.font_medium.render(timer_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=timer_center)
        self.screen.blit(text_surface, text_rect)
        
        # Level info
        if self.current_level:
            level_text = f"Level {self.current_level_num}: {self.current_level.title}"
            level_surface = self.font_medium.render(level_text, True, (255, 255, 255))
            self.screen.blit(level_surface, (20, 20))
            
            # Current objective (dynamic based on level progress)
            if hasattr(self.current_level, 'get_current_objective'):
                obj_text = f"Objective: {self.current_level.get_current_objective()}"
            else:
                obj_text = f"Objective: {self.current_level.objective}"
            obj_surface = self.font_small.render(obj_text, True, (200, 255, 200))
            self.screen.blit(obj_surface, (20, 50))
            
            # Player inventory status
            if self.player.inventory:
                inv_text = f"Carrying: {self.player.inventory.title()}"
                inv_surface = self.font_small.render(inv_text, True, (255, 255, 100))
                self.screen.blit(inv_surface, (20, 75))
                
                # Key indicator with icon
                if self.player.inventory == 'key':
                    # Draw small key icon
                    key_x, key_y = 150, 77
                    pygame.draw.rect(self.screen, (255, 215, 0), (key_x, key_y, 8, 2))
                    pygame.draw.circle(self.screen, (255, 215, 0), (key_x + 9, key_y + 1), 3)
                    pygame.draw.circle(self.screen, (255, 235, 100), (key_x + 9, key_y + 1), 1)
            
            # Interaction hint
            if self.current_level_num == 2:  # Level 2 specific hints
                if hasattr(self.current_level, 'key_collected') and self.current_level.key_collected:
                    if not hasattr(self.current_level, 'door_unlocked') or not self.current_level.door_unlocked:
                        hint_text = "Press SPACE near the door to unlock it!"
                        hint_surface = self.font_small.render(hint_text, True, (100, 255, 100))
                        self.screen.blit(hint_surface, (20, 100))
        
        # Lives remaining counter
        lives_text = f"Lives: {self.lives_remaining}/{self.total_lives}"
        lives_surface = self.font_small.render(lives_text, True, (200, 255, 200))
        self.screen.blit(lives_surface, (10, WINDOW_HEIGHT - 30))
        
        # Message display
        if self.message_timer > 0:
            msg_surface = self.font_medium.render(self.message, True, (255, 255, 100))
            msg_rect = msg_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100))
            
            # Message background
            bg_rect = pygame.Rect(msg_rect.x - 20, msg_rect.y - 10, msg_rect.width + 40, msg_rect.height + 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(self.screen, (255, 255, 100), bg_rect, 2)
            
            self.screen.blit(msg_surface, msg_rect)
    
    def draw_lesson_screen(self):
        """Draw the life lesson screen after level completion"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Main lesson panel
        panel_width = WINDOW_WIDTH - 100
        panel_height = 400
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Panel background with gradient effect
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100, 150, 200), panel_rect, 3, border_radius=15)
        
        # "Level Complete!" title
        title_text = f"Level {self.current_level_num} Complete!"
        title_surface = self.font_large.render(title_text, True, (255, 255, 100))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 50))
        self.screen.blit(title_surface, title_rect)
        
        # Life Lesson header
        lesson_header = "Life Lesson:"
        header_surface = self.font_medium.render(lesson_header, True, (150, 255, 150))
        header_rect = header_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 100))
        self.screen.blit(header_surface, header_rect)
        
        # Life lesson text (word wrapped)
        if self.lesson_text:
            self.draw_wrapped_text(self.lesson_text, panel_x + 30, panel_y + 140, 
                                 panel_width - 60, self.font_small, (255, 255, 255))
        
        # Next level indicator
        if self.next_level_ready:
            next_text = f"Next: Level {self.current_level_num + 1}"
            next_surface = self.font_medium.render(next_text, True, (100, 255, 100))
            next_rect = next_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 80))
            self.screen.blit(next_surface, next_rect)
            
            # Continue instruction
            continue_text = "Press SPACE to continue to next level"
            continue_surface = self.font_small.render(continue_text, True, (100, 255, 100))
            continue_rect = continue_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 50))
            
            # Button background
            button_bg = pygame.Rect(continue_rect.x - 15, continue_rect.y - 8, 
                                   continue_rect.width + 30, continue_rect.height + 16)
            pygame.draw.rect(self.screen, (0, 100, 0), button_bg, border_radius=8)
            pygame.draw.rect(self.screen, (100, 255, 100), button_bg, 2, border_radius=8)
            self.screen.blit(continue_surface, continue_rect)
        else:
            # Final level completed
            final_text = "All levels completed!"
            final_surface = self.font_medium.render(final_text, True, (255, 200, 100))
            final_rect = final_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 80))
            self.screen.blit(final_surface, final_rect)
            
            # Continue to victory instruction
            continue_text = "Press SPACE to see final results"
            continue_surface = self.font_small.render(continue_text, True, (100, 255, 100))
            continue_rect = continue_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 50))
            
            # Button background
            button_bg = pygame.Rect(continue_rect.x - 15, continue_rect.y - 8, 
                                   continue_rect.width + 30, continue_rect.height + 16)
            pygame.draw.rect(self.screen, (0, 100, 0), button_bg, border_radius=8)
            pygame.draw.rect(self.screen, (100, 255, 100), button_bg, 2, border_radius=8)
            self.screen.blit(continue_surface, continue_rect)
    
    def draw_wrapped_text(self, text, x, y, max_width, font, color, center=False):
        """Draw text with word wrapping, optionally centered"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        line_height = font.get_height() + 5
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            if center:
                # Center each line within the max_width
                line_x = x + (max_width - line_surface.get_width()) // 2
            else:
                line_x = x
            self.screen.blit(line_surface, (line_x, y + i * line_height))
    
    def draw_game(self):
        """Draw the main game scene"""
        if self.current_level:
            self.current_level.draw(self.screen)
        self.player.draw(self.screen)
    
    def draw_death_screen(self):
        """Draw death screen with motivational second chance"""
        # Draw game background first
        self.draw_game()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((50, 20, 20))
        self.screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = WINDOW_WIDTH - 100
        panel_height = 350
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (40, 20, 20), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 100, 100), panel_rect, 3, border_radius=15)
        
        if self.lives_remaining > 0 and self.show_motivation:
            # Still have lives left - show motivation
            if self.lives_remaining == 2:
                title_text = "Second Chance!"
                title_color = (255, 200, 100)
            elif self.lives_remaining == 1:
                title_text = "Final Chance!"
                title_color = (255, 150, 50)
            else:
                title_text = "Try Again!"
                title_color = (255, 200, 100)
            
            # Motivational quote - CENTERED
            self.draw_wrapped_text(self.motivation_quote, panel_x + 30, panel_y + 80, 
                                 panel_width - 60, self.font_small, (255, 255, 200), center=True)
            
            # Lives remaining display
            lives_text = f"Lives Remaining: {self.lives_remaining}"
            lives_surface = self.font_medium.render(lives_text, True, (255, 255, 100))
            lives_rect = lives_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 120))
            self.screen.blit(lives_surface, lives_rect)
            
            # Restart instruction
            restart_text = "Press SPACE to try again with a fresh start"
            restart_surface = self.font_medium.render(restart_text, True, (100, 255, 100))
            restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 80))
            
            # Button background
            button_bg = pygame.Rect(restart_rect.x - 25, restart_rect.y - 15, 
                                   restart_rect.width + 50, restart_rect.height + 30)
            pygame.draw.rect(self.screen, (0, 100, 0), button_bg, border_radius=12)
            pygame.draw.rect(self.screen, (100, 255, 100), button_bg, 3, border_radius=12)
            self.screen.blit(restart_surface, restart_rect)
            
            # Warning text based on lives remaining
            if self.lives_remaining == 1:
                warning_text = "⚠️  This is your FINAL life!"
                warning_color = (255, 100, 100)
            else:
                warning_text = f"⚠️  {self.lives_remaining} lives remaining!"
                warning_color = (255, 200, 100)
            
            warning_surface = self.font_small.render(warning_text, True, warning_color)
            warning_rect = warning_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 40))
            self.screen.blit(warning_surface, warning_rect)
            
        else:
            # Regular death (shouldn't happen with new system, but fallback)
            title_text = "Time's Up!"
            title_color = (255, 100, 100)
            
            restart_text = "Press SPACE to restart"
            restart_surface = self.font_medium.render(restart_text, True, (100, 255, 100))
            restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 60))
            self.screen.blit(restart_surface, restart_rect)
        
        # Title
        title_surface = self.font_large.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 40))
        self.screen.blit(title_surface, title_rect)
        
        # Menu instruction
        menu_text = "Press ESC for main menu"
        menu_surface = self.font_small.render(menu_text, True, (200, 200, 200))
        menu_rect = menu_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 15))
        self.screen.blit(menu_surface, menu_rect)
    
    def draw_game_over_screen(self):
        """Draw game over screen after second failure"""
        # Gradient background
        for y in range(WINDOW_HEIGHT):
            color_intensity = int(30 + 20 * (y / WINDOW_HEIGHT))
            color = (color_intensity, color_intensity // 3, color_intensity // 3)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Main panel
        panel_width = WINDOW_WIDTH - 80
        panel_height = 400
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (60, 20, 20), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 100, 100), panel_rect, 4, border_radius=20)
        
        # Game Over title
        title_text = "GAME OVER"
        title_surface = self.font_large.render(title_text, True, (255, 100, 100))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 60))
        self.screen.blit(title_surface, title_rect)
        
        # Failure message
        failure_text = f"You ran out of lives on Level {self.current_level_num}."
        failure_surface = self.font_medium.render(failure_text, True, (255, 200, 200))
        failure_rect = failure_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 120))
        self.screen.blit(failure_surface, failure_rect)
        
        # Encouraging message
        encourage_lines = [
            "Don't give up! Every master was once a disaster.",
            "Learn from this experience and come back stronger.",
            "The greatest victories come after the toughest defeats."
        ]
        
        for i, line in enumerate(encourage_lines):
            line_surface = self.font_small.render(line, True, (255, 255, 200))
            line_rect = line_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 170 + i * 25))
            self.screen.blit(line_surface, line_rect)
        
        # Stats
        stats_text = f"You reached Level {self.current_level_num} using {self.lives_lived} lives"
        stats_surface = self.font_small.render(stats_text, True, (200, 255, 200))
        stats_rect = stats_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 270))
        self.screen.blit(stats_surface, stats_rect)
        
        # Try again button
        try_again_text = "Press SPACE to return to main menu"
        try_again_surface = self.font_medium.render(try_again_text, True, (100, 255, 100))
        try_again_rect = try_again_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 320))
        
        # Button background
        button_bg = pygame.Rect(try_again_rect.x - 25, try_again_rect.y - 15, 
                               try_again_rect.width + 50, try_again_rect.height + 30)
        pygame.draw.rect(self.screen, (0, 100, 0), button_bg, border_radius=15)
        pygame.draw.rect(self.screen, (100, 255, 100), button_bg, 3, border_radius=15)
        self.screen.blit(try_again_surface, try_again_rect)
    
    def draw_victory_screen(self):
        """Draw final victory screen with play again option"""
        # Gradient background
        for y in range(WINDOW_HEIGHT):
            color_intensity = int(50 + 100 * (y / WINDOW_HEIGHT))
            color = (color_intensity // 3, color_intensity // 2, color_intensity)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Victory panel
        panel_width = WINDOW_WIDTH - 100
        panel_height = 450
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 215, 0), panel_rect, 3, border_radius=15)
        
        # Victory text
        victory_text = "🎉 CONGRATULATIONS! 🎉"
        victory_surface = self.font_large.render(victory_text, True, (255, 255, 100))
        victory_rect = victory_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 60))
        self.screen.blit(victory_surface, victory_rect)
        
        # Completion message
        complete_text = "You've mastered all 3 levels and learned valuable life lessons!"
        complete_surface = self.font_medium.render(complete_text, True, (200, 255, 200))
        complete_rect = complete_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 110))
        self.screen.blit(complete_surface, complete_rect)
        
        # Life lessons summary
        lessons_header = "Life Lessons Learned:"
        header_surface = self.font_medium.render(lessons_header, True, (150, 255, 150))
        header_rect = header_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 150))
        self.screen.blit(header_surface, header_rect)
        
        # Individual lessons
        lessons = [
            "1. Taking Initiative - Success begins with the first step",
            "2. Preparation Opens Opportunities - Education unlocks doors", 
            "3. Urgency Creates Focus - Deadlines motivate achievement"
        ]
        
        for i, lesson in enumerate(lessons):
            lesson_surface = self.font_small.render(lesson, True, (255, 255, 255))
            lesson_rect = lesson_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 180 + i * 25))
            self.screen.blit(lesson_surface, lesson_rect)
        
        # Stats
        stats_text = f"Total Lives Used: {self.lives_lived}"
        stats_surface = self.font_medium.render(stats_text, True, (255, 255, 100))
        stats_rect = stats_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 280))
        self.screen.blit(stats_surface, stats_rect)
        
        # Play again button
        play_again_text = "Press SPACE to Play Again"
        play_again_surface = self.font_medium.render(play_again_text, True, (100, 255, 100))
        play_again_rect = play_again_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 330))
        
        # Button background
        button_bg = pygame.Rect(play_again_rect.x - 20, play_again_rect.y - 10, 
                               play_again_rect.width + 40, play_again_rect.height + 20)
        pygame.draw.rect(self.screen, (0, 100, 0), button_bg, border_radius=10)
        pygame.draw.rect(self.screen, (100, 255, 100), button_bg, 2, border_radius=10)
        self.screen.blit(play_again_surface, play_again_rect)
        
        # Menu instruction
        menu_text = "Press ESC to return to main menu"
        menu_surface = self.font_small.render(menu_text, True, (200, 200, 200))
        menu_rect = menu_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 380))
        self.screen.blit(menu_surface, menu_rect)
    
    def draw_menu(self):
        """Draw enhanced main menu with game information"""
        # Background gradient
        for y in range(WINDOW_HEIGHT):
            color_intensity = int(30 + 50 * (y / WINDOW_HEIGHT))
            color = (color_intensity // 4, color_intensity // 3, color_intensity // 2)
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))
        
        # Main panel
        panel_width = WINDOW_WIDTH - 80
        panel_height = WINDOW_HEIGHT - 100
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (30, 30, 50, 200), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (100, 150, 200), panel_rect, 3, border_radius=20)
        
        # Title
        title = self.font_large.render("10 Second Life", True, (255, 255, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, panel_y + 60))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Echoes of a Short World v2.0", True, (200, 200, 255))
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, panel_y + 100))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Game description
        description_lines = [
            "A unique puzzle-adventure where each life lasts only 10 seconds!",
            "Master 3 challenging levels while learning valuable life lessons.",
            "Your actions persist across lives - use strategy and wisdom to succeed."
        ]
        
        for i, line in enumerate(description_lines):
            desc_surface = self.font_small.render(line, True, (200, 255, 200))
            desc_rect = desc_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 150 + i * 25))
            self.screen.blit(desc_surface, desc_rect)
        
        # Level preview
        levels_header = "Levels & Life Lessons:"
        header_surface = self.font_medium.render(levels_header, True, (255, 200, 100))
        header_rect = header_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 250))
        self.screen.blit(header_surface, header_rect)
        
        level_info = [
            "Level 1: First Steps - Learn the power of taking initiative",
            "Level 2: The Door - Discover how preparation opens opportunities", 
            "Level 3: Time Pressure - Master focus under deadlines"
        ]
        
        for i, level in enumerate(level_info):
            level_surface = self.font_small.render(level, True, (255, 255, 255))
            level_rect = level_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 280 + i * 25))
            self.screen.blit(level_surface, level_rect)
        
        # Start button
        start_text = "Press SPACE to Begin Your Journey"
        start_surface = self.font_medium.render(start_text, True, (100, 255, 100))
        start_rect = start_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 380))
        
        # Button background
        button_bg = pygame.Rect(start_rect.x - 25, start_rect.y - 15, 
                               start_rect.width + 50, start_rect.height + 30)
        pygame.draw.rect(self.screen, (0, 100, 0), button_bg, border_radius=15)
        pygame.draw.rect(self.screen, (100, 255, 100), button_bg, 3, border_radius=15)
        self.screen.blit(start_surface, start_rect)
        
        # Controls
        controls_header = "Controls:"
        controls_surface = self.font_small.render(controls_header, True, (255, 200, 100))
        controls_rect = controls_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 450))
        self.screen.blit(controls_surface, controls_rect)
        
        controls = [
            "Arrow Keys: Move • SPACE: Interact & Continue • ESC: Menu"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.font_small.render(control, True, (200, 200, 200))
            control_rect = control_surface.get_rect(center=(WINDOW_WIDTH//2, panel_y + 475 + i * 20))
            self.screen.blit(control_surface, control_rect)
    
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
            self.draw_game()
            self.draw_ui()
        elif self.state == GameState.DEATH:
            self.draw_death_screen()
        elif self.state == GameState.LEVEL_COMPLETE:
            # Draw game background first
            self.draw_game()
            self.draw_ui()
            # Then draw lesson screen overlay
            if self.show_lesson:
                self.draw_lesson_screen()
        elif self.state == GameState.VICTORY:
            self.draw_victory_screen()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over_screen()
        
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
