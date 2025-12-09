import cv2
import numpy as np
import os

out_path = os.path.join("videos", "traffic.mp4")
os.makedirs("videos", exist_ok=True)

width, height = 640, 360
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(out_path, fourcc, 30, (width, height))

for i in range(300):  # 10 seconds video
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(frame, "Traffic Simulation", (100, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)
    out.write(frame)

out.release()
print("🎥 Generated: videos/traffic.mp4")
