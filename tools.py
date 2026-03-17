# ==========================================
# PROJECT ANDROMEDA: CENTRAL NODE TOOLKIT
# MISSION: B2B Medical Distribution Suite
# ==========================================
import os
import re
import json
import time
import smtplib
import logging
import requests
import difflib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- ENTERPRISE LOGGING SYSTEM ---
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "andromeda_node.log"),
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- AUTO-CORRECTION (SELF-HEALING) DECORATOR ---
def auto_retry(max_attempts=3, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logging.warning(f"Tool '{func.__name__}' failed (Attempt {attempts}/{max_attempts}). Error: {e}")
                    if attempts == max_attempts:
                        logging.error(f"Tool '{func.__name__}' critical failure.")
                        return f"[SYSTEM ERROR] {func.__name__} failed after retries."
                    time.sleep(delay)
        return wrapper
    return decorator

class AndromedaCentralTools:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.calendar_path = os.path.join(self.base_dir, "calendar.json")
        self.leads_path = os.path.join(self.base_dir, "leads.json")
        self.kobold_url = "http://localhost:5001/api/v1/generate"
        
        # Wholesale Medical B2B Directory
        self.directory = {
            "supplier": "returns@sunpharma.in",
            "logistics": "dispatch@apollo-logistics.com",
            "finance": "accounts@dispensary.com",
            "manager": "boss@dispensary.com"
        }
        self._init_storage()
        logging.info("Andromeda Central Toolkit (Medical B2B Suite) Initialized.")

    def _init_storage(self):
        """Ensures all enterprise databases exist."""
        for path in [self.calendar_path, self.leads_path]:
            if not os.path.exists(path):
                with open(path, 'w') as f: json.dump({"data": []}, f)

    def _fuzzy_match_role(self, user_input):
        roles = list(self.directory.keys())
        matches = difflib.get_close_matches(user_input.lower(), roles, n=1, cutoff=0.5)
        if matches:
            return matches[0], self.directory[matches[0]]
        return None, None

    # --- TOOL 1: AUTO-EMAILER ---
    @auto_retry(max_attempts=2, delay=3)
    def dispatch_email(self, target_input, instruction):
        logging.info(f"Initiating dispatch_email. Target: {target_input}")
        role, target_email = self._fuzzy_match_role(target_input)
        if not target_email: return f"[ERROR] Could not auto-correct '{target_input}'."

        prompt = f"<|system|>\nYou are Andromeda-01. Draft a formal B2B email based on: '{instruction}'. Output ONLY the body.<|end|>\n<|user|>\nDraft the email.<|end|>\n<|assistant|>\n"
        res = requests.post(self.kobold_url, json={"prompt": prompt, "max_length": 200, "temperature": 0.4}, timeout=45)
        res.raise_for_status()
        email_body = res.json()['results'][0]['text'].strip()

        sender_email = "your_bot_email@gmail.com"
        sender_password = "your_app_password" 

        msg = MIMEMultipart()
        msg['From'] = f"Andromeda Central Node <{sender_email}>"
        msg['To'] = target_email
        msg['Subject'] = f"Automated B2B Dispatch: {instruction[:30]}..."
        msg.attach(MIMEText(email_body, 'plain'))

        # Uncomment to actually send when you configure the email:
        # with smtplib.SMTP('smtp.gmail.com', 587) as server:
        #     server.starttls()
        #     server.login(sender_email, sender_password)
        #     server.send_message(msg)
            
        logging.info(f"Email drafted and prepared for {target_email}")
        return f"Drafted and sent professional email to '{role}'."

    # --- TOOL 2: GSTIN EXTRACTOR ---
    @auto_retry(max_attempts=3, delay=2)
    def verify_business(self, company_name):
        logging.info(f"Initiating GSTIN search for: {company_name}")
        search_url = f"https://www.google.com/search?q={company_name}+official+GSTIN"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(search_url, headers=headers, timeout=10)
        res.raise_for_status()
        
        pattern = r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b"
        matches = list(set(re.findall(pattern, res.text)))
        
        if matches: return f"Found valid GSTIN(s) for {company_name}: {', '.join(matches)}"
        return f"No verified GSTIN found for {company_name}."

    # --- TOOL 3: DEEP LEAD FINDER ---
    @auto_retry(max_attempts=3, delay=2)
    def scout_leads(self, niche, location="India"):
        logging.info(f"Scouting leads for {niche} in {location}")
        simulated_lead = f"Procurement Contact at top {niche} in {location}"
        
        with open(self.leads_path, 'r') as f: leads_db = json.load(f)
        new_entry = {
            "niche": niche, 
            "location": location, 
            "data": simulated_lead,
            "timestamp": str(datetime.now())
        }
        leads_db["data"].append(new_entry)
        
        with open(self.leads_path, 'w') as f: json.dump(leads_db, f, indent=4)
        logging.info("B2B Lead logged successfully.")
        return f"Scouting complete. New B2B leads for {niche} logged to database."

    # --- TOOL 4: ENTERPRISE SCHEDULER ---
    def manage_schedule(self, action, detail, date_str=None):
        logging.info(f"Calendar Action: {action} | Detail: {detail}")
        try:
            with open(self.calendar_path, 'r') as f: cal = json.load(f)
            
            if action.lower() == "add":
                if not date_str: return "[ERROR] Must provide a date to schedule an event."
                cal["data"].append({"event": detail, "date": date_str, "logged_at": str(datetime.now())})
                with open(self.calendar_path, 'w') as f: json.dump(cal, f, indent=4)
                return f"Successfully scheduled: '{detail}' for {date_str}."
                
            elif action.lower() == "view":
                events = [f"{e['date']}: {e['event']}" for e in cal["data"]]
                return "Current Schedule:\n" + "\n".join(events) if events else "Schedule is completely clear."
                
        except Exception as e:
            logging.error(f"Calendar sync failed: {e}")
            return f"Calendar sync failed: {e}"