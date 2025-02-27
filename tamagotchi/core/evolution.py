# evolution.py
# Evolution paths and system for the Dark Tamagotchi game

import random
from tamagotchi.utils.config import EVOLUTION_QUALITY, EVOLUTION_MULTIPLIER

# Evolution paths [creature_type][evolution_stage][quality]
# Quality: 0=Poor, 1=Good, 2=Best
EVOLUTION_PATHS = {
    "Skeleton": [
        # Stage 1 evolutions
        [
            {
                "type": "Brittle Skeleton",
                "description": "A weak skeleton with fragile bones.",
                "stat_boosts": {"max_hp": 1.1, "attack": 1.1, "defense": 0.9, "speed": 1.0},
                "ability_bonus": "bone_shard"
            },
            {
                "type": "Bone Warrior", 
                "description": "A skeleton trained in basic combat.",
                "stat_boosts": {"max_hp": 1.2, "attack": 1.2, "defense": 1.1, "speed": 1.1},
                "ability_bonus": "bone_shield"
            },
            {
                "type": "Death Knight",
                "description": "A powerful skeletal warrior infused with dark energy.",
                "stat_boosts": {"max_hp": 1.3, "attack": 1.3, "defense": 1.2, "speed": 1.2},
                "ability_bonus": "soul_drain"
            }
        ],
        # Stage 2 evolutions
        [
            {
                "type": "Bone Collector",
                "description": "A skeleton that collects bones from fallen foes.",
                "stat_boosts": {"max_hp": 1.1, "attack": 1.2, "defense": 1.0, "speed": 1.1},
                "ability_bonus": "bone_storm"
            },
            {
                "type": "Skeletal Champion",
                "description": "A skeleton that has mastered combat techniques.",
                "stat_boosts": {"max_hp": 1.2, "attack": 1.3, "defense": 1.2, "speed": 1.2},
                "ability_bonus": "death_grip"
            },
            {
                "type": "Lich Apprentice",
                "description": "A skeleton with budding necromantic powers.",
                "stat_boosts": {"max_hp": 1.3, "attack": 1.4, "defense": 1.3, "speed": 1.2},
                "ability_bonus": "life_drain"
            }
        ],
        # Further stages can be added here
    ],
    
    "Fire Elemental": [
        # Stage 1 evolutions
        [
            {
                "type": "Ember Spirit",
                "description": "A weak fire spirit barely clinging to this realm.",
                "stat_boosts": {"max_hp": 0.9, "attack": 1.2, "defense": 0.8, "speed": 1.2},
                "ability_bonus": "spark"
            },
            {
                "type": "Flame Keeper",
                "description": "A disciplined elemental maintaining its fiery form.",
                "stat_boosts": {"max_hp": 1.1, "attack": 1.3, "defense": 1.0, "speed": 1.3},
                "ability_bonus": "heat_wave"
            },
            {
                "type": "Inferno Core",
                "description": "A concentrated essence of pure flame and destruction.",
                "stat_boosts": {"max_hp": 1.2, "attack": 1.5, "defense": 1.1, "speed": 1.4},
                "ability_bonus": "fire_nova"
            }
        ],
        # Add more stages
    ],
    
    "Knight": [
        # Stage 1 evolutions
        [
            {
                "type": "Squire",
                "description": "A knight-in-training with basic combat skills.",
                "stat_boosts": {"max_hp": 1.2, "attack": 1.0, "defense": 1.2, "speed": 0.9},
                "ability_bonus": "shield_bash"
            },
            {
                "type": "Knight Captain",
                "description": "A skilled knight who leads others into battle.",
                "stat_boosts": {"max_hp": 1.3, "attack": 1.2, "defense": 1.3, "speed": 1.0},
                "ability_bonus": "rally"
            },
            {
                "type": "Holy Paladin",
                "description": "A knight blessed with divine power and protection.",
                "stat_boosts": {"max_hp": 1.4, "attack": 1.3, "defense": 1.4, "speed": 1.1},
                "ability_bonus": "divine_shield"
            }
        ],
        # Add more stages
    ],
    
    "Goblin": [
        # Stage 1 evolutions
        [
            {
                "type": "Goblin Scrapper",
                "description": "A scraggly goblin surviving on wits and desperation.",
                "stat_boosts": {"max_hp": 1.0, "attack": 1.1, "defense": 0.9, "speed": 1.2},
                "ability_bonus": "dirty_trick"
            },
            {
                "type": "Goblin Trickster",
                "description": "A cunning goblin known for clever tactics and traps.",
                "stat_boosts": {"max_hp": 1.1, "attack": 1.2, "defense": 1.0, "speed": 1.4},
                "ability_bonus": "smoke_bomb"
            },
            {
                "type": "Goblin Shaman",
                "description": "A goblin that has tapped into primal magic.",
                "stat_boosts": {"max_hp": 1.2, "attack": 1.3, "defense": 1.1, "speed": 1.5},
                "ability_bonus": "hex"
            }
        ],
        # Add more stages
    ],
    
    "Troll": [
        # Stage 1 evolutions
        [
            {
                "type": "Cave Troll",
                "description": "A brutish troll that lives in dark caves.",
                "stat_boosts": {"max_hp": 1.3, "attack": 1.1, "defense": 1.1, "speed": 0.8},
                "ability_bonus": "rock_throw"
            },
            {
                "type": "Battle Troll",
                "description": "A troll hardened by many conflicts and battles.",
                "stat_boosts": {"max_hp": 1.4, "attack": 1.2, "defense": 1.2, "speed": 0.9},
                "ability_bonus": "battle_roar"
            },
            {
                "type": "Ancient Troll",
                "description": "A massive troll with regenerative abilities and ancient wisdom.",
                "stat_boosts": {"max_hp": 1.5, "attack": 1.3, "defense": 1.3, "speed": 1.0},
                "ability_bonus": "regeneration"
            }
        ],
        # Add more stages
    ]
}

def get_evolution_quality(creature):
    """Determine the quality of evolution based on creature's stats"""
    wellness = creature.wellness
    mood_diff = abs(creature.mood - creature.ideal_mood)
    
    if wellness >= EVOLUTION_QUALITY["best"]["wellness_threshold"] and \
       mood_diff <= EVOLUTION_QUALITY["best"]["mood_diff_threshold"]:
        return 2  # Best evolution
    elif wellness >= EVOLUTION_QUALITY["good"]["wellness_threshold"] and \
         mood_diff <= EVOLUTION_QUALITY["good"]["mood_diff_threshold"]:
        return 1  # Good evolution
    else:
        return 0  # Poor evolution

def get_evolution_data(creature_type, evolution_stage, quality):
    """Get evolution data for a creature"""
    try:
        # Adjust for 0-based indexing
        stage_index = evolution_stage - 1
        if stage_index < 0:
            stage_index = 0
            
        # Make sure we don't go out of bounds
        if creature_type not in EVOLUTION_PATHS:
            return None
            
        stages = EVOLUTION_PATHS[creature_type]
        if stage_index >= len(stages):
            return None
            
        paths = stages[stage_index]
        if quality >= len(paths):
            quality = len(paths) - 1
            
        return paths[quality]
    except (KeyError, IndexError):
        return None

def apply_evolution(creature, evolution_data):
    """Apply evolution changes to a creature"""
    if not evolution_data:
        return False
        
    # Save old type for logging
    old_type = creature.creature_type
    
    # Update creature type
    creature.creature_type = evolution_data["type"]
    
    # Apply stat boosts
    for stat, multiplier in evolution_data["stat_boosts"].items():
        if hasattr(creature, stat):
            current_value = getattr(creature, stat)
            setattr(creature, stat, int(current_value * multiplier))
    
    # Handle ability bonus
    ability_bonus = evolution_data.get("ability_bonus")
    if ability_bonus:
        from tamagotchi.core.abilities import get_specific_ability
        new_ability = get_specific_ability(ability_bonus)
        if new_ability:
            creature.pending_skill = new_ability
    
    # Log the evolution
    print(f"[Evolution] {old_type} evolved into {creature.creature_type}!")
    print(f"[Evolution] {evolution_data['description']}")
    
    return True

def check_for_evolution(creature):
    """Check if a creature is ready to evolve and handle the evolution"""
    from tamagotchi.utils.config import EVOLUTION_THRESHOLDS
    
    # Check if ready for evolution
    if creature.evolution_stage >= len(EVOLUTION_THRESHOLDS):
        return False  # Already at max evolution
        
    if creature.level < EVOLUTION_THRESHOLDS[creature.evolution_stage - 1]:
        return False  # Not high enough level
    
    # Determine evolution quality
    quality = get_evolution_quality(creature)
    
    # Get evolution data
    evolution_data = get_evolution_data(
        creature.base_type,  # Use the original base type for evolution paths
        creature.evolution_stage,
        quality
    )
    
    # Apply evolution if possible
    if evolution_data:
        success = apply_evolution(creature, evolution_data)
        if success:
            creature.evolution_stage += 1
            return True
    
    return False
