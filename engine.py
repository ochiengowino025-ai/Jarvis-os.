

     import requests, time, os, threading, subprocess, json, sys, re, shutil, socket
import speech_recognition as sr
from datetime import datetime

# ==========================================
# 🔑 CORE CONFIG & MASTER KEYS
# ==========================================
MASTER_TOKEN = "8555656962:AAG2GZv15siG-3gXTeqPXAWNNF5Z3jSn3Og"
COMMANDER_ID = "6628636143"
AI_KEY = "AIzaSyA0vRBIp7HSdWgNkc5VobsVNAVeE3ZvGlE"
WEATHER_API_KEY = "4b575e3d155f6beb08194f34455af822" # Your verified key
CITY = "Njoro" 

UPDATE_URL = "https://raw.githubusercontent.com/ochiengowino025-ai/Jarvis-os./refs/heads/main/engine.py"
VOICE_CODE = "alpha"

# Paths
STORAGE = os.path.expanduser("~/storage/shared")
LIBRARY = os.path.join(STORAGE, "Documents/Study_Materials")
REMINDERS_FILE = os.path.expanduser("~/command_center/reminders.txt")

# ==========================================
# 🌤️ MODULE 1: WEATHER & DRESSING LOGIC
# ==========================================
def get_weather_intel():
    """Fetches 24hr forecast and provides campus dressing advice."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()
        forecasts = res['list'][:8] # Next 24 hours (8 * 3hr slots)
        temps = [f['main']['temp'] for f in forecasts]
        rain = any("rain" in f['weather'][0]['description'].lower() for f in forecasts)
        
        low_temp = min(temps)
        advice = f"Today in {CITY}, the forecast shows a low of {low_temp}°C. "
        
        if low_temp < 15:
            advice += "It will be quite cold; please wear a heavy jacket. "
        elif 15 <= low_temp < 22:
            advice += "It's cool; a hoodie or sweater is recommended. "
        else:
            advice += "The weather is warm; light clothing is fine. "
            
        if rain:
            advice += "Warning: Rain is expected. Do not forget your umbrella."
        return advice
    except:
        return "Weather data currently unavailable."

# ==========================================
# 📚 MODULE 2: ACADEMIC & TASK MANAGEMENT
# ==========================================
def get_daily_tasks():
    """Reads reminders from your local file."""
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            tasks = f.read().strip()
            return f"Your activities for today: {tasks}" if tasks else "No activities set for today."
    return "Reminders file not found."

def organize_revision_hub():
    """Auto-organizes PDFs for study."""
    downloads = os.path.join(STORAGE, "Download")
    if not os.path.exists(LIBRARY): os.makedirs(LIBRARY, exist_ok=True)
    count = 0
    if os.path.exists(downloads):
        for f in os.listdir(downloads):
            if f.lower().endswith(".pdf"):
                shutil.move(os.path.join(downloads, f), os.path.join(LIBRARY, f))
                count += 1
    return count

# ==========================================
# 🎤 MODULE 3: VOICE & SCHEDULER
# ==========================================
def speak(text):
    print(f"🗣️ JARVIS: {text}")
    subprocess.run(["termux-tts-speak", text])

def morning_briefing():
    """Triggered at 07:00 AM sharp."""
    speak("Good morning Commander. Jarvis OS system check complete.")
    speak(get_weather_intel())
    speak(get_daily_tasks())
    
    pdfs = organize_revision_hub()
    if pdfs > 0:
        speak(f"I have also moved {pdfs} new documents to your revision hub.")
    speak("All systems are green. Have a productive day.")

def background_loop():
    """Handles time triggers and GitHub updates."""
    while True:
        now = datetime.now()
        # 7:00 AM Briefing
        if now.hour == 7 and now.minute == 0:
            morning_briefing()
            time.sleep(65) # Stop double-trigger
            
        # TIER 1 SELF-UPDATE
        try:
            res = requests.get(UPDATE_URL, timeout=20)
            if res.status_code == 200:
                with open(__file__, 'r') as f:
                    if res.text != f.read():
                        with open(__file__, 'w') as f: f.write(res.text)
                        os.execv(sys.executable, ['python'] + sys.argv)
        except: pass
        time.sleep(30)

if __name__ == "__main__":
    # Ensure local directory exists
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)
    
    threading.Thread(target=background_loop, daemon=True).start()
    speak("Jarvis OS Satellite Online.")
    
    # Continuous voice recognition loop
    while True: time.sleep(10)

    
        
