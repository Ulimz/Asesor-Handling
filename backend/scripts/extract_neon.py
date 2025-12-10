from PIL import Image
import numpy as np
import os

def luma_to_alpha(input_path, output_path):
    print(f"Processing {input_path} with Luma Mask...")
    try:
        # Open image and ensure it has an alpha channel
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        
        newData = []
        for item in datas:
            # item is (R, G, B, A)
            r, g, b, a = item
            
            # Calculate Luminance (perceived brightness)
            # Luma = 0.299*R + 0.587*G + 0.114*B
            # For blue neon, Blue dominates, so we can use max(r,g,b) or a simple average
            # Ideally, we want Black to be transparent (A=0) and Bright color to be opaque (A=255)
            
            # Simple approach: Max brightness determines opacity
            max_val = max(r, g, b)
            
            # Apply a curve to make background cleaner (crush blacks)
            # If brightness is low (< 20), make it 0 to remove noise
            if max_val < 15:
                new_alpha = 0
            else:
                # Scale alpha: brighten the midtones slightly so the neon pops
                # Formula: Alpha = (Brightness / 255) ^ 0.5 * 255 (Gamma correction for opacity)
                new_alpha = int(min(255, (max_val / 255.0) ** 0.6 * 255))
            
            # We keep the original RGB colors, but replace Alpha
            newData.append((r, g, b, new_alpha))

        img.putdata(newData)
        img.save(output_path, "PNG")
        print(f"Saved Luma-masked logo to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

# Paths
source_dir = r"C:\Users\ulise\.gemini\antigravity\brain\b7f5d950-2b29-4946-9a71-5320cfb2bbf7"
target_dir = r"c:\Users\ulise\Programas Uli\Asistente_Handling\public"
source_file = os.path.join(source_dir, "uploaded_image_1765387259228.jpg") # User GIMP edited
target_file = os.path.join(target_dir, "logo_v4_gimp.png")

luma_to_alpha(source_file, target_file)
