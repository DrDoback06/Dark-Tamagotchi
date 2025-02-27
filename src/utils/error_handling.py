# error_handling.py
# Error handling and logging system for Dark Tamagotchi

import logging
import os
import traceback
import sys
import time
import pygame

class GameLogger:
    """
    Logging system for game events and errors
    
    This class provides a consistent way to log events, warnings,
    and errors throughout the game, with both console output and
    file logging.
    """
    
    def __init__(self, log_file="game_log.txt", console_level=logging.INFO):
        """
        Initialize the logger
        
        Parameters:
        -----------
        log_file : str, optional
            Path to the log file
        console_level : int, optional
            Logging level for console output
        """
        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        # Create timestamped log file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(logs_dir, f"{timestamp}_{log_file}")
        
        # Configure logger
        self.logger = logging.getLogger("DarkTamagotchi")
        self.logger.setLevel(logging.DEBUG)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Last error message for UI display
        self.last_error = None
        self.error_time = 0
        self.error_display_duration = 5.0  # seconds
        
        self.logger.info("Logger initialized")
        
    def debug(self, message):
        """
        Log a debug message
        
        Parameters:
        -----------
        message : str
            Debug message to log
        """
        self.logger.debug(message)
        
    def info(self, message):
        """
        Log an info message
        
        Parameters:
        -----------
        message : str
            Info message to log
        """
        self.logger.info(message)
        
    def warning(self, message):
        """
        Log a warning message
        
        Parameters:
        -----------
        message : str
            Warning message to log
        """
        self.logger.warning(message)
        
    def error(self, message, exception=None):
        """
        Log an error message
        
        Parameters:
        -----------
        message : str
            Error message to log
        exception : Exception, optional
            Exception object if available
        """
        if exception:
            error_details = f"{message}: {str(exception)}\n{traceback.format_exc()}"
            self.logger.error(error_details)
        else:
            self.logger.error(message)
            
        # Store for UI display
        self.last_error = message
        self.error_time = time.time()
        
    def critical(self, message, exception=None):
        """
        Log a critical error message
        
        Parameters:
        -----------
        message : str
            Critical error message to log
        exception : Exception, optional
            Exception object if available
        """
        if exception:
            error_details = f"{message}: {str(exception)}\n{traceback.format_exc()}"
            self.logger.critical(error_details)
        else:
            self.logger.critical(message)
            
        # Store for UI display
        self.last_error = f"CRITICAL: {message}"
        self.error_time = time.time()
        
    def get_error_message(self):
        """
        Get the last error message if it's still within the display duration
        
        Returns:
        --------
        str or None
            The last error message, or None if no error or display time has passed
        """
        if self.last_error and time.time() - self.error_time < self.error_display_duration:
            return self.last_error
        return None
        
    def update(self):
        """Update the logger state"""
        # Clear old error messages
        if self.last_error and time.time() - self.error_time >= self.error_display_duration:
            self.last_error = None
            
    def draw_error(self, surface):
        """
        Draw the current error message on screen if any
        
        Parameters:
        -----------
        surface : pygame.Surface
            Surface to draw on
            
        Returns:
        --------
        bool
            True if an error was drawn, False otherwise
        """
        error_msg = self.get_error_message()
        if not error_msg:
            return False
            
        # Create error box
        error_width = min(600, surface.get_width() - 40)
        error_height = 60
        error_x = surface.get_width() // 2 - error_width // 2
        error_y = 20
        
        # Create semi-transparent background
        error_surface = pygame.Surface((error_width, error_height), pygame.SRCALPHA)
        error_surface.fill((200, 50, 50, 220))  # Semi-transparent red
        
        # Draw border
        pygame.draw.rect(error_surface, (255, 255, 255), error_surface.get_rect(), 2)
        
        # Draw text
        font = pygame.font.SysFont("Arial", 16)
        text = font.render(error_msg, True, (255, 255, 255))
        text_rect = text.get_rect(center=(error_width // 2, error_height // 2))
        error_surface.blit(text, text_rect)
        
        # Blit to main surface
        surface.blit(error_surface, (error_x, error_y))
        
        return True

# Safe file operations with error handling
def safe_load_json(file_path, default=None):
    """
    Safely load a JSON file with error handling
    
    Parameters:
    -----------
    file_path : str
        Path to the JSON file
    default : any, optional
        Default value to return if loading fails
        
    Returns:
    --------
    any
        The loaded JSON data, or default if loading failed
    """
    import json
    
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return default
            
        with open(file_path, "r") as f:
            data = json.load(f)
            
        logger.debug(f"Successfully loaded: {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}", e)
        
        # Try to create a backup of the corrupted file
        try:
            backup_path = f"{file_path}.backup"
            with open(file_path, "r") as src, open(backup_path, "w") as dst:
                dst.write(src.read())
            logger.info(f"Created backup of corrupted file: {backup_path}")
        except Exception as backup_error:
            logger.error(f"Failed to create backup of corrupted file", backup_error)
            
        return default
    except Exception as e:
        logger.error(f"Error loading {file_path}", e)
        return default

def safe_save_json(file_path, data):
    """
    Safely save data to a JSON file with error handling
    
    Parameters:
    -----------
    file_path : str
        Path to the JSON file
    data : any
        Data to save
        
    Returns:
    --------
    bool
        True if saving was successful, False otherwise
    """
    import json
    
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # First write to a temporary file
        temp_file = f"{file_path}.temp"
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=4)
            
        # If the write was successful, rename to the actual file
        if os.path.exists(file_path):
            # Create a backup first
            backup_file = f"{file_path}.backup"
            os.replace(file_path, backup_file)
            
        os.replace(temp_file, file_path)
        
        logger.debug(f"Successfully saved: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving {file_path}", e)
        return False

# Exception handler for unexpected errors
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Global exception handler for unhandled exceptions
    
    Parameters:
    -----------
    exc_type : type
        Exception type
    exc_value : Exception
        Exception instance
    exc_traceback : traceback
        Exception traceback
    """
    # Log the exception
    logger.critical(f"Unhandled {exc_type.__name__}", exc_value)
    
    # Show an error message
    error_msg = f"An unexpected error occurred: {exc_type.__name__}: {exc_value}"
    
    # Try to show an error dialog
    try:
        if pygame.get_init():
            # Try to show error on screen if pygame is running
            # This is a simple fallback - in reality, you'd want a proper error dialog
            error_font = pygame.font.SysFont("Arial", 20)
            error_text = error_font.render(error_msg, True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(400, 300))
            
            screen = pygame.display.get_surface()
            if screen:
                screen.fill((0, 0, 0))
                screen.blit(error_text, error_rect)
                pygame.display.flip()
                
                # Wait for user to acknowledge
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                            waiting = False
                            
        else:
            # If pygame isn't running, just print to console
            print(f"\nCRITICAL ERROR: {error_msg}")
            print("See log file for details.")
            
    except Exception:
        # If all else fails, just print to console
        print(f"\nCRITICAL ERROR: {error_msg}")
        print("See log file for details.")
        
    # Original exception handling
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

# Initialize the global logger
logger = GameLogger()

# Set up global exception handler
sys.excepthook = global_exception_handler
