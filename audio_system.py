#!/usr/bin/env python3
"""
Enhanced Audio System for 10 Second Life
Immersive sound design with contextual audio
"""

import pygame
import math
import random
from typing import Dict, Optional

class AudioSystem:
    """Manages all game audio with dynamic mixing"""
    
    def __init__(self):
        # Initialize mixer with high quality settings
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.current_music = None
        self.ambient_sounds = {}
        
        # Create procedural sounds
        self.create_procedural_sounds()
    
    def create_procedural_sounds(self):
        """Create sounds procedurally using pygame"""
        
        # Footstep sound
        footstep = pygame.sndarray.make_sound(self.generate_footstep())
        self.sounds['footstep'] = footstep
        
        # Key pickup sound
        key_pickup = pygame.sndarray.make_sound(self.generate_key_pickup())
        self.sounds['key_pickup'] = key_pickup
        
        # Door open sound
        door_open = pygame.sndarray.make_sound(self.generate_door_open())
        self.sounds['door_open'] = door_open
        
        # Success chime
        success = pygame.sndarray.make_sound(self.generate_success_chime())
        self.sounds['success'] = success
        
        # Orb collect sound
        orb_collect = pygame.sndarray.make_sound(self.generate_orb_collect())
        self.sounds['orb_collect'] = orb_collect
        
        # Heartbeat sound
        heartbeat = pygame.sndarray.make_sound(self.generate_heartbeat())
        self.sounds['heartbeat'] = heartbeat
        
        # Ambient hum
        ambient = pygame.sndarray.make_sound(self.generate_ambient_hum())
        self.sounds['ambient'] = ambient
        
        # UI click
        ui_click = pygame.sndarray.make_sound(self.generate_ui_click())
        self.sounds['ui_click'] = ui_click
        
        # Timer warning
        timer_warning = pygame.sndarray.make_sound(self.generate_timer_warning())
        self.sounds['timer_warning'] = timer_warning
        
        # Level complete
        level_complete = pygame.sndarray.make_sound(self.generate_level_complete())
        self.sounds['level_complete'] = level_complete
    
    def generate_wave(self, frequency: float, duration: float, sample_rate: int = 44100, 
                     wave_type: str = 'sine', amplitude: float = 0.5):
        """Generate a basic waveform"""
        try:
            import numpy as np
            
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                t = float(i) / sample_rate
                
                if wave_type == 'sine':
                    wave = amplitude * math.sin(2 * math.pi * frequency * t)
                elif wave_type == 'square':
                    wave = amplitude * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1)
                elif wave_type == 'sawtooth':
                    wave = amplitude * (2 * (t * frequency - math.floor(t * frequency + 0.5)))
                elif wave_type == 'triangle':
                    wave = amplitude * (2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1)
                else:
                    wave = 0
                
                # Apply envelope (fade in/out)
                envelope = 1.0
                fade_frames = int(0.01 * sample_rate)  # 10ms fade
                if i < fade_frames:
                    envelope = i / fade_frames
                elif i > frames - fade_frames:
                    envelope = (frames - i) / fade_frames
                
                wave *= envelope
                arr[i] = [wave, wave]
            
            return (arr * 32767).astype('int16')
        except ImportError:
            # Fallback: return empty sound if numpy is not available
            return pygame.sndarray.make_sound([[0, 0]])
    
    def generate_footstep(self):
        """Generate a footstep sound"""
        try:
            import numpy as np
            
            duration = 0.15
            sample_rate = 44100
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                t = float(i) / sample_rate
                
                # Low frequency thump
                thump = 0.3 * math.sin(2 * math.pi * 80 * t) * math.exp(-t * 10)
                
                # High frequency scratch (noise)
                scratch = 0.1 * (random.random() - 0.5) * math.exp(-t * 15)
                
                wave = thump + scratch
                arr[i] = [wave, wave]
            
            return (arr * 32767).astype('int16')
        except ImportError:
            return pygame.sndarray.make_sound([[0, 0]])
    
    def generate_key_pickup(self):
        """Generate a magical key pickup sound"""
        # Rising chime with sparkle
        base_freq = 440  # A4
        harmonics = [1, 1.5, 2, 3]
        duration = 0.5
        
        import numpy as np
        sample_rate = 44100
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = float(i) / sample_rate
            wave = 0
            
            for harmonic in harmonics:
                freq = base_freq * harmonic
                amplitude = 0.2 / harmonic
                wave += amplitude * math.sin(2 * math.pi * freq * t)
            
            # Rising pitch effect
            pitch_mod = 1 + 0.5 * t
            wave *= math.exp(-t * 2)  # Decay
            
            # Add sparkle (high frequency modulation)
            sparkle = 0.1 * math.sin(2 * math.pi * 2000 * t) * math.exp(-t * 5)
            wave += sparkle
            
            arr[i] = [wave, wave]
        
        return (arr * 32767).astype('int16')
    
    def generate_door_open(self):
        """Generate a wooden door opening sound"""
        import numpy as np
        
        duration = 0.8
        sample_rate = 44100
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = float(i) / sample_rate
            
            # Creaking sound (low frequency with noise)
            creak_freq = 150 + 50 * math.sin(2 * math.pi * 3 * t)
            creak = 0.3 * math.sin(2 * math.pi * creak_freq * t)
            
            # Wood friction noise
            noise = 0.2 * (random.random() - 0.5)
            
            # Combine and apply envelope
            wave = (creak + noise) * (1 - t / duration)
            arr[i] = [wave, wave]
        
        return (arr * 32767).astype('int16')
    
    def generate_success_chime(self):
        """Generate a success chime"""
        # Major chord progression
        notes = [261.63, 329.63, 392.00, 523.25]  # C, E, G, C
        duration = 1.0
        
        import numpy as np
        sample_rate = 44100
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            t = float(i) / sample_rate
            wave = 0
            
            for j, freq in enumerate(notes):
                delay = j * 0.1  # Stagger notes
                if t > delay:
                    note_t = t - delay
                    amplitude = 0.25 * math.exp(-note_t * 2)
                    wave += amplitude * math.sin(2 * math.pi * freq * note_t)
            
            arr[i] = [wave, wave]
        
        return (arr * 32767).astype('int16')
    
    def generate_orb_collect(self):
        """Generate orb collection sound"""
        return self.generate_wave(880, 0.3, wave_type='sine', amplitude=0.4)
    
    def generate_heartbeat(self):
        """Generate heartbeat sound"""
        import numpy as np
        
        duration = 0.6
        sample_rate = 44100
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        # Two beats: lub-dub
        beat1_start = 0.0
        beat1_duration = 0.15
        beat2_start = 0.2
        beat2_duration = 0.1
        
        for i in range(frames):
            t = float(i) / sample_rate
            wave = 0
            
            # First beat (lub)
            if beat1_start <= t <= beat1_start + beat1_duration:
                beat_t = (t - beat1_start) / beat1_duration
                wave += 0.5 * math.sin(2 * math.pi * 60 * beat_t) * (1 - beat_t)
            
            # Second beat (dub)
            if beat2_start <= t <= beat2_start + beat2_duration:
                beat_t = (t - beat2_start) / beat2_duration
                wave += 0.4 * math.sin(2 * math.pi * 80 * beat_t) * (1 - beat_t)
            
            arr[i] = [wave, wave]
        
        return (arr * 32767).astype('int16')
    
    def generate_ambient_hum(self):
        """Generate ambient background hum"""
        return self.generate_wave(55, 2.0, wave_type='sine', amplitude=0.1)
    
    def generate_ui_click(self):
        """Generate UI click sound"""
        return self.generate_wave(800, 0.05, wave_type='sine', amplitude=0.3)
    
    def generate_timer_warning(self):
        """Generate timer warning beep"""
        return self.generate_wave(1000, 0.1, wave_type='square', amplitude=0.4)
    
    def generate_level_complete(self):
        """Generate level complete fanfare"""
        # Ascending scale
        notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        duration = 1.5
        
        import numpy as np
        sample_rate = 44100
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        note_duration = duration / len(notes)
        
        for i in range(frames):
            t = float(i) / sample_rate
            wave = 0
            
            note_index = int(t / note_duration)
            if note_index < len(notes):
                note_t = t - note_index * note_duration
                freq = notes[note_index]
                amplitude = 0.3 * math.exp(-note_t * 3)
                wave = amplitude * math.sin(2 * math.pi * freq * note_t)
            
            arr[i] = [wave, wave]
        
        return (arr * 32767).astype('int16')
    
    def play_sound(self, sound_name: str, volume: float = 1.0):
        """Play a sound effect"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume * self.sfx_volume)
            sound.play()
    
    def play_ambient(self, sound_name: str, loop: bool = True):
        """Play ambient sound"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(0.3 * self.sfx_volume)
            if loop:
                sound.play(-1)  # Loop indefinitely
            else:
                sound.play()
    
    def stop_ambient(self, sound_name: str):
        """Stop ambient sound"""
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
    
    def set_volumes(self, music_vol: float, sfx_vol: float):
        """Set master volumes"""
        self.music_volume = max(0.0, min(1.0, music_vol))
        self.sfx_volume = max(0.0, min(1.0, sfx_vol))
    
    def play_contextual_sound(self, context: str, **kwargs):
        """Play sound based on game context"""
        if context == "player_move":
            if random.random() < 0.1:  # 10% chance per frame
                self.play_sound('footstep', 0.3)
        
        elif context == "timer_low":
            time_remaining = kwargs.get('time_remaining', 10)
            if time_remaining < 3 and int(time_remaining * 10) % 10 == 0:
                self.play_sound('timer_warning', 0.6)
        
        elif context == "heartbeat":
            time_remaining = kwargs.get('time_remaining', 10)
            if time_remaining < 5:
                self.play_sound('heartbeat', 0.4)
    
    def cleanup(self):
        """Clean up audio resources"""
        pygame.mixer.quit()
