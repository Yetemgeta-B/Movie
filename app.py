import customtkinter as ctk
import os
from pathlib import Path
import sys
import json
import shutil
import time

# Import settings handler
from settings_handler import settings

# Import screens
from ui.screens.home_screen import HomeScreen
from ui.screens.series_screen import SeriesScreen
from ui.screens.movies_screen import MoviesScreen
from redesigned_ui.document_view import DocumentViewScreen

# Set appearance mode and default color theme (now handled by settings handler)
ctk.set_appearance_mode(settings.get_appearance_mode())
ctk.set_default_color_theme(settings.get_color_theme())

class App(ctk.CTk):
    """Main application class with navigation between screens"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Movie and Series Tracker")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Configure grid for layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main content frame that takes the full window
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Content area (where screens will be displayed)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 70))
        
        # Create floating navbar at the bottom
        self.navbar_frame = ctk.CTkFrame(
            self.main_frame, 
            corner_radius=15,
            fg_color=("#e0e0e0", "#333333"),  # Light/Dark mode colors
            border_width=1,
            border_color=("#c0c0c0", "#555555")
        )
        self.navbar_frame.grid(row=0, column=0, sticky="s", padx=20, pady=10)
        
        # Create the floating navbar
        self._create_floating_navbar()
        
        # Initialize screens dictionary
        self.screens = {}
        
        # Create the screens (but don't display yet)
        self._create_screens()
        
        # Status bar for feedback messages
        self.status_bar = ctk.CTkLabel(
            self.main_frame,
            text="",
            height=30,
            corner_radius=8,
            fg_color=("gray85", "gray25"),
            text_color=("gray10", "gray90")
        )
        self.status_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 80))
        self.status_bar.grid_remove()  # Hide initially
        
        # Show the home screen by default
        self.show_screen("home")
    
    def _create_floating_navbar(self):
        """Create the floating navbar at the bottom of the screen"""
        # Configure grid for navbar items
        self.navbar_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Define navigation items (icon, text, screen_name)
        nav_items = [
            ("🏠", "Home", "home"),
            ("🎥", "Movies", "movies"),
            ("📺", "TV Series", "series"),
            ("📄", "Document", "document"),
            ("⚙️", "Settings", "settings")
        ]
        
        # Color themes for active/inactive buttons
        active_colors = {
            "fg_color": ("#4a86e8", "#2d5bb9"),  # Vibrant blue
            "text_color": ("#ffffff", "#ffffff"),
            "hover_color": ("#3a76d8", "#1d4ba9")
        }
        
        inactive_colors = {
            "fg_color": "transparent",
            "text_color": ("#555555", "#aaaaaa"),
            "hover_color": ("#e5e5e5", "#444444")
        }
        
        # Navigation buttons dictionary
        self.nav_buttons = {}
        
        # Create button for each nav item
        for idx, (icon, text, screen_name) in enumerate(nav_items):
            button = ctk.CTkButton(
                self.navbar_frame,
                corner_radius=10,
                height=40,
                width=120,
                text=f"{icon} {text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                **inactive_colors,
                command=lambda s=screen_name: self.show_screen(s)
            )
            button.grid(row=0, column=idx, padx=10, pady=10)
            self.nav_buttons[screen_name] = button
    
    def _create_screens(self):
        """Create all the application screens"""
        # Home Screen
        self.screens["home"] = HomeScreen(
            self.content_frame,
            on_navigate=self.show_screen
        )
        
        # Movies Screen
        self.screens["movies"] = MoviesScreen(
            self.content_frame
        )
        
        # Series Screen
        self.screens["series"] = SeriesScreen(
            self.content_frame
        )
        
        # Document View Screen
        self.screens["document"] = DocumentViewScreen(
            self.content_frame
        )
        
        # Settings Screen - Create a scrollable frame for all settings
        self.screens["settings"] = ctk.CTkFrame(self.content_frame)
        
        # Create a scrollable frame for all settings content
        settings_scroll = ctk.CTkScrollableFrame(
            self.screens["settings"],
            label_text="Settings",
            label_font=ctk.CTkFont(size=20, weight="bold"),
            corner_radius=10
        )
        settings_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Theme section
        theme_frame = ctk.CTkFrame(settings_scroll)
        theme_frame.pack(fill="x", padx=20, pady=20)
        
        theme_label = ctk.CTkLabel(
            theme_frame, 
            text="Theme",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        theme_label.pack(anchor="w", padx=10, pady=5)
        
        # Theme buttons
        theme_buttons_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        light_button = ctk.CTkButton(
            theme_buttons_frame,
            text="☀️ Light",
            command=lambda: self._change_appearance_mode("Light")
        )
        light_button.pack(side="left", padx=5)
        
        dark_button = ctk.CTkButton(
            theme_buttons_frame,
            text="🌙 Dark",
            command=lambda: self._change_appearance_mode("Dark")
        )
        dark_button.pack(side="left", padx=5)
        
        system_button = ctk.CTkButton(
            theme_buttons_frame,
            text="🖥️ System",
            command=lambda: self._change_appearance_mode("System")
        )
        system_button.pack(side="left", padx=5)
        
        # API Settings section
        api_frame = ctk.CTkFrame(settings_scroll)
        api_frame.pack(fill="x", padx=20, pady=20)
        
        api_label = ctk.CTkLabel(
            api_frame, 
            text="API Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        api_label.pack(anchor="w", padx=10, pady=5)
        
        # TMDB API Key
        tmdb_label = ctk.CTkLabel(api_frame, text="TMDB API Key:")
        tmdb_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Create StringVar to track changes
        self.tmdb_api_var = ctk.StringVar(value=settings.get("TMDB_API_KEY", ""))
        tmdb_entry = ctk.CTkEntry(api_frame, placeholder_text="Enter TMDB API key", textvariable=self.tmdb_api_var)
        tmdb_entry.pack(fill="x", padx=10, pady=(5, 10))
        
        # OMDB API Key
        omdb_label = ctk.CTkLabel(api_frame, text="OMDB API Key:")
        omdb_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Create StringVar to track changes
        self.omdb_api_var = ctk.StringVar(value=settings.get("OMDB_API_KEY", ""))
        omdb_entry = ctk.CTkEntry(api_frame, placeholder_text="Enter OMDB API key", textvariable=self.omdb_api_var)
        omdb_entry.pack(fill="x", padx=10, pady=(5, 10))
        
        # Save API keys button
        save_api_button = ctk.CTkButton(
            api_frame,
            text="Save API Keys",
            command=self._save_api_keys,
            width=120
        )
        save_api_button.pack(anchor="e", padx=10, pady=10)
        
        # Word document settings section
        word_frame = ctk.CTkFrame(settings_scroll)
        word_frame.pack(fill="x", padx=20, pady=20)
        
        word_label = ctk.CTkLabel(
            word_frame, 
            text="Word Document Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        word_label.pack(anchor="w", padx=10, pady=5)
        
        # Word document path
        word_path_label = ctk.CTkLabel(word_frame, text="Word Document Path:")
        word_path_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Create StringVar to track changes
        self.word_path_var = ctk.StringVar(value=settings.get("WORD_DOC_PATH", ""))
        word_path_entry = ctk.CTkEntry(word_frame, placeholder_text="Enter Word document path", textvariable=self.word_path_var)
        word_path_entry.pack(fill="x", padx=10, pady=(5, 10))
        
        # Browse button
        browse_button = ctk.CTkButton(
            word_frame,
            text="Browse...",
            command=self._browse_word_doc,
            width=120
        )
        browse_button.pack(anchor="e", padx=10, pady=10)
        
        # Desktop Shortcut section
        shortcut_frame = ctk.CTkFrame(settings_scroll)
        shortcut_frame.pack(fill="x", padx=20, pady=20)
        
        shortcut_label = ctk.CTkLabel(
            shortcut_frame, 
            text="Desktop Shortcut",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        shortcut_label.pack(anchor="w", padx=10, pady=5)
        
        # Create description
        shortcut_desc = ctk.CTkLabel(
            shortcut_frame,
            text="Create a shortcut on your desktop for quick access to the application.",
            justify="left"
        )
        shortcut_desc.pack(anchor="w", padx=10, pady=5)
        
        # Icon selection
        icon_label = ctk.CTkLabel(shortcut_frame, text="Shortcut Icon:")
        icon_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        icon_frame = ctk.CTkFrame(shortcut_frame, fg_color="transparent")
        icon_frame.pack(fill="x", padx=10, pady=5)
        
        # Available icons
        icon_options = ["🎬 Default", "🎞️ Film", "📺 TV", "📝 Document", "🎭 Drama", "🎮 Game"]
        self.selected_icon = ctk.StringVar(value=icon_options[0])
        
        for i, icon in enumerate(icon_options):
            icon_button = ctk.CTkButton(
                icon_frame,
                text=icon,
                width=60,
                height=40,
                command=lambda i=icon: self.selected_icon.set(i)
            )
            icon_button.pack(side="left", padx=5)
        
        # Custom icon
        custom_icon_frame = ctk.CTkFrame(shortcut_frame, fg_color="transparent")
        custom_icon_frame.pack(fill="x", padx=10, pady=5)
        
        self.custom_icon_path = ctk.StringVar(value="")
        custom_icon_entry = ctk.CTkEntry(
            custom_icon_frame, 
            placeholder_text="Custom icon path (.ico file)",
            textvariable=self.custom_icon_path,
            width=250
        )
        custom_icon_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        browse_icon_button = ctk.CTkButton(
            custom_icon_frame,
            text="Browse...",
            command=self._browse_icon,
            width=80
        )
        browse_icon_button.pack(side="right", padx=5)
        
        # Create shortcut button
        create_shortcut_button = ctk.CTkButton(
            shortcut_frame,
            text="Create Desktop Shortcut",
            command=self._create_desktop_shortcut,
            width=200,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        create_shortcut_button.pack(anchor="center", pady=15)
        
        # Offline Mode section
        offline_frame = ctk.CTkFrame(settings_scroll)
        offline_frame.pack(fill="x", padx=20, pady=20)
        
        offline_label = ctk.CTkLabel(
            offline_frame, 
            text="Offline Mode",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        offline_label.pack(anchor="w", padx=10, pady=5)
        
        # Create a description label
        offline_desc = ctk.CTkLabel(
            offline_frame,
            text="Offline mode allows you to use the app without internet connection.\nThe app will use cached data for movies and series.",
            justify="left"
        )
        offline_desc.pack(anchor="w", padx=10, pady=5)
        
        # Status message for offline mode
        self.offline_status = ctk.CTkLabel(
            offline_frame,
            text="",
            fg_color="transparent"
        )
        self.offline_status.pack(fill="x", padx=10, pady=5)
        
        # Offline mode switch
        self.offline_var = ctk.BooleanVar(value=settings.is_offline_mode())
        offline_switch = ctk.CTkSwitch(
            offline_frame,
            text="Enable Offline Mode",
            variable=self.offline_var,
            command=self._toggle_offline_mode
        )
        offline_switch.pack(anchor="w", padx=10, pady=10)
        
        # Cache size setting
        cache_label = ctk.CTkLabel(offline_frame, text="Cache Size (items):")
        cache_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        cache_frame = ctk.CTkFrame(offline_frame, fg_color="transparent")
        cache_frame.pack(fill="x", padx=10, pady=5)
        
        self.cache_size_var = ctk.StringVar(value=str(settings.get_offline_cache_size()))
        cache_entry = ctk.CTkEntry(cache_frame, width=100, textvariable=self.cache_size_var)
        cache_entry.pack(side="left", padx=5)
        
        cache_set_button = ctk.CTkButton(
            cache_frame,
            text="Set Cache Size",
            command=self._set_cache_size,
            width=120
        )
        cache_set_button.pack(side="left", padx=5)
        
        # Cache status message
        self.cache_status = ctk.CTkLabel(
            offline_frame,
            text="",
            fg_color="transparent"
        )
        self.cache_status.pack(fill="x", padx=10, pady=5)
        
        # Cache management buttons
        cache_buttons_frame = ctk.CTkFrame(offline_frame, fg_color="transparent")
        cache_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        clear_cache_button = ctk.CTkButton(
            cache_buttons_frame,
            text="Clear Cache",
            command=self._clear_cache,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        clear_cache_button.pack(side="left", padx=5)
        
        refresh_cache_button = ctk.CTkButton(
            cache_buttons_frame,
            text="Refresh Cache",
            command=self._refresh_cache
        )
        refresh_cache_button.pack(side="left", padx=5)
        
        # Data Export section
        export_frame = ctk.CTkFrame(settings_scroll)
        export_frame.pack(fill="x", padx=20, pady=20)
        
        export_label = ctk.CTkLabel(
            export_frame, 
            text="Data Management",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        export_label.pack(anchor="w", padx=10, pady=5)
        
        # Export buttons
        export_buttons_frame = ctk.CTkFrame(export_frame, fg_color="transparent")
        export_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        export_movies_button = ctk.CTkButton(
            export_buttons_frame,
            text="Export Movies to CSV",
            command=self._export_movies_to_csv,
            fg_color="#4a86e8",
            hover_color="#2d5bb9"
        )
        export_movies_button.pack(side="left", padx=5)
        
        export_series_button = ctk.CTkButton(
            export_buttons_frame,
            text="Export Series to CSV",
            command=self._export_series_to_csv,
            fg_color="#4a86e8",
            hover_color="#2d5bb9"
        )
        export_series_button.pack(side="left", padx=5)
        
        backup_button = ctk.CTkButton(
            export_frame,
            text="🔄 Backup Data",
            command=self._backup_data,
            fg_color="#4a86e8",
            hover_color="#2d5bb9"
        )
        backup_button.pack(anchor="w", padx=10, pady=10)
        
        # Export status label
        self.export_status = ctk.CTkLabel(
            export_frame,
            text="",
            fg_color="transparent"
        )
        self.export_status.pack(fill="x", padx=10, pady=5)
        
        # App version
        version_label = ctk.CTkLabel(
            settings_scroll,
            text="v1.2.0",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        )
        version_label.pack(pady=20)
    
    def show_screen(self, screen_name):
        """Show the specified screen and hide others"""
        # Hide all screens
        for screen in self.screens.values():
            screen.pack_forget()
        
        # Show the requested screen
        if screen_name in self.screens:
            self.screens[screen_name].pack(fill="both", expand=True)
            
            # Update navbar button states
            for name, button in self.nav_buttons.items():
                if name == screen_name:
                    button.configure(
                        fg_color=("#4a86e8", "#2d5bb9"),  # Vibrant blue
                        text_color=("#ffffff", "#ffffff"),
                        hover_color=("#3a76d8", "#1d4ba9")
                    )
                else:
                    button.configure(
                        fg_color="transparent",
                        text_color=("#555555", "#aaaaaa"),
                        hover_color=("#e5e5e5", "#444444")
                    )
    
    def _change_appearance_mode(self, new_mode):
        """Change the app's appearance mode"""
        settings.set_appearance_mode(new_mode)
        self.show_status(f"Theme changed to {new_mode} mode", "success")
    
    def _create_desktop_shortcut(self):
        """Create a desktop shortcut for the application"""
        # Get desktop path
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Get current script path
        script_path = os.path.abspath(__file__)
        app_dir = os.path.dirname(script_path)
        main_script = os.path.join(app_dir, "main.py")
        
        try:
            # For Windows: Create a proper .lnk shortcut using win32com
            import win32com.client
            
            shortcut_path = os.path.join(desktop_path, "Movie Tracker.lnk")
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            
            # Get the Python executable path
            python_exe = sys.executable  # Get the path to the Python executable
            
            # Set shortcut properties
            shortcut.TargetPath = python_exe
            shortcut.Arguments = f'"{main_script}"'
            shortcut.WorkingDirectory = app_dir
            
            # Handle icon selection
            icon_path = ""
            selected_icon = self.selected_icon.get()
            custom_path = self.custom_icon_path.get()
            
            # Custom icon path takes precedence if valid
            if custom_path and os.path.exists(custom_path) and custom_path.lower().endswith('.ico'):
                icon_path = custom_path
            else:
                # Create default icons directory if it doesn't exist
                icons_dir = os.path.join(app_dir, "ui", "assets", "icons")
                os.makedirs(icons_dir, exist_ok=True)
                
                # Map selected icon text to icon file
                icon_files = {
                    "🎬 Default": "default.ico",
                    "🎞️ Film": "film.ico",
                    "📺 TV": "tv.ico",
                    "📝 Document": "document.ico",
                    "🎭 Drama": "drama.ico",
                    "🎮 Game": "game.ico"
                }
                
                # Use default icon if selected icon is not in map
                icon_file = icon_files.get(selected_icon, "default.ico")
                icon_path = os.path.join(icons_dir, icon_file)
                
                # If icon doesn't exist, copy from resources or use Python's icon
                if not os.path.exists(icon_path):
                    # Try to find icon in resources
                    resource_icon = os.path.join(app_dir, "resources", "icons", icon_file)
                    if os.path.exists(resource_icon):
                        shutil.copy(resource_icon, icon_path)
                    else:
                        # Fallback to Python's icon
                        icon_path = f"{python_exe},0"
            
            # Set icon location
            if icon_path:
                shortcut.IconLocation = icon_path
            else:
                shortcut.IconLocation = f"{python_exe},0"
                
            shortcut.Description = "Movie and Series Tracker Application"
            
            # Save the shortcut
            shortcut.save()
            
            # Test if the shortcut was created
            if os.path.exists(shortcut_path):
                self.show_status("Desktop shortcut created successfully!", "success")
            else:
                self.show_status("Failed to create shortcut. The file was not created.", "error")
        
        except Exception as e:
            error_message = f"Error creating shortcut: {str(e)}"
            self.show_status(error_message, "error")
    
    def _save_api_keys(self):
        """Save the API keys using the settings handler"""
        try:
            # Get the values from the entry fields
            tmdb_key = self.tmdb_api_var.get().strip()
            omdb_key = self.omdb_api_var.get().strip()
            word_path = self.word_path_var.get().strip()
            
            # Save all settings at once
            settings.set_multiple({
                "TMDB_API_KEY": tmdb_key,
                "OMDB_API_KEY": omdb_key,
                "WORD_DOC_PATH": word_path
            })
            
            self.show_status("Settings saved successfully!", "success")
            return True
        except Exception as e:
            self.show_status(f"Error saving settings: {str(e)}", "error")
            return False
    
    def _browse_word_doc(self):
        """Browse for a Word document and update the path"""
        from tkinter import filedialog
        
        # Get the current file path or default to user's documents folder
        current_path = self.word_path_var.get()
        initial_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~/Documents")
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Word Document",
            initialdir=initial_dir,
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")]
        )
        
        # Update the entry field if a file was selected
        if file_path:
            self.word_path_var.set(file_path)
            # Save the path to settings
            settings.set("WORD_DOC_PATH", file_path)
            self.show_status(f"Document path updated: {os.path.basename(file_path)}", "success")
    
    def _toggle_offline_mode(self):
        """Toggle offline mode"""
        offline_enabled = self.offline_var.get()
        settings.set_offline_mode(offline_enabled)
        
        # Show status message in the offline frame
        status = "enabled" if offline_enabled else "disabled"
        status_color = ("#c3e6cb", "#285b2a") if offline_enabled else ("#f8d7da", "#691c22")
        self.offline_status.configure(
            text=f"Offline mode {status}. The change will take effect on restart.",
            fg_color=status_color
        )
        
        # Show global status message
        self.show_status(f"Offline mode {status}. Changes will apply on restart.", "info")
    
    def _set_cache_size(self):
        """Set the offline cache size"""
        try:
            cache_size = int(self.cache_size_var.get())
            if cache_size <= 0:
                raise ValueError("Cache size must be positive")
                
            settings.set_offline_cache_size(cache_size)
            
            # Show status message
            self.cache_status.configure(
                text=f"Cache size set to {cache_size} items.",
                fg_color=("#c3e6cb", "#285b2a")
            )
            
            self.show_status(f"Cache size set to {cache_size} items.", "success")
        except ValueError as e:
            self.cache_status.configure(
                text=f"Invalid cache size: {str(e)}",
                fg_color=("#f8d7da", "#691c22")
            )
            self.show_status(f"Invalid cache size: {str(e)}", "error")
    
    def _clear_cache(self):
        """Clear the offline cache"""
        try:
            # Create or clear the cache directory
            cache_dir = Path("data/cache")
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)
            
            # Show status message
            self.cache_status.configure(
                text="Cache cleared successfully.",
                fg_color=("#c3e6cb", "#285b2a")
            )
            
            self.show_status("Cache cleared successfully.", "success")
        except Exception as e:
            self.cache_status.configure(
                text=f"Error clearing cache: {str(e)}",
                fg_color=("#f8d7da", "#691c22")
            )
            self.show_status(f"Error clearing cache: {str(e)}", "error")
    
    def _refresh_cache(self):
        """Refresh the offline cache with latest data"""
        try:
            # Create the cache directory if it doesn't exist
            cache_dir = Path("data/cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Show message that this is a placeholder
            self.cache_status.configure(
                text="Cache refresh will be implemented in a future update.",
                fg_color=("#fff3cd", "#856404")
            )
            
            self.show_status("Cache refresh will be implemented in a future update.", "warning")
        except Exception as e:
            self.cache_status.configure(
                text=f"Error refreshing cache: {str(e)}",
                fg_color=("#f8d7da", "#691c22")
            )
            self.show_status(f"Error refreshing cache: {str(e)}", "error")
    
    def _export_movies_to_csv(self):
        """Export movies data to a CSV file"""
        try:
            from tkinter import filedialog
            import csv
            
            # Ask for a save location
            filepath = filedialog.asksaveasfilename(
                title="Save Movies CSV",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if not filepath:
                return
            
            # Read the movies data
            movies_data = []
            data_file = Path("data/movies.json")
            if data_file.exists():
                with open(data_file, "r") as f:
                    movies_data = json.load(f)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV headers
                fieldnames = ['title', 'year', 'watch_date', 'user_rating', 'director', 
                             'genres', 'runtime', 'release_date', 'imdb_rating', 'rt_rating',
                             'is_rewatch']
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each movie
                for movie in movies_data:
                    # Filter only the fields we want
                    row = {key: movie.get(key, '') for key in fieldnames if key in movie}
                    writer.writerow(row)
            
            # Show success message
            self.export_status.configure(
                text=f"Successfully exported {len(movies_data)} movies to CSV!",
                fg_color=("#c3e6cb", "#285b2a")
            )
            
            self.show_status(f"Successfully exported {len(movies_data)} movies to CSV!", "success")
            
        except Exception as e:
            self.export_status.configure(
                text=f"Error exporting movies: {str(e)}",
                fg_color=("#f8d7da", "#691c22")
            )
            self.show_status(f"Error exporting movies: {str(e)}", "error")
    
    def _export_series_to_csv(self):
        """Export series data to a CSV file"""
        try:
            from tkinter import filedialog
            import csv
            
            # Ask for a save location
            filepath = filedialog.asksaveasfilename(
                title="Save Series CSV",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if not filepath:
                return
            
            # Read the series data
            series_data = []
            data_file = Path("data/series.json")
            if data_file.exists():
                with open(data_file, "r") as f:
                    series_data = json.load(f)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV headers
                fieldnames = ['title', 'year', 'watch_date', 'user_rating', 'status',
                             'current_season', 'current_episode', 'seasons', 'episodes',
                             'genres', 'creator', 'first_air_date']
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each series
                for series in series_data:
                    # Filter only the fields we want
                    row = {key: series.get(key, '') for key in fieldnames if key in series}
                    writer.writerow(row)
            
            # Show success message
            self.export_status.configure(
                text=f"Successfully exported {len(series_data)} series to CSV!",
                fg_color=("#c3e6cb", "#285b2a")
            )
            
            self.show_status(f"Successfully exported {len(series_data)} series to CSV!", "success")
            
        except Exception as e:
            self.export_status.configure(
                text=f"Error exporting series: {str(e)}",
                fg_color=("#f8d7da", "#691c22")
            )
            self.show_status(f"Error exporting series: {str(e)}", "error")
    
    def _backup_data(self):
        """Backup movies and series data to a timestamped folder"""
        try:
            from tkinter import filedialog
            import shutil
            from datetime import datetime
            
            # Ask for a backup directory
            backup_dir = filedialog.askdirectory(
                title="Select Backup Directory"
            )
            
            if not backup_dir:
                return
            
            # Create a timestamped folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = os.path.join(backup_dir, f"media_tracker_backup_{timestamp}")
            os.makedirs(backup_folder, exist_ok=True)
            
            # Copy files to backup folder
            data_dir = Path("data")
            if not data_dir.exists():
                os.makedirs("data", exist_ok=True)
            
            # Create empty files if they don't exist
            movies_file = data_dir / "movies.json"
            series_file = data_dir / "series.json"
            
            if not movies_file.exists():
                with open(movies_file, "w") as f:
                    json.dump([], f)
            
            if not series_file.exists():
                with open(series_file, "w") as f:
                    json.dump([], f)
            
            # Copy files
            shutil.copy2(movies_file, backup_folder)
            shutil.copy2(series_file, backup_folder)
            
            # Copy config file too
            config_file = Path("config.py")
            if config_file.exists():
                shutil.copy2(config_file, backup_folder)
            
            # Show success message
            self.export_status.configure(
                text=f"Backup created successfully at: {backup_folder}",
                fg_color=("#c3e6cb", "#285b2a")
            )
            
            self.show_status("Backup created successfully!", "success")
            
        except Exception as e:
            self.export_status.configure(
                text=f"Error creating backup: {str(e)}",
                fg_color=("#f8d7da", "#691c22")
            )
            self.show_status(f"Error creating backup: {str(e)}", "error")
    
    def _browse_icon(self):
        """Browse for a custom icon file for the desktop shortcut"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        
        if file_path:
            self.custom_icon_path.set(file_path)
            self.show_status(f"Custom icon selected: {os.path.basename(file_path)}", "success")
            
    def show_status(self, message, status_type="info", duration=3.0):
        """Show a status message in the status bar"""
        # Set colors based on status type
        if status_type == "success":
            fg_color = ("#c3e6cb", "#285b2a")  # Light green / Dark green
            text_color = ("#155724", "#d4edda")  # Dark green text / Light green text
        elif status_type == "error":
            fg_color = ("#f8d7da", "#691c22")  # Light red / Dark red
            text_color = ("#721c24", "#f8d7da")  # Dark red text / Light red text
        elif status_type == "warning":
            fg_color = ("#fff3cd", "#856404")  # Light yellow / Dark yellow
            text_color = ("#856404", "#fff3cd")  # Dark yellow text / Light yellow text
        else:  # info
            fg_color = ("#d1ecf1", "#0c5460")  # Light blue / Dark blue
            text_color = ("#0c5460", "#d1ecf1")  # Dark blue text / Light blue text
            
        # Update status bar
        self.status_bar.configure(
            text=message,
            fg_color=fg_color,
            text_color=text_color
        )
        
        # Show the status bar
        self.status_bar.grid()
        
        # Schedule hiding the status bar after duration
        self.after(int(duration * 1000), self.status_bar.grid_remove)
        
        # Return focus to the main window
        self.focus_force()


if __name__ == "__main__":
    app = App()
    app.mainloop() 