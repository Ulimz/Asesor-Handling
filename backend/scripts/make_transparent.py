from PIL import Image
import numpy as np
import os

def remove_black_background(input_path, output_path):
    print(f"Processing {input_path}...")
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        
        newData = []
        for item in datas:
            # Check if pixel is dark (black)
            # Threshold: R, G, B all < 30
            if item[0] < 30 and item[1] < 30 and item[2] < 30:
                newData.append((0, 0, 0, 0)) # Fully transparent
            else:
                newData.append(item) # Keep original pixel

        img.putdata(newData)
        img.save(output_path, "PNG")
        print(f"Saved transparent logo to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

# Paths
source_dir = r"C:\Users\ulise\.gemini\antigravity\brain\b7f5d950-2b29-4946-9a71-5320cfb2bbf7"
target_dir = r"c:\Users\ulise\Programas Uli\Asistente_Handling\public"
source_file = os.path.join(source_dir, "uploaded_image_1765381963332.png")
target_file = os.path.join(target_dir, "logo_transparent_final.png")

remove_black_background(source_file, target_file)
