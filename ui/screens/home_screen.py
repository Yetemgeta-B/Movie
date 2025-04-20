import customtkinter as ctk
from typing import List, Dict, Callable, Optional
import random
from pathlib import Path
import datetime

class HomeScreen(ctk.CTkFrame):
    """
    Home screen with navigation buttons to all sections of the app.
    """
    
    def __init__(self, master, on_navigate=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Store the navigate callback
        self.on_navigate = on_navigate
        
        # Configure frame
        self.configure(fg_color="transparent")
        
        # Create UI elements
        self._create_ui()
    
    def _create_ui(self):
        """Create the home screen UI"""
        # Main container with some padding
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with app name
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 30))
        
        self.app_logo = ctk.CTkLabel(
            self.header_frame,
            text="🎬",  # Movie emoji
            font=ctk.CTkFont(size=48)
        )
        self.app_logo.pack(pady=(20, 0))
        
        self.app_title = ctk.CTkLabel(
            self.header_frame,
            text="Movie & Series Tracker",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.app_title.pack(pady=(5, 0))
        
        self.app_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="Keep track of all your favorite content",
            font=ctk.CTkFont(size=16),
            text_color="gray70"
        )
        self.app_subtitle.pack(pady=(5, 0))
        
        # Card grid for navigation buttons
        self.card_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.card_grid.pack(fill="both", expand=True)
        
        # Configure grid with 2 columns
        self.card_grid.columnconfigure(0, weight=1)
        self.card_grid.columnconfigure(1, weight=1)
        
        # Create navigation cards
        self._create_nav_card(
            row=0, column=0,
            title="Movies",
            description="Browse, search, and add movies to your collection",
            icon="🎥",
            screen_name="movies"
        )
        
        self._create_nav_card(
            row=0, column=1,
            title="TV Series",
            description="Track TV shows, seasons, and episodes you're watching",
            icon="📺",
            screen_name="series"
        )
        
        self._create_nav_card(
            row=1, column=0,
            title="Document View",
            description="View and edit Word document tables directly",
            icon="📄",
            screen_name="document"
        )
        
        self._create_nav_card(
            row=1, column=1,
            title="Settings",
            description="Configure app preferences and file locations",
            icon="⚙️",
            screen_name="settings"
        )
        
        # Footer with version info
        self.footer = ctk.CTkLabel(
            self.main_container,
            text="Version 1.2.0",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.footer.pack(pady=(30, 0), anchor="se")
    
    def _create_nav_card(self, row, column, title, description, icon, screen_name):
        """Create a navigation card with an icon, title, and description"""
        # Card frame
        card = ctk.CTkFrame(self.card_grid, corner_radius=15)
        card.grid(row=row, column=column, padx=15, pady=15, sticky="nsew")
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=48)
        )
        icon_label.pack(pady=(20, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color="gray70",
            wraplength=200
        )
        desc_label.pack(pady=(0, 15), padx=15)
        
        # Button
        button = ctk.CTkButton(
            card,
            text=f"Open {title}",
            height=40,
            fg_color=("#4a86e8", "#2d5bb9"),  # Match app theme
            hover_color=("#3a76d8", "#1d4ba9"),  # Darker blue for hover
            command=lambda: self._navigate_to_screen(screen_name)
        )
        button.pack(padx=15, pady=(0, 20), fill="x")
    
    def _navigate_to_screen(self, screen_name):
        """Navigate to the selected screen"""
        if self.on_navigate:
            self.on_navigate(screen_name)
    
    def _get_movie_count(self):
        """Get the count of movies in the data file"""
        try:
            data_file = Path("data/movies.json")
            if data_file.exists():
                import json
                with open(data_file, "r") as f:
                    movies_data = json.load(f)
                return len(movies_data)
            return 0
        except Exception:
            return 0
    
    def _get_series_count(self):
        """Get the count of series in the data file"""
        try:
            data_file = Path("data/series.json")
            if data_file.exists():
                import json
                with open(data_file, "r") as f:
                    series_data = json.load(f)
                return len(series_data)
            return 0
        except Exception:
            return 0 