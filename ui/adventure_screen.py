# ui/adventure_screen.py
# Adventure screen for Dark Tamagotchi

import pygame
import pygame.freetype
import random
from ui.ui_base import Button, TextBox, ProgressBar, Tooltip
from src.core.creatures import Creature
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE,
    ADVENTURE_COMPLETION_DISTANCE
)
from adventure_system import Adventure

class AdventureScreen:
    """Adventure mode interface"""
    
    def __init__(self, screen, creature, on_complete=None, on_battle=None, on_main_menu=None):
        """
        Initialize the adventure screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        creature : Creature
            The player's creature
        on_complete : function, optional
            Callback for adventure completion
        on_battle : function, optional
            Callback for battles
        on_main_menu : function, optional
            Callback for returning to main menu
        """
        self.screen = screen
        self.creature = creature
        self.on_complete = on_complete
        self.on_battle = on_battle
        self.on_main_menu = on_main_menu
        
        # Create adventure
        self.adventure = Adventure(creature)
        
        # Initialize fonts
        pygame.freetype.init()
        self.font_large = pygame.freetype.SysFont('Arial', 32)
        self.font_medium = pygame.freetype.SysFont('Arial', 24)
        self.font_small = pygame.freetype.SysFont('Arial', 16)
        
        # Create background
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(BLACK)
        
        # Background elements
        self.bg_elements = []
        self.generate_background_elements()
        
        # Initialize UI components
        self.init_ui()
        
        # Create tooltip
        self.tooltip = Tooltip("")
        self.active_tooltip = None
        
        # Current event handling
        self.current_event = None
        self.event_buttons = []
        
        # Animation variables
        self.animation_time = 0
        self.creatures = []  # List of creatures encountered during adventure
        
    def generate_background_elements(self):
        """Generate random background elements for the adventure"""
        # Create trees, rocks, clouds, etc.
        for _ in range(20):
            element = {
                "type": random.choice(["tree", "rock", "bush", "flower"]),
                "x": random.randint(0, WINDOW_WIDTH),
                "y": random.randint(WINDOW_HEIGHT // 2, WINDOW_HEIGHT - 50),
                "size": random.randint(20, 50)
            }
            self.bg_elements.append(element)
            
        # Create clouds
        for _ in range(5):
            cloud = {
                "type": "cloud",
                "x": random.randint(0, WINDOW_WIDTH),
                "y": random.randint(50, WINDOW_HEIGHT // 3),
                "width": random.randint(60, 150),
                "height": random.randint(30, 60),
                "speed": random.uniform(5, 15)
            }
            self.bg_elements.append(cloud)
        
    def init_ui(self):
        """Initialize UI components"""
        # Title
        self.title = TextBox(
            WINDOW_WIDTH // 2 - 100,
            20,
            200,
            40,
            "Adventure",
            None,
            WHITE,
            32,
            "center",
            "middle"
        )
        
        # Progress bar
        self.progress_bar = ProgressBar(
            100,
            80,
            WINDOW_WIDTH - 200,
            20,
            self.adventure.distance,
            self.adventure.max_distance,
            DARK_GRAY,
            GREEN,
            WHITE,
            True,
            "Progress"
        )
        
        # Creature stats
        stats_width = 200
        stats_height = 80
        stats_x = 20
        stats_y = 120
        
        self.stats_box = pygame.Rect(stats_x, stats_y, stats_width, stats_height)
        
        # HP bar
        self.hp_bar = ProgressBar(
            stats_x + 10,
            stats_y + 10,
            stats_width - 20,
            20,
            self.creature.current_hp,
            self.creature.max_hp,
            DARK_GRAY,
            RED,
            WHITE,
            True,
            "HP"
        )
        
        # Energy bar
        self.energy_bar = ProgressBar(
            stats_x + 10,
            stats_y + 40,
            stats_width - 20,
            20,
            self.creature.energy,
            self.creature.energy_max,
            DARK_GRAY,
            BLUE,
            WHITE,
            True,
            "Energy"
        )
        
        # Adventure log
        log_width = WINDOW_WIDTH - 400
        log_height = 100
        log_x = 240
        log_y = 120
        
        self.log_box = TextBox(
            log_x,
            log_y,
            log_width,
            log_height,
            "Adventure started! Exploring the wilderness...",
            DARK_GRAY,
            WHITE,
            16,
            "left",
            "top",
            True,
            True,
            5
        )
        
        # Action buttons
        button_width = 150
        button_height = 40
        button_x = WINDOW_WIDTH - button_width - 20
        button_spacing = 10
        
        self.continue_button = Button(
            button_x,
            WINDOW_HEIGHT - 3 * (button_height + button_spacing),
            button_width,
            button_height,
            "Continue",
            self.on_continue_click,
            DARK_GRAY,
            GREEN,
            WHITE,
            20,
            "Continue the adventure"
        )
        
        self.rest_button = Button(
            button_x,
            WINDOW_HEIGHT - 2 * (button_height + button_spacing),
            button_width,
            button_height,
            "Rest",
            self.on_rest_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            20,
            "Rest to recover energy"
        )
        
        self.exit_button = Button(
            button_x,
            WINDOW_HEIGHT - button_height - button_spacing,
            button_width,
            button_height,
            "Exit",
            self.on_exit_click,
            DARK_GRAY,
            RED,
            WHITE,
            20,
            "Exit the adventure"
        )
        
    def on_continue_click(self):
        """Handle continue button click"""
        if self.current_event:
            # Clear current event
            self.current_event = None
            self.event_buttons = []
            
            # Add log message
            self.log_box.set_text(f"{self.log_box.text}\nContinuing the adventure...")
            
    def on_rest_click(self):
        """Handle rest button click"""
        # Rest to recover energy and HP
        energy_recovery = self.creature.energy_max * 0.3
        hp_recovery = self.creature.max_hp * 0.2
        
        old_energy = self.creature.energy
        old_hp = self.creature.current_hp
        
        self.creature.energy = min(self.creature.energy_max, self.creature.energy + energy_recovery)
        self.creature.current_hp = min(self.creature.max_hp, self.creature.current_hp + hp_recovery)
        
        actual_energy_recovered = self.creature.energy - old_energy
        actual_hp_recovered = self.creature.current_hp - old_hp
        
        # Add log message
        self.log_box.set_text(
            f"{self.log_box.text}\n"
            f"Rested and recovered {int(actual_energy_recovered)} energy and {int(actual_hp_recovered)} HP."
        )
        
    def on_exit_click(self):
        """Handle exit button click"""
        # End adventure and collect rewards
        if not self.adventure.is_complete:
            self.adventure.is_active = False
            
            # Add log message
            self.log_box.set_text(f"{self.log_box.text}\nExiting adventure early.")
            
        # Call callback
        if self.on_main_menu:
            self.on_main_menu()
            
    def handle_event_choice(self, choice_index):
        """
        Handle player's choice in an event
        
        Parameters:
        -----------
        choice_index : int
            Index of the chosen option
        """
        if not self.current_event or choice_index >= len(self.current_event["options"]):
            return
            
        # Process the choice
        result = self.adventure.handle_special_encounter_choice(choice_index)
        
        # Add result to log
        self.log_box.set_text(f"{self.log_box.text}\n{result['message']}")
        
        # Handle result based on type
        if result["type"] == "encounter":
            # Store the creature for battle
            self.current_event = None
            self.event_buttons = []
            
            if self.on_battle:
                self.on_battle(result["creature"])
                
        elif result["type"] == "reward":
            # Just clear the event after showing the reward
            self.current_event = None
            self.event_buttons = []
            
        # Other result types would be handled here
        
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
            # If there's a current event with choices, check those buttons first
            if self.current_event and self.event_buttons:
                for i, button in enumerate(self.event_buttons):
                    if button.handle_event(event):
                        if button.hovered and button.tooltip:
                            self.active_tooltip = button.tooltip
                        break
                        
            # Check main buttons
            elif self.continue_button.handle_event(event):
                if self.continue_button.hovered and self.continue_button.tooltip:
                    self.active_tooltip = self.continue_button.tooltip
                    
            elif self.rest_button.handle_event(event):
                if self.rest_button.hovered and self.rest_button.tooltip:
                    self.active_tooltip = self.rest_button.tooltip
                    
            elif self.exit_button.handle_event(event):
                if self.exit_button.hovered and self.exit_button.tooltip:
                    self.active_tooltip = self.exit_button.tooltip
                    
    def update(self, dt):
        """
        Update the adventure screen
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        # Update animation
        self.animation_time += dt / 1000.0
        
        # Update background elements
        for element in self.bg_elements:
            if element["type"] == "cloud":
                element["x"] += element["speed"] * dt / 1000.0
                if element["x"] > WINDOW_WIDTH + element["width"]:
                    element["x"] = -element["width"]
                    
        # If there's no current event, update the adventure
        if not self.current_event and self.adventure.is_active:
            event = self.adventure.update(dt)
            
            if event:
                # Handle the event
                self.handle_adventure_event(event)
                
        # Update UI with current stats
        self.update_ui()
        
    def update_ui(self):
        """Update UI components with current stats"""
        # Update progress bar
        self.progress_bar.set_value(self.adventure.distance)
        
        # Update HP and energy bars
        self.hp_bar.set_value(self.creature.current_hp)
        self.energy_bar.set_value(self.creature.energy)
        
    def handle_adventure_event(self, event):
        """
        Handle an adventure event
        
        Parameters:
        -----------
        event : dict
            Event data
        """
        # Log the event
        if "message" in event:
            self.log_box.set_text(f"{self.log_box.text}\n{event['message']}")
            
        # Process based on event type
        if event["type"] == "encounter":
            # Store the creature for battle
            if self.on_battle:
                self.on_battle(event["creature"])
                
        elif event["type"] == "item":
            # Item was already added to inventory in Adventure.update()
            pass
            
        elif event["type"] == "special":
            # Show special encounter with choices
            self.current_event = event
            
            # Create buttons for each choice
            self.create_event_choice_buttons(event)
            
        elif event["type"] == "completion":
            # Adventure complete
            self.adventure.is_complete = True
            self.adventure.is_active = False
            
            if self.on_complete:
                self.on_complete()
                
    def create_event_choice_buttons(self, event):
        """
        Create buttons for event choices
        
        Parameters:
        -----------
        event : dict
            Event data
        """
        self.event_buttons = []
        
        options = event.get("options", [])
        if not options:
            return
            
        # Create a button for each option
        button_width = 300
        button_height = 40
        button_spacing = 10
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        button_start_y = WINDOW_HEIGHT // 2
        
        for i, option in enumerate(options):
            button = Button(
                button_x,
                button_start_y + i * (button_height + button_spacing),
                button_width,
                button_height,
                option["text"],
                lambda idx=i: self.handle_event_choice(idx),
                DARK_GRAY,
                BLUE,
                WHITE,
                16
            )
            self.event_buttons.append(button)
            
    def draw(self):
        """Draw the adventure screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw sky
        sky_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, (100, 150, 255), sky_rect)
        
        # Draw ground
        ground_rect = pygame.Rect(0, WINDOW_HEIGHT // 2, WINDOW_WIDTH, WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, (100, 180, 100), ground_rect)
        
        # Draw path
        path_width = 100
        path_points = [
            (0, WINDOW_HEIGHT - 100),
            (WINDOW_WIDTH, WINDOW_HEIGHT - 100)
        ]
        pygame.draw.line(self.screen, (160, 140, 120), path_points[0], path_points[1], path_width)
        
        # Draw background elements
        for element in self.bg_elements:
            if element["type"] == "tree":
                # Draw tree
                trunk_rect = pygame.Rect(
                    element["x"], 
                    element["y"] - element["size"], 
                    element["size"] // 3, 
                    element["size"]
                )
                pygame.draw.rect(self.screen, (100, 70, 30), trunk_rect)
                
                leaves_rect = pygame.Rect(
                    element["x"] - element["size"] // 2,
                    element["y"] - element["size"] * 1.5,
                    element["size"],
                    element["size"]
                )
                pygame.draw.ellipse(self.screen, (30, 100, 30), leaves_rect)
                
            elif element["type"] == "rock":
                # Draw rock
                rock_rect = pygame.Rect(
                    element["x"],
                    element["y"] - element["size"] // 2,
                    element["size"],
                    element["size"] // 2
                )
                pygame.draw.ellipse(self.screen, (150, 150, 150), rock_rect)
                
            elif element["type"] == "bush":
                # Draw bush
                bush_rect = pygame.Rect(
                    element["x"] - element["size"] // 2,
                    element["y"] - element["size"] // 2,
                    element["size"],
                    element["size"] // 2
                )
                pygame.draw.ellipse(self.screen, (50, 120, 50), bush_rect)
                
            elif element["type"] == "flower":
                # Draw flower
                stem_rect = pygame.Rect(
                    element["x"],
                    element["y"] - element["size"] // 2,
                    element["size"] // 8,
                    element["size"] // 2
                )
                pygame.draw.rect(self.screen, (30, 100, 30), stem_rect)
                
                flower_rect = pygame.Rect(
                    element["x"] - element["size"] // 4,
                    element["y"] - element["size"] // 2 - element["size"] // 4,
                    element["size"] // 2,
                    element["size"] // 4
                )
                pygame.draw.ellipse(self.screen, (255, 200, 50), flower_rect)
                
            elif element["type"] == "cloud":
                # Draw cloud
                cloud_rect = pygame.Rect(
                    int(element["x"]),
                    element["y"],
                    element["width"],
                    element["height"]
                )
                pygame.draw.ellipse(self.screen, (240, 240, 255), cloud_rect)
        
        # Draw title
        self.title.draw(self.screen)
        
        # Draw progress bar
        self.progress_bar.draw(self.screen)
        
        # Draw stats box background
        pygame.draw.rect(self.screen, DARK_GRAY, self.stats_box, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, self.stats_box, width=2, border_radius=5)
        
        # Draw HP and energy bars
        self.hp_bar.draw(self.screen)
        self.energy_bar.draw(self.screen)
        
        # Draw adventure log
        self.log_box.draw(self.screen)
        
        # Draw player character
        player_x = 100
        player_y = WINDOW_HEIGHT - 150
        player_width = 50
        player_height = 50
        
        # Simple bouncing animation
        bounce_offset = int(5 * pygame.math.sin(self.animation_time * 5))
        
        player_rect = pygame.Rect(
            player_x,
            player_y + bounce_offset,
            player_width,
            player_height
        )
        pygame.draw.rect(self.screen, BLUE, player_rect, border_radius=10)
        
        # Draw creature name above player
        player_name = TextBox(
            player_x + player_width // 2,
            player_y - 20 + bounce_offset,
            0,
            0,
            self.creature.creature_type,
            None,
            WHITE,
            12,
            "center",
            "middle"
        )
        player_name.draw(self.screen)
        
        # Draw buttons
        self.continue_button.draw(self.screen)
        self.rest_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        
        # Draw current event if any
        if self.current_event:
            self.draw_current_event()
            
        # Draw event choice buttons if any
        for button in self.event_buttons:
            button.draw(self.screen)
            
        # Draw tooltip if active
        if self.active_tooltip:
            self.tooltip.text = self.active_tooltip
            self.tooltip.show(pygame.mouse.get_pos())
            self.tooltip.draw(self.screen)
        else:
            self.tooltip.hide()
            
        # Draw completion message if adventure is complete
        if self.adventure.is_complete:
            self.draw_completion_message()
            
    def draw_current_event(self):
        """Draw the current event"""
        # Create overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw event box
        event_box = pygame.Rect(
            WINDOW_WIDTH // 2 - 300,
            WINDOW_HEIGHT // 2 - 200,
            600,
            150
        )
        pygame.draw.rect(self.screen, DARK_GRAY, event_box, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, event_box, width=2, border_radius=10)
        
        # Draw event message
        event_message = TextBox(
            event_box.x + 20,
            event_box.y + 20,
            event_box.width - 40,
            event_box.height - 40,
            self.current_event["message"],
            None,
            WHITE,
            20,
            "center",
            "middle",
            False,
            True
        )
        event_message.draw(self.screen)
        
    def draw_completion_message(self):
        """Draw adventure completion message"""
        # Create overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw completion box
        completion_box = pygame.Rect(
            WINDOW_WIDTH // 2 - 250,
            WINDOW_HEIGHT // 2 - 150,
            500,
            300
        )
        pygame.draw.rect(self.screen, DARK_GRAY, completion_box, border_radius=10)
        pygame.draw.rect(self.screen, GREEN, completion_box, width=3, border_radius=10)
        
        # Draw completion title
        completion_title = TextBox(
            WINDOW_WIDTH // 2,
            completion_box.y + 30,
            0,
            0,
            "Adventure Complete!",
            None,
            GREEN,
            32,
            "center",
            "middle"
        )
        completion_title.draw(self.screen)
        
        # Draw stats
        stats_text = [
            f"Distance: {int(self.adventure.distance)}/{ADVENTURE_COMPLETION_DISTANCE}",
            f"Encounters: {len(self.adventure.encounters)}",
            f"Items Found: {len(self.adventure.items_found)}",
            f"Time: {int((self.adventure.end_time - self.adventure.start_time) // 60)}m {int((self.adventure.end_time - self.adventure.start_time) % 60)}s",
            f"XP Gained: {int(self.adventure.distance / ADVENTURE_COMPLETION_DISTANCE * 100)}"
        ]
        
        for i, text in enumerate(stats_text):
            stat_text = TextBox(
                WINDOW_WIDTH // 2,
                completion_box.y + 100 + i * 30,
                0,
                0,
                text,
                None,
                WHITE,
                20,
                "center",
                "middle"
            )
            stat_text.draw(self.screen)
            
        # Draw continue message
        continue_text = TextBox(
            WINDOW_WIDTH // 2,
            completion_box.y + 250,
            0,
            0,
            "Press 'Exit' to return to the main screen",
            None,
            YELLOW,
            16,
            "center",
            "middle"
        )
        continue_text.draw(self.screen)
