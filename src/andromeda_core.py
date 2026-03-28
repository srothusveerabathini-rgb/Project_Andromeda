import os, sys, time, json, re, requests, logging

# --- PATHING ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.driver import AndromedaDriver
from src.tools import AndromedaCentralTools

# --- FAULT TOLERANCE: The Repairer ---
def auto_retry(max_attempts=3, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(max_attempts):
                try: return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Retrying {func.__name__} due to: {e}")
                    time.sleep(delay)
            return "[ERROR] Tool critical failure."
        return wrapper
    return decorator

class AndromedaOrchestrator:
    def __init__(self):
        log_dir = os.path.join(os.path.dirname(__file__), "Logs")
        os.makedirs(log_dir, exist_ok=True)
            
        self.log_path = os.path.join(log_dir, "andromeda_node.log")
        logging.basicConfig(filename=self.log_path, level=logging.INFO, format="%(asctime)s | %(message)s")
        
        self.driver = AndromedaDriver(port="9011")
        
        # --- i3 STABILITY PATCH ---
        try:
            self.driver.driver.set_page_load_timeout(30)
            self.driver.driver.set_script_timeout(30)
        except: pass

        self.tools = AndromedaCentralTools()
        self.auth_key = "NEBULA_2026_X"
        self.awaiting_auth = {}

    def _repair_json(self, raw):
        try:
            clean = re.sub(r'```json\s*|```', '', raw).strip()
            match = re.search(r'\{.*\}', clean, re.DOTALL)
            return json.loads(match.group().replace("'", '"')) if match else None
        except: return None

    # Apply your auto_retry to all Neural Engine calls!
    @auto_retry(max_attempts=3, delay=2)
    def generate_llm_response(self, payload, timeout=45):
        res = requests.post("http://localhost:5001/api/v1/generate", json=payload, timeout=timeout)
        return res.json()['results'][0]['text']

    def handle_killswitch(self, contact, msg):
        if msg.strip().lower() == "sudo kill":
            self.awaiting_auth[contact] = time.time()
            return "system termination initiated. enter high-level authorization key:"
        if contact in self.awaiting_auth:
            if time.time() - self.awaiting_auth[contact] > 30:
                del self.awaiting_auth[contact]; return "auth timeout."
            if msg.strip() == self.auth_key:
                self.driver.send_reply("[CRITICAL] SHUTTING DOWN."); os._exit(0)
            del self.awaiting_auth[contact]; return "invalid auth. resuming loop."
        return None

    def process_task(self, contact, msg):
        logging.info(f"[INPUT] {contact}: {msg}")
        if kill := self.handle_killswitch(contact, msg): return kill

        # 1. THE ZERO-RAM EXTRACTOR (Bypass the LLM entirely for speed)
        msg_clean = msg.lower()
        extracted_company = "NONE"
        
        # Instantly slice the text without using AI
        if "gstin of" in msg_clean:
            extracted_company = msg_clean.split("gstin of ")[-1].strip()
            print(f"[REASONING] Zero-RAM Bypass. Target Entity: {extracted_company}")
            obs = self.tools.verify_business(extracted_company)
            
        elif "scout" in msg_clean or "leads" in msg_clean:
            extracted_company = msg_clean.split("for ")[-1].strip() if "for " in msg_clean else "steel"
            obs = self.tools.scout_leads(extracted_company)
            
        elif "email" in msg_clean or "dispatch" in msg_clean:
            obs = self.tools.dispatch_email("manager", msg)
            
        else:
            obs = "Logic calibrated. Andromeda is standing by for instructions."

        # 2. SYNTHESIS: Final Professional Reply
        try:
            synth = f"<|system|>max 15 words. Be professional.<|end|>\n<|user|>Action result: {obs}<|end|>\n<|assistant|>"
            payload_synth = {"prompt": synth, "max_length": 40, "stop_sequence": ["<|end|>"], "temperature": 0.3}
            final = self.generate_llm_response(payload_synth, timeout=40)
            if final == "[ERROR] Tool critical failure.": return obs.lower()[:100]
            return final.strip().lower()
        except: 
            return obs.lower()[:100]

    def main_loop(self):
        logging.info("[SUCCESS] ANDROMEDA SYSTEM ONLINE.")
        print("[ACTIVE] Monitoring WhatsApp on Port 9011...")
        while True:
            try:
                unread = self.driver.get_unread_messages()
                for t in unread:
                    reply = self.process_task(t['contact'], t['message'])
                    self.driver.send_reply(reply)
            except Exception as e: 
                err_msg = str(e).lower()
                logging.error(f"Runtime Glitch: {err_msg}")
                
                # --- ENTERPRISE AUTO-REVIVE ---
                if "invalid session id" in err_msg or "disconnected" in err_msg or "closed" in err_msg:
                    print("\n[CRITICAL] WhatsApp Connection Severed. Auto-Reviving Session...")
                    try:
                        self.driver = AndromedaDriver(port="9011")
                        self.driver.driver.set_page_load_timeout(30)
                        print("[SUCCESS] Session Restored. Resuming Operations.\n")
                    except Exception as revive_e:
                        print(f"[FATAL] Could not revive session: {revive_e}")
                        time.sleep(10) # Prevent rapid crash looping
            time.sleep(5)

if __name__ == "__main__":
    try: AndromedaOrchestrator().main_loop()
    except KeyboardInterrupt: print("\n[SYSTEM] Powering down.")