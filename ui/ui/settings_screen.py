# ui/settings_screen.py
# Settings screen for Dark Tamagotchi

import pygame
import pygame.freetype
import json
import os
from ui.ui_base import Button, TextBox, Tooltip
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE
)
from sound_manager import get_instance as get_sound_manager
from tutorial_system import get_instance as get_tutorial_manager

class Slider:
    """Simple slider UI control for adjusting numeric values"""
    
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, 
                 on_change=None, color=BLUE, bg_color=DARK_GRAY):
        """
        Initialize a slider
        
        Parameters:
        -----------
        x : int
            X position
        y : int
            Y position
        width : int
            Width of the slider track
        height : int
            Height of the slider track
        min_value : float
            Minimum slider value
        max_value : float
            Maximum slider value
        initial_value : float
            Initial slider value
        on_change : function, optional
            Callback function when slider value changes
        color : tuple, optional
            Color of the slider handle
        bg_color : tuple, optional
            Color of the slider track
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = max(min_value, min(max_value, initial_value))
        self.on_change = on_change
        self.color = color
        self.bg_color = bg_color
        self.dragging = False
        self.enabled = True
        
    def handle_event(self, event):
        """
        Handle pygame events
        
        Parameters:
        -----------
        event : pygame.event.Event
            The event to handle
            
        Returns:
        --------
        bool
            True if the event was handled, False otherwise
        """
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                # Set the value based on click position
                self._update_value(event.pos[0])
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Update value while dragging
                self._update_value(event.pos[0])
                return True
                
        return False
        
    def _update_value(self, x_pos):
        """
        Update the slider value based on x position
        
        Parameters:
        -----------
        x_pos : int
            X position of the mouse
        """
        # Calculate the relative position (0 to 1)
        rel_pos = (x_pos - self.rect.left) / self.rect.width
        rel_pos = max(0, min(1, rel_pos))
        
        # Convert to value range
        new_value = self.min_value + rel_pos * (self.max_value - self.min_value)
        
        # Only update if value changed
        if new_value != self.value:
            self.value = new_value
            
            # Call the callback if provided
            if self.on_change:
                self.on_change(self.value)
                
    def draw(self, surface):
        """
        Draw the slider
        
        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.enabled:
            bg_color = GRAY
            handle_color = DARK_GRAY
        else:
            bg_color = self.bg_color
            handle_color = self.color
            
        # Draw track
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=self.rect.height // 2)
        
        # Draw filled portion
        fill_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.left, self.rect.top, fill_width, self.rect.height)
        pygame.draw.rect(surface, handle_color, fill_rect, border_radius=self.rect.height // 2)
        
        # Draw handle
        handle_pos = self.rect.left + fill_width
        handle_radius = self.rect.height
        pygame.draw.circle(surface, WHITE, (handle_pos, self.rect.centery), handle_radius // 2)
        
    def set_value(self, value):
        """
        Set the slider value
        
        Parameters:
        -----------
        value : float
            New value
        """
        self.value = max(self.min_value, min(self.max_value, value))
        
    def get_value(self):
        """
        Get the current slider value
        
        Returns:
        --------
        float
            Current value
        """
        return self.value

class ToggleSwitch:
    """Simple toggle switch UI control"""
    
    def __init__(self, x, y, width, height, initial_state=False, on_change=None, 
                 on_color=GREEN, off_color=RED):
        """
        Initialize a toggle switch
        
        Parameters:
        -----------
        x : int
            X position
        y : int
            Y position
        width : int
            Width of the switch
        height : int
            Height of the switch
        initial_state : bool, optional
            Initial state (True = on, False = off)
        on_change : function, optional
            Callback function when state changes
        on_color : tuple, optional
            Color when switch is on
        off_color : tuple, optional
            Color when switch is off
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.state = initial_state
        self.on_change = on_change
        self.on_color = on_color
        self.off_color = off_color
        self.enabled = True
        
    def handle_event(self, event):
        """
        Handle pygame events
        
        Parameters:
        -----------
        event : pygame.event.Event
            The event to handle
            
        Returns:
        --------
        bool
            True if the event was handled, False otherwise
        """
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.toggle()
                return True
                
        return False
        
    def toggle(self):
        """Toggle the switch state"""
        self.state = not self.state
        
        # Call the callback if provided
        if self.on_change:
            self.on_change(self.state)
            
    def draw(self, surface):
        """
        Draw the toggle switch
        
        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        # Draw track
        track_rect = pygame.Rect(
            self.rect.left,
            self.rect.top + self.rect.height // 4,
            self.rect.width,
            self.rect.height // 2
        )
        
        if self.enabled:
            track_color = self.on_color if self.state else self.off_color
        else:
            track_color = GRAY
            
        pygame.draw.rect(surface, track_color, track_rect, border_radius=track_rect.height // 2)
        
        # Draw handle
        handle_radius = self.rect.height // 2
        if self.state:
            handle_pos = (self.rect.right - handle_radius, self.rect.centery)
        else:
            handle_pos = (self.rect.left + handle_radius, self.rect.centery)
            
        if self.enabled:
            handle_color = WHITE
        else:
            handle_color = DARK_GRAY
            
        pygame.draw.circle(surface, handle_color, handle_pos, handle_radius)
        
    def set_state(self, state):
        """
        Set the switch state
        
        Parameters:
        -----------
        state : bool
            New state
        """
        if self.state != state:
            self.state = state
            
            # Call the callback if provided
            if self.on_change:
                self.on_change(self.state)
                
    def get_state(self):
        """
        Get the current state
        
        Returns:
        --------
        bool
            Current state
        """
        return self.state

class SettingsScreen:
    """Settings screen for adjusting game options"""
    
    def __init__(self, screen, on_back=None):
        """
        Initialize the settings screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        on_back : function, optional
            Callback for back button
        """
        self.screen = screen
        self.on_back = on_back
        
        # Get managers
        self.sound_manager = get_sound_manager()
        self.tutorial_manager = get_tutorial_manager()
        
        # Initialize fonts
        pygame.freetype.init()
        self.font_large = pygame.freetype.SysFont('Arial', 32)
        self.font_medium = pygame.freetype.SysFont('Arial', 24)
        self.font_small = pygame.freetype.SysFont('Arial', 18)
        
        # Create background
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(BLACK)
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize UI components
        self.init_ui()
        
        # Create tooltip
        self.tooltip = Tooltip("")
        self.active_tooltip = None
        
    def load_settings(self):
        """
        Load settings from file
        
        Returns:
        --------
        dict
            Settings dictionary
        """
        default_settings = {
            "sound": {
                "music_volume": 0.5,
                "sound_volume": 0.7,
                "muted": False
            },
            "graphics": {
                "fullscreen": False,
                "animations": True,
                "particles": True
            },
            "gameplay": {
                "difficulty": "normal",
                "tutorials": True,
                "auto_save": True,
                "auto_save_interval": 60  # seconds
            }
        }
        
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    
                # Merge with defaults
                for category, options in default_settings.items():
                    if category not in settings:
                        settings[category] = {}
                    for option, value in options.items():
                        if option not in settings[category]:
                            settings[category][option] = value
                            
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return default_settings
        
    def save_settings(self):
        """Save settings to file"""
        try:
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
                
            print("Settings saved")
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def init_ui(self):
        """Initialize UI components"""
        # Title
        self.title = TextBox(
            WINDOW_WIDTH // 2,
            30,
            0,
            0,
            "Settings",
            None,
            WHITE,
            32,
            "center",
            "middle"
        )
        
        # Create section headers
        self.sound_header = TextBox(
            WINDOW_WIDTH // 2,
            80,
            0,
            0,
            "Sound",
            None,
            YELLOW,
            24,
            "center",
            "middle"
        )
        
        self.graphics_header = TextBox(
            WINDOW_WIDTH // 2,
            200,
            0,
            0,
            "Graphics",
            None,
            YELLOW,
            24,
            "center",
            "middle"
        )
        
        self.gameplay_header = TextBox(
            WINDOW_WIDTH // 2,
            320,
            0,
            0,
            "Gameplay",
            None,
            YELLOW,
            24,
            "center",
            "middle"
        )
        
        # Create sound settings
        self.music_volume_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            120,
            100,
            30,
            "Music Volume:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        self.music_volume_slider = Slider(
            WINDOW_WIDTH // 2,
            120,
            200,
            20,
            0.0,
            1.0,
            self.settings["sound"]["music_volume"],
            self.on_music_volume_change
        )
        
        self.sound_volume_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            150,
            100,
            30,
            "Sound Volume:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        self.sound_volume_slider = Slider(
            WINDOW_WIDTH // 2,
            150,
            200,
            20,
            0.0,
            1.0,
            self.settings["sound"]["sound_volume"],
            self.on_sound_volume_change
        )
        
        self.mute_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            180,
            100,
            30,
            "Mute Audio:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        self.mute_toggle = ToggleSwitch(
            WINDOW_WIDTH // 2,
            180,
            60,
            30,
            self.settings["sound"]["muted"],
            self.on_mute_toggle
        )
        
        # Create graphics settings
        self.fullscreen_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            240,
            100,
            30,
            "Fullscreen:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        self.fullscreen_toggle = ToggleSwitch(
            WINDOW_WIDTH // 2,
            240,
            60,
            30,
            self.settings["graphics"]["fullscreen"],
            self.on_fullscreen_toggle
        )
        
        self.animations_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            270,
            100,
            30,
            "Animations:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        self.animations_toggle = ToggleSwitch(
            WINDOW_WIDTH // 2,
            270,
            60,
            30,
            self.settings["graphics"]["animations"],
            self.on_animations_toggle
        )
        
        self.particles_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            300,
            100,
            30,
            "Particles:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        self.particles_toggle = ToggleSwitch(
            WINDOW_WIDTH // 2,
            300,
            60,
            30,
            self.settings["graphics"]["particles"],
            self.on_particles_toggle
        )
        
        # Create gameplay settings
        self.difficulty_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            360,
            100,
            30,
            "Difficulty:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        # Difficulty buttons
        button_width = 100
        button_height = 30
        button_spacing = 10
        
        difficulties = ["Easy", "Normal", "Hard"]
        self.difficulty_buttons = []
        
        for i, diff in enumerate(difficulties):
            button_x = WINDOW_WIDTH // 2 + i * (button_width + button_spacing) - ((len(difficulties) - 1) * (button_width + button_spacing)) // 2
            is_selected = self.settings["gameplay"]["difficulty"].lower() == diff.lower()
            
            button = Button(
                button_x,
                360,
                button_width,
                button_height,
                diff,
                lambda d=diff: self.on_difficulty_select(d),
                GREEN if is_selected else DARK_GRAY,
                BLUE if not is_selected else GREEN,
                WHITE,
                16
            )
            self.difficulty_buttons.append(button)
            
        self.tutorials_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            400,
            100,
            30,
            "Tutorials:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        self.tutorials_toggle = ToggleSwitch(
            WINDOW_WIDTH // 2,
            400,
            60,
            30,
            self.settings["gameplay"]["tutorials"],
            self.on_tutorials_toggle
        )
        
        self.reset_tutorials_button = Button(
            WINDOW_WIDTH // 2 + 100,
            400,
            150,
            30,
            "Reset Tutorials",
            self.on_reset_tutorials,
            DARK_GRAY,
            RED,
            WHITE,
            16,
            "Reset all tutorial progress"
        )
        
        self.auto_save_label = TextBox(
            WINDOW_WIDTH // 2 - 150,
            440,
            100,
            30,
            "Auto Save:",
            None,
            WHITE,
            18,
            "left",
            "middle"
        )
        
        self.auto_save_toggle = ToggleSwitch(
            WINDOW_WIDTH // 2,
            440,
            60,
            30,
            self.settings["gameplay"]["auto_save"],
            self.on_auto_save_toggle
        )
        
        # Action buttons
        button_width = 150
        button_height = 40
        button_spacing = 20
        button_y = WINDOW_HEIGHT - 80
        
        self.save_button = Button(
            WINDOW_WIDTH // 2 - button_width - button_spacing // 2,
            button_y,
            button_width,
            button_height,
            "Save Settings",
            self.on_save_click,
            DARK_GRAY,
            GREEN,
            WHITE,
            20,
            "Save all settings"
        )
        
        self.back_button = Button(
            WINDOW_WIDTH // 2 + button_spacing // 2,
            button_y,
            button_width,
            button_height,
            "Back",
            self.on_back_click,
            DARK_GRAY,
            RED,
            WHITE,
            20,
            "Return without saving"
        )
        
    def on_music_volume_change(self, value):
        """
        Handle music volume change
        
        Parameters:
        -----------
        value : float
            New volume value
        """
        self.settings["sound"]["music_volume"] = value
        self.sound_manager.set_music_volume(value)
        
    def on_sound_volume_change(self, value):
        """
        Handle sound volume change
        
        Parameters:
        -----------
        value : float
            New volume value
        """
        self.settings["sound"]["sound_volume"] = value
        self.sound_manager.set_sound_volume(value)
        
    def on_mute_toggle(self, state):
        """
        Handle mute toggle
        
        Parameters:
        -----------
        state : bool
            New mute state
        """
        self.settings["sound"]["muted"] = state
        self.sound_manager.toggle_mute()
        
    def on_fullscreen_toggle(self, state):
        """
        Handle fullscreen toggle
        
        Parameters:
        -----------
        state : bool
            New fullscreen state
        """
        self.settings["graphics"]["fullscreen"] = state
        
    def on_animations_toggle(self, state):
        """
        Handle animations toggle
        
        Parameters:
        -----------
        state : bool
            New animations state
        """
        self.settings["graphics"]["animations"] = state
        
    def on_particles_toggle(self, state):
        """
        Handle particles toggle
        
        Parameters:
        -----------
        state : bool
            New particles state
        """
        self.settings["graphics"]["particles"] = state
        
    def on_difficulty_select(self, difficulty):
        """
        Handle difficulty selection
        
        Parameters:
        -----------
        difficulty : str
            Selected difficulty
        """
        self.settings["gameplay"]["difficulty"] = difficulty.lower()
        
        # Update button colors
        for button in self.difficulty_buttons:
            if button.text.lower() == difficulty.lower():
                button.bg_color = GREEN
            else:
                button.bg_color = DARK_GRAY
                
    def on_tutorials_toggle(self, state):
        """
        Handle tutorials toggle
        
        Parameters:
        -----------
        state : bool
            New tutorials state
        """
        self.settings["gameplay"]["tutorials"] = state
        
    def on_reset_tutorials(self):
        """Handle reset tutorials button click"""
        self.tutorial_manager.reset_tutorial_progress()
        self.sound_manager.play_sound("ui/click")
        
    def on_auto_save_toggle(self, state):
        """
        Handle auto save toggle
        
        Parameters:
        -----------
        state : bool
            New auto save state
        """
        self.settings["gameplay"]["auto_save"] = state
        
    def on_save_click(self):
        """Handle save button click"""
        self.save_settings()
        self.sound_manager.play_sound("ui/click")
        
        if self.on_back:
            self.on_back()
            
    def on_back_click(self):
        """Handle back button click"""
        self.sound_manager.play_sound("ui/click")
        
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
        # Reset tooltip
        self.active_tooltip = None
        
        # Process events
        for event in events:
            # Check sliders
            self.music_volume_slider.handle_event(event)
            self.sound_volume_slider.handle_event(event)
            
            # Check toggles
            self.mute_toggle.handle_event(event)
            self.fullscreen_toggle.handle_event(event)
            self.animations_toggle.handle_event(event)
            self.particles_toggle.handle_event(event)
            self.tutorials_toggle.handle_event(event)
            self.auto_save_toggle.handle_event(event)
            
            # Check buttons
            for button in self.difficulty_buttons:
                if button.handle_event(event):
                    break
                    
            if self.reset_tutorials_button.handle_event(event):
                if self.reset_tutorials_button.hovered and self.reset_tutorials_button.tooltip:
                    self.active_tooltip = self.reset_tutorials_button.tooltip
                    
            elif self.save_button.handle_event(event):
                if self.save_button.hovered and self.save_button.tooltip:
                    self.active_tooltip = self.save_button.tooltip
                    
            elif self.back_button.handle_event(event):
                if self.back_button.hovered and self.back_button.tooltip:
                    self.active_tooltip = self.back_button.tooltip
        
    def update(self, dt):
        """
        Update the settings screen
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        pass
        
    def draw(self):
        """Draw the settings screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        self.title.draw(self.screen)
        
        # Draw section headers
        self.sound_header.draw(self.screen)
        self.graphics_header.draw(self.screen)
        self.gameplay_header.draw(self.screen)
        
        # Draw sound settings
        self.music_volume_label.draw(self.screen)
        self.music_volume_slider.draw(self.screen)
        self.sound_volume_label.draw(self.screen)
        self.sound_volume_slider.draw(self.screen)
        self.mute_label.draw(self.screen)
        self.mute_toggle.draw(self.screen)
        
        # Draw graphics settings
        self.fullscreen_label.draw(self.screen)
        self.fullscreen_toggle.draw(self.screen)
        self.animations_label.draw(self.screen)
        self.animations_toggle.draw(self.screen)
        self.particles_label.draw(self.screen)
        self.particles_toggle.draw(self.screen)
        
        # Draw gameplay settings
        self.difficulty_label.draw(self.screen)
        for button in self.difficulty_buttons:
            button.draw(self.screen)
        self.tutorials_label.draw(self.screen)
        self.tutorials_toggle.draw(self.screen)
        self.reset_tutorials_button.draw(self.screen)
        self.auto_save_label.draw(self.screen)
        self.auto_save_toggle.draw(self.screen)
        
        # Draw action buttons
        self.save_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # Draw tooltip if active
        if self.active_tooltip:
            self.tooltip.text = self.active_tooltip
            self.tooltip.show(pygame.mouse.get_pos())
            self.tooltip.draw(self.screen)
        else:
            self.tooltip.hide()
