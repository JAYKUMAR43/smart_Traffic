import streamlit as st
import cv2
import time
import os
import sys
from PIL import Image

# Ensure src modules import correctly
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.detection import detect_traffic
from src.signal_logic import decide_direction, congestion_level
from src.voice_alerts import speak_text

# Paths
VIDEO_PATH = os.path.join(BASE_DIR, "videos", "traffic.mp4")
SIM_PATH = os.path.join(BASE_DIR, "videos", "simulation.mp4")
ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

# UI Config
st.set_page_config(page_title="Smart Traffic AI", page_icon="🚦", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #00E1FF;
        text-align: center;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FFFFFF;
    }
    .metric-label {
        font-size: 1rem;
        color: #AAAAAA;
    }
    .status-panel {
        background-color: #0E1117;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00E1FF;
        margin-top: 20px;
    }
    .highlight-green { color: #00FF00; font-weight: bold; }
    .highlight-red { color: #FF0000; font-weight: bold; }
    .highlight-yellow { color: #FFFF00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-header'>🚦 Smart AI Traffic Management System</div>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Control Panel")
video_option = st.sidebar.radio("Select Source", ["Real Traffic Video", "Simulated Video"], index=1)
use_camera = st.sidebar.toggle("🎥 Use Laptop Camera")

source_path = VIDEO_PATH if video_option == "Real Traffic Video" else SIM_PATH
if use_camera: source_path = 0

# State
if 'last_signal' not in st.session_state: st.session_state.last_signal = "Horizontal"
if 'last_voice_time' not in st.session_state: st.session_state.last_voice_time = 0

start_button = st.sidebar.button("▶ Start System", type="primary")

if start_button:
    col_video, col_stats = st.columns([2, 1])
    
    with col_video:
        stframe = st.empty()
    
    with col_stats:
        st.markdown("### 📊 Live Traffic Metrics")
        m1, m2 = st.columns(2)
        with m1:
            metric_h = st.empty()
        with m2:
            metric_v = st.empty()
            
        st.markdown("---")
        st.markdown("### 🧠 AI Decision Log")
        log_placeholder = st.empty()
        
        st.markdown("---")
        st.markdown("### 🚦 Signal Status")
        signal_status = st.empty()

    cap = cv2.VideoCapture(source_path)
    
    if not cap.isOpened():
        st.error(f"❌ Could not open video source: {source_path}")
        st.stop()

    while True:
        ret, frame = cap.read()
        if not ret:
            st.success("Simulation Complete")
            break
            
        # Detection
        objects, img = detect_traffic(frame)
        
        # Spatial Counting
        h, w, _ = img.shape
        roi_h_y1, roi_h_y2 = int(h * 0.35), int(h * 0.65)
        roi_v_x1, roi_v_x2 = int(w * 0.35), int(w * 0.65)
        
        count_h = 0
        count_v = 0
        amb_detected = False
        
        for obj in objects:
            cx, cy = obj["x"] + obj["w"]//2, obj["y"] + obj["h"]//2
            if roi_h_y1 < cy < roi_h_y2: count_h += 1
            elif roi_v_x1 < cx < roi_v_x2: count_v += 1
            if obj["label"] == "ambulance": amb_detected = True
            
        # AI Logic
        new_signal = decide_direction(count_h, count_v, amb_detected)
        
        # Voice Alerts & Logic Display
        current_time = time.time()
        log_text = ""
        
        # State Management for Voice
        if 'emergency_active' not in st.session_state: st.session_state.emergency_active = False
        
        if amb_detected:
            log_text = "🚨 <span class='highlight-red'>EMERGENCY VEHICLE DETECTED!</span><br>Override: Priority to Ambulance Lane."
            
            if not st.session_state.emergency_active:
                # Emergency JUST started
                speak_text("Emergency vehicle detected. Priority given to ambulance lane.")
                st.session_state.emergency_active = True
                st.session_state.last_voice_time = current_time
            
            # Keep signal updated to ambulance direction (handled by decide_direction logic or override)
            # In simulation, we might need to infer direction if not passed explicitly, 
            # but here we rely on decide_direction returning "Emergency" or specific direction.
            
        else:
            # No ambulance
            if st.session_state.emergency_active:
                # Emergency JUST ended
                speak_text("Emergency vehicle passed. Reverting to normal traffic flow.")
                st.session_state.emergency_active = False
                st.session_state.last_voice_time = current_time
            
            # Normal Volume Logic
            if new_signal != st.session_state.last_signal:
                # Signal Switch
                reason = "Higher Volume"
                log_text = f"⚖️ <span class='highlight-yellow'>Volume Shift Detected</span><br>H: {count_h} | V: {count_v}<br>Switching Signal to {new_signal}."
                
                # Only speak if enough time passed or it's a significant switch
                if current_time - st.session_state.last_voice_time > 8:
                    speak_text(f"Volume increased in {new_signal} lane. Switching priority.")
                    st.session_state.last_voice_time = current_time
                
                st.session_state.last_signal = new_signal
            else:
                log_text = f"✅ System Stable<br>Maintaining Green for {new_signal}."

        # Update UI
        stframe.image(img, channels="BGR", use_container_width=True)
        
        metric_h.markdown(f"<div class='metric-box'><div class='metric-value'>{count_h}</div><div class='metric-label'>Horizontal Lane</div></div>", unsafe_allow_html=True)
        metric_v.markdown(f"<div class='metric-box'><div class='metric-value'>{count_v}</div><div class='metric-label'>Vertical Lane</div></div>", unsafe_allow_html=True)
        
        log_placeholder.markdown(f"<div class='status-panel'>{log_text}</div>", unsafe_allow_html=True)
        
        if amb_detected:
             signal_status.error("🚨 EMERGENCY PRIORITY ACTIVE")
        elif new_signal == "Horizontal":
            signal_status.success("🟢 Horizontal Lane is GREEN")
        elif new_signal == "Vertical":
            signal_status.success("🟢 Vertical Lane is GREEN")

        time.sleep(0.03) # Limit FPS for UI stability

    cap.release()
