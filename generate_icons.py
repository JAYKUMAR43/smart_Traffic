from PIL import Image, ImageDraw
import os

# Create icons folder inside dashboard
icons_dir = os.path.join("dashboard", "icons")
os.makedirs(icons_dir, exist_ok=True)

# Icon size
size = (300, 300)

def create_icon(output_path, direction="horizontal"):
    img = Image.new("RGB", size, "black")
    draw = ImageDraw.Draw(img)

    if direction == "horizontal":
        draw.rectangle([50, 130, 250, 170], fill="green")  # Horizontal green bar
    else:
        draw.rectangle([130, 50, 170, 250], fill="green")  # Vertical green bar

    img.save(output_path)
    print(f"Saved: {output_path}")

# Generate both icons
create_icon(os.path.join(icons_dir, "green_horizontal.png"), "horizontal")
create_icon(os.path.join(icons_dir, "green_vertical.png"), "vertical")

print("\n🎉 Icons Generated Successfully!")
