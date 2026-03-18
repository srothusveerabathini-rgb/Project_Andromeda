import time
import random
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Config
CHROME_PORT = "9011"

class WhatsAppDriver:
    def __init__(self):
        print(f"[STEALTH] Engaging F-117 WebDriver on Port {CHROME_PORT}...")
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
        
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.implicitly_wait(2)
            print("[STEALTH] Link Established. WhatsApp Web Active.")
        except Exception as e:
            print(f"[ERROR] Could not connect to Chrome. Is it running on port {CHROME_PORT}?")
            sys.exit(1)

    def human_typing(self, element, text):
        """Stochastic typing to bypass Meta heuristics."""
        for char in text:
            element.send_keys(char)
            # 50ms to 150ms per keystroke
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
            unread_badges = self.driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'unread message')]")
            for badge in unread_badges:
                # Navigate up the DOM to find the chat container
                chat_container = badge.find_element(By.XPATH, "../../..")
                chat_container.click()
                time.sleep(1.5) # Wait for chat to load
                
                # Extract the last received message
                messages = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in span.selectable-text")
                if messages:
                    last_msg = messages[-1].text
                    contact_name = self.driver.find_element(By.CSS_SELECTOR, "header span[dir='auto']").text
                    unread_chats.append({"contact": contact_name, "message": last_msg})
        except Exception as e:
            pass # Ignore DOM errors so the loop doesn't crash
            
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

