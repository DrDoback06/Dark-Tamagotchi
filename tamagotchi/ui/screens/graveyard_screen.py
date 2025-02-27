# ui/graveyard_screen.py
# Graveyard screen for Dark Tamagotchi

import pygame
import pygame.freetype
import time
from tamagotchi.ui.ui_base import Button, TextBox, ScrollableList, Tooltip
from tamagotchi.utils.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE
)

class GraveyardScreen:
    """Graveyard screen for managing dead creatures"""
    
    def __init__(self, screen, char_manager, current_creature, on_back=None):
        """
        Initialize the graveyard screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        char_manager : CharacterManager
            Character manager with tombstone data
        current_creature : Creature
            The player's active creature
        on_back : function, optional
            Callback for back button
        """
        self.screen = screen
        self.char_manager = char_manager
        self.current_creature = current_creature
        self.on_back = on_back
        
        # Load tombstones
        self.tombstones = self.char_manager.get_tombstones()
        
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
        
        # Selected tombstone
        self.selected_tombstone = None
        self.selected_index = -1
        
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
            "Graveyard",
            None,
            WHITE,
            32,
            "center",
            "middle"
        )
        
        # Subtitle
        self.subtitle = TextBox(
            WINDOW_WIDTH // 2,
            70,
            0,
            0,
            "Honor your fallen creatures and transfer their knowledge",
            None,
            GRAY,
            18,
            "center",
            "middle"
        )
        
        # Current creature info
        info_width = 300
        info_height = 80
        info_x = WINDOW_WIDTH - info_width - 50
        info_y = 100
        
        self.info_box = pygame.Rect(info_x, info_y, info_width, info_height)
        
        self.creature_info = TextBox(
            info_x + 20,
            info_y + 10,
            info_width - 40,
            60,
            f"Current: {self.current_creature.creature_type}\n"
            f"Level: {self.current_creature.level} | XP: {self.current_creature.xp}/{self.current_creature.level * 100}",
            None,
            WHITE,
            16,
            "left",
            "middle"
        )
        
        # Tombstone list
        list_width = 300
        list_height = 350
        list_x = 50
        list_y = 120
        
        # Format tombstone names for the list
        tombstone_labels = []
        for tomb in self.tombstones:
            label = f"{tomb['creature_type']} (Lvl {tomb['level']})"
            if tomb.get("xp_transferred", False):
                label += " [Transferred]"
            tombstone_labels.append(label)
        
        self.tombstone_list = ScrollableList(
            list_x,
            list_y,
            list_width,
            list_height,
            tombstone_labels,
            DARK_GRAY,
            40,
            BLUE,
            GRAY,
            WHITE,
            16,
            self.on_tombstone_select
        )
        
        # Tombstone details panel
        details_width = 400
        details_height = 350
        details_x = WINDOW_WIDTH - details_width - 50
        details_y = 200
        
        self.details_panel = pygame.Rect(details_x, details_y, details_width, details_height)
        
        # Tombstone details text boxes
        self.tombstone_name = TextBox(
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
        
        self.tombstone_details = TextBox(
            details_x + 20,
            details_y + 60,
            details_width - 40,
            200,
            "",
            None,
            GRAY,
            16,
            "left",
            "top",
            False,
            True
        )
        
        # Transfer XP button
        self.transfer_button = Button(
            details_x + details_width // 2 - 75,
            details_y + details_height - 60,
            150,
            40,
            "Transfer XP",
            self.on_transfer_xp,
            DARK_GRAY,
            GREEN,
            WHITE,
            20,
            "Transfer bonus XP to your current creature"
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
            
    def on_tombstone_select(self, index, tombstone_label):
        """
        Handle tombstone selection
        
        Parameters:
        -----------
        index : int
            Index of the selected tombstone
        tombstone_label : str
            Label of the selected tombstone
        """
        if index < 0 or index >= len(self.tombstones):
            return
            
        self.selected_tombstone = self.tombstones[index]
        self.selected_index = index
        
        # Update tombstone details
        self.update_tombstone_details()
        
    def on_transfer_xp(self):
        """Handle transfer XP button click"""
        if not self.selected_tombstone or self.selected_index < 0:
            self.add_notification("No tombstone selected!")
            return
            
        # Check if XP already transferred
        if self.selected_tombstone.get("xp_transferred", False):
            self.add_notification("XP already transferred from this tombstone!")
            return
            
        # Transfer the XP
        success = self.char_manager.transfer_bonus_xp(self.selected_index, self.current_creature)
        
        if success:
            # Update the tombstone in our local list
            self.selected_tombstone["xp_transferred"] = True
            
            # Update the list item
            tombstone_labels = []
            for tomb in self.tombstones:
                label = f"{tomb['creature_type']} (Lvl {tomb['level']})"
                if tomb.get("xp_transferred", False):
                    label += " [Transferred]"
                tombstone_labels.append(label)
                
            self.tombstone_list.set_items(tombstone_labels)
            
            # Update the details
            self.update_tombstone_details()
            
            # Update creature info
            self.creature_info.set_text(
                f"Current: {self.current_creature.creature_type}\n"
                f"Level: {self.current_creature.level} | XP: {self.current_creature.xp}/{self.current_creature.level * 100}"
            )
            
            # Add notification
            bonus_xp = self.selected_tombstone.get("bonus_xp", 0)
            self.add_notification(f"Transferred {bonus_xp} XP!")
        else:
            self.add_notification("Failed to transfer XP!")
            
    def update_tombstone_details(self):
        """Update tombstone details panel"""
        if not self.selected_tombstone:
            self.tombstone_name.set_text("")
            self.tombstone_details.set_text("")
            self.transfer_button.enabled = False
            self.transfer_button.bg_color = DARK_GRAY
            return
            
        # Update tombstone details
        creature_type = self.selected_tombstone.get("creature_type", "Unknown")
        level = self.selected_tombstone.get("level", 0)
        
        self.tombstone_name.set_text(f"{creature_type} (Level {level})")
        
        # Format details text
        cause = self.selected_tombstone.get("cause_of_death", "unknown")
        age_seconds = self.selected_tombstone.get("age", 0)
        age_minutes = int(age_seconds // 60)
        age_seconds = int(age_seconds % 60)
        
        timestamp = self.selected_tombstone.get("time_of_death", 0)
        date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
        
        bonus_xp = self.selected_tombstone.get("bonus_xp", 0)
        transferred = self.selected_tombstone.get("xp_transferred", False)
        
        details_text = (
            f"Cause of death: {cause.capitalize()}\n"
            f"Lived for: {age_minutes}m {age_seconds}s\n"
            f"Date of death: {date_str}\n"
            f"Bonus XP available: {bonus_xp}\n"
            f"XP transferred: {'Yes' if transferred else 'No'}"
        )
        
        self.tombstone_details.set_text(details_text)
        
        # Enable/disable transfer button
        can_transfer = not transferred and bonus_xp > 0
        self.transfer_button.enabled = can_transfer
        self.transfer_button.bg_color = GREEN if can_transfer else DARK_GRAY
        
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
                    
            elif self.transfer_button.handle_event(event):
                if self.transfer_button.hovered and self.transfer_button.tooltip:
                    self.active_tooltip = self.transfer_button.tooltip
                    
            # Check tombstone list
            self.tombstone_list.handle_event(event)
        
    def update(self, dt):
        """
        Update the graveyard screen
        
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
                
    def draw(self):
        """Draw the graveyard screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title and subtitle
        self.title.draw(self.screen)
        self.subtitle.draw(self.screen)
        
        # Draw info box background
        pygame.draw.rect(self.screen, DARK_GRAY, self.info_box, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.info_box, width=2, border_radius=5)
        
        # Draw creature info
        self.creature_info.draw(self.screen)
        
        # Draw tombstone list
        self.tombstone_list.draw(self.screen)
        
        # Draw details panel background
        pygame.draw.rect(self.screen, DARK_GRAY, self.details_panel, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.details_panel, width=2, border_radius=5)
        
        # Draw tombstone details
        self.tombstone_name.draw(self.screen)
        self.tombstone_details.draw(self.screen)
        
        # Draw transfer button
        self.transfer_button.draw(self.screen)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
        # Draw decorative tombstones
        self.draw_decorative_tombstones()
        
        # Draw notifications
        self.draw_notifications()
        
        # Draw tooltip if active
        if self.active_tooltip:
            self.tooltip.text = self.active_tooltip
            self.tooltip.show(pygame.mouse.get_pos())
            self.tooltip.draw(self.screen)
        else:
            self.tooltip.hide()
            
    def draw_decorative_tombstones(self):
        """Draw decorative tombstones in the background"""
        # Draw some tombstone shapes
        for i in range(3):
            x = 100 + i * 100
            y = WINDOW_HEIGHT - 150
            
            # Draw tombstone shape
            tombstone_width = 60
            tombstone_height = 80
            
            # Base
            pygame.draw.rect(self.screen, GRAY, 
                            (x - tombstone_width // 2, y - tombstone_height, tombstone_width, tombstone_height),
                            border_radius=10)
            
            # Top semi-circle
            pygame.draw.arc(self.screen, GRAY,
                           (x - tombstone_width // 2, y - tombstone_height - 20, tombstone_width, 40),
                           3.14, 0, width=20)
            
            # Draw R.I.P. text
            rip_text = TextBox(
                x,
                y - tombstone_height + 20,
                0,
                0,
                "R.I.P.",
                None,
                BLACK,
                14,
                "center",
                "middle"
            )
            rip_text.draw(self.screen)
            
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
