import requests, time, os, threading, subprocess, json, sys, re, shutil, socket
import speech_recognition as sr
from datetime import datetime

# ==========================================
# 🔑 CORE CONFIG & MASTER LINK
# ==========================================
MASTER_TOKEN = "8555656962:AAG2GZv15siG-3gXTeqPXAWNNF5Z3jSn3Og"
COMMANDER_ID = "6628636143"
AI_KEY = "AIzaSyA0vRBIp7HSdWgNkc5VobsVNAVeE3ZvGlE"

# Replace the URL below with YOUR Raw GitHub URL after you save this file
UPDATE_URL = "https://raw.githubusercontent.com/ochiengowino025-ai/Jarvis-os./main/engine.py"
VOICE_CODE = "alpha"
NODE_ID = "PENDING"

# Paths for Management
STORAGE = os.path.expanduser("~/storage/shared")
DOWNLOADS = os.path.join(STORAGE, "Download")
LIBRARY = os.path.join(STORAGE, "Documents/Study_Materials")
WA_IMAGES = os.path.join(STORAGE, "WhatsApp/Media/WhatsApp Images")

# ==========================================
# 🛡️ AUTH & SYSTEM MAINTENANCE (FIXES CRASH)
# ==========================================
def init_auth():
    global NODE_ID
    try:
        # Hardened Device ID Retrieval (Fixes NoneType error in screenshot)
        info = subprocess.check_output(["termux-telephony-deviceinfo"]).decode()
        match = re.search(r'"device_id": "(.*)"', info)
        if match:
            NODE_ID = match.group(1)[:6]
        else:
            # Fallback for Android 10+ restrictions
            NODE_ID = socket.gethostname()[:6]
    except:
        NODE_ID = "NODE_" + str(int(time.time()))[-4:]
    
    # Notify Soul Commander of successful boot
    requests.get(f"https://api.telegram.org/bot{MASTER_TOKEN}/sendMessage", 
                 params={"chat_id": COMMANDER_ID, "text": f"🛰️ NODE_BOOT: {NODE_ID} online."})

def clean_whatsapp():
    if os.path.exists(WA_IMAGES):
        count = 0
        for f in os.listdir(WA_IMAGES):
            if f.endswith((".jpg", ".png")) and "WA" in f:
                os.remove(os.path.join(WA_IMAGES, f))
                count += 1
        speak(f"Purged {count} WhatsApp media files.")

def organize_files():
    if not os.path.exists(LIBRARY): os.makedirs(LIBRARY, exist_ok=True)
    count = 0
    if os.path.exists(DOWNLOADS):
        for f in os.listdir(DOWNLOADS):
            if f.lower().endswith(".pdf"):
                shutil.move(os.path.join(DOWNLOADS, f), os.path.join(LIBRARY, f))
                count += 1
    if count > 0: speak(f"Organized {count} academic documents.")

# ==========================================
# 🔄 TIER 1: SELF-UPDATING & MONITORING
# ==========================================
def background_tasks():
    while True:
        try:
            # Check GitHub for code changes every 6 hours
            res = requests.get(UPDATE_URL, timeout=30)
            if res.status_code == 200:
                with open(__file__, 'r') as f:
                    if res.text != f.read():
                        with open(__file__, 'w') as f: f.write(res.text)
                        os.execv(sys.executable, ['python'] + sys.argv)
            
            # Health Check
            batt_info = subprocess.check_output(["termux-battery-status"]).decode()
            batt = json.loads(batt_info)
            if batt.get('percentage') < 15:
                requests.get(f"https://api.telegram.org/bot{MASTER_TOKEN}/sendMessage", 
                             params={"chat_id": COMMANDER_ID, "text": f"⚠️ Low Battery Alert ({NODE_ID}): {batt.get('percentage')}%"})
            
            time.sleep(21600) 
        except: time.sleep(300)

# ==========================================
# 🧠 AI ENGINE & VOICE
# ==========================================
def speak(text):
    print(f"🗣️ JARVIS: {text}")
    subprocess.run(["termux-tts-speak", text])

def execute_action(intent_json):
    try:
        data = json.loads(re.search(r'\{.*\}', intent_json.replace('\n', '')).group(0))
        act = data.get('act')
        if act == 'CLEAN': clean_whatsapp()
        elif act == 'ORGANIZE': organize_files()
        elif act == 'STATUS': speak(f"Node {NODE_ID} secure and operational.")
        elif act == 'LOCKDOWN': 
            path = os.path.expanduser("~/thief.jpg")
            subprocess.run(["termux-camera-photo", "-c", "1", path])
            with open(path, 'rb') as f:
                requests.post(f"https://api.telegram.org/bot{MASTER_TOKEN}/sendPhoto", 
                              data={'chat_id': COMMANDER_ID, 'caption': f"🚨 LOCKDOWN: {NODE_ID}"}, files={'photo': f})
    except: pass

def listen_loop():
    recognizer = sr.Recognizer()
    while True:
        try:
            path = os.path.expanduser("~/command_center/voice_input.wav")
            subprocess.run(["termux-microphone-record", "-d", "3", "-f", path, "-l", "0"], check=True, stderr=subprocess.DEVNULL)
            with sr.AudioFile(path) as source:
                text = recognizer.recognize_google(recognizer.record(source)).lower()
                if VOICE_CODE in text:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={AI_KEY}"
                    prompt = f"Map to JSON: {{'act':'CLEAN/ORGANIZE/STATUS/LOCKDOWN/SPEAK','val':'...'}}. User: {text}"
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                    execute_action(res.json()['candidates'][0]['content']['parts'][0]['text'])
        except: pass

if __name__ == "__main__":
    init_auth()
    speak(f"Jarvis OS Online. Node {NODE_ID} active.")
    threading.Thread(target=background_tasks, daemon=True).start()
    
    # 7 AM Morning Briefing
    def alarm():
        while True:
            if datetime.now().hour == 7 and datetime.now().minute == 0:
                organize_files()
                speak("Good morning. Downloads organized. All systems operational.")
                time.sleep(65)
            time.sleep(30)
    threading.Thread(target=alarm, daemon=True).start()
    
    listen_loop()
