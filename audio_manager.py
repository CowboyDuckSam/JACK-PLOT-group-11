import pygame
import os


class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except:
            self.audio_enabled = False
            print("Warning: No audio device found.")

        self.current_bgm = None

    def play_sfx(self, sound_name):
        if not self.audio_enabled: return
        print(f"🔊 [SFX] Played: {sound_name}")

        filepath = f"assets/{sound_name}.wav"
        if os.path.exists(filepath):
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(1.0)  # Make sure SFX are at 100% volume
            sound.play()

    def play_bgm(self, track_name):
        if not self.audio_enabled: return
        if self.current_bgm == track_name:
            return

        self.current_bgm = track_name
        print(f"🎵 [BGM] Changed background music to: {track_name}")

        filepath = f"assets/{track_name}.mp3"
        if os.path.exists(filepath):
            pygame.mixer.music.load(filepath)

            # Lower the music to 30% volume so the sound effects cut through!
            pygame.mixer.music.set_volume(0.3)

            pygame.mixer.music.play(-1)