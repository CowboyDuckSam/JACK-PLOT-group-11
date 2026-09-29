import pygame
import os


class AudioManager:
    def __init__(self):
        # start up the pygame mixer safely
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except:
            self.audio_enabled = False
            print("Warning: No audio device found.")

        self.current_bgm = None

    def play_sfx(self, sound_name):
        if not self.audio_enabled: return

        # for now, just print it so we know the system works!
        print(f"🔊 [SFX] Played: {sound_name}")

        # when you have files, uncomment this:
        # filepath = f"assets/{sound_name}.wav"
        # if os.path.exists(filepath):
        #     sound = pygame.mixer.Sound(filepath)
        #     sound.play()

    def play_bgm(self, track_name):
        if not self.audio_enabled: return

        # don't restart the song if it's already playing
        if self.current_bgm == track_name:
            return

        self.current_bgm = track_name
        print(f"🎵 [BGM] Changed background music to: {track_name}")

        # when you have files, uncomment this:
        # filepath = f"assets/{track_name}.mp3"
        # if os.path.exists(filepath):
        #     pygame.mixer.music.load(filepath)
        #     pygame.mixer.music.play(-1) # -1 means loop forever