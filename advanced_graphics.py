"""
Advanced Professional Graphics System for 10 Second Life
High-quality sprites, animations, and visual effects
"""

import pygame
import math
import random
import numpy as np
from typing import List, Tuple, Dict

# Professional color palette
PALETTE = {
    # Environment
    'sky_top': (25, 25, 40),
    'sky_bottom': (60, 40, 80),
    'ground': (45, 35, 25),
    'grass': (40, 80, 30),
    'stone': (90, 85, 80),
    'wood': (101, 67, 33),
    'metal': (120, 120, 140),
    'wall': (70, 70, 70),
    
    # Characters
    'player_body': (100, 150, 255),
    'player_highlight': (180, 200, 255),
    'player_shadow': (60, 90, 180),
    'npc_tree': (34, 139, 34),
    'npc_tree_bark': (101, 67, 33),
    'npc_mirror': (200, 100, 255),
    'npc_watcher': (255, 100, 100),
    
    # Items
    'item_seed': (144, 238, 144),
    'item_torch_handle': (139, 69, 19),
    'item_torch_flame': (255, 140, 0),
    'item_key': (255, 215, 0),
    'item_glow': (255, 255, 200),
    
    # Doors and switches
    'door_wood': (101, 67, 33),
    'switch_off': (120, 120, 120),
    'switch_on': (100, 255, 100),
    
    # UI
    'ui_bg': (20, 20, 30),
    'ui_border': (100, 100, 120),
    'ui_accent': (255, 215, 0),
    'text_primary': (255, 255, 255),
    'text_secondary': (180, 180, 200),
    'text_danger': (255, 69, 0),
    'text_success': (50, 205, 50),
    
    # Effects
    'particle_magic': (255, 105, 180),
    'particle_fire': (255, 69, 0),
    'particle_nature': (50, 205, 50),
    'particle_gold': (255, 215, 0),
}

class AdvancedSprite:
    """Advanced sprite with animations and effects"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.animation_frame = 0
        self.animation_speed = 0.1
        
    def update_animation(self, dt):
        self.animation_frame += self.animation_speed * dt
        
    def get_surface(self):
        return self.surface

class PlayerSprite(AdvancedSprite):
    """Advanced player sprite with detailed design and animations"""
    def __init__(self):
        super().__init__(32, 32)
        self.glow_intensity = 0
        self.create_sprite()
    
    def create_sprite(self):
        self.surface.fill((0, 0, 0, 0))  # Clear surface
        
        # Body (main circle)
        center = (16, 16)
        pygame.draw.circle(self.surface, PALETTE['player_body'], center, 14)
        
        # Highlight (smaller circle, offset)
        pygame.draw.circle(self.surface, PALETTE['player_highlight'], (13, 13), 8)
        
        # Shadow/depth
        pygame.draw.circle(self.surface, PALETTE['player_shadow'], (18, 18), 6)
        
        # Eyes
        pygame.draw.circle(self.surface, PALETTE['text_primary'], (12, 12), 2)
        pygame.draw.circle(self.surface, PALETTE['text_primary'], (20, 12), 2)
        pygame.draw.circle(self.surface, (0, 0, 0), (12, 12), 1)
        pygame.draw.circle(self.surface, (0, 0, 0), (20, 12), 1)
        
        # Mouth (small curve)
        mouth_points = [(14, 20), (16, 22), (18, 20)]
        pygame.draw.lines(self.surface, PALETTE['text_primary'], False, mouth_points, 2)
    
    def draw_with_glow(self, screen, x, y, glow=False):
        if glow:
            # Create glow effect
            glow_surface = pygame.Surface((48, 48), pygame.SRCALPHA)
            for i in range(5):
                alpha = 50 - i * 10
                radius = 20 + i * 3
                glow_color = (*PALETTE['item_glow'][:3], alpha)
                pygame.draw.circle(glow_surface, glow_color, (24, 24), radius)
            screen.blit(glow_surface, (x - 8, y - 8))
        
        screen.blit(self.surface, (x, y))

class TreeSprite(AdvancedSprite):
    """Detailed tree sprite with trunk, branches, and leaves"""
    def __init__(self, has_fruit=False):
        super().__init__(64, 80)
        self.has_fruit = has_fruit
        self.create_sprite()
    
    def create_sprite(self):
        self.surface.fill((0, 0, 0, 0))
        
        # Trunk
        trunk_rect = pygame.Rect(26, 50, 12, 30)
        pygame.draw.rect(self.surface, PALETTE['npc_tree_bark'], trunk_rect)
        
        # Trunk texture lines
        for i in range(3):
            y_pos = 55 + i * 8
            pygame.draw.line(self.surface, (80, 50, 20), (28, y_pos), (36, y_pos), 1)
        
        # Main canopy
        pygame.draw.circle(self.surface, PALETTE['npc_tree'], (32, 35), 22)
        
        # Canopy layers for depth
        pygame.draw.circle(self.surface, (50, 160, 50), (28, 30), 15)
        pygame.draw.circle(self.surface, (30, 120, 30), (36, 32), 12)
        pygame.draw.circle(self.surface, (60, 180, 60), (32, 40), 18)
        
        # Fruit if planted
        if self.has_fruit:
            fruit_positions = [(25, 25), (39, 28), (30, 42)]
            for pos in fruit_positions:
                pygame.draw.circle(self.surface, PALETTE['item_seed'], pos, 3)
                pygame.draw.circle(self.surface, (100, 200, 100), pos, 2)

class ItemSprite(AdvancedSprite):
    """Detailed item sprites with proper designs"""
    def __init__(self, item_type):
        super().__init__(32, 32)
        self.item_type = item_type
        self.create_sprite()
    
    def create_sprite(self):
        self.surface.fill((0, 0, 0, 0))
        center = (16, 16)
        
        if self.item_type == "seed":
            # Detailed seed with glow
            pygame.draw.circle(self.surface, PALETTE['item_seed'], center, 8)
            pygame.draw.circle(self.surface, (100, 200, 100), center, 6)
            pygame.draw.circle(self.surface, (200, 255, 200), center, 3)
            
            # Sparkle points
            sparkle_points = [(8, 8), (24, 8), (8, 24), (24, 24)]
            for point in sparkle_points:
                pygame.draw.circle(self.surface, PALETTE['item_glow'], point, 2)
        
        elif self.item_type == "torch":
            # Torch handle
            handle_rect = pygame.Rect(14, 16, 4, 12)
            pygame.draw.rect(self.surface, PALETTE['item_torch_handle'], handle_rect)
            
            # Handle wrapping
            for i in range(3):
                y_pos = 18 + i * 3
                pygame.draw.line(self.surface, (80, 40, 10), (14, y_pos), (18, y_pos), 1)
            
            # Flame (layered for realism)
            flame_points = [(16, 6), (12, 14), (20, 14), (16, 16)]
            pygame.draw.polygon(self.surface, PALETTE['item_torch_flame'], flame_points)
            
            inner_flame = [(16, 8), (14, 14), (18, 14), (16, 16)]
            pygame.draw.polygon(self.surface, (255, 200, 0), inner_flame)
            
            core_flame = [(16, 10), (15, 14), (17, 14), (16, 16)]
            pygame.draw.polygon(self.surface, (255, 255, 100), core_flame)
        
        elif self.item_type == "key":
            # Key head (circular)
            pygame.draw.circle(self.surface, PALETTE['item_key'], (12, 16), 6)
            pygame.draw.circle(self.surface, PALETTE['ui_bg'], (12, 16), 3)
            
            # Key shaft
            shaft_rect = pygame.Rect(18, 15, 8, 2)
            pygame.draw.rect(self.surface, PALETTE['item_key'], shaft_rect)
            
            # Key teeth
            teeth_rects = [
                pygame.Rect(24, 13, 2, 2),
                pygame.Rect(22, 11, 2, 2),
                pygame.Rect(26, 17, 2, 2)
            ]
            for rect in teeth_rects:
                pygame.draw.rect(self.surface, PALETTE['item_key'], rect)

class DoorSprite(AdvancedSprite):
    """Detailed door sprite with panels and hardware"""
    def __init__(self, is_open=False):
        super().__init__(64, 96)
        self.is_open = is_open
        self.create_sprite()
    
    def create_sprite(self):
        self.surface.fill((0, 0, 0, 0))
        
        if self.is_open:
            # Open door - just frame and hinges
            frame_color = PALETTE['wood']
            pygame.draw.rect(self.surface, frame_color, (0, 0, 8, 96))  # Left frame
            pygame.draw.rect(self.surface, frame_color, (56, 0, 8, 96))  # Right frame
            pygame.draw.rect(self.surface, frame_color, (0, 0, 64, 8))  # Top frame
            pygame.draw.rect(self.surface, frame_color, (0, 88, 64, 8))  # Bottom frame
            
            # Hinges
            hinge_positions = [(2, 20), (2, 76)]
            for pos in hinge_positions:
                pygame.draw.rect(self.surface, PALETTE['metal'], (*pos, 4, 8))
        else:
            # Closed door with detailed panels
            door_color = PALETTE['wood']
            pygame.draw.rect(self.surface, door_color, (0, 0, 64, 96))
            
            # Door panels (raised effect)
            panel_rects = [
                pygame.Rect(8, 12, 20, 30),
                pygame.Rect(36, 12, 20, 30),
                pygame.Rect(8, 54, 20, 30),
                pygame.Rect(36, 54, 20, 30)
            ]
            
            for rect in panel_rects:
                # Panel shadow
                shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
                pygame.draw.rect(self.surface, (80, 50, 20), shadow_rect)
                # Panel highlight
                pygame.draw.rect(self.surface, (140, 90, 50), rect)
            
            # Door handle
            handle_center = (52, 48)
            pygame.draw.circle(self.surface, PALETTE['metal'], handle_center, 4)
            pygame.draw.circle(self.surface, (150, 150, 170), handle_center, 3)
            
            # Keyhole
            keyhole_rect = pygame.Rect(50, 46, 4, 2)
            pygame.draw.rect(self.surface, (0, 0, 0), keyhole_rect)

class AdvancedParticleSystem:
    """Professional particle system with multiple effect types"""
    def __init__(self):
        self.particles = []
        self.emitters = []
    
    def add_explosion(self, x, y, color, count=15, size_range=(2, 6), speed_range=(50, 150)):
        """Create explosion effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            size = random.uniform(*size_range)
            lifetime = random.uniform(0.8, 2.0)
            
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'type': 'explosion'
            }
            self.particles.append(particle)
    
    def add_sparkle_trail(self, x, y, color, count=8):
        """Create sparkle trail effect"""
        for _ in range(count):
            offset_x = random.uniform(-20, 20)
            offset_y = random.uniform(-20, 20)
            size = random.uniform(1, 3)
            lifetime = random.uniform(1.0, 2.5)
            
            particle = {
                'x': x + offset_x,
                'y': y + offset_y,
                'vx': random.uniform(-10, 10),
                'vy': random.uniform(-30, -5),
                'color': color,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'type': 'sparkle'
            }
            self.particles.append(particle)
    
    def add_fire_effect(self, x, y, count=5):
        """Create fire particle effect"""
        for _ in range(count):
            particle = {
                'x': x + random.uniform(-5, 5),
                'y': y,
                'vx': random.uniform(-10, 10),
                'vy': random.uniform(-40, -20),
                'color': random.choice([PALETTE['particle_fire'], (255, 140, 0), (255, 200, 0)]),
                'size': random.uniform(2, 4),
                'lifetime': random.uniform(0.5, 1.2),
                'max_lifetime': random.uniform(0.5, 1.2),
                'type': 'fire'
            }
            self.particles.append(particle)
    
    def add_magic_sparkle(self, x, y, count=5):
        """Create magical sparkle effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 60)
            size = random.uniform(2, 4)
            lifetime = random.uniform(1.5, 3.0)
            
            particle = {
                'x': x + random.uniform(-10, 10),
                'y': y + random.uniform(-10, 10),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': PALETTE['particle_magic'],
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'type': 'sparkle'
            }
            self.particles.append(particle)
    
    def update(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['lifetime'] -= dt
            
            # Add gravity for certain particle types
            if particle['type'] in ['explosion', 'fire']:
                particle['vy'] += 50 * dt  # Gravity
            
            # Remove dead particles
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        """Draw all particles with advanced effects"""
        for particle in self.particles:
            alpha_ratio = particle['lifetime'] / particle['max_lifetime']
            alpha = int(255 * alpha_ratio)
            
            if alpha > 0:
                size = max(1, int(particle['size'] * alpha_ratio))
                color = (*particle['color'][:3], min(255, alpha))
                
                # Create particle surface with alpha
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                
                if particle['type'] == 'sparkle':
                    # Draw sparkle as a star shape
                    center = (size, size)
                    points = []
                    for i in range(8):
                        angle = i * math.pi / 4
                        if i % 2 == 0:
                            radius = size
                        else:
                            radius = size // 2
                        x = center[0] + math.cos(angle) * radius
                        y = center[1] + math.sin(angle) * radius
                        points.append((x, y))
                    pygame.draw.polygon(particle_surf, color, points)
                else:
                    # Draw regular circular particle
                    pygame.draw.circle(particle_surf, color, (size, size), size)
                
                screen.blit(particle_surf, (int(particle['x'] - size), int(particle['y'] - size)))

def draw_advanced_background(screen, width, height):
    """Draw professional gradient background with atmospheric effects"""
    # Create gradient from top to bottom
    for y in range(height):
        ratio = y / height
        r = int(PALETTE['sky_top'][0] * (1 - ratio) + PALETTE['sky_bottom'][0] * ratio)
        g = int(PALETTE['sky_top'][1] * (1 - ratio) + PALETTE['sky_bottom'][1] * ratio)
        b = int(PALETTE['sky_top'][2] * (1 - ratio) + PALETTE['sky_bottom'][2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))
    
    # Add atmospheric stars
    star_positions = [(random.randint(0, width), random.randint(0, height // 2)) for _ in range(100)]
    current_time = pygame.time.get_ticks()
    
    for i, (x, y) in enumerate(star_positions):
        # Twinkling effect
        twinkle = math.sin(current_time * 0.001 + i * 0.1) * 0.5 + 0.5
        alpha = int(30 + twinkle * 70)
        
        star_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (*PALETTE['text_primary'], alpha), (1, 1), 1)
        screen.blit(star_surf, (x, y))

def draw_advanced_ui_panel(screen, rect, title="", alpha=200, border_color=None):
    """Draw professional UI panel with gradient and effects"""
    # Create panel surface
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # Gradient background
    for y in range(rect.height):
        ratio = y / rect.height
        base_color = PALETTE['ui_bg']
        highlight_color = tuple(min(255, c + 20) for c in base_color)
        
        r = int(base_color[0] * (1 - ratio) + highlight_color[0] * ratio)
        g = int(base_color[1] * (1 - ratio) + highlight_color[1] * ratio)
        b = int(base_color[2] * (1 - ratio) + highlight_color[2] * ratio)
        
        pygame.draw.line(panel_surf, (*((r, g, b)), alpha), (0, y), (rect.width, y))
    
    # Border with glow effect
    border_col = border_color or PALETTE['ui_border']
    pygame.draw.rect(panel_surf, (*border_col, alpha), (0, 0, rect.width, rect.height), 2)
    pygame.draw.rect(panel_surf, (*border_col, alpha // 2), (1, 1, rect.width - 2, rect.height - 2), 1)
    
    screen.blit(panel_surf, rect)
    
    # Title with glow effect
    if title:
        font = pygame.font.Font(None, 24)
        title_surf = font.render(title, True, PALETTE['ui_accent'])
        title_rect = title_surf.get_rect()
        title_rect.centerx = rect.centerx
        title_rect.y = rect.y + 5
        
        # Title glow
        glow_surf = font.render(title, True, (100, 80, 0))
        for offset in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            screen.blit(glow_surf, (title_rect.x + offset[0], title_rect.y + offset[1]))
        
        screen.blit(title_surf, title_rect)

def draw_circular_timer(screen, center, radius, progress, color):
    """Draw professional circular timer with effects"""
    # Background circle
    bg_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
    pygame.draw.circle(bg_surf, (*PALETTE['ui_bg'], 180), (radius + 5, radius + 5), radius + 3)
    pygame.draw.circle(bg_surf, (*PALETTE['ui_border'], 200), (radius + 5, radius + 5), radius + 3, 2)
    screen.blit(bg_surf, (center[0] - radius - 5, center[1] - radius - 5))
    
    # Progress arc
    if progress > 0:
        start_angle = -math.pi / 2
        end_angle = start_angle + (2 * math.pi * progress)
        
        # Create arc points
        points = [center]
        for i in range(int(progress * 60) + 1):
            angle = start_angle + (end_angle - start_angle) * i / 60
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        
        if len(points) > 2:
            pygame.draw.polygon(screen, color, points)
    
    # Inner circle with glow
    inner_radius = radius - 8
    glow_surf = pygame.Surface((inner_radius * 2 + 6, inner_radius * 2 + 6), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*color, 100), (inner_radius + 3, inner_radius + 3), inner_radius + 2)
    pygame.draw.circle(glow_surf, (*PALETTE['ui_bg'], 255), (inner_radius + 3, inner_radius + 3), inner_radius)
    screen.blit(glow_surf, (center[0] - inner_radius - 3, center[1] - inner_radius - 3))
