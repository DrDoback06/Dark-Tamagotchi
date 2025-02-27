# ui/evolution_screen.py
# Evolution screen for Dark Tamagotchi

import pygame
import pygame.freetype
import random
import math
from tamagotchi.ui.ui_base import Button, TextBox, Tooltip
from tamagotchi.utils.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, BLUE, YELLOW, PURPLE
)
from asset_manager import get_instance as get_asset_manager
from sound_manager import get_instance as get_sound_manager

class EvolutionScreen:
    """
    Evolution screen that shows a creature evolving with animation and effects.
    
    This screen is displayed when a creature evolves, showing the transformation
    from the old form to the new form with visual effects.
    """
    
    def __init__(self, screen, old_creature, new_creature, old_type, new_type, on_complete=None):
        """
        Initialize the evolution screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        old_creature : Creature
            The creature before evolution
        new_creature : Creature
            The creature after evolution (same instance, but updated)
        old_type : str
            The creature's type before evolution
        new_type : str
            The creature's type after evolution
        on_complete : function, optional
            Callback for when the evolution animation completes
        """
        self.screen = screen
        self.old_creature = old_creature
        self.new_creature = new_creature
        self.old_type = old_type
        self.new_type = new_type
        self.on_complete = on_complete
        
        # Get asset and sound managers
        self.asset_manager = get_asset_manager()
        self.sound_manager = get_sound_manager()
        
        # Play evolution music
        self.sound_manager.play_music("evolution", loops=0)
        
        # Initialize fonts
        pygame.freetype.init()
        self.font_large = pygame.freetype.SysFont('Arial', 48)
        self.font_medium = pygame.freetype.SysFont('Arial', 32)
        self.font_small = pygame.freetype.SysFont('Arial', 24)
        
        # Create background
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill(BLACK)
        
        # Animation variables
        self.animation_time = 0
        self.animation_duration = 5.0  # seconds
        self.particles = []
        self.light_intensity = 0
        self.animation_phase = 0  # 0: intro, 1: transform, 2: outro
        self.flash_alpha = 0
        
        # Get creature images
        self.old_image = self.asset_manager.get_image(f"creatures/{old_type.lower().replace(' ', '_')}", (200, 200))
        self.new_image = self.asset_manager.get_image(f"creatures/{new_type.lower().replace(' ', '_')}", (200, 200))
        
        # Generate particles
        self.generate_particles()
        
        # Continue button (initially hidden)
        self.continue_button = Button(
            WINDOW_WIDTH // 2 - 100,
            WINDOW_HEIGHT - 100,
            200,
            50,
            "Continue",
            self.on_continue_click,
            DARK_GRAY,
            GREEN,
            WHITE,
            24
        )
        self.show_continue = False
        
        # Create text boxes
        self.title = TextBox(
            WINDOW_WIDTH // 2,
            50,
            0,
            0,
            "Evolution!",
            None,
            YELLOW,
            48,
            "center",
            "middle"
        )
        
        self.old_name = TextBox(
            WINDOW_WIDTH // 4,
            WINDOW_HEIGHT // 2 + 120,
            0,
            0,
            old_type,
            None,
            WHITE,
            24,
            "center",
            "middle"
        )
        
        self.new_name = TextBox(
            3 * WINDOW_WIDTH // 4,
            WINDOW_HEIGHT // 2 + 120,
            0,
            0,
            new_type,
            None,
            YELLOW,
            24,
            "center",
            "middle"
        )
        
        # New stats info
        stats_diff = {
            "HP": new_creature.max_hp - old_creature.max_hp,
            "Attack": new_creature.attack - old_creature.attack,
            "Defense": new_creature.defense - old_creature.defense,
            "Speed": new_creature.speed - old_creature.speed
        }
        
        stats_text = "Stat Increases:\n"
        for stat, diff in stats_diff.items():
            stats_text += f"{stat}: +{diff}\n"
            
        self.stats_box = TextBox(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT - 180,
            300,
            100,
            stats_text,
            DARK_GRAY,
            GREEN,
            20,
            "center",
            "middle",
            True,
            False
        )
        
    def generate_particles(self):
        """Generate particle effects for the evolution animation"""
        self.particles = []
        
        # Create various particles
        for _ in range(100):
            particle = {
                "x": WINDOW_WIDTH // 2,
                "y": WINDOW_HEIGHT // 2,
                "speed": random.uniform(50, 200),
                "angle": random.uniform(0, 2 * math.pi),
                "size": random.uniform(2, 8),
                "color": random.choice([YELLOW, WHITE, PURPLE]),
                "decay": random.uniform(0.3, 1.0),
                "alpha": 255
            }
            self.particles.append(particle)
            
    def on_continue_click(self):
        """Handle continue button click"""
        if self.on_complete:
            # Play click sound
            self.sound_manager.play_sound("ui/click")
            self.on_complete()
            
    def handle_events(self, events):
        """
        Handle pygame events
        
        Parameters:
        -----------
        events : list
            List of pygame events
        """
        # Only process button events if it's visible
        if self.show_continue:
            for event in events:
                self.continue_button.handle_event(event)
        
    def update(self, dt):
        """
        Update the evolution animation
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        # Convert dt to seconds
        dt_sec = dt / 1000.0
        
        # Update animation time
        self.animation_time += dt_sec
        
        # Update animation phases
        if self.animation_time < 1.0:
            # Phase 0: Intro - glow builds up
            self.animation_phase = 0
            self.light_intensity = self.animation_time
            
        elif self.animation_time < 3.0:
            # Phase 1: Transform - flash and particle explosion
            self.animation_phase = 1
            
            # Flash effect
            phase_time = self.animation_time - 1.0
            if phase_time < 0.2:
                self.flash_alpha = int(phase_time / 0.2 * 255)
            elif phase_time < 0.5:
                self.flash_alpha = int(255 - (phase_time - 0.2) / 0.3 * 255)
                
            # Play transformation sound at the start of phase 1
            if self.animation_time >= 1.0 and self.animation_time < 1.1:
                self.sound_manager.play_sound("battle/victory")
                
        else:
            # Phase 2: Outro - show result and continue button
            self.animation_phase = 2
            self.light_intensity = max(0, 1.0 - (self.animation_time - 3.0) / 1.0)
            
            # Show continue button after animation
            if self.animation_time >= 4.0:
                self.show_continue = True
                
        # Update particles
        for particle in self.particles:
            # Only move particles during phase 1
            if self.animation_phase == 1:
                # Update position based on speed and angle
                particle["x"] += math.cos(particle["angle"]) * particle["speed"] * dt_sec
                particle["y"] += math.sin(particle["angle"]) * particle["speed"] * dt_sec
                
                # Decrease alpha for fade-out
                particle["alpha"] = max(0, particle["alpha"] - particle["decay"] * dt_sec * 100)
                
    def draw(self):
        """Draw the evolution screen with animation"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title
        self.title.draw(self.screen)
        
        # Draw creature images
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        
        # Calculate positions based on animation phase
        if self.animation_phase == 0:
            # Intro - creatures start from their positions
            old_x = WINDOW_WIDTH // 4
            new_x = 3 * WINDOW_WIDTH // 4
            old_alpha = 255
            new_alpha = 0
        elif self.animation_phase == 1:
            # Transform - old creature moves to center and fades out, new creature fades in
            progress = (self.animation_time - 1.0) / 2.0  # 0.0 to 1.0 during phase 1
            old_x = WINDOW_WIDTH // 4 + (center_x - WINDOW_WIDTH // 4) * progress
            new_x = center_x
            old_alpha = int(255 * (1.0 - progress))
            new_alpha = int(255 * progress)
        else:
            # Outro - new creature moves to its position
            progress = min(1.0, (self.animation_time - 3.0) / 1.0)  # 0.0 to 1.0 during phase 2
            old_x = center_x
            new_x = center_x + (3 * WINDOW_WIDTH // 4 - center_x) * progress
            old_alpha = 0
            new_alpha = 255
            
        # Create surfaces with alpha for fading
        if old_alpha > 0:
            old_surface = self.old_image.copy()
            if old_alpha < 255:
                old_surface.set_alpha(old_alpha)
            old_rect = old_surface.get_rect(center=(old_x, center_y))
            self.screen.blit(old_surface, old_rect)
            
        if new_alpha > 0:
            new_surface = self.new_image.copy()
            if new_alpha < 255:
                new_surface.set_alpha(new_alpha)
            new_rect = new_surface.get_rect(center=(new_x, center_y))
            self.screen.blit(new_surface, new_rect)
            
        # Draw creature names
        if self.animation_phase < 2:
            self.old_name.x = old_x
            self.old_name.draw(self.screen)
        
        if self.animation_phase > 0:
            self.new_name.x = new_x
            self.new_name.draw(self.screen)
            
        # Draw particles
        for particle in self.particles:
            if particle["alpha"] > 0:
                # Get color with alpha
                color = particle["color"][:3] + (int(particle["alpha"]),)
                
                # Draw particle
                pygame.draw.circle(
                    self.screen,
                    color,
                    (int(particle["x"]), int(particle["y"])),
                    int(particle["size"])
                )
                
        # Draw light glow effect
        if self.light_intensity > 0:
            # Create a surface for the glow effect
            glow_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            
            # Draw multiple circles with decreasing opacity for glow effect
            for radius in range(100, 10, -10):
                intensity = int(self.light_intensity * 100 * (1 - radius / 100))
                if intensity <= 0:
                    continue
                    
                color = (255, 255, 100, intensity)
                pygame.draw.circle(
                    glow_surface,
                    color,
                    (center_x, center_y),
                    radius
                )
                
            # Blit the glow surface
            self.screen.blit(glow_surface, (0, 0))
            
        # Draw full screen flash effect
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, self.flash_alpha))
            self.screen.blit(flash_surface, (0, 0))
            
        # Draw stats after evolution is complete
        if self.animation_phase == 2:
            self.stats_box.draw(self.screen)
            
        # Draw continue button if visible
        if self.show_continue:
            self.continue_button.draw(self.screen)
