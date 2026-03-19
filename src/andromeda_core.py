# PROJECT ANDROMEDA
# BLOCK 1: THE ARSENAL (IMPORTS)
import os
import sys
import time
import json
import random
import re
import requests
import logging
import ctypes
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# IMPORT THE TOOL SUITE (Ensuring relative pathing works)
try:
    from src.tools import AndromedaCentralTools
except ImportError:
    from tools import AndromedaCentralTools

# BLOCK 2: SYSTEM ARCHITECTURE & PATHS
try: 
    ctypes.windll.user32.SetProcessDPIAware()
except Exception: 
    pass

SYSTEM_NAME = "ANDROMEDA-01"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAIN_DIR = os.path.join(BASE_DIR, "Brain_Data")
MEMORY_PATH = os.path.join(BRAIN_DIR, "memory.json")
KOBOLD_URL = "http://localhost:5001/api/v1/generate"
CHROME_PORT = "9011"

if not os.path.exists(BRAIN_DIR):
    os.makedirs(BRAIN_DIR)
    print(f"[BOOT] Neural Storage initialized at: {BRAIN_DIR}")

# BLOCK 3: THE ReAct NEURAL ENGINE (Reason + Act + Synthesize)
class AndromedaBrain:
    def __init__(self):
        self.memory_file = MEMORY_PATH
        self.session = requests.Session()
        self.tools = AndromedaCentralTools()
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

    def _llm_call(self, prompt, temp=0.2, max_tokens=150):
        """Internal helper for local Phi-3.5 communication."""
        payload = {
            "prompt": prompt,
            "max_length": max_tokens,
            "temperature": temp,
            "stop_sequence": ["<|end|>", "<|user|>"]
        }
        try:
            res = self.session.post(KOBOLD_URL, json=payload, timeout=60)
            return res.json()['results'][0]['text'].strip()
        except Exception as e:
            return None

    def generate_reply(self, contact, message):
        """Dual-Pass Loop: Decides on tool (Pass 1) -> Executes -> Summarizes (Pass 2)"""
        
        # --- PASS 1: REASONING (The Router) ---
        router_system = (
            "Output ONLY JSON. Tools: 'dispatch_email', 'verify_business', 'scout_leads', 'manage_schedule', 'chat'. "
            "Format: {\"tool\": \"name\", \"args\": {}}"
        )
        pass1_prompt = f"<|system|>\n{router_system}<|end|>\n<|user|>\n{message}<|end|>\n<|assistant|>\n"
        
        raw_json = self._llm_call(pass1_prompt, temp=0.1)
        
        try:
            json_str = re.search(r'\{.*\}', raw_json, re.DOTALL).group()
            data = json.loads(json_str)
            tool_name = data.get("tool", "chat")
            args = data.get("args", {})
        except:
            tool_name = "chat"
            args = {"text": "re-calibrating logic gates..."}

        # --- ACTION: TOOL EXECUTION ---
        if tool_name == "verify_business":
            observation = self.tools.verify_business(args.get("company_name"))
        elif tool_name == "dispatch_email":
            observation = self.tools.dispatch_email(args.get("target"), args.get("instruction"))
        elif tool_name == "scout_leads":
            observation = self.tools.scout_leads(args.get("niche"))
        elif tool_name == "manage_schedule":
            observation = self.tools.manage_schedule(args.get("action"), args.get("detail"), args.get("date_str"))
        else:
            observation = args.get("text", "standing by for tasks.")

        # --- PASS 2: SYNTHESIS (Natural Language) ---
        synthesis_system = (
            f"You are Andromeda-01. User: '{message}'. Result: '{observation}'. "
            "Write a professional, 1-sentence WhatsApp reply. lowercase only. under 15 words."
        )
        pass2_prompt = f"<|system|>\n{synthesis_system}<|end|>\n<|assistant|>\n"
        
        final_msg = self._llm_call(pass2_prompt, temp=0.7) 
        
        if not final_msg: final_msg = observation

        if contact not in self.memory: self.memory[contact] = []
        self.memory[contact].append({"msg": message, "resp": final_msg, "time": str(datetime.now())})
        self.save_memory()

        return final_msg

# BLOCK 4: F-117 STEALTH DRIVER
class AndromedaDriver:
    def __init__(self):
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
        
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.implicitly_wait(2)
            print("[BOOT] Stealth Driver Online.")
        except Exception:
            print(f"[CRITICAL] Chrome instance not found on port {CHROME_PORT}")
            sys.exit(1)

    def stealth_click(self, element):
        """Physics-based movement to bypass Meta's anti-bot system."""
        try:
            ActionChains(self.driver).move_to_element_with_offset(
                element, random.randint(-15, 15), random.randint(-10, 10)
            ).perform()
            time.sleep(random.uniform(0.05, 0.1))
            
            ActionChains(self.driver).move_to_element(element).perform()
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def human_typing(self, element, text):
        """Stochastic typing rhythm."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15)) 
            if random.random() < 0.02 and char.isalpha():
                element.send_keys(random.choice(['a', 'e', 's', 't']))
                time.sleep(random.uniform(0.1, 0.2))
                element.send_keys(Keys.BACKSPACE)

    def get_unread_messages(self):
        unread_chats = []
        try:
            unread_badges = self.driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'unread message')]")
            for badge in unread_badges:
                chat_container = badge.find_element(By.XPATH, "../../..")
                self.stealth_click(chat_container)
                time.sleep(1.5) 
                messages = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in span.selectable-text")
                if messages:
                    last_msg = messages[-1].text
                    contact_name = self.driver.find_element(By.CSS_SELECTOR, "header span[dir='auto']").text
                    unread_chats.append({"contact": contact_name, "message": last_msg})
        except Exception:
            pass 
        return unread_chats

    def send_reply(self, reply_text):
        try:
            chat_box = self.driver.find_element(By.XPATH, "//div[@title='Type a message']")
            self.stealth_click(chat_box)
            self.human_typing(chat_box, reply_text)
            chat_box.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"[ERROR] Chatbox interaction failed: {e}")