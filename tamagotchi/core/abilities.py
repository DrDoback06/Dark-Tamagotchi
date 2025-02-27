# abilities.py
# Abilities and skills for the Dark Tamagotchi game

import random
from tamagotchi.utils.config import ABILITY_TIER_CHANCES

class Ability:
    def __init__(self, name, base_damage, ability_type, tier=1, min_level=1,
                 energy_cost=10, effect_value=0, duration=0, cooldown=0,
                 description=""):
        """
        Initialize an ability
        
        Parameters:
        -----------
        name : str
            Name of the ability
        base_damage : int
            Base damage for damage abilities
        ability_type : str
            Type of ability: "damage", "buff", "debuff", "heal", "drain", "status", etc.
        tier : int
            Tier of the ability (1-3)
        min_level : int
            Minimum creature level required to use this ability
        energy_cost : int
            Energy cost to use the ability
        effect_value : float
            Magnitude of the effect (e.g., 0.2 for +20%)
        duration : int
            Duration of effect in turns (0 means instant)
        cooldown : int
            Cooldown in turns before ability can be used again
        description : str
            Description of the ability
        """
        self.name = name
        self.base_damage = base_damage
        self.ability_type = ability_type
        self.tier = tier
        self.min_level = min_level
        self.energy_cost = energy_cost
        self.effect_value = effect_value
        self.duration = duration
        self.cooldown = cooldown
        self.description = description
        self.current_cooldown = 0
        self.damage = self.calculate_damage()
        
    def calculate_damage(self):
        """Calculate the actual damage based on tier"""
        multiplier = 1 + (self.tier - 1) * 0.3
        return int(self.base_damage * multiplier)
        
    def apply_effect(self, attacker, defender, battle):
        """
        Apply the ability's effect in battle
        
        Parameters:
        -----------
        attacker : Creature
            The creature using the ability
        defender : Creature
            The target of the ability
        battle : Battle
            The battle instance
        """
        effect_applied = False
        
        if self.ability_type == "damage":
            # Base damage is already applied in battle.apply_attack
            pass
            
        elif self.ability_type == "buff":
            # Add a positive effect to the attacker
            stat = "attack"  # Default stat to buff
            attacker.add_effect({
                "name": f"{self.name}",
                "stat": stat, 
                "multiplier": 1 + self.effect_value, 
                "duration": self.duration
            })
            battle.log(f"{attacker.creature_type}'s {stat} was increased!")
            effect_applied = True
            
        elif self.ability_type == "debuff":
            # Add a negative effect to the defender
            stat = "defense"  # Default stat to debuff
            defender.add_effect({
                "name": f"{self.name}",
                "stat": stat, 
                "multiplier": max(0.1, 1 - self.effect_value), 
                "duration": self.duration
            })
            battle.log(f"{defender.creature_type}'s {stat} was decreased!")
            effect_applied = True
            
        elif self.ability_type == "heal":
            # Heal the attacker
            heal_amount = int(attacker.max_hp * self.effect_value)
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal_amount)
            battle.log(f"{attacker.creature_type} healed for {heal_amount} HP!")
            effect_applied = True
            
        elif self.ability_type == "drain":
            # Damage the defender and heal the attacker
            drain_amount = int(self.damage * self.effect_value)
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + drain_amount)
            battle.log(f"{attacker.creature_type} drained {drain_amount} HP from {defender.creature_type}!")
            effect_applied = True
            
        elif self.ability_type == "status":
            # Apply a status effect like stun or poison
            status_type = "stun"  # Default status effect
            defender.add_effect({
                "name": f"{self.name}",
                "status": status_type, 
                "duration": self.duration
            })
            battle.log(f"{defender.creature_type} was {status_type}ned!")
            effect_applied = True
            
        elif self.ability_type == "aoe":
            # Area of effect damage (in multiplayer this would hit all enemies)
            # For now, just do extra damage to the defender
            aoe_damage = int(self.damage * self.effect_value)
            defender.current_hp = max(0, defender.current_hp - aoe_damage)
            battle.log(f"{self.name} dealt {aoe_damage} additional AoE damage!")
            effect_applied = True
            
        return effect_applied
        
    def start_cooldown(self):
        """Start the cooldown for this ability"""
        self.current_cooldown = self.cooldown
        
    def reduce_cooldown(self):
        """Reduce cooldown by 1 turn"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            
    def is_on_cooldown(self):
        """Check if ability is on cooldown"""
        return self.current_cooldown > 0
        
    def __str__(self):
        """String representation of the ability"""
        return f"{self.name} (Tier {self.tier}) - Damage: {self.damage}, Cost: {self.energy_cost} energy"

def ability_to_dict(ability):
    """Convert an ability to a dictionary for saving"""
    return {
        "name": ability.name,
        "base_damage": ability.base_damage,
        "ability_type": ability.ability_type,
        "tier": ability.tier,
        "min_level": ability.min_level,
        "energy_cost": ability.energy_cost,
        "effect_value": ability.effect_value,
        "duration": ability.duration,
        "cooldown": ability.cooldown,
        "description": ability.description,
        "current_cooldown": ability.current_cooldown
    }

def ability_from_dict(data):
    """Create an ability from a dictionary"""
    ability = Ability(
        data["name"],
        data["base_damage"],
        data["ability_type"],
        data.get("tier", 1),
        data.get("min_level", 1),
        data.get("energy_cost", 10),
        data.get("effect_value", 0),
        data.get("duration", 0),
        data.get("cooldown", 0),
        data.get("description", "")
    )
    ability.current_cooldown = data.get("current_cooldown", 0)
    return ability

# ===== ABILITY POOLS =====

# Abilities specific to each creature type
TYPE_ABILITY_POOLS = {
    "Skeleton": [
        {
            "name": "Bone Smash", 
            "base_damage": 12, 
            "ability_type": "damage", 
            "min_level": 1,
            "energy_cost": 10,
            "description": "Smashes the enemy with bone-crushing force."
        },
        {
            "name": "Haunting Howl", 
            "base_damage": 6, 
            "ability_type": "debuff", 
            "min_level": 1, 
            "effect_value": 0.2, 
            "duration": 2,
            "energy_cost": 12,
            "description": "A terrifying howl that weakens enemy defenses."
        },
        {
            "name": "Bone Shield", 
            "base_damage": 0, 
            "ability_type": "buff", 
            "min_level": 5, 
            "effect_value": 0.5, 
            "duration": 2,
            "energy_cost": 15,
            "description": "Creates a shield of bones that increases defense."
        },
        {
            "name": "Soul Drain", 
            "base_damage": 8, 
            "ability_type": "drain", 
            "min_level": 10, 
            "effect_value": 0.5,
            "energy_cost": 20,
            "description": "Drains life force from the enemy to heal yourself."
        }
    ],
    
    "Fire Elemental": [
        {
            "name": "Flame Burst", 
            "base_damage": 15, 
            "ability_type": "damage", 
            "min_level": 1,
            "energy_cost": 12,
            "description": "A sudden burst of intense flame."
        },
        {
            "name": "Scorch", 
            "base_damage": 8, 
            "ability_type": "debuff", 
            "min_level": 1, 
            "effect_value": 0.3, 
            "duration": 2,
            "energy_cost": 10,
            "description": "Burns the enemy, reducing their attack."
        },
        {
            "name": "Heat Wave", 
            "base_damage": 10, 
            "ability_type": "aoe", 
            "min_level": 5, 
            "effect_value": 0.7,
            "energy_cost": 18,
            "description": "A wave of heat that damages all enemies."
        },
        {
            "name": "Fire Nova", 
            "base_damage": 25, 
            "ability_type": "damage", 
            "min_level": 10,
            "energy_cost": 25,
            "cooldown": 3,
            "description": "A powerful explosion of fire energy."
        }
    ],
    
    "Knight": [
        {
            "name": "Sword Slash", 
            "base_damage": 13, 
            "ability_type": "damage", 
            "min_level": 1,
            "energy_cost": 8,
            "description": "A basic but effective sword attack."
        },
        {
            "name": "Shield Bash", 
            "base_damage": 7, 
            "ability_type": "status", 
            "min_level": 1, 
            "duration": 1,
            "energy_cost": 12,
            "description": "Bashes with a shield, potentially stunning the enemy."
        },
        {
            "name": "Rally", 
            "base_damage": 0, 
            "ability_type": "buff", 
            "min_level": 5, 
            "effect_value": 0.3, 
            "duration": 3,
            "energy_cost": 15,
            "description": "Raises morale, increasing attack power."
        },
        {
            "name": "Divine Protection", 
            "base_damage": 0, 
            "ability_type": "heal", 
            "min_level": 10, 
            "effect_value": 0.3,
            "energy_cost": 20,
            "description": "A divine blessing that heals wounds."
        }
    ],
    
    "Goblin": [
        {
            "name": "Sneak Attack", 
            "base_damage": 14, 
            "ability_type": "damage", 
            "min_level": 1,
            "energy_cost": 8,
            "description": "A surprise attack from the shadows."
        },
        {
            "name": "Panic", 
            "base_damage": 5, 
            "ability_type": "status", 
            "min_level": 1, 
            "duration": 1,
            "energy_cost": 10,
            "description": "Causes the enemy to panic, potentially missing their next turn."
        },
        {
            "name": "Smoke Bomb", 
            "base_damage": 6, 
            "ability_type": "debuff", 
            "min_level": 5, 
            "effect_value": 0.4, 
            "duration": 2,
            "energy_cost": 15,
            "description": "Throws a smoke bomb that reduces enemy accuracy."
        },
        {
            "name": "Dirty Trick", 
            "base_damage": 12, 
            "ability_type": "damage", 
            "min_level": 10, 
            "effect_value": 0.3,
            "energy_cost": 18,
            "description": "A cunning maneuver that deals damage and may debuff the enemy."
        }
    ],
    
    "Troll": [
        {
            "name": "Club Smash", 
            "base_damage": 16, 
            "ability_type": "damage", 
            "min_level": 1,
            "energy_cost": 15,
            "description": "A powerful but slow attack with a crude club."
        },
        {
            "name": "Roar", 
            "base_damage": 0, 
            "ability_type": "debuff", 
            "min_level": 1, 
            "effect_value": 0.2, 
            "duration": 2,
            "energy_cost": 10,
            "description": "A terrifying roar that intimidates enemies."
        },
        {
            "name": "Regeneration", 
            "base_damage": 0, 
            "ability_type": "heal", 
            "min_level": 5, 
            "effect_value": 0.2,
            "energy_cost": 20,
            "description": "Trolls can regenerate health over time."
        },
        {
            "name": "Battle Frenzy", 
            "base_damage": 10, 
            "ability_type": "buff", 
            "min_level": 10, 
            "effect_value": 0.5, 
            "duration": 2,
            "energy_cost": 25,
            "description": "Enters a frenzied state with increased attack power."
        }
    ]
}

# Abilities available to all creature types
COMMON_ABILITY_POOL = [
    {
        "name": "Quick Strike", 
        "base_damage": 10, 
        "ability_type": "damage", 
        "min_level": 1,
        "energy_cost": 5,
        "description": "A fast attack that does moderate damage."
    },
    {
        "name": "Focus", 
        "base_damage": 0, 
        "ability_type": "buff", 
        "min_level": 1, 
        "effect_value": 0.2, 
        "duration": 1,
        "energy_cost": 8,
        "description": "Increases focus to boost attack power."
    },
    {
        "name": "Dodge", 
        "base_damage": 0, 
        "ability_type": "buff", 
        "min_level": 5, 
        "effect_value": 0.3, 
        "duration": 1,
        "energy_cost": 10,
        "description": "Prepares to dodge the next attack, increasing defense."
    },
    {
        "name": "Rest", 
        "base_damage": 0, 
        "ability_type": "heal", 
        "min_level": 3, 
        "effect_value": 0.15,
        "energy_cost": 0,  # Free but skips turn
        "description": "Take a moment to recover some health."
    }
]

# Special abilities (typically gained through evolution)
SPECIAL_ABILITIES = {
    "bone_shard": {
        "name": "Bone Shard", 
        "base_damage": 18, 
        "ability_type": "damage", 
        "tier": 2, 
        "min_level": 1,
        "energy_cost": 15,
        "description": "Fires razor-sharp bone shards at the enemy."
    },
    "bone_shield": {
        "name": "Reinforced Bone Shield", 
        "base_damage": 0, 
        "ability_type": "buff", 
        "tier": 2, 
        "min_level": 1, 
        "effect_value": 0.7, 
        "duration": 2,
        "energy_cost": 20,
        "description": "Creates a powerful shield of reinforced bone."
    },
    "soul_drain": {
        "name": "Greater Soul Drain", 
        "base_damage": 15, 
        "ability_type": "drain", 
        "tier": 3, 
        "min_level": 1, 
        "effect_value": 0.8,
        "energy_cost": 25,
        "description": "Drains a significant amount of life force from the enemy."
    },
    "spark": {
        "name": "Ember Spark", 
        "base_damage": 12, 
        "ability_type": "damage", 
        "tier": 2, 
        "min_level": 1,
        "energy_cost": 10,
        "description": "Creates a spark that ignites the enemy."
    },
    "heat_wave": {
        "name": "Improved Heat Wave", 
        "base_damage": 18, 
        "ability_type": "aoe", 
        "tier": 2, 
        "min_level": 1, 
        "effect_value": 0.8,
        "energy_cost": 22,
        "description": "An enhanced wave of heat that damages all enemies."
    },
    "fire_nova": {
        "name": "Inferno Nova", 
        "base_damage": 35, 
        "ability_type": "damage", 
        "tier": 3, 
        "min_level": 1,
        "energy_cost": 30,
        "cooldown": 3,
        "description": "A massively powerful explosion of fiery energy."
    },
    # Add more special abilities for other creature types
}

def get_random_tier():
    """Get a random ability tier based on chances"""
    roll = random.random()
    cum_prob = 0
    for tier, prob in sorted(ABILITY_TIER_CHANCES.items()):
        cum_prob += prob
        if roll < cum_prob:
            return tier
    return 1  # Default to tier 1

def generate_random_ability(creature_type, level=1):
    """Generate a random ability for a given creature type and level"""
    # Combine type-specific and common pools
    specific_pool = TYPE_ABILITY_POOLS.get(creature_type, [])
    
    # Filter abilities by minimum level
    eligible_abilities = [a for a in specific_pool + COMMON_ABILITY_POOL if a["min_level"] <= level]
    
    if not eligible_abilities:
        # Fallback if no abilities match the level
        eligible_abilities = COMMON_ABILITY_POOL
    
    # Select a random ability
    ability_data = random.choice(eligible_abilities)
    
    # Determine tier (higher level creatures can get higher tier abilities)
    max_possible_tier = min(3, 1 + level // 10)  # Every 10 levels allows a higher tier
    tier = min(get_random_tier(), max_possible_tier)
    
    # Create and return the ability
    ability = Ability(
        ability_data["name"],
        ability_data["base_damage"],
        ability_data["ability_type"],
        tier,
        ability_data.get("min_level", 1),
        ability_data.get("energy_cost", 10),
        ability_data.get("effect_value", 0),
        ability_data.get("duration", 0),
        ability_data.get("cooldown", 0),
        ability_data.get("description", "")
    )
    
    return ability

def get_specific_ability(ability_key):
    """Get a specific ability by its key from SPECIAL_ABILITIES"""
    if ability_key in SPECIAL_ABILITIES:
        ability_data = SPECIAL_ABILITIES[ability_key]
        return Ability(
            ability_data["name"],
            ability_data["base_damage"],
            ability_data["ability_type"],
            ability_data.get("tier", 2),
            ability_data.get("min_level", 1),
            ability_data.get("energy_cost", 15),
            ability_data.get("effect_value", 0),
            ability_data.get("duration", 0),
            ability_data.get("cooldown", 0),
            ability_data.get("description", "")
        )
    return None

def generate_starting_abilities(creature_type):
    """Generate 4 starting abilities for a new creature"""
    abilities = []
    
    # Always give one type-specific attack ability
    specific_attacks = [a for a in TYPE_ABILITY_POOLS.get(creature_type, []) 
                         if a["ability_type"] == "damage" and a["min_level"] == 1]
    if specific_attacks:
        ability_data = random.choice(specific_attacks)
        abilities.append(Ability(
            ability_data["name"],
            ability_data["base_damage"],
            ability_data["ability_type"],
            1,  # Force tier 1 for starting abilities
            ability_data.get("min_level", 1),
            ability_data.get("energy_cost", 10),
            ability_data.get("effect_value", 0),
            ability_data.get("duration", 0),
            ability_data.get("cooldown", 0),
            ability_data.get("description", "")
        ))
    
    # Fill the rest with random abilities
    while len(abilities) < 4:
        ability = generate_random_ability(creature_type, 1)
        # Avoid duplicates
        if not any(a.name == ability.name for a in abilities):
            ability.tier = 1  # Force tier 1 for starting abilities
            abilities.append(ability)
    
    return abilities
