import pygame
import random
import os
import sys   # <-- eklendi
from gtts import gTTS
import tempfile
import time

pygame.init()
screen = pygame.display.set_mode((1200,800))
pygame.display.set_caption("Audio Visual Memory Test")
font = pygame.font.SysFont(None, 28)

# Global skorlar
correct_count = 0
wrong_count = 0
streak = 0

cities = ["Amsterdam", "Ankara", "Ashgabat", "Baghdad", "Bahrain", "Baku", "Bangkok", "Basel", "Batumi", "Beirut",
          "Belgrade", "Berlin", "Bilbao", "Bishkek", "Bologna", "Bombay", "Boston", "Bremen", "Budapest", "Dallas",
          "Delhi", "Doha", "Dubai", "Dublin", "Hamburg", "Havana", "Houston", "Kathmandu", "Kiev", "Lagos", "Lisbon",
          "London", "Lyon", "Madrid", "Malaga", "Malta", "Manchester", "Melbourne", "Miami", "Milan", "Montreal",
          "Moscow", "Munich", "Paris", "Phuket", "Porto", "Prague", "Riyadh", "Rotterdam", "Salzburg", "Santiago",
          "Shanghai", "Singapore", "Stockholm", "Stuttgart", "Sydney", "Tashkent", "Tokyo", "Toronto", "Tunis",
          "Valencia", "Venice", "Vienna", "Zagreb", "Zurich"]

def speak(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_path = fp.name
    tts.save(temp_path)
    pygame.mixer.init()
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    os.remove(temp_path)

def run_game():
    global correct_count, wrong_count, streak

    # --- Zorluk seçimi ---
    difficulty_levels = [2,3,4,5,6,7]
    selected_difficulty = 0
    selecting = True
    while selecting:
        screen.fill((255,255,255))
        screen.blit(font.render("Select difficulty (2-7):", True, (0,0,0)), (50,50))

        # Skor bilgisi başta göster
        screen.blit(font.render(f"Correct sets: {correct_count}", True, (0,150,0)), (400, 50))
        screen.blit(font.render(f"Wrong sets: {wrong_count}", True, (200,0,0)), (550, 50))
        screen.blit(font.render(f"Streak: {streak}", True, (0,0,200)), (700, 50))

        for idx, lvl in enumerate(difficulty_levels):
            pygame.draw.rect(screen, (0,0,200), (50+idx*60, 100, 50, 50))
            screen.blit(font.render(str(lvl), True, (255,255,255)), (65+idx*60, 115))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                for idx, lvl in enumerate(difficulty_levels):
                    if 50+idx*60 <= mx <= 100+idx*60 and 100 <= my <= 150:
                        selected_difficulty = lvl
                        selecting = False

    # --- Başlangıç ekranı ---
    corridors = list(range(1,11))
    occupied = random.sample(corridors,2)
    screen.fill((255,255,255))
    for i, c in enumerate(reversed(corridors)):
        color = (255,0,0) if c in occupied else (0,0,0)
        screen.blit(font.render(f"Corridor {c}", True, color), (50,50+i*50))
    pygame.display.flip()
    pygame.time.delay(3500)
    # kırmızılar siyaha dönsün
    screen.fill((255,255,255))
    for i, c in enumerate(reversed(corridors)):
        screen.blit(font.render(f"Corridor {c}", True, (0,0,0)), (50,50+i*50))
    pygame.display.flip()
    pygame.time.delay(1000)

    # --- Anonslar: doğru ve yanlış karışık ---
    available_corridors = [c for c in corridors if c not in occupied]
    remaining_cities = cities.copy()

    # doğru anonslar
    correct_announcements = []
    for _ in range(selected_difficulty):
        city = random.choice(remaining_cities)
        remaining_cities.remove(city)
        corridor = random.choice(available_corridors)
        correct_announcements.append((city, corridor))

    # yanlış anonslar
    num_wrong = random.randint(1,3)
    wrong_announcements = []
    for _ in range(num_wrong):
        if not remaining_cities:
            break
        city = random.choice(remaining_cities)
        remaining_cities.remove(city)
        corridor = random.choice(occupied)
        wrong_announcements.append((city, corridor))

    all_announcements = correct_announcements + wrong_announcements
    random.shuffle(all_announcements)

    announcements = []
    for city, corridor in all_announcements:
        announcements.append((city, corridor))
        speak(f"To {city} on Corridor {corridor}")
        time.sleep(0.5)

    # --- Şehir seçme ekranı ---
    cities_sorted = sorted(cities)
    selected = [False]*len(cities_sorted)
    running = True
    next_button = pygame.Rect(950, 700, 200, 50)

    while running:
        screen.fill((255,255,255))
        screen.blit(font.render("Select the cities that can fly:", True, (0,0,0)), (50,20))
        for idx, city in enumerate(cities_sorted):
            col = idx // 13
            row = idx % 13
            x = 50 + col * 220
            y = 80 + row * 40
            color = (0,200,0) if selected[idx] else (0,0,0)
            txt = font.render(city, True, color)
            screen.blit(txt, (x,y))
        pygame.draw.rect(screen, (0,0,200), next_button)
        screen.blit(font.render("Next", True, (255,255,255)), (next_button.x + 60, next_button.y + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = event.pos
                for idx, city in enumerate(cities_sorted):
                    col = idx // 13
                    row = idx % 13
                    x = 50 + col * 220
                    y = 80 + row * 40
                    if x <= mx <= x+180 and y <= my <= y+30:
                        selected[idx] = not selected[idx]
                if next_button.collidepoint(mx,my):
                    running = False

    # --- Feedback ve SKOR ---
    correct_cities = set([city for city,_ in correct_announcements])
    selected_set = set([city for idx, city in enumerate(cities_sorted) if selected[idx]])
    wrong_selected = selected_set - correct_cities
    missed_correct = correct_cities - selected_set

    if len(wrong_selected) > 0 or len(missed_correct) > 0:
        wrong_count += 1
        streak = 0
        set_result = "WRONG"
    else:
        correct_count += 1
        streak += 1
        set_result = "CORRECT"

    feedback_button = pygame.Rect(950, 700, 200, 50)
    running = True
    while running:
        screen.fill((255,255,255))
        screen.blit(font.render("Feedback: green=correct, red=wrong, blue=unselected", True, (0,0,0)), (50,20))
        for idx, city in enumerate(cities_sorted):
            col = idx // 13
            row = idx % 13
            x = 50 + col * 220
            y = 80 + row * 40
            if city in correct_cities and city in selected_set:
                color = (0,200,0)
            elif city in correct_cities and city not in selected_set:
                color = (0,0,255)
            elif city not in correct_cities and city in selected_set:
                color = (255,0,0)
            else:
                color = (0,0,0)
            txt = font.render(city, True, color)
            screen.blit(txt, (x,y))

        screen.blit(font.render(f"Set result: {set_result}", True, (0,0,0)), (700, 600))
        screen.blit(font.render(f"Correct sets: {correct_count}", True, (0,150,0)), (700, 630))
        screen.blit(font.render(f"Wrong sets: {wrong_count}", True, (200,0,0)), (700, 660))
        screen.blit(font.render(f"Streak: {streak}", True, (0,0,200)), (700, 690))

        pygame.draw.rect(screen, (0,200,0), feedback_button)
        screen.blit(font.render("Restart", True, (255,255,255)), (feedback_button.x + 50, feedback_button.y + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if feedback_button.collidepoint(event.pos):
                    run_game()

run_game()