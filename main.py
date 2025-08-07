#!/usr/bin/env python3
"""
10 Second Life: Echoes of a Short World
A 2D puzzle-adventure game where each life lasts only 10 seconds
"""

import pygame
import json
import os
import sys
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from graphics import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
LIFE_DURATION = 10.0  # 10 seconds per life

# Enhanced color system now imported from graphics.py

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    DEATH = "death"
    DIALOGUE = "dialogue"

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)

@dataclass
class WorldState:
    """Persistent world state that survives across lives"""
    doors_opened: List[str]
    seeds_planted: List[str]
    items_collected: List[str]
    npcs_talked_to: List[str]
    switches_activated: List[str]
    vines_burned: List[str]
    areas_unlocked: List[str]
    life_count: int
    total_time_played: float
    
    def to_dict(self):
        return {
            'doors_opened': self.doors_opened,
            'seeds_planted': self.seeds_planted,
            'items_collected': self.items_collected,
            'npcs_talked_to': self.npcs_talked_to,
            'switches_activated': self.switches_activated,
            'vines_burned': self.vines_burned,
            'areas_unlocked': self.areas_unlocked,
            'life_count': self.life_count,
            'total_time_played': self.total_time_played
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class GameObject:
    def __init__(self, x, y, width, height, color=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color or COLORS['text_primary']
        self.rect = pygame.Rect(x, y, width, height)
    
    def update_rect(self):
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, COLORS['player'])
        self.speed = 200  # pixels per second
        self.inventory = None
        self.spawn_x = x
        self.spawn_y = y
        self.glow_timer = 0
    
    def move(self, dx, dy, dt, obstacles):
        # Calculate new position
        new_x = self.x + dx * self.speed * dt
        new_y = self.y + dy * self.speed * dt
        
        # Check boundaries
        new_x = max(0, min(SCREEN_WIDTH - self.width, new_x))
        new_y = max(0, min(SCREEN_HEIGHT - self.height, new_y))
        
        # Check collision with obstacles
        temp_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        collision = False
        for obstacle in obstacles:
            if temp_rect.colliderect(obstacle.rect):
                collision = True
                break
        
        if not collision:
            self.x = new_x
            self.y = new_y
            self.update_rect()
    
    def reset_position(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.update_rect()
        self.inventory = None

class NPC(GameObject):
    def __init__(self, x, y, name, color=None, dialogue=None):
        if color is None:
            if name == "Talking Tree":
                color = COLORS['tree']
            elif name == "Mirror Twin":
                color = COLORS['npc_mirror']
            else:
                color = COLORS['npc_watcher']
        super().__init__(x, y, 32, 32, color)
        self.name = name
        self.dialogue = dialogue or []
        self.dialogue_index = 0
        self.has_talked = False
    
    def get_current_dialogue(self, world_state):
        if not self.dialogue:
            return f"Hello, I'm {self.name}!"
        
        # Adjust dialogue based on world state
        if self.name == "Talking Tree":
            if world_state.life_count == 1:
                return "Welcome, young soul. Your journey begins now..."
            elif len(world_state.seeds_planted) > 0:
                return "I remember you planted a seed. It grows with each life..."
            else:
                return "Each life teaches us something new. What will you learn?"
        
        return self.dialogue[self.dialogue_index % len(self.dialogue)]

class Item(GameObject):
    def __init__(self, x, y, name, color=None):
        if color is None:
            if name == "seed":
                color = COLORS['item_seed']
            elif name == "torch":
                color = COLORS['item_torch']
            elif name == "key":
                color = COLORS['item_key']
            else:
                color = COLORS['text_accent']
        super().__init__(x, y, 24, 24, color)
        self.name = name
        self.collected = False

class Door(GameObject):
    def __init__(self, x, y, door_id, color=None):
        super().__init__(x, y, 64, 96, color or COLORS['door_wood'])
        self.door_id = door_id
        self.is_open = False
    
    def draw(self, screen):
        if self.is_open:
            # Draw open door (just the frame)
            pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, 8, self.rect.height))
            pygame.draw.rect(screen, self.color, (self.rect.x + self.rect.width - 8, self.rect.y, 8, self.rect.height))
            pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, self.rect.width, 8))
        else:
            # Draw closed door
            super().draw(screen)

class Switch(GameObject):
    def __init__(self, x, y, switch_id, color=None):
        super().__init__(x, y, 32, 16, color or COLORS['switch_off'])
        self.switch_id = switch_id
        self.is_activated = False
    
    def draw(self, screen):
        color = GREEN if self.is_activated else RED
        pygame.draw.rect(screen, color, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("10 Second Life: Echoes of a Short World")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = GameState.MENU
        self.life_timer = LIFE_DURATION
        self.world_state = self.load_world_state()
        
        # Enhanced graphics
        self.particle_system = ParticleSystem()
        self.screen_shake = 0
        self.background_stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(50)]
        
        # Font
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game objects
        self.player = Player(100, 100)
        self.npcs = []
        self.items = []
        self.doors = []
        self.switches = []
        self.obstacles = []
        
        # Dialogue system
        self.current_dialogue = ""
        self.dialogue_timer = 0
        self.dialogue_npc = None
        
        # Initialize game world
        self.setup_world()
        
        # Audio
        self.setup_audio()
    
    def setup_audio(self):
        """Setup audio system with generated sounds"""
        try:
            # Create simple sound effects using pygame's sound generation
            self.sounds = {}
            
            # Heartbeat sound (simple beep)
            heartbeat = pygame.sndarray.make_sound(
                self.generate_tone(440, 0.1, 44100)
            )
            self.sounds['heartbeat'] = heartbeat
            
            # Death sound
            death_sound = pygame.sndarray.make_sound(
                self.generate_tone(220, 0.5, 44100)
            )
            self.sounds['death'] = death_sound
            
            # Interaction sound
            interact_sound = pygame.sndarray.make_sound(
                self.generate_tone(660, 0.2, 44100)
            )
            self.sounds['interact'] = interact_sound
            
        except:
            # Fallback if sound generation fails
            self.sounds = {}
    
    def generate_tone(self, frequency, duration, sample_rate):
        """Generate a simple tone"""
        import numpy as np
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        for i in range(frames):
            wave = np.sin(2 * np.pi * frequency * i / sample_rate)
            arr[i] = [wave * 0.3, wave * 0.3]  # Stereo, reduced volume
        return (arr * 32767).astype(np.int16)
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass  # Ignore sound errors
    
    def setup_world(self):
        """Initialize the game world with objects"""
        # Clear existing objects
        self.npcs.clear()
        self.items.clear()
        self.doors.clear()
        self.switches.clear()
        self.obstacles.clear()
        
        # Zone 1: Garden of Beginnings
        # Talking Tree
        tree = NPC(300, 200, "Talking Tree")
        self.npcs.append(tree)
        
        # Seed item
        if "seed_garden" not in self.world_state.items_collected:
            seed = Item(400, 300, "seed")
            self.items.append(seed)
            # Add sparkle effect around seed
            self.particle_system.add_magic_sparkle(400 + 12, 300 + 12, 2)
        
        # Door to Memory Cavern
        door1 = Door(500, 100, "cavern_door")
        if "cavern_door" in self.world_state.doors_opened:
            door1.is_open = True
        self.doors.append(door1)
        
        # Zone 2: Memory Cavern (if unlocked)
        if "memory_cavern" in self.world_state.areas_unlocked:
            # Torch item
            if "torch_cavern" not in self.world_state.items_collected:
                torch = Item(600, 400, "torch")
                self.items.append(torch)
                # Add fire particles around torch
                self.particle_system.add_particle(600 + 12, 400 + 12, 0, -20, COLORS['particle_fire'], 2, 0.8)
            
            # Vines (obstacle that can be burned)
            if "vines_entrance" not in self.world_state.vines_burned:
                vine_obstacle = GameObject(700, 350, 64, 64, COLORS['tree_dark'])
                self.obstacles.append(vine_obstacle)
        
        # Key for tower
        if "memory_cavern" in self.world_state.areas_unlocked and "key_tower" not in self.world_state.items_collected:
            key = Item(750, 500, "key")
            self.items.append(key)
            # Add golden glow around key
            self.particle_system.add_magic_sparkle(750 + 12, 500 + 12, 1)
        
        # Switch puzzle
        switch1 = Switch(200, 400, "switch1")
        if "switch1" in self.world_state.switches_activated:
            switch1.is_activated = True
        self.switches.append(switch1)
        
        # Mirror Twin NPC (appears after certain progress)
        if self.world_state.life_count > 5:
            mirror_twin = NPC(800, 300, "Mirror Twin")
            self.npcs.append(mirror_twin)
            # Add mystical particles around Mirror Twin
            self.particle_system.add_magic_sparkle(800 + 16, 300 + 16, 3)
        
        # Obstacles (walls)
        self.obstacles.extend([
            GameObject(0, 0, SCREEN_WIDTH, 10, COLORS['wall']),  # Top wall
            GameObject(0, SCREEN_HEIGHT-10, SCREEN_WIDTH, 10, COLORS['wall']),  # Bottom wall
            GameObject(0, 0, 10, SCREEN_HEIGHT, COLORS['wall']),  # Left wall
            GameObject(SCREEN_WIDTH-10, 0, 10, SCREEN_HEIGHT, COLORS['wall']),  # Right wall
        ])
    
    def load_world_state(self):
        """Load persistent world state from file"""
        try:
            if os.path.exists('world_state.json'):
                with open('world_state.json', 'r') as f:
                    data = json.load(f)
                    return WorldState.from_dict(data)
        except:
            pass
        
        # Return default world state
        return WorldState(
            doors_opened=[],
            seeds_planted=[],
            items_collected=[],
            npcs_talked_to=[],
            switches_activated=[],
            vines_burned=[],
            areas_unlocked=[],
            life_count=0,
            total_time_played=0.0
        )
    
    def save_world_state(self):
        """Save persistent world state to file"""
        try:
            with open('world_state.json', 'w') as f:
                json.dump(self.world_state.to_dict(), f, indent=2)
        except:
            pass
    
    def start_new_life(self):
        """Start a new 10-second life"""
        self.state = GameState.PLAYING
        self.life_timer = LIFE_DURATION
        self.world_state.life_count += 1
        self.player.reset_position()
        self.setup_world()  # Refresh world based on current state
        
        # Play heartbeat at start of life
        self.play_sound('heartbeat')
    
    def end_life(self):
        """End current life and show death screen"""
        self.state = GameState.DEATH
        self.save_world_state()
        self.play_sound('death')
    
    def handle_interaction(self):
        """Handle player interaction with objects"""
        player_rect = self.player.rect
        
        # Check NPC interactions
        for npc in self.npcs:
            if player_rect.colliderect(npc.rect):
                self.start_dialogue(npc)
                self.play_sound('interact')
                return
        
        # Check item pickup
        for item in self.items[:]:  # Use slice to avoid modification during iteration
            if player_rect.colliderect(item.rect) and not item.collected:
                if self.player.inventory is None:  # Can only carry one item
                    self.player.inventory = item.name
                    item.collected = True
                    self.items.remove(item)
                    self.world_state.items_collected.append(item.name)
                    # Add pickup effect
                    self.particle_system.add_explosion(item.x + 12, item.y + 12, COLORS['text_accent'], 8)
                    self.player.glow_timer = 1.0  # Player glows after pickup
                    self.play_sound('interact')
                return
        
        # Check door interactions
        for door in self.doors:
            if player_rect.colliderect(door.rect):
                if not door.is_open:
                    # Try to open door
                    if door.door_id == "cavern_door" and self.player.inventory == "key":
                        door.is_open = True
                        self.world_state.doors_opened.append(door.door_id)
                        self.world_state.areas_unlocked.append("memory_cavern")
                        self.player.inventory = None  # Use up the key
                        # Add door opening effect
                        self.particle_system.add_explosion(door.x + 32, door.y + 48, COLORS['item_key'], 12)
                        self.screen_shake = 0.5
                        self.play_sound('interact')
                return
        
        # Check switch interactions
        for switch in self.switches:
            if player_rect.colliderect(switch.rect):
                if not switch.is_activated:
                    switch.is_activated = True
                    switch.color = COLORS['switch_on']
                    self.world_state.switches_activated.append(switch.switch_id)
                    # Add switch activation effect
                    self.particle_system.add_explosion(switch.x + 16, switch.y + 8, COLORS['switch_on'], 6)
                    self.play_sound('interact')
                return
        
        # Special interactions based on inventory
        if self.player.inventory == "seed":
            # Plant seed near tree
            tree_pos = None
            for npc in self.npcs:
                if npc.name == "Talking Tree":
                    tree_pos = (npc.x, npc.y)
                    break
            
            if tree_pos and abs(self.player.x - tree_pos[0]) < 100 and abs(self.player.y - tree_pos[1]) < 100:
                self.world_state.seeds_planted.append("garden_seed")
                self.player.inventory = None
                # Add nature effect for seed planting
                self.particle_system.add_nature_effect(tree_pos[0] + 16, tree_pos[1] + 16, 8)
                self.play_sound('interact')
        
        elif self.player.inventory == "torch":
            # Burn vines
            for obstacle in self.obstacles[:]:
                if player_rect.colliderect(obstacle.rect) and obstacle.color == COLORS['tree_dark']:
                    # Add fire effect before removing vines
                    self.particle_system.add_explosion(obstacle.x + 32, obstacle.y + 32, COLORS['particle_fire'], 15)
                    self.obstacles.remove(obstacle)
                    self.world_state.vines_burned.append("vines_entrance")
                    self.player.inventory = None
                    self.screen_shake = 0.3
                    self.play_sound('interact')
                    break
    
    def start_dialogue(self, npc):
        """Start dialogue with an NPC"""
        self.state = GameState.DIALOGUE
        self.dialogue_npc = npc
        self.current_dialogue = npc.get_current_dialogue(self.world_state)
        self.dialogue_timer = 3.0  # Show dialogue for 3 seconds
        
        # Mark NPC as talked to
        if npc.name not in self.world_state.npcs_talked_to:
            self.world_state.npcs_talked_to.append(npc.name)
    
    def update(self, dt):
        """Update game state"""
        # Update particle system
        self.particle_system.update(dt)
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= dt
        
        # Update player glow
        if hasattr(self.player, 'glow_timer') and self.player.glow_timer > 0:
            self.player.glow_timer -= dt
        
        if self.state == GameState.PLAYING:
            # Update life timer
            self.life_timer -= dt
            self.world_state.total_time_played += dt
            
            # Check if life ended
            if self.life_timer <= 0:
                self.end_life()
                return
            
            # Handle input
            keys = pygame.key.get_pressed()
            dx = dy = 0
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
            
            # Move player
            self.player.move(dx, dy, dt, self.obstacles)
            
            # Play heartbeat when time is running low
            if self.life_timer <= 3.0 and int(self.life_timer * 4) % 2 == 0:
                if hasattr(self, '_last_heartbeat') and self.life_timer < self._last_heartbeat - 0.5:
                    self.play_sound('heartbeat')
                    self._last_heartbeat = self.life_timer
                elif not hasattr(self, '_last_heartbeat'):
                    self._last_heartbeat = self.life_timer
        
        elif self.state == GameState.DIALOGUE:
            # Update dialogue timer
            self.dialogue_timer -= dt
            if self.dialogue_timer <= 0:
                self.state = GameState.PLAYING
    
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
                        self.handle_interaction()
                
                elif self.state == GameState.DEATH:
                    if event.key == pygame.K_SPACE:
                        self.start_new_life()
                    elif event.key == pygame.K_r:
                        # Reset world state
                        self.world_state = WorldState(
                            doors_opened=[],
                            seeds_planted=[],
                            items_collected=[],
                            npcs_talked_to=[],
                            switches_activated=[],
                            vines_burned=[],
                            areas_unlocked=[],
                            life_count=0,
                            total_time_played=0.0
                        )
                        self.save_world_state()
                        self.start_new_life()
                
                elif self.state == GameState.DIALOGUE:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                        self.state = GameState.PLAYING
    
    def draw(self):
        """Draw everything to the screen"""
        # Apply screen shake
        shake_offset_x = shake_offset_y = 0
        if self.screen_shake > 0:
            shake_offset_x = random.randint(-3, 3)
            shake_offset_y = random.randint(-3, 3)
        
        # Enhanced background
        self.draw_background()
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.DEATH:
            self.draw_death_screen()
        elif self.state == GameState.DIALOGUE:
            self.draw_game()
            self.draw_dialogue()
        
        # Draw particles on top
        self.particle_system.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_background(self):
        """Draw enhanced background with stars and gradient"""
        # Gradient background
        draw_gradient_rect(self.screen, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 
                          COLORS['bg_dark'], COLORS['bg_light'])
        
        # Twinkling stars
        for i, (x, y) in enumerate(self.background_stars):
            # Make stars twinkle based on time
            twinkle = math.sin(pygame.time.get_ticks() * 0.001 + i) * 0.5 + 0.5
            alpha = int(50 + twinkle * 100)
            star_color = (*COLORS['text_primary'], alpha)
            
            try:
                star_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
                pygame.draw.circle(star_surf, star_color, (1, 1), 1)
                self.screen.blit(star_surf, (x, y))
            except:
                pygame.draw.circle(self.screen, COLORS['text_primary'], (x, y), 1)
    
    def draw_menu(self):
        """Draw the main menu"""
        title = self.font_large.render("10 Second Life", True, COLORS['text_primary'])
        subtitle = self.font_medium.render("Echoes of a Short World", True, COLORS['text_secondary'])
        instruction = self.font_small.render("Press SPACE to start your first life", True, COLORS['text_accent'])
        
        # Center text
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(instruction, instruction_rect)
        
        # Show stats if player has played before
        if self.world_state.life_count > 0:
            stats = self.font_small.render(f"Lives lived: {self.world_state.life_count}", True, COLORS['progress'])
            stats_rect = stats.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            self.screen.blit(stats, stats_rect)
            
            # Add sparkle effects around the title
            self.particle_system.add_magic_sparkle(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100, 1)
    
    def draw_game(self):
        """Draw the main game"""
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw doors with enhanced graphics
        for door in self.doors:
            draw_enhanced_door(self.screen, door.x, door.y, door.width, door.height, door.is_open)
        
        # Draw switches with enhanced graphics
        for switch in self.switches:
            color = COLORS['switch_on'] if switch.is_activated else COLORS['switch_off']
            pygame.draw.rect(self.screen, color, switch.rect)
            # Add glow effect for activated switches
            if switch.is_activated:
                glow_rect = pygame.Rect(switch.rect.x - 2, switch.rect.y - 2, 
                                      switch.rect.width + 4, switch.rect.height + 4)
                pygame.draw.rect(self.screen, COLORS['switch_on'], glow_rect, 2)
        
        # Draw items with enhanced graphics
        for item in self.items:
            if not item.collected:
                draw_enhanced_item(self.screen, item.x, item.y, item.name)
        
        # Draw NPCs with enhanced graphics
        for npc in self.npcs:
            if npc.name == "Talking Tree":
                has_seed = len(self.world_state.seeds_planted) > 0
                draw_enhanced_tree(self.screen, npc.x, npc.y, npc.width, npc.height, has_seed)
            else:
                npc.draw(self.screen)
            
            # Draw name above NPC with enhanced styling
            name_text = self.font_small.render(npc.name, True, COLORS['text_accent'])
            name_rect = name_text.get_rect(center=(npc.x + npc.width//2, npc.y - 15))
            
            # Background for name
            bg_rect = pygame.Rect(name_rect.x - 5, name_rect.y - 2, 
                                name_rect.width + 10, name_rect.height + 4)
            draw_enhanced_ui_panel(self.screen, bg_rect, alpha=150)
            self.screen.blit(name_text, name_rect)
        
        # Draw player with enhanced graphics
        glow = hasattr(self.player, 'glow_timer') and self.player.glow_timer > 0
        draw_enhanced_player(self.screen, self.player.x, self.player.y, 
                           self.player.width, self.player.height, glow)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        """Draw UI elements"""
        # Enhanced circular timer
        timer_progress = self.life_timer / LIFE_DURATION
        if self.life_timer <= 3.0:
            timer_color = COLORS['timer_danger']
        elif self.life_timer <= 5.0:
            timer_color = COLORS['timer_warning']
        else:
            timer_color = COLORS['timer_normal']
        
        # Draw circular timer
        timer_center = (80, 60)
        draw_timer_arc(self.screen, timer_center, 35, timer_progress, timer_color)
        
        # Timer text in center
        timer_text = self.font_medium.render(f"{self.life_timer:.1f}", True, timer_color)
        timer_rect = timer_text.get_rect(center=timer_center)
        self.screen.blit(timer_text, timer_rect)
        
        # Life count with enhanced panel
        life_panel_rect = pygame.Rect(20, 120, 200, 35)
        draw_enhanced_ui_panel(self.screen, life_panel_rect, f"Life #{self.world_state.life_count}")
        
        # Inventory with enhanced styling
        if self.player.inventory:
            inv_panel_rect = pygame.Rect(20, 165, 250, 30)
            draw_enhanced_ui_panel(self.screen, inv_panel_rect, alpha=180)
            inv_text = self.font_small.render(f"Carrying: {self.player.inventory}", True, COLORS['text_accent'])
            inv_rect = inv_text.get_rect(center=(inv_panel_rect.centerx, inv_panel_rect.centery))
            self.screen.blit(inv_text, inv_rect)
        
        # Instructions with enhanced panel
        instruction_panel_rect = pygame.Rect(20, SCREEN_HEIGHT - 40, 400, 25)
        draw_enhanced_ui_panel(self.screen, instruction_panel_rect, alpha=150)
        instruction = self.font_small.render("E/SPACE: Interact | WASD/Arrows: Move", True, COLORS['text_secondary'])
        instruction_rect = instruction.get_rect(center=(instruction_panel_rect.centerx, instruction_panel_rect.centery))
        self.screen.blit(instruction, instruction_rect)
        
        # Progress indicators with enhanced styling
        progress_items = []
        if self.world_state.seeds_planted:
            progress_items.append("✓ Seed planted")
        if self.world_state.doors_opened:
            progress_items.append("✓ Door opened")
        if self.world_state.vines_burned:
            progress_items.append("✓ Vines burned")
        if len(self.world_state.areas_unlocked) > 0:
            progress_items.append(f"✓ {len(self.world_state.areas_unlocked)} areas unlocked")
        
        if progress_items:
            progress_panel_height = len(progress_items) * 25 + 20
            progress_panel_rect = pygame.Rect(20, 210, 220, progress_panel_height)
            draw_enhanced_ui_panel(self.screen, progress_panel_rect, "Progress", alpha=180)
            
            for i, item in enumerate(progress_items):
                progress_text = self.font_small.render(item, True, COLORS['progress'])
                self.screen.blit(progress_text, (30, 235 + i * 25))
    
    def draw_death_screen(self):
        """Draw the death screen"""
        # Semi-transparent overlay with gradient
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        draw_gradient_rect(overlay, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 
                          COLORS['bg_dark'], (0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Death message with glow effect
        death_text = self.font_large.render("You Died", True, COLORS['timer_danger'])
        death_rect = death_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        
        # Add glow effect
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_text = self.font_large.render("You Died", True, (100, 0, 0))
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2 + offset[0], SCREEN_HEIGHT//2 - 50 + offset[1]))
            self.screen.blit(glow_text, glow_rect)
        
        self.screen.blit(death_text, death_rect)
        
        # Stats with enhanced panel
        stats = [
            f"Life #{self.world_state.life_count} completed",
            f"Total time played: {self.world_state.total_time_played:.1f}s",
            f"Progress: {len(self.world_state.doors_opened)} doors opened",
            f"Items found: {len(self.world_state.items_collected)}",
        ]
        
        stats_panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 20, 400, len(stats) * 30 + 20)
        draw_enhanced_ui_panel(self.screen, stats_panel_rect, "Life Summary", alpha=200)
        
        y_offset = SCREEN_HEIGHT//2 + 10
        for stat in stats:
            stat_text = self.font_small.render(stat, True, COLORS['text_secondary'])
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.screen.blit(stat_text, stat_rect)
            y_offset += 30
        
        # Instructions with enhanced styling
        instruction_panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 + 140, 360, 40)
        draw_enhanced_ui_panel(self.screen, instruction_panel_rect, alpha=200)
        instruction = self.font_medium.render("SPACE: Next Life | R: Reset Progress", True, COLORS['text_accent'])
        instruction_rect = instruction.get_rect(center=(instruction_panel_rect.centerx, instruction_panel_rect.centery))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_dialogue(self):
        """Draw dialogue box"""
        # Enhanced dialogue box background
        dialogue_rect = pygame.Rect(50, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 100, 100)
        draw_enhanced_ui_panel(self.screen, dialogue_rect, alpha=220)
        
        # NPC name with enhanced styling
        if self.dialogue_npc:
            name_text = self.font_medium.render(self.dialogue_npc.name, True, COLORS['text_accent'])
            self.screen.blit(name_text, (dialogue_rect.x + 15, dialogue_rect.y + 10))
        
        # Dialogue text (wrap if too long)
        words = self.current_dialogue.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font_small.size(test_line)[0] < dialogue_rect.width - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw dialogue lines with enhanced styling
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            line_text = self.font_small.render(line, True, COLORS['text_primary'])
            self.screen.blit(line_text, (dialogue_rect.x + 15, dialogue_rect.y + 40 + i * 20))
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        # Save state before quitting
        self.save_world_state()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        import numpy as np
    except ImportError:
        print("Installing required dependencies...")
        os.system("pip install numpy pygame")
        import numpy as np
    
    game = Game()
    game.run()
