# time_system.py
# Day and night cycle system for Dark Tamagotchi

import pygame
import time
import math

class TimeSystem:
    """
    Manages the day and night cycle in the game.
    
    This system tracks in-game time, provides day/night state information,
    and handles visual transitions between different times of day.
    """
    
    # Time of day definitions (in game hours)
    DAWN = 5.0
    MORNING = 8.0
    NOON = 12.0
    AFTERNOON = 15.0
    EVENING = 18.0
    NIGHT = 21.0
    MIDNIGHT = 0.0
    
    # Color palettes for different times of day
    COLORS = {
        "dawn": {
            "sky": (255, 200, 150),
            "ground": (100, 120, 80),
            "ambient": (255, 220, 180),
            "shadow": (70, 60, 90)
        },
        "day": {
            "sky": (100, 150, 255),
            "ground": (100, 180, 100),
            "ambient": (255, 255, 255),
            "shadow": (80, 80, 100)
        },
        "evening": {
            "sky": (255, 150, 100),
            "ground": (80, 120, 60),
            "ambient": (255, 200, 150),
            "shadow": (60, 50, 80)
        },
        "night": {
            "sky": (20, 30, 80),
            "ground": (30, 60, 40),
            "ambient": (100, 120, 180),
            "shadow": (10, 10, 30)
        }
    }
    
    def __init__(self, time_scale=60.0):
        """
        Initialize the time system
        
        Parameters:
        -----------
        time_scale : float
            Scale factor for time progression (real seconds per game hour)
        """
        self.time_scale = time_scale  # Real seconds per game hour
        self.game_hour = 12.0  # Start at noon
        self.day = 1
        self.start_time = time.time()
        self.paused = False
        self.pause_time = 0
        
        # For tracking time-based events
        self.last_hour = self.game_hour
        self.hour_changed = False
        self.day_changed = False
        
        # For visual effects
        self.transition_progress = 0.0
        self.current_palette = self.get_color_palette()
        self.target_palette = self.current_palette
        
    def update(self, dt):
        """
        Update the time system
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        if self.paused:
            return
            
        # Convert dt to seconds
        dt_sec = dt / 1000.0
        
        # Store previous hour and day
        prev_hour = self.game_hour
        prev_day = self.day
        
        # Update game time
        self.game_hour += dt_sec / self.time_scale
        
        # Wrap day
        if self.game_hour >= 24.0:
            self.game_hour -= 24.0
            self.day += 1
            
        # Check for hour change
        self.hour_changed = int(prev_hour) != int(self.game_hour)
        
        # Check for day change
        self.day_changed = prev_day != self.day
        
        # Update color transitions
        self.update_color_transition(dt_sec)
        
    def update_color_transition(self, dt_sec):
        """
        Update color transition effects
        
        Parameters:
        -----------
        dt_sec : float
            Time passed in seconds
        """
        # Get the target color palette for current time
        self.target_palette = self.get_color_palette()
        
        # If target palette is different from current, transition
        if self.target_palette != self.current_palette:
            transition_speed = 0.5  # Complete transition in 2 seconds
            self.transition_progress += dt_sec * transition_speed
            
            if self.transition_progress >= 1.0:
                self.transition_progress = 0.0
                self.current_palette = self.target_palette
                
    def get_time_of_day(self):
        """
        Get the current time of day as a string
        
        Returns:
        --------
        str
            Time of day: 'dawn', 'morning', 'day', 'afternoon', 'evening', or 'night'
        """
        if self.MIDNIGHT <= self.game_hour < self.DAWN:
            return "night"
        elif self.DAWN <= self.game_hour < self.MORNING:
            return "dawn"
        elif self.MORNING <= self.game_hour < self.NOON:
            return "morning"
        elif self.NOON <= self.game_hour < self.AFTERNOON:
            return "day"
        elif self.AFTERNOON <= self.game_hour < self.EVENING:
            return "afternoon"
        elif self.EVENING <= self.game_hour < self.NIGHT:
            return "evening"
        else:  # self.NIGHT <= self.game_hour < 24.0:
            return "night"
            
    def get_color_palette(self):
        """
        Get the color palette for the current time of day
        
        Returns:
        --------
        dict
            Color palette with sky, ground, ambient, and shadow colors
        """
        time_of_day = self.get_time_of_day()
        
        if time_of_day in ("dawn", "morning"):
            return self.COLORS["dawn"]
        elif time_of_day in ("day", "afternoon"):
            return self.COLORS["day"]
        elif time_of_day == "evening":
            return self.COLORS["evening"]
        else:  # night
            return self.COLORS["night"]
            
    def get_current_colors(self):
        """
        Get the current colors based on transition state
        
        Returns:
        --------
        dict
            Interpolated color palette
        """
        if self.transition_progress == 0.0:
            return self.current_palette
            
        result = {}
        for key in self.current_palette:
            current_color = self.current_palette[key]
            target_color = self.target_palette[key]
            
            # Interpolate between current and target colors
            r = int(current_color[0] + (target_color[0] - current_color[0]) * self.transition_progress)
            g = int(current_color[1] + (target_color[1] - current_color[1]) * self.transition_progress)
            b = int(current_color[2] + (target_color[2] - current_color[2]) * self.transition_progress)
            
            result[key] = (r, g, b)
            
        return result
        
    def pause(self):
        """Pause the time system"""
        if not self.paused:
            self.paused = True
            self.pause_time = time.time()
            
    def resume(self):
        """Resume the time system"""
        if self.paused:
            self.paused = False
            pause_duration = time.time() - self.pause_time
            self.start_time += pause_duration
            
    def set_time(self, hour):
        """
        Set the game time to a specific hour
        
        Parameters:
        -----------
        hour : float
            Game hour to set (0-24)
        """
        self.game_hour = max(0.0, min(24.0, hour))
        self.current_palette = self.get_color_palette()
        self.target_palette = self.current_palette
        self.transition_progress = 0.0
        
    def get_day_progress(self):
        """
        Get the progress through the current day
        
        Returns:
        --------
        float
            Progress (0.0 to 1.0) through the current day
        """
        return self.game_hour / 24.0
        
    def get_formatted_time(self):
        """
        Get a formatted time string (HH:MM AM/PM)
        
        Returns:
        --------
        str
            Formatted time string
        """
        hour = int(self.game_hour)
        minute = int((self.game_hour - hour) * 60)
        
        period = "AM" if hour < 12 else "PM"
        hour12 = hour % 12
        if hour12 == 0:
            hour12 = 12
            
        return f"{hour12:02d}:{minute:02d} {period}"
        
    def did_hour_change(self):
        """Check if the hour changed this update"""
        return self.hour_changed
        
    def did_day_change(self):
        """Check if the day changed this update"""
        return self.day_changed
        
    def get_light_level(self):
        """
        Get the current light level (0.0 to 1.0)
        
        Returns:
        --------
        float
            Light level where 1.0 is full daylight and 0.0 is darkness
        """
        time_of_day = self.get_time_of_day()
        
        if time_of_day == "day":
            return 1.0
        elif time_of_day in ("morning", "afternoon"):
            return 0.9
        elif time_of_day == "evening":
            return 0.7
        elif time_of_day == "dawn":
            return 0.6
        else:  # night
            return 0.3
            
    def get_encounter_modifier(self):
        """
        Get the encounter rate modifier based on time of day
        
        Returns:
        --------
        float
            Modifier for encounter rates
        """
        time_of_day = self.get_time_of_day()
        
        # Night increases monster encounters
        if time_of_day == "night":
            return 1.5
        # Dawn and evening slightly increase encounters
        elif time_of_day in ("dawn", "evening"):
            return 1.2
        # Default is normal rate
        return 1.0
        
    def get_sky_color(self):
        """
        Get the current sky color based on time
        
        Returns:
        --------
        tuple
            RGB color tuple
        """
        colors = self.get_current_colors()
        return colors["sky"]
        
    def get_ground_color(self):
        """
        Get the current ground color based on time
        
        Returns:
        --------
        tuple
            RGB color tuple
        """
        colors = self.get_current_colors()
        return colors["ground"]
        
    def get_ambient_color(self):
        """
        Get the current ambient light color
        
        Returns:
        --------
        tuple
            RGB color tuple
        """
        colors = self.get_current_colors()
        return colors["ambient"]
        
    def get_shadow_color(self):
        """
        Get the current shadow color
        
        Returns:
        --------
        tuple
            RGB color tuple
        """
        colors = self.get_current_colors()
        return colors["shadow"]
        
    def draw_day_night_indicator(self, surface, x, y, width, height):
        """
        Draw a day/night cycle indicator UI element
        
        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        x, y : int
            Position to draw at
        width, height : int
            Size of the indicator
        """
        # Draw background
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height), border_radius=height//2)
        
        # Draw time marker
        progress = self.get_day_progress()
        marker_x = x + int(width * progress)
        marker_y = y + height // 2
        marker_radius = height // 2
        
        # Draw sun or moon based on time
        if 6 <= self.game_hour < 18:  # Daytime (sun)
            pygame.draw.circle(surface, (255, 220, 100), (marker_x, marker_y), marker_radius)
        else:  # Nighttime (moon)
            pygame.draw.circle(surface, (220, 220, 255), (marker_x, marker_y), marker_radius)
            # Draw moon shadow for realism
            shadow_x = marker_x + marker_radius // 3
            shadow_y = marker_y - marker_radius // 3
            pygame.draw.circle(surface, (50, 50, 80), (shadow_x, shadow_y), marker_radius * 0.8)
            
        # Draw time labels
        font = pygame.font.SysFont("Arial", 10)
        labels = ["12 AM", "6 AM", "12 PM", "6 PM", "12 AM"]
        positions = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for label, pos in zip(labels, positions):
            label_surf = font.render(label, True, (200, 200, 200))
            label_x = x + int(width * pos) - label_surf.get_width() // 2
            label_y = y + height + 2
            surface.blit(label_surf, (label_x, label_y))

# Singleton instance
_instance = None

def get_instance():
    """Get the global time system instance"""
    global _instance
    if _instance is None:
        _instance = TimeSystem()
    return _instance

# Integration with Adventure Screen
def apply_time_effects_to_adventure_screen(adventure_screen):
    """
    Apply time of day effects to the adventure screen
    
    Parameters:
    -----------
    adventure_screen : AdventureScreen
        The adventure screen to modify
    """
    time_system = get_instance()
    
    # Update background colors
    adventure_screen.sky_color = time_system.get_sky_color()
    adventure_screen.ground_color = time_system.get_ground_color()
    
    # Modify encounter rates
    adventure_screen.adventure.encounter_modifier = time_system.get_encounter_modifier()
    
    # Apply lighting effects
    adventure_screen.light_level = time_system.get_light_level()
