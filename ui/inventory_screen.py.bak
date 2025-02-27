# ui/inventory_screen.py
# Inventory management screen for Dark Tamagotchi

import pygame
import pygame.freetype
from ui.ui_base import Button, TextBox, ScrollableList, Tooltip
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE
)

class InventoryScreen:
    """Inventory management screen"""
    
    def __init__(self, screen, creature, on_back=None):
        """
        Initialize the inventory screen
        
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
        
        # Selected item
        self.selected_item = None
        
        # Notification variables
        self.notifications = []
        self.notification_time = 3.0  # seconds
        
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
            "Inventory",
            None,
            WHITE,
            32,
            "center",
            "middle"
        )
        
        # Creature stats
        stats_width = 300
        stats_height = 80
        stats_x = 50
        stats_y = 80
        
        self.stats_box = pygame.Rect(stats_x, stats_y, stats_width, stats_height)
        
        # HP bar
        self.hp_text = TextBox(
            stats_x + 10,
            stats_y + 10,
            280,
            20,
            f"HP: {int(self.creature.current_hp)}/{self.creature.max_hp}",
            None,
            WHITE,
            16,
            "left",
            "middle"
        )
        
        # Energy bar
        self.energy_text = TextBox(
            stats_x + 10,
            stats_y + 40,
            280,
            20,
            f"Energy: {int(self.creature.energy)}/{self.creature.energy_max}",
            None,
            WHITE,
            16,
            "left",
            "middle"
        )
        
        # Item list
        list_width = 300
        list_height = 400
        list_x = 50
        list_y = 180
        
        self.item_list = ScrollableList(
            list_x,
            list_y,
            list_width,
            list_height,
            [item.name for item in self.creature.inventory],
            DARK_GRAY,
            30,
            BLUE,
            GRAY,
            WHITE,
            16,
            self.on_item_select
        )
        
        # Item details panel
        details_width = 400
        details_height = 400
        details_x = WINDOW_WIDTH - details_width - 50
        details_y = 180
        
        self.details_panel = pygame.Rect(details_x, details_y, details_width, details_height)
        
        # Use button
        self.use_button = Button(
            details_x + details_width // 2 - 50,
            details_y + details_height - 60,
            100,
            40,
            "Use Item",
            self.on_use_item,
            DARK_GRAY,
            GREEN,
            WHITE,
            20,
            "Use the selected item"
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
        
        # Item details text boxes
        self.item_name = TextBox(
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
        
        self.item_description = TextBox(
            details_x + 20,
            details_y + 60,
            details_width - 40,
            100,
            "",
            None,
            GRAY,
            16,
            "left",
            "top",
            False,
            True
        )
        
        self.item_effect = TextBox(
            details_x + 20,
            details_y + 170,
            details_width - 40,
            30,
            "",
            None,
            GREEN,
            16,
            "left",
            "top"
        )
        
        self.item_quantity = TextBox(
            details_x + 20,
            details_y + 210,
            details_width - 40,
            30,
            "",
            None,
            YELLOW,
            16,
            "left",
            "top"
        )
        
    def on_back_click(self):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
            
    def on_item_select(self, index, item_name):
        """
        Handle item selection
        
        Parameters:
        -----------
        index : int
            Index of the selected item
        item_name : str
            Name of the selected item
        """
        # Find the selected item in inventory
        for item in self.creature.inventory:
            if item.name == item_name:
                self.selected_item = item
                break
                
        # Update item details
        self.update_item_details()
        
    def on_use_item(self):
        """Handle use item button click"""
        if not self.selected_item:
            self.add_notification("No item selected!")
            return
            
        # Use the item
        success = self.creature.use_item(self.selected_item.name)
        
        if success:
            self.add_notification(f"Used {self.selected_item.name}!")
            
            # Update UI
            self.update_ui()
            
            # Clear selection if item was used up
            if self.selected_item.quantity <= 0:
                self.selected_item = None
                self.update_item_details()
        else:
            self.add_notification(f"Cannot use {self.selected_item.name}!")
            
    def update_item_details(self):
        """Update item details panel"""
        if not self.selected_item:
            self.item_name.set_text("")
            self.item_description.set_text("")
            self.item_effect.set_text("")
            self.item_quantity.set_text("")
            return
            
        # Update item details
        self.item_name.set_text(self.selected_item.name)
        self.item_description.set_text(self.selected_item.description)
        
        # Format effect text based on effect type
        effect = self.selected_item.effect
        effect_type = effect.get("type", "unknown")
        
        if effect_type == "heal":
            effect_text = f"Heals {effect.get('amount', 0)} HP"
        elif effect_type == "energy":
            effect_text = f"Restores {effect.get('amount', 0)} energy"
        elif effect_type == "hunger":
            effect_text = f"Reduces hunger by {effect.get('amount', 0)}"
        elif effect_type == "mood":
            effect_text = f"Changes mood by {effect.get('amount', 0)}"
        elif effect_type == "stat_boost":
            stat = effect.get("stat", "unknown")
            amount = effect.get("amount", 0)
            effect_text = f"Increases {stat} by {amount}"
        elif effect_type == "skill":
            effect_text = "Teaches a new ability"
        else:
            effect_text = "Unknown effect"
            
        self.item_effect.set_text(f"Effect: {effect_text}")
        self.item_quantity.set_text(f"Quantity: {self.selected_item.quantity}")
        
    def update_ui(self):
        """Update UI components with current stats"""
        # Update creature stats
        self.hp_text.set_text(f"HP: {int(self.creature.current_hp)}/{self.creature.max_hp}")
        self.energy_text.set_text(f"Energy: {int(self.creature.energy)}/{self.creature.energy_max}")
        
        # Update item list
        self.item_list.set_items([item.name for item in self.creature.inventory])
        
        # Update item details if needed
        if self.selected_item:
            # Check if selected item still exists
            if self.selected_item.name in [item.name for item in self.creature.inventory]:
                self.update_item_details()
            else:
                self.selected_item = None
                self.update_item_details()
                
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
                    
            elif self.use_button.handle_event(event):
                if self.use_button.hovered and self.use_button.tooltip:
                    self.active_tooltip = self.use_button.tooltip
                    
            # Check item list
            self.item_list.handle_event(event)
        
    def update(self, dt):
        """
        Update the inventory screen
        
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
                
        # Update UI
        self.update_ui()
        
    def draw(self):
        """Draw the inventory screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        self.title.draw(self.screen)
        
        # Draw stats box background
        pygame.draw.rect(self.screen, DARK_GRAY, self.stats_box, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.stats_box, width=2, border_radius=5)
        
        # Draw stats
        self.hp_text.draw(self.screen)
        self.energy_text.draw(self.screen)
        
        # Draw item list
        self.item_list.draw(self.screen)
        
        # Draw details panel background
        pygame.draw.rect(self.screen, DARK_GRAY, self.details_panel, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.details_panel, width=2, border_radius=5)
        
        # Draw item details
        self.item_name.draw(self.screen)
        self.item_description.draw(self.screen)
        self.item_effect.draw(self.screen)
        self.item_quantity.draw(self.screen)
        
        # Draw buttons
        self.use_button.draw(self.screen)
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
