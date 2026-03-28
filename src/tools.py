import os, json, re, requests, time, smtplib, logging, difflib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

class AndromedaCentralTools:
    
    def __init__(self):
        # 1. Define the Neural Engine URL for email drafting
        self.kobold_url = "http://localhost:5001/api/v1/generate"
        
        # 2. Define the Contact Directory for dispatching emails
        self.directory = {
            "Target Email": "example@email.com",
        }
        
        # 3. Main WhatsApp Driver reference (for focus management)
        # We don't initialize a new driver here; core_proc handles the main instance.
        print("[TOOLS] Andromeda Arsenal Loaded. Awaiting Neural Commands.")

    @auto_retry()
    def scout_leads(self, niche, location="Hyderabad"):
        logging.info(f"Scouting {niche} in {location}")
        query = f"{niche}+steel+suppliers+in+{location}+contact+email" # Hardened query
        res = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        
        # Regex for emails
        found_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', res.text)
        
        # FILTER: Remove DuckDuckGo meta-emails and duplicates
        blacklist = ['duckduckgo.com', 'w3.org', 'example.com', 'google.com']
        emails = [e for e in list(set(found_emails)) if not any(b in e for b in blacklist)]
        
        if emails:
            return f"Found {len(emails)} leads for {niche} in {location}: {', '.join(emails[:3])}"
        return "No valid business leads found on the first page."

    @auto_retry()
    def dispatch_email(self, target_input, instruction):
        logging.info(f"Initiating email dispatch to {target_input}")
        roles = list(self.directory.keys())
        match = difflib.get_close_matches(target_input.lower(), roles, n=1)
        target_email = self.directory[match[0]] if match else "ramesh.vb2008@gmail.com"

        prompt = f"<|system|>Draft B2B email body for: {instruction}<|end|>\n<|assistant|>"
        body = requests.post(self.kobold_url, json={"prompt": prompt, "max_length": 150}, timeout=45).json()['results'][0]['text']

        sender_email = "Enter senders email here"
        sender_password = "Enter sender's app password here"

        msg = MIMEMultipart()
        msg['From'] = f"Andromeda Central <{sender_email}>"
        msg['To'] = target_email
        msg['Subject'] = f"Automated Dispatch: {instruction[:20]}"
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return f"successfully dispatched email to {target_email}."


    @auto_retry(max_attempts=3, delay=2)
    def verify_business(self, company):
        # GUARDRAIL: If the LLM hallucinates and sends an empty string, STOP.
        if not company or company.strip().upper() == "NONE":
            return "[ERROR] Neural Engine failed to provide a valid target company."

        try:
            print(f"[SCALPEL] Executing Zero-RAM Bing sweep for: {company}...")
            
            # Bing search URL
            query = f"GSTIN+of+{company}".replace(" ", "+")
            url = f"https://www.bing.com/search?q={query}"
            
            # A modern User-Agent is critical so Bing thinks we are a real browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            
            # Execute a hyper-fast request (NO SELENIUM REQUIRED)
            res = requests.get(url, headers=headers, timeout=10)
            
            # REGEX EXTRACTION directly from the raw HTML text
            pattern = r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}"
            matches = list(set(re.findall(pattern, res.text)))
            
            if not matches:
                return f"Verification Complete: No GSTIN found for {company} in public databases."

            # TELANGANA PRIORITY LOGIC (36 prefix)
            for gstin in matches:
                if gstin.startswith("36"):
                    print(f"[SUCCESS] Telangana GSTIN Acquired: {gstin}")
                    return f"GSTIN for {company} (Telangana): {gstin}"
            
            # FALLBACK: First matched GSTIN
            print(f"[SUCCESS] GSTIN Acquired: {matches[0]}")
            return f"GSTIN for {company}: {matches[0]}"

        except Exception as e:
            return f"Andromeda Search Error: {str(e)}"