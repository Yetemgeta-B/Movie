import os
import sys
import traceback
from pathlib import Path

def create_desktop_shortcut():
    """Create a desktop shortcut with detailed error reporting"""
    print("Starting desktop shortcut creation...")
    
    # Get desktop path
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    print(f"Desktop path: {desktop_path}")
    
    # Get current script path
    script_path = os.path.abspath(__file__)
    app_dir = os.path.dirname(script_path)
    main_script = os.path.join(app_dir, "main.py")
    print(f"App directory: {app_dir}")
    print(f"Main script: {main_script}")
    
    try:
        # Check if pywin32 is installed
        try:
            import win32com.client
            print("win32com.client module successfully imported")
        except ImportError:
            print("ERROR: win32com.client module not found. Please install it with:")
            print("pip install pywin32")
            return False
            
        shortcut_path = os.path.join(desktop_path, "Movie Tracker.lnk")
        print(f"Creating shortcut at: {shortcut_path}")
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        
        # Get the Python executable path
        python_exe = sys.executable
        print(f"Python executable: {python_exe}")
        
        # Set shortcut properties
        shortcut.TargetPath = python_exe
        shortcut.Arguments = f'"{main_script}"'
        shortcut.WorkingDirectory = app_dir
        
        # Handle icon selection
        icons_dir = os.path.join(app_dir, "ui", "assets", "icons")
        icon_path = os.path.join(icons_dir, "default.ico")
        
        if os.path.exists(icon_path):
            print(f"Using icon: {icon_path}")
            shortcut.IconLocation = icon_path
        else:
            print(f"Icon not found at {icon_path}, using Python icon")
            shortcut.IconLocation = f"{python_exe},0"
            
        shortcut.Description = "Movie and Series Tracker Application"
        
        # Save the shortcut
        print("Saving shortcut...")
        shortcut.save()
        
        # Verify shortcut was created
        if os.path.exists(shortcut_path):
            print(f"SUCCESS: Shortcut created at {shortcut_path}")
            return True
        else:
            print(f"ERROR: Shortcut file not found after creation at {shortcut_path}")
            return False
            
    except Exception as e:
        print(f"ERROR creating shortcut: {str(e)}")
        print("Detailed traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = create_desktop_shortcut()
    if result:
        print("\nShortcut created successfully. Check your desktop for 'Movie Tracker.lnk'")
    else:
        print("\nFailed to create shortcut. See error messages above.")
    
    # Keep the window open
    input("\nPress Enter to exit...") 