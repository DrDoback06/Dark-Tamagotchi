# items.py
# Items and inventory system for the Dark Tamagotchi game

import random
from tamagotchi.core.abilities import get_specific_ability, generate_random_ability

class Item:
    def __init__(self, name, item_type, effect, description, value=1, quantity=1):
        """
        Initialize an item
        
        Parameters:
        -----------
        name : str
            Name of the item
        item_type : str
            Type of item: "consumable", "equipment", "key", etc.
        effect : dict
            Effect of using the item (type-specific)
        description : str
            Description of the item
        value : int
            Value of the item (for trading/selling)
        quantity : int
            How many of this item
        """
        self.name = name
        self.item_type = item_type
        self.effect = effect
        self.description = description
        self.value = value
        self.quantity = quantity
        
    def use(self, target):
        """
        Use the item on a target
        
        Parameters:
        -----------
        target : Creature
            The creature to use the item on
            
        Returns:
        --------
        bool
            True if the item was used successfully, False otherwise
        """
        if self.quantity <= 0:
            print(f"[Item] Cannot use {self.name}: none remaining.")
            return False
            
        effect_type = self.effect.get("type", "")
        
        if effect_type == "heal":
            # Healing items restore HP
            heal_amount = self.effect.get("amount", 0)
            target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
            print(f"[Item] Used {self.name}: {target.creature_type} healed for {heal_amount} HP.")
            
        elif effect_type == "energy":
            # Energy items restore energy
            energy_amount = self.effect.get("amount", 0)
            target.energy = min(target.energy_max, target.energy + energy_amount)
            print(f"[Item] Used {self.name}: {target.creature_type}'s energy restored by {energy_amount}.")
            
        elif effect_type == "mood":
            # Mood items affect mood
            mood_amount = self.effect.get("amount", 0)
            target.mood = max(0, min(100, target.mood + mood_amount))
            print(f"[Item] Used {self.name}: {target.creature_type}'s mood changed by {mood_amount}.")
            
        elif effect_type == "hunger":
            # Food items reduce hunger
            hunger_amount = self.effect.get("amount", 0)
            target.hunger = max(0, target.hunger - hunger_amount)
            print(f"[Item] Used {self.name}: {target.creature_type}'s hunger reduced by {hunger_amount}.")
            
        elif effect_type == "skill":
            # Skill items teach new abilities
            from tamagotchi.core.abilities import Ability
            ability_data = self.effect.get("ability", None)
            if isinstance(ability_data, Ability):
                # If we already have an Ability object
                new_ability = ability_data
            else:
                # Create a new random ability
                new_ability = generate_random_ability(target.creature_type, target.level)
                
            # Add the new ability
            target.learn_ability(new_ability)
            print(f"[Item] Used {self.name}: {target.creature_type} learned {new_ability.name}!")
            
        elif effect_type == "stat_boost":
            # Permanent stat boosts
            stat = self.effect.get("stat", "")
            boost_amount = self.effect.get("amount", 0)
            
            if stat and hasattr(target, stat):
                current_value = getattr(target, stat)
                setattr(target, stat, current_value + boost_amount)
                print(f"[Item] Used {self.name}: {target.creature_type}'s {stat} increased by {boost_amount}!")
            else:
                print(f"[Item] Cannot apply {self.name}: invalid stat {stat}.")
                return False
                
        else:
            print(f"[Item] Unknown effect type: {effect_type}")
            return False
            
        # Item was used successfully
        self.quantity -= 1
        return True
        
    def to_dict(self):
        """Convert item to dictionary for saving"""
        return {
            "name": self.name,
            "item_type": self.item_type,
            "effect": self.effect,
            "description": self.description,
            "value": self.value,
            "quantity": self.quantity
        }
        
    def __str__(self):
        """String representation of the item"""
        return f"{self.name} (x{self.quantity}) - {self.description}"


def item_from_dict(data):
    """Create an item from a dictionary"""
    return Item(
        data["name"],
        data["item_type"],
        data["effect"],
        data["description"],
        data.get("value", 1),
        data.get("quantity", 1)
    )


# ===== PREDEFINED ITEMS =====

# Common consumable items
CONSUMABLE_ITEMS = {
    "small_health_potion": {
        "name": "Small Health Potion",
        "item_type": "consumable",
        "effect": {"type": "heal", "amount": 20},
        "description": "A small vial of red liquid that restores some health.",
        "value": 10
    },
    "medium_health_potion": {
        "name": "Medium Health Potion",
        "item_type": "consumable",
        "effect": {"type": "heal", "amount": 50},
        "description": "A medium-sized flask of red liquid that restores health.",
        "value": 25
    },
    "large_health_potion": {
        "name": "Large Health Potion",
        "item_type": "consumable",
        "effect": {"type": "heal", "amount": 100},
        "description": "A large bottle of red liquid that restores significant health.",
        "value": 50
    },
    "energy_drink": {
        "name": "Energy Drink",
        "item_type": "consumable",
        "effect": {"type": "energy", "amount": 30},
        "description": "A fizzy drink that restores some energy.",
        "value": 15
    },
    "energy_crystal": {
        "name": "Energy Crystal",
        "item_type": "consumable",
        "effect": {"type": "energy", "amount": 80},
        "description": "A glowing crystal that restores significant energy.",
        "value": 40
    },
    "bread": {
        "name": "Bread",
        "item_type": "consumable",
        "effect": {"type": "hunger", "amount": 20},
        "description": "A simple loaf of bread to reduce hunger.",
        "value": 5
    },
    "cooked_meat": {
        "name": "Cooked Meat",
        "item_type": "consumable",
        "effect": {"type": "hunger", "amount": 40},
        "description": "A juicy piece of cooked meat that significantly reduces hunger.",
        "value": 15
    },
    "favorite_treat": {
        "name": "Favorite Treat",
        "item_type": "consumable",
        "effect": {"type": "mood", "amount": 15},
        "description": "A special treat that improves your creature's mood.",
        "value": 20
    },
    "luxury_food": {
        "name": "Luxury Food",
        "item_type": "consumable",
        "effect": {"type": "mood", "amount": 25, "hunger": 30},
        "description": "Premium food that reduces hunger and greatly improves mood.",
        "value": 35
    }
}

# Stat boost items
STAT_BOOST_ITEMS = {
    "strength_essence": {
        "name": "Essence of Strength",
        "item_type": "consumable",
        "effect": {"type": "stat_boost", "stat": "attack", "amount": 2},
        "description": "Permanently increases attack power by 2.",
        "value": 100
    },
    "defense_essence": {
        "name": "Essence of Defense",
        "item_type": "consumable",
        "effect": {"type": "stat_boost", "stat": "defense", "amount": 2},
        "description": "Permanently increases defense by 2.",
        "value": 100
    },
    "vitality_essence": {
        "name": "Essence of Vitality",
        "item_type": "consumable",
        "effect": {"type": "stat_boost", "stat": "max_hp", "amount": 10},
        "description": "Permanently increases maximum HP by 10.",
        "value": 120
    },
    "speed_essence": {
        "name": "Essence of Speed",
        "item_type": "consumable",
        "effect": {"type": "stat_boost", "stat": "speed", "amount": 2},
        "description": "Permanently increases speed by 2.",
        "value": 100
    }
}

# Skill/ability items
SKILL_ITEMS = {
    "skill_scroll": {
        "name": "Skill Scroll",
        "item_type": "consumable",
        "effect": {"type": "skill", "ability": None},  # Ability will be generated when found
        "description": "A scroll containing instructions for a new ability.",
        "value": 75
    }
}

# Function to generate random items for adventures, etc.
def generate_random_item(rarity="common"):
    """
    Generate a random item based on rarity
    
    Parameters:
    -----------
    rarity : str
        Rarity level: "common", "uncommon", "rare"
        
    Returns:
    --------
    Item
        A new Item instance
    """
    # Set probabilities based on rarity
    if rarity == "common":
        item_pools = [
            (CONSUMABLE_ITEMS, 0.9),
            (STAT_BOOST_ITEMS, 0.05),
            (SKILL_ITEMS, 0.05)
        ]
    elif rarity == "uncommon":
        item_pools = [
            (CONSUMABLE_ITEMS, 0.6),
            (STAT_BOOST_ITEMS, 0.25),
            (SKILL_ITEMS, 0.15)
        ]
    elif rarity == "rare":
        item_pools = [
            (CONSUMABLE_ITEMS, 0.3),
            (STAT_BOOST_ITEMS, 0.4),
            (SKILL_ITEMS, 0.3)
        ]
    else:
        # Default to common
        item_pools = [
            (CONSUMABLE_ITEMS, 0.9),
            (STAT_BOOST_ITEMS, 0.05),
            (SKILL_ITEMS, 0.05)
        ]
        
    # Choose which item pool to use
    roll = random.random()
    cumulative_prob = 0
    chosen_pool = CONSUMABLE_ITEMS  # Default
    
    for pool, prob in item_pools:
        cumulative_prob += prob
        if roll <= cumulative_prob:
            chosen_pool = pool
            break
            
    # Select a random item from the chosen pool
    item_key = random.choice(list(chosen_pool.keys()))
    item_data = chosen_pool[item_key]
    
    # Create the item
    item = Item(
        item_data["name"],
        item_data["item_type"],
        item_data["effect"].copy(),  # Copy to avoid modifying the template
        item_data["description"],
        item_data.get("value", 1),
        1  # Default to quantity of 1
    )
    
    # Special case for skill scrolls - generate a random ability
    if item.name == "Skill Scroll":
        # The ability will be generated when used, based on the creature's type
        pass
        
    return item

# Specialized creature food generator
def generate_creature_food(creature_type):
    """Generate food specifically for a creature type"""
    
    # Define creature-specific foods
    type_foods = {
        "Skeleton": {
            "name": "Bone Marrow",
            "effect": {"type": "hunger", "amount": 50, "mood": 25},
            "description": "Rich bone marrow that skeletons find delicious.",
            "value": 25
        },
        "Fire Elemental": {
            "name": "Burning Coal",
            "effect": {"type": "hunger", "amount": 50, "mood": 25},
            "description": "A lump of burning coal, perfect for a fire elemental's diet.",
            "value": 25
        },
        "Knight": {
            "name": "Knight's Ration",
            "effect": {"type": "hunger", "amount": 50, "mood": 25},
            "description": "A proper, balanced meal fit for a noble knight.",
            "value": 25
        },
        "Goblin": {
            "name": "Shiny Trinket",
            "effect": {"type": "hunger", "amount": 40, "mood": 35},
            "description": "Goblins love shiny things, even if they're not edible.",
            "value": 30
        },
        "Troll": {
            "name": "Raw Meat",
            "effect": {"type": "hunger", "amount": 60, "mood": 20},
            "description": "A large chunk of raw meat, perfect for trolls.",
            "value": 20
        }
    }
    
    # Get the appropriate food or default to generic food
    food_data = type_foods.get(creature_type, {
        "name": "Generic Food",
        "effect": {"type": "hunger", "amount": 40},
        "description": "A bland but nutritious meal.",
        "value": 15
    })
    
    # Create the food item
    food = Item(
        food_data["name"],
        "consumable",
        food_data["effect"],
        food_data["description"],
        food_data.get("value", 15),
        1
    )
    
    return food
