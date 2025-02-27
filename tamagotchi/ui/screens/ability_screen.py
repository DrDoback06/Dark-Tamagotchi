# ui/ability_screen.py
# Ability management screen for Dark Tamagotchi

import pygame
import pygame.freetype
from tamagotchi.ui.ui_base import Button, TextBox, ScrollableList, Tooltip
from tamagotchi.utils.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE
)

class AbilityScreen:
    """Ability management screen"""
    
    def __init__(self, screen, creature, on_back=None):
        """
        Initialize the ability screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        creature : Creature
            The player's creature
        on_back : function, optional
            Callback for back button
        """
        self.screen = screen
        self.creature = creature
        self.on_back = on_back
        
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
        
        # Selected ability
        self.selected_ability = None
        self.selected_index = -1
        
        # New ability to learn (if any)
        self.new_ability = self.creature.pending_skill
        
        # Notification variables
        self.notifications = []
        self.notification_time = 3.0  # seconds
        
        # Initialize UI components
        self.init_ui()
        
        # Create tooltip
        self.tooltip = Tooltip("")
        self.active_tooltip = None
        
        # Learning mode for new ability
        self.learning_mode = self.new_ability is not None
        
    def init_ui(self):
        """Initialize UI components"""
        # Title
        self.title = TextBox(
            WINDOW_WIDTH // 2 - 100,
            20,
            200,
            40,
            "Abilities",
            None,
            WHITE,
            32,
            "center",
            "middle"
        )
        
        # Creature info
        info_width = 400
        info_height = 80
        info_x = WINDOW_WIDTH // 2 - info_width // 2
        info_y = 80
        
        self.info_box = pygame.Rect(info_x, info_y, info_width, info_height)
        
        self.creature_info = TextBox(
            info_x + 20,
            info_y + 10,
            info_width - 40,
            60,
            f"{self.creature.creature_type} (Level {self.creature.level})\n"
            f"Allowed Ability Tier: {self.creature.allowed_tier}",
            None,
            WHITE,
            16,
            "center",
            "middle"
        )
        
        # Ability list
        list_width = 300
        list_height = 350
        list_x = 50
        list_y = 180
        
        self.ability_list = ScrollableList(
            list_x,
            list_y,
            list_width,
            list_height,
            [ability.name for ability in self.creature.abilities],
            DARK_GRAY,
            40,
            BLUE,
            GRAY,
            WHITE,
            16,
            self.on_ability_select
        )
        
        # Ability details panel
        details_width = 400
        details_height = 350
        details_x = WINDOW_WIDTH - details_width - 50
        details_y = 180
        
        self.details_panel = pygame.Rect(details_x, details_y, details_width, details_height)
        
        # Ability details text boxes
        self.ability_name = TextBox(
            details_x + 20,
            details_y + 20,
            details_width - 40,
            30,
            "",
            None,
            WHITE,
            24,
            "left",
            "top"
        )
        
        self.ability_description = TextBox(
            details_x + 20,
            details_y + 60,
            details_width - 40,
            80,
            "",
            None,
            GRAY,
            16,
            "left",
            "top",
            False,
            True
        )
        
        self.ability_type = TextBox(
            details_x + 20,
            details_y + 150,
            details_width - 40,
            30,
            "",
            None,
            YELLOW,
            16,
            "left",
            "top"
        )
        
        self.ability_damage = TextBox(
            details_x + 20,
            details_y + 180,
            details_width - 40,
            30,
            "",
            None,
            RED,
            16,
            "left",
            "top"
        )
        
        self.ability_energy = TextBox(
            details_x + 20,
            details_y + 210,
            details_width - 40,
            30,
            "",
            None,
            BLUE,
            16,
            "left",
            "top"
        )
        
        self.ability_tier = TextBox(
            details_x + 20,
            details_y + 240,
            details_width - 40,
            30,
            "",
            None,
            PURPLE,
            16,
            "left",
            "top"
        )
        
        # New ability panel (only shown when learning a new ability)
        if self.learning_mode:
            # "Learn New Ability" text
            self.learn_title = TextBox(
                WINDOW_WIDTH // 2,
                details_y - 50,
                0,
                0,
                "Learn New Ability",
                None,
                GREEN,
                24,
                "center",
                "middle"
            )
            
            # New ability details panel
            new_ability_width = 400
            new_ability_height = 150
            new_ability_x = WINDOW_WIDTH // 2 - new_ability_width // 2
            new_ability_y = details_y + details_height + 20
            
            self.new_ability_panel = pygame.Rect(new_ability_x, new_ability_y, new_ability_width, new_ability_height)
            
            # New ability info
            self.new_ability_info = TextBox(
                new_ability_x + 20,
                new_ability_y + 20,
                new_ability_width - 40,
                110,
                f"New Ability: {self.new_ability.name}\n"
                f"Type: {self.new_ability.ability_type.capitalize()}\n"
                f"Damage: {self.new_ability.damage}\n"
                f"Energy Cost: {self.new_ability.energy_cost}\n"
                f"Tier: {self.new_ability.tier}",
                None,
                WHITE,
                16,
                "left",
                "top"
            )
            
            # "Select an ability to replace" instruction
            self.replace_instruction = TextBox(
                WINDOW_WIDTH // 2,
                list_y - 30,
                0,
                0,
                "Select an ability to replace:",
                None,
                YELLOW,
                18,
                "center",
                "middle"
            )
            
            # Learn button (enabled only when an ability is selected)
            self.learn_button = Button(
                new_ability_x + new_ability_width // 2 - 50,
                new_ability_y + new_ability_height - 40,
                100,
                30,
                "Learn",
                self.on_learn_ability,
                DARK_GRAY,
                GREEN,
                WHITE,
                16,
                "Replace the selected ability with the new one"
            )
        
        # Back button
        self.back_button = Button(
            WINDOW_WIDTH // 2 - 50,
            WINDOW_HEIGHT - 70,
            100,
            40,
            "Back",
            self.on_back_click,
            DARK_GRAY,
            RED,
            WHITE,
            20,
            "Return to previous screen"
        )
        
    def on_back_click(self):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
            
    def on_ability_select(self, index, ability_name):
        """
        Handle ability selection
        
        Parameters:
        -----------
        index : int
            Index of the selected ability
        ability_name : str
            Name of the selected ability
        """
        # Find the selected ability
        for i, ability in enumerate(self.creature.abilities):
            if ability.name == ability_name:
                self.selected_ability = ability
                self.selected_index = i
                break
                
        # Update ability details
        self.update_ability_details()
        
    def on_learn_ability(self):
        """Handle learn ability button click"""
        if not self.learning_mode or self.selected_index < 0 or not self.new_ability:
            return
            
        # Replace the selected ability with the new one
        success = self.creature.replace_ability(self.selected_index, len(self.creature.abilities) - 1)
        
        if success:
            self.add_notification(f"Learned {self.new_ability.name}!")
            
            # Clear pending skill
            self.creature.pending_skill = None
            
            # Exit learning mode
            self.learning_mode = False
            
            # Update UI
            self.init_ui()
            self.update_ability_details()
        else:
            self.add_notification("Failed to learn ability!")
            
    def update_ability_details(self):
        """Update ability details panel"""
        if not self.selected_ability:
            self.ability_name.set_text("")
            self.ability_description.set_text("")
            self.ability_type.set_text("")
            self.ability_damage.set_text("")
            self.ability_energy.set_text("")
            self.ability_tier.set_text("")
            return
            
        # Update ability details
        self.ability_name.set_text(self.selected_ability.name)
        
        # Create description if not available
        description = self.selected_ability.description
        if not description:
            if self.selected_ability.ability_type == "damage":
                description = "Deals damage to the target."
            elif self.selected_ability.ability_type == "buff":
                description = "Boosts one of your stats."
            elif self.selected_ability.ability_type == "debuff":
                description = "Reduces one of the target's stats."
            elif self.selected_ability.ability_type == "heal":
                description = "Restores your health."
            elif self.selected_ability.ability_type == "drain":
                description = "Deals damage and restores health."
            elif self.selected_ability.ability_type == "status":
                description = "Applies a status effect to the target."
            else:
                description = "No description available."
                
        self.ability_description.set_text(description)
        
        # Other details
        self.ability_type.set_text(f"Type: {self.selected_ability.ability_type.capitalize()}")
        self.ability_damage.set_text(f"Damage: {self.selected_ability.damage}")
        self.ability_energy.set_text(f"Energy Cost: {self.selected_ability.energy_cost}")
        
        tier_text = f"Tier: {self.selected_ability.tier}"
        if self.selected_ability.tier > self.creature.allowed_tier:
            tier_text += " (Too high for your level!)"
            
        self.ability_tier.set_text(tier_text)
        
    def add_notification(self, message):
        """
        Add a notification message
        
        Parameters:
        -----------
        message : str
            Notification message
        """
        self.notifications.append({
            "message": message,
            "time": self.notification_time
        })
        
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
            # Check buttons
            if self.back_button.handle_event(event):
                if self.back_button.hovered and self.back_button.tooltip:
                    self.active_tooltip = self.back_button.tooltip
                    
            # Check learn button if in learning mode
            if self.learning_mode and hasattr(self, 'learn_button'):
                if self.learn_button.handle_event(event):
                    if self.learn_button.hovered and self.learn_button.tooltip:
                        self.active_tooltip = self.learn_button.tooltip
                    
            # Check ability list
            self.ability_list.handle_event(event)
        
    def update(self, dt):
        """
        Update the ability screen
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        # Update animation
        self.animation_time += dt / 1000.0
        
        # Update notifications
        for notification in self.notifications[:]:
            notification["time"] -= dt / 1000.0
            if notification["time"] <= 0:
                self.notifications.remove(notification)
                
        # Update abilities if in learning mode
        if self.learning_mode:
            # Enable/disable learn button based on selection
            if hasattr(self, 'learn_button'):
                self.learn_button.enabled = self.selected_index >= 0
                self.learn_button.bg_color = GREEN if self.selected_index >= 0 else DARK_GRAY
                
    def draw(self):
        """Draw the ability screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        self.title.draw(self.screen)
        
        # Draw info box background
        pygame.draw.rect(self.screen, DARK_GRAY, self.info_box, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.info_box, width=2, border_radius=5)
        
        # Draw creature info
        self.creature_info.draw(self.screen)
        
        # Draw learning mode elements if active
        if self.learning_mode:
            if hasattr(self, 'learn_title'):
                self.learn_title.draw(self.screen)
                
            if hasattr(self, 'replace_instruction'):
                self.replace_instruction.draw(self.screen)
                
            if hasattr(self, 'new_ability_panel'):
                # Draw new ability panel background
                pygame.draw.rect(self.screen, DARK_GRAY, self.new_ability_panel, border_radius=5)
                pygame.draw.rect(self.screen, GREEN, self.new_ability_panel, width=2, border_radius=5)
                
                # Draw new ability info
                if hasattr(self, 'new_ability_info'):
                    self.new_ability_info.draw(self.screen)
                    
                # Draw learn button
                if hasattr(self, 'learn_button'):
                    self.learn_button.draw(self.screen)
        
        # Draw ability list
        self.ability_list.draw(self.screen)
        
        # Draw details panel background
        pygame.draw.rect(self.screen, DARK_GRAY, self.details_panel, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.details_panel, width=2, border_radius=5)
        
        # Draw ability details
        self.ability_name.draw(self.screen)
        self.ability_description.draw(self.screen)
        self.ability_type.draw(self.screen)
        self.ability_damage.draw(self.screen)
        self.ability_energy.draw(self.screen)
        self.ability_tier.draw(self.screen)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
        # Draw notifications
        self.draw_notifications()
        
        # Draw tooltip if active
        if self.active_tooltip:
            self.tooltip.text = self.active_tooltip
            self.tooltip.show(pygame.mouse.get_pos())
            self.tooltip.draw(self.screen)
        else:
            self.tooltip.hide()
            
    def draw_notifications(self):
        """Draw notification messages"""
        if not self.notifications:
            return
            
        notification_height = 30
        notification_spacing = 5
        notification_width = 300
        notification_x = WINDOW_WIDTH // 2 - notification_width // 2
        
        for i, notification in enumerate(self.notifications):
            notification_y = 70 + i * (notification_height + notification_spacing)
            
            # Draw background with fade based on time remaining
            alpha = min(255, int(255 * (notification["time"] / self.notification_time)))
            bg_rect = pygame.Rect(notification_x, notification_y, notification_width, notification_height)
            
            bg_surface = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (*BLUE[:3], alpha), bg_surface.get_rect(), border_radius=5)
            self.screen.blit(bg_surface, bg_rect)
            
            # Draw text
            text_surf, text_rect = self.font_small.render(notification["message"], WHITE)
            text_x = notification_x + (notification_width - text_rect.width) // 2
            text_y = notification_y + (notification_height - text_rect.height) // 2
            self.screen.blit(text_surf, (text_x, text_y))
