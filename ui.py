import pygame, psutil, os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "src", "Logs", "andromeda_node.log")
WIDTH, HEIGHT = 1200, 800

BG_COLOR, PANEL_BG, BORDER_COLOR = (10, 10, 15), (20, 20, 25), (40, 40, 50)
NEON_GREEN, CYAN, RED = (57, 255, 20), (0, 255, 255), (255, 50, 50)

def get_latest_logs(filepath, max_lines=32):
    if not os.path.exists(filepath): return ["[SYS] Awaiting Log Stream..."]
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f.readlines()[-max_lines:]]
    except: return ["[GUI ERROR] IO Collision - Retrying..."]

def draw_graph(surface, font, data, x, y, w, h, color, title):
    pygame.draw.rect(surface, PANEL_BG, (x, y, w, h))
    pygame.draw.rect(surface, BORDER_COLOR, (x, y, w, h), 2)
    
    current_val = data[-1]
    text_color = RED if current_val > 85 else color
    surface.blit(font.render(f"{title}: {current_val:.1f}%", True, text_color), (x + 15, y + 15))
    
    points = []
    step_x = w / len(data)
    plot_h = h - 50 
    for i, val in enumerate(data):
        points.append((x + (i * step_x), (y + h - 10) - ((val / 100) * plot_h)))
        
    if len(points) > 1:
        pygame.draw.line(surface, BORDER_COLOR, (x, y + h - 10 - (0.5 * plot_h)), (x + w, y + h - 10 - (0.5 * plot_h)), 1)
        pygame.draw.lines(surface, color, False, points, 2)

def main():
    pygame.init(); screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("ANDROMEDA TACTICAL C2")
    font_main = pygame.font.SysFont("consolas", 14)
    font_title = pygame.font.SysFont("consolas", 20, bold=True)
    clock = pygame.time.Clock()

    cpu_history, ram_history = [0] * 100, [0] * 100

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()

        cpu_history.pop(0); cpu_history.append(psutil.cpu_percent())
        ram_history.pop(0); ram_history.append(psutil.virtual_memory().percent)

        screen.fill(BG_COLOR)

        log_pane_w = int(WIDTH * 0.65)
        pygame.draw.rect(screen, PANEL_BG, (20, 20, log_pane_w, HEIGHT - 40))
        pygame.draw.rect(screen, BORDER_COLOR, (20, 20, log_pane_w, HEIGHT - 40), 2)
        
        screen.blit(font_title.render("=== ANDROMEDA NODE TELEMETRY | UID: A-01 ===", True, NEON_GREEN), (35, 35))
        pygame.draw.line(screen, NEON_GREEN, (35, 60), (log_pane_w, 60), 1)

        for i, log in enumerate(get_latest_logs(LOG_PATH, (HEIGHT - 100) // 22)):
            color = RED if "[ERROR]" in log else NEON_GREEN if "[SUCCESS]" in log else CYAN
            screen.blit(font_main.render(log, True, color), (35, 75 + (i * 22)))

        gx, gw, gh = log_pane_w + 40, WIDTH - (log_pane_w + 40) - 20, (HEIGHT // 2) - 30
        draw_graph(screen, font_title, cpu_history, gx, 20, gw, gh, NEON_GREEN, "SYSTEM CPU")
        draw_graph(screen, font_title, ram_history, gx, (HEIGHT // 2) + 10, gw, gh, CYAN, "MEMORY ALLOC")

        pygame.display.flip(); clock.tick(15)

if __name__ == "__main__": main()