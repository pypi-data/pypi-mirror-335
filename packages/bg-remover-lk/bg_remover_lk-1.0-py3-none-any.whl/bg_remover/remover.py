import os
from rembg import remove
from PIL import Image

def remove_background(input_dir="input/", output_dir="output/"):
    """Removes background from all .jpg, .jpeg, and .png images in the input directory."""
    
    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    print(f"📂 Checking files in: {input_dir}")
    files = os.listdir(input_dir)
    
    if not files:
        print("⚠️ No images found in the input folder. Add some images and try again.")
        return

    print(f"📝 Files found: {files}")

    for file_name in files:
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):  # Process only valid image files
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, f"{file_name.rsplit('.', 1)[0]}_bg.png")  # Save as .png
            
            print(f"⚡ Processing: {file_name}")

            try:
                print(f"📤 Opening image: {input_path}")
                input_image = Image.open(input_path)

                print("🔄 Removing background...")
                output = remove(input_image)

                print("🎨 Converting to RGB if needed...")
                if output.mode == 'RGBA':
                    output = output.convert("RGB")  # Convert to RGB

                print(f"💾 Saving output: {output_path}")
                output.save(output_path)

                print(f"✅ Successfully processed: {file_name}")

            except Exception as e:
                print(f"❌ Error processing {file_name}: {e}")
        else:
            print(f"⏩ Skipping non-image file: {file_name}")

# Run the background removal function
if __name__ == "__main__":
    remove_background()
