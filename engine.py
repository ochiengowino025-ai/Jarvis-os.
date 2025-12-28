import requests, time, os, threading, subprocess, json, sys, re, shutil, socket
from datetime import datetime

MASTER_TOKEN = "8555656962:AAG2GZv15siG-3gXTeqPXAWNNF5Z3jSn3Og"
COMMANDER_ID = "6628636143"
WEATHER_API_KEY = "4b575e3d155f6beb08194f34455af822"
CITY = "Njoro"
VOICE_CODE = "alpha"
UPDATE_URL = "https://raw.githubusercontent.com/ochiengowino025-ai/Jarvis-os./refs/heads/main/engine.py"

STORAGE = os.path.expanduser("~/storage/shared")
LIBRARY = os.path.join(STORAGE, "Documents/Study_Materials")
REMINDERS_FILE = os.path.expanduser("~/command_center/reminders.txt")

def speak(text):
    print(f"🗣️ JARVIS: {text}")
    subprocess.run(["termux-tts-speak", text])

def get_weather_intel():
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()
        forecasts = res['list'][:8]
        temps = [f['main']['temp'] for f in forecasts]
        rain = any("rain" in f['weather'][0]['description'].lower() for f in forecasts)
        low_temp = min(temps)
        report = f"Today in {CITY}, the low will be {low_temp} degrees Celsius. "
        if low_temp < 15: report += "It is cold; wear a heavy jacket. "
        elif 15 <= low_temp < 22: report += "It is cool; a sweater is recommended. "
        else: report += "It is warm today. "
        if rain: report += "Warning: Rain is expected, carry an umbrella."
        return report
    except: return "Weather data unavailable."

def get_daily_tasks():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            tasks = f.read().strip()
            return f"Your activities for today: {tasks}" if tasks else "No activities set."
    return "Reminders file not found."

def organize_files():
    downloads = os.path.join(STORAGE, "Download")
    if not os.path.exists(LIBRARY): os.makedirs(LIBRARY, exist_ok=True)
    count = 0
    if os.path.exists(downloads):
        for f in os.listdir(downloads):
            if f.lower().endswith(".pdf"):
                try:
                    shutil.move(os.path.join(downloads, f), os.path.join(LIBRARY, f))
                    count += 1
                except: pass
    return count

def background_loop():
    while True:
        now = datetime.now()
        if now.hour == 7 and now.minute == 0:
            speak("Good morning Commander. Jarvis OS briefing initiated.")
            speak(get_weather_intel())
            speak(get_daily_tasks())
            pdfs = organize_files()
            if pdfs > 0: speak(f"I have organized {pdfs} study materials.")
            time.sleep(65)
        try:
            res = requests.get(UPDATE_URL, timeout=20)
            if res.status_code == 200:
                with open(__file__, 'r') as f:
                    content = f.read()
                    if res.text != content:
                        with open(__file__, 'w') as f: f.write(res.text)
                        os.execv(sys.executable, ['python'] + sys.argv)
        except: pass
        time.sleep(30)

if __name__ == "__main__":
    print("🚀 JARVIS: FULL SYSTEM RESTORED.")
    threading.Thread(target=background_loop, daemon=True).start()
    speak("Jarvis OS Online. Everything we worked for has been restored.")
    while True:
        time.sleep(10)
