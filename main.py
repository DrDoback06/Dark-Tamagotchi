# main.py
# Entry point for Dark Tamagotchi game

import pygame
import sys
import os
from tamagotchi.utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, FRAME_RATE, GAME_TITLE
# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
from tamagotchi.game import GameEngine

def main():
    # Initialize pygame
    pygame.init()

    # Create game window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)

    # Create game clock
    clock = pygame.time.Clock()

    # Create game engine
    engine = GameEngine(screen)

    # Main game loop
    while engine.running:
        # Calculate delta time
        dt = clock.tick(FRAME_RATE)

        # Get events
        events = pygame.event.get()

        # Handle quit event
        for event in events:
            if event.type == pygame.QUIT:
                engine.quit_game()
                pygame.quit()
                sys.exit()

        # Handle game events
        engine.handle_events(events)

        # Update game logic
        engine.update(dt)

        # Draw the game
        engine.draw()

        # Update the display
        pygame.display.flip()

    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()