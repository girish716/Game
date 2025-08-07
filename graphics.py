"""
Enhanced graphics and visual effects for 10 Second Life
"""

import pygame
import math
import random
from typing import List, Tuple

# Enhanced color palette
COLORS = {
    'bg_dark': (15, 15, 25),
    'bg_light': (25, 25, 35),
    'player': (100, 150, 255),
    'player_glow': (150, 200, 255),
    'tree': (34, 139, 34),
    'tree_dark': (0, 100, 0),
    'npc_mirror': (200, 100, 255),
    'npc_watcher': (255, 100, 100),
    'item_seed': (144, 238, 144),
    'item_torch': (255, 140, 0),
    'item_key': (255, 215, 0),
    'door_wood': (139, 69, 19),
    'door_metal': (105, 105, 105),
    'switch_off': (139, 0, 0),
    'switch_on': (0, 255, 0),
    'wall': (70, 70, 80),
    'floor': (40, 40, 50),
    'ui_bg': (20, 20, 30),
    'ui_border': (100, 100, 120),
    'text_primary': (255, 255, 255),
    'text_secondary': (180, 180, 200),
    'text_accent': (255, 215, 0),
    'timer_normal': (255, 255, 255),
    'timer_warning': (255, 165, 0),
    'timer_danger': (255, 69, 0),
    'progress': (0, 255, 127),
    'particle_magic': (255, 105, 180),
    'particle_fire': (255, 69, 0),
    'particle_nature': (50, 205, 50)
}

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            color = (*self.color, alpha)
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
            try:
                # Create a surface with per-pixel alpha
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size, size), size)
                screen.blit(surf, (int(self.x - size), int(self.y - size)))
            except:
                # Fallback to simple circle
                pygame.draw.circle(screen, self.color[:3], (int(self.x), int(self.y)), size)

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, vx, vy, color, size=3, lifetime=1.0):
        self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))
    
    def add_explosion(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2, 5)
            lifetime = random.uniform(0.5, 1.5)
            self.add_particle(x, y, vx, vy, color, size, lifetime)
    
    def add_magic_sparkle(self, x, y, count=5):
        for _ in range(count):
            vx = random.uniform(-30, 30)
            vy = random.uniform(-50, -10)
            size = random.uniform(1, 3)
            lifetime = random.uniform(1.0, 2.0)
            self.add_particle(x, y, vx, vy, COLORS['particle_magic'], size, lifetime)
    
    def add_nature_effect(self, x, y, count=3):
        for _ in range(count):
            vx = random.uniform(-20, 20)
            vy = random.uniform(-30, 10)
            size = random.uniform(2, 4)
            lifetime = random.uniform(1.5, 2.5)
            particle = Particle(x, y, vx, vy, COLORS['particle_nature'], size, lifetime)
            particle.gravity = 20  # Gentle fall
            self.particles.append(particle)
    
    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

def draw_gradient_rect(screen, rect, color1, color2, vertical=True):
    """Draw a gradient rectangle"""
    if vertical:
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(screen, (r, g, b), 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))
    else:
        for x in range(rect.width):
            ratio = x / rect.width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(screen, (r, g, b), 
                           (rect.x + x, rect.y), 
                           (rect.x + x, rect.y + rect.height))

def draw_enhanced_player(screen, x, y, width, height, glow=False):
    """Draw an enhanced player sprite"""
    center_x = x + width // 2
    center_y = y + height // 2
    
    # Glow effect
    if glow:
        for i in range(3):
            glow_size = width // 2 + i * 2
            glow_alpha = 50 - i * 15
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*COLORS['player_glow'], glow_alpha), 
                             (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (center_x - glow_size, center_y - glow_size))
    
    # Main body
    pygame.draw.circle(screen, COLORS['player'], (center_x, center_y), width // 2)
    
    # Inner highlight
    pygame.draw.circle(screen, COLORS['player_glow'], 
                      (center_x - 3, center_y - 3), width // 4)
    
    # Eyes
    eye_size = 3
    pygame.draw.circle(screen, COLORS['text_primary'], 
                      (center_x - 5, center_y - 2), eye_size)
    pygame.draw.circle(screen, COLORS['text_primary'], 
                      (center_x + 5, center_y - 2), eye_size)

def draw_enhanced_tree(screen, x, y, width, height, has_seed=False):
    """Draw an enhanced tree sprite"""
    # Trunk
    trunk_width = width // 3
    trunk_height = height // 2
    trunk_rect = pygame.Rect(x + width//2 - trunk_width//2, 
                           y + height - trunk_height, 
                           trunk_width, trunk_height)
    pygame.draw.rect(screen, COLORS['door_wood'], trunk_rect)
    
    # Tree crown (multiple circles for organic look)
    crown_y = y + height // 4
    pygame.draw.circle(screen, COLORS['tree_dark'], 
                      (x + width//2, crown_y), width//2 + 2)
    pygame.draw.circle(screen, COLORS['tree'], 
                      (x + width//2, crown_y), width//2)
    
    # Smaller crown details
    pygame.draw.circle(screen, COLORS['tree_dark'], 
                      (x + width//3, crown_y - 5), width//4)
    pygame.draw.circle(screen, COLORS['tree'], 
                      (x + width//3, crown_y - 5), width//4 - 1)
    
    pygame.draw.circle(screen, COLORS['tree_dark'], 
                      (x + 2*width//3, crown_y - 3), width//5)
    pygame.draw.circle(screen, COLORS['tree'], 
                      (x + 2*width//3, crown_y - 3), width//5 - 1)
    
    # Seed/fruit if planted
    if has_seed:
        fruit_x = x + width//2 + 8
        fruit_y = crown_y + 5
        pygame.draw.circle(screen, COLORS['item_seed'], (fruit_x, fruit_y), 4)
        pygame.draw.circle(screen, COLORS['progress'], (fruit_x, fruit_y), 2)

def draw_enhanced_door(screen, x, y, width, height, is_open=False, door_type="wood"):
    """Draw an enhanced door"""
    color = COLORS['door_wood'] if door_type == "wood" else COLORS['door_metal']
    
    if is_open:
        # Open door - just frame
        frame_width = 6
        pygame.draw.rect(screen, color, (x, y, frame_width, height))
        pygame.draw.rect(screen, color, (x + width - frame_width, y, frame_width, height))
        pygame.draw.rect(screen, color, (x, y, width, frame_width))
        pygame.draw.rect(screen, color, (x, y + height - frame_width, width, frame_width))
    else:
        # Closed door with details
        pygame.draw.rect(screen, color, (x, y, width, height))
        
        # Door panels
        panel_margin = 8
        panel_width = (width - 3 * panel_margin) // 2
        panel_height = (height - 3 * panel_margin) // 2
        
        for i in range(2):
            for j in range(2):
                panel_x = x + panel_margin + i * (panel_width + panel_margin)
                panel_y = y + panel_margin + j * (panel_height + panel_margin)
                panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
                
                # Inset panel effect
                darker_color = tuple(max(0, c - 30) for c in color)
                pygame.draw.rect(screen, darker_color, panel_rect)
                
        # Door handle
        handle_x = x + width - 15
        handle_y = y + height // 2
        pygame.draw.circle(screen, COLORS['item_key'], (handle_x, handle_y), 4)

def draw_enhanced_item(screen, x, y, item_name):
    """Draw enhanced item sprites"""
    center_x = x + 12
    center_y = y + 12
    
    if item_name == "seed":
        # Glowing seed
        pygame.draw.circle(screen, COLORS['item_seed'], (center_x, center_y), 8)
        pygame.draw.circle(screen, COLORS['progress'], (center_x, center_y), 4)
        # Sparkle effect
        for i in range(3):
            angle = i * 2 * math.pi / 3
            spark_x = center_x + int(12 * math.cos(angle))
            spark_y = center_y + int(12 * math.sin(angle))
            pygame.draw.circle(screen, COLORS['text_accent'], (spark_x, spark_y), 2)
    
    elif item_name == "torch":
        # Torch handle
        pygame.draw.rect(screen, COLORS['door_wood'], (center_x - 2, center_y, 4, 16))
        # Flame
        flame_points = [
            (center_x, center_y - 8),
            (center_x - 4, center_y - 2),
            (center_x + 4, center_y - 2),
            (center_x, center_y - 12)
        ]
        pygame.draw.polygon(screen, COLORS['item_torch'], flame_points)
        pygame.draw.polygon(screen, COLORS['particle_fire'], 
                          [(center_x, center_y - 10), 
                           (center_x - 2, center_y - 4),
                           (center_x + 2, center_y - 4)])
    
    elif item_name == "key":
        # Key shaft
        pygame.draw.rect(screen, COLORS['item_key'], (center_x - 8, center_y - 1, 12, 2))
        # Key head
        pygame.draw.circle(screen, COLORS['item_key'], (center_x - 8, center_y), 4)
        pygame.draw.circle(screen, COLORS['bg_dark'], (center_x - 8, center_y), 2)
        # Key teeth
        pygame.draw.rect(screen, COLORS['item_key'], (center_x + 2, center_y - 3, 2, 3))
        pygame.draw.rect(screen, COLORS['item_key'], (center_x + 4, center_y - 2, 2, 2))

def draw_enhanced_ui_panel(screen, rect, title="", alpha=200):
    """Draw an enhanced UI panel with gradient and border"""
    # Create surface with alpha
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # Gradient background
    for y in range(rect.height):
        ratio = y / rect.height
        color_val = int(30 * (1 - ratio) + 20 * ratio)
        color = (color_val, color_val, color_val + 10, alpha)
        pygame.draw.line(panel_surf, color, (0, y), (rect.width, y))
    
    # Border
    pygame.draw.rect(panel_surf, (*COLORS['ui_border'], alpha), 
                    (0, 0, rect.width, rect.height), 2)
    
    screen.blit(panel_surf, rect)
    
    # Title if provided
    if title:
        font = pygame.font.Font(None, 24)
        title_surf = font.render(title, True, COLORS['text_accent'])
        title_rect = title_surf.get_rect()
        title_rect.centerx = rect.centerx
        title_rect.y = rect.y + 5
        screen.blit(title_surf, title_rect)

def draw_timer_arc(screen, center, radius, progress, color):
    """Draw a circular timer arc"""
    if progress <= 0:
        return
    
    # Draw background circle
    pygame.draw.circle(screen, COLORS['ui_bg'], center, radius + 3)
    pygame.draw.circle(screen, COLORS['ui_border'], center, radius + 3, 2)
    
    # Draw progress arc
    start_angle = -math.pi / 2  # Start at top
    end_angle = start_angle + (2 * math.pi * progress)
    
    # Create points for the arc
    points = [center]
    for i in range(int(progress * 60) + 1):
        angle = start_angle + (end_angle - start_angle) * i / 60
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    
    if len(points) > 2:
        pygame.draw.polygon(screen, color, points)
    
    # Inner circle
    pygame.draw.circle(screen, COLORS['bg_dark'], center, radius - 10)
