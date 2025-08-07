#!/usr/bin/env python3
"""
Enhanced Graphics System for 10 Second Life
Realistic sprites, modern UI, and immersive visual effects
"""

import pygame
import math
import random
from typing import Tuple, List

# Enhanced Color Palette
PALETTE = {
    # UI Colors
    'bg_primary': (15, 20, 35),
    'bg_secondary': (25, 35, 55),
    'ui_panel': (35, 45, 70),
    'ui_border': (60, 80, 120),
    'ui_accent': (100, 150, 255),
    'ui_success': (80, 200, 120),
    'ui_warning': (255, 180, 60),
    'ui_danger': (255, 100, 100),
    'text_primary': (240, 245, 255),
    'text_secondary': (180, 190, 210),
    'text_muted': (120, 130, 150),
    
    # Game Object Colors
    'player_blue': (80, 140, 255),
    'player_glow': (120, 180, 255),
    'orb_gold': (255, 215, 0),
    'orb_glow': (255, 235, 100),
    'key_gold': (218, 165, 32),
    'key_shine': (255, 215, 0),
    'door_wood': (101, 67, 33),
    'door_metal': (105, 105, 105),
    'door_handle': (184, 134, 11),
    'coin_gold': (255, 215, 0),
    'coin_shine': (255, 245, 150),
    
    # Environmental Colors
    'wall_stone': (70, 70, 80),
    'wall_highlight': (90, 90, 100),
    'floor_tile': (45, 50, 65),
    'shadow': (10, 15, 25),
    'light_warm': (255, 220, 180),
    'light_cool': (180, 220, 255),
    
    # Particle Colors
    'sparkle_gold': (255, 215, 0),
    'sparkle_white': (255, 255, 255),
    'magic_blue': (100, 150, 255),
    'fire_orange': (255, 100, 50),
    'fire_yellow': (255, 200, 50)
}

class ParticleSystem:
    """Advanced particle system for visual effects"""
    
    def __init__(self):
        self.particles = []
    
    def add_sparkle(self, x: int, y: int, color: Tuple[int, int, int] = None):
        """Add sparkle particles around a point"""
        if color is None:
            color = PALETTE['sparkle_gold']
        
        for _ in range(random.randint(3, 6)):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'vx': random.uniform(-50, 50),
                'vy': random.uniform(-50, 50),
                'life': random.uniform(0.5, 1.5),
                'max_life': random.uniform(0.5, 1.5),
                'color': color,
                'size': random.randint(2, 4)
            }
            self.particles.append(particle)
    
    def add_glow_pulse(self, x: int, y: int, radius: int, color: Tuple[int, int, int]):
        """Add a pulsing glow effect"""
        particle = {
            'x': x,
            'y': y,
            'radius': radius,
            'max_radius': radius + 20,
            'life': 1.0,
            'max_life': 1.0,
            'color': color,
            'type': 'glow'
        }
        self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['life'] -= dt
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
            
            if particle.get('type') == 'glow':
                # Pulsing glow effect
                life_ratio = particle['life'] / particle['max_life']
                particle['radius'] = particle['max_radius'] * (0.5 + 0.5 * math.sin(particle['life'] * 8))
            else:
                # Regular particle movement
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt
                particle['vy'] += 100 * dt  # Gravity
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            if particle['life'] <= 0:
                continue
            
            life_ratio = particle['life'] / particle['max_life']
            alpha = int(255 * life_ratio)
            
            if particle.get('type') == 'glow':
                # Draw glow effect
                glow_surf = pygame.Surface((particle['radius'] * 2, particle['radius'] * 2), pygame.SRCALPHA)
                # Ensure alpha is within valid range
                safe_alpha = max(0, min(255, alpha // 3))
                color_with_alpha = (particle['color'][0], particle['color'][1], particle['color'][2], safe_alpha)
                pygame.draw.circle(glow_surf, color_with_alpha, 
                                 (particle['radius'], particle['radius']), particle['radius'])
                screen.blit(glow_surf, (particle['x'] - particle['radius'], particle['y'] - particle['radius']))
            else:
                # Draw sparkle particle
                size = int(particle['size'] * life_ratio)
                if size > 0:
                    # Ensure alpha is within valid range and color is RGB tuple
                    safe_alpha = max(0, min(255, alpha))
                    base_color = particle['color'][:3]  # Ensure only RGB components
                    color_with_alpha = (base_color[0], base_color[1], base_color[2], safe_alpha)
                    particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
                    screen.blit(particle_surf, (particle['x'] - size, particle['y'] - size))

def draw_realistic_player(screen, x: int, y: int, width: int, height: int):
    """Draw a realistic player character"""
    # Body (blue with gradient)
    body_rect = pygame.Rect(x + 2, y + 8, width - 4, height - 8)
    pygame.draw.ellipse(screen, PALETTE['player_blue'], body_rect)
    
    # Head
    head_rect = pygame.Rect(x + 4, y, width - 8, 12)
    pygame.draw.ellipse(screen, PALETTE['player_blue'], head_rect)
    
    # Glow effect
    glow_rect = pygame.Rect(x - 2, y - 2, width + 4, height + 4)
    glow_surf = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surf, (*PALETTE['player_glow'], 60), (0, 0, width + 4, height + 4))
    screen.blit(glow_surf, (x - 2, y - 2))
    
    # Eyes
    pygame.draw.circle(screen, PALETTE['text_primary'], (x + 6, y + 4), 2)
    pygame.draw.circle(screen, PALETTE['text_primary'], (x + width - 6, y + 4), 2)

def draw_realistic_orb(screen, x: int, y: int, width: int, height: int, glow_time: float):
    """Draw a realistic glowing orb"""
    center_x = x + width // 2
    center_y = y + height // 2
    radius = min(width, height) // 2
    
    # Outer glow (pulsing)
    glow_intensity = 0.7 + 0.3 * math.sin(glow_time * 2)
    glow_radius = int(radius * (1.5 + 0.3 * math.sin(glow_time * 3)))
    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
    glow_alpha = int(100 * glow_intensity)
    pygame.draw.circle(glow_surf, (*PALETTE['orb_glow'], glow_alpha), 
                      (glow_radius, glow_radius), glow_radius)
    screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))
    
    # Main orb body
    pygame.draw.circle(screen, PALETTE['orb_gold'], (center_x, center_y), radius)
    
    # Inner highlight
    highlight_offset = int(radius * 0.3)
    pygame.draw.circle(screen, PALETTE['orb_glow'], 
                      (center_x - highlight_offset, center_y - highlight_offset), 
                      radius // 3)
    
    # Core shine
    pygame.draw.circle(screen, PALETTE['sparkle_white'], 
                      (center_x - highlight_offset, center_y - highlight_offset), 
                      radius // 6)

def draw_realistic_key(screen, x: int, y: int, width: int, height: int, glow_time: float):
    """Draw a realistic golden key"""
    # Key shaft
    shaft_rect = pygame.Rect(x + 2, y + height//2 - 2, width - 8, 4)
    pygame.draw.rect(screen, PALETTE['key_gold'], shaft_rect)
    
    # Key head (circular)
    head_center = (x + width - 6, y + height//2)
    pygame.draw.circle(screen, PALETTE['key_gold'], head_center, 6)
    pygame.draw.circle(screen, PALETTE['key_shine'], head_center, 4)
    
    # Key teeth
    teeth_y = y + height//2 + 2
    for i in range(3):
        tooth_x = x + 4 + i * 3
        pygame.draw.rect(screen, PALETTE['key_gold'], (tooth_x, teeth_y, 2, 3))
    
    # Glow effect
    glow_alpha = int(80 + 40 * math.sin(glow_time * 4))
    glow_surf = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*PALETTE['key_shine'], glow_alpha), 
                      (width//2 + 5, height//2 + 5), width//2 + 5)
    screen.blit(glow_surf, (x - 5, y - 5))

def draw_realistic_door(screen, x: int, y: int, width: int, height: int, is_open: bool = False):
    """Draw a realistic wooden door"""
    if is_open:
        return  # Don't draw if open
    
    # Door frame
    frame_rect = pygame.Rect(x - 2, y - 2, width + 4, height + 4)
    pygame.draw.rect(screen, PALETTE['wall_stone'], frame_rect)
    
    # Door body (wood texture)
    door_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, PALETTE['door_wood'], door_rect)
    
    # Wood grain lines
    for i in range(0, height, 8):
        line_y = y + i
        pygame.draw.line(screen, (PALETTE['door_wood'][0] - 20, PALETTE['door_wood'][1] - 20, PALETTE['door_wood'][2] - 20), 
                        (x + 2, line_y), (x + width - 2, line_y), 1)
    
    # Door panels
    panel1_rect = pygame.Rect(x + 4, y + 6, width - 8, height//2 - 10)
    panel2_rect = pygame.Rect(x + 4, y + height//2 + 4, width - 8, height//2 - 10)
    pygame.draw.rect(screen, PALETTE['door_wood'], panel1_rect, 2)
    pygame.draw.rect(screen, PALETTE['door_wood'], panel2_rect, 2)
    
    # Door handle
    handle_center = (x + width - 8, y + height//2)
    pygame.draw.circle(screen, PALETTE['door_handle'], handle_center, 4)
    pygame.draw.circle(screen, PALETTE['door_metal'], handle_center, 2)
    
    # Shadow effect
    shadow_rect = pygame.Rect(x + 2, y + 2, width, height)
    shadow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (*PALETTE['shadow'], 100), (0, 0, width, height))
    screen.blit(shadow_surf, (x + 2, y + 2))

def draw_modern_ui_panel(screen, rect: pygame.Rect, alpha: int = 200):
    """Draw a modern UI panel with gradient and border"""
    # Create gradient background
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    for y in range(rect.height):
        gradient_ratio = y / rect.height
        color1 = PALETTE['ui_panel']
        color2 = PALETTE['bg_secondary']
        
        r = int(color1[0] * (1 - gradient_ratio) + color2[0] * gradient_ratio)
        g = int(color1[1] * (1 - gradient_ratio) + color2[1] * gradient_ratio)
        b = int(color1[2] * (1 - gradient_ratio) + color2[2] * gradient_ratio)
        
        pygame.draw.line(panel_surf, (r, g, b, alpha), (0, y), (rect.width, y))
    
    screen.blit(panel_surf, rect)
    
    # Border
    pygame.draw.rect(screen, PALETTE['ui_border'], rect, 2)
    
    # Subtle inner highlight
    inner_rect = pygame.Rect(rect.x + 1, rect.y + 1, rect.width - 2, rect.height - 2)
    pygame.draw.rect(screen, (*PALETTE['ui_accent'], 30), inner_rect, 1)

def draw_circular_timer(screen, center_x: int, center_y: int, radius: int, 
                       time_remaining: float, max_time: float):
    """Draw a circular timer with modern styling"""
    # Background circle
    pygame.draw.circle(screen, PALETTE['bg_secondary'], (center_x, center_y), radius + 3)
    pygame.draw.circle(screen, PALETTE['ui_border'], (center_x, center_y), radius + 3, 2)
    
    # Timer progress
    progress = time_remaining / max_time
    angle = 2 * math.pi * progress - math.pi / 2  # Start from top
    
    # Color based on time remaining
    if progress > 0.5:
        color = PALETTE['ui_success']
    elif progress > 0.2:
        color = PALETTE['ui_warning']
    else:
        color = PALETTE['ui_danger']
    
    # Draw progress arc
    if progress > 0:
        points = [(center_x, center_y)]
        for i in range(int(360 * progress) + 1):
            angle_rad = math.radians(i - 90)
            x = center_x + radius * math.cos(angle_rad)
            y = center_y + radius * math.sin(angle_rad)
            points.append((x, y))
        
        if len(points) > 2:
            pygame.draw.polygon(screen, color, points)
    
    # Inner circle
    pygame.draw.circle(screen, PALETTE['bg_primary'], (center_x, center_y), radius - 5)
    
    # Time text
    font = pygame.font.Font(None, 24)
    time_text = f"{time_remaining:.1f}s"
    text_surface = font.render(time_text, True, PALETTE['text_primary'])
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    screen.blit(text_surface, text_rect)

def draw_lesson_panel(screen, lesson_text: str, x: int, y: int, width: int):
    """Draw a beautiful lesson panel with the real-life wisdom"""
    # Calculate panel height based on text
    font = pygame.font.Font(None, 28)
    words = lesson_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] > width - 40:
            if current_line:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                lines.append(word)
                current_line = ""
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line.strip())
    
    panel_height = len(lines) * 35 + 40
    panel_rect = pygame.Rect(x, y, width, panel_height)
    
    # Draw modern panel
    draw_modern_ui_panel(screen, panel_rect, 220)
    
    # Draw lesson icon (lightbulb)
    icon_center = (x + 25, y + 25)
    pygame.draw.circle(screen, PALETTE['ui_warning'], icon_center, 12)
    pygame.draw.circle(screen, PALETTE['text_primary'], icon_center, 8)
    
    # Draw lesson text
    title_font = pygame.font.Font(None, 32)
    title_surface = title_font.render("Life Lesson", True, PALETTE['ui_accent'])
    screen.blit(title_surface, (x + 50, y + 10))
    
    # Draw lesson content
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, PALETTE['text_primary'])
        screen.blit(line_surface, (x + 20, y + 45 + i * 35))

def create_background_pattern(screen):
    """Create a subtle background pattern"""
    width, height = screen.get_size()
    
    # Gradient background
    for y in range(height):
        gradient_ratio = y / height
        color1 = PALETTE['bg_primary']
        color2 = PALETTE['bg_secondary']
        
        r = int(color1[0] * (1 - gradient_ratio) + color2[0] * gradient_ratio)
        g = int(color1[1] * (1 - gradient_ratio) + color2[1] * gradient_ratio)
        b = int(color1[2] * (1 - gradient_ratio) + color2[2] * gradient_ratio)
        
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))
    
    # Subtle grid pattern
    for x in range(0, width, 50):
        pygame.draw.line(screen, (*PALETTE['ui_border'], 20), (x, 0), (x, height))
    for y in range(0, height, 50):
        pygame.draw.line(screen, (*PALETTE['ui_border'], 20), (0, y), (width, y))
