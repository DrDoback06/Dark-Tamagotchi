# database.py
# Save/load system for Dark Tamagotchi

import json
import os
import time
from creatures import Creature
from items import item_from_dict

# File paths
CREATURES_FILE = "saved_creatures.json"
TOMBSTONES_FILE = "tombstones.json"
SETTINGS_FILE = "settings.json"
SAVE_DIR = "saves"

def ensure_save_directory():
    """Ensure the save directory exists"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def get_save_path(filename):
    """Get the full path for a save file"""
    ensure_save_directory()
    return os.path.join(SAVE_DIR, filename)

def save_creatures(creatures):
    """
    Save a list of creatures to file
    
    Parameters:
    -----------
    creatures : list
        List of Creature objects to save
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        data = [creature.to_dict() for creature in creatures]
        with open(get_save_path(CREATURES_FILE), "w") as f:
            json.dump(data, f, indent=4)
        print(f"[Database] Saved {len(creatures)} creatures.")
        return True
    except Exception as e:
        print(f"[Database] Error saving creatures: {e}")
        return False

def load_creatures():
    """
    Load creatures from file
    
    Returns:
    --------
    list
        List of Creature objects loaded from file
    """
    creatures = []
    try:
        file_path = get_save_path(CREATURES_FILE)
        if not os.path.exists(file_path):
            print("[Database] No saved creatures found.")
            return creatures
            
        with open(file_path, "r") as f:
            data = json.load(f)
            
        for creature_data in data:
            try:
                creature = Creature.from_dict(creature_data)
                creatures.append(creature)
            except Exception as e:
                print(f"[Database] Error loading creature: {e}")
                
        print(f"[Database] Loaded {len(creatures)} creatures.")
        return creatures
    except Exception as e:
        print(f"[Database] Error loading creatures: {e}")
        return creatures

def save_tombstone(tombstone):
    """
    Save a tombstone record
    
    Parameters:
    -----------
    tombstone : dict
        Tombstone data to save
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        file_path = get_save_path(TOMBSTONES_FILE)
        tombstones = []
        
        # Load existing tombstones if file exists
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                tombstones = json.load(f)
                
        # Add the new tombstone
        tombstones.append(tombstone)
        
        # Save back to file
        with open(file_path, "w") as f:
            json.dump(tombstones, f, indent=4)
            
        print(f"[Database] Saved tombstone for {tombstone['creature_type']}.")
        return True
    except Exception as e:
        print(f"[Database] Error saving tombstone: {e}")
        return False

def load_tombstones():
    """
    Load tombstone records
    
    Returns:
    --------
    list
        List of tombstone records
    """
    tombstones = []
    try:
        file_path = get_save_path(TOMBSTONES_FILE)
        if not os.path.exists(file_path):
            print("[Database] No tombstones found.")
            return tombstones
            
        with open(file_path, "r") as f:
            tombstones = json.load(f)
            
        print(f"[Database] Loaded {len(tombstones)} tombstones.")
        return tombstones
    except Exception as e:
        print(f"[Database] Error loading tombstones: {e}")
        return tombstones

def transfer_tombstone_xp(tombstone_index, target_creature):
    """
    Transfer XP from a tombstone to a creature
    
    Parameters:
    -----------
    tombstone_index : int
        Index of the tombstone to transfer from
    target_creature : Creature
        Creature to transfer XP to
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        tombstones = load_tombstones()
        
        # Validate index
        if tombstone_index < 0 or tombstone_index >= len(tombstones):
            print(f"[Database] Invalid tombstone index: {tombstone_index}")
            return False
            
        # Get the tombstone
        tombstone = tombstones[tombstone_index]
        
        # Check if already transferred
        if tombstone.get("xp_transferred", False):
            print(f"[Database] Tombstone XP already transferred.")
            return False
            
        # Get bonus XP
        bonus_xp = tombstone.get("bonus_xp", 0)
        if bonus_xp <= 0:
            print(f"[Database] No bonus XP available in tombstone.")
            return False
            
        # Transfer XP
        target_creature.gain_xp(bonus_xp)
        print(f"[Database] Transferred {bonus_xp} XP from {tombstone['creature_type']} to {target_creature.creature_type}.")
        
        # Mark as transferred
        tombstone["xp_transferred"] = True
        
        # Save updated tombstones
        with open(get_save_path(TOMBSTONES_FILE), "w") as f:
            json.dump(tombstones, f, indent=4)
            
        return True
    except Exception as e:
        print(f"[Database] Error transferring tombstone XP: {e}")
        return False

def save_settings(settings):
    """
    Save game settings
    
    Parameters:
    -----------
    settings : dict
        Settings to save
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        with open(get_save_path(SETTINGS_FILE), "w") as f:
            json.dump(settings, f, indent=4)
        print(f"[Database] Saved settings.")
        return True
    except Exception as e:
        print(f"[Database] Error saving settings: {e}")
        return False

def load_settings():
    """
    Load game settings
    
    Returns:
    --------
    dict
        Game settings
    """
    default_settings = {
        "sound_enabled": True,
        "music_volume": 0.7,
        "sfx_volume": 0.8,
        "fullscreen": False,
        "server_address": "localhost",
        "server_port": 9999,
        "username": f"Player_{int(time.time() % 10000)}"
    }
    
    try:
        file_path = get_save_path(SETTINGS_FILE)
        if not os.path.exists(file_path):
            print("[Database] No settings found, using defaults.")
            return default_settings
            
        with open(file_path, "r") as f:
            settings = json.load(f)
            
        # Merge with defaults in case new settings were added
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
                
        print(f"[Database] Loaded settings.")
        return settings
    except Exception as e:
        print(f"[Database] Error loading settings: {e}")
        return default_settings

def save_game_state(manager):
    """
    Save the entire game state
    
    Parameters:
    -----------
    manager : CharacterManager
        Character manager with the game state
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        # Save creatures
        save_creatures(manager.creatures)
        
        # Save settings if needed
        # save_settings(manager.settings)
        
        print(f"[Database] Full game state saved.")
        return True
    except Exception as e:
        print(f"[Database] Error saving game state: {e}")
        return False

def auto_save(manager, auto_save_interval=30):
    """
    Auto-save the game state if interval has passed
    
    Parameters:
    -----------
    manager : CharacterManager
        Character manager with the game state
    auto_save_interval : int
        Interval in seconds between auto-saves
        
    Returns:
    --------
    bool
        True if saved, False otherwise
    """
    current_time = time.time()
    last_save_time = getattr(manager, 'last_save_time', 0)
    
    if current_time - last_save_time >= auto_save_interval:
        success = save_game_state(manager)
        if success:
            manager.last_save_time = current_time
        return success
    return False

class CharacterManager:
    """Manager class for creatures and game state"""
    
    def __init__(self):
        """Initialize the character manager"""
        self.creatures = []
        self.settings = load_settings()
        self.last_save_time = time.time()
        self.load_characters()
        
    def load_characters(self):
        """Load characters from save file"""
        self.creatures = load_creatures()
        
    def add_creature(self, creature):
        """
        Add a creature to the manager
        
        Parameters:
        -----------
        creature : Creature
            Creature to add
        """
        self.creatures.append(creature)
        save_creatures(self.creatures)
        print(f"[CharacterManager] Added {creature.creature_type} to manager.")
        
    def remove_creature(self, creature):
        """
        Remove a creature from the manager
        
        Parameters:
        -----------
        creature : Creature
            Creature to remove
        """
        if creature in self.creatures:
            self.creatures.remove(creature)
            save_creatures(self.creatures)
            print(f"[CharacterManager] Removed {creature.creature_type} from manager.")
        else:
            print(f"[CharacterManager] Creature not found in manager.")
            
    def get_creature(self, index):
        """
        Get a creature by index
        
        Parameters:
        -----------
        index : int
            Index of the creature to get
            
        Returns:
        --------
        Creature or None
            The creature at the specified index, or None if not found
        """
        if 0 <= index < len(self.creatures):
            return self.creatures[index]
        return None
        
    def get_all_creatures(self):
        """
        Get all creatures
        
        Returns:
        --------
        list
            List of all creatures
        """
        return self.creatures
        
    def get_living_creatures(self):
        """
        Get all living creatures
        
        Returns:
        --------
        list
            List of living creatures
        """
        return [c for c in self.creatures if c.is_alive]
        
    def get_dead_creatures(self):
        """
        Get all dead creatures
        
        Returns:
        --------
        list
            List of dead creatures
        """
        return [c for c in self.creatures if not c.is_alive]
        
    def get_tombstones(self):
        """
        Get all tombstones
        
        Returns:
        --------
        list
            List of tombstone records
        """
        return load_tombstones()
        
    def transfer_bonus_xp(self, tombstone_index, target_creature):
        """
        Transfer bonus XP from a tombstone to a creature
        
        Parameters:
        -----------
        tombstone_index : int
            Index of the tombstone to transfer from
        target_creature : Creature
            Creature to transfer XP to
            
        Returns:
        --------
        bool
            True if successful, False otherwise
        """
        return transfer_tombstone_xp(tombstone_index, target_creature)
        
    def save_all(self):
        """
        Save all data
        
        Returns:
        --------
        bool
            True if successful, False otherwise
        """
        return save_game_state(self)
        
    def auto_save(self, interval=30):
        """
        Auto-save if interval has passed
        
        Parameters:
        -----------
        interval : int
            Interval in seconds between auto-saves
            
        Returns:
        --------
        bool
            True if saved, False otherwise
        """
        return auto_save(self, interval)
        
    def update_all_creatures(self, dt):
        """
        Update all living creatures
        
        Parameters:
        -----------
        dt : int
            Time passed in milliseconds
        """
        for creature in self.get_living_creatures():
            creature.update_needs(dt)
            creature.update_age(dt)
