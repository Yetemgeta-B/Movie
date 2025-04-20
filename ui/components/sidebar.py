import customtkinter as ctk
from typing import Callable, Dict, List

class Sidebar(ctk.CTkFrame):
    """
    A modern sidebar navigation component for the Movie Tracker application.
    """
    
    def __init__(self, master, width=200, corner_radius=0, **kwargs):
        super().__init__(master, width=width, corner_radius=corner_radius, **kwargs)
        
        # Set fixed width for sidebar
        self.width = width
        self.configure(width=width)
        
        # Prevent resizing
        self.grid_propagate(False)
        
        # Set background color
        self.configure(fg_color=("#333", "#1c1c1c"))  # Light mode, Dark mode
        
        # Store navigation callbacks
        self.nav_callbacks = {}
        
        # Create sidebar UI
        self._create_sidebar_ui()
    
    def _create_sidebar_ui(self):
        """Create the sidebar UI components"""
        # Logo or app name
        self.logo_label = ctk.CTkLabel(
            self, 
            text="Movie Tracker", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#fff", "#fff")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Separator
        self.separator = ctk.CTkFrame(self, height=1, fg_color="gray50")
        self.separator.grid(row=1, column=0, sticky="ew", padx=15, pady=10)
        
        # Navigation buttons with icons (using text placeholders for now)
        self.nav_buttons = {}
        
        # Nav items with icons
        nav_items = [
            {"id": "home", "text": "🏠 Home", "row": 2},
            {"id": "movies", "text": "🎬 Movies", "row": 3},
            {"id": "series", "text": "📺 Series", "row": 4},
            {"id": "tables", "text": "📋 Tables", "row": 5},
            {"id": "settings", "text": "⚙️ Settings", "row": 6}
        ]
        
        # Create nav buttons
        for item in nav_items:
            self.nav_buttons[item["id"]] = ctk.CTkButton(
                self,
                text=item["text"],
                fg_color="transparent",
                text_color=("#fff", "#fff"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                height=40,
                corner_radius=5,
                command=lambda i=item["id"]: self._on_nav_button_click(i)
            )
            self.nav_buttons[item["id"]].grid(
                row=item["row"], 
                column=0, 
                sticky="ew", 
                padx=10, 
                pady=5
            )
        
        # Spacer to push footer to bottom
        self.spacer = ctk.CTkFrame(self, fg_color="transparent")
        self.spacer.grid(row=7, column=0, sticky="ew", pady=10)
        self.grid_rowconfigure(7, weight=1)
        
        # Version info at bottom
        self.version_label = ctk.CTkLabel(
            self, 
            text="v1.0.0",
            text_color="gray70",
            font=ctk.CTkFont(size=10)
        )
        self.version_label.grid(row=8, column=0, padx=20, pady=(0, 20))
    
    def set_nav_callbacks(self, callbacks: Dict[str, Callable]):
        """Set navigation callbacks for sidebar buttons"""
        self.nav_callbacks = callbacks
    
    def _on_nav_button_click(self, button_id: str):
        """Handle navigation button clicks"""
        # Reset all buttons to default style
        for btn_id, button in self.nav_buttons.items():
            if btn_id == button_id:
                # Highlight selected button
                button.configure(fg_color=("gray70", "gray30"))
            else:
                # Reset other buttons
                button.configure(fg_color="transparent")
        
        # Call the callback if it exists
        if button_id in self.nav_callbacks:
            self.nav_callbacks[button_id]()
    
    def select_tab(self, tab_id: str):
        """Programmatically select a tab"""
        self._on_nav_button_click(tab_id) 