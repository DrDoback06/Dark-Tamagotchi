# ui/battle_screen.py
# Battle screen for Dark Tamagotchi

import pygame
import pygame.freetype
from ui.ui_base import Button, TextBox, ProgressBar, Tooltip
from tamagotchi.utils.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE
)

class BattleScreen:
    """Battle screen interface"""
    
    def __init__(self, screen, battle, on_exit_battle=None):
        """
        Initialize the battle screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        battle : Battle
            The battle instance
        on_exit_battle : function, optional
            Callback for exiting the battle
        """
        self.screen = screen
        self.battle = battle
        self.on_exit_battle = on_exit_battle
        
        # Initialize fonts
        pygame.freetype.init()
        self.font_large = pygame.freetype.SysFont('Arial', 32)
        self.font_medium = pygame.freetype.SysFont('Arial', 24)
        self.font_small = pygame.freetype.SysFont('Arial', 16)
        
        # Create background
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(BLACK)
        
        # Animation variables
        self.animation_time = 0
        self.anim_offset = 0
        self.attack_animation = None
        self.attack_anim_time = 0
        
        # Initialize UI components
        self.init_ui()
        
        # Create tooltip
        self.tooltip = Tooltip("")
        self.active_tooltip = None
        
    def init_ui(self):
        """Initialize UI components"""
        # Title
        self.title = TextBox(
            WINDOW_WIDTH // 2 - 100,
            20,
            200,
            40,
            "Battle",
            None,
            WHITE,
            32,
            "center",
            "middle"
        )
        
        # Battle log
        log_width = WINDOW_WIDTH - 200
        log_height = 100
        log_x = 100
        log_y = 70
        
        self.log_box = TextBox(
            log_x,
            log_y,
            log_width,
            log_height,
            "\n".join(self.battle.get_log(3)),
            DARK_GRAY,
            WHITE,
            16,
            "left",
            "top",
            True,
            True
        )
        
        # Player creature area (left)
        player_width = 300
        player_height = 350
        player_x = 50
        player_y = 200
        
        self.player_box = pygame.Rect(player_x, player_y, player_width, player_height)
        
        # Player creature info
        self.player_name = TextBox(
            player_x + player_width // 2,
            player_y + 10,
            0,
            30,
            self.battle.player.creature_type,
            None,
            WHITE,
            24,
            "center",
            "top"
        )
        
        self.player_level = TextBox(
            player_x + player_width // 2,
            player_y + 40,
            0,
            20,
            f"Level {self.battle.player.level}",
            None,
            GRAY,
            16,
            "center",
            "top"
        )
        
        # Player HP bar
        self.player_hp_bar = ProgressBar(
            player_x + 20,
            player_y + 70,
            player_width - 40,
            20,
            self.battle.player.current_hp,
            self.battle.player.max_hp,
            DARK_GRAY,
            GREEN,
            WHITE,
            True,
            "HP"
        )
        
        # Player Energy bar
        self.player_energy_bar = ProgressBar(
            player_x + 20,
            player_y + 100,
            player_width - 40,
            20,
            self.battle.player.energy,
            self.battle.player.energy_max,
            DARK_GRAY,
            BLUE,
            WHITE,
            True,
            "Energy"
        )
        
        # Enemy creature area (right)
        enemy_width = 300
        enemy_height = 350
        enemy_x = WINDOW_WIDTH - enemy_width - 50
        enemy_y = 200
        
        self.enemy_box = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
        
        # Enemy creature info
        self.enemy_name = TextBox(
            enemy_x + enemy_width // 2,
            enemy_y + 10,
            0,
            30,
            self.battle.enemy.creature_type,
            None,
            WHITE,
            24,
            "center",
            "top"
        )
        
        self.enemy_level = TextBox(
            enemy_x + enemy_width // 2,
            enemy_y + 40,
            0,
            20,
            f"Level {self.battle.enemy.level}",
            None,
            GRAY,
            16,
            "center",
            "top"
        )
        
        # Enemy HP bar
        self.enemy_hp_bar = ProgressBar(
            enemy_x + 20,
            enemy_y + 70,
            enemy_width - 40,
            20,
            self.battle.enemy.current_hp,
            self.battle.enemy.max_hp,
            DARK_GRAY,
            GREEN,
            WHITE,
            True,
            "HP"
        )
        
        # Ability buttons
        ability_width = 150
        ability_height = 50
        ability_spacing = 20
        ability_row1_y = WINDOW_HEIGHT - 140
        ability_row2_y = WINDOW_HEIGHT - 70
        
        self.ability_buttons = []
        
        # Calculate positions for a 2x2 grid of ability buttons
        positions = [
            (WINDOW_WIDTH // 2 - ability_width - ability_spacing // 2, ability_row1_y),
            (WINDOW_WIDTH // 2 + ability_spacing // 2, ability_row1_y),
            (WINDOW_WIDTH // 2 - ability_width - ability_spacing // 2, ability_row2_y),
            (WINDOW_WIDTH // 2 + ability_spacing // 2, ability_row2_y)
        ]
        
        # Create ability buttons
        for i, ability in enumerate(self.battle.player.abilities):
            if i < len(positions):
                button = Button(
                    positions[i][0],
                    positions[i][1],
                    ability_width,
                    ability_height,
                    ability.name,
                    lambda idx=i: self.on_ability_click(idx),
                    DARK_GRAY,
                    BLUE,
                    WHITE,
                    16,
                    f"{ability.description} - Damage: {ability.damage}, Energy: {ability.energy_cost}"
                )
                self.ability_buttons.append(button)
                
        # Exit button
        self.exit_button = Button(
            50,
            WINDOW_HEIGHT - 60,
            100,
            40,
            "Exit",
            self.on_exit_click,
            DARK_GRAY,
            RED,
            WHITE,
            16,
            "Exit the battle"
        )
        
        # Turn indicator
        self.turn_indicator = TextBox(
            WINDOW_WIDTH // 2,
            160,
            0,
            30,
            "Your Turn" if self.battle.turn == "player" else "Enemy Turn",
            None,
            YELLOW if self.battle.turn == "player" else GRAY,
            24,
            "center",
            "middle"
        )
        
    def on_ability_click(self, ability_index):
        """
        Handle ability button click
        
        Parameters:
        -----------
        ability_index : int
            Index of the ability
        """
        # Only process if it's player's turn
        if self.battle.turn != "player" or self.battle.battle_over:
            return
            
        # Try to use the ability
        success = self.battle.player_turn(ability_index)
        
        if success:
            # Play attack animation
            self.attack_animation = "player"
            self.attack_anim_time = 0
            
            # Update battle log
            self.log_box.set_text("\n".join(self.battle.get_log(3)))
            
            # Update turn indicator
            self.turn_indicator.set_text("Enemy Turn")
            self.turn_indicator.text_color = GRAY
            
    def on_exit_click(self):
        """Handle exit button click"""
        # End the battle and give any rewards/penalties
        if not self.battle.battle_over:
            self.battle.battle_over = True
            self.battle.winner = "enemy"  # Player forfeits
            
        self.battle.end_battle()
        
        if self.on_exit_battle:
            self.on_exit_battle()
            
    def handle_events(self, events):
        """
        Handle pygame events
        
        Parameters:
        -----------
        events : list
            List of pygame events
        """
        # Reset tooltip
        self.active_tooltip = None
        
        # Process events
        for event in events:
            # Check ability buttons
            for button in self.ability_buttons:
                if button.handle_event(event):
                    if button.hovered and button.tooltip:
                        self.active_tooltip = button.tooltip
                    break
            
            # Check exit button
            if self.exit_button.handle_event(event):
                if self.exit_button.hovered and self.exit_button.tooltip:
                    self.active_tooltip = self.exit_button.tooltip
                    
    def update(self, dt):
        """
        Update the battle screen
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        # Update animation
        self.animation_time += dt / 1000.0
        self.anim_offset = int(5 * pygame.math.sin(self.animation_time * 5))
        
        # Update attack animation
        if self.attack_animation:
            self.attack_anim_time += dt / 1000.0
            if self.attack_anim_time >= 0.5:  # Animation duration
                self.attack_animation = None
                
                # If it was enemy's turn, they attack after animation
                if self.battle.turn == "enemy" and not self.battle.battle_over:
                    self.battle.enemy_turn()
                    
                    # Play enemy attack animation
                    self.attack_animation = "enemy"
                    self.attack_anim_time = 0
                    
                    # Update battle log
                    self.log_box.set_text("\n".join(self.battle.get_log(3)))
                    
                    # Update turn indicator
                    self.turn_indicator.set_text("Your Turn" if self.battle.turn == "player" else "Enemy Turn")
                    self.turn_indicator.text_color = YELLOW if self.battle.turn == "player" else GRAY
                    
        # Update UI with current battle state
        self.update_ui()
        
        # Check if battle is over
        if self.battle.battle_over and self.battle.winner:
            # Display battle result
            result = "Victory!" if self.battle.winner == "player" else "Defeat!"
            self.turn_indicator.set_text(result)
            self.turn_indicator.text_color = GREEN if self.battle.winner == "player" else RED
            
    def update_ui(self):
        """Update UI components with current battle state"""
        # Update HP and energy bars
        self.player_hp_bar.set_value(self.battle.player.current_hp)
        self.player_energy_bar.set_value(self.battle.player.energy)
        self.enemy_hp_bar.set_value(self.battle.enemy.current_hp)
        
        # Enable/disable ability buttons based on energy and turn
        for i, button in enumerate(self.ability_buttons):
            if i < len(self.battle.player.abilities):
                ability = self.battle.player.abilities[i]
                can_use = (
                    self.battle.turn == "player" and
                    ability.energy_cost <= self.battle.player.energy and
                    not self.battle.battle_over and
                    not ability.is_on_cooldown()
                )
                button.enabled = can_use
                button.bg_color = BLUE if can_use else DARK_GRAY
        
    def draw(self):
        """Draw the battle screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        self.title.draw(self.screen)
        
        # Draw battle log
        self.log_box.draw(self.screen)
        
        # Draw turn indicator
        self.turn_indicator.draw(self.screen)
        
        # Draw player area
        offset = self.anim_offset if self.attack_animation != "player" else 0
        pygame.draw.rect(self.screen, DARK_GRAY, 
                         pygame.Rect(self.player_box.x, self.player_box.y + offset, 
                                    self.player_box.width, self.player_box.height),
                         border_radius=5)
        
        # Draw enemy area
        offset = self.anim_offset if self.attack_animation != "enemy" else 0
        pygame.draw.rect(self.screen, DARK_GRAY, 
                         pygame.Rect(self.enemy_box.x, self.enemy_box.y + offset, 
                                    self.enemy_box.width, self.enemy_box.height),
                         border_radius=5)
        
        # Draw player info
        self.player_name.draw(self.screen)
        self.player_level.draw(self.screen)
        self.player_hp_bar.draw(self.screen)
        self.player_energy_bar.draw(self.screen)
        
        # Draw enemy info
        self.enemy_name.draw(self.screen)
        self.enemy_level.draw(self.screen)
        self.enemy_hp_bar.draw(self.screen)
        
        # Draw placeholder creature icons
        player_icon_rect = pygame.Rect(
            self.player_box.x + 75,
            self.player_box.y + 150,
            150,
            150
        )
        pygame.draw.rect(self.screen, GRAY, player_icon_rect, border_radius=10)
        
        enemy_icon_rect = pygame.Rect(
            self.enemy_box.x + 75,
            self.enemy_box.y + 150,
            150,
            150
        )
        pygame.draw.rect(self.screen, GRAY, enemy_icon_rect, border_radius=10)
        
        # Draw ability buttons
        for button in self.ability_buttons:
            button.draw(self.screen)
            
        # Draw exit button
        self.exit_button.draw(self.screen)
        
        # Draw attack animation
        if self.attack_animation:
            self.draw_attack_animation()
            
        # Draw battle over message if applicable
        if self.battle.battle_over:
            self.draw_battle_over()
            
        # Draw tooltip if active
        if self.active_tooltip:
            self.tooltip.text = self.active_tooltip
            self.tooltip.show(pygame.mouse.get_pos())
            self.tooltip.draw(self.screen)
        else:
            self.tooltip.hide()
            
    def draw_attack_animation(self):
        """Draw attack animation"""
        # Simple animation - a line from attacker to target
        if self.attack_animation == "player":
            start_x = self.player_box.x + self.player_box.width // 2
            start_y = self.player_box.y + self.player_box.height // 2
            end_x = self.enemy_box.x + self.enemy_box.width // 2
            end_y = self.enemy_box.y + self.enemy_box.height // 2
        else:  # enemy attack
            start_x = self.enemy_box.x + self.enemy_box.width // 2
            start_y = self.enemy_box.y + self.enemy_box.height // 2
            end_x = self.player_box.x + self.player_box.width // 2
            end_y = self.player_box.y + self.player_box.height // 2
            
        # Calculate current position based on animation time
        progress = min(1.0, self.attack_anim_time / 0.5)
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress
        
        # Draw the projectile
        pygame.draw.circle(self.screen, YELLOW, (int(current_x), int(current_y)), 10)
        
    def draw_battle_over(self):
        """Draw battle over message and summary"""
        if not self.battle.battle_over:
            return
            
        # Get battle summary
        summary = self.battle.get_battle_summary()
        
        # Create overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw result box
        result_box = pygame.Rect(
            WINDOW_WIDTH // 2 - 200,
            WINDOW_HEIGHT // 2 - 150,
            400,
            300
        )
        pygame.draw.rect(self.screen, DARK_GRAY, result_box, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, result_box, width=2, border_radius=10)
        
        # Draw result title
        result_title = TextBox(
            WINDOW_WIDTH // 2,
            result_box.y + 20,
            0,
            40,
            "Victory!" if summary["winner"] == "player" else "Defeat!",
            None,
            GREEN if summary["winner"] == "player" else RED,
            32,
            "center",
            "top"
        )
        result_title.draw(self.screen)
        
        # Draw summary details
        summary_text = [
            f"Turns: {summary['turns']}",
            f"Your HP: {int(summary['player_hp_remaining'])}/{self.battle.player.max_hp} ({summary['player_hp_percent']}%)",
            f"Enemy HP: {int(summary['enemy_hp_remaining'])}/{self.battle.enemy.max_hp} ({summary['enemy_hp_percent']}%)"
        ]
        
        if summary["winner"] == "player":
            summary_text.append(f"XP Gained: {summary.get('xp_gain', 0)}")
        else:
            summary_text.append(f"XP Lost: {summary.get('xp_loss', 0)}")
            
        # Draw each line
        for i, line in enumerate(summary_text):
            text_box = TextBox(
                WINDOW_WIDTH // 2,
                result_box.y + 80 + i * 30,
                0,
                30,
                line,
                None,
                WHITE,
                20,
                "center",
                "top"
            )
            text_box.draw(self.screen)
            
        # Draw continue instruction
        continue_text = TextBox(
            WINDOW_WIDTH // 2,
            result_box.y + 250,
            0,
            30,
            "Click 'Exit' to continue",
            None,
            YELLOW,
            20,
            "center",
            "top"
        )
        continue_text.draw(self.screen)
