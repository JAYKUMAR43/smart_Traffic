import cv2
import numpy as np
import random
import os
import sys

# Ensure src modules import correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.signal_logic import decide_direction

# Configuration
WIDTH, HEIGHT = 1280, 720
FPS = 60
DURATION_SEC = 60 # Longer duration to show multiple events
TOTAL_FRAMES = FPS * DURATION_SEC
OUTPUT_PATH = os.path.join("videos", "simulation.mp4")

# Colors
COLOR_ROAD = (50, 50, 50)
COLOR_MARKING = (255, 255, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_GRASS = (34, 139, 34)
COLOR_ZEBRA = (220, 220, 220)

# Road Geometry
H_ROAD_Y1, H_ROAD_Y2 = 240, 480
V_ROAD_X1, V_ROAD_X2 = 520, 760
LANE_WIDTH = 120

STOP_X_LEFT = V_ROAD_X1 - 20
STOP_X_RIGHT = V_ROAD_X2 + 20
STOP_Y_TOP = H_ROAD_Y1 - 20
STOP_Y_BOTTOM = H_ROAD_Y2 + 20

def draw_vehicle_detailed(frame, v):
    x, y, w, h = int(v.x), int(v.y), int(v.w), int(v.h)
    cx, cy = x + w//2, y + h//2
    
    # Base Colors
    if v.type == "car": color = (0, 0, 200) # Red
    elif v.type == "bike": color = (200, 100, 0) # Blue-ish
    elif v.type == "auto": color = (0, 255, 255) # Yellow
    elif v.type == "bus": color = (0, 100, 0) # Green
    elif v.type == "truck": color = (0, 165, 255) # Orange
    elif v.type == "ambulance": color = (255, 255, 255) # White
    
    # Draw Body
    cv2.rectangle(frame, (x, y), (x+w, y+h), color, -1)
    
    is_horizontal = v.direction in ['left', 'right']
    
    if v.type == "car":
        if is_horizontal:
            cv2.rectangle(frame, (x+w//4, y+2), (x+3*w//4, y+h-2), (0,0,0), -1) 
            cv2.rectangle(frame, (x+w//3, y+4), (x+2*w//3, y+h-4), color, -1)
        else:
            cv2.rectangle(frame, (x+2, y+h//4), (x+w-2, y+3*h//4), (0,0,0), -1)
            cv2.rectangle(frame, (x+4, y+h//3), (x+w-4, y+2*h//3), color, -1)
            
    elif v.type == "auto":
        if is_horizontal:
            cv2.rectangle(frame, (x+w//4, y), (x+3*w//4, y+h), (0,0,0), -1)
        else:
            cv2.rectangle(frame, (x, y+h//4), (x+w, y+3*h//4), (0,0,0), -1)
            
    elif v.type == "bike":
        cv2.circle(frame, (cx, cy), 5, (50,50,50), -1)
        
    elif v.type == "bus":
        if is_horizontal:
            cv2.line(frame, (x, y+5), (x+w, y+5), (200,255,255), 4)
            cv2.line(frame, (x, y+h-5), (x+w, y+h-5), (200,255,255), 4)
        else:
            cv2.line(frame, (x+5, y), (x+5, y+h), (200,255,255), 4)
            cv2.line(frame, (x+w-5, y), (x+w-5, y+h), (200,255,255), 4)

    elif v.type == "ambulance":
        if is_horizontal:
            cv2.line(frame, (cx, y+5), (cx, y+h-5), (0,0,255), 4)
            cv2.line(frame, (cx-10, cy), (cx+10, cy), (0,0,255), 4)
        else:
            cv2.line(frame, (x+5, cy), (x+w-5, cy), (0,0,255), 4)
            cv2.line(frame, (cx, cy-10), (cx, cy+10), (0,0,255), 4)
        
        if (int(v.x + v.y) // 20) % 2 == 0:
            cv2.circle(frame, (x, y), 4, (0,0,255), -1)
            cv2.circle(frame, (x+w, y+h), 4, (0,0,255), -1)

class Vehicle:
    def __init__(self, v_type, direction, x, y):
        self.type = v_type
        self.direction = direction
        self.x = float(x)
        self.y = float(y)
        
        # Speeds
        if v_type == "ambulance": self.base_speed = 9.0
        elif v_type == "car": self.base_speed = random.uniform(6.0, 8.0)
        elif v_type == "bike": self.base_speed = random.uniform(7.0, 9.0)
        elif v_type == "auto": self.base_speed = random.uniform(5.0, 7.0)
        elif v_type == "bus": self.base_speed = random.uniform(4.0, 5.0)
        elif v_type == "truck": self.base_speed = random.uniform(3.0, 4.0)
        
        self.speed = self.base_speed
        
        # Dimensions
        if v_type == "bike": self.w, self.h = 15, 30
        elif v_type == "auto": self.w, self.h = 25, 35
        elif v_type == "car": self.w, self.h = 30, 50
        elif v_type == "bus": self.w, self.h = 40, 90
        elif v_type == "truck": self.w, self.h = 40, 100
        elif v_type == "ambulance": self.w, self.h = 35, 60
            
        if direction in ['left', 'right']:
            self.w, self.h = self.h, self.w

    def get_rect(self):
        return (self.x, self.y, self.w, self.h)

    def move(self, green_direction, vehicles_ahead):
        # Collision Avoidance
        safe_dist = 40
        min_dist = 9999
        
        for other in vehicles_ahead:
            if other is self: continue
            
            same_lane = False
            if self.direction in ['left', 'right']:
                if abs(self.y - other.y) < 20: same_lane = True
            else:
                if abs(self.x - other.x) < 20: same_lane = True
            
            if same_lane:
                d = 9999
                if self.direction == 'right' and other.x > self.x: d = other.x - (self.x + self.w)
                elif self.direction == 'left' and other.x < self.x: d = self.x - (other.x + other.w)
                elif self.direction == 'down' and other.y > self.y: d = other.y - (self.y + self.h)
                elif self.direction == 'up' and other.y < self.y: d = self.y - (other.y + other.h)
                
                if d < min_dist: min_dist = d

        # Traffic Light Logic
        is_green = False
        
        # Ambulance Logic: If Emergency mode, Ambulance ALWAYS has green
        if green_direction == "Emergency" and self.type == "ambulance": 
            is_green = True
        elif green_direction == "Horizontal" and self.direction in ['left', 'right']: 
            is_green = True
        elif green_direction == "Vertical" and self.direction in ['up', 'down']: 
            is_green = True

        # Stop Line Logic
        dist_to_stop = 9999
        if not is_green and self.type != "ambulance":
            if self.direction == 'right' and self.x < STOP_X_LEFT: dist_to_stop = STOP_X_LEFT - (self.x + self.w)
            elif self.direction == 'left' and self.x > STOP_X_RIGHT: dist_to_stop = self.x - STOP_X_RIGHT
            elif self.direction == 'down' and self.y < STOP_Y_TOP: dist_to_stop = STOP_Y_TOP - (self.y + self.h)
            elif self.direction == 'up' and self.y > STOP_Y_BOTTOM: dist_to_stop = self.y - STOP_Y_BOTTOM
        
        # Target Speed
        target = self.base_speed
        
        if min_dist < safe_dist: target = 0 
        elif min_dist < safe_dist * 2: target = self.base_speed * 0.5
        
        if dist_to_stop < 150 and dist_to_stop > 0: target = min(target, dist_to_stop / 10)
        if dist_to_stop <= 5: target = 0
        
        # Physics
        if self.speed < target: self.speed += 0.3
        elif self.speed > target: self.speed -= 0.5
        if self.speed < 0: self.speed = 0
        
        # Move
        if self.direction == 'right': self.x += self.speed
        elif self.direction == 'left': self.x -= self.speed
        elif self.direction == 'down': self.y += self.speed
        elif self.direction == 'up': self.y -= self.speed

def generate():
    os.makedirs("videos", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))
    
    vehicles = []
    
    print(f"Generating High Intensity Simulation ({DURATION_SEC}s)...")
    
    current_signal = "Horizontal"
    
    # Timers
    amb_timer = 0
    
    for i in range(TOTAL_FRAMES):
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        frame[:] = COLOR_GRASS
        
        # Roads
        cv2.rectangle(frame, (0, H_ROAD_Y1), (WIDTH, H_ROAD_Y2), COLOR_ROAD, -1)
        cv2.rectangle(frame, (V_ROAD_X1, 0), (V_ROAD_X2, HEIGHT), COLOR_ROAD, -1)
        
        # Markings
        for z in range(H_ROAD_Y1+10, H_ROAD_Y2-10, 25):
            cv2.line(frame, (STOP_X_LEFT-40, z), (STOP_X_LEFT, z), COLOR_ZEBRA, 12)
            cv2.line(frame, (STOP_X_RIGHT, z), (STOP_X_RIGHT+40, z), COLOR_ZEBRA, 12)
        for z in range(V_ROAD_X1+10, V_ROAD_X2-10, 25):
            cv2.line(frame, (z, STOP_Y_TOP-40), (z, STOP_Y_TOP), COLOR_ZEBRA, 12)
            cv2.line(frame, (z, STOP_Y_BOTTOM), (z, STOP_Y_BOTTOM+40), COLOR_ZEBRA, 12)
            
        cv2.line(frame, (0, (H_ROAD_Y1+H_ROAD_Y2)//2), (STOP_X_LEFT, (H_ROAD_Y1+H_ROAD_Y2)//2), COLOR_YELLOW, 2)
        cv2.line(frame, (STOP_X_RIGHT, (H_ROAD_Y1+H_ROAD_Y2)//2), (WIDTH, (H_ROAD_Y1+H_ROAD_Y2)//2), COLOR_YELLOW, 2)
        cv2.line(frame, ((V_ROAD_X1+V_ROAD_X2)//2, 0), ((V_ROAD_X1+V_ROAD_X2)//2, STOP_Y_TOP), COLOR_YELLOW, 2)
        cv2.line(frame, ((V_ROAD_X1+V_ROAD_X2)//2, STOP_Y_BOTTOM), ((V_ROAD_X1+V_ROAD_X2)//2, HEIGHT), COLOR_YELLOW, 2)

        # --- HIGH INTENSITY SPAWNING ---
        # Constant pressure from all sides
        rate_h = 0.15
        rate_v = 0.15
        
        # Random bursts
        if i % 300 < 150: rate_h = 0.3 # Burst Horizontal
        else: rate_v = 0.3 # Burst Vertical

        # Ambulance Spawning (Every ~12 seconds)
        amb_timer += 1
        if amb_timer > 700: # ~12s at 60fps
            amb_timer = 0
            # Spawn ambulance from random direction
            d = random.choice(['right', 'left', 'down', 'up'])
            if d == 'right': x, y = -100, H_ROAD_Y2 - 60
            elif d == 'left': x, y = WIDTH + 50, H_ROAD_Y1 + 60
            elif d == 'down': x, y = V_ROAD_X1 + 60, -100
            elif d == 'up': x, y = V_ROAD_X2 - 60, HEIGHT + 50
            
            # Ensure no overlap for ambulance
            overlap = False
            for v in vehicles:
                if abs(v.x - x) < 100 and abs(v.y - y) < 100: overlap = True
            if not overlap:
                vehicles.append(Vehicle("ambulance", d, x, y))

        # Regular Traffic Spawn
        if random.random() < rate_h:
            d = random.choice(['right', 'left'])
            offset = random.randint(10, 80)
            if d == 'right': x, y = -100, H_ROAD_Y2 - offset - 20
            else: x, y = WIDTH + 50, H_ROAD_Y1 + offset
            
            overlap = False
            for v in vehicles:
                if abs(v.x - x) < 80 and abs(v.y - y) < 60: overlap = True
            if not overlap: vehicles.append(Vehicle(random.choice(["car", "auto", "bike", "bus"]), d, x, y))
            
        if random.random() < rate_v:
            d = random.choice(['down', 'up'])
            offset = random.randint(10, 80)
            if d == 'down': x, y = V_ROAD_X1 + offset, -100
            else: x, y = V_ROAD_X2 - offset - 20, HEIGHT + 50
            
            overlap = False
            for v in vehicles:
                if abs(v.x - x) < 60 and abs(v.y - y) < 80: overlap = True
            if not overlap: vehicles.append(Vehicle(random.choice(["car", "auto", "bike", "bus"]), d, x, y))

        # Logic Update
        if i % 10 == 0:
            count_h = 0
            count_v = 0
            amb_detected = False
            amb_direction = None
            
            for v in vehicles:
                cx, cy = v.x + v.w/2, v.y + v.h/2
                if H_ROAD_Y1 < cy < H_ROAD_Y2: count_h += 1
                elif V_ROAD_X1 < cx < V_ROAD_X2: count_v += 1
                
                if v.type == "ambulance": 
                    amb_detected = True
                    amb_direction = v.direction
            
            # AI Decision
            signal = decide_direction(count_h, count_v, amb_detected)
            
            # If Emergency, we must know WHICH direction to give green
            if signal == "Emergency":
                # Find direction of ambulance
                if amb_direction in ['left', 'right']: current_signal = "Horizontal"
                elif amb_direction in ['up', 'down']: current_signal = "Vertical"
                else: current_signal = "Horizontal" # Default
            else:
                current_signal = signal

        # Move & Draw
        vehicles.sort(key=lambda v: v.y)
        for v in vehicles:
            v.move(current_signal, vehicles)
            draw_vehicle_detailed(frame, v)

        vehicles = [v for v in vehicles if -150 < v.x < WIDTH + 150 and -150 < v.y < HEIGHT + 150]

        # Lights
        color_h = (0, 255, 0) if current_signal == "Horizontal" else (0, 0, 255)
        color_v = (0, 255, 0) if current_signal == "Vertical" else (0, 0, 255)
        
        cv2.circle(frame, (V_ROAD_X1 - 30, STOP_Y_TOP - 30), 15, color_v, -1)
        cv2.circle(frame, (STOP_X_RIGHT + 30, H_ROAD_Y1 - 30), 15, color_h, -1)
        cv2.circle(frame, (V_ROAD_X2 + 30, STOP_Y_BOTTOM + 30), 15, color_v, -1)
        cv2.circle(frame, (STOP_X_LEFT - 30, H_ROAD_Y2 + 30), 15, color_h, -1)
        
        # Overlay Text
        cv2.putText(frame, "Smart Traffic AI | VIKAS IGU Meerpur", (WIDTH-450, HEIGHT-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        
        status_text = f"Signal: {current_signal}"
        if current_signal == "Horizontal": status_text += " (V-Queue)"
        else: status_text += " (H-Queue)"
             
        cv2.putText(frame, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print("Done.")

if __name__ == "__main__":
    generate()
