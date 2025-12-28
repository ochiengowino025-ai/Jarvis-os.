import requests, time, os, threading, subprocess, json, sys, re, shutil, socket
import speech_recognition as sr
from datetime import datetime

# ==========================================
# 🔑 SOUL COMMANDER CONFIG
# ==========================================
MASTER_TOKEN = "8555656962:AAG2GZv15siG-3gXTeqPXAWNNF5Z3jSn3Og"
COMMANDER_ID = "6628636143"
AI_KEY = "AIzaSyA0vRBIp7HSdWgNkc5VobsVNAVeE3ZvGlE"
# REPLACE WITH YOUR RAW GITHUB URL AFTER SAVING
UPDATE_URL = "https://raw.githubusercontent.com/ochiengowino025-ai/Jarvis-os./main/engine.py"
VOICE_CODE = "alpha"
NODE_ID = "PENDING"

# Paths
STORAGE = os.path.expanduser("~/storage/shared")
DOWNLOADS = os.path.join(STORAGE, "Download")
LIBRARY = os.path.join(STORAGE, "Documents/Study_Materials")
WA_IMAGES = os.path.join(STORAGE, "WhatsApp/Media/WhatsApp Images")

# ==========================================
# 🛡️ AUTH FIX (NoneType Check)
# ==========================================
def init_auth():
    global NODE_ID
    try:
        # Fix for Screenshot 125870.jpg
        info = subprocess.check_output(["termux-telephony-deviceinfo"]).decode()
        match = re.search(r'"device_id": "(.*)"', info)
        if match:
            NODE_ID = match.group(1)[:6]
        else:
            NODE_ID = socket.gethostname()[:6]
    except:
        NODE_ID = "NODE_" + str(int(time.time()))[-4:]
    
    requests.get(f"https://api.telegram.org/bot{MASTER_TOKEN}/sendMessage", 
                 params={"chat_id": COMMANDER_ID, "text": f"🛰️ NODE_BOOT: {NODE_ID} online."})

def clean_whatsapp():
    if os.path.exists(WA_IMAGES):
        for f in os.listdir(WA_IMAGES):
            if f.endswith((".jpg", ".png")) and "WA" in f:
                os.remove(os.path.join(WA_IMAGES, f))
    print("WhatsApp Cleaned.")

def organize_files():
    if not os.path.exists(LIBRARY): os.makedirs(LIBRARY, exist_ok=True)
    if os.path.exists(DOWNLOADS):
        for f in os.listdir(DOWNLOADS):
            if f.lower().endswith(".pdf"):
                shutil.move(os.path.join(DOWNLOADS, f), os.path.join(LIBRARY, f))

def speak(text):
    print(f"🗣️ JARVIS: {text}")
    subprocess.run(["termux-tts-speak", text])

def background_tasks():
    while True:
        try:
            res = requests.get(UPDATE_URL, timeout=30)
            if res.status_code == 200:
                with open(__file__, 'r') as f:
                    if res.text != f.read():
                        with open(__file__, 'w') as f: f.write(res.text)
                        os.execv(sys.executable, ['python'] + sys.argv)
            time.sleep(21600)
        except: time.sleep(300)

if __name__ == "__main__":
    init_auth()
    speak(f"Jarvis OS Online. Node {NODE_ID} active.")
    threading.Thread(target=background_tasks, daemon=True).start()
    # Continuous listening logic would go here
    while True: time.sleep(10)
