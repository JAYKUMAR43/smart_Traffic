import cv2
import numpy as np

# --- GLOBAL OBJECTS (reuse between frames) ---
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=500, varThreshold=40, detectShadows=True
)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

# ------------------------------------------------
# MAIN FUNCTION: detect_traffic(frame)
# ------------------------------------------------
def detect_traffic(frame):
    """
    Simple motion-based vehicle detection using background subtraction.
    No YOLO, no internet needed.
    Returns:
      - counts: dict of estimated vehicle counts
      - output: frame with rectangles drawn
    """
    # Standard size for stability
    frame_resized = cv2.resize(frame, (960, 540))

    # 1) Background subtraction
    fg_mask = bg_subtractor.apply(frame_resized)

    # 2) Threshold to keep strong motion only
    _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

    # 3) Remove noise + fill gaps
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_DILATE, kernel, iterations=2)

    # 4) Contours = moving objects
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Vehicle objects list
    detected_objects = []

    output = frame_resized.copy()

    for cnt in contours:
        area = cv2.contourArea(cnt)

        # Ignore small noise
        if area < 800:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        # Rough classification based on area size
        if area < 2000:
            label = "motorcycle"
        elif area < 6000:
            label = "car"
        elif area < 12000:
            label = "truck"
        else:
            label = "bus"

        # Store object data
        detected_objects.append({
            "label": label,
            "x": x, "y": y, "w": w, "h": h,
            "area": area
        })

        # Draw box + label on frame
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            output,
            label,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

    return detected_objects, output
