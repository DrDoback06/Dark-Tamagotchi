# asset_manager.py
# A simple asset management system for Dark Tamagotchi

import os
import pygame
import json

class AssetManager:
    """
    Asset management system that makes it easy to load and use game assets
    without needing to modify code.
    
    How to use:
    1. Place images in the assets/images/ folder
    2. Organize images into subfolders by type (creatures, ui, items, etc.)
    3. Update the asset_manifest.json file with new assets
    4. Access assets in code via get_image("category/asset_name")
    """
    
    def __init__(self):
        """Initialize the asset manager"""
        self.images = {}
        self.sounds = {}
        self.music = {}
        self.fonts = {}
        
        # Base paths
        self.image_path = "assets/images"
        self.sound_path = "assets/sounds"
        self.music_path = "assets/music"
        self.font_path = "assets/fonts"
        
        # Create folders if they don't exist
        self._ensure_folders_exist()
        
        # Initialize pygame resources if needed
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        # Load the asset manifest
        self.load_manifest()
        
    def _ensure_folders_exist(self):
        """Create necessary folders if they don't exist"""
        folders = [
            self.image_path,
            os.path.join(self.image_path, "creatures"),
            os.path.join(self.image_path, "ui"),
            os.path.join(self.image_path, "backgrounds"),
            os.path.join(self.image_path, "items"),
            self.sound_path,
            self.music_path,
            self.font_path
        ]
        
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"Created folder: {folder}")
                
        # Create default manifest if it doesn't exist
        if not os.path.exists("assets/asset_manifest.json"):
            self._create_default_manifest()
                
    def _create_default_manifest(self):
        """Create a default asset manifest file"""
        default_manifest = {
            "images": {
                "creatures": {
                    "skeleton": "creatures/skeleton.png",
                    "fire_elemental": "creatures/fire_elemental.png",
                    "knight": "creatures/knight.png",
                    "goblin": "creatures/goblin.png",
                    "troll": "creatures/troll.png"
                },
                "ui": {
                    "button": "ui/button.png",
                    "panel": "ui/panel.png",
                    "hp_bar": "ui/hp_bar.png",
                    "energy_bar": "ui/energy_bar.png"
                },
                "backgrounds": {
                    "main_menu": "backgrounds/main_menu.png",
                    "battle": "backgrounds/battle.png",
                    "adventure": "backgrounds/adventure.png"
                },
                "items": {
                    "potion": "items/potion.png",
                    "food": "items/food.png",
                    "scroll": "items/scroll.png"
                }
            },
            "sounds": {
                "ui": {
                    "click": "ui_click.wav",
                    "hover": "ui_hover.wav"
                },
                "battle": {
                    "attack": "battle_attack.wav",
                    "heal": "battle_heal.wav",
                    "victory": "battle_victory.wav",
                    "defeat": "battle_defeat.wav"
                }
            },
            "music": {
                "main_menu": "main_menu.mp3",
                "battle": "battle.mp3",
                "adventure": "adventure.mp3"
            },
            "fonts": {
                "main": "main_font.ttf",
                "title": "title_font.ttf"
            }
        }
        
        with open("assets/asset_manifest.json", "w") as f:
            json.dump(default_manifest, f, indent=4)
            
        print("Created default asset manifest file")
                
    def load_manifest(self):
        """Load the asset manifest and preload assets"""
        try:
            with open("assets/asset_manifest.json", "r") as f:
                self.manifest = json.load(f)
                
            # Preload images
            self._preload_images()
            
            print("Asset manifest loaded successfully")
        except Exception as e:
            print(f"Error loading asset manifest: {e}")
            # Create a default manifest in case of error
            self._create_default_manifest()
            
    def _preload_images(self):
        """Preload images from the manifest"""
        if "images" not in self.manifest:
            return
            
        for category, assets in self.manifest["images"].items():
            for name, path in assets.items():
                # Full path to the image
                full_path = os.path.join(self.image_path, path)
                
                # Check if the file exists, if not, create a placeholder
                if not os.path.exists(full_path):
                    self._create_placeholder_image(full_path, name)
                    
                try:
                    # Load the image and store it
                    img = pygame.image.load(full_path).convert_alpha()
                    key = f"{category}/{name}"
                    self.images[key] = img
                    print(f"Loaded image: {key}")
                except Exception as e:
                    print(f"Error loading image {full_path}: {e}")
                    
    def _create_placeholder_image(self, path, name):
        """Create a placeholder image if the asset doesn't exist"""
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Create a simple surface
        size = (64, 64)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Fill with a color based on name hash
        name_hash = hash(name)
        r = (name_hash & 0xFF0000) >> 16
        g = (name_hash & 0x00FF00) >> 8
        b = name_hash & 0x0000FF
        
        pygame.draw.rect(surface, (r, g, b, 180), (0, 0, size[0], size[1]))
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, size[0], size[1]), 2)
        
        # Add text
        font = pygame.font.SysFont("Arial", 12)
        text = font.render(name, True, (255, 255, 255))
        surface.blit(text, (size[0]//2 - text.get_width()//2, size[1]//2 - text.get_height()//2))
        
        # Save to file
        pygame.image.save(surface, path)
        print(f"Created placeholder image: {path}")
        
    def get_image(self, key, scale=None):
        """
        Get an image by its key
        
        Parameters:
        -----------
        key : str
            Image key in format "category/name" (e.g., "creatures/skeleton")
        scale : tuple, optional
            Scale to resize the image to (width, height)
            
        Returns:
        --------
        pygame.Surface
            The loaded image, or a placeholder if not found
        """
        if key in self.images:
            img = self.images[key]
            if scale:
                return pygame.transform.scale(img, scale)
            return img
            
        # If image is not found, create a placeholder
        print(f"Image not found: {key}, creating placeholder")
        size = (64, 64) if not scale else scale
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 255, 180), (0, 0, size[0], size[1]))
        
        # Add text
        font = pygame.font.SysFont("Arial", 12)
        text = font.render(key, True, (255, 255, 255))
        text_rect = text.get_rect(center=(size[0]//2, size[1]//2))
        surface.blit(text, text_rect)
        
        return surface
        
    def play_sound(self, key, volume=1.0):
        """
        Play a sound by its key
        
        Parameters:
        -----------
        key : str
            Sound key in format "category/name" (e.g., "battle/attack")
        volume : float, optional
            Volume level from 0.0 to 1.0
            
        Returns:
        --------
        pygame.mixer.Sound or None
            The sound object, or None if not found
        """
        # Load sound on demand if not already loaded
        if key not in self.sounds:
            category, name = key.split('/')
            if category in self.manifest.get("sounds", {}) and name in self.manifest["sounds"][category]:
                path = os.path.join(self.sound_path, self.manifest["sounds"][category][name])
                if os.path.exists(path):
                    try:
                        self.sounds[key] = pygame.mixer.Sound(path)
                    except Exception as e:
                        print(f"Error loading sound {path}: {e}")
                        return None
                else:
                    print(f"Sound file not found: {path}")
                    return None
            else:
                print(f"Sound key not found in manifest: {key}")
                return None
                
        sound = self.sounds.get(key)
        if sound:
            sound.set_volume(volume)
            sound.play()
        return sound
        
    def play_music(self, key, volume=0.5, loops=-1):
        """
        Play music by its key
        
        Parameters:
        -----------
        key : str
            Music key (e.g., "main_menu")
        volume : float, optional
            Volume level from 0.0 to 1.0
        loops : int, optional
            Number of times to repeat (-1 for infinite)
            
        Returns:
        --------
        bool
            True if successful, False otherwise
        """
        if key not in self.music:
            if key in self.manifest.get("music", {}):
                path = os.path.join(self.music_path, self.manifest["music"][key])
                if os.path.exists(path):
                    self.music[key] = path
                else:
                    print(f"Music file not found: {path}")
                    return False
            else:
                print(f"Music key not found in manifest: {key}")
                return False
                
        try:
            pygame.mixer.music.load(self.music[key])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            return True
        except Exception as e:
            print(f"Error playing music {key}: {e}")
            return False
            
    def get_font(self, key, size):
        """
        Get a font by its key
        
        Parameters:
        -----------
        key : str
            Font key (e.g., "main")
        size : int
            Font size in points
            
        Returns:
        --------
        pygame.font.Font
            The font object, or a default font if not found
        """
        font_key = f"{key}_{size}"
        
        if font_key not in self.fonts:
            if key in self.manifest.get("fonts", {}):
                path = os.path.join(self.font_path, self.manifest["fonts"][key])
                if os.path.exists(path):
                    try:
                        self.fonts[font_key] = pygame.font.Font(path, size)
                    except Exception as e:
                        print(f"Error loading font {path}: {e}")
                        self.fonts[font_key] = pygame.font.SysFont("Arial", size)
                else:
                    print(f"Font file not found: {path}")
                    self.fonts[font_key] = pygame.font.SysFont("Arial", size)
            else:
                print(f"Font key not found in manifest: {key}")
                self.fonts[font_key] = pygame.font.SysFont("Arial", size)
                
        return self.fonts[font_key]

# Initialize the global asset manager
_instance = None

def get_instance():
    """Get the global asset manager instance"""
    global _instance
    if _instance is None:
        _instance = AssetManager()
    return _instance
