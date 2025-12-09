import os
import playsound
import pyttsx3
import threading

# Initialize engine once
try:
    engine = pyttsx3.init()
except:
    engine = None

def play_alert(audio_path):
    try:
        if os.path.exists(audio_path):
            playsound.playsound(audio_path, block=False)
    except:
        pass

def speak_text(text):
    """
    Speak text using pyttsx3 in a separate thread to avoid blocking.
    """
    def _speak():
        try:
            # Re-init might be needed if engine is not thread safe, 
            # but usually one global instance is okay if locked.
            # For simplicity in Streamlit, we create a new engine instance per call 
            # or just try-except.
            local_engine = pyttsx3.init()
            local_engine.say(text)
            local_engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    thread = threading.Thread(target=_speak)
    thread.start()
