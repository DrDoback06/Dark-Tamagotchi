# tutorial_system.py
# Tutorial system for Dark Tamagotchi

import pygame
import json
import os
from ui.ui_base import Button, TextBox
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, GRAY, DARK_GRAY, BLUE, YELLOW
)
from sound_manager import get_instance as get_sound_manager

class TutorialStep:
    """
    A single step in a tutorial sequence
    
    A tutorial step can highlight a UI element, display text,
    and wait for a specific player action before proceeding.
    """
    
    def __init__(self, text, target_rect=None, highlight=True, 
                 action_type=None, position="bottom", arrow=True):
        """
        Initialize a tutorial step
        
        Parameters:
        -----------
        text : str
            Text to display for this step
        target_rect : pygame.Rect or tuple, optional
            Rectangle to highlight (x, y, width, height)
        highlight : bool, optional
            Whether to highlight the target rectangle
        action_type : str, optional
            Type of action required to proceed: "click", "click_target", "key", or None
        position : str, optional
            Position of the text box: "top", "bottom", "left", "right", or "center"
        arrow : bool, optional
            Whether to draw an arrow pointing to the target
        """
        self.text = text
        
        # Convert target_rect to Rect if it's a tuple
        if isinstance(target_rect, tuple) and len(target_rect) == 4:
            self.target_rect = pygame.Rect(target_rect)
        else:
            self.target_rect = target_rect
            
        self.highlight = highlight
        self.action_type = action_type
        self.position = position
        self.arrow = arrow
        
        # UI components
        self.text_box = None
        self.next_button = None
        
        # State
        self.completed = False
        
    def initialize_ui(self, screen_rect):
        """
        Initialize UI components based on screen dimensions
        
        Parameters:
        -----------
        screen_rect : pygame.Rect
            Rectangle representing the screen dimensions
        """
        # Text box dimensions
        box_width = min(400, screen_rect.width - 40)
        box_height = 120
        
        # Determine text box position
        if self.target_rect:
            if self.position == "top":
                box_x = self.target_rect.centerx - box_width // 2
                box_y = self.target_rect.top - box_height - 20
            elif self.position == "bottom":
                box_x = self.target_rect.centerx - box_width // 2
                box_y = self.target_rect.bottom + 20
            elif self.position == "left":
                box_x = self.target_rect.left - box_width - 20
                box_y = self.target_rect.centery - box_height // 2
            elif self.position == "right":
                box_x = self.target_rect.right + 20
                box_y = self.target_rect.centery - box_height // 2
            else:  # center
                box_x = screen_rect.centerx - box_width // 2
                box_y = screen_rect.centery - box_height // 2
        else:
            # No target, center on screen
            box_x = screen_rect.centerx - box_width // 2
            box_y = screen_rect.bottom - box_height - 40  # Near bottom of screen
            
        # Keep text box on screen
        box_x = max(10, min(box_x, screen_rect.width - box_width - 10))
        box_y = max(10, min(box_y, screen_rect.height - box_height - 10))
        
        # Create text box
        self.text_box = TextBox(
            box_x,
            box_y,
            box_width,
            box_height,
            self.text,
            DARK_GRAY,
            WHITE,
            16,
            "left",
            "top",
            True,
            True
        )
        
        # Create next button if there's no specific action required
        if not self.action_type or self.action_type == "click":
            button_width = 80
            button_height = 30
            button_x = box_x + box_width - button_width - 10
            button_y = box_y + box_height - button_height - 10
            
            self.next_button = Button(
                button_x,
                button_y,
                button_width,
                button_height,
                "Next",
                None,  # This will be set by the tutorial manager
                DARK_GRAY,
                BLUE,
                WHITE,
                14
            )
            
    def handle_event(self, event):
        """
        Handle a pygame event
        
        Parameters:
        -----------
        event : pygame.event.Event
            The event to handle
            
        Returns:
        --------
        bool
            True if the step was completed by this event, False otherwise
        """
        if self.completed:
            return False
            
        if self.action_type == "click_target" and event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click was on target
            if self.target_rect and self.target_rect.collidepoint(event.pos):
                self.completed = True
                return True
                
        elif self.action_type == "key" and event.type == pygame.KEYDOWN:
            # Any key press completes the step
            self.completed = True
            return True
            
        elif self.next_button and event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click was on next button
            if self.next_button.rect.collidepoint(event.pos):
                self.completed = True
                return True
                
        # Pass event to the next button if it exists
        if self.next_button:
            self.next_button.handle_event(event)
            
        return False
        
    def draw(self, surface):
        """
        Draw the tutorial step
        
        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        # Draw highlight overlay
        if self.highlight and self.target_rect:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))  # Dark semi-transparent
            
            # Cut out a hole for the target rect
            if self.target_rect:
                pygame.draw.rect(overlay, (0, 0, 0, 0), self.target_rect)
                
                # Draw a highlight border around the target
                border_rect = self.target_rect.inflate(6, 6)
                pygame.draw.rect(overlay, YELLOW, border_rect, 3)
                
            # Draw the overlay
            surface.blit(overlay, (0, 0))
            
        # Draw text box
        if self.text_box:
            self.text_box.draw(surface)
            
        # Draw arrow pointing to target
        if self.arrow and self.target_rect and self.text_box:
            # Determine arrow points based on text box and target positions
            text_center = (
                self.text_box.x + self.text_box.width // 2,
                self.text_box.y + self.text_box.height // 2
            )
            target_center = (
                self.target_rect.centerx,
                self.target_rect.centery
            )
            
            # Calculate direction vector
            dx = target_center[0] - text_center[0]
            dy = target_center[1] - text_center[1]
            
            # Normalize and scale
            length = max(1, (dx**2 + dy**2)**0.5)
            dx = dx / length * 30
            dy = dy / length * 30
            
            # Calculate arrow points
            arrow_start = (
                text_center[0] + dx * 0.5,
                text_center[1] + dy * 0.5
            )
            arrow_end = (
                target_center[0] - dx * 0.5,
                target_center[1] - dy * 0.5
            )
            
            # Draw arrow line
            pygame.draw.line(surface, YELLOW, arrow_start, arrow_end, 2)
            
            # Draw arrowhead
            angle = math.atan2(-dy, -dx)  # Negative to point toward target
            arrow_size = 10
            arrowhead_points = [
                (arrow_end[0], arrow_end[1]),
                (arrow_end[0] + arrow_size * math.cos(angle + math.pi/6),
                 arrow_end[1] + arrow_size * math.sin(angle + math.pi/6)),
                (arrow_end[0] + arrow_size * math.cos(angle - math.pi/6),
                 arrow_end[1] + arrow_size * math.sin(angle - math.pi/6))
            ]
            pygame.draw.polygon(surface, YELLOW, arrowhead_points)
            
        # Draw next button
        if self.next_button:
            self.next_button.draw(surface)

class TutorialManager:
    """
    Manages tutorial sequences for different parts of the game
    
    The tutorial manager loads tutorial data from JSON files, tracks
    which tutorials have been completed, and handles displaying the
    appropriate tutorials at the right time.
    """
    
    def __init__(self):
        """Initialize the tutorial manager"""
        # Load tutorial data
        self.tutorials = {}
        self.completed_tutorials = set()
        self.active_tutorial = None
        self.current_step_index = 0
        self.sound_manager = get_sound_manager()
        
        # Load tutorial data and progress
        self.load_tutorials()
        self.load_progress()
        
    def load_tutorials(self):
        """Load tutorial data from JSON files"""
        try:
            # Ensure the tutorials directory exists
            if not os.path.exists("tutorials"):
                os.makedirs("tutorials")
                self._create_default_tutorials()
                
            # Load all tutorial files
            for filename in os.listdir("tutorials"):
                if filename.endswith(".json"):
                    tutorial_id = filename[:-5]  # Remove .json extension
                    file_path = os.path.join("tutorials", filename)
                    
                    with open(file_path, "r") as f:
                        tutorial_data = json.load(f)
                        
                    self.tutorials[tutorial_id] = tutorial_data
                    print(f"Loaded tutorial: {tutorial_id}")
        except Exception as e:
            print(f"Error loading tutorials: {e}")
            
    def _create_default_tutorials(self):
        """Create default tutorial files"""
        # Main tutorial
        main_tutorial = {
            "name": "Welcome to Dark Tamagotchi",
            "description": "Learn the basics of caring for your creature",
            "steps": [
                {
                    "text": "Welcome to Dark Tamagotchi! This tutorial will guide you through the basics of taking care of your creature.",
                    "position": "center"
                },
                {
                    "text": "This is your creature's home screen. From here, you can care for your creature, check its stats, and more.",
                    "position": "bottom"
                },
                {
                    "text": "These bars show your creature's health, energy, and hunger levels. Keep an eye on them!",
                    "target_rect": [50, 80, 300, 100],
                    "position": "right"
                },
                {
                    "text": "Use the Feed button to feed your creature when it's hungry.",
                    "target_rect": [100, 400, 120, 40],
                    "position": "top",
                    "action_type": "click_target"
                },
                {
                    "text": "Your creature's mood affects how it evolves. Try to keep it close to the ideal mood for best results.",
                    "target_rect": [50, 160, 300, 30],
                    "position": "right"
                },
                {
                    "text": "Remember to put your creature to sleep when its energy is low.",
                    "target_rect": [230, 400, 120, 40],
                    "position": "top"
                },
                {
                    "text": "That's the basics! Explore the other buttons to battle, adventure, and more. Have fun!",
                    "position": "center"
                }
            ]
        }
        
        # Battle tutorial
        battle_tutorial = {
            "name": "Battle Tutorial",
            "description": "Learn how to battle with your creature",
            "steps": [
                {
                    "text": "Welcome to battle mode! Here you'll face off against other creatures.",
                    "position": "center"
                },
                {
                    "text": "This is your creature's health and energy. Keep track of them during battle.",
                    "target_rect": [50, 70, 300, 100],
                    "position": "right"
                },
                {
                    "text": "This is your opponent's health. Reduce it to zero to win!",
                    "target_rect": [450, 70, 300, 30],
                    "position": "left"
                },
                {
                    "text": "Use your abilities to attack your opponent. Each ability costs energy and may have different effects.",
                    "target_rect": [300, 400, 300, 100],
                    "position": "top"
                },
                {
                    "text": "After you attack, your opponent will take their turn. Combat continues until one creature is defeated.",
                    "position": "center"
                },
                {
                    "text": "Winning battles earns XP, which helps your creature level up and evolve!",
                    "position": "center"
                }
            ]
        }
        
        # Adventure tutorial
        adventure_tutorial = {
            "name": "Adventure Tutorial",
            "description": "Learn how to go on adventures",
            "steps": [
                {
                    "text": "Welcome to adventure mode! Here you'll explore the world and find treasures.",
                    "position": "center"
                },
                {
                    "text": "This progress bar shows how far along you are in your adventure.",
                    "target_rect": [100, 80, 600, 20],
                    "position": "bottom"
                },
                {
                    "text": "Your creature will automatically walk through the world. Keep an eye out for encounters and items!",
                    "target_rect": [100, 300, 50, 50],
                    "position": "right"
                },
                {
                    "text": "You can rest during an adventure to recover energy and health.",
                    "target_rect": [650, 500, 120, 40],
                    "position": "left"
                },
                {
                    "text": "Complete adventures to earn rewards and XP!",
                    "position": "center"
                }
            ]
        }
        
        # Save tutorials to files
        try:
            with open(os.path.join("tutorials", "main.json"), "w") as f:
                json.dump(main_tutorial, f, indent=4)
                
            with open(os.path.join("tutorials", "battle.json"), "w") as f:
                json.dump(battle_tutorial, f, indent=4)
                
            with open(os.path.join("tutorials", "adventure.json"), "w") as f:
                json.dump(adventure_tutorial, f, indent=4)
                
            print("Created default tutorial files")
        except Exception as e:
            print(f"Error creating default tutorials: {e}")
            
    def load_progress(self):
        """Load tutorial progress from file"""
        try:
            if os.path.exists("tutorial_progress.json"):
                with open("tutorial_progress.json", "r") as f:
                    progress = json.load(f)
                    
                self.completed_tutorials = set(progress.get("completed", []))
        except Exception as e:
            print(f"Error loading tutorial progress: {e}")
            
    def save_progress(self):
        """Save tutorial progress to file"""
        try:
            progress = {
                "completed": list(self.completed_tutorials)
            }
            
            with open("tutorial_progress.json", "w") as f:
                json.dump(progress, f, indent=4)
        except Exception as e:
            print(f"Error saving tutorial progress: {e}")
            
    def start_tutorial(self, tutorial_id):
        """
        Start a tutorial sequence
        
        Parameters:
        -----------
        tutorial_id : str
            ID of the tutorial to start
            
        Returns:
        --------
        bool
            True if tutorial was started, False otherwise
        """
        # Check if tutorial exists
        if tutorial_id not in self.tutorials:
            print(f"Tutorial not found: {tutorial_id}")
            return False
            
        # Check if tutorial has already been completed
        if tutorial_id in self.completed_tutorials and tutorial_id != "main":
            print(f"Tutorial already completed: {tutorial_id}")
            return False
            
        # Get tutorial data
        tutorial_data = self.tutorials[tutorial_id]
        
        # Create steps
        steps = []
        for step_data in tutorial_data.get("steps", []):
            # Convert target_rect from list to tuple if it exists
            target_rect = None
            if "target_rect" in step_data:
                target_rect = tuple(step_data["target_rect"])
                
            step = TutorialStep(
                step_data.get("text", ""),
                target_rect,
                step_data.get("highlight", True),
                step_data.get("action_type"),
                step_data.get("position", "bottom"),
                step_data.get("arrow", True)
            )
            steps.append(step)
            
        # Set active tutorial
        self.active_tutorial = {
            "id": tutorial_id,
            "data": tutorial_data,
            "steps": steps,
            "current_step": 0
        }
        
        # Initialize the first step
        if steps:
            screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
            steps[0].initialize_ui(screen_rect)
            
            # Set the button callback for the first step
            if steps[0].next_button:
                steps[0].next_button.callback = lambda: self.advance_tutorial()
                
            # Play sound
            self.sound_manager.play_sound("ui/hover")
            
        return True
        
    def advance_tutorial(self):
        """
        Advance to the next step in the active tutorial
        
        Returns:
        --------
        bool
            True if advanced to next step, False if tutorial is complete
        """
        if not self.active_tutorial:
            return False
            
        # Mark current step as completed
        steps = self.active_tutorial["steps"]
        current_step = self.active_tutorial["current_step"]
        
        if current_step < len(steps):
            steps[current_step].completed = True
            
        # Move to next step
        current_step += 1
        self.active_tutorial["current_step"] = current_step
        
        # Check if tutorial is complete
        if current_step >= len(steps):
            # Mark tutorial as completed
            tutorial_id = self.active_tutorial["id"]
            self.completed_tutorials.add(tutorial_id)
            self.save_progress()
            
            # Clear active tutorial
            self.active_tutorial = None
            
            # Play sound
            self.sound_manager.play_sound("ui/click")
            
            return False
            
        # Initialize the next step
        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        steps[current_step].initialize_ui(screen_rect)
        
        # Set the button callback for the next step
        if steps[current_step].next_button:
            steps[current_step].next_button.callback = lambda: self.advance_tutorial()
            
        # Play sound
        self.sound_manager.play_sound("ui/click")
            
        return True
        
    def handle_events(self, events):
        """
        Handle pygame events
        
        Parameters:
        -----------
        events : list
            List of pygame events
            
        Returns:
        --------
        bool
            True if an event was handled by the tutorial, False otherwise
        """
        if not self.active_tutorial:
            return False
            
        # Get current step
        steps = self.active_tutorial["steps"]
        current_step = self.active_tutorial["current_step"]
        
        if current_step < len(steps):
            # Handle events for current step
            for event in events:
                if steps[current_step].handle_event(event):
                    # Step was completed, advance to next step
                    self.advance_tutorial()
                    return True
                    
        return False
        
    def draw(self, surface):
        """
        Draw the active tutorial step
        
        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
            
        Returns:
        --------
        bool
            True if a tutorial was drawn, False otherwise
        """
        if not self.active_tutorial:
            return False
            
        # Draw current step
        steps = self.active_tutorial["steps"]
        current_step = self.active_tutorial["current_step"]
        
        if current_step < len(steps):
            steps[current_step].draw(surface)
            return True
            
        return False
        
    def is_tutorial_active(self):
        """Check if a tutorial is active"""
        return self.active_tutorial is not None
        
    def is_tutorial_completed(self, tutorial_id):
        """Check if a tutorial has been completed"""
        return tutorial_id in self.completed_tutorials
        
    def reset_tutorial_progress(self):
        """Reset all tutorial progress"""
        self.completed_tutorials = set()
        self.save_progress()
        
    def mark_tutorial_completed(self, tutorial_id):
        """Mark a tutorial as completed without showing it"""
        if tutorial_id in self.tutorials:
            self.completed_tutorials.add(tutorial_id)
            self.save_progress()
            return True
        return False

# Initialize the global tutorial manager
_instance = None

def get_instance():
    """Get the global tutorial manager instance"""
    global _instance
    if _instance is None:
        _instance = TutorialManager()
    return _instance
