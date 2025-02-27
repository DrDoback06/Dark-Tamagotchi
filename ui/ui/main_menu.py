# ui/main_menu.py
# Main menu screen for Dark Tamagotchi

import pygame
from ui.ui_base import Button, TextBox, Tooltip
from config import WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY, BLUE

class MainMenu:
    """Main menu screen for the game"""

    def __init__(self, screen, on_new_game=None, on_load_game=None, on_settings=None, on_quit=None):
        """
        Initialize the main menu

        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        on_new_game : function, optional
            Callback for new game button
        on_load_game : function, optional
            Callback for load game button
        on_settings : function, optional
            Callback for settings button
        on_quit : function, optional
            Callback for quit button
        """
        self.screen = screen
        self.on_new_game = on_new_game
        self.on_load_game = on_load_game
        self.on_settings = on_settings
        self.on_quit = on_quit

        # Create background
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(BLACK)

        # Initialize font
        self.font = pygame.font.SysFont("Arial", 48)
        self.small_font = pygame.font.SysFont("Arial", 24)

        # Create title
        self.title = TextBox(
            WINDOW_WIDTH // 2 - 200,
            100,
            400,
            80,
            "Dark Tamagotchi",
            None,
            WHITE,
            48,
            "center",
            "middle"
        )

        # Create subtitle
        self.subtitle = TextBox(
            WINDOW_WIDTH // 2 - 200,
            180,
            400,
            40,
            "Raise Your Creature, Battle Your Friends",
            None,
            GRAY,
            24,
            "center",
            "middle"
        )

        # Create buttons
        button_width = 200
        button_height = 50
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        button_start_y = 250
        button_spacing = 20

        self.new_game_btn = Button(
            button_x,
            button_start_y,
            button_width,
            button_height,
            "New Creature",
            self.on_new_game_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            24,
            "Create a new creature to start your adventure"
        )

        self.load_game_btn = Button(
            button_x,
            button_start_y + button_height + button_spacing,
            button_width,
            button_height,
            "Load Creature",
            self.on_load_game_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            24,
            "Load an existing creature"
        )

        self.settings_btn = Button(
            button_x,
            button_start_y + (button_height + button_spacing) * 2,
            button_width,
            button_height,
            "Settings",
            self.on_settings_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            24,
            "Adjust game settings"
        )

        self.quit_btn = Button(
            button_x,
            button_start_y + (button_height + button_spacing) * 3,
            button_width,
            button_height,
            "Quit",
            self.on_quit_click,
            DARK_GRAY,
            BLUE,
            WHITE,
            24,
            "Exit the game"
        )

        # Create tooltip
        self.tooltip = Tooltip("")
        self.active_tooltip = None

        # Animation variables
        self.animation_time = 0
        self.pulse_scale = 1.0

    def on_new_game_click(self):
        """Handle new game button click"""
        if self.on_new_game:
            self.on_new_game()

    def on_load_game_click(self):
        """Handle load game button click"""
        if self.on_load_game:
            self.on_load_game()

    def on_settings_click(self):
        """Handle settings button click"""
        if self.on_settings:
            self.on_settings()

    def on_quit_click(self):
        """Handle quit button click"""
        if self.on_quit:
            self.on_quit()
        else:
            pygame.quit()

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
            if self.new_game_btn.handle_event(event):
                if self.new_game_btn.hovered and self.new_game_btn.tooltip:
                    self.active_tooltip = self.new_game_btn.tooltip

            elif self.load_game_btn.handle_event(event):
                if self.load_game_btn.hovered and self.load_game_btn.tooltip:
                    self.active_tooltip = self.load_game_btn.tooltip

            elif self.settings_btn.handle_event(event):
                if self.settings_btn.hovered and self.settings_btn.tooltip:
                    self.active_tooltip = self.settings_btn.tooltip

            elif self.quit_btn.handle_event(event):
                if self.quit_btn.hovered and self.quit_btn.tooltip:
                    self.active_tooltip = self.quit_btn.tooltip

    def update(self, dt):
        """
        Update the main menu

        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        # Update animation
        self.animation_time += dt / 1000.0
        self.pulse_scale = 1.0 + 0.05 * abs(pygame.math.sin(self.animation_time))

    def draw(self, current_creature=None):
        """
        Draw the main menu

        Parameters:
        -----------
        current_creature : Creature, optional
            Current active creature
        """
        # Draw background
        self.screen.blit(self.background, (0, 0))

        # Draw animated title
        self.title.draw(self.screen)
        self.subtitle.draw(self.screen)

        # Draw buttons
        self.new_game_btn.draw(self.screen)
        self.load_game_btn.draw(self.screen)
        self.settings_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)

        # Draw current creature info if available
        if current_creature:
            info_text = f"Current Creature: {current_creature.creature_type} (Level {current_creature.level})"
            creature_info = TextBox(
                WINDOW_WIDTH // 2 - 250,
                WINDOW_HEIGHT - 100,
                500,
                40,
                info_text,
                DARK_GRAY,
                WHITE,
                20,
                "center",
                "middle",
                True
            )
            creature_info.draw(self.screen)

            # Draw continue button
            continue_btn = Button(
                WINDOW_WIDTH // 2 - 100,
                WINDOW_HEIGHT - 50,
                200,
                40,
                "Continue",
                None,  # This would be handled by the game engine
                DARK_GRAY,
                BLUE,
                WHITE,
                20
            )
            continue_btn.draw(self.screen)

        # Draw tooltip if active
        if self.active_tooltip:
            self.tooltip.text = self.active_tooltip
            self.tooltip.show(pygame.mouse.get_pos())
            self.tooltip.draw(self.screen)
        else:
            self.tooltip.hide()
