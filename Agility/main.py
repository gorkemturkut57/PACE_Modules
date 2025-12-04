import pygame, random
from pygame.locals import *
import sys

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = screen.get_size()
pygame.display.set_caption("Agility Reflex Module")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont(None, 32)
BIG_FONT = pygame.font.SysFont(None, 64)

# Kutu
BOX_W, BOX_H = int(W * 0.8), int(H * 0.25)
BOX_X, BOX_Y = (W - BOX_W) // 2, (H - BOX_H) // 2 + 80
BOX_RECT = pygame.Rect(BOX_X, BOX_Y, BOX_W, BOX_H)
BOX_COLOR = (160, 160, 160)

# Cisim
OBJ_SIZE = int(min(W, H) * 0.15)
SPEED = 300
FAKE_PROB = 0.4

# Renkler
RED = (220, 50, 50)
GREEN = (40, 180, 40)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
BUTTON_PRESSED = (60, 60, 60)

# Modlar
MOD1 = {
    K_LEFT: ("red", "circle"),
    K_UP: ("red", "square"),
    K_DOWN: ("green", "square"),
    K_RIGHT: ("green", "circle"),
}

MOD2 = {
    K_RIGHT: ("red", "circle"),
    K_DOWN: ("red", "square"),
    K_LEFT: ("green", "circle"),
    K_UP: ("green", "square"),
}

# Dokunmatik tuşlar için dikdörtgenler
BUTTON_SIZE = int(min(W, H) * 0.15)
BUTTON_MARGIN = 20
BUTTON_AREA_W = BUTTON_SIZE * 3 + BUTTON_MARGIN * 2

# Tuşları sağda konumlandır
BUTTONS = {
    K_UP: pygame.Rect(W - BUTTON_AREA_W + BUTTON_SIZE + BUTTON_MARGIN, 
                      H // 2 - BUTTON_SIZE * 2 - BUTTON_MARGIN, 
                      BUTTON_SIZE, BUTTON_SIZE),
    K_LEFT: pygame.Rect(W - BUTTON_AREA_W, 
                        H // 2 - BUTTON_SIZE // 2, 
                        BUTTON_SIZE, BUTTON_SIZE),
    K_RIGHT: pygame.Rect(W - BUTTON_AREA_W + (BUTTON_SIZE + BUTTON_MARGIN) * 2, 
                         H // 2 - BUTTON_SIZE // 2, 
                         BUTTON_SIZE, BUTTON_SIZE),
    K_DOWN: pygame.Rect(W - BUTTON_AREA_W + BUTTON_SIZE + BUTTON_MARGIN, 
                        H // 2 + BUTTON_SIZE // 2 + BUTTON_MARGIN, 
                        BUTTON_SIZE, BUTTON_SIZE),
}

pressed_buttons = set()

def choose_mode():
    while True:
        screen.fill(BLACK)
        screen.blit(BIG_FONT.render("1: Mod 1 | 2: Mod 2", True, WHITE), (W//2 - 200, H//2 - 40))
        screen.blit(FONT.render("ESC = quit", True, WHITE), (20, 20))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_1:
                    return MOD1
                elif event.key == K_2:
                    return MOD2
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

MAPPING = choose_mode()
KEY_FOR = {(v[0], v[1]): k for k, v in MAPPING.items()}

def draw_obj(surface, typ, pos):
    color = RED if typ["color"] == "red" else GREEN
    x, y = pos
    s = typ["size"]
    if typ["shape"] == "circle":
        pygame.draw.circle(surface, color, (int(x), int(y)), s // 2)
        pygame.draw.circle(surface, BLACK, (int(x), int(y)), s // 2, 2)
    else:
        r = pygame.Rect(int(x - s / 2), int(y - s / 2), s, s)
        pygame.draw.rect(surface, color, r)
        pygame.draw.rect(surface, BLACK, r, 2)

def draw_button(surface, rect, key, pressed):
    color = BUTTON_PRESSED if pressed else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, BLACK, rect, 3, border_radius=10)
    
    # Ok işaretleri
    cx, cy = rect.centerx, rect.centery
    arrow_size = BUTTON_SIZE // 4
    
    if key == K_UP:
        points = [(cx, cy - arrow_size), (cx - arrow_size, cy + arrow_size//2), (cx + arrow_size, cy + arrow_size//2)]
    elif key == K_DOWN:
        points = [(cx, cy + arrow_size), (cx - arrow_size, cy - arrow_size//2), (cx + arrow_size, cy - arrow_size//2)]
    elif key == K_LEFT:
        points = [(cx - arrow_size, cy), (cx + arrow_size//2, cy - arrow_size), (cx + arrow_size//2, cy + arrow_size)]
    elif key == K_RIGHT:
        points = [(cx + arrow_size, cy), (cx - arrow_size//2, cy - arrow_size), (cx - arrow_size//2, cy + arrow_size)]
    
    pygame.draw.polygon(surface, WHITE, points)

def spawn_object():
    shape = random.choice(["circle", "square"])
    color = random.choice(["red", "green"])
    fake = random.random() < FAKE_PROB
    x = BOX_X + BOX_W // 2 + random.randint(-BOX_W//4, BOX_W//4)
    y = H + OBJ_SIZE
    vy = -SPEED
    return {
        "typ": {"shape": shape, "color": color, "size": OBJ_SIZE},
        "pos": [x, y],
        "vel": [0, vy],
        "fake": fake,
        "exploded": False,
        "spawn_time": pygame.time.get_ticks(),
    }

total_correct = 0
total_wrong = 0
reaction_times = []
last_rt = 0
obj = None
last_spawn = -3000
next_spawn_delay = random.randint(1000, 5000)
message = ""
message_time = 0
reaction_start = None
running = True

while running:
    dt = clock.tick(60)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            else:
                # Klavye tuşu işleme
                if obj and not obj["exploded"] and reaction_start:
                    expected = KEY_FOR.get((obj["typ"]["color"], obj["typ"]["shape"]))
                    if event.key == expected:
                        rt = int(now - reaction_start)
                        last_rt = rt
                        message = f"BAŞARILI ({rt} ms)"
                        total_correct += 1
                        reaction_times.append(rt)
                        obj["exploded"] = True
                        message_time = now
                    else:
                        message = "YANLIŞ TUŞ"
                        total_wrong += 1
                        obj["exploded"] = True
                        message_time = now
                elif obj and not reaction_start:
                    message = "ERKEN BASIŞ"
                    total_wrong += 1
                    message_time = now
                elif obj is None:
                    message = "YANLIŞ TUŞ"
                    total_wrong += 1
                    message_time = now
        
        elif event.type == MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for key, rect in BUTTONS.items():
                if rect.collidepoint(mouse_pos):
                    pressed_buttons.add(key)
                    # Tuş basımı işleme (klavye ile aynı mantık)
                    if obj and not obj["exploded"] and reaction_start:
                        expected = KEY_FOR.get((obj["typ"]["color"], obj["typ"]["shape"]))
                        if key == expected:
                            rt = int(now - reaction_start)
                            last_rt = rt
                            message = f"BAŞARILI ({rt} ms)"
                            total_correct += 1
                            reaction_times.append(rt)
                            obj["exploded"] = True
                            message_time = now
                        else:
                            message = "YANLIŞ TUŞ"
                            total_wrong += 1
                            obj["exploded"] = True
                            message_time = now
                    elif obj and not reaction_start:
                        message = "ERKEN BASIŞ"
                        total_wrong += 1
                        message_time = now
                    elif obj is None:
                        message = "YANLIŞ TUŞ"
                        total_wrong += 1
                        message_time = now
        
        elif event.type == MOUSEBUTTONUP:
            pressed_buttons.clear()

    # Spawn
    if obj is None and now - last_spawn >= next_spawn_delay:
        obj = spawn_object()
        last_spawn = now
        next_spawn_delay = random.randint(1000, 5000)
        reaction_start = None

    # Update
    if obj:
        obj["pos"][1] += obj["vel"][1] * dt / 1000
        
        if not obj["exploded"] and not obj["fake"] and reaction_start is None:
            if obj["pos"][1] - OBJ_SIZE/2 <= BOX_Y + BOX_H:
                reaction_start = now
        
        if obj["fake"] and not obj["exploded"]:
            if obj["pos"][1] - OBJ_SIZE/2 <= BOX_Y + BOX_H - 1:
                obj["exploded"] = True
        
        if not obj["exploded"] and not obj["fake"]:
            if obj["pos"][1] < BOX_Y - OBJ_SIZE:
                message = "KAÇIRILDI"
                total_wrong += 1
                message_time = now
                obj["exploded"] = True
        
        if obj["exploded"]:
            obj = None

    # Çizim
    screen.fill(WHITE)
    pygame.draw.rect(screen, BOX_COLOR, BOX_RECT)
    pygame.draw.rect(screen, BLACK, BOX_RECT, 5)

    if obj:
        draw_obj(screen, obj["typ"], obj["pos"])

    screen.blit(FONT.render(f"Son doğru tepki: {last_rt} ms", True, BLACK), (W - BUTTON_AREA_W - 320, 20))

    if message and now - message_time < 2500:
        surf = BIG_FONT.render(message, True, BLACK)
        screen.blit(surf, (W//2 - surf.get_width()//2, BOX_Y + BOX_H + 20))

    # İstatistikler
    avg_rt = int(sum(reaction_times)/len(reaction_times)) if reaction_times else 0
    stats = [
        f"Doğru: {total_correct}",
        f"Yanlış: {total_wrong}",
        f"Ortalama Tepki Süresi: {avg_rt} ms"
    ]
    for i, t in enumerate(stats):
        screen.blit(FONT.render(t, True, BLACK), (W - BUTTON_AREA_W - 320, 50 + i*30))

    # Dokunmatik tuşlar
    for key, rect in BUTTONS.items():
        draw_button(screen, rect, key, key in pressed_buttons)

    pygame.display.flip()

pygame.quit()