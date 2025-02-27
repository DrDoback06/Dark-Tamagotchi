# adventure_system.py
# Adventure mode functionality for Dark Tamagotchi

import random
import time
from config import (
    ADVENTURE_ENCOUNTER_CHANCE, 
    ADVENTURE_ITEM_CHANCE, 
    ADVENTURE_STEP_DISTANCE,
    ADVENTURE_COMPLETION_DISTANCE
)
from creatures import Creature
from items import generate_random_item
from battle_system import Battle

class Adventure:
    def __init__(self, player_creature):
        """
        Initialize an adventure
        
        Parameters:
        -----------
        player_creature : Creature
            The player's creature going on the adventure
        """
        self.player = player_creature
        self.distance = 0  # Current distance traveled
        self.max_distance = ADVENTURE_COMPLETION_DISTANCE
        self.events = []  # Log of adventure events
        self.encounters = []  # List of encounters encountered
        self.items_found = []  # List of items found
        self.is_complete = False
        self.is_active = True
        self.start_time = time.time()
        self.end_time = None
        
        # Special encounters that can happen during the adventure
        self.special_encounters = [
            "ancient_ruins",
            "mystical_spring",
            "abandoned_laboratory",
            "dark_cave",
            "enchanted_grove"
        ]
        
        # Progress flags for special encounters
        self.encountered_special = set()
        self.current_special_encounter = None
        
        # Initial log
        self.log(f"{player_creature.creature_type} started an adventure!")
        
    def update(self, dt):
        """
        Update the adventure progress
        
        Parameters:
        -----------
        dt : int
            Time passed in milliseconds
            
        Returns:
        --------
        dict or None
            Event data if an event occurred, None otherwise
        """
        if not self.is_active:
            return None
            
        # Convert dt to seconds
        dt_sec = dt / 1000.0
        
        # Calculate step size based on creature speed
        step_size = (self.player.speed / 10.0) * ADVENTURE_STEP_DISTANCE * dt_sec
        self.distance += step_size
        
        # Check for completion
        if self.distance >= self.max_distance:
            return self.complete_adventure()
            
        # Check for random events
        event = self.check_for_events(dt_sec)
        if event:
            return event
            
        return None
        
    def check_for_events(self, dt_sec):
        """
        Check for random events while adventuring
        
        Parameters:
        -----------
        dt_sec : float
            Time passed in seconds
            
        Returns:
        --------
        dict or None
            Event data if an event occurred, None otherwise
        """
        # Adjust probabilities based on time passed
        encounter_prob = ADVENTURE_ENCOUNTER_CHANCE * dt_sec
        item_prob = ADVENTURE_ITEM_CHANCE * dt_sec
        special_prob = 0.02 * dt_sec  # 2% chance per second for special encounters
        
        # Roll for events
        roll = random.random()
        
        if roll < encounter_prob:
            return self.generate_encounter()
        elif roll < (encounter_prob + item_prob):
            return self.generate_item()
        elif roll < (encounter_prob + item_prob + special_prob):
            return self.generate_special_encounter()
            
        return None
        
    def generate_encounter(self):
        """
        Generate a random creature encounter
        
        Returns:
        --------
        dict
            Encounter event data
        """
        # Create a wild creature
        wild_creature = Creature()
        
        # Scale wild creature level based on player level
        level_diff = random.randint(-2, 2)
        target_level = max(1, self.player.level + level_diff)
        
        # Level up the wild creature to match
        for _ in range(1, target_level):
            wild_creature.level_up()
            
        # Create encounter data
        encounter = {
            "type": "encounter",
            "creature": wild_creature,
            "message": f"Encountered a wild {wild_creature.creature_type} (Level {wild_creature.level})!"
        }
        
        # Add to log and encounters list
        self.log(encounter["message"])
        self.encounters.append(encounter)
        
        return encounter
        
    def generate_item(self):
        """
        Generate a random item find
        
        Returns:
        --------
        dict
            Item event data
        """
        # Determine item rarity based on adventure progress
        progress = self.distance / self.max_distance
        if progress > 0.8:
            rarity = "rare"
        elif progress > 0.5:
            rarity = "uncommon"
        else:
            rarity = "common"
            
        # Generate the item
        item = generate_random_item(rarity)
        
        # Create item data
        item_event = {
            "type": "item",
            "item": item,
            "message": f"Found a {item.name}!"
        }
        
        # Add to player's inventory
        self.player.add_item(item)
        
        # Add to log and items list
        self.log(item_event["message"])
        self.items_found.append(item)
        
        return item_event
        
    def generate_special_encounter(self):
        """
        Generate a special encounter
        
        Returns:
        --------
        dict
            Special encounter event data
        """
        # Only generate special encounters that haven't happened yet
        available = [enc for enc in self.special_encounters if enc not in self.encountered_special]
        
        # If all special encounters have happened, just generate a regular item or encounter
        if not available:
            if random.random() < 0.5:
                return self.generate_encounter()
            else:
                return self.generate_item()
                
        # Choose a random special encounter
        encounter_type = random.choice(available)
        self.encountered_special.add(encounter_type)
        self.current_special_encounter = encounter_type
        
        # Generate encounter data based on type
        encounter_data = self.get_special_encounter_data(encounter_type)
        
        # Add to log
        self.log(encounter_data["message"])
        
        return encounter_data
        
    def get_special_encounter_data(self, encounter_type):
        """
        Get data for a specific special encounter
        
        Parameters:
        -----------
        encounter_type : str
            Type of special encounter
            
        Returns:
        --------
        dict
            Special encounter data
        """
        if encounter_type == "ancient_ruins":
            return {
                "type": "special",
                "special_type": "ancient_ruins",
                "message": "You discovered ancient ruins! Exploring them might yield valuable rewards but could be dangerous.",
                "options": [
                    {"text": "Explore carefully", "result": "item_reward"},
                    {"text": "Search for treasure", "result": "encounter_reward"},
                    {"text": "Leave the ruins", "result": "nothing"}
                ]
            }
            
        elif encounter_type == "mystical_spring":
            return {
                "type": "special",
                "special_type": "mystical_spring",
                "message": "You found a mystical spring glowing with energy!",
                "options": [
                    {"text": "Drink from the spring", "result": "heal"},
                    {"text": "Bathe in the spring", "result": "stat_boost"},
                    {"text": "Collect spring water", "result": "item_spring"}
                ]
            }
            
        elif encounter_type == "abandoned_laboratory":
            return {
                "type": "special",
                "special_type": "abandoned_laboratory",
                "message": "You discovered an abandoned laboratory with strange equipment.",
                "options": [
                    {"text": "Examine the equipment", "result": "item_tech"},
                    {"text": "Try to activate the machinery", "result": "random"},
                    {"text": "Look for research notes", "result": "skill"}
                ]
            }
            
        elif encounter_type == "dark_cave":
            return {
                "type": "special",
                "special_type": "dark_cave",
                "message": "You found a dark cave with strange noises coming from inside.",
                "options": [
                    {"text": "Enter cautiously", "result": "encounter_hard"},
                    {"text": "Search near the entrance", "result": "item_simple"},
                    {"text": "Leave the cave", "result": "nothing"}
                ]
            }
            
        elif encounter_type == "enchanted_grove":
            return {
                "type": "special",
                "special_type": "enchanted_grove",
                "message": "You discovered an enchanted grove filled with magical flora.",
                "options": [
                    {"text": "Gather magical herbs", "result": "item_magic"},
                    {"text": "Meditate in the grove", "result": "energy_restore"},
                    {"text": "Explore deeper", "result": "random_reward"}
                ]
            }
            
        # Default case
        return {
            "type": "special",
            "special_type": "mystery",
            "message": "You encountered something mysterious!",
            "options": [
                {"text": "Investigate", "result": "random"},
                {"text": "Ignore and continue", "result": "nothing"}
            ]
        }
        
    def handle_special_encounter_choice(self, choice_index):
        """
        Handle player's choice in a special encounter
        
        Parameters:
        -----------
        choice_index : int
            Index of the chosen option
            
        Returns:
        --------
        dict
            Result of the choice
        """
        if not self.current_special_encounter:
            return {"message": "No active special encounter."}
            
        # Get encounter data
        encounter_data = self.get_special_encounter_data(self.current_special_encounter)
        
        # Validate choice
        if choice_index < 0 or choice_index >= len(encounter_data["options"]):
            return {"message": "Invalid choice."}
            
        # Get the result type
        result_type = encounter_data["options"][choice_index]["result"]
        
        # Process the result
        result = self.process_special_encounter_result(result_type)
        
        # Clear current encounter
        self.current_special_encounter = None
        
        return result
        
    def process_special_encounter_result(self, result_type):
        """
        Process the result of a special encounter choice
        
        Parameters:
        -----------
        result_type : str
            Type of result to process
            
        Returns:
        --------
        dict
            Result data
        """
        # Different rewards based on result type
        if result_type == "item_reward":
            # Find a good item
            item = generate_random_item("uncommon")
            self.player.add_item(item)
            self.items_found.append(item)
            
            return {
                "type": "reward",
                "message": f"You carefully explored and found a {item.name}!",
                "item": item
            }
            
        elif result_type == "encounter_reward":
            # Create a stronger creature with good rewards
            wild_creature = Creature()
            # Make it 2 levels higher than player
            target_level = self.player.level + 2
            for _ in range(1, target_level):
                wild_creature.level_up()
                
            return {
                "type": "encounter",
                "message": f"You found treasure, but it's guarded by a {wild_creature.creature_type}!",
                "creature": wild_creature,
                "bonus_reward": True
            }
            
        elif result_type == "nothing":
            return {
                "type": "message",
                "message": "You decide to move on without investigating further."
            }
            
        elif result_type == "heal":
            # Restore health
            heal_amount = self.player.max_hp * 0.5
            old_hp = self.player.current_hp
            self.player.current_hp = min(self.player.max_hp, self.player.current_hp + heal_amount)
            actual_heal = self.player.current_hp - old_hp
            
            return {
                "type": "heal",
                "message": f"The spring's water heals {self.player.creature_type} for {int(actual_heal)} HP!",
                "heal_amount": actual_heal
            }
            
        elif result_type == "stat_boost":
            # Random stat boost
            stats = ["attack", "defense", "speed", "max_hp"]
            stat = random.choice(stats)
            
            if stat == "max_hp":
                boost = random.randint(5, 10)
            else:
                boost = random.randint(1, 3)
                
            old_value = getattr(self.player, stat)
            setattr(self.player, stat, old_value + boost)
            
            # If HP was boosted, also increase current HP
            if stat == "max_hp":
                self.player.current_hp += boost
                
            return {
                "type": "stat_boost",
                "message": f"The spring's energy increases {self.player.creature_type}'s {stat} by {boost}!",
                "stat": stat,
                "amount": boost
            }
            
        elif result_type == "item_spring":
            # Special healing item
            from items import Item
            item = Item(
                "Mystical Spring Water",
                "consumable",
                {"type": "heal", "amount": 100},
                "Water from a mystical spring that greatly restores health.",
                value=50,
                quantity=1
            )
            self.player.add_item(item)
            
            return {
                "type": "reward",
                "message": "You collected some of the mystical spring water in a vial.",
                "item": item
            }
            
        # Add more result types here...
        
        elif result_type == "random":
            # Random outcome from several possibilities
            outcomes = ["item_reward", "encounter_reward", "heal", "stat_boost", "skill", "energy_restore"]
            return self.process_special_encounter_result(random.choice(outcomes))
            
        # Default case
        return {
            "type": "message",
            "message": "You made a choice, but nothing particularly interesting happened."
        }
        
    def complete_adventure(self):
        """
        Complete the adventure
        
        Returns:
        --------
        dict
            Completion event data
        """
        if self.is_complete:
            return None
            
        self.is_complete = True
        self.is_active = False
        self.end_time = time.time()
        
        # Calculate rewards based on adventure performance
        duration = self.end_time - self.start_time
        encounters_defeated = sum(1 for e in self.encounters if e.get("defeated", False))
        items_collected = len(self.items_found)
        
        # Base XP reward
        xp_reward = 100
        
        # Bonus for quick completion
        if duration < 300:  # 5 minutes
            xp_reward += 50
            
        # Bonus for encounters
        xp_reward += encounters_defeated * 20
        
        # Bonus for items
        xp_reward += items_collected * 10
        
        # Award XP
        self.player.gain_xp(xp_reward)
        
        # Create completion data
        completion_data = {
            "type": "completion",
            "message": f"Adventure complete! {self.player.creature_type} gained {xp_reward} XP!",
            "xp_reward": xp_reward,
            "duration": duration,
            "encounters": len(self.encounters),
            "items": len(self.items_found)
        }
        
        # Add to log
        self.log(completion_data["message"])
        
        return completion_data
        
    def log(self, message):
        """
        Add a message to the adventure log
        
        Parameters:
        -----------
        message : str
            Message to add to the log
        """
        self.events.append({
            "time": time.time(),
            "message": message
        })
        print(f"[Adventure] {message}")
        
    def get_progress(self):
        """
        Get the adventure progress
        
        Returns:
        --------
        float
            Progress percentage (0-100)
        """
        return (self.distance / self.max_distance) * 100

class MultiplayerAdventure(Adventure):
    """Extended Adventure class for multiplayer adventures"""
    
    def __init__(self, player_creature, party_id=None, is_host=True):
        """
        Initialize a multiplayer adventure
        
        Parameters:
        -----------
        player_creature : Creature
            The player's creature
        party_id : str, optional
            ID of the adventure party
        is_host : bool
            Whether this client is the host of the adventure
        """
        super().__init__(player_creature)
        
        self.party_id = party_id or f"party_{int(time.time())}"
        self.is_host = is_host
        self.party_members = [player_creature]
        self.waiting_for_sync = False
        
        # For multiplayer sync
        self.event_queue = []  # Events to send to other players
        self.received_events = []  # Events received from other players
        
    def add_party_member(self, creature):
        """
        Add a party member to the adventure
        
        Parameters:
        -----------
        creature : Creature
            Creature to add to the party
        """
        if len(self.party_members) < 4:  # Limit to 4 members
            self.party_members.append(creature)
            self.log(f"{creature.creature_type} joined the adventure party!")
            return True
        else:
            return False
            
    def remove_party_member(self, creature_id):
        """
        Remove a party member from the adventure
        
        Parameters:
        -----------
        creature_id : str
            ID of the creature to remove
        """
        for i, creature in enumerate(self.party_members):
            if id(creature) == creature_id:
                removed = self.party_members.pop(i)
                self.log(f"{removed.creature_type} left the adventure party.")
                return True
        return False
        
    def update(self, dt):
        """
        Update the multiplayer adventure
        
        Parameters:
        -----------
        dt : int
            Time passed in milliseconds
            
        Returns:
        --------
        dict or None
            Event data if an event occurred, None otherwise
        """
        # Only host updates adventure progress
        if not self.is_host or self.waiting_for_sync or not self.is_active:
            return None
            
        # Standard update
        event = super().update(dt)
        
        if event:
            # Add to event queue to sync with other players
            self.event_queue.append(event)
            self.waiting_for_sync = True
            
        return event
        
    def sync_event(self, event_data, from_player=None):
        """
        Sync an event with other players
        
        Parameters:
        -----------
        event_data : dict
            Event data to sync
        from_player : str, optional
            ID of the player who sent the event
            
        Returns:
        --------
        bool
            True if the event was synced, False otherwise
        """
        self.received_events.append({
            "data": event_data,
            "from": from_player,
            "time": time.time()
        })
        
        # Process the event
        event_type = event_data.get("type", "")
        
        if event_type == "encounter":
            # Store creature data for battle
            self.log(f"Party encountered a {event_data['creature'].creature_type}!")
            self.encounters.append(event_data)
            
        elif event_type == "item":
            # Add item to player's inventory
            if from_player != id(self.player):
                self.log(f"Party found a {event_data['item'].name}!")
                self.player.add_item(event_data["item"])
                
        elif event_type == "special":
            # Store special encounter data
            self.current_special_encounter = event_data["special_type"]
            self.log(event_data["message"])
            
        elif event_type == "completion":
            # Adventure complete
            self.is_complete = True
            self.is_active = False
            self.log("Adventure completed by the party!")
            
        # Clear waiting flag
        self.waiting_for_sync = False
        
        return True
        
    def get_sync_data(self):
        """
        Get data to sync with other players
        
        Returns:
        --------
        dict
            Sync data
        """
        return {
            "party_id": self.party_id,
            "distance": self.distance,
            "max_distance": self.max_distance,
            "is_complete": self.is_complete,
            "events": self.event_queue,
            "party_size": len(self.party_members)
        }
