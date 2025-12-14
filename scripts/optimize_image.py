from PIL import Image
import os
import sys

def optimize_image(path, max_width=512):
    try:
        if not os.path.exists(path):
            print(f"Error: File not found at {path}")
            return

        img = Image.open(path)
        print(f"Original: {img.format}, Size: {img.size}, Mode: {img.mode}")
        
        # Calculate new size
        width_percent = (max_width / float(img.size[0]))
        if width_percent < 1:
            h_size = int((float(img.size[1]) * float(width_percent)))
            img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
            print(f"Resized to: {img.size}")
        else:
            print("Image is smaller than max_width, skipping resize.")

        # Optimize and save
        output_path = path # Overwrite
        img.save(output_path, optimize=True, quality=85)
        print(f"Optimized image saved to {output_path}")
        
        # Check new size
        new_size = os.path.getsize(output_path)
        print(f"New file size: {new_size / 1024:.2f} KB")

    except Exception as e:
        print(f"Error optimizing image: {e}")

if __name__ == "__main__":
    optimize_image(sys.argv[1])
