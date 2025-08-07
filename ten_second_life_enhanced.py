#!/usr/bin/env python3
"""
10 Second Life: Echoes of a Short World - Enhanced Edition
Beautiful graphics, immersive audio, and meaningful life lessons
"""

import pygame
import json
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Import our enhanced systems
from enhanced_graphics import *
from audio_system import AudioSystem

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
LIFE_DURATION = 10.0

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    DEATH = "death"
    LEVEL_COMPLETE = "level_complete"
    LESSON = "lesson"
    VICTORY = "victory"

@dataclass
class GameProgress:
    current_level: int = 1
    levels_completed: List[int] = None
    total_lives_used: int = 0
    lessons_learned: List[str] = None
    
    def __post_init__(self):
        if self.levels_completed is None:
            self.levels_completed = []
        if self.lessons_learned is None:
            self.lessons_learned = []

class GameObject:
    def __init__(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        self.glow_time = 0
    
    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, dt: float):
        self.glow_time += dt
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class EnhancedPlayer(GameObject):
    def __init__(self, x: int, y: int, audio_system: AudioSystem):
        super().__init__(x, y, 20, 20, PALETTE['player_blue'])
        self.speed = 200
        self.inventory = None
        self.start_x = x
        self.start_y = y
        self.audio = audio_system
        self.move_timer = 0
    
    def update(self, dt: float, keys):
        super().update(dt)
        old_x, old_y = self.x, self.y
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * dt
        
        self.x = max(10, min(WINDOW_WIDTH - self.width - 10, self.x))
        self.y = max(10, min(WINDOW_HEIGHT - self.height - 10, self.y))
        
        if (old_x != self.x or old_y != self.y):
            self.move_timer += dt
            if self.move_timer > 0.3:
                self.audio.play_contextual_sound("player_move")
                self.move_timer = 0
        
        self.update_rect()
    
    def reset_position(self):
        self.x = self.start_x
        self.y = self.start_y
        self.inventory = None
        self.update_rect()
    
    def draw(self, screen):
        draw_realistic_player(screen, self.x, self.y, self.width, self.height)

class EnhancedItem(GameObject):
    def __init__(self, x: int, y: int, item_type: str, audio_system: AudioSystem):
        color = PALETTE.get(f'{item_type}_gold', PALETTE['orb_gold'])
        super().__init__(x, y, 15, 15, color)
        self.type = item_type
        self.collected = False
        self.audio = audio_system
    
    def collect(self):
        if not self.collected:
            self.collected = True
            if self.type == 'orb':
                self.audio.play_sound('orb_collect')
            elif self.type == 'key':
                self.audio.play_sound('key_pickup')
            else:
                self.audio.play_sound('success', 0.6)
    
    def draw(self, screen):
        if not self.collected:
            if self.type == 'orb':
                draw_realistic_orb(screen, self.x, self.y, self.width, self.height, self.glow_time)
            elif self.type == 'key':
                draw_realistic_key(screen, self.x, self.y, self.width, self.height, self.glow_time)

class EnhancedDoor(GameObject):
    def __init__(self, x: int, y: int, audio_system: AudioSystem):
        super().__init__(x, y, 30, 50, PALETTE['door_wood'])
        self.is_open = False
        self.audio = audio_system
    
    def open_door(self):
        if not self.is_open:
            self.is_open = True
            self.audio.play_sound('door_open')
    
    def draw(self, screen):
        draw_realistic_door(screen, self.x, self.y, self.width, self.height, self.is_open)

class Level:
    def __init__(self, number: int, title: str, objective: str, lesson: str):
        self.number = number
        self.title = title
        self.objective = objective
        self.lesson = lesson
        self.completed = False
        self.items = []
        self.doors = []
        self.particles = ParticleSystem()
    
    def setup(self, audio_system: AudioSystem):
        pass
    
    def update(self, dt: float, player: EnhancedPlayer) -> bool:
        self.particles.update(dt)
        for item in self.items:
            item.update(dt)
        return False
    
    def handle_interaction(self, player: EnhancedPlayer) -> Optional[str]:
        return None
    
    def draw(self, screen):
        for door in self.doors:
            door.draw(screen)
        for item in self.items:
            item.draw(screen)
        self.particles.draw(screen)

class Level1_FirstSteps(Level):
    def __init__(self):
        super().__init__(
            1, "First Steps", "Collect the glowing orb to begin your journey",
            "Success begins with taking the first step. Every journey starts with action, no matter how small."
        )
    
    def setup(self, audio_system: AudioSystem):
        orb = EnhancedItem(WINDOW_WIDTH//2 - 7, WINDOW_HEIGHT//2 - 7, 'orb', audio_system)
        self.items.append(orb)
    
    def update(self, dt: float, player: EnhancedPlayer) -> bool:
        super().update(dt, player)
        
        if random.random() < 0.3:
            self.particles.add_sparkle(WINDOW_WIDTH//2 + random.randint(-20, 20), 
                                     WINDOW_HEIGHT//2 + random.randint(-20, 20))
        
        for item in self.items:
            if not item.collected and player.rect.colliderect(item.rect):
                item.collect()
                for _ in range(10):
                    self.particles.add_sparkle(player.x + player.width//2, 
                                             player.y + player.height//2, 
                                             PALETTE['sparkle_white'])
                return True
        return False

class Level2_TheDoor(Level):
    def __init__(self):
        super().__init__(
            2, "The Door", "Find the key and unlock the door",
            "Opportunities exist everywhere, but preparation is the key that opens doors to success."
        )
    
    def setup(self, audio_system: AudioSystem):
        key = EnhancedItem(100, WINDOW_HEIGHT//2, 'key', audio_system)
        self.items.append(key)
        door = EnhancedDoor(WINDOW_WIDTH - 100, WINDOW_HEIGHT//2 - 25, audio_system)
        self.doors.append(door)
    
    def update(self, dt: float, player: EnhancedPlayer) -> bool:
        super().update(dt, player)
        
        for item in self.items:
            if not item.collected and random.random() < 0.2:
                self.particles.add_sparkle(item.x + item.width//2, item.y + item.height//2)
        
        for item in self.items:
            if not item.collected and player.rect.colliderect(item.rect):
                item.collect()
                player.inventory = 'key'
        
        for door in self.doors:
            if door.is_open and player.rect.colliderect(door.rect):
                return True
        return False
    
    def handle_interaction(self, player: EnhancedPlayer) -> Optional[str]:
        for door in self.doors:
            if player.rect.colliderect(door.rect) and not door.is_open:
                if player.inventory == 'key':
                    door.open_door()
                    player.inventory = None
                    return "Door unlocked! Walk through to continue."
                else:
                    return "This door requires a key. Preparation opens opportunities."
        return None

class TenSecondLifeEnhanced:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("10 Second Life: Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.audio = AudioSystem()
        self.particles = ParticleSystem()
        
        self.state = GameState.MENU
        self.progress = GameProgress()
        self.life_timer = LIFE_DURATION
        self.message = ""
        self.message_timer = 0
        self.lesson_timer = 0
        
        self.player = EnhancedPlayer(50, WINDOW_HEIGHT//2, self.audio)
        self.current_level = None
        self.levels = {1: Level1_FirstSteps(), 2: Level2_TheDoor()}
        
        self.font_title = pygame.font.Font(None, 64)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.audio.play_ambient('ambient')
        self.load_level(self.progress.current_level)
    
    def load_level(self, level_number: int):
        if level_number in self.levels:
            self.current_level = self.levels[level_number]
            self.current_level.setup(self.audio)
            self.player.reset_position()
            self.life_timer = LIFE_DURATION
            self.message = f"Level {level_number}: {self.current_level.title}"
            self.message_timer = 3.0
            self.audio.play_sound('ui_click')
    
    def start_new_life(self):
        self.state = GameState.PLAYING
        self.life_timer = LIFE_DURATION
        self.progress.total_lives_used += 1
        self.player.reset_position()
        self.audio.play_sound('heartbeat', 0.6)
    
    def complete_level(self):
        self.state = GameState.LESSON
        self.current_level.completed = True
        self.lesson_timer = 6.0
        
        if self.progress.current_level not in self.progress.levels_completed:
            self.progress.levels_completed.append(self.progress.current_level)
            self.progress.lessons_learned.append(self.current_level.lesson)
        
        self.audio.play_sound('level_complete')
    
    def next_level(self):
        self.progress.current_level += 1
        if self.progress.current_level <= len(self.levels):
            self.load_level(self.progress.current_level)
            self.state = GameState.PLAYING
        else:
            self.state = GameState.VICTORY
            self.audio.play_sound('success')
    
    def update(self, dt: float):
        self.particles.update(dt)
        
        if self.state == GameState.PLAYING:
            self.life_timer -= dt
            self.audio.play_contextual_sound("timer_low", time_remaining=self.life_timer)
            if self.life_timer < 5:
                self.audio.play_contextual_sound("heartbeat", time_remaining=self.life_timer)
            
            if self.life_timer <= 0:
                self.state = GameState.DEATH
                return
            
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys)
            
            if self.current_level:
                if self.current_level.update(dt, self.player):
                    self.complete_level()
        
        elif self.state == GameState.LESSON:
            self.lesson_timer -= dt
            if self.lesson_timer <= 0:
                self.state = GameState.LEVEL_COMPLETE
        
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.audio.play_sound('ui_click', 0.4)
                
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_new_life()
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_e or event.key == pygame.K_SPACE:
                        if self.current_level:
                            msg = self.current_level.handle_interaction(self.player)
                            if msg:
                                self.message = msg
                                self.message_timer = 3.0
                    elif event.key == pygame.K_r:
                        self.load_level(self.progress.current_level)
                        self.start_new_life()
                
                elif self.state == GameState.DEATH:
                    if event.key == pygame.K_SPACE:
                        self.start_new_life()
                    elif event.key == pygame.K_r:
                        self.load_level(self.progress.current_level)
                        self.start_new_life()
                
                elif self.state == GameState.LESSON:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.LEVEL_COMPLETE
                
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_SPACE:
                        self.next_level()
    
    def draw_enhanced_ui(self):
        draw_circular_timer(self.screen, WINDOW_WIDTH - 80, 80, 50, 
                          self.life_timer, LIFE_DURATION)
        
        if self.current_level:
            panel_rect = pygame.Rect(10, 10, 400, 100)
            draw_modern_ui_panel(self.screen, panel_rect)
            
            title_surface = self.font_medium.render(f"Level {self.current_level.number}: {self.current_level.title}", 
                                                   True, PALETTE['text_primary'])
            self.screen.blit(title_surface, (20, 25))
            
            obj_surface = self.font_small.render(self.current_level.objective, True, PALETTE['ui_warning'])
            self.screen.blit(obj_surface, (20, 55))
            
            lives_surface = self.font_small.render(f"Lives Used: {self.progress.total_lives_used}", 
                                                  True, PALETTE['text_secondary'])
            self.screen.blit(lives_surface, (20, 80))
        
        if self.player.inventory:
            inv_rect = pygame.Rect(10, WINDOW_HEIGHT - 60, 200, 40)
            draw_modern_ui_panel(self.screen, inv_rect)
            inv_surface = self.font_small.render(f"Carrying: {self.player.inventory}", 
                                               True, PALETTE['ui_success'])
            self.screen.blit(inv_surface, (20, WINDOW_HEIGHT - 45))
        
        if self.message:
            msg_surface = self.font_medium.render(self.message, True, PALETTE['ui_warning'])
            msg_rect = msg_surface.get_rect(center=(WINDOW_WIDTH//2, 150))
            bg_rect = pygame.Rect(msg_rect.x - 15, msg_rect.y - 10, msg_rect.width + 30, msg_rect.height + 20)
            draw_modern_ui_panel(self.screen, bg_rect)
            self.screen.blit(msg_surface, msg_rect)
    
    def draw_menu(self):
        create_background_pattern(self.screen)
        
        title = self.font_title.render("10 Second Life", True, PALETTE['text_primary'])
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_large.render("Enhanced Edition", True, PALETTE['ui_warning'])
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
        self.screen.blit(subtitle, subtitle_rect)
        
        panel_rect = pygame.Rect(WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 + 20, 400, 120)
        draw_modern_ui_panel(self.screen, panel_rect)
        
        instruction1 = self.font_medium.render("Press SPACE to begin", True, PALETTE['ui_success'])
        instruction1_rect = instruction1.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50))
        self.screen.blit(instruction1, instruction1_rect)
        
        instruction2 = self.font_small.render("Each level teaches a life lesson", True, PALETTE['text_secondary'])
        instruction2_rect = instruction2.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 80))
        self.screen.blit(instruction2, instruction2_rect)
    
    def draw_lesson_screen(self):
        create_background_pattern(self.screen)
        
        if self.current_level:
            draw_lesson_panel(self.screen, self.current_level.lesson, 
                            WINDOW_WIDTH//2 - 300, WINDOW_HEIGHT//2 - 150, 600)
            
            continue_text = self.font_medium.render("Press SPACE to continue", True, PALETTE['ui_success'])
            continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 150))
            self.screen.blit(continue_text, continue_rect)
    
    def draw_death_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*PALETTE['shadow'], 150), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2 - 100, 400, 200)
        draw_modern_ui_panel(self.screen, panel_rect)
        
        death_text = self.font_large.render("Life Ended", True, PALETTE['ui_danger'])
        death_rect = death_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        self.screen.blit(death_text, death_rect)
        
        continue_text = self.font_medium.render("Press SPACE for new life", True, PALETTE['text_primary'])
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_level_complete(self):
        create_background_pattern(self.screen)
        
        complete_text = self.font_large.render("Level Complete!", True, PALETTE['ui_success'])
        complete_rect = complete_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        self.screen.blit(complete_text, complete_rect)
        
        continue_text = self.font_medium.render("Press SPACE to continue", True, PALETTE['text_primary'])
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_victory(self):
        create_background_pattern(self.screen)
        
        victory_text = self.font_title.render("Congratulations!", True, PALETTE['ui_success'])
        victory_rect = victory_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
        self.screen.blit(victory_text, victory_rect)
        
        stats_text = f"Journey completed in {self.progress.total_lives_used} lives"
        stats_surface = self.font_medium.render(stats_text, True, PALETTE['text_primary'])
        stats_rect = stats_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
        self.screen.blit(stats_surface, stats_rect)
    
    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
        else:
            create_background_pattern(self.screen)
            
            if self.state == GameState.PLAYING:
                if self.current_level:
                    self.current_level.draw(self.screen)
                self.player.draw(self.screen)
                self.draw_enhanced_ui()
            elif self.state == GameState.DEATH:
                if self.current_level:
                    self.current_level.draw(self.screen)
                self.player.draw(self.screen)
                self.draw_death_screen()
            elif self.state == GameState.LESSON:
                self.draw_lesson_screen()
            elif self.state == GameState.LEVEL_COMPLETE:
                self.draw_level_complete()
            elif self.state == GameState.VICTORY:
                self.draw_victory()
        
        self.particles.draw(self.screen)
        pygame.display.flip()
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        
        self.audio.cleanup()
        pygame.quit()

if __name__ == "__main__":
    game = TenSecondLifeEnhanced()
    game.run()
