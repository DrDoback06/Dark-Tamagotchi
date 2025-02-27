# creatures.py
# Creature class and related functionality for the Dark Tamagotchi game

import random
import time
from config import BASE_STATS, STAT_GROWTH, XP_MULTIPLIER, MAX_AGE, AGE_FACTOR_PER_WELLNESS
from abilities import generate_starting_abilities, ability_to_dict, ability_from_dict

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
        
    @property
    def wellness(self):
        """Calculate overall wellness (0-100)"""
        hp_ratio = self.current_hp / self.max_hp
        energy_ratio = self.energy / self.energy_max
        hunger_ratio = 1 - (self.hunger / 100.0)
        
        # Weight factors for overall wellness
        hp_weight = 0.4
        energy_weight = 0.3
        hunger_weight = 0.3
        
        overall = (hp_ratio * hp_weight + 
                   energy_ratio * energy_weight + 
                   hunger_ratio * hunger_weight) * 100
                   
        return max(0, min(100, int(overall)))
        
    def gain_xp(self, amount):
        """
        Add XP to the creature and handle level up if needed
        
        Parameters:
        -----------
        amount : int
            Amount of XP to add
        """
        self.xp += amount
        print(f"[XP] {self.creature_type} gained {amount} XP. Total: {self.xp}")
        
        # Check for level up
        xp_threshold = self.level * XP_MULTIPLIER
        if self.xp >= xp_threshold:
            self.level_up()
            
    def lose_xp(self, amount):
        """
        Remove XP from the creature and handle level down if needed
        
        Parameters:
        -----------
        amount : int
            Amount of XP to remove
        """
        self.xp -= amount
        print(f"[XP] {self.creature_type} lost {amount} XP.")
        
        # Check for level down
        while self.xp < 0 and self.level > 1:
            self.level -= 1
            self.xp += self.level * XP_MULTIPLIER
            print(f"[Level Down] {self.creature_type} dropped to Level {self.level}!")
            self.remove_high_level_abilities()
            
        # Ensure XP doesn't go below 0
        if self.xp < 0:
            self.xp = 0
            
    def level_up(self):
        """Handle level up: increase stats and offer new ability"""
        self.level += 1
        
        # Reset XP for the new level
        self.xp = 0
        
        # Increase stats randomly within ranges
        hp_inc = random.randint(*STAT_GROWTH["hp"])
        atk_inc = random.randint(*STAT_GROWTH["attack"])
        def_inc = random.randint(*STAT_GROWTH["defense"])
        spd_inc = random.randint(*STAT_GROWTH["speed"])
        energy_inc = random.randint(*STAT_GROWTH["energy_max"])
        
        self.max_hp += hp_inc
        self.attack += atk_inc
        self.defense += def_inc
        self.speed += spd_inc
        self.energy_max += energy_inc
        
        # Restore HP and energy on level up
        self.current_hp = self.max_hp
        self.energy = self.energy_max
        
        # Increase allowed ability tier every 10 levels
        if self.level % 10 == 0 and self.allowed_tier < 3:
            self.allowed_tier += 1
            print(f"[Level Up] {self.creature_type} can now use Tier {self.allowed_tier} abilities!")
            
        # Generate a pending skill to be chosen by the player
        from abilities import generate_random_ability
        self.pending_skill = generate_random_ability(self.creature_type, self.level)
        
        # Log the level up
        print(f"[Level Up] {self.creature_type} reached Level {self.level}!")
        print(f"  Stats: +HP:{hp_inc}, +Atk:{atk_inc}, +Def:{def_inc}, +Spd:{spd_inc}, +Energy:{energy_inc}")
        print(f"  New ability available: {self.pending_skill.name}")
        
        # Check for possible evolution
        from evolution import check_for_evolution
        check_for_evolution(self)
        
    def learn_ability(self, new_ability):
        """
        Learn a new ability
        
        Parameters:
        -----------
        new_ability : Ability
            The new ability to learn
            
        Returns:
        --------
        bool
            True if the ability was learned, False otherwise
        """
        # If we already have 4 abilities, one must be replaced
        if len(self.abilities) >= 4:
            # The UI will handle ability replacement
            # For now, just add it so it's visible in the list of options
            self.abilities.append(new_ability)
            return True
        else:
            self.abilities.append(new_ability)
            return True
            
    def replace_ability(self, old_index, new_index):
        """
        Replace an old ability with a new one
        
        Parameters:
        -----------
        old_index : int
            Index of the ability to replace
        new_index : int
            Index of the new ability (should be the last one if coming from pending_skill)
            
        Returns:
        --------
        bool
            True if successful, False otherwise
        """
        if old_index < 0 or old_index >= len(self.abilities) or \
           new_index < 0 or new_index >= len(self.abilities):
            return False
            
        # Log the replacement
        old_ability = self.abilities[old_index]
        new_ability = self.abilities[new_index]
        print(f"[Ability] {self.creature_type} replaced {old_ability.name} with {new_ability.name}")
        
        # If new_index is the last ability (from pending_skill)
        if new_index == len(self.abilities) - 1:
            # Replace the ability at old_index
            self.abilities[old_index] = new_ability
            # Remove the last ability (now duplicated)
            self.abilities.pop()
        else:
            # Direct swap
            self.abilities[old_index], self.abilities[new_index] = self.abilities[new_index], self.abilities[old_index]
            
        return True
        
    def remove_high_level_abilities(self):
        """Remove abilities that require a higher level than current"""
        filtered = []
        for ability in self.abilities:
            if ability.min_level > self.level:
                print(f"[Forget Ability] {self.creature_type} forgot {ability.name} due to level drop.")
            else:
                filtered.append(ability)
                
        self.abilities = filtered
        
    def add_effect(self, effect):
        """
        Add a temporary effect to the creature
        
        Parameters:
        -----------
        effect : dict
            Effect to add with keys like 'name', 'stat', 'multiplier', 'duration', etc.
        """
        self.active_effects.append(effect)
        effect_name = effect.get('name', 'Effect')
        print(f"[Effect] {self.creature_type} gained {effect_name} for {effect.get('duration', 1)} turns.")
        
    def update_effects(self):
        """Update active effects, reducing duration and removing expired ones"""
        active = []
        for effect in self.active_effects:
            effect['duration'] -= 1
            if effect['duration'] > 0:
                active.append(effect)
            else:
                print(f"[Effect] {effect.get('name', 'Effect')} has worn off from {self.creature_type}.")
                
        self.active_effects = active
        
    def has_status_effect(self, status_type):
        """
        Check if creature has a specific status effect
        
        Parameters:
        -----------
        status_type : str
            Type of status effect to check for
            
        Returns:
        --------
        bool
            True if the creature has the status effect, False otherwise
        """
        for effect in self.active_effects:
            if 'status' in effect and effect['status'] == status_type:
                return True
        return False
        
    def get_stat_with_effects(self, stat_name):
        """
        Get a stat value with all active effects applied
        
        Parameters:
        -----------
        stat_name : str
            Name of the stat to get
            
        Returns:
        --------
        int or float
            The modified stat value
        """
        if not hasattr(self, stat_name):
            return 0
            
        base_value = getattr(self, stat_name)
        multiplier = 1.0
        
        # Apply effects that modify this stat
        for effect in self.active_effects:
            if 'stat' in effect and effect['stat'] == stat_name and 'multiplier' in effect:
                multiplier *= effect['multiplier']
                
        return int(base_value * multiplier)
        
    def feed(self):
        """Feed the creature to reduce hunger"""
        current_time = time.time()
        
        # Reset feed count if enough time has passed
        from config import MAX_FEEDS_PER_HOUR
        if current_time - self.last_feed_time >= 3600:  # 1 hour
            self.feed_count = 0
            self.last_feed_time = current_time
            
        # Check if creature can be fed more
        if self.feed_count >= MAX_FEEDS_PER_HOUR:
            print(f"[Feed] {self.creature_type} cannot be fed more now. Try again later.")
            return False
            
        # Reduce hunger and update mood
        hunger_reduction = 40
        self.hunger = max(0, self.hunger - hunger_reduction)
        
        # Mood improvement depends on how close to ideal the creature is
        mood_improvement = 5
        if abs(self.hunger - 0) < 20:  # If hunger is low (which is good)
            mood_improvement += 5
            
        self.mood = min(100, self.mood + mood_improvement)
        
        # Update feed count
        self.feed_count += 1
        
        print(f"[Feed] {self.creature_type} fed. Hunger: {self.hunger}, Mood: {self.mood}")
        return True
        
    def sleep(self):
        """Put the creature to sleep"""
        if self.is_sleeping:
            print(f"[Sleep] {self.creature_type} is already sleeping.")
            return False
            
        self.is_sleeping = True
        print(f"[Sleep] {self.creature_type} is now sleeping.")
        return True
        
    def wake_up(self):
        """Wake the creature up"""
        if not self.is_sleeping:
            print(f"[Wake] {self.creature_type} is already awake.")
            return False
            
        self.is_sleeping = False
        print(f"[Wake] {self.creature_type} has woken up.")
        return True
        
    def update_needs(self, dt):
        """
        Update creature needs (hunger, energy, health) based on time
        
        Parameters:
        -----------
        dt : int
            Time passed in milliseconds
        """
        dt_sec = dt / 1000.0  # Convert to seconds
        
        # Update hunger
        from config import HUNGER_RATE
        hunger_increase = HUNGER_RATE * dt_sec / 60  # per minute
        self.hunger = min(100, self.hunger + hunger_increase)
        
        # Update energy
        from config import ENERGY_CONSUMPTION_RATE, ENERGY_RECOVERY_RATE
        if self.is_sleeping:
            # Energy recovery when sleeping
            energy_change = ENERGY_RECOVERY_RATE * dt_sec / 60
            self.energy = min(self.energy_max, self.energy + energy_change)
        else:
            # Energy consumption when awake
            energy_change = ENERGY_CONSUMPTION_RATE * dt_sec / 60
            self.energy = max(0, self.energy - energy_change)
            
        # Update health based on hunger
        from config import HUNGER_DAMAGE_THRESHOLD
        if self.hunger >= HUNGER_DAMAGE_THRESHOLD:
            # Creatures take damage when very hungry
            damage_factor = (self.hunger - HUNGER_DAMAGE_THRESHOLD) / (100 - HUNGER_DAMAGE_THRESHOLD)
            health_loss = self.max_hp * 0.05 * damage_factor * dt_sec / 60
            self.current_hp = max(0, self.current_hp - health_loss)
            
            if self.current_hp <= 0 and self.is_alive:
                self.die("hunger")
                
        # Natural health regeneration when hunger is low
        elif self.hunger < 30 and self.current_hp < self.max_hp:
            regen_amount = self.max_hp * 0.01 * dt_sec / 60
            self.current_hp = min(self.max_hp, self.current_hp + regen_amount)
            
        # Update mood based on how far from ideal conditions
        mood_change = 0
        
        # Hunger affects mood - being too hungry is bad
        if self.hunger > 70:
            mood_change -= 0.5 * dt_sec / 60
        elif self.hunger < 30:
            mood_change += 0.2 * dt_sec / 60
            
        # Energy affects mood - being too tired is bad
        energy_ratio = self.energy / self.energy_max
        if energy_ratio < 0.3:
            mood_change -= 0.5 * dt_sec / 60
        elif energy_ratio > 0.7:
            mood_change += 0.2 * dt_sec / 60
            
        # Apply mood change
        self.mood = max(0, min(100, self.mood + mood_change))
        
    def update_age(self, dt):
        """
        Update creature age and check for death by old age
        
        Parameters:
        -----------
        dt : int
            Time passed in milliseconds
        """
        if not self.is_alive:
            return
            
        dt_sec = dt / 1000.0  # Convert to milliseconds to seconds
        self.age += dt_sec
        
        # Calculate maximum lifespan based on wellness
        # Better wellness = longer lifespan
        wellness_factor = self.wellness / 100.0
        max_lifespan = MAX_AGE * (1 + wellness_factor * AGE_FACTOR_PER_WELLNESS)
        
        # Log remaining lifespan occasionally
        if int(self.age) % 60 == 0 and self.age > 1:
            remaining = max(0, max_lifespan - self.age)
            print(f"[Age] {self.creature_type} Age: {int(self.age)} sec. Remaining: ~{int(remaining)} sec.")
            
        # Check if creature has reached end of lifespan
        if self.age >= max_lifespan:
            self.die("old_age")
            
    def die(self, cause):
        """
        Handle creature death
        
        Parameters:
        -----------
        cause : str
            Cause of death
        """
        if not self.is_alive:
            return
            
        self.is_alive = False
        self.cause_of_death = cause
        
        # Calculate bonus XP for tombstone
        bonus_xp = int(self.level * 100 * (self.wellness / 100))
        
        print(f"[Death] {self.creature_type} has died due to {cause}.")
        print(f"[Death] {self.creature_type} was level {self.level} and lived for {int(self.age)} seconds.")
        print(f"[Death] Bonus XP available: {bonus_xp}")
        
        # Create tombstone record
        tombstone = {
            "creature_type": self.creature_type,
            "level": self.level,
            "age": self.age,
            "cause_of_death": cause,
            "bonus_xp": bonus_xp,
            "xp_transferred": False,
            "time_of_death": time.time()
        }
        
        # Save tombstone
        from database import save_tombstone
        save_tombstone(tombstone)
        
    def add_item(self, item):
        """
        Add an item to the creature's inventory
        
        Parameters:
        -----------
        item : Item
            Item to add
        """
        # Check if we already have this item
        for inv_item in self.inventory:
            if inv_item.name == item.name:
                # Stack items of the same type
                inv_item.quantity += item.quantity
                print(f"[Inventory] Added {item.quantity} {item.name}(s). Total: {inv_item.quantity}")
                return
                
        # Add new item
        self.inventory.append(item)
        print(f"[Inventory] New item added: {item.name} (x{item.quantity})")
        
    def use_item(self, item_name):
        """
        Use an item from inventory
        
        Parameters:
        -----------
        item_name : str
            Name of the item to use
            
        Returns:
        --------
        bool
            True if item was used successfully, False otherwise
        """
        # Find the item
        for item in self.inventory:
            if item.name == item_name and item.quantity > 0:
                # Use the item
                result = item.use(self)
                
                # Remove item if it was used up
                if item.quantity <= 0:
                    self.inventory.remove(item)
                    
                return result
                
        print(f"[Inventory] Item '{item_name}' not found or depleted.")
        return False
        
    def to_dict(self):
        """Convert creature to a dictionary for saving"""
        return {
            "creature_type": self.creature_type,
            "base_type": self.base_type,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "energy_max": self.energy_max,
            "ideal_mood": self.ideal_mood,
            "current_hp": self.current_hp,
            "energy": self.energy,
            "hunger": self.hunger,
            "mood": self.mood,
            "level": self.level,
            "xp": self.xp,
            "evolution_stage": self.evolution_stage,
            "age": self.age,
            "is_alive": self.is_alive,
            "cause_of_death": self.cause_of_death,
            "is_sleeping": self.is_sleeping,
            "feed_count": self.feed_count,
            "last_feed_time": self.last_feed_time,
            "allowed_tier": self.allowed_tier,
            "abilities": [ability_to_dict(a) for a in self.abilities],
            "pending_skill": ability_to_dict(self.pending_skill) if self.pending_skill else None,
            "inventory": [item.to_dict() for item in self.inventory]
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a creature from a dictionary"""
        creature = cls(data["creature_type"])
        
        # Restore base attributes
        creature.base_type = data.get("base_type", data["creature_type"])
        creature.max_hp = data["max_hp"]
        creature.attack = data["attack"]
        creature.defense = data["defense"]
        creature.speed = data["speed"]
        creature.energy_max = data.get("energy_max", 100)
        creature.ideal_mood = data.get("ideal_mood", 50)
        
        # Restore current state
        creature.current_hp = data["current_hp"]
        creature.energy = data.get("energy", creature.energy_max)
        creature.hunger = data.get("hunger", 0)
        creature.mood = data.get("mood", creature.ideal_mood)
        
        # Restore progression
        creature.level = data["level"]
        creature.xp = data["xp"]
        creature.evolution_stage = data["evolution_stage"]
        
        # Restore lifespan
        creature.age = data["age"]
        creature.is_alive = data["is_alive"]
        creature.cause_of_death = data.get("cause_of_death", None)
        
        # Restore state flags
        creature.is_sleeping = data.get("is_sleeping", False)
        creature.feed_count = data.get("feed_count", 0)
        creature.last_feed_time = data.get("last_feed_time", time.time())
        creature.allowed_tier = data.get("allowed_tier", 1)
        
        # Restore abilities
        creature.abilities = [ability_from_dict(a) for a in data["abilities"]]
        if data.get("pending_skill"):
            creature.pending_skill = ability_from_dict(data["pending_skill"])
        
        # Restore inventory
        from items import item_from_dict
        if "inventory" in data:
            creature.inventory = [item_from_dict(i) for i in data["inventory"]]
            
        return creature
        
    def __str__(self):
        """String representation of the creature"""
        # Format abilities string
        abilities_str = "\n  ".join(str(a) for a in self.abilities)
        
        # Format inventory string
        inventory_str = "\n  ".join(str(item) for item in self.inventory) if self.inventory else "Empty"
        
        return (
            f"=== {self.creature_type} (Level {self.level}) ===\n"
            f"Evolution Stage: {self.evolution_stage}\n"
            f"XP: {self.xp}/{self.level * XP_MULTIPLIER}\n"
            f"HP: {int(self.current_hp)}/{self.max_hp}\n"
            f"Stats: Atk {self.attack}, Def {self.defense}, Spd {self.speed}\n"
            f"Energy: {int(self.energy)}/{self.energy_max}\n"
            f"Hunger: {int(self.hunger)}/100 (0 is best)\n"
            f"Mood: {int(self.mood)}/100 (ideal: {self.ideal_mood})\n"
            f"Wellness: {self.wellness}%\n"
            f"Age: {int(self.age // 60)}m {int(self.age % 60)}s\n"
            f"Status: {'Sleeping' if self.is_sleeping else 'Awake'}\n"
            f"Abilities:\n  {abilities_str}\n"
            f"Inventory:\n  {inventory_str}\n"
        )
