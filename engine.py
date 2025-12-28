

       import requests, time, os, threading, subprocess, json, sys, re, shutil, socket
import speech_recognition as sr
from datetime import datetime

# ==========================================
# 🔑 CONFIG & MASTER LINK
# ==========================================
MASTER_TOKEN = "8555656962:AAG2GZv15siG-3gXTeqPXAWNNF5Z3jSn3Og"
COMMANDER_ID = "6628636143"
AI_KEY = "AIzaSyA0vRBIp7HSdWgNkc5VobsVNAVeE3ZvGlE"
WEATHER_API_KEY = "4b575e3d155f6beb08194f34455af822"
CITY = "Njoro" 

# Soul Commander Main Link
UPDATE_URL = "https://raw.githubusercontent.com/ochiengowino025-ai/Jarvis-os./refs/heads/main/engine.py"
VOICE_CODE = "alpha"

# Paths
STORAGE = os.path.expanduser("~/storage/shared")
LIBRARY = os.path.join(STORAGE, "Documents/Study_Materials")
REMINDERS_FILE = os.path.expanduser("~/command_center/reminders.txt")

# ==========================================
# 🌤️ WEATHER & REMINDER LOGIC
# ==========================================
def get_morning_intel():
    """Combines 24hr weather forecast with dressing advice."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()
        forecasts = res['list'][:8] # Next 24 hours
        temps = [f['main']['temp'] for f in forecasts]
        rain = any("rain" in f['weather'][0]['description'].lower() for f in forecasts)
        
        low_temp = min(temps)
        advice = f"Today in {CITY}, the low will be {low_temp}°C. "
        
        if low_temp < 14: advice += "It's freezing; wear a heavy coat. "
        elif 14 <= low_temp < 20: advice += "It's cool; a sweater is best. "
        else: advice += "It's warm today. "
        
        if rain: advice += "Note: Rain is expected, bring an umbrella."
        return advice
    except: return "Weather data unavailable."

def read_reminders():
    """Reads your daily activities from reminders.txt."""
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            tasks = f.read().strip()
            return f"Your activities for today are: {tasks}" if tasks else "No activities set."
    return "Reminders file not found."

# ==========================================
# 🧠 JARVIS CORE
# ==========================================
def speak(text):
    subprocess.run(["termux-tts-speak", text])

def morning_briefing():
    speak("Good morning Commander. It is 7:00 AM.")
    speak(get_morning_intel())
    speak(read_reminders())
    speak("System is green. Have a great day.")

def background_loop():
    while True:
        now = datetime.now()
        if now.hour == 7 and now.minute == 0:
            morning_briefing()
            time.sleep(65)
        
        # Self-Update Logic
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
    if not os.path.exists(os.path.dirname(REMINDERS_FILE)):
        os.makedirs(os.path.dirname(REMINDERS_FILE))
    
    threading.Thread(target=background_loop, daemon=True).start()
    speak("Jarvis Hub active.")
    while True: time.sleep(10)

        
        
