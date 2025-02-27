# personality_system.py
# Personality traits for creatures in Dark Tamagotchi

import random

# Define personality traits with their effects
PERSONALITY_TRAITS = {
    "Brave": {
        "description": "Fearless in the face of danger",
        "stat_effects": {"attack": 0.15, "defense": -0.05},
        "preferred_food": "meat",
        "evolution_bonus": "combat"
    },
    "Timid": {
        "description": "Cautious and avoids danger",
        "stat_effects": {"speed": 0.15, "attack": -0.05},
        "preferred_food": "vegetables",
        "evolution_bonus": "intelligence"
    },
    "Stubborn": {
        "description": "Resistant to change",
        "stat_effects": {"defense": 0.15, "speed": -0.05},
        "preferred_food": "bread",
        "evolution_bonus": "endurance"
    },
    "Curious": {
        "description": "Always exploring and learning",
        "stat_effects": {"speed": 0.1, "attack": 0.05},
        "preferred_food": "exotic fruits",
        "evolution_bonus": "exploration"
    },
    "Gentle": {
        "description": "Kind and caring",
        "stat_effects": {"max_hp": 0.15, "attack": -0.05},
        "preferred_food": "berries",
        "evolution_bonus": "healing"
    },
    "Aggressive": {
        "description": "Quick to fight",
        "stat_effects": {"attack": 0.2, "defense": -0.1},
        "preferred_food": "raw meat",
        "evolution_bonus": "combat"
    },
    "Playful": {
        "description": "Energetic and fun-loving",
        "stat_effects": {"speed": 0.1, "energy_max": 0.1},
        "preferred_food": "candy",
        "evolution_bonus": "agility"
    },
    "Lazy": {
        "description": "Conserves energy",
        "stat_effects": {"max_hp": 0.1, "energy_max": 0.1, "speed": -0.1},
        "preferred_food": "cooked meals",
        "evolution_bonus": "regeneration"
    },
    "Smart": {
        "description": "Intelligent and strategic",
        "stat_effects": {"attack": 0.05, "defense": 0.05, "speed": 0.05},
        "preferred_food": "special herbs",
        "evolution_bonus": "strategy"
    },
    "Loyal": {
        "description": "Devoted to their caretaker",
        "stat_effects": {"max_hp": 0.05, "attack": 0.05, "defense": 0.05},
        "preferred_food": "home-cooked meals",
        "evolution_bonus": "bond"
    }
}

# Define evolution bonuses
EVOLUTION_BONUSES = {
    "combat": {
        "description": "Enhanced combat abilities",
        "effect": lambda creature: setattr(creature, "attack", creature.attack * 1.2)
    },
    "intelligence": {
        "description": "Enhanced learning abilities",
        "effect": lambda creature: setattr(creature, "allowed_tier", min(3, creature.allowed_tier + 1))
    },
    "endurance": {
        "description": "Enhanced survival abilities",
        "effect": lambda creature: setattr(creature, "max_hp", int(creature.max_hp * 1.2))
    },
    "exploration": {
        "description": "Enhanced adventure abilities",
        "effect": lambda creature: setattr(creature, "speed", int(creature.speed * 1.2))
    },
    "healing": {
        "description": "Enhanced recovery abilities",
        "effect": lambda creature: add_heal_bonus(creature)
    },
    "agility": {
        "description": "Enhanced speed and energy",
        "effect": lambda creature: setattr(creature, "energy_max", int(creature.energy_max * 1.2))
    },
    "regeneration": {
        "description": "Enhanced regeneration abilities",
        "effect": lambda creature: add_regen_bonus(creature)
    },
    "strategy": {
        "description": "Enhanced ability effectiveness",
        "effect": lambda creature: enhance_abilities(creature)
    },
    "bond": {
        "description": "Enhanced overall growth",
        "effect": lambda creature: enhance_all_stats(creature)
    }
}

def add_heal_bonus(creature):
    """Add healing bonus to creature"""
    creature.healing_bonus = 1.2
    
def add_regen_bonus(creature):
    """Add regeneration bonus to creature"""
    creature.regeneration_bonus = 0.05  # 5% HP regen per turn
    
def enhance_abilities(creature):
    """Enhance creature's abilities"""
    for ability in creature.abilities:
        ability.damage = int(ability.damage * 1.1)
        
def enhance_all_stats(creature):
    """Enhance all creature stats slightly"""
    creature.attack = int(creature.attack * 1.1)
    creature.defense = int(creature.defense * 1.1)
    creature.speed = int(creature.speed * 1.1)
    creature.max_hp = int(creature.max_hp * 1.1)
    creature.energy_max = int(creature.energy_max * 1.1)

def generate_random_personality():
    """Generate a random personality with traits"""
    # Choose a primary trait
    primary_trait = random.choice(list(PERSONALITY_TRAITS.keys()))
    
    # Randomly choose a secondary trait that's different from primary
    secondary_traits = [t for t in PERSONALITY_TRAITS.keys() if t != primary_trait]
    secondary_trait = random.choice(secondary_traits) if random.random() < 0.5 else None
    
    return {
        "primary_trait": primary_trait,
        "secondary_trait": secondary_trait,
        "compatibility": random.randint(1, 10)  # For breeding compatibility
    }

def apply_personality_effects(creature, personality):
    """Apply personality effects to a creature's stats"""
    primary_trait = personality["primary_trait"]
    secondary_trait = personality["secondary_trait"]
    
    # Apply primary trait effects
    if primary_trait in PERSONALITY_TRAITS:
        trait_data = PERSONALITY_TRAITS[primary_trait]
        for stat, modifier in trait_data["stat_effects"].items():
            if hasattr(creature, stat):
                base_value = getattr(creature, stat)
                if isinstance(base_value, int):
                    # Integer stats (like HP, attack, etc.)
                    new_value = int(base_value * (1 + modifier))
                    setattr(creature, stat, new_value)
                elif isinstance(base_value, float):
                    # Float stats
                    new_value = base_value * (1 + modifier)
                    setattr(creature, stat, new_value)
    
    # Apply secondary trait effects (at half strength)
    if secondary_trait in PERSONALITY_TRAITS:
        trait_data = PERSONALITY_TRAITS[secondary_trait]
        for stat, modifier in trait_data["stat_effects"].items():
            if hasattr(creature, stat):
                base_value = getattr(creature, stat)
                if isinstance(base_value, int):
                    # Integer stats (like HP, attack, etc.)
                    new_value = int(base_value * (1 + modifier * 0.5))
                    setattr(creature, stat, new_value)
                elif isinstance(base_value, float):
                    # Float stats
                    new_value = base_value * (1 + modifier * 0.5)
                    setattr(creature, stat, new_value)

def get_preferred_food(personality):
    """Get preferred food based on personality"""
    primary_trait = personality["primary_trait"]
    if primary_trait in PERSONALITY_TRAITS:
        return PERSONALITY_TRAITS[primary_trait]["preferred_food"]
    return None

def apply_evolution_bonus(creature, personality):
    """Apply evolution bonus based on personality when evolving"""
    primary_trait = personality["primary_trait"]
    if primary_trait in PERSONALITY_TRAITS:
        bonus_type = PERSONALITY_TRAITS[primary_trait]["evolution_bonus"]
        if bonus_type in EVOLUTION_BONUSES:
            EVOLUTION_BONUSES[bonus_type]["effect"](creature)
            return EVOLUTION_BONUSES[bonus_type]["description"]
    return None

def get_personality_description(personality):
    """Get the description of a personality"""
    result = ""
    primary_trait = personality["primary_trait"]
    secondary_trait = personality["secondary_trait"]
    
    if primary_trait in PERSONALITY_TRAITS:
        result += f"Primarily {primary_trait}: {PERSONALITY_TRAITS[primary_trait]['description']}"
        
    if secondary_trait in PERSONALITY_TRAITS:
        result += f"\nSecondarily {secondary_trait}: {PERSONALITY_TRAITS[secondary_trait]['description']}"
        
    return result

def calculate_mood_impact(personality, action):
    """Calculate the impact of an action on mood based on personality"""
    primary_trait = personality["primary_trait"]
    
    # Default impact values
    impact = {
        "feed": 10,
        "sleep": 5,
        "play": 15,
        "battle": 0,
        "adventure": 5
    }
    
    # Modify impact based on personality trait
    if primary_trait == "Brave":
        impact["battle"] += 10
        impact["adventure"] += 5
    elif primary_trait == "Timid":
        impact["battle"] -= 5
        impact["sleep"] += 5
    elif primary_trait == "Stubborn":
        impact["feed"] -= 2
        impact["battle"] += 5
    elif primary_trait == "Curious":
        impact["adventure"] += 10
    elif primary_trait == "Gentle":
        impact["battle"] -= 10
        impact["play"] += 5
    elif primary_trait == "Aggressive":
        impact["battle"] += 15
        impact["sleep"] -= 5
    elif primary_trait == "Playful":
        impact["play"] += 10
        impact["sleep"] -= 3
    elif primary_trait == "Lazy":
        impact["adventure"] -= 5
        impact["sleep"] += 10
    elif primary_trait == "Smart":
        impact["adventure"] += 5
        impact["battle"] += 3
    elif primary_trait == "Loyal":
        impact["feed"] += 5
        impact["play"] += 5
        
    return impact.get(action, 0)

# Add this function to the Creature class in creatures.py
def add_personality_to_creature(creature):
    """Add a personality to a creature"""
    creature.personality = generate_random_personality()
    apply_personality_effects(creature, creature.personality)
    return creature.personality
