# creature_selector.py
# Creature selector screen for Dark Tamagotchi

import pygame
from tamagotchi.utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, WHITE, GRAY, DARK_GRAY, BLUE

class CreatureSelectorScreen:
    """Creature selector screen"""

    def __init__(self, screen, creatures, on_select=None, on_delete=None, on_back=None):
        """
        Initialize the creature selector screen

        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        creatures : list
            List of creatures to display
        on_select : function, optional
            Callback for selecting a creature
        on_delete : function, optional
            Callback for deleting a creature
        on_back : function, optional
            Callback for going back
        """
        self.screen = screen
        self.creatures = creatures
        self.on_select = on_select
        self.on_delete = on_delete
        self.on_back = on_back

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        # Title
        self.title = pygame.font.SysFont("Arial", 36).render("Select a Creature", True, (255, 255, 255))

        # Creature list (simplified for now)
        self.list_rects = []

        # Create rectangles for each creature
        y = 100
        for creature in self.creatures:
            rect = pygame.Rect(50, y, WINDOW_WIDTH - 100, 50)
            self.list_rects.append(rect)
            y += 60

        # Back button
        self.back_button = pygame.Rect(50, WINDOW_HEIGHT - 70, 100, 40)

    def set_creatures(self, creatures):
        """
        Update the list of creatures

        Parameters:
        -----------
        creatures : list
            New list of creatures
        """
        self.creatures = creatures
        self.init_ui()

    def handle_events(self, events):
        """
        Handle pygame events

        Parameters:
        -----------
        events : list
            List of pygame events
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if a creature was clicked
                pos = event.pos

                for i, rect in enumerate(self.list_rects):
                    if rect.collidepoint(pos):
                        if i < len(self.creatures):
                            if self.on_select:
                                self.on_select(self.creatures[i])

                # Check if back button was clicked
                if self.back_button.collidepoint(pos):
                    if self.on_back:
                        self.on_back()

    def update(self, dt):
        """
        Update the selector screen

        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        pass

    def draw(self):
        """Draw the selector screen"""
        # Fill background
        self.screen.fill((0, 0, 0))

        # Draw title
        self.screen.blit(self.title, (WINDOW_WIDTH // 2 - self.title.get_width() // 2, 30))

        # Draw creature list
        for i, rect in enumerate(self.list_rects):
            if i < len(self.creatures):
                creature = self.creatures[i]

                # Draw rectangle
                pygame.draw.rect(self.screen, (50, 50, 50), rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

                # Draw creature info
                name = pygame.font.SysFont("Arial", 24).render(
                    f"{creature.creature_type} (Level {creature.level})", True, (255, 255, 255))
                self.screen.blit(name, (rect.x + 20, rect.y + 10))

                # Draw select button
                select_btn = pygame.Rect(rect.right - 180, rect.y + 10, 80, 30)
                pygame.draw.rect(self.screen, (0, 100, 200), select_btn)
                select_text = pygame.font.SysFont("Arial", 16).render("Select", True, (255, 255, 255))
                self.screen.blit(select_text, (select_btn.x + 15, select_btn.y + 5))

                # Draw delete button
                delete_btn = pygame.Rect(rect.right - 90, rect.y + 10, 80, 30)
                pygame.draw.rect(self.screen, (200, 50, 50), delete_btn)
                delete_text = pygame.font.SysFont("Arial", 16).render("Delete", True, (255, 255, 255))
                self.screen.blit(delete_text, (delete_btn.x + 15, delete_btn.y + 5))

        # Draw back button
        pygame.draw.rect(self.screen, (100, 100, 100), self.back_button)
        pygame.draw.rect(self.screen, (255, 255, 255), self.back_button, 2)
        back_text = pygame.font.SysFont("Arial", 20).render("Back", True, (255, 255, 255))
        self.screen.blit(back_text, (self.back_button.x + 25, self.back_button.y + 10))