import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

error_msg = "Pygame is not installed. Install it using:\n pip install pygame"

class SoundPlayer:
    def __init__(self, app):
        self.developer = app.developer
        self.volume = 0.5
        pygame.mixer.init()  # Initialize pygame mixer once

    def play(self, sound, volume=None):
        if volume is None:
            volume = 50
        elif volume <= 0:
            if self.developer:
                print("The volume is very low, set to '0'.")
            volume = 0
        elif volume > 100:
            if self.developer:
                print("The volume is too high, set to max, 100.")
            volume = 100

        volume /= 100  # Convert 1-100 to 0.0-1.0

        try:
            pygame.mixer.music.load(sound)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
        except Exception as e:
            if self.developer:
                print(f"Error while playing sound: {e}")

    def stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            if self.developer:
                print(f"Error: {e}")

    def master_volume(self, volume):
        if volume <= 0:
            if self.developer:
                print("The volume is very low, set to '0'.")
            volume = 0
        elif volume > 100:
            if self.developer:
                print("The volume is too high, set to max, 100.")
            volume = 100

        volume /= 100

        try:
            pygame.mixer.music.set_volume(volume)
        except Exception as e:
            if self.developer:
                print(f"Error setting volume: {e}")

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def mute(self):
        pygame.mixer.music.set_volume(0)
