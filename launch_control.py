import subprocess
import time
import os
import sys
import requests
import socket

# --- SYSTEM PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
BIN_DIR = os.path.join(BASE_DIR, "bin")

# Ensure bin directory exists
os.makedirs(BIN_DIR, exist_ok=True) 

# --- CONFIGURATION & DOWNLOAD LINKS ---
KOBOLD_EXE = os.path.join(BIN_DIR, "koboldcpp-nocuda.exe")
KOBOLD_URL = "https://github.com/LostRuins/koboldcpp/releases/latest/download/koboldcpp-nocuda.exe"

MODEL_FILE = os.path.join(BIN_DIR, "Phi-3.5-mini-instruct-Q4_K_M.gguf")
MODEL_URL = "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf"

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PORT = 9011

def download_with_progress(url, dest):
    """Downloads a file in chunks and displays a sleek CLI progress bar."""
    filename = os.path.basename(dest)
    print(f"      [NETWORK] Fetching {filename}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 * 1024 # 1 MB chunks
    downloaded = 0
    
    with open(dest, 'wb') as f:
        for data in response.iter_content(block_size):
            f.write(data)
            downloaded += len(data)
            if total_size > 0:
                percent = downloaded / total_size
                bar_length = 40
                filled = int(bar_length * percent)
                bar = '█' * filled + '-' * (bar_length - filled)
                sys.stdout.write(f"\r      [{bar}] {downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB ({(percent*100):.1f}%)")
                sys.stdout.flush()
    print("\n      [SUCCESS] Download verified.")

def setup_dependencies():
    """Checks for required binaries and downloads them strictly if missing."""
    print("[0/4] Running System Integrity Check...")
    
    if os.path.exists(KOBOLD_EXE):
        print("      [OK] Kobold engine found in /bin. Skipping download.")
    else:
        print("      [WARN] Kobold engine missing. Initiating auto-provisioning...")
        download_with_progress(KOBOLD_URL, KOBOLD_EXE)
    
    if os.path.exists(MODEL_FILE):
        print("      [OK] Neural weights found in /bin. Skipping download.")
    else:
        print("      [WARN] Neural weights missing. Initiating auto-provisioning...")
        download_with_progress(MODEL_URL, MODEL_FILE)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def boot_ui():
    print("[1/4] Booting Andromeda OS Overlay...")
    subprocess.Popen([sys.executable, "ui.py"], cwd=BASE_DIR)
    time.sleep(2) 

def boot_kobold():
    print("[2/4] Initializing Kobold Neural Engine...")
    cmd = [KOBOLD_EXE, MODEL_FILE, "--port", "5001", "--highpriority", "--quiet"]
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)

    print("      Waiting for API to stabilize (Loading weights into RAM)...")
    for _ in range(30): # 2.5 minute timeout
        try:
            if requests.get("http://localhost:5001/api/v1/model", timeout=2).status_code == 200:
                print("      [READY] Neural link established.")
                return True
        except requests.exceptions.RequestException:
            time.sleep(5)
    
    print("[CRITICAL] Neural Engine failed to boot. Check the Kobold console.")
    return False

def boot_chrome():
    if is_port_in_use(CHROME_PORT):
        print(f"[3/4] Chrome Stealth Driver already active on port {CHROME_PORT}.")
        return
    
    print("[3/4] Launching Stealth Chrome Instance...")
    profile_dir = os.path.join(BASE_DIR, "Brain_Data", "Chrome_Profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={CHROME_PORT}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://web.whatsapp.com"
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3) 

def boot_core():
    core_path = os.path.join(SRC_DIR, "andromeda_core.py")
    print(f"[4/4] Activating Andromeda Orchestrator...")
    subprocess.run([sys.executable, core_path], cwd=BASE_DIR)

if __name__ == "__main__":
    print("""
    =========================================
      ANDROMEDA-01 // LAUNCH SEQUENCE ACTIVE 
    =========================================
    """)
    
    setup_dependencies()
    
    boot_ui()
    if boot_kobold():
        boot_chrome()
        boot_core()
    else:
        print("\n[!] Launch sequence aborted due to engine failure.")