"""
Movie and Series Tracker
A beautiful and feature-rich application to track your watched movies and TV shows.
"""

# Import the main App class
from app import App
# Import settings handler to ensure it's initialized first
from core.settings_handler import settings

# Check for required packages
def check_requirements():
    try:
        import customtkinter
        import PIL
        import requests
        import tkcalendar
        import win32com
        import pandas
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install all required packages using:")
        print("pip install -r requirements.txt")
        return False

# Main entry point
if __name__ == "__main__":
    # Check if all requirements are met
    if check_requirements():
        # Create data directory if it doesn't exist
        import os
        from pathlib import Path
        Path("data").mkdir(exist_ok=True)
        
        # Ensure settings are loaded before app starts
        print(f"Appearance mode: {settings.get_appearance_mode()}")
        print(f"Color theme: {settings.get_color_theme()}")
        
        # Start the application
        app = App()
        app.mainloop()
    else:
        input("Press Enter to exit...") 