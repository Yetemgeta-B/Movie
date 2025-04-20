import os
import json
from pathlib import Path
import customtkinter as ctk

# Table formatting settings (moved from config.py)
MOVIE_TABLE_INDEX = 2  # The movie table is the 2nd table in document (index starts at 1)
SERIES_TABLE_INDEX = 1  # The series table is the 1st table in document

# Column indices for movie table (0-based)
MOVIE_COLUMNS = {
    "NO": 0,
    "NAME": 1,
    "TIME_DURATION": 2,
    "GENRE": 3,
    "WATCH_DATE": 4,
    "RELEASE_DATE": 5,
    "RATE": 6,
    "IMDB_RATING": 7,
    "RT_RATING": 8
}

# Column indices for series table (0-based)
SERIES_COLUMNS = {
    "NO": 0,
    "NAME": 1,
    "SEASON": 2,
    "EPISODE": 3,
    "GENRE": 4,
    "STARTING_DATE": 5,
    "FINISHING_DATE": 6,
    "FIRST_EPI_DATE": 7,
    "RATE": 8,
    "IMDB_RATING": 9,
    "RT_RATING": 10,
    "FINISHED": 11
}

class SettingsHandler:
    """Handles all application settings and configuration management"""
    
    def __init__(self):
        """Initialize settings handler with default values"""
        self.config_file = 'config.json'
        
        # Default settings
        self.default_settings = {
            "TMDB_API_KEY": "",
            "OMDB_API_KEY": "",
            "WORD_DOC_PATH": "",
            "APPEARANCE_MODE": "System",
            "COLOR_THEME": "blue",
            "MOVIE_TABLE_INDEX": MOVIE_TABLE_INDEX,
            "SERIES_TABLE_INDEX": SERIES_TABLE_INDEX,
            "OFFLINE_MODE": False,
            "OFFLINE_CACHE_SIZE": 200  # Number of items to cache
        }
        
        # Load settings from file or use defaults
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from config file or create with defaults if not exists"""
        try:
            # Try to load from JSON file first
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            
            # Fall back to legacy config.py if exists
            elif os.path.exists('config.py'):
                settings = self.default_settings.copy()
                # Import values from config.py
                try:
                    from config import TMDB_API_KEY, OMDB_API_KEY, WORD_DOC_PATH
                    settings["TMDB_API_KEY"] = TMDB_API_KEY
                    settings["OMDB_API_KEY"] = OMDB_API_KEY
                    settings["WORD_DOC_PATH"] = WORD_DOC_PATH
                except ImportError:
                    pass
                
                # Save to new format
                self.save_settings(settings)
                return settings
            
            # Create new config with defaults
            else:
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings=None):
        """Save settings to config file"""
        if settings is None:
            settings = self.settings
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
            self.settings = settings
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a setting value by key"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and save to file"""
        self.settings[key] = value
        return self.save_settings()
    
    def set_multiple(self, settings_dict):
        """Update multiple settings at once and save"""
        self.settings.update(settings_dict)
        return self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def get_appearance_mode(self):
        """Get the current appearance mode"""
        return self.get("APPEARANCE_MODE", "System")
    
    def set_appearance_mode(self, mode):
        """Set the appearance mode and apply it"""
        if mode in ["System", "Dark", "Light"]:
            self.set("APPEARANCE_MODE", mode)
            ctk.set_appearance_mode(mode)
            return True
        return False
    
    def get_color_theme(self):
        """Get the current color theme"""
        return self.get("COLOR_THEME", "blue")
    
    def set_color_theme(self, theme):
        """Set the color theme and apply it"""
        if theme in ["blue", "green", "dark-blue"]:
            self.set("COLOR_THEME", theme)
            ctk.set_default_color_theme(theme)
            return True
        return False
    
    def get_movie_table_index(self):
        """Get the movie table index"""
        return self.get("MOVIE_TABLE_INDEX", MOVIE_TABLE_INDEX)
    
    def get_series_table_index(self):
        """Get the series table index"""
        return self.get("SERIES_TABLE_INDEX", SERIES_TABLE_INDEX)
    
    def get_movie_columns(self):
        """Get the movie columns mapping"""
        return MOVIE_COLUMNS
    
    def get_series_columns(self):
        """Get the series columns mapping"""
        return SERIES_COLUMNS
    
    def is_offline_mode(self):
        """Check if offline mode is enabled"""
        return self.get("OFFLINE_MODE", False)
    
    def set_offline_mode(self, enabled):
        """Enable or disable offline mode"""
        return self.set("OFFLINE_MODE", bool(enabled))
    
    def get_offline_cache_size(self):
        """Get the maximum number of items to cache for offline mode"""
        return self.get("OFFLINE_CACHE_SIZE", 200)
    
    def set_offline_cache_size(self, size):
        """Set the maximum number of items to cache for offline mode"""
        if isinstance(size, int) and size > 0:
            return self.set("OFFLINE_CACHE_SIZE", size)
        return False

# Create a singleton instance
settings = SettingsHandler() 