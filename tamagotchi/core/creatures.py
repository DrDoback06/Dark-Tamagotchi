# creatures.py
# Creature class and related functionality for the Dark Tamagotchi game

import random
import time
from tamagotchi.utils.config import BASE_STATS, STAT_GROWTH, XP_MULTIPLIER, MAX_AGE, AGE_FACTOR_PER_WELLNESS
from tamagotchi.core.abilities import generate_starting_abilities, ability_to_dict, ability_from_dict

class Creature:
    def __init__(self, creature_type=None):
        """
        Initialize a new creature
        
        Parameters:
        -----------
        creature_type : str, optional
            Type of creature to create. If None, a random type will be chosen.
        """
        # Select random creature type if none provided
        all_types = list(BASE_STATS.keys())
        if creature_type is None or creature_type not in all_types:
            creature_type = random.choice(all_types)
            
        self.creature_type = creature_type
        self.base_type = creature_type  # Store original type for evolution paths
        
        # Initialize base stats with small random variations
        base = BASE_STATS[creature_type]
        self.max_hp = base["hp"] + random.randint(-5, 5)
        self.attack = base["attack"] + random.randint(-2, 2)
        self.defense = base["defense"] + random.randint(-2, 2)
        self.speed = base["speed"] + random.randint(-2, 2)
        self.energy_max = base["energy_max"] + random.randint(-5, 5)
        self.ideal_mood = base["ideal_mood"]
        
        # Current state
        self.current_hp = self.max_hp
        self.energy = self.energy_max
        self.hunger = 0  # 0-100, 0 is not hungry
        self.mood = self.ideal_mood  # 0-100, higher is better
        
        # Progression
        self.level = 1
        self.xp = 0
        self.evolution_stage = 1
        
        # Lifespan
        self.age = 0.0  # in seconds
        self.is_alive = True
        self.cause_of_death = None
        
        # Abilities
        self.abilities = generate_starting_abilities(creature_type)
        self.pending_skill = None  # New skill to be chosen after level up
        self.active_effects = []  # Effects currently affecting the creature
        
        # State flags
        self.is_sleeping = False
        self.feed_count = 0
        self.last_feed_time = time.time()
        self.allowed_tier = 1  # Maximum ability tier allowed (increases with level)
        
        # Inventory
        self.inventory = []

    # Rest of the Creature class implementation...
    # I'm keeping this shorter for brevity, but you need to include all the methods from the original file