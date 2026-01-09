from PIL import Image, ImageOps
import numpy as np

def fix_dark_logo():
    try:
        # Load the Dark Mode Logo (which is currently Black Text on White BG)
        img = Image.open("logo.png").convert("RGBA")
        
        # Method:
        # We want "White Text on Transparent BG".
        # Currently we assume it is "Black Text on White BG".
        
        data = np.array(img)
        r, g, b, a = data.T
        
        # Identify White Background pixels (High R, G, B)
        white_areas = (r > 200) & (g > 200) & (b > 200)
        
        # Identify Black Text pixels (Low R, G, B)
        black_areas = (r < 50) & (g < 50) & (b < 50)
        
        # 1. Make Background Transparent
        # (Actually, let's just rebuild the image)
        
        # New Image Array (Initialize as Transparent)
        new_data = np.zeros_like(data)
        
        # 2. Where original was Black (Text), make it WHITE (255, 255, 255, 255)
        # We can be broader: Anything NOT white background should be White Text?
        # Let's simple Invert the colors: Black->White.
        # And use the Inverse Brightness as Alpha? 
        
        # Better approach for "Black Text on White BG" -> "White Text on Transparent":
        # Alpha = Inverted Brightness.
        # Color = White.
        
        # Convert to Grayscale for brightness
        gray = img.convert("L")
        gray_np = np.array(gray)
        
        # Invert: Black(0) becomes 255 (Opaque). White(255) becomes 0 (Transparent).
        # But we want the TEXT to be white.
        # So Alpha channel = 255 - gray_np
        alpha = 255 - gray_np
        
        # Threshold alpha to clean up artifacts?
        # alpha[alpha < 20] = 0 # Clean up noise
        
        # Create pure white image
        white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
        
        # Apply the calculated alpha
        white_img.putalpha(Image.fromarray(alpha))
        
        # Save
        white_img.save("logo_fixed.png")
        print("Successfully created logo_fixed.png (White Text / Transparent BG)")
        
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    fix_dark_logo()
