import os
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

def create_icon(name, color, output_dir):
    """Create a simple icon with the given color and letter label"""
    # Create a 128x128 RGB image with the specified color
    img = Image.new('RGB', (128, 128), color)
    draw = ImageDraw.Draw(img)
    
    # Create a simple icon design (border)
    border_width = 10
    draw.rectangle(
        [(border_width, border_width), 
         (128 - border_width, 128 - border_width)], 
        outline="#FFFFFF", 
        width=3
    )
    
    # Get the first letter of the name for the icon
    letter = name[0].upper()
    
    # Try to use a built-in font, or use default if not available
    try:
        # Try to find a font (this will vary by system)
        font_paths = [
            "C:\\Windows\\Fonts\\Arial.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 64)
                break
        
        if font is None:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Draw the letter centered in the icon
        # Using getbbox() for Pillow >= 9.2.0 or fallback to approximation
        try:
            bbox = font.getbbox(letter)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Fallback for older Pillow versions
            text_width, text_height = (50, 50)  # Approximation
            
        position = ((128 - text_width) // 2, (128 - text_height) // 2 - 5)
        draw.text(position, letter, fill="#FFFFFF", font=font)
    except Exception as e:
        print(f"Error adding text to icon: {e}")
        # Create a simple circle if text fails
        draw.ellipse((34, 34, 94, 94), fill="#FFFFFF")
    
    # Save the icon
    output_path = os.path.join(output_dir, f"{name}.ico")
    img.save(output_path, format="ICO")
    print(f"Created icon: {output_path}")

def main():
    # Create icons directory if it doesn't exist
    icons_dir = os.path.join("ui", "assets", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # Define icons to create (name and color)
    icons = [
        ("default", "#3498db"),  # Blue
        ("film", "#e74c3c"),     # Red
        ("tv", "#2ecc71"),       # Green
        ("document", "#f39c12"), # Yellow
        ("drama", "#9b59b6"),    # Purple
        ("game", "#1abc9c")      # Teal
    ]
    
    # Create each icon
    for name, color in icons:
        create_icon(name, color, icons_dir)
    
    print("All icons created successfully!")

if __name__ == "__main__":
    main() 