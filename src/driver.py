import time
import random
import math
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class AndromedaDriver:
    def __init__(self, port="9011"):
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.implicitly_wait(8)
            print("[SYSTEM] Stealth Driver Active: Bézier Navigation Verified.")
        except Exception:
            sys.exit(1)

    def _calculate_bezier(self, p0, p1, p2, t):
        """
        Quadratic Bézier Formula:
        $$B(t) = (1-t)^2 P_0 + 2(1-t)t P_1 + t^2 P_2$$
        """
        x = (1 - t)**2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
        y = (1 - t)**2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
        return int(x), int(y)

    def _human_glide(self, element):
        action = ActionChains(self.driver)
        p0 = (random.randint(-300, 300), random.randint(-300, 300))
        p2 = (random.randint(-5, 5), random.randint(-5, 5)) 
        p1 = (random.randint(-150, 150), random.randint(-150, 150))
        steps = random.randint(15, 25)
        for i in range(1, steps + 1):
            t = i / steps
            t_eased = t * t * (3 - 2 * t) # Smoothstep easing
            target_x, target_y = self._calculate_bezier(p0, p1, p2, t_eased)
            action.move_to_element_with_offset(element, target_x, target_y).perform()
            time.sleep(random.uniform(0.01, 0.02))

    def _stealth_click(self, element):
        try:
            self._human_glide(element)
            time.sleep(random.uniform(0.1, 0.3))
            action = ActionChains(self.driver)
            action.click_and_hold(element).perform()
            time.sleep(random.uniform(0.08, 0.15))
            action.release(element).perform()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def human_typing(self, element, text):
        """Simulates human typing: Wrong Key -> Backspace -> Correct Key."""
        for char in text:
            # 1.5% chance to perform a 'Wrong Key' typo
            if random.random() < 0.015 and char.isalpha():
                element.send_keys(random.choice(['q','w','e','a','s','z','x']))
                time.sleep(random.uniform(0.3, 0.5)) # Frustration pause
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.1, 0.2))
                element.send_keys(char) # Type the correct character
            else:
                element.send_keys(char)
            
            # Rhythmic delay + Cognitive pause after punctuation
            delay = random.uniform(0.05, 0.18)
            if char in [".", ",", "!", "?"]:
                delay += random.uniform(0.4, 0.8)
            time.sleep(delay)

    def get_unread_messages(self):
        unread_data = []
        try:
            badges = self.driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'unread message')]")
            for badge in badges:
                chat_row = badge.find_element(By.XPATH, "../../..")
                self._stealth_click(chat_row)
                time.sleep(1.5)
                bubbles = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in span.selectable-text")
                if bubbles:
                    text = bubbles[-1].text
                    contact = self.driver.find_element(By.CSS_SELECTOR, "header span[dir='auto']").text
                    unread_data.append({"contact": contact, "message": text})
        except Exception:
            pass
        return unread_data

    def send_reply(self, reply_text):
        try:
            chat_box = self.driver.find_element(By.XPATH, "//div[@title='Type a message']")
            self._stealth_click(chat_box)
            self.human_typing(chat_box, reply_text)
            time.sleep(random.uniform(0.5, 1.0))
            chat_box.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"[ERROR] Dispatch failed: {e}")