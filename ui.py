import pygame
import os
import ctypes

# --- SYSTEM PATHS ---
# Calculates paths relative to where ui.py is located (the root folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "src", "Logs", "andromeda_node.log")

# --- UI SETTINGS ---
WIDTH, HEIGHT = 450, 600  # Widget size
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
DARK_CYAN = (0, 100, 100)

# --- PIN TO TOP RIGHT ---
try:
    # Get screen resolution via Windows API
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    # Calculate position (Screen Width - UI Width - 20px padding from the right edge)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{screen_width - WIDTH - 20},20"
except Exception:
    pass # Fallback if not running on Windows

pygame.init()

# --- FRAMELESS & ALWAYS ON TOP ---
# pygame.NOFRAME removes the standard close/minimize/maximize borders
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("ANDROMEDA_OS")

try:
    # Windows API trick to force the window to stay ALWAYS ON TOP of other apps
    hwnd = pygame.display.get_wm_info()["window"]
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
except Exception:
    pass

# --- FONTS ---
font_title = pygame.font.SysFont("Consolas", 24, bold=True)
font_text = pygame.font.SysFont("Consolas", 14)

def get_thinking_logs(limit=16):
    """Tails the log file to show what the ReAct engine is doing."""
    if not os.path.exists(LOG_PATH):
        return ["AWAITING NEURAL LINK..."]
    try:
        with open(LOG_PATH, 'r') as f:
            lines = f.readlines()
            # Clean up the logs and truncate them so they don't run off the screen
            return [line.strip()[-55:] for line in lines[-limit:]]
    except Exception:
        return ["LOG SYNC ERROR"]

def draw_ui(frame_count):
    screen.fill(BLACK)
    
    # 1. BORDER
    pygame.draw.rect(screen, CYAN, (0, 0, WIDTH, HEIGHT), 2)
    
    # 2. HEADER
    title = font_title.render("ANDROMEDA_OS", True, CYAN)
    screen.blit(title, (20, 20))
    pygame.draw.line(screen, CYAN, (20, 50), (WIDTH - 20, 50), 1)

    # 3. LIVE LOG FEED (MIDDLE)
    logs = get_thinking_logs()
    y_offset = 70
    for log in logs:
        log_render = font_text.render(f"> {log}", True, CYAN)
        screen.blit(log_render, (20, y_offset))
        y_offset += 25

    # 4. ANIMATED "THINKING" STATUS (BOTTOM)
    # Uses the frame count to cycle through characters, creating a spinning animation
    spinner = ["|", "/", "-", "\\"][int((frame_count / 10) % 4)]
    status_text = f"NEURAL CORE: THINKING [{spinner}]"
    
    status_render = font_text.render(status_text, True, CYAN)
    screen.blit(status_render, (20, HEIGHT - 40))
    pygame.draw.line(screen, DARK_CYAN, (20, HEIGHT - 50), (WIDTH - 20, HEIGHT - 50), 1)

    pygame.display.flip()

def run_os():
    clock = pygame.time.Clock()
    running = True
    frame_count = 0

    while running:
        # Allow exiting by pressing ESCAPE (since there is no "X" button anymore)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        draw_ui(frame_count)
        frame_count += 1
        
        # Lock to 30 FPS. High enough to look smooth, low enough to not steal CPU from the LLM.
        clock.tick(30) 

    pygame.quit()

if __name__ == "__main__":
    run_os()s