import pygame
import os


class AudioManager:
    def __init__(self):
        self.sfx_cache = {}
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except:
            self.audio_enabled = False
            print("Warning: No audio device found.")

        self.current_bgm = None

    def play_sfx(self, sound_name):
        if not self.audio_enabled: return

        if sound_name not in self.sfx_cache:
            filepath = f"assets/{sound_name}.wav"
            if os.path.exists(filepath):
                self.sfx_cache[sound_name] = pygame.mixer.Sound(filepath)
                self.sfx_cache[sound_name].set_volume(1.0)
            else:
                print(f"Warning: Missing SFX asset: {filepath}")
                return

        print(f"🔊 [SFX] Played: {sound_name}")
        self.sfx_cache[sound_name].play()

    def play_bgm(self, track_name):
        if not self.audio_enabled: return
        if self.current_bgm == track_name:
            return

        self.current_bgm = track_name
        print(f"🎵 [BGM] Changed background music to: {track_name}")

        filepath = f"assets/{track_name}.mp3"
        if os.path.exists(filepath):
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)