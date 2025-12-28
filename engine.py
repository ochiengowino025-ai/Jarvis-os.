
import requests, time, os, threading, subprocess, json, sys, re, shutil, socket
import speech_recognition as sr
from datetime import datetime

# ==========================================
# 🔑 CORE CONFIG & AUTH
# ==========================================
MASTER_TOKEN = "8555656962:AAG2GZv15siG-3gXTeqPXAWNNF5Z3jSn3Og"
COMMANDER_ID = "6628636143"
AI_KEY = "AIzaSyA0vRBIp7HSdWgNkc5VobsVNAVeE3ZvGlE"

# INTEGRATED OPENWEATHER API KEY
WEATHER_API_KEY = "4b575e3d155f6beb08194f34455af822"
CITY = "Njoro" 

UPDATE_URL = "https://raw.githubusercontent.com/ochiengowino025-ai/Jarvis-os./refs/heads/main/engine.py"
VOICE_CODE = "alpha"

# Paths
STORAGE = os.path.expanduser("~/storage/shared")
DOWNLOADS = os.path.join(STORAGE, "Download")
LIBRARY = os.path.join(STORAGE, "Documents/Study_Materials")

# ==========================================
# 🌤️ MORNING INTELLIGENCE (WEATHER & DRESSING)
# ==========================================
def get_24hr_forecast():
    """Fetches a detailed daily outlook using the 5-day/3-hour API."""
    try:
        # API call for forecast data
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()
        
        # Extract next 8 entries (roughly 24 hours of data)
        forecasts = res['list'][:8]
        temps = [f['main']['temp'] for f in forecasts]
        rain_prob = any("rain" in f['weather'][0]['description'].lower() for f in forecasts)
        
        max_temp = max(temps)
        min_temp = min(temps)
        
        report = f"The forecast for the next 24 hours in {CITY} indicates a high of {max_temp}°C and a low of {min_temp}°C. "
        
        # Tailored Recommendation Logic
        if min_temp < 14:
            report += "It will be quite cold tonight or early morning; please wear a heavy coat. "
        elif 14 <= min_temp < 20:
            report += "Expect a cool day; a hoodie or sweater is highly recommended. "
        else:
            report += "The weather remains warm; light clothing is sufficient. "
            
        if rain_prob:
            report += "Warning: Rain is detected in today's forecast. You must carry an umbrella."
            
        return report
    except Exception as e:
        return "Weather service currently unavailable, but stay alert to changing conditions."

def morning_briefing():
    """Full 7:00 AM Automated Briefing."""
    speak("Good morning Commander. Jarvis OS Initializing morning brief.")
    
    # 1. Weather Update & Clothing Advice
    weather_report = get_24hr_forecast()
    speak(weather_report)
    
    # 2. Daily Maintenance
    count = organize_files()
    if count > 0:
        speak(f"Maintenance complete: {count} academic documents moved to your Revision Hub.")
    
    speak("Your campus system is green. Have a productive day.")

# ==========================================
# 🧠 HARDWARE & FILE ACTIONS
# ==========================================
def speak(text):
    print(f"🗣️ JARVIS: {text}")
    subprocess.run(["termux-tts-speak", text])

def organize_files():
    if not os.path.exists(LIBRARY): os.makedirs(LIBRARY, exist_ok=True)
    count = 0
    if os.path.exists(DOWNLOADS):
        for f in os.listdir(DOWNLOADS):
            if f.lower().endswith(".pdf"):
                try:
                    shutil.move(os.path.join(DOWNLOADS, f), os.path.join(LIBRARY, f))
                    count += 1
                except: pass
    return count

# ==========================================
# 🔄 CONTINUOUS BACKGROUND OPS
# ==========================================
def background_loop():
    while True:
        now = datetime.now()
        # 7:00 AM SHARP TRIGGER
        if now.hour == 7 and now.minute == 0:
            morning_briefing()
            time.sleep(61) # Prevent double trigger
            
        # TIER 1 SELF-UPDATE CHECK
        try:
            update_res = requests.get(UPDATE_URL, timeout=20)
            if update_res.status_code == 200:
                with open(__file__, 'r') as f:
                    if update_res.text != f.read():
                        with open(__file__, 'w') as f: f.write(update_res.text)
                        os.execv(sys.executable, ['python'] + sys.argv)
        except: pass
        
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=background_loop, daemon=True).start()
    speak("Satellite node online.")
    
    # Simple Voice Recognition for weather queries
    recognizer = sr.Recognizer()
    while True:
        try:
            path = os.path.expanduser("~/command_center/voice_input.wav")
            subprocess.run(["termux-microphone-record", "-d", "3", "-f", path, "-l", "0"], check=True, stderr=subprocess.DEVNULL)
            with sr.AudioFile(path) as source:
                text = recognizer.recognize_google(recognizer.record(source)).lower()
                if VOICE_CODE in text:
                    if "weather" in text:
                        speak(get_24hr_forecast())
        except: pass
        
