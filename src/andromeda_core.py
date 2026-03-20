# PROJECT ANDROMEDA: ORCHESTRATOR NODE
import os
import sys
import time
import json
import re
import requests
import logging
from datetime import datetime

# --- CRITICAL PATH FIX ---
# This ensures that Python can find the 'src' folder even if you run this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.driver import AndromedaDriver
from src.tools import AndromedaCentralTools

class AndromedaOrchestrator:
    def __init__(self):
        self.version = "1.0.5-ENTERPRISE"
        self.memory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Brain_Data", "memory.json")
        self.log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs", "andromeda_node.log")
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
        # Configure logging to write to the file that the UI watches
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format="%(asctime)s | [%(levelname)s] | %(message)s",
            datefmt="%H:%M:%S"
        )
        
        self.config = {
            "llm_url": "http://localhost:5001/api/v1/generate",
            "chrome_port": "9011",
            "kill_auth": "NEBULA_2026_X", # Enterprise Authorization Key
            "polling_interval": 5
        }
        
        # State Tracking
        self.awaiting_auth = {} # {contact_id: timestamp}
        self.driver = AndromedaDriver(port=self.config["chrome_port"])
        self.tools = AndromedaCentralTools()
        self._boot_sequence()

    def _boot_sequence(self):
        """Initializes directories and local persistence."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, 'w') as f: json.dump({}, f)
        logging.info(f"[BOOT] {self.version} Neural Loop Online.")
        print(f"[BOOT] {self.version} Orchestrator Active.")

    def _llm_gateway(self, prompt, temperature=0.2):
        """Robust API wrapper for local Phi-3.5 communication."""
        payload = {
            "prompt": prompt,
            "max_length": 200,
            "temperature": temperature,
            "stop_sequence": ["<|end|>", "<|user|>"]
        }
        try:
            response = requests.post(self.config["llm_url"], json=payload, timeout=60)
            response.raise_for_status()
            return response.json()['results'][0]['text'].strip()
        except Exception as e:
            logging.error(f"LLM Gateway Timeout: {e}")
            return None

    def _repair_json(self, raw_string):
        """Enterprise-grade JSON extraction using regex and quote sanitization."""
        try:
            match = re.search(r'\{.*\}', raw_string, re.DOTALL)
            if not match: return None
            
            clean_json = match.group()
            # Fix common SLM errors: replace single quotes with double quotes
            clean_json = clean_json.replace("'", '"')
            return json.loads(clean_json)
        except Exception:
            return None

    def handle_killswitch(self, contact, message):
        """Implements the Sudo Kill State Machine."""
        msg_norm = message.strip().lower()

        # Phase 1: Initiation
        if msg_norm == "sudo kill":
            self.awaiting_auth[contact] = time.time()
            logging.warning(f"Killswitch initiated by {contact}.")
            return "system termination initiated. enter high-level authorization key:"

        # Phase 2: Verification
        if contact in self.awaiting_auth:
            # Check for timeout (30 seconds to enter password)
            if time.time() - self.awaiting_auth[contact] > 30:
                del self.awaiting_auth[contact]
                logging.info(f"Killswitch timeout for {contact}.")
                return "authorization timeout. session restored."

            if message.strip() == self.config["kill_auth"]:
                self.driver.send_reply("identity verified. shutting down all andromeda nodes.")
                logging.error(f"[CRITICAL] Remote Shutdown executed by {contact}.")
                print(f"[CRITICAL] Remote Shutdown executed by {contact}.")
                time.sleep(2)
                os._exit(0) # Immediate process termination
            else:
                del self.awaiting_auth[contact]
                logging.warning(f"Invalid killswitch auth from {contact}.")
                return "invalid credentials. lockdown engaged. resuming normal operations."
        
        return None

    def process_node(self, contact, message):
        """The Dual-Pass ReAct Engine."""
        logging.info(f"[INPUT] Message from {contact}: {message[:30]}...")
        
        # 1. Check for Command Overrides (Killswitch)
        kill_response = self.handle_killswitch(contact, message)
        if kill_response: return kill_response

        # 2. Pass 1: Logical Routing (Reasoning)
        router_prompt = (
            f"<|system|>\nYou are the Andromeda Logic Router. Available tools: "
            f"dispatch_email, verify_business, scout_leads, manage_schedule, chat. "
            f"Output ONLY JSON in this format: {{\"tool\": \"name\", \"args\": {{}}}}<|end|>\n"
            f"<|user|>\n{message}<|end|>\n<|assistant|>\n"
        )
        
        logging.info("[THOUGHT] Pass 1: Determining optimal tool sequence...")
        raw_output = self._llm_gateway(router_prompt, temperature=0.1)
        action = self._repair_json(raw_output)
        
        tool_name = action.get("tool", "chat") if action else "chat"
        args = action.get("args", {}) if action else {}
        logging.info(f"[ACTION] Selected Tool: {tool_name}")

        # 3. Action: Tool Execution
        if tool_name == "verify_business":
            observation = self.tools.verify_business(args.get("company_name", ""))
        elif tool_name == "dispatch_email":
            observation = self.tools.dispatch_email(args.get("target", ""), args.get("instruction", ""))
        elif tool_name == "scout_leads":
            observation = self.tools.scout_leads(args.get("niche", ""))
        elif tool_name == "manage_schedule":
            observation = self.tools.manage_schedule(args.get("action", ""), args.get("detail", ""), args.get("date_str"))
        else:
            observation = args.get("text", "Logic gate re-calibrated. Standing by.")

        logging.info(f"[OBSERVATION] {observation}")

        # 4. Pass 2: Response Synthesis
        synth_prompt = (
            f"<|system|>\nYou are Andromeda-01. Professional Agent. "
            f"Current Context: User said '{message}'. Tool Result: '{observation}'. "
            f"Response constraints: lowercase only, max 15 words.<|end|>\n<|assistant|>\n"
        )
        
        logging.info("[THOUGHT] Pass 2: Synthesizing output...")
        final_response = self._llm_gateway(synth_prompt, temperature=0.7) or observation
        logging.info(f"[OUTPUT] Synthesized: {final_response}")
        return final_response

    def run(self):
        """The Resilient Execution Loop."""
        while True:
            try:
                # Check if driver is still responsive
                if not hasattr(self.driver, 'driver'):
                    logging.error("Driver connection lost. Attempting reconnection...")
                    self.driver = AndromedaDriver(port=self.config["chrome_port"])
                
                inbox = self.driver.get_unread_messages()
                for task in inbox:
                    response = self.process_node(task['contact'], task['message'])
                    self.driver.send_reply(response)
                    
            except Exception as e:
                logging.error(f"Critical Runtime Glitch: {e}")
                time.sleep(10) # Cooling period before retry
            
            time.sleep(self.config["polling_interval"])

if __name__ == "__main__":
    node = AndromedaOrchestrator()
    node.run()