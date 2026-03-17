# PROJECT ANDROMEDA
# IMPORTS
import os
import sys
import time
import json
import random
import threading
import subprocess
import requests
import pygame
import ctypes
import win32gui
import win32con
import keyboard
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

#CONFIG & PATH ARCHITECTURE

try: 
    ctypes.windll.user32.SetProcessDPIAware()
except Exception: 
    pass
user32 = ctypes.windll.user32
try:
    SCREEN_WIDTH = user32.GetSystemMetrics(0)
    POS_X, POS_Y = SCREEN_WIDTH - 420, 50 
except Exception:
    SCREEN_WIDTH, POS_X, POS_Y = 1920, 1500, 50

SYSTEM_NAME = "ANDROMEDA-01"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAIN_DIR = os.path.join(BASE_DIR, "Brain_Data")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
MEMORY_PATH = os.path.join(BRAIN_DIR, "memory.json")
AUDIT_LOG = os.path.join(BASE_DIR, "andromeda_audit.log")
CHROME_PROFILE = os.path.join(BASE_DIR, "ChromeProfile")

KOBOLD_EXE = os.path.join(BASE_DIR, "koboldcpp-nocuda.exe")
MODEL_PATH = os.path.join(BASE_DIR, "phi-3.5-mini-instruct-q4.gguf") 
KOBOLD_URL = "http://localhost:5001/api/v1/generate"
CHROME_PORT = "9011"

if not os.path.exists(BRAIN_DIR):
    os.makedirs(BRAIN_DIR)
    print(f"[BOOT] Neural Storage initialized dynamically at: {BRAIN_DIR}")

# BLOCK 3: CONTEXT-AWARE NEURAL ENGINE

class AndromedaBrain:
    def __init__(self):
        self.memory_file = MEMORY_PATH
        self.session = requests.Session()
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def generate_reply(self, contact, message, tone_override="efficient and professional"):
        history = self.memory.get(contact, [])[-3:]
        history_str = "".join([f"<|user|>\n{r}<|end|>\n<|assistant|>\n{t}<|end|>\n" for r, t in history])
        
        system_prompt = f"You are {SYSTEM_NAME}, an autonomous enterprise AI. Tone: {tone_override}. Keep responses under 15 words. Lowercase only."
        full_prompt = f"<|system|>\n{system_prompt}<|end|>\n{history_str}<|user|>\n{message}<|end|>\n<|assistant|>\n"
        
        payload = {
            "prompt": full_prompt,
            "max_length": 60,
            "temperature": 0.7,
            "stop_sequence": ["<|end|>", "<|user|>"]
        }
        
        try:
            res = self.session.post(KOBOLD_URL, json=payload, timeout=90)
            reply = res.json()['results'][0]['text'].strip()
            
            if contact not in self.memory:
                self.memory[contact] = []
            self.memory[contact].append((message, reply))
            self.save_memory()
            
            return reply
        except Exception:
            return "Sorry for interrupting, can you please repeat that"