import pygame

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gra z Triggerem i Dialogiem")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Wczytanie obrazków
map_width = 2800
map_height = 2800
background = pygame.image.load('map.png').convert()
character = pygame.image.load('character.png').convert_alpha()

# Wymiary postaci
char_width = character.get_width()
char_height = character.get_height()

# Początkowa pozycja
char_x = (map_width - char_width) // 2
char_y = (map_height - char_height) // 2

# Prędkość poruszania
speed = 5

# Trigger
trigger_rect = pygame.Rect(100, 100, 50, 50)  # Obszar aktywacji
show_dialog = False
answer = None

# Czcionka
font = pygame.font.Font(None, 36)

def draw_dialog():
    # Tło dialogu
    dialog_width = 600
    dialog_height = 300
    dialog_x = (screen_width - dialog_width) // 2
    dialog_y = (screen_height - dialog_height) // 2
    
    pygame.draw.rect(screen, GRAY, (dialog_x, dialog_y, dialog_width, dialog_height))
    
    # Pytanie
    text = font.render("Czy Polską rządzą Żydzi?", True, BLACK)
    text_rect = text.get_rect(center=(screen_width//2, dialog_y + 50))
    screen.blit(text, text_rect)
    
    # Przyciski odpowiedzi
    yes_rect = pygame.Rect(dialog_x + 100, dialog_y + 150, 150, 50)
    no_rect = pygame.Rect(dialog_x + 350, dialog_y + 150, 150, 50)
    
    pygame.draw.rect(screen, GREEN, yes_rect)
    pygame.draw.rect(screen, RED, no_rect)
    
    # Teksty przycisków
    yes_text = font.render("TAK", True, WHITE)
    no_text = font.render("NIE", True, WHITE)
    screen.blit(yes_text, (yes_rect.x + 40, yes_rect.y + 10))
    screen.blit(no_text, (no_rect.x + 40, no_rect.y + 10))
    
    return yes_rect, no_rect

# Główna pętla gry
clock = pygame.time.Clock()
running = True

while running:
    # Obsługa zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Sprawdź czy postać jest w strefie triggera
                distance = pygame.math.Vector2(
                    char_x - trigger_rect.x,
                    char_y - trigger_rect.y
                ).length()
                
                if distance < 50 and not show_dialog:
                    show_dialog = True
                    
        if event.type == pygame.MOUSEBUTTONDOWN and show_dialog:
            mouse_pos = pygame.mouse.get_pos()
            yes_rect, no_rect = draw_dialog()
            
            if yes_rect.collidepoint(mouse_pos):
                answer = "TAK"
                show_dialog = False
            elif no_rect.collidepoint(mouse_pos):
                answer = "NIE"
                show_dialog = False

    # Poruszanie postacią (tylko gdy dialog nie jest otwarty)
    if not show_dialog:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            char_x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            char_x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            char_y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            char_y += speed

    # Ograniczenie ruchu postaci
    char_x = max(0, min(char_x, map_width - char_width))
    char_y = max(0, min(char_y, map_height - char_height))

    # Kamera
    camera_x = char_x + char_width//2 - screen_width//2
    camera_y = char_y + char_height//2 - screen_height//2
    camera_x = max(0, min(camera_x, map_width - screen_width))
    camera_y = max(0, min(camera_y, map_height - screen_height))

    # Rysowanie
    screen.blit(background, (0, 0), (camera_x, camera_y, screen_width, screen_height))
    screen.blit(character, (char_x - camera_x, char_y - camera_y))
    
    # Rysowanie triggera (debug)
    # pygame.draw.rect(screen, RED, (trigger_rect.x - camera_x, trigger_rect.y - camera_y, trigger_rect.w, trigger_rect.h))
    
    if show_dialog:
        yes_rect, no_rect = draw_dialog()
        
    if answer:
        answer_text = font.render(f"Wybrałeś odpowiedź: {answer}", True, WHITE)
        screen.blit(answer_text, (10, 10))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()