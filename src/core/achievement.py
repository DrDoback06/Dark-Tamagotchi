# achievement_system.py
# Achievement system for Dark Tamagotchi

import json
import os
import time
import pygame

class Achievement:
    """
    Represents a single game achievement
    """
    
    def __init__(self, id, name, description, icon=None, hidden=False, 
                 category="general", points=10, prerequisites=None):
        """
        Initialize an achievement
        
        Parameters:
        -----------
        id : str
            Unique identifier for the achievement
        name : str
            Display name of the achievement
        description : str
            Description of how to earn the achievement
        icon : str, optional
            Path to the icon image
        hidden : bool, optional
            If True, the achievement is hidden until unlocked
        category : str, optional
            Category of the achievement
        points : int, optional
            Point value of the achievement
        prerequisites : list, optional
            List of achievement IDs that must be unlocked first
        """
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.hidden = hidden
        self.category = category
        self.points = points
        self.prerequisites = prerequisites or []
        
        # Runtime state
        self.unlocked = False
        self.unlock_time = None
        self.progress = 0
        self.progress_max = 1
        self.just_unlocked = False  # For notifications
        
    def unlock(self):
        """Unlock the achievement"""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_time = time.time()
            self.progress = self.progress_max
            self.just_unlocked = True
            return True
        return False
        
    def update_progress(self, value):
        """
        Update progress toward unlocking the achievement
        
        Parameters:
        -----------
        value : int
            New progress value
            
        Returns:
        --------
        bool
            True if the achievement was unlocked, False otherwise
        """
        if self.unlocked:
            return False
            
        old_progress = self.progress
        self.progress = min(value, self.progress_max)
        
        if self.progress >= self.progress_max and old_progress < self.progress_max:
            return self.unlock()
            
        return False
        
    def increment_progress(self, amount=1):
        """
        Increment progress toward unlocking the achievement
        
        Parameters:
        -----------
        amount : int, optional
            Amount to increment by
            
        Returns:
        --------
        bool
            True if the achievement was unlocked, False otherwise
        """
        return self.update_progress(self.progress + amount)
        
    def get_progress_percentage(self):
        """
        Get progress as a percentage
        
        Returns:
        --------
        float
            Progress percentage (0-100)
        """
        if self.progress_max == 0:
            return 100.0
        return (self.progress / self.progress_max) * 100.0
        
    def has_prerequisites_met(self, unlocked_ids):
        """
        Check if all prerequisites are met
        
        Parameters:
        -----------
        unlocked_ids : set
            Set of unlocked achievement IDs
            
        Returns:
        --------
        bool
            True if all prerequisites are met, False otherwise
        """
        for prereq in self.prerequisites:
            if prereq not in unlocked_ids:
                return False
        return True
        
    def to_dict(self):
        """
        Convert achievement to dictionary for saving
        
        Returns:
        --------
        dict
            Dictionary representation of the achievement
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "hidden": self.hidden,
            "category": self.category,
            "points": self.points,
            "prerequisites": self.prerequisites,
            "unlocked": self.unlocked,
            "unlock_time": self.unlock_time,
            "progress": self.progress,
            "progress_max": self.progress_max
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create an achievement from a dictionary
        
        Parameters:
        -----------
        data : dict
            Dictionary data
            
        Returns:
        --------
        Achievement
            Achievement instance
        """
        achievement = cls(
            data["id"],
            data["name"],
            data["description"],
            data.get("icon"),
            data.get("hidden", False),
            data.get("category", "general"),
            data.get("points", 10),
            data.get("prerequisites", [])
        )
        
        achievement.unlocked = data.get("unlocked", False)
        achievement.unlock_time = data.get("unlock_time")
        achievement.progress = data.get("progress", 0)
        achievement.progress_max = data.get("progress_max", 1)
        
        return achievement
        
    def __repr__(self):
        return f"Achievement({self.id}, {self.name}, {self.unlocked})"

class AchievementManager:
    """
    Manages achievements, tracks progress, and handles notifications
    """
    
    def __init__(self):
        """Initialize the achievement manager"""
        self.achievements = {}
        self.categories = {}
        self.notifications = []
        self.notification_duration = 5.0  # seconds
        
        # UI elements
        self.font_large = None
        self.font_small = None
        self.popup_surface = None
        
        # Load achievements
        self.load_achievements()
        self.load_progress()
        
    def load_achievements(self):
        """Load achievement definitions"""
        try:
            if not os.path.exists("achievements"):
                os.makedirs("achievements")
                self._create_default_achievements()
                
            # Load achievement definitions
            with open("achievements/definitions.json", "r") as f:
                definitions = json.load(f)
                
            # Process achievements
            for category, category_data in definitions.items():
                self.categories[category] = category_data.get("name", category)
                
                for achievement_data in category_data.get("achievements", []):
                    achievement = Achievement(
                        achievement_data["id"],
                        achievement_data["name"],
                        achievement_data["description"],
                        achievement_data.get("icon"),
                        achievement_data.get("hidden", False),
                        category,
                        achievement_data.get("points", 10),
                        achievement_data.get("prerequisites", [])
                    )
                    
                    if "progress_max" in achievement_data:
                        achievement.progress_max = achievement_data["progress_max"]
                        
                    self.achievements[achievement.id] = achievement
                    
            print(f"Loaded {len(self.achievements)} achievements")
        except Exception as e:
            print(f"Error loading achievements: {e}")
            self._create_default_achievements()
            
    def _create_default_achievements(self):
        """Create default achievement definitions"""
        # Creature achievements
        creature_achievements = [
            {
                "id": "first_creature",
                "name": "First Steps",
                "description": "Create your first creature",
                "points": 5
            },
            {
                "id": "level10",
                "name": "Growth Spurt",
                "description": "Reach level 10 with any creature",
                "points": 10
            },
            {
                "id": "level25",
                "name": "Impressive Growth",
                "description": "Reach level 25 with any creature",
                "points": 20,
                "prerequisites": ["level10"]
            },
            {
                "id": "level50",
                "name": "Master Trainer",
                "description": "Reach level 50 with any creature",
                "points": 30,
                "prerequisites": ["level25"]
            },
            {
                "id": "first_evolution",
                "name": "Evolving Bond",
                "description": "Evolve a creature for the first time",
                "points": 15
            },
            {
                "id": "all_evolutions",
                "name": "Evolutionary Mastery",
                "description": "Discover all evolution paths for a creature type",
                "points": 50,
                "hidden": True,
                "prerequisites": ["first_evolution"]
            },
            {
                "id": "collect_5_creatures",
                "name": "Creature Collector",
                "description": "Collect 5 different creatures",
                "points": 20,
                "progress_max": 5
            }
        ]
        
        # Battle achievements
        battle_achievements = [
            {
                "id": "first_battle",
                "name": "First Victory",
                "description": "Win your first battle",
                "points": 10
            },
            {
                "id": "win_10_battles",
                "name": "Battle Hardened",
                "description": "Win 10 battles",
                "points": 20,
                "progress_max": 10,
                "prerequisites": ["first_battle"]
            },
            {
                "id": "win_50_battles",
                "name": "Battle Master",
                "description": "Win 50 battles",
                "points": 30,
                "progress_max": 50,
                "prerequisites": ["win_10_battles"]
            },
            {
                "id": "perfect_victory",
                "name": "Flawless Victory",
                "description": "Win a battle without taking damage",
                "points": 20,
                "hidden": True
            },
            {
                "id": "comeback_kid",
                "name": "Comeback Kid",
                "description": "Win a battle with less than 10% HP remaining",
                "points": 25,
                "hidden": True
            }
        ]
        
        # Adventure achievements
        adventure_achievements = [
            {
                "id": "first_adventure",
                "name": "Adventurer",
                "description": "Complete your first adventure",
                "points": 10
            },
            {
                "id": "complete_5_adventures",
                "name": "Explorer",
                "description": "Complete 5 adventures",
                "points": 20,
                "progress_max": 5,
                "prerequisites": ["first_adventure"]
            },
            {
                "id": "complete_20_adventures",
                "name": "Veteran Explorer",
                "description": "Complete 20 adventures",
                "points": 30,
                "progress_max": 20,
                "prerequisites": ["complete_5_adventures"]
            },
            {
                "id": "find_rare_item",
                "name": "Treasure Hunter",
                "description": "Find a rare item during an adventure",
                "points": 20,
                "hidden": True
            },
            {
                "id": "night_adventurer",
                "name": "Night Crawler",
                "description": "Complete an adventure that started during night time",
                "points": 15,
                "hidden": True
            }
        ]
        
        # Collection achievements
        collection_achievements = [
            {
                "id": "first_item",
                "name": "Collector",
                "description": "Collect your first item",
                "points": 5
            },
            {
                "id": "collect_10_items",
                "name": "Hoarder",
                "description": "Collect 10 different items",
                "points": 15,
                "progress_max": 10,
                "prerequisites": ["first_item"]
            },
            {
                "id": "collect_all_food",
                "name": "Gourmet",
                "description": "Collect all types of food",
                "points": 30,
                "hidden": True
            },
            {
                "id": "collect_all_abilities",
                "name": "Skill Master",
                "description": "Discover all abilities for a creature type",
                "points": 40,
                "hidden": True
            }
        ]
        
        # Create the definitions file
        definitions = {
            "creature": {
                "name": "Creature Mastery",
                "achievements": creature_achievements
            },
            "battle": {
                "name": "Battle Prowess",
                "achievements": battle_achievements
            },
            "adventure": {
                "name": "Adventure",
                "achievements": adventure_achievements
            },
            "collection": {
                "name": "Collection",
                "achievements": collection_achievements
            }
        }
        
        try:
            with open("achievements/definitions.json", "w") as f:
                json.dump(definitions, f, indent=4)
                
            print("Created default achievement definitions")
            
            # Load these achievements
            for category, category_data in definitions.items():
                self.categories[category] = category_data.get("name", category)
                
                for achievement_data in category_data.get("achievements", []):
                    achievement = Achievement(
                        achievement_data["id"],
                        achievement_data["name"],
                        achievement_data["description"],
                        achievement_data.get("icon"),
                        achievement_data.get("hidden", False),
                        category,
                        achievement_data.get("points", 10),
                        achievement_data.get("prerequisites", [])
                    )
                    
                    if "progress_max" in achievement_data:
                        achievement.progress_max = achievement_data["progress_max"]
                        
                    self.achievements[achievement.id] = achievement
        except Exception as e:
            print(f"Error creating default achievements: {e}")
            
    def load_progress(self):
        """Load achievement progress"""
        try:
            if os.path.exists("achievements/progress.json"):
                with open("achievements/progress.json", "r") as f:
                    progress = json.load(f)
                    
                for achievement_id, data in progress.items():
                    if achievement_id in self.achievements:
                        achievement = self.achievements[achievement_id]
                        achievement.unlocked = data.get("unlocked", False)
                        achievement.unlock_time = data.get("unlock_time")
                        achievement.progress = data.get("progress", 0)
                        
            print("Loaded achievement progress")
        except Exception as e:
            print(f"Error loading achievement progress: {e}")
            
    def save_progress(self):
        """Save achievement progress"""
        try:
            progress = {}
            for achievement_id, achievement in self.achievements.items():
                progress[achievement_id] = {
                    "unlocked": achievement.unlocked,
                    "unlock_time": achievement.unlock_time,
                    "progress": achievement.progress
                }
                
            # Ensure directory exists
            if not os.path.exists("achievements"):
                os.makedirs("achievements")
                
            with open("achievements/progress.json", "w") as f:
                json.dump(progress, f, indent=4)
                
            print("Saved achievement progress")
            return True
        except Exception as e:
            print(f"Error saving achievement progress: {e}")
            return False
            
    def unlock_achievement(self, achievement_id):
        """
        Unlock an achievement
        
        Parameters:
        -----------
        achievement_id : str
            ID of the achievement to unlock
            
        Returns:
        --------
        bool
            True if the achievement was unlocked, False if already unlocked or not found
        """
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            if achievement.unlock():
                self._add_notification(achievement)
                self.save_progress()
                return True
        return False
        
    def update_achievement_progress(self, achievement_id, value):
        """
        Update progress toward an achievement
        
        Parameters:
        -----------
        achievement_id : str
            ID of the achievement
        value : int
            New progress value
            
        Returns:
        --------
        bool
            True if the achievement was updated or unlocked, False otherwise
        """
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            old_progress = achievement.progress
            
            if achievement.update_progress(value):
                # Achievement unlocked
                self._add_notification(achievement)
                self.save_progress()
                return True
            elif old_progress != achievement.progress:
                # Progress updated but not unlocked
                self.save_progress()
                return True
                
        return False
        
    def increment_achievement_progress(self, achievement_id, amount=1):
        """
        Increment progress toward an achievement
        
        Parameters:
        -----------
        achievement_id : str
            ID of the achievement
        amount : int, optional
            Amount to increment by
            
        Returns:
        --------
        bool
            True if the achievement was updated or unlocked, False otherwise
        """
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            return self.update_achievement_progress(achievement_id, achievement.progress + amount)
        return False
        
    def _add_notification(self, achievement):
        """
        Add an achievement notification
        
        Parameters:
        -----------
        achievement : Achievement
            Achievement that was unlocked
        """
        self.notifications.append({
            "achievement": achievement,
            "time": self.notification_duration,
            "alpha": 255
        })
        
    def update(self, dt):
        """
        Update the achievement system
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        dt_sec = dt / 1000.0
        
        # Update notifications
        for notification in list(self.notifications):
            notification["time"] -= dt_sec
            
            # Fade out the notification at the end
            if notification["time"] < 1.0:
                notification["alpha"] = int(255 * notification["time"])
                
            if notification["time"] <= 0:
                self.notifications.remove(notification)
                
        # Reset just_unlocked flags
        for achievement in self.achievements.values():
            if achievement.just_unlocked:
                achievement.just_unlocked = False
                
    def draw_notifications(self, surface):
        """
        Draw achievement notifications
        
        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
        """
        if not self.notifications:
            return
            
        # Initialize fonts if needed
        if self.font_large is None:
            self.font_large = pygame.font.SysFont("Arial", 20)
            self.font_small = pygame.font.SysFont("Arial", 16)
            
        # Draw each notification
        y_offset = 20
        for notification in self.notifications:
            achievement = notification["achievement"]
            alpha = notification["alpha"]
            
            # Create notification surface if needed
            if self.popup_surface is None:
                self.popup_surface = pygame.Surface((300, 80), pygame.SRCALPHA)
                
            # Clear the surface
            self.popup_surface.fill((0, 0, 0, 0))
            
            # Draw background
            pygame.draw.rect(self.popup_surface, (50, 50, 50, alpha), (0, 0, 300, 80), border_radius=10)
            pygame.draw.rect(self.popup_surface, (100, 100, 200, alpha), (0, 0, 300, 80), width=2, border_radius=10)
            
            # Draw achievement unlocked text
            title_text = self.font_large.render("Achievement Unlocked!", True, (255, 255, 100, alpha))
            self.popup_surface.blit(title_text, (10, 10))
            
            # Draw achievement name
            name_text = self.font_large.render(achievement.name, True, (255, 255, 255, alpha))
            self.popup_surface.blit(name_text, (10, 35))
            
            # Draw achievement description
            desc_text = self.font_small.render(achievement.description, True, (200, 200, 200, alpha))
            self.popup_surface.blit(desc_text, (10, 55))
            
            # Draw to main surface
            surface.blit(self.popup_surface, (surface.get_width() - 320, y_offset))
            y_offset += 100
            
    def get_total_points(self):
        """
        Get the total achievement points earned
        
        Returns:
        --------
        int
            Total points earned
        """
        return sum(achievement.points for achievement in self.achievements.values() if achievement.unlocked)
        
    def get_unlocked_achievements(self):
        """
        Get list of unlocked achievements
        
        Returns:
        --------
        list
            List of unlocked Achievement objects
        """
        return [a for a in self.achievements.values() if a.unlocked]
        
    def get_available_achievements(self):
        """
        Get list of achievements that can be progressed
        
        Returns:
        --------
        list
            List of available Achievement objects
        """
        unlocked_ids = {a.id for a in self.achievements.values() if a.unlocked}
        return [a for a in self.achievements.values() 
                if not a.unlocked and a.has_prerequisites_met(unlocked_ids) and not a.hidden]
                
    def get_achievement_by_id(self, achievement_id):
        """
        Get an achievement by ID
        
        Parameters:
        -----------
        achievement_id : str
            ID of the achievement
            
        Returns:
        --------
        Achievement or None
            Achievement object, or None if not found
        """
        return self.achievements.get(achievement_id)
        
    def get_category_achievements(self, category):
        """
        Get achievements in a category
        
        Parameters:
        -----------
        category : str
            Category name
            
        Returns:
        --------
        list
            List of Achievement objects in the category
        """
        return [a for a in self.achievements.values() if a.category == category]
        
    def get_progress_percentage(self):
        """
        Get overall achievement completion percentage
        
        Returns:
        --------
        float
            Percentage of achievements unlocked (0-100)
        """
        total = len(self.achievements)
        if total == 0:
            return 0.0
            
        unlocked = len(self.get_unlocked_achievements())
        return (unlocked / total) * 100.0
        
    def check_creature_achievements(self, creature):
        """
        Check for creature-related achievements
        
        Parameters:
        -----------
        creature : Creature
            The creature to check
        """
        # Level achievements
        if creature.level >= 10:
            self.unlock_achievement("level10")
            
        if creature.level >= 25:
            self.unlock_achievement("level25")
            
        if creature.level >= 50:
            self.unlock_achievement("level50")
            
    def check_evolution_achievement(self, creature, is_first_evolution):
        """
        Check for evolution-related achievements
        
        Parameters:
        -----------
        creature : Creature
            The creature that evolved
        is_first_evolution : bool
            Whether this is the first evolution ever
        """
        if is_first_evolution:
            self.unlock_achievement("first_evolution")
            
    def check_battle_achievements(self, battle_result):
        """
        Check for battle-related achievements
        
        Parameters:
        -----------
        battle_result : dict
            Battle result data
        """
        if battle_result["winner"] == "player":
            # First battle victory
            self.unlock_achievement("first_battle")
            
            # Track battle wins
            self.increment_achievement_progress("win_10_battles")
            self.increment_achievement_progress("win_50_battles")
            
            # Perfect victory
            if battle_result["player_hp_percent"] == 100:
                self.unlock_achievement("perfect_victory")
                
            # Comeback victory
            if battle_result["player_hp_percent"] <= 10:
                self.unlock_achievement("comeback_kid")
                
    def check_adventure_achievements(self, adventure_result):
        """
        Check for adventure-related achievements
        
        Parameters:
        -----------
        adventure_result : dict
            Adventure result data
        """
        # First adventure completion
        self.unlock_achievement("first_adventure")
        
        # Track adventure completions
        self.increment_achievement_progress("complete_5_adventures")
        self.increment_achievement_progress("complete_20_adventures")
        
        # Night adventurer
        if adventure_result.get("started_at_night", False):
            self.unlock_achievement("night_adventurer")
            
    def check_item_achievements(self, item, is_first_item):
        """
        Check for item-related achievements
        
        Parameters:
        -----------
        item : Item
            The item that was found
        is_first_item : bool
            Whether this is the first item ever found
        """
        if is_first_item:
            self.unlock_achievement("first_item")
            
        # Track item collection
        self.increment_achievement_progress("collect_10_items")
        
        # Rare item achievement
        if item.rarity == "rare":
            self.unlock_achievement("find_rare_item")
            
    def check_creature_collection(self, creature_count, creature_types):
        """
        Check for creature collection achievements
        
        Parameters:
        -----------
        creature_count : int
            Number of creatures collected
        creature_types : set
            Set of collected creature types
        """
        # First creature
        if creature_count >= 1:
            self.unlock_achievement("first_creature")
            
        # Creature collector
        self.update_achievement_progress("collect_5_creatures", len(creature_types))

# Singleton instance
_instance = None

def get_instance():
    """Get the global achievement manager instance"""
    global _instance
    if _instance is None:
        _instance = AchievementManager()
    return _instance

# Achievement screen
class AchievementScreen:
    """Screen to display and track achievements"""
    
    def __init__(self, screen, on_back=None):
        """
        Initialize the achievement screen
        
        Parameters:
        -----------
        screen : pygame.Surface
            The game screen surface
        on_back : function, optional
            Callback for back button
        """
        self.screen = screen
        self.on_back = on_back
        self.achievement_manager = get_instance()
        
        # Initialize fonts
        pygame.freetype.init()
        self.font_large = pygame.freetype.SysFont('Arial', 32)
        self.font_medium = pygame.freetype.SysFont('Arial', 24)
        self.font_small = pygame.freetype.SysFont('Arial', 16)
        
        # Create background
        self.background = pygame.Surface((screen.get_width(), screen.get_height()))
        self.background.fill((0, 0, 0))
        
        # UI elements
        self.category_buttons = []
        self.back_button = None
        self.selected_category = None
        self.achievement_list = []
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Title
        self.title = TextBox(
            screen_width // 2,
            30,
            0,
            0,
            "Achievements",
            None,
            (255, 255, 255),
            32,
            "center",
            "middle"
        )
        
        # Achievement points
        total_points = self.achievement_manager.get_total_points()
        unlocked_count = len(self.achievement_manager.get_unlocked_achievements())
        total_count = len(self.achievement_manager.achievements)
        
        self.points_text = TextBox(
            screen_width // 2,
            70,
            0,
            0,
            f"Points: {total_points} | Unlocked: {unlocked_count}/{total_count}",
            None,
            (200, 200, 100),
            20,
            "center",
            "middle"
        )
        
        # Category buttons
        button_width = 150
        button_height = 40
        button_spacing = 20
        categories = list(self.achievement_manager.categories.items())
        total_width = len(categories) * button_width + (len(categories) - 1) * button_spacing
        start_x = (screen_width - total_width) // 2
        
        self.category_buttons = []
        for i, (category_id, category_name) in enumerate(categories):
            button_x = start_x + i * (button_width + button_spacing)
            button = Button(
                button_x,
                120,
                button_width,
                button_height,
                category_name,
                lambda c=category_id: self.select_category(c),
                (50, 50, 50),
                (100, 100, 200),
                (255, 255, 255),
                16
            )
            self.category_buttons.append(button)
            
        # Select first category by default
        if categories:
            self.selected_category = categories[0][0]
            self.category_buttons[0].bg_color = (100, 100, 200)
            
        # Update achievement list
        self.update_achievement_list()
        
        # Back button
        self.back_button = Button(
            screen_width // 2 - 50,
            screen_height - 60,
            100,
            40,
            "Back",
            self.on_back_click,
            (50, 50, 50),
            (200, 50, 50),
            (255, 255, 255),
            20
        )
        
    def update_achievement_list(self):
        """Update the list of achievements based on selected category"""
        if not self.selected_category:
            self.achievement_list = []
            return
            
        # Get achievements in the selected category
        self.achievement_list = self.achievement_manager.get_category_achievements(self.selected_category)
        
        # Show unlocked achievements first, then available achievements
        unlocked = [a for a in self.achievement_list if a.unlocked]
        available = [a for a in self.achievement_list if not a.unlocked and not a.hidden 
                     and a.has_prerequisites_met({a.id for a in unlocked})]
        hidden = [a for a in self.achievement_list if not a.unlocked and a.hidden]
        
        self.achievement_list = unlocked + available + hidden
        
        # Reset scroll
        self.scroll_offset = 0
        self.max_scroll = max(0, len(self.achievement_list) * 100 - 350)
        
    def select_category(self, category_id):
        """
        Select a category of achievements
        
        Parameters:
        -----------
        category_id : str
            ID of the category to select
        """
        if category_id != self.selected_category:
            self.selected_category = category_id
            
            # Update button colors
            for button in self.category_buttons:
                if button.text == self.achievement_manager.categories.get(category_id, category_id):
                    button.bg_color = (100, 100, 200)
                else:
                    button.bg_color = (50, 50, 50)
                    
            # Update achievement list
            self.update_achievement_list()
            
    def on_back_click(self):
        """Handle back button click"""
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
        for event in events:
            # Handle buttons
            for button in self.category_buttons:
                button.handle_event(event)
                
            self.back_button.handle_event(event)
            
            # Scrolling
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 20)
                elif event.button == 5:  # Scroll down
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + 20)
                    
    def update(self, dt):
        """
        Update the achievement screen
        
        Parameters:
        -----------
        dt : int
            Time passed since last update in milliseconds
        """
        # Update achievement manager
        self.achievement_manager.update(dt)
        
        # Update points text
        total_points = self.achievement_manager.get_total_points()
        unlocked_count = len(self.achievement_manager.get_unlocked_achievements())
        total_count = len(self.achievement_manager.achievements)
        
        self.points_text.set_text(f"Points: {total_points} | Unlocked: {unlocked_count}/{total_count}")
        
    def draw(self):
        """Draw the achievement screen"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw title and points
        self.title.draw(self.screen)
        self.points_text.draw(self.screen)
        
        # Draw category buttons
        for button in self.category_buttons:
            button.draw(self.screen)
            
        # Draw achievement list
        list_x = 50
        list_y = 180 - self.scroll_offset
        list_width = screen_width - 100
        
        # Draw list background
        list_bg_rect = pygame.Rect(list_x, 180, list_width, 350)
        pygame.draw.rect(self.screen, (30, 30, 30), list_bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 100), list_bg_rect, width=2, border_radius=5)
        
        # Draw scrollbar if needed
        if self.max_scroll > 0:
            scrollbar_height = 350 * (350 / (self.max_scroll + 350))
            scrollbar_pos = 180 + (350 - scrollbar_height) * (self.scroll_offset / self.max_scroll)
            scrollbar_rect = pygame.Rect(screen_width - 30, scrollbar_pos, 10, scrollbar_height)
            pygame.draw.rect(self.screen, (100, 100, 100), scrollbar_rect, border_radius=5)
            
        # Set up a clip rect for the list area
        pygame.draw.rect(self.screen, (0, 0, 0, 0), list_bg_rect, 0)  # For defining clip area
        
        # Draw each achievement
        for i, achievement in enumerate(self.achievement_list):
            achievement_y = list_y + i * 100
            
            # Skip if out of view
            if achievement_y + 90 < 180 or achievement_y > 530:
                continue
                
            # Draw achievement
            self.draw_achievement(achievement, list_x, achievement_y, list_width)
            
        # Draw back button
        self.back_button.draw(self.screen)
        
        # Draw achievement notifications
        self.achievement_manager.draw_notifications(self.screen)
        
    def draw_achievement(self, achievement, x, y, width):
        """
        Draw a single achievement
        
        Parameters:
        -----------
        achievement : Achievement
            Achievement to draw
        x, y : int
            Position to draw at
        width : int
            Width of the achievement display
        """
        # Background
        if achievement.unlocked:
            bg_color = (50, 70, 50)
            border_color = (100, 200, 100)
        else:
            bg_color = (50, 50, 50)
            border_color = (100, 100, 100)
            
        achievement_rect = pygame.Rect(x, y, width, 90)
        pygame.draw.rect(self.screen, bg_color, achievement_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, achievement_rect, width=2, border_radius=5)
        
        # Achievement name
        if achievement.unlocked or not achievement.hidden:
            name_text = self.font_medium.render(achievement.name, True, (255, 255, 255))
        else:
            name_text = self.font_medium.render("???", True, (200, 200, 200))
            
        self.screen.blit(name_text[0], (x + 10, y + 10))
        
        # Description
        if achievement.unlocked or not achievement.hidden:
            desc_text = self.font_small.render(achievement.description, True, (200, 200, 200))
        else:
            desc_text = self.font_small.render("Achievement hidden until unlocked", True, (150, 150, 150))
            
        self.screen.blit(desc_text[0], (x + 10, y + 40))
        
        # Points and progress
        points_text = self.font_small.render(f"{achievement.points} pts", True, (255, 255, 100))
        self.screen.blit(points_text[0], (x + width - 80, y + 10))
        
        # Draw progress bar for multi-step achievements
        if achievement.progress_max > 1:
            progress_width = 200
            progress_height = 10
            progress_x = x + 10
            progress_y = y + 70
            
            # Background
            pygame.draw.rect(self.screen, (30, 30, 30), 
                            (progress_x, progress_y, progress_width, progress_height),
                            border_radius=5)
            
            # Fill
            progress_fill = (achievement.progress / achievement.progress_max) * progress_width
            if progress_fill > 0:
                pygame.draw.rect(self.screen, (100, 200, 100), 
                                (progress_x, progress_y, progress_fill, progress_height),
                                border_radius=5)
                
            # Progress text
            progress_text = self.font_small.render(
                f"{achievement.progress}/{achievement.progress_max}", 
                True, (200, 200, 200))
            self.screen.blit(progress_text[0], (progress_x + progress_width + 10, progress_y - 2))
            
        # Unlock time if unlocked
        if achievement.unlocked and achievement.unlock_time:
            from datetime import datetime
            unlock_date = datetime.fromtimestamp(achievement.unlock_time)
            time_text = self.font_small.render(
                f"Unlocked: {unlock_date.strftime('%Y-%m-%d %H:%M')}", 
                True, (150, 150, 150))
            self.screen.blit(time_text[0], (x + width - 200, y + 70))
