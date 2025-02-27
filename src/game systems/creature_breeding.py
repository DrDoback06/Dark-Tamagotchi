# breeding_system.py
# Creature breeding system for Dark Tamagotchi

import random
import time
from creatures import Creature
from personality_system import apply_personality_effects, generate_random_personality

class BreedingSystem:
    """
    Manages creature breeding and genetics
    
    This system handles breeding compatibility, gene inheritance,
    and offspring generation.
    """
    
    # Compatibility matrix (higher = more compatible)
    # Format: {creature_type: {compatible_type: compatibility_score}}
    COMPATIBILITY = {
        "Skeleton": {
            "Skeleton": 10,
            "Knight": 6,
            "Goblin": 4,
            "Troll": 4,
            "Fire Elemental": 2
        },
        "Knight": {
            "Knight": 10,
            "Skeleton": 6,
            "Goblin": 4,
            "Troll": 2,
            "Fire Elemental": 0
        },
        "Goblin": {
            "Goblin": 10,
            "Troll": 8,
            "Skeleton": 4,
            "Knight": 4,
            "Fire Elemental": 2
        },
        "Troll": {
            "Troll": 10,
            "Goblin": 8,
            "Skeleton": 4,
            "Knight": 2,
            "Fire Elemental": 0
        },
        "Fire Elemental": {
            "Fire Elemental": 10,
            "Skeleton": 2,
            "Goblin": 2,
            "Knight": 0,
            "Troll": 0
        }
    }
    
    # Hybrid types resulting from breeding different types
    HYBRID_TYPES = {
        ("Skeleton", "Knight"): "Undead Knight",
        ("Knight", "Skeleton"): "Undead Knight",
        
        ("Skeleton", "Goblin"): "Bone Thief",
        ("Goblin", "Skeleton"): "Bone Thief",
        
        ("Skeleton", "Troll"): "Skeletal Troll",
        ("Troll", "Skeleton"): "Skeletal Troll",
        
        ("Skeleton", "Fire Elemental"): "Ash Skeleton",
        ("Fire Elemental", "Skeleton"): "Ash Skeleton",
        
        ("Knight", "Goblin"): "Rogue Knight",
        ("Goblin", "Knight"): "Rogue Knight",
        
        ("Knight", "Troll"): "Armored Troll",
        ("Troll", "Knight"): "Armored Troll",
        
        ("Knight", "Fire Elemental"): "Flame Knight",
        ("Fire Elemental", "Knight"): "Flame Knight",
        
        ("Goblin", "Troll"): "Hobgoblin",
        ("Troll", "Goblin"): "Hobgoblin",
        
        ("Goblin", "Fire Elemental"): "Fire Imp",
        ("Fire Elemental", "Goblin"): "Fire Imp",
        
        ("Troll", "Fire Elemental"): "Lava Troll",
        ("Fire Elemental", "Troll"): "Lava Troll"
    }
    
    # Base stats for hybrid types
    HYBRID_BASE_STATS = {
        "Undead Knight": {
            "hp": 55, 
            "attack": 9, 
            "defense": 8, 
            "speed": 6, 
            "energy_max": 105,
            "ideal_mood": 60
        },
        "Bone Thief": {
            "hp": 48,
            "attack": 10,
            "defense": 5,
            "speed": 8,
            "energy_max": 90,
            "ideal_mood": 50
        },
        "Skeletal Troll": {
            "hp": 60,
            "attack": 9,
            "defense": 9,
            "speed": 5,
            "energy_max": 110,
            "ideal_mood": 35
        },
        "Ash Skeleton": {
            "hp": 45,
            "attack": 11,
            "defense": 4,
            "speed": 8,
            "energy_max": 95,
            "ideal_mood": 55
        },
        "Rogue Knight": {
            "hp": 52,
            "attack": 9,
            "defense": 8,
            "speed": 7,
            "energy_max": 95,
            "ideal_mood": 70
        },
        "Armored Troll": {
            "hp": 65,
            "attack": 8,
            "defense": 11,
            "speed": 4,
            "energy_max": 115,
            "ideal_mood": 55
        },
        "Flame Knight": {
            "hp": 50,
            "attack": 10,
            "defense": 7,
            "speed": 8,
            "energy_max": 100,
            "ideal_mood": 75
        },
        "Hobgoblin": {
            "hp": 55,
            "attack": 8,
            "defense": 9,
            "speed": 7,
            "energy_max": 100,
            "ideal_mood": 45
        },
        "Fire Imp": {
            "hp": 42,
            "attack": 11,
            "defense": 4,
            "speed": 10,
            "energy_max": 85,
            "ideal_mood": 65
        },
        "Lava Troll": {
            "hp": 60,
            "attack": 9,
            "defense": 8,
            "speed": 7,
            "energy_max": 105,
            "ideal_mood": 50
        }
    }
    
    def __init__(self):
        """Initialize the breeding system"""
        # Track breeding cooldowns
        self.breeding_cooldowns = {}  # {creature_id: cooldown_end_time}
        
        # Breeding records
        self.successful_breeds = 0
        self.total_offspring = 0
        
    def get_compatibility_score(self, creature1, creature2):
        """
        Calculate compatibility score between two creatures
        
        Parameters:
        -----------
        creature1, creature2 : Creature
            Creatures to check compatibility between
            
        Returns:
        --------
        int
            Compatibility score (0-10, higher = more compatible)
        """
        type1 = creature1.base_type
        type2 = creature2.base_type
        
        # Get base compatibility from matrix
        if type1 in self.COMPATIBILITY and type2 in self.COMPATIBILITY[type1]:
            base_score = self.COMPATIBILITY[type1][type2]
        else:
            base_score = 0
            
        # Same creature can't breed with itself
        if id(creature1) == id(creature2):
            return 0
            
        # Close relatives can't breed (TODO: implement lineage tracking)
        
        # Adjust based on personality compatibility (if system is enabled)
        personality_modifier = 0
        if hasattr(creature1, "personality") and hasattr(creature2, "personality"):
            # Personalities with higher compatibility scores are more compatible
            c1_compat = creature1.personality.get("compatibility", 5)
            c2_compat = creature2.personality.get("compatibility", 5)
            personality_modifier = (c1_compat + c2_compat) / 4  # Range: 0.5 to 5
            
        # Combine and clamp score
        final_score = base_score + personality_modifier
        return max(0, min(10, final_score))
        
    def check_breeding_compatibility(self, creature1, creature2):
        """
        Check if two creatures can breed
        
        Parameters:
        -----------
        creature1, creature2 : Creature
            Creatures to check compatibility between
            
        Returns:
        --------
        dict
            Compatibility information including score and any issues
        """
        result = {
            "compatible": False,
            "score": 0,
            "issues": []
        }
        
        # Check if creatures are alive
        if not creature1.is_alive or not creature2.is_alive:
            result["issues"].append("Both creatures must be alive to breed")
            return result
            
        # Check for breeding cooldown
        now = time.time()
        cooldown1 = self.breeding_cooldowns.get(id(creature1), 0)
        cooldown2 = self.breeding_cooldowns.get(id(creature2), 0)
        
        if now < cooldown1:
            result["issues"].append(f"{creature1.creature_type} is on breeding cooldown")
            
        if now < cooldown2:
            result["issues"].append(f"{creature2.creature_type} is on breeding cooldown")
            
        # Check minimum level
        min_level = 10
        if creature1.level < min_level:
            result["issues"].append(f"{creature1.creature_type} must be at least level {min_level}")
            
        if creature2.level < min_level:
            result["issues"].append(f"{creature2.creature_type} must be at least level {min_level}")
            
        # Calculate compatibility score
        score = self.get_compatibility_score(creature1, creature2)
        result["score"] = score
        
        # Determine if breeding is possible
        min_score = 2  # Minimum score required for breeding
        if score >= min_score and not result["issues"]:
            result["compatible"] = True
            
        return result
        
    def breed_creatures(self, creature1, creature2):
        """
        Attempt to breed two creatures
        
        Parameters:
        -----------
        creature1, creature2 : Creature
            Parent creatures
            
        Returns:
        --------
        dict
            Result with offspring if successful, or error information
        """
        # Check compatibility
        compatibility = self.check_breeding_compatibility(creature1, creature2)
        if not compatibility["compatible"]:
            return {
                "success": False,
                "message": "These creatures are not compatible for breeding",
                "issues": compatibility["issues"]
            }
            
        # Calculate success chance based on compatibility score
        success_chance = compatibility["score"] / 10.0
        
        # Attempt breeding
        if random.random() <= success_chance:
            # Generate offspring
            offspring = self.generate_offspring(creature1, creature2)
            
            # Apply breeding cooldown
            cooldown_hours = 12  # Base cooldown
            self.breeding_cooldowns[id(creature1)] = time.time() + (cooldown_hours * 3600)
            self.breeding_cooldowns[id(creature2)] = time.time() + (cooldown_hours * 3600)
            
            # Update breeding statistics
            self.successful_breeds += 1
            self.total_offspring += 1
            
            return {
                "success": True,
                "message": "Breeding successful!",
                "offspring": offspring
            }
        else:
            # Breeding failed
            # Apply shorter cooldown
            cooldown_hours = 4  # Shorter cooldown for failed attempt
            self.breeding_cooldowns[id(creature1)] = time.time() + (cooldown_hours * 3600)
            self.breeding_cooldowns[id(creature2)] = time.time() + (cooldown_hours * 3600)
            
            return {
                "success": False,
                "message": "Breeding attempt failed. Try again later."
            }
            
    def generate_offspring(self, parent1, parent2):
        """
        Generate an offspring from two parent creatures
        
        Parameters:
        -----------
        parent1, parent2 : Creature
            Parent creatures
            
        Returns:
        --------
        Creature
            Offspring creature
        """
        # Determine offspring type
        type1 = parent1.base_type
        type2 = parent2.base_type
        
        # Check for hybrid type
        if (type1, type2) in self.HYBRID_TYPES:
            offspring_type = self.HYBRID_TYPES[(type1, type2)]
        else:
            # Randomly choose one parent's type
            offspring_type = random.choice([type1, type2])
            
        # Create offspring with determined type
        if offspring_type in self.HYBRID_BASE_STATS:
            # Create a hybrid creature
            offspring = self.create_hybrid_creature(offspring_type)
        else:
            # Create a normal creature
            offspring = Creature(offspring_type)
            
        # Inherit stats from parents
        self.inherit_stats(offspring, parent1, parent2)
        
        # Inherit abilities
        self.inherit_abilities(offspring, parent1, parent2)
        
        # Generate personality with influence from parents
        self.inherit_personality(offspring, parent1, parent2)
        
        # Record lineage
        offspring.parent1_id = id(parent1)
        offspring.parent2_id = id(parent2)
        offspring.parent1_type = parent1.creature_type
        offspring.parent2_type = parent2.creature_type
        
        return offspring
        
    def create_hybrid_creature(self, hybrid_type):
        """
        Create a hybrid creature
        
        Parameters:
        -----------
        hybrid_type : str
            Type of hybrid to create
            
        Returns:
        --------
        Creature
            New hybrid creature
        """
        # Create base creature
        offspring = Creature()
        
        # Override type and stats
        offspring.creature_type = hybrid_type
        offspring.base_type = hybrid_type
        
        # Apply hybrid stats
        if hybrid_type in self.HYBRID_BASE_STATS:
            hybrid_stats = self.HYBRID_BASE_STATS[hybrid_type]
            offspring.max_hp = hybrid_stats["hp"]
            offspring.attack = hybrid_stats["attack"]
            offspring.defense = hybrid_stats["defense"]
            offspring.speed = hybrid_stats["speed"]
            offspring.energy_max = hybrid_stats["energy_max"]
            offspring.ideal_mood = hybrid_stats["ideal_mood"]
            
            # Reset current values
            offspring.current_hp = offspring.max_hp
            offspring.energy = offspring.energy_max
            offspring.mood = hybrid_stats["ideal_mood"]
            
        return offspring
        
    def inherit_stats(self, offspring, parent1, parent2):
        """
        Have offspring inherit stats from parents
        
        Parameters:
        -----------
        offspring : Creature
            Offspring creature
        parent1, parent2 : Creature
            Parent creatures
        """
        # For each stat, inherit from either one parent or a blend
        inheritance_method = random.choice(["dominant", "recessive", "blend"])
        
        if inheritance_method == "dominant":
            # One parent's stats are dominant
            dominant_parent = random.choice([parent1, parent2])
            
            # Inherit with slight variation
            variation = 0.1  # 10% variation
            
            offspring.max_hp = int(dominant_parent.max_hp * random.uniform(1 - variation, 1 + variation))
            offspring.attack = int(dominant_parent.attack * random.uniform(1 - variation, 1 + variation))
            offspring.defense = int(dominant_parent.defense * random.uniform(1 - variation, 1 + variation))
            offspring.speed = int(dominant_parent.speed * random.uniform(1 - variation, 1 + variation))
            offspring.energy_max = int(dominant_parent.energy_max * random.uniform(1 - variation, 1 + variation))
            
        elif inheritance_method == "recessive":
            # Each stat inherited from one parent or the other
            offspring.max_hp = int(random.choice([parent1.max_hp, parent2.max_hp]) * random.uniform(0.95, 1.05))
            offspring.attack = int(random.choice([parent1.attack, parent2.attack]) * random.uniform(0.95, 1.05))
            offspring.defense = int(random.choice([parent1.defense, parent2.defense]) * random.uniform(0.95, 1.05))
            offspring.speed = int(random.choice([parent1.speed, parent2.speed]) * random.uniform(0.95, 1.05))
            offspring.energy_max = int(random.choice([parent1.energy_max, parent2.energy_max]) * random.uniform(0.95, 1.05))
            
        else:  # "blend"
            # Average of parents' stats with slight boost chance
            boost = random.uniform(1.0, 1.15)  # Heterosis effect (hybrid vigor)
            
            offspring.max_hp = int(((parent1.max_hp + parent2.max_hp) / 2) * boost)
            offspring.attack = int(((parent1.attack + parent2.attack) / 2) * boost)
            offspring.defense = int(((parent1.defense + parent2.defense) / 2) * boost)
            offspring.speed = int(((parent1.speed + parent2.speed) / 2) * boost)
            offspring.energy_max = int(((parent1.energy_max + parent2.energy_max) / 2) * boost)
            
        # Ensure minimum values
        offspring.max_hp = max(10, offspring.max_hp)
        offspring.attack = max(1, offspring.attack)
        offspring.defense = max(1, offspring.defense)
        offspring.speed = max(1, offspring.speed)
        offspring.energy_max = max(50, offspring.energy_max)
        
        # Reset current values
        offspring.current_hp = offspring.max_hp
        offspring.energy = offspring.energy_max
        
        # Also inherit ideal mood (with variation)
        mood_variation = 10
        offspring.ideal_mood = max(0, min(100, (parent1.ideal_mood + parent2.ideal_mood) // 2 + 
                                        random.randint(-mood_variation, mood_variation)))
        offspring.mood = offspring.ideal_mood
        
    def inherit_abilities(self, offspring, parent1, parent2):
        """
        Have offspring inherit abilities from parents
        
        Parameters:
        -----------
        offspring : Creature
            Offspring creature
        parent1, parent2 : Creature
            Parent creatures
        """
        # Get all parent abilities
        all_abilities = []
        for ability in parent1.abilities:
            all_abilities.append(ability)
        for ability in parent2.abilities:
            if not any(a.name == ability.name for a in all_abilities):
                all_abilities.append(ability)
                
        # Random chance to inherit abilities from parents
        from abilities import generate_starting_abilities, generate_random_ability
        
        # Start with type-specific abilities
        offspring.abilities = generate_starting_abilities(offspring.creature_type)
        
        # Add 0-2 random parent abilities
        parent_abilities = random.sample(all_abilities, min(2, len(all_abilities)))
        for ability in parent_abilities:
            # Small chance for ability enhancement
            if random.random() < 0.2:  # 20% chance
                # Enhanced version of parent ability
                enhanced_ability = ability.__class__(
                    ability.name + " Plus",
                    int(ability.base_damage * 1.2),
                    ability.ability_type,
                    ability.tier,
                    ability.min_level,
                    ability.energy_cost,
                    ability.effect_value * 1.2 if ability.effect_value > 0 else ability.effect_value,
                    ability.duration,
                    ability.cooldown,
                    ability.description + " (Enhanced)"
                )
                offspring.abilities.append(enhanced_ability)
            else:
                # Clone parent ability
                offspring.abilities.append(ability)
                
        # Ensure we don't have duplicates or too many abilities
        unique_abilities = []
        for ability in offspring.abilities:
            if not any(a.name == ability.name for a in unique_abilities):
                unique_abilities.append(ability)
                
        # Limit to 4 abilities
        if len(unique_abilities) > 4:
            offspring.abilities = unique_abilities[:4]
        else:
            offspring.abilities = unique_abilities
            
    def inherit_personality(self, offspring, parent1, parent2):
        """
        Generate personality with influence from parents
        
        Parameters:
        -----------
        offspring : Creature
            Offspring creature
        parent1, parent2 : Creature
            Parent creatures
        """
        # Default to random personality if parents don't have personalities
        if not hasattr(parent1, "personality") or not hasattr(parent2, "personality"):
            offspring.personality = generate_random_personality()
            apply_personality_effects(offspring, offspring.personality)
            return
            
        # Get parent personalities
        p1_trait = parent1.personality.get("primary_trait", None)
        p2_trait = parent2.personality.get("primary_trait", None)
        
        # Offspring has a chance to inherit from either parent or get a random trait
        inheritance_roll = random.random()
        
        if inheritance_roll < 0.4:  # 40% chance to inherit from parent 1
            primary_trait = p1_trait
        elif inheritance_roll < 0.8:  # 40% chance to inherit from parent 2
            primary_trait = p2_trait
        else:  # 20% chance for random trait
            from personality_system import PERSONALITY_TRAITS
            primary_trait = random.choice(list(PERSONALITY_TRAITS.keys()))
            
        # Secondary trait has a chance to come from other parent
        secondary_trait = None
        if random.random() < 0.5:  # 50% chance for secondary trait
            parent2_trait = parent2.personality.get("primary_trait", None)
            if parent2_trait != primary_trait:
                secondary_trait = parent2_trait
                
        # Compatibility score is an average of parents with small variation
        p1_compat = parent1.personality.get("compatibility", 5)
        p2_compat = parent2.personality.get("compatibility", 5)
        compatibility = (p1_compat + p2_compat) // 2 + random.randint(-1, 1)
        compatibility = max(1, min(10, compatibility))
        
        # Create offspring personality
        offspring.personality = {
            "primary_trait": primary_trait,
            "secondary_trait": secondary_trait,
            "compatibility": compatibility
        }
        
        # Apply personality effects
        apply_personality_effects(offspring, offspring.personality)

# Singleton instance
_instance = None

def get_instance():
    """Get the global breeding system instance"""
    global _instance
    if _instance is None:
        _instance = BreedingSystem()
    return _instance

# Breeding screen
class BreedingScreen:
    """Screen for breeding creatures"""
    
    def __init__(self, screen, char_manager, on_back=None):
        """
        Initialize the breeding screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        char_manager : CharacterManager
            Character manager with available creatures
        on_back : function, optional
            Callback for back button
        """
        self.screen = screen
        self.char_manager = char_manager
        self.on_back = on_back
        self.breeding_system = get_instance()
        
        # Initialize fonts
        pygame.freetype.init()
        self.font_large = pygame.freetype.SysFont('Arial', 32)
        self.font_medium = pygame.freetype.SysFont('Arial', 24)
        self.font_small = pygame.freetype.SysFont('Arial', 16)
        
        # Create background
        self.background = pygame.Surface((screen.get_width(), screen.get_height()))
        self.background.fill((0, 0, 0))
        
        # Selection state
        self.selected_parent1 = None
        self.selected_parent2 = None
        self.available_creatures = []
        self.compatibility_result = None
        self.breeding_result = None
        
        # UI components
        self.parent1_buttons = []
        self.parent2_buttons = []
        self.breed_button = None
        self.back_button = None
        
        # Get available creatures
        self.available_creatures = [c for c in self.char_manager.get_living_creatures() 
                                   if c.level >= 10]
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Title
        self.title = TextBox(
            screen_width // 2,
            30,
            0,
            0,
            "Creature Breeding",
            None,
            (255, 255, 255),
            32,
            "center",
            "middle"
        )
        
        # Subtitle
        self.subtitle = TextBox(
            screen_width // 2,
            70,
            0,
            0,
            "Select two creatures to breed",
            None,
            (200, 200, 200),
            20,
            "center",
            "middle"
        )
        
        # Parent 1 section
        self.parent1_title = TextBox(
            screen_width // 4,
            100,
            0,
            0,
            "Parent 1",
            None,
            (255, 200, 100),
            24,
            "center",
            "middle"
        )
        
        # Parent 2 section
        self.parent2_title = TextBox(
            3 * screen_width // 4,
            100,
            0,
            0,
            "Parent 2",
            None,
            (255, 200, 100),
            24,
            "center",
            "middle"
        )
        
        # Create creature buttons for parent 1
        self.parent1_buttons = []
        y = 150
        for i, creature in enumerate(self.available_creatures):
            button = Button(
                screen_width // 4 - 100,
                y + i * 50,
                200,
                40,
                f"{creature.creature_type} (Lv.{creature.level})",
                lambda c=creature: self.select_parent1(c),
                (50, 50, 50),
                (100, 100, 200),
                (255, 255, 255),
                16
            )
            self.parent1_buttons.append(button)
            
        # Create creature buttons for parent 2
        self.parent2_buttons = []
        y = 150
        for i, creature in enumerate(self.available_creatures):
            button = Button(
                3 * screen_width // 4 - 100,
                y + i * 50,
                200,
                40,
                f"{creature.creature_type} (Lv.{creature.level})",
                lambda c=creature: self.select_parent2(c),
                (50, 50, 50),
                (100, 100, 200),
                (255, 255, 255),
                16
            )
            self.parent2_buttons.append(button)
            
        # Compatibility display
        self.compatibility_text = TextBox(
            screen_width // 2,
            350,
            0,
            0,
            "Select two parents to check compatibility",
            None,
            (200, 200, 200),
            18,
            "center",
            "middle"
        )
        
        # Breeding result display
        self.result_text = TextBox(
            screen_width // 2,
            400,
            300,
            100,
            "",
            (50, 50, 50),
            (255, 255, 255),
            18,
            "center",
            "middle",
            True,
            True
        )
        
        # Breed button
        self.breed_button = Button(
            screen_width // 2 - 60,
            screen_height - 160,
            120,
            50,
            "Breed",
            self.on_breed_click,
            (50, 50, 50),
            (100, 200, 100),
            (255, 255, 255),
            20
        )
        self.breed_button.enabled = False
        
        # Back button
        self.back_button = Button(
            screen_width // 2 - 50,
            screen_height - 80,
            100,
            40,
            "Back",
            self.on_back_click,
            (50, 50, 50),
            (200, 50, 50),
            (255, 255, 255),
            20
        )
        
    def select_parent1(self, creature):
        """
        Select the first parent
        
        Parameters:
        -----------
        creature : Creature
            Creature to select as parent 1
        """
        if self.selected_parent1 == creature:
            self.selected_parent1 = None
        else:
            self.selected_parent1 = creature
            
        # Update button colors
        for i, button in enumerate(self.parent1_buttons):
            if i < len(self.available_creatures) and self.available_creatures[i] == self.selected_parent1:
                button.bg_color = (100, 150, 100)
            else:
                button.bg_color = (50, 50, 50)
                
        # Update compatibility check
        self.update_compatibility()
        
    def select_parent2(self, creature):
        """
        Select the second parent
        
        Parameters:
        -----------
        creature : Creature
            Creature to select as parent 2
        """
        if self.selected_parent2 == creature:
            self.selected_parent2 = None
        else:
            self.selected_parent2 = creature
            
        # Update button colors
        for i, button in enumerate(self.parent2_buttons):
            if i < len(self.available_creatures) and self.available_creatures[i] == self.selected_parent2:
                button.bg_color = (100, 150, 100)
            else:
                button.bg_color = (50, 50, 50)
                
        # Update compatibility check
        self.update_compatibility()
        
    def update_compatibility(self):
        """Update compatibility check"""
        if self.selected_parent1 and self.selected_parent2:
            result = self.breeding_system.check_breeding_compatibility(
                self.selected_parent1,
                self.selected_parent2
            )
            self.compatibility_result = result
            
            # Update compatibility text
            compatibility_color = (255, 255, 255)
            if result["compatible"]:
                text = f"Compatibility: {result['score']:.1f}/10 - These creatures can breed!"
                compatibility_color = (100, 255, 100)
            else:
                text = f"Compatibility: {result['score']:.1f}/10 - Not compatible"
                for issue in result["issues"]:
                    text += f"\n• {issue}"
                compatibility_color = (255, 100, 100)
                
            self.compatibility_text.set_text(text)
            self.compatibility_text.text_color = compatibility_color
            
            # Enable/disable breed button
            self.breed_button.enabled = result["compatible"]
            if result["compatible"]:
                self.breed_button.bg_color = (100, 200, 100)
            else:
                self.breed_button.bg_color = (50, 50, 50)
                
        else:
            self.compatibility_result = None
            self.compatibility_text.set_text("Select two parents to check compatibility")
            self.compatibility_text.text_color = (200, 200, 200)
            self.breed_button.enabled = False
            self.breed_button.bg_color = (50, 50, 50)
            
    def on_breed_click(self):
        """Handle breed button click"""
        if not self.selected_parent1 or not self.selected_parent2 or not self.breed_button.enabled:
            return
            
        # Attempt breeding
        result = self.breeding_system.breed_creatures(self.selected_parent1, self.selected_parent2)
        self.breeding_result = result
        
        # Update result text
        if result["success"]:
            offspring = result["offspring"]
            
            # Add offspring to character manager
            self.char_manager.add_creature(offspring)
            
            # Display success message
            text = f"Breeding successful!\n\nNew creature: {offspring.creature_type} (Level 1)"
            text += f"\nHP: {offspring.max_hp}, Atk: {offspring.attack}, Def: {offspring.defense}, Spd: {offspring.speed}"
            
            if hasattr(offspring, "personality") and offspring.personality:
                text += f"\nPersonality: {offspring.personality['primary_trait']}"
                
            self.result_text.set_text(text)
            self.result_text.bg_color = (30, 70, 30)
            
        else:
            # Display failure message
            text = f"Breeding failed: {result['message']}"
            if "issues" in result:
                for issue in result["issues"]:
                    text += f"\n• {issue}"
                    
            self.result_text.set_text(text)
            self.result_text.bg_color = (70, 30, 30)
            
    def on_back_click(self):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
            
    def handle_events(self, events):
        """
        Handle pygame events
        
        Parameters:
        -----------
        events : list
            List of pygame events
        """
        for event in events:
            # Handle parent 1 buttons
            for button in self.parent1_buttons:
                button.handle_event(event)
                
            # Handle parent 2 buttons
            for button in self.parent2_buttons:
                button.handle_event(event)
                
            # Handle breed button
            self.breed_button.handle_event(event)
            
            # Handle back button
            self.back_button.handle_event(event)
            
    def update(self, dt):
        """
        Update the breeding screen
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        pass
        
    def draw(self):
        """Draw the breeding screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw titles
        self.title.draw(self.screen)
        self.subtitle.draw(self.screen)
        self.parent1_title.draw(self.screen)
        self.parent2_title.draw(self.screen)
        
        # Draw parent 1 buttons
        for button in self.parent1_buttons:
            button.draw(self.screen)
            
        # Draw parent 2 buttons
        for button in self.parent2_buttons:
            button.draw(self.screen)
            
        # Draw compatibility text
        self.compatibility_text.draw(self.screen)
        
        # Draw breeding result
        if self.breeding_result:
            self.result_text.draw(self.screen)
            
        # Draw breed button
        self.breed_button.draw(self.screen)
        
        # Draw back button
        self.back_button.draw(self.screen)
