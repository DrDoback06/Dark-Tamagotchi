# battle_system.py
# Battle system for Dark Tamagotchi

import random
from config import STUN_CHANCE, MAX_BATTLE_TURNS, XP_GAIN_PER_BATTLE, XP_LOSS_PERCENT

class Battle:
    def __init__(self, player_creature, enemy_creature):
        """
        Initialize a battle between two creatures
        
        Parameters:
        -----------
        player_creature : Creature
            The player's creature
        enemy_creature : Creature
            The enemy's creature
        """
        self.player = player_creature
        self.enemy = enemy_creature
        self.turn = "player"  # 'player' or 'enemy'
        self.battle_over = False
        self.winner = None
        self.turn_count = 0
        self.max_turns = MAX_BATTLE_TURNS
        self.log_messages = ["Battle started!"]
        
        # Store initial HP and energy for post-battle restoration
        self.player_initial_hp = player_creature.current_hp
        self.player_initial_energy = player_creature.energy
        self.enemy_initial_hp = enemy_creature.current_hp
        self.enemy_initial_energy = enemy_creature.energy
        
        # For multiplayer
        self.waiting_for_command = False
        self.player_role = "player"  # 'player' or 'opponent'
        
    def calculate_damage(self, attacker, defender, ability):
        """
        Calculate damage for an attack
        
        Parameters:
        -----------
        attacker : Creature
            The attacking creature
        defender : Creature
            The defending creature
        ability : Ability
            The ability being used
            
        Returns:
        --------
        int
            The calculated damage
        """
        # Get stats with active effects
        attack_power = attacker.get_stat_with_effects('attack')
        defense_value = defender.get_stat_with_effects('defense')
        
        # Base damage calculation
        raw_damage = ability.damage + attack_power - int(defense_value * 0.5)
        
        # Random factor (90%-110%)
        random_factor = random.uniform(0.9, 1.1)
        
        # Critical hit chance (5% chance, 1.5x damage)
        crit_chance = 0.05
        crit_multiplier = 1.0
        is_critical = random.random() < crit_chance
        if is_critical:
            crit_multiplier = 1.5
            self.log(f"Critical hit!")
            
        # Calculate final damage
        final_damage = max(1, int(raw_damage * random_factor * crit_multiplier))
        
        return final_damage
        
    def apply_attack(self, attacker, defender, ability_index):
        """
        Apply an attack using the specified ability
        
        Parameters:
        -----------
        attacker : Creature
            The attacking creature
        defender : Creature
            The defending creature
        ability_index : int
            Index of the ability to use
            
        Returns:
        --------
        bool
            True if the attack was applied successfully, False otherwise
        """
        # Validate ability index
        if ability_index < 0 or ability_index >= len(attacker.abilities):
            self.log(f"Invalid ability selection!")
            return False
            
        ability = attacker.abilities[ability_index]
        
        # Check if stunned
        if attacker.has_status_effect('stun'):
            self.log(f"{attacker.creature_type} is stunned and cannot act!")
            return True  # Attack attempt is consumed
            
        # Check ability requirements
        if ability.tier > getattr(attacker, 'allowed_tier', 1):
            self.log(f"Cannot use {ability.name}: tier {ability.tier} > allowed tier {attacker.allowed_tier}!")
            return False
            
        if ability.is_on_cooldown():
            self.log(f"{ability.name} is on cooldown for {ability.current_cooldown} more turns!")
            return False
            
        if attacker.energy < ability.energy_cost:
            self.log(f"Not enough energy to use {ability.name} (cost: {ability.energy_cost})!")
            return False
            
        # Deduct energy
        attacker.energy -= ability.energy_cost
        
        # Calculate and apply damage
        damage = self.calculate_damage(attacker, defender, ability)
        defender.current_hp -= damage
        
        # Log the attack
        self.log(f"{attacker.creature_type} used {ability.name} for {damage} damage!")
        
        # Apply additional effects if ability has them
        effect_applied = ability.apply_effect(attacker, defender, self)
        
        # Check for stun chance on damage abilities
        if ability.ability_type == "damage" and random.random() < STUN_CHANCE:
            stun_duration = 1
            defender.add_effect({
                'name': 'Stunned',
                'status': 'stun',
                'duration': stun_duration
            })
            self.log(f"{defender.creature_type} is stunned for {stun_duration} turn(s)!")
            
        # Start cooldown
        if ability.cooldown > 0:
            ability.start_cooldown()
            
        # Check if defender died
        if defender.current_hp <= 0:
            defender.current_hp = 0
            self.battle_over = True
            self.winner = "player" if defender == self.enemy else "enemy"
            
            winner_name = attacker.creature_type
            loser_name = defender.creature_type
            self.log(f"{winner_name} defeated {loser_name}!")
            
        return True
        
    def enemy_turn(self):
        """
        Execute the enemy's turn
        
        Returns:
        --------
        bool
            True if the enemy's turn was executed, False otherwise
        """
        if self.battle_over:
            return False
            
        # Update effects at the start of the turn
        self.enemy.update_effects()
        
        # Check if stunned
        if self.enemy.has_status_effect('stun'):
            self.log(f"{self.enemy.creature_type} is stunned and cannot act!")
            self.turn = "player"
            self.turn_count += 1
            self.check_turn_limit()
            return True
            
        # AI decision: choose the best ability to use
        best_ability_index = self.choose_enemy_ability()
        
        # If no valid ability was found
        if best_ability_index is None:
            self.log(f"{self.enemy.creature_type} has no usable abilities!")
            self.turn = "player"
            self.turn_count += 1
            self.check_turn_limit()
            return True
            
        # Apply the attack
        self.apply_attack(self.enemy, self.player, best_ability_index)
        
        # End turn if battle isn't over
        if not self.battle_over:
            self.turn = "player"
            self.turn_count += 1
            self.check_turn_limit()
            
        return True
        
    def player_turn(self, ability_index):
        """
        Execute the player's turn
        
        Parameters:
        -----------
        ability_index : int
            Index of the ability to use
            
        Returns:
        --------
        bool
            True if the player's turn was executed, False otherwise
        """
        if self.battle_over:
            return False
            
        # Update effects at the start of the turn
        self.player.update_effects()
        
        # Check if stunned
        if self.player.has_status_effect('stun'):
            self.log(f"{self.player.creature_type} is stunned and cannot act!")
            self.turn = "enemy"
            self.turn_count += 1
            self.check_turn_limit()
            return True
            
        # Apply the attack
        success = self.apply_attack(self.player, self.enemy, ability_index)
        
        # If attack was successful and battle isn't over, switch turn
        if success and not self.battle_over:
            self.turn = "enemy"
            self.turn_count += 1
            self.check_turn_limit()
            
        return success
        
    def choose_enemy_ability(self):
        """
        Choose the best ability for the enemy to use
        
        Returns:
        --------
        int or None
            Index of the chosen ability, or None if no valid ability is available
        """
        usable_abilities = []
        
        # Find abilities that can be used
        for i, ability in enumerate(self.enemy.abilities):
            if not ability.is_on_cooldown() and ability.energy_cost <= self.enemy.energy:
                usable_abilities.append((i, ability))
                
        if not usable_abilities:
            return None
            
        # Basic strategy logic
        if self.enemy.current_hp < self.enemy.max_hp * 0.3:
            # Low health: prioritize healing or high damage
            for i, ability in usable_abilities:
                if ability.ability_type == "heal":
                    return i
                    
            # If no healing, try to deal maximum damage
            return max(usable_abilities, key=lambda x: x[1].damage)[0]
        elif self.player.current_hp < self.player.max_hp * 0.2:
            # Player low health: prioritize damage to finish them
            damage_abilities = [(i, ability) for i, ability in usable_abilities 
                               if ability.ability_type == "damage"]
            if damage_abilities:
                return max(damage_abilities, key=lambda x: x[1].damage)[0]
        
        # Default: randomly choose an ability with weighted probabilities
        weights = []
        for _, ability in usable_abilities:
            if ability.ability_type == "damage":
                weights.append(3)  # Higher weight for damage
            elif ability.ability_type == "heal" and self.enemy.current_hp < self.enemy.max_hp * 0.7:
                weights.append(2)  # Moderate weight for healing when needed
            else:
                weights.append(1)  # Base weight for other abilities
                
        # Choose based on weights
        total = sum(weights)
        choice = random.uniform(0, total)
        current = 0
        
        for i, weight in enumerate(weights):
            current += weight
            if choice <= current:
                return usable_abilities[i][0]
                
        # Fallback: random choice
        return random.choice([i for i, _ in usable_abilities])
        
    def check_turn_limit(self):
        """Check if the maximum turn limit has been reached"""
        if self.turn_count >= self.max_turns:
            self.battle_over = True
            self.winner = None  # Draw
            self.log(f"Battle ended in a draw after {self.turn_count} turns!")
            
    def end_battle(self):
        """Handle end-of-battle effects and rewards"""
        # Award XP if the player won
        if self.winner == "player":
            # Base XP gain
            base_xp = XP_GAIN_PER_BATTLE
            
            # Level difference bonus/penalty
            level_diff = self.enemy.level - self.player.level
            level_modifier = 1.0 + (level_diff * 0.1)  # 10% per level difference
            
            # Health remaining bonus (up to 20%)
            health_ratio = self.player.current_hp / self.player.max_hp
            health_bonus = 1.0 + (health_ratio * 0.2)
            
            # Calculate final XP
            xp_gain = int(base_xp * level_modifier * health_bonus)
            
            # Award XP
            self.player.gain_xp(xp_gain)
            self.log(f"{self.player.creature_type} gained {xp_gain} XP!")
            
            # Award random item chance
            item_chance = 0.3  # 30% chance
            if random.random() < item_chance:
                from items import generate_random_item
                item = generate_random_item("common")
                self.player.add_item(item)
                self.log(f"Found {item.name}!")
                
        # XP loss if the player lost
        elif self.winner == "enemy":
            # Calculate XP loss
            xp_loss = int(self.player.xp * (XP_LOSS_PERCENT / 100.0))
            if xp_loss > 0:
                self.player.lose_xp(xp_loss)
                self.log(f"{self.player.creature_type} lost {xp_loss} XP.")
                
        # Restore some energy and a bit of health after battle
        energy_restore = self.player.energy_max * 0.3
        health_restore = self.player.max_hp * 0.1
        
        self.player.energy = min(self.player.energy_max, self.player.energy + energy_restore)
        self.player.current_hp = min(self.player.max_hp, self.player.current_hp + health_restore)
        
        self.log(f"Battle ended. Some energy and health restored.")
        return self.winner
        
    def get_battle_summary(self):
        """Get a summary of the battle results"""
        if not self.battle_over:
            return "Battle is still in progress."
            
        summary = {
            "winner": self.winner,
            "turns": self.turn_count,
            "player_hp_remaining": self.player.current_hp,
            "player_hp_percent": int((self.player.current_hp / self.player.max_hp) * 100),
            "enemy_hp_remaining": self.enemy.current_hp,
            "enemy_hp_percent": int((self.enemy.current_hp / self.enemy.max_hp) * 100)
        }
        
        if self.winner == "player":
            summary["outcome"] = f"{self.player.creature_type} defeated {self.enemy.creature_type}!"
            summary["xp_gain"] = int(XP_GAIN_PER_BATTLE * (1 + (self.enemy.level - self.player.level) * 0.1))
        elif self.winner == "enemy":
            summary["outcome"] = f"{self.player.creature_type} was defeated by {self.enemy.creature_type}."
            summary["xp_loss"] = int(self.player.xp * (XP_LOSS_PERCENT / 100.0))
        else:
            summary["outcome"] = "The battle ended in a draw."
            
        return summary
        
    def log(self, message):
        """Add a message to the battle log"""
        self.log_messages.append(message)
        print(f"[Battle] {message}")
        
    def get_log(self, last_n=None):
        """
        Get the battle log
        
        Parameters:
        -----------
        last_n : int, optional
            Number of most recent log messages to return
            
        Returns:
        --------
        list
            The log messages
        """
        if last_n is None:
            return self.log_messages
        return self.log_messages[-last_n:]

class MultiplayerBattle(Battle):
    """Extended Battle class for multiplayer battles"""
    
    def __init__(self, player_creature, opponent_creature, player_role="player1"):
        """
        Initialize a multiplayer battle
        
        Parameters:
        -----------
        player_creature : Creature
            The player's creature
        opponent_creature : Creature
            The opponent's creature
        player_role : str
            The player's role: 'player1' (goes first) or 'player2'
        """
        super().__init__(player_creature, opponent_creature)
        
        self.player_role = player_role
        self.current_turn_role = "player1"  # player1 always goes first
        
        # Set turn based on player role
        if player_role == "player1":
            self.turn = "player"
        else:
            self.turn = "enemy"
            
        self.waiting_for_command = self.turn == "enemy"
        
    def handle_opponent_action(self, action_data):
        """
        Handle an action from the opponent
        
        Parameters:
        -----------
        action_data : dict
            Data about the opponent's action
            
        Returns:
        --------
        bool
            True if the action was processed, False otherwise
        """
        if self.battle_over:
            return False
            
        # Verify it's the opponent's turn
        if (self.player_role == "player1" and self.current_turn_role != "player2") or \
           (self.player_role == "player2" and self.current_turn_role != "player1"):
            self.log("Received out-of-turn action from opponent!")
            return False
            
        # Process the action
        ability_index = action_data.get("ability_index", 0)
        
        if self.player_role == "player1":
            # If we're player1, opponent is "enemy"
            success = self.apply_attack(self.enemy, self.player, ability_index)
            if success:
                self.current_turn_role = "player1"
                self.turn = "player"
                self.waiting_for_command = False
        else:
            # If we're player2, opponent is "player"
            success = self.apply_attack(self.player, self.enemy, ability_index)
            if success:
                self.current_turn_role = "player2"
                self.turn = "player"
                self.waiting_for_command = False
                
        self.turn_count += 1
        self.check_turn_limit()
        return success
        
    def player_action(self, ability_index):
        """
        Process a player action in multiplayer
        
        Parameters:
        -----------
        ability_index : int
            Index of the ability to use
            
        Returns:
        --------
        dict
            Action data to send to the opponent
        """
        if self.battle_over or self.waiting_for_command:
            return None
            
        success = False
        
        # Process based on role
        if self.player_role == "player1":
            # player1 attacks with player creature
            success = self.apply_attack(self.player, self.enemy, ability_index)
            if success:
                self.current_turn_role = "player2"
                self.turn = "enemy"
                self.waiting_for_command = True
        else:
            # player2 attacks with enemy creature
            success = self.apply_attack(self.enemy, self.player, ability_index)
            if success:
                self.current_turn_role = "player1"
                self.turn = "enemy"
                self.waiting_for_command = True
                
        if success:
            self.turn_count += 1
            self.check_turn_limit()
            
            # Return action data to send to opponent
            return {
                "type": "BATTLE_ACTION",
                "ability_index": ability_index,
                "current_turn": self.current_turn_role
            }
            
        return None
