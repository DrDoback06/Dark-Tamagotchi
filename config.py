# config.py
# Configuration and constants for the Dark Tamagotchi game

# Game window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FRAME_RATE = 60
GAME_TITLE = "Dark Tamagotchi"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Font sizes
FONT_SMALL = 16
FONT_MEDIUM = 24
FONT_LARGE = 32
FONT_HUGE = 48

# Creature Stats
BASE_STATS = {
    "Skeleton": {"hp": 50, "attack": 10, "defense": 5, "speed": 7, "energy_max": 100, "ideal_mood": 40},
    "Fire Elemental": {"hp": 40, "attack": 12, "defense": 3, "speed": 10, "energy_max": 90, "ideal_mood": 70},
    "Knight": {"hp": 60, "attack": 8, "defense": 10, "speed": 5, "energy_max": 110, "ideal_mood": 80},
    "Goblin": {"hp": 45, "attack": 9, "defense": 6, "speed": 9, "energy_max": 80, "ideal_mood": 60},
    "Troll": {"hp": 70, "attack": 7, "defense": 12, "speed": 4, "energy_max": 120, "ideal_mood": 30},
}

# Stat growth ranges on level up
STAT_GROWTH = {
    "hp": (5, 10),
    "attack": (1, 3),
    "defense": (1, 3),
    "speed": (1, 2),
    "energy_max": (2, 5)
}

# Evolution system
EVOLUTION_THRESHOLDS = [10, 25, 45, 70, 100]  # Level thresholds for evolution stages
MAX_EVOLUTION_STAGE = 5
EVOLUTION_MULTIPLIER = 1.2  # Stat boost on evolution

# Evolution path quality thresholds
EVOLUTION_QUALITY = {
    "poor": {"wellness_threshold": 30, "mood_diff_threshold": 50},
    "good": {"wellness_threshold": 60, "mood_diff_threshold": 30},
    "best": {"wellness_threshold": 80, "mood_diff_threshold": 15}
}

# XP system
XP_MULTIPLIER = 100  # XP needed = level * XP_MULTIPLIER
XP_GAIN_PER_BATTLE = 50  # Base XP for winning a battle
XP_LOSS_PERCENT = 10  # Percentage of XP lost in defeat

# Ability Tier Chances
ABILITY_TIER_CHANCES = {1: 0.75, 2: 0.20, 3: 0.05}

# Creature aging (in seconds for testing, should be longer in production)
MAX_AGE = 3600  # 1 hour of game time (would be much longer in a real game)
AGE_FACTOR_PER_WELLNESS = 0.5  # Each percent of wellness extends life by 0.5%

# Needs system
HUNGER_RATE = 5  # Units per minute
ENERGY_CONSUMPTION_RATE = 3  # Units per minute when active
ENERGY_RECOVERY_RATE = 10  # Units per minute when sleeping
HUNGER_DAMAGE_THRESHOLD = 80  # When hunger exceeds this, health starts declining
MAX_FEEDS_PER_HOUR = 3

# Adventure mode
ADVENTURE_ENCOUNTER_CHANCE = 0.2  # Chance per step of encounter
ADVENTURE_ITEM_CHANCE = 0.15  # Chance per step of finding an item
ADVENTURE_STEP_DISTANCE = 5  # Pixels per step
ADVENTURE_COMPLETION_DISTANCE = 1000  # Distance needed to complete an adventure

# Battle system
MAX_BATTLE_TURNS = 20  # Maximum turns before a draw
STUN_CHANCE = 0.2  # Base chance for stun abilities

# Network settings
SERVER_HOST = 'localhost'
SERVER_PORT = 9999
SOCKET_TIMEOUT = 5.0  # Seconds

# Autosave settings
AUTOSAVE_INTERVAL = 60  # Seconds
