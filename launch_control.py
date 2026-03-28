import subprocess, time, os, sys, requests

# --- SYSTEM PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
BIN_DIR = os.path.join(BASE_DIR, "bin")
LOG_PATH = os.path.join(SRC_DIR, "Logs", "andromeda_node.log")

os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

KOBOLD_EXE = os.path.join(BIN_DIR, "koboldcpp-nocuda.exe")
KOBOLD_URL = "https://github.com/LostRuins/koboldcpp/releases/latest/download/koboldcpp-nocuda.exe"
MODEL_FILE = os.path.join(BIN_DIR, "Phi-3.5-mini-instruct-IQ4_XS.gguf")
MODEL_URL = "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-IQ4_XS.gguf?download=true"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def purge_ram():
    print("[SYSTEM] Purging ghost binaries...")
    for proc in ["chrome.exe", "koboldcpp-nocuda.exe", "chromedriver.exe"]:
        os.system(f"taskkill /f /im {proc} /T >nul 2>&1")
    time.sleep(2)

def download_with_progress(url, dest, name):
    print(f"      [WARN] Provisioning {name} from remote server...")
    r = requests.get(url, stream=True)
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(1024*1024):
            if chunk: f.write(chunk)
    print(f"      [SUCCESS] {name} acquired.")

def setup_dependencies():
    if not os.path.exists(KOBOLD_EXE): download_with_progress(KOBOLD_URL, KOBOLD_EXE, "Kobold Engine")
    if not os.path.exists(MODEL_FILE): download_with_progress(MODEL_URL, MODEL_FILE, "Phi-3.5 Weights")

def thermal_cooldown(s=15):
    print(f"[SYSTEM] Cooldown: {s}s...")
    time.sleep(s)

if __name__ == "__main__":
    purge_ram()
    setup_dependencies()
    with open(LOG_PATH, 'w') as f: f.write("[SYSTEM] ANDROMEDA_OS BOOTING...\n")
    
    # 1. Start Tactical UI (Added CREATE_NEW_CONSOLE to decouple it)
    print("[1/4] Launching Tactical UI...")
    ui_proc = subprocess.Popen([sys.executable, "ui.py"], cwd=BASE_DIR, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    # 2. Start Neural Engine
    print("[2/4] Loading Neural Weights...")
    k_cmd = [KOBOLD_EXE, MODEL_FILE, "--port", "5001", "--threads", "2", "--highpriority", "--quiet", "--contextsize", "1024"]
    llm_proc = subprocess.Popen(k_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    while True:
        try:
            if requests.get("http://localhost:5001/api/v1/model", timeout=2).status_code == 200: break
        except: time.sleep(3)
    
    thermal_cooldown(10)

    # 3. Start Ghost Browser
    print("[3/4] Initializing Sovereign Browser...")
    profile = os.path.join(BASE_DIR, "Brain_Data", "Chrome_Profile")
    chrome_cmd = [
        CHROME_PATH, "--remote-debugging-port=9011", f"--user-data-dir={profile}",
         "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage", 
        "--remote-allow-origins=*", "https://web.whatsapp.com"
    ]
    # Keep Chrome alive even if the launcher hangs
    chrome_proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.DETACHED_PROCESS)
    time.sleep(15) 
    
    # 4. Start Orchestrator (WITH THE FENNEC TRAP)
    print("[4/4] Activating Orchestrator...")
    
    # Notice the "cmd", "/k" added to the start of the list
    trap_cmd = ["cmd", "/k", sys.executable, "andromeda_core.py"]
    
    core_proc = subprocess.Popen(trap_cmd, cwd=SRC_DIR, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    print("[SYSTEM] All nodes active. Launcher entering holding pattern...")
    core_proc.wait()