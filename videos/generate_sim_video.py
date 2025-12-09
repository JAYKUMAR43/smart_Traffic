import cv2
import numpy as np
import os
import random

width, height = 1280, 720
fps = 30
duration = 40  # seconds
total_frames = fps * duration

vehicles = []

# Vehicle types
types = [
    ("car", (0, 255, 0), (60, 30)),
    ("truck", (255, 0, 0), (100, 40)),
    ("motorcycle", (0, 255, 255), (35, 18)),
    ("bus", (255, 255, 0), (120, 45)),
    ("ambulance", (0, 0, 255), (70, 35))
]

def spawn_vehicle():
    kind, color, size = random.choice(types)

    direction = random.choice(["left", "right", "up", "down"])
    if direction == "left":
        x, y = width, height//2 + random.randint(-200, 200)
        vx, vy = -random.randint(4, 7), 0
    elif direction == "right":
        x, y = 0, height//2 + random.randint(-200, 200)
        vx, vy = random.randint(4, 7), 0
    elif direction == "up":
        x, y = width//2 + random.randint(-200, 200), height
        vx, vy = 0, -random.randint(4, 7)
    else:  # down
        x, y = width//2 + random.randint(-200, 200), 0
        vx, vy = 0, random.randint(4, 7)

    return {"type": kind, "color": color, "size": size, "pos": [x, y], "vel": [vx, vy]}

output_path = os.path.join(os.path.dirname(__file__), "traffic.mp4")
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

for frame in range(total_frames):
    img = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Randomly spawn vehicles
    if random.random() < 0.15:
        vehicles.append(spawn_vehicle())

    for v in vehicles[:]:
        x, y = v["pos"]
        w, h = v["size"]
        cv2.rectangle(img, (int(x), int(y)), (int(x + w), int(y + h)), v["color"], -1)
        v["pos"][0] += v["vel"][0]
        v["pos"][1] += v["vel"][1]

        if x < -150 or x > width + 150 or y < -150 or y > height + 150:
            vehicles.remove(v)

    video.write(img)

video.release()
print("🎥 Simulation traffic.mp4 generated successfully!")
