import os
import sys
import traceback
import argparse
from pathlib import Path

def create_shortcut(output_dir=None, shortcut_name=None):
    """
    Create a shortcut with detailed error reporting
    
    Args:
        output_dir (str): Directory where shortcut will be created (defaults to desktop)
        shortcut_name (str): Name of the shortcut file (defaults to "Movie Tracker")
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("Starting shortcut creation...")
    
    # Use desktop as default output directory
    if not output_dir:
        # Use specific OneDrive desktop path
        output_dir = r"C:\Users\HP\OneDrive\Desktop"
    
    # Use default shortcut name if not specified
    if not shortcut_name:
        shortcut_name = "Movie Tracker"
    
    # Ensure shortcut name has .lnk extension
    if not shortcut_name.lower().endswith('.lnk'):
        shortcut_name += '.lnk'
        
    print(f"Output directory: {output_dir}")
    print(f"Shortcut name: {shortcut_name}")
    
    # Ensure output directory exists
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"ERROR: Could not create output directory: {e}")
        return False
    
    # Get current script path and calculate the app directory
    script_path = os.path.abspath(__file__)
    app_dir = os.path.dirname(script_path)  # This script is in the root directory
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
            
        shortcut_path = os.path.join(output_dir, shortcut_name)
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
    # Create argument parser
    parser = argparse.ArgumentParser(description="Create a shortcut for the Movie Tracker application")
    parser.add_argument("--output-dir", "-o", help="Directory where shortcut will be created")
    parser.add_argument("--name", "-n", help="Name of the shortcut (without .lnk extension)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the shortcut creation function
    success = create_shortcut(
        output_dir=args.output_dir,
        shortcut_name=args.name
    )
    
    # Provide feedback to the user
    if success:
        print("\nShortcut created successfully!")
    else:
        print("\nFailed to create shortcut. See error details above.")
    
    # Wait for user input before closing if run directly
    if sys.stdout.isatty():
        input("\nPress Enter to exit...") 