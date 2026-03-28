import time, random, numpy as np, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _get_bezier_points(start, end, c1, c2, num_points=12):
    t = np.linspace(0, 1, num_points).reshape(-1, 1)
    s, e, c1, c2 = np.array(start), np.array(end), np.array(c1), np.array(c2)
    return (1-t)**3 * s + 3*(1-t)**2 * t * c1 + 3*(1-t) * t**2 * c2 + t**3 * e

class AndromedaDriver:
    def __init__(self, port="9011"):
        opt = Options()
        opt.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        self.driver = webdriver.Chrome(options=opt)

    def _phantom_glide(self, element):
        try:
            rect = self.driver.execute_script("return arguments[0].getBoundingClientRect();", element)
            tx, ty = int(rect['left'] + rect['width']/2), int(rect['top'] + rect['height']/2)
            points = _get_bezier_points([0,0], [tx, ty], [100, 200], [tx-50, ty-50])
            actions = ActionChains(self.driver)
            cx, cy = 0, 0
            for (px, py) in points:
                actions.move_by_offset(int(px-cx), int(py-cy))
                cx, cy = int(px), int(py)
            actions.perform()
        except: pass

    def human_typing(self, element, text):
        for char in text:
            if random.random() < 0.015:
                element.send_keys(random.choice('qwertyuiop'))
                time.sleep(0.2); element.send_keys(Keys.BACKSPACE)
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.12))

    def get_unread_messages(self):
        # THE ISOLATION PROTOCOL: Ignore the sidebar, target the chat list only
        js = """
            let chatContainer = document.getElementById('pane-side') || document.querySelector('div[aria-label="Chat list"]');
            if (!chatContainer) return null;

            let badges = chatContainer.querySelectorAll('span[aria-label*="unread"]');
            for (let badge of badges) {
                let label = badge.getAttribute('aria-label').toLowerCase();
                if (label.includes("message")) {
                    return badge.closest('div[role="row"]') || badge.closest('div[role="gridcell"]') || badge;
                }
            }
            return null;
        """
        try:
            target = self.driver.execute_script(js)
            if target:
                # Glide the phantom mouse to the exact coordinates
                self._phantom_glide(target)
                time.sleep(0.5) 
                
                # THE APEX BYPASS: Raw OS-Level Pixel Click
                # Physically clicks the monitor coordinates to bypass React event blockers
                actions = ActionChains(self.driver)
                actions.move_to_element(target).click().perform()
                
                # SURVIVAL PROTOCOL: Wait up to 10 seconds for the header to render
                header_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//header//span[@dir="auto"]'))
                )
                name = header_element.text
                
                # THE EXTRACTION PATCH: Use dir="ltr" to capture the actual message text
                # We target 'message-in' to ignore our own sent messages
                msgs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'message-in')]//span[@dir='ltr']")
                
                if msgs:
                    msg_text = msgs[-1].text
                else:
                    # Fallback if it's an image, voice note, or the DOM didn't load yet
                    msg_text = "[Media]"
                
                return [{"contact": name, "message": msg_text}]
                
        except Exception as e: 
            logging.error(f"Vision Fault: {e}")
        return []
        
    def send_reply(self, text):
        try:
            box = self.driver.find_element(By.XPATH, '//div[@title="Type a message" or @role="textbox"]')
            self._phantom_glide(box); box.click()
            self.human_typing(box, text)
            time.sleep(0.5); box.send_keys(Keys.ENTER)
        except: pass