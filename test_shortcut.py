import os
import sys
import win32com.client

def create_test_shortcut():
    # Get desktop path
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    print(f"Desktop path: {desktop_path}")
    
    # Get current directory
    app_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"App directory: {app_dir}")
    
    # Get Python executable
    python_exe = sys.executable
    print(f"Python executable: {python_exe}")
    
    # Target script (use main.py if it exists, otherwise this script)
    main_script = os.path.join(app_dir, "main.py")
    if not os.path.exists(main_script):
        main_script = os.path.abspath(__file__)
    print(f"Target script: {main_script}")
    
    # Create shortcut path
    shortcut_path = os.path.join(desktop_path, "Movie Tracker Test.lnk")
    print(f"Shortcut path: {shortcut_path}")
    
    try:
        # Create shortcut
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        
        # Set shortcut properties
        shortcut.TargetPath = python_exe
        shortcut.Arguments = f'"{main_script}"'
        shortcut.WorkingDirectory = app_dir
        
        # Use one of the existing icons
        icon_path = os.path.join(app_dir, "ui", "assets", "icons", "default.ico")
        if os.path.exists(icon_path):
            shortcut.IconLocation = icon_path
        else:
            shortcut.IconLocation = f"{python_exe},0"
            
        shortcut.Description = "Movie Tracker Test Shortcut"
        
        # Save the shortcut
        shortcut.save()
        
        # Check if created
        if os.path.exists(shortcut_path):
            print(f"SUCCESS: Shortcut created at {shortcut_path}")
        else:
            print(f"ERROR: Shortcut file was not created")
    
    except Exception as e:
        print(f"ERROR creating shortcut: {str(e)}")

if __name__ == "__main__":
    print("Testing desktop shortcut creation...")
    create_test_shortcut()
    print("Test complete. Press Enter to exit.")
    input() 