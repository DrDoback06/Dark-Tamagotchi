# sound_manager.py
# A simple sound management system for Dark Tamagotchi

import pygame
import os
import json
from asset_manager import get_instance as get_asset_manager

class SoundManager:
    """
    Sound manager for easily playing sounds and music in the game.
    
    This class provides an easy interface for playing sounds and music,
    managing volume levels, and handling sound effects.
    """
    
    def __init__(self):
        """Initialize the sound manager"""
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        # Get the asset manager
        self.asset_manager = get_asset_manager()
        
        # Volume settings
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.muted = False
        
        # Currently playing music
        self.current_music = None
        
        # Load settings if available
        self.load_settings()
        
    def load_settings(self):
        """Load sound settings from file"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    
                if "sound" in settings:
                    sound_settings = settings["sound"]
                    self.music_volume = sound_settings.get("music_volume", 0.5)
                    self.sound_volume = sound_settings.get("sound_volume", 0.7)
                    self.muted = sound_settings.get("muted", False)
                    
                    # Apply settings
                    pygame.mixer.music.set_volume(0 if self.muted else self.music_volume)
        except Exception as e:
            print(f"Error loading sound settings: {e}")
            
    def save_settings(self):
        """Save sound settings to file"""
        try:
            settings = {}
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    
            settings["sound"] = {
                "music_volume": self.music_volume,
                "sound_volume": self.sound_volume,
                "muted": self.muted
            }
            
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving sound settings: {e}")
            
    def play_sound(self, sound_key):
        """
        Play a sound effect
        
        Parameters:
        -----------
        sound_key : str
            Key of the sound to play (e.g., "battle/attack")
            
        Returns:
        --------
        bool
            True if sound was played, False otherwise
        """
        if self.muted:
            return False
            
        volume = self.sound_volume
        return self.asset_manager.play_sound(sound_key, volume) is not None
        
    def play_music(self, music_key, loops=-1):
        """
        Play background music
        
        Parameters:
        -----------
        music_key : str
            Key of the music to play (e.g., "main_menu")
        loops : int, optional
            Number of times to loop the music (-1 for infinite)
            
        Returns:
        --------
        bool
            True if music was started, False otherwise
        """
        # Don't restart the same music
        if self.current_music == music_key:
            return True
            
        volume = 0 if self.muted else self.music_volume
        success = self.asset_manager.play_music(music_key, volume, loops)
        
        if success:
            self.current_music = music_key
            
        return success
        
    def stop_music(self):
        """Stop the currently playing music"""
        pygame.mixer.music.stop()
        self.current_music = None
        
    def pause_music(self):
        """Pause the currently playing music"""
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        """Unpause the music"""
        pygame.mixer.music.unpause()
        
    def set_music_volume(self, volume):
        """
        Set the music volume
        
        Parameters:
        -----------
        volume : float
            Volume level from 0.0 to 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if not self.muted:
            pygame.mixer.music.set_volume(self.music_volume)
        self.save_settings()
        
    def set_sound_volume(self, volume):
        """
        Set the sound effect volume
        
        Parameters:
        -----------
        volume : float
            Volume level from 0.0 to 1.0
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        self.save_settings()
        
    def toggle_mute(self):
        """Toggle mute/unmute for all audio"""
        self.muted = not self.muted
        
        # Apply mute setting
        pygame.mixer.music.set_volume(0 if self.muted else self.music_volume)
        
        self.save_settings()
        return self.muted
        
    def is_muted(self):
        """Check if audio is muted"""
        return self.muted
        
    def get_music_volume(self):
        """Get the current music volume"""
        return self.music_volume
        
    def get_sound_volume(self):
        """Get the current sound effect volume"""
        return self.sound_volume

# Initialize the global sound manager
_instance = None

def get_instance():
    """Get the global sound manager instance"""
    global _instance
    if _instance is None:
        _instance = SoundManager()
    return _instance
