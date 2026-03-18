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

# CONFIG & PATH ARCHITECTURE

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

# BLOCK 4:

class AndromedaDriver:
    def __init__(self):
        print("[BOOT] Engaging Stealth WebDriver on Port 9011...")
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
        
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.implicitly_wait(2)
            print("[BOOT] Chrome Link Established. WhatsApp Web Active.")
        except Exception as e:
            print(f"[ERROR] Could not connect to Chrome. Is it running with --remote-debugging-port={CHROME_PORT}?")
            sys.exit(1)

    def human_typing(self, element, text):
        """Stochastic typing to bypass Meta heuristics."""
        for char in text:
            element.send_keys(char)
            # The Admin Latency: 50ms to 150ms per keystroke
            time.sleep(random.uniform(0.05, 0.15)) 
            
            # 2% chance to make a typo and backspace it
            if random.random() < 0.02 and char.isalpha():
                element.send_keys(random.choice(['a', 'e', 's', 't']))
                time.sleep(random.uniform(0.1, 0.2))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.3))

    def get_unread_messages(self):
        """Scans the DOM for the unread message badge."""
        unread_chats = []
        try:
            # WhatsApp DOM classes change, but aria-labels usually remain stable
            unread_badges = self.driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'unread message')]")
            for badge in unread_badges:
                # Navigate up the DOM to find the chat container
                chat_container = badge.find_element(By.XPATH, "../../..")
                chat_container.click()
                time.sleep(1) # Wait for chat to load
                
                # Extract the last received message
                messages = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in span.selectable-text")
                if messages:
                    last_msg = messages[-1].text
                    contact_name = self.driver.find_element(By.CSS_SELECTOR, "header span[dir='auto']").text
                    unread_chats.append({"contact": contact_name, "message": last_msg})
        except Exception as e:
            pass # Keep it moving, don't crash on DOM errors
            
        return unread_chats

    def send_reply(self, reply_text):
        """Targets the chatbox and executes human typing."""
        try:
            chat_box = self.driver.find_element(By.XPATH, "//div[@title='Type a message']")
            chat_box.click()
            self.human_typing(chat_box, reply_text)
            chat_box.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"[SYS_WARNING] Could not locate chat box: {e}")