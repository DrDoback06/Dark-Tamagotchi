# game_engine.py
# Main game engine for Dark Tamagotchi

import pygame
import time
import random
from config import WINDOW_WIDTH, WINDOW_HEIGHT, AUTOSAVE_INTERVAL
from src.game_systems.adventure_system import Adventure
from ui.adventure_screen import AdventureScreen

# Import UI screens
from ui.main_menu import MainMenu
from ui.creature_screen import CreatureScreen
from ui.battle_screen import BattleScreen
from ui.adventure_screen import AdventureScreen
from ui.creature_selector import CreatureSelectorScreen
from ui.inventory_screen import InventoryScreen
from ui.ability_screen import AbilityScreen
from ui.graveyard_screen import GraveyardScreen

# Import game systems
from src.game_systems.creatures import Creature
from src.game_systems.battle_system import Battle
from src.game_systems.adventure_system import Adventure
from src.game_systems.database import CharacterManager
from src.game_systems.network import NetworkClient

class GameEngine:
    """Main game engine that controls game flow and screens"""
    
    def __init__(self, screen):
        """
        Initialize the game engine
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        """
        self.screen = screen
        self.running = True
        self.state = "MAIN_MENU"
        self.current_creature = None
        self.char_manager = CharacterManager()
        
        # Initialize screens
        self.init_screens()
        
        # Networking
        self.network_client = None
        
        # Autosave timer
        self.last_autosave_time = time.time()
        
        # Load music and sounds
        self.init_audio()
        
    def init_screens(self):
        """Initialize all game screens"""
        # Main menu
        self.main_menu = MainMenu(
            self.screen,
            on_new_game=self.start_new_game,
            on_load_game=self.start_creature_selector,
            on_settings=self.show_settings,
            on_quit=self.quit_game
        )
        
        # Creature screen will be initialized when needed
        self.creature_screen = None
        
        # Battle screen will be initialized when needed
        self.battle_screen = None
        
        # Adventure screen will be initialized when needed
        self.adventure_screen = None
        
        # Creature selector screen will be initialized when needed
        self.selector_screen = None
        
        # Other screens
        self.inventory_screen = None
        self.abilities_screen = None
        self.settings_screen = None
        self.graveyard_screen = None
        self.evolution_screen = None
        self.multiplayer_screen = None
        self.multiplayer_lobby = None
        
    def init_audio(self):
        """Initialize music and sound effects"""
        pygame.mixer.init()
        
    def start_new_game(self):
        """Start a new game with a new creature"""
        # Create a new creature
        self.current_creature = Creature()
        
        # Add to character manager
        self.char_manager.add_creature(self.current_creature)
        
        # Initialize creature screen
        self.create_creature_screen()
        
        # Change state
        self.state = "CREATURE_SCREEN"
        
    def start_creature_selector(self):
        """Show the creature selector screen"""
        # Get all creatures
        creatures = self.char_manager.get_all_creatures()
        
        # Initialize selector screen
        self.selector_screen = CreatureSelectorScreen(
            self.screen,
            creatures,
            on_select=self.select_creature,
            on_delete=self.delete_creature,
            on_back=self.return_to_main_menu
        )
        
        # Change state
        self.state = "SELECTOR_SCREEN"
        
    def select_creature(self, creature):
        """
        Select a creature from the selector
        
        Parameters:
        -----------
        creature : Creature
            The selected creature
        """
        self.current_creature = creature
        
        # Initialize creature screen
        self.create_creature_screen()
        
        # Change state
        self.state = "CREATURE_SCREEN"
        
    def delete_creature(self, creature):
        """
        Delete a creature
        
        Parameters:
        -----------
        creature : Creature
            The creature to delete
        """
        self.char_manager.remove_creature(creature)
        
        # Refresh selector screen
        creatures = self.char_manager.get_all_creatures()
        self.selector_screen.set_creatures(creatures)
        
    def create_creature_screen(self):
        """Create the creature screen with the current creature"""
        self.creature_screen = CreatureScreen(
            self.screen,
            self.current_creature,
            on_battle=self.start_battle,
            on_adventure=self.start_adventure,
            on_main_menu=self.return_to_main_menu,
            on_show_inventory=self.show_inventory,
            on_show_abilities=self.show_abilities
        )
        
    def start_battle(self):
        """Start a battle with a random creature"""
        # Create a enemy creature similar to player's level
        enemy_creature = Creature()
        
        # Scale enemy to player's level
        level_diff = random.randint(-2, 2)
        target_level = max(1, self.current_creature.level + level_diff)
        
        # Level up the enemy to target level
        for _ in range(1, target_level):
            enemy_creature.level_up()
            
        # Create battle
        battle = Battle(self.current_creature, enemy_creature)
        
        # Initialize battle screen
        self.battle_screen = BattleScreen(
            self.screen,
            battle,
            on_exit_battle=self.return_to_creature_screen
        )
        
        # Change state
        self.state = "BATTLE_SCREEN"
        
    def start_adventure(self):
        """Start an adventure"""
        # Initialize adventure screen
        self.adventure_screen = AdventureScreen(
            self.screen,
            self.current_creature,
            on_complete=self.adventure_complete,
            on_battle=self.adventure_battle,
            on_main_menu=self.return_to_creature_screen
        )
        
        # Change state
        self.state = "ADVENTURE_SCREEN"
        
    def adventure_complete(self):
        """Handle adventure completion"""
        # Save game
        self.char_manager.save_all()
        
    def adventure_battle(self, enemy_creature):
        """
        Start a battle from adventure
        
        Parameters:
        -----------
        enemy_creature : Creature
            The enemy creature to battle
        """
        # Create battle
        battle = Battle(self.current_creature, enemy_creature)
        
        # Initialize battle screen
        self.battle_screen = BattleScreen(
            self.screen,
            battle,
            on_exit_battle=self.return_to_adventure
        )
        
        # Change state
        self.state = "BATTLE_SCREEN"
        
    def return_to_adventure(self):
        """Return to adventure after battle"""
        # Change state
        self.state = "ADVENTURE_SCREEN"
        
    def show_inventory(self):
        """Show inventory screen"""
        # Not implemented yet
        pass
        
    def show_abilities(self):
        """Show abilities screen"""
        # Not implemented yet
        pass
        
    def show_settings(self):
        """Show settings screen"""
        # Not implemented yet
        pass
        
    def start_multiplayer(self):
        """Start multiplayer mode"""
        # Initialize network client
        if not self.network_client:
            self.network_client = NetworkClient()
            
            try:
                self.network_client.connect()
            except Exception as e:
                print(f"[GameEngine] Failed to connect to server: {e}")
                return
                
        # Initialize lobby screen
        # This would be implemented when we have the multiplayer lobby screen
        pass
        
    def return_to_creature_screen(self):
        """Return to creature screen"""
        # Re-create creature screen with updated data
        self.create_creature_screen()
        
        # Change state
        self.state = "CREATURE_SCREEN"
        
    def return_to_main_menu(self):
        """Return to main menu"""
        # Save game
        self.char_manager.save_all()
        
        # Change state
        self.state = "MAIN_MENU"
        
    def quit_game(self):
        """Quit the game"""
        # Save game
        self.char_manager.save_all()
        
        # Set running to False to exit game loop
        self.running = False
        
    def check_autosave(self):
        """Check if it's time to autosave"""
        current_time = time.time()
        if current_time - self.last_autosave_time >= AUTOSAVE_INTERVAL:
            self.char_manager.save_all()
            self.last_autosave_time = current_time
            
    def handle_events(self, events):
        """
        Handle pygame events
        
        Parameters:
        -----------
        events : list
            List of pygame events
        """
        # Process events based on current state
        if self.state == "MAIN_MENU":
            self.main_menu.handle_events(events)
            
        elif self.state == "CREATURE_SCREEN":
            self.creature_screen.handle_events(events)
            
        elif self.state == "BATTLE_SCREEN":
            self.battle_screen.handle_events(events)
            
        elif self.state == "ADVENTURE_SCREEN":
            self.adventure_screen.handle_events(events)
            
        elif self.state == "SELECTOR_SCREEN":
            self.selector_screen.handle_events(events)
            
        # Add more states as needed
        
    def update(self, dt):
        """
        Update game logic
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        # Check for autosave
        self.check_autosave()
        
        # Update based on current state
        if self.state == "MAIN_MENU":
            self.main_menu.update(dt)
            
        elif self.state == "CREATURE_SCREEN":
            # Update creature needs and age
            if self.current_creature and self.current_creature.is_alive:
                self.current_creature.update_needs(dt)
                self.current_creature.update_age(dt)
                
            # Update screen
            self.creature_screen.update(dt)
            
        elif self.state == "BATTLE_SCREEN":
            self.battle_screen.update(dt)
            
        elif self.state == "ADVENTURE_SCREEN":
            self.adventure_screen.update(dt)
            
        elif self.state == "SELECTOR_SCREEN":
            self.selector_screen.update(dt)
            
        # Add more states as needed
        
    def draw(self):
        """Draw the current screen"""
        # Draw based on current state
        if self.state == "MAIN_MENU":
            self.main_menu.draw(current_creature=self.current_creature)
            
        elif self.state == "CREATURE_SCREEN":
            self.creature_screen.draw()
            
        elif self.state == "BATTLE_SCREEN":
            self.battle_screen.draw()
            
        elif self.state == "ADVENTURE_SCREEN":
            self.adventure_screen.draw()
            
        elif self.state == "SELECTOR_SCREEN":
            self.selector_screen.draw()
            
        # Add more states as needed
            
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
