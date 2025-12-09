import os
from PIL import Image, ImageDraw

ICON_DIR = os.path.join("dashboard", "icons")
os.makedirs(ICON_DIR, exist_ok=True)

def create_icon(filename, color, orientation=None):
    img = Image.new("RGB", (300, 300), "black")
    draw = ImageDraw.Draw(img)

    if filename == "red_all.png":
        draw.rectangle([50, 120, 250, 180], fill="red")
    else:
        if orientation == "horizontal":
            draw.rectangle([0, 120, 300, 180], fill=color)
        elif orientation == "vertical":
            draw.rectangle([120, 0, 180, 300], fill=color)
        elif orientation == "right":
            draw.polygon([(300,150),(200,100),(200,200)], fill=color)

    img.save(os.path.join(ICON_DIR, filename))
    print(f"✔ Created → {filename}")

create_icon("green_horizontal.png", "green", "horizontal")
create_icon("green_vertical.png", "green", "vertical")
create_icon("green_right.png", "green", "right")
create_icon("red_all.png", "red")

print("\n🎉 All Icons Generated Successfully!")
