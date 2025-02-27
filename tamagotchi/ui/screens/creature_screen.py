# ui/creature_screen.py
# Creature management screen for Dark Tamagotchi

import pygame
import pygame.freetype
from ui.ui_base import Button, TextBox, ProgressBar, IconButton, Tooltip
from tamagotchi.utils.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE
)

class CreatureScreen:
    """Creature management screen"""
    
    def __init__(self, screen, creature, on_battle=None, on_adventure=None, on_main_menu=None, 
                 on_show_inventory=None, on_show_abilities=None):
        """
        Initialize the creature screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        creature : Creature
            The creature to display
        on_battle : function, optional
            Callback for battle button
        on_adventure : function, optional
            Callback for adventure button
        on_main_menu : function, optional
            Callback for main menu button
        on_show_inventory : function, optional
            Callback for inventory button
        on_show_abilities : function, optional
            Callback for abilities button
        """
        self.screen = screen
        self.creature = creature
        self.on_battle = on_battle
        self.on_adventure = on_adventure
        self.on_main_menu = on_main_menu
        self.on_show_inventory = on_show_inventory
        self.on_show_abilities = on_show_abilities
        
        # Initialize fonts
        pygame.freetype.init()
        self.font_large = pygame.freetype.SysFont('Arial', 32)
        self.font_medium = pygame.freetype.SysFont('Arial', 24)
        self.font_small = pygame.freetype.SysFont('Arial', 16)
        
        # Create background
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(BLACK)
        
        # Initialize UI components
        self.init_ui()
        
        # Create tooltip
        self.tooltip = Tooltip("")
        self.active_tooltip = None
        
        # Animation variables
        self.animation_time = 0
        
        # Notification variables
        self.notifications = []
        self.notification_time = 3.0  # 3 seconds per notification
        
    def init_ui(self):
        """Initialize UI components"""
        # Title area
        self.title = TextBox(
            WINDOW_WIDTH // 2 - 200,
            20,
            400,
            40,
            f"{self.creature.creature_type} - Level {self.creature.level}",
            None,
            WHITE,
            32,
            "center",
            "middle"
        )
        
        # Creature stats panel (left side)
        stats_panel_width = 300
        stats_panel_height = 400
        stats_panel_x = 50
        stats_panel_y = 80
        
        self.stats_panel = pygame.Rect(stats_panel_x, stats_panel_y, stats_panel_width, stats_panel_height)
        
        # Add stat labels and values
        self.stat_labels = []
        self.stat_values = []
        
        stat_y = stats_panel_y + 10
        stat_height = 25
        stat_spacing = 5
        
        # HP stat with progress bar
        self.hp_label = TextBox(
            stats_panel_x + 10,
            stat_y,
            60,
            stat_height,
            "HP:",
            None,
            WHITE,
            16,
            "left",
            "middle"
        )
        
        self.hp_bar = ProgressBar(
            stats_panel_x + 80,
            stat_y,
            stats_panel_width - 100,
            stat_height,
            self.creature.current_hp,
            self.creature.max_hp,
            DARK_GRAY,
            RED,
            WHITE,
            True
        )
        
        stat_y += stat_height + stat_spacing
        
        # Energy stat with progress bar
        self.energy_label = TextBox(
            stats_panel_x + 10,
            stat_y,
            60,
            stat_height,
            "Energy:",
            None,
            WHITE,
            16,
            "left",
            "middle"
        )
        
        self.energy_bar = ProgressBar(
            stats_panel_x + 80,
            stat_y,
            stats_panel_width - 100,
            stat_height,
            self.creature.energy,
            self.creature.energy_max,
            DARK_GRAY,
            BLUE,
            WHITE,
            True
        )
        
        stat_y += stat_height + stat_spacing
        
        # Hunger stat with progress bar (inversed - lower is better)
        self.hunger_label = TextBox(
            stats_panel_x + 10,
            stat_y,
            60,
            stat_height,
            "Hunger:",
            None,
            WHITE,
            16,
            "left",
            "middle"
        )
        
        # For hunger, invert the fill since lower hunger is better
        self.hunger_bar = ProgressBar(
            stats_panel_x + 80,
            stat_y,
            stats_panel_width - 100,
            stat_height,
            100 - self.creature.hunger,  # Invert for display
            100,
            DARK_GRAY,
            GREEN,
            WHITE,
            True
        )
        
        stat_y += stat_height + stat_spacing
        
        # Mood stat with progress bar
        self.mood_label = TextBox(
            stats_panel_x + 10,
            stat_y,
            60,
            stat_height,
            "Mood:",
            None,
            WHITE,
            16,
            "left",
            "middle"
        )
        
        # Determine color based on how close to ideal mood
        mood_diff = abs(self.creature.mood - self.creature.ideal_mood)
        if mood_diff < 10:
            mood_color = GREEN
        elif mood_diff < 30:
            mood_color = YELLOW
        else:
            mood_color = RED
            
        self.mood_bar = ProgressBar(
            stats_panel_x + 80,
            stat_y,
            stats_panel_width - 100,
            stat_height,
            self.creature.mood,
            100,
            DARK_GRAY,
            mood_color,
            WHITE,
            True
        )
        
        stat_y += stat_height + stat_spacing
        
        # Other stats as text
        stats = [
            ("Attack:", f"{self.creature.attack}"),
            ("Defense:", f"{self.creature.defense}"),
            ("Speed:", f"{self.creature.speed}"),
            ("Age:", f"{int(self.creature.age // 60)}m {int(self.creature.age % 60)}s"),
            ("XP:", f"{self.creature.xp}/{self.creature.level * 100}"),
            ("Wellness:", f"{self.creature.wellness}%"),
            ("Evolution:", f"Stage {self.creature.evolution_stage}")
        ]
        
        for label, value in stats:
            label_box = TextBox(
                stats_panel_x + 10,
                stat_y,
                100,
                stat_height,
                label,
                None,
                WHITE,
                16,
                "left",
                "middle"
            )
            
            value_box = TextBox(
                stats_panel_x + 110,
                stat_y,
                stats_panel_width - 120,
                stat_height,
                value,
                None,
                GRAY,
                16,
                "left",
                "middle"
            )
            
            self.stat_labels.append(label_box)
            self.stat_values.append(value_box)
            
            stat_y += stat_height + stat_spacing
        
        # Action buttons panel (bottom)
        button_panel_height = 100
        button_panel_y = WINDOW_HEIGHT - button_panel_height - 20
        button_width = 120
        button_height = 40
        button_spacing = 20
        button_start_x = (WINDOW_WIDTH - (button_width * 4 + button_spacing * 3)) // 2
        
        # Create action buttons
        self.feed_button = Button(
            button_start_x,
            button_panel_y + 10,
            button_width,
            button_height,
            "Feed",
            self.on_feed_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            20,
            "Feed your creature to reduce hunger"
        )
        
        self.sleep_button = Button(
            button_start_x + button_width + button_spacing,
            button_panel_y + 10,
            button_width,
            button_height,
            "Sleep" if not self.creature.is_sleeping else "Wake Up",
            self.on_sleep_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            20,
            "Toggle sleep mode to recover energy"
        )
        
        self.inventory_button = Button(
            button_start_x + (button_width + button_spacing) * 2,
            button_panel_y + 10,
            button_width,
            button_height,
            "Inventory",
            self.on_inventory_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            20,
            "View and use items in your inventory"
        )
        
        self.abilities_button = Button(
            button_start_x + (button_width + button_spacing) * 3,
            button_panel_y + 10,
            button_width,
            button_height,
            "Abilities",
            self.on_abilities_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            20,
            "View and manage your abilities"
        )
        
        # Activity buttons (second row)
        self.battle_button = Button(
            button_start_x,
            button_panel_y + button_height + 20,
            button_width,
            button_height,
            "Battle",
            self.on_battle_click,
            DARK_GRAY,
            RED,
            WHITE,
            20,
            "Battle against other creatures"
        )
        
        self.adventure_button = Button(
            button_start_x + button_width + button_spacing,
            button_panel_y + button_height + 20,
            button_width,
            button_height,
            "Adventure",
            self.on_adventure_click,
            DARK_GRAY,
            GREEN,
            WHITE,
            20,
            "Go on an adventure to find items and improve skills"
        )
        
        self.main_menu_button = Button(
            button_start_x + (button_width + button_spacing) * 3,
            button_panel_y + button_height + 20,
            button_width,
            button_height,
            "Main Menu",
            self.on_main_menu_click,
            DARK_GRAY,
            GRAY,
            WHITE,
            20,
            "Return to the main menu"
        )
        
        # Create pending skill notification if any
        if self.creature.pending_skill:
            self.add_notification(f"New ability available: {self.creature.pending_skill.name}")
        
    def on_feed_click(self):
        """Handle feed button click"""
        success = self.creature.feed()
        if success:
            self.add_notification(f"{self.creature.creature_type} was fed!")
        else:
            self.add_notification(f"Cannot feed {self.creature.creature_type} right now.")
            
    def on_sleep_click(self):
        """Handle sleep button click"""
        if self.creature.is_sleeping:
            self.creature.wake_up()
            self.sleep_button.set_text("Sleep")
            self.add_notification(f"{self.creature.creature_type} woke up!")
        else:
            self.creature.sleep()
            self.sleep_button.set_text("Wake Up")
            self.add_notification(f"{self.creature.creature_type} went to sleep.")
            
    def on_inventory_click(self):
        """Handle inventory button click"""
        if self.on_show_inventory:
            self.on_show_inventory()
            
    def on_abilities_click(self):
        """Handle abilities button click"""
        if self.on_show_abilities:
            self.on_show_abilities()
            
    def on_battle_click(self):
        """Handle battle button click"""
        if self.on_battle:
            self.on_battle()
            
    def on_adventure_click(self):
        """Handle adventure button click"""
        if self.on_adventure:
            self.on_adventure()
            
    def on_main_menu_click(self):
        """Handle main menu button click"""
        if self.on_main_menu:
            self.on_main_menu()
            
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
        
    def update_ui(self):
        """Update UI components with current creature stats"""
        # Update title
        self.title.set_text(f"{self.creature.creature_type} - Level {self.creature.level}")
        
        # Update progress bars
        self.hp_bar.set_value(self.creature.current_hp)
        self.hp_bar.max_value = self.creature.max_hp
        
        self.energy_bar.set_value(self.creature.energy)
        self.energy_bar.max_value = self.creature.energy_max
        
        self.hunger_bar.set_value(100 - self.creature.hunger)  # Invert for display
        
        self.mood_bar.set_value(self.creature.mood)
        
        # Update mood bar color
        mood_diff = abs(self.creature.mood - self.creature.ideal_mood)
        if mood_diff < 10:
            self.mood_bar.fill_color = GREEN
        elif mood_diff < 30:
            self.mood_bar.fill_color = YELLOW
        else:
            self.mood_bar.fill_color = RED
        
        # Update other stats
        stat_values = [
            f"{self.creature.attack}",
            f"{self.creature.defense}",
            f"{self.creature.speed}",
            f"{int(self.creature.age // 60)}m {int(self.creature.age % 60)}s",
            f"{self.creature.xp}/{self.creature.level * 100}",
            f"{self.creature.wellness}%",
            f"Stage {self.creature.evolution_stage}"
        ]
        
        for i, value in enumerate(stat_values):
            if i < len(self.stat_values):
                self.stat_values[i].set_text(value)
        
        # Update sleep button text
        self.sleep_button.set_text("Wake Up" if self.creature.is_sleeping else "Sleep")
        
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
            buttons = [
                self.feed_button, self.sleep_button, self.inventory_button, 
                self.abilities_button, self.battle_button, self.adventure_button,
                self.main_menu_button
            ]
            
            for button in buttons:
                if button.handle_event(event):
                    if button.hovered and button.tooltip:
                        self.active_tooltip = button.tooltip
                    break
        
    def update(self, dt):
        """
        Update the creature screen
        
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
                
        # Update UI components with current creature stats
        self.update_ui()
        
    def draw(self):
        """Draw the creature screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        self.title.draw(self.screen)
        
        # Draw stats panel background
        pygame.draw.rect(self.screen, DARK_GRAY, self.stats_panel, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.stats_panel, width=2, border_radius=5)
        
        # Draw stat bars
        self.hp_label.draw(self.screen)
        self.hp_bar.draw(self.screen)
        
        self.energy_label.draw(self.screen)
        self.energy_bar.draw(self.screen)
        
        self.hunger_label.draw(self.screen)
        self.hunger_bar.draw(self.screen)
        
        self.mood_label.draw(self.screen)
        self.mood_bar.draw(self.screen)
        
        # Draw other stats
        for label, value in zip(self.stat_labels, self.stat_values):
            label.draw(self.screen)
            value.draw(self.screen)
            
        # Draw creature visualization (placeholder)
        creature_display_rect = pygame.Rect(
            WINDOW_WIDTH - 350,
            100,
            300,
            300
        )
        pygame.draw.rect(self.screen, DARK_GRAY, creature_display_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, creature_display_rect, width=2, border_radius=5)
        
        # Draw placeholder creature icon
        icon_rect = pygame.Rect(
            creature_display_rect.x + 50,
            creature_display_rect.y + 50,
            200,
            200
        )
        pygame.draw.rect(self.screen, GRAY, icon_rect, border_radius=10)
        
        creature_name = TextBox(
            creature_display_rect.x + 150,
            creature_display_rect.y + 260,
            0,
            0,
            self.creature.creature_type,
            None,
            WHITE,
            20,
            "center",
            "middle"
        )
        creature_name.draw(self.screen)
        
        # Draw buttons
        self.feed_button.draw(self.screen)
        self.sleep_button.draw(self.screen)
        self.inventory_button.draw(self.screen)
        self.abilities_button.draw(self.screen)
        self.battle_button.draw(self.screen)
        self.adventure_button.draw(self.screen)
        self.main_menu_button.draw(self.screen)
        
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
