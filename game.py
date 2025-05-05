import pygame

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gra z Zablokowanymi Obszarami")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
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

# Lista zablokowanych obszarów (ze współrzędnych: lewy dolny róg, prawy górny)
blocked_areas = [
    # Wcześniejsze
    pygame.Rect(0, 194, 768 - 0, 230 - 194),
    pygame.Rect(0, 0, 329 - 0, 2800 - 0),
    pygame.Rect(66, 2243, 825 - 66, 2800 - 2243),
    pygame.Rect(785, 2556, 2800 - 785, 2800 - 2556),
    pygame.Rect(1770, 1936, 2800 - 1770, 2354 - 1936),
    pygame.Rect(2489, 1075, 2800 - 2489, 1959 - 1075),
    pygame.Rect(1778, 1115, 2647 - 1778, 1283 - 1115),

    # Nowe
    pygame.Rect(1950, 1453, 2242 - 1950, 1624 - 1453),
    pygame.Rect(956, 1289, 1289 - 956, 1446 - 1289),
    pygame.Rect(1125, 1138, 1307 - 1125, 1252 - 1138),
    pygame.Rect(966, 1553, 1287 - 966, 1615 - 1553),
    pygame.Rect(211, 1882, 489 - 211, 2051 - 1882),
    pygame.Rect(320, 1332, 618 - 320, 1727 - 1332),
    pygame.Rect(400, 639, 855 - 400, 853 - 639),
    pygame.Rect(817, 687, 909 - 817, 1079 - 687),
    pygame.Rect(802, 0, 1095 - 802, 143 - 0),
    pygame.Rect(1130, 0, 1333 - 1130, 163 - 0),
    pygame.Rect(1351, 11, 1589 - 1351, 93 - 11),
    pygame.Rect(1713, 0, 2800 - 1713, 80 - 0),
    pygame.Rect(1977, 46, 2800 - 1977, 205 - 46),
    pygame.Rect(2355, 150, 2800 - 2355, 421 - 150),
    pygame.Rect(1120, 528, 2074 - 1120, 908 - 528),
]


# Czcionka
font = pygame.font.Font(None, 36)

def check_collision(new_x, new_y):
    """Sprawdza kolizję z wszystkimi zablokowanymi obszarami"""
    temp_rect = pygame.Rect(new_x, new_y, char_width, char_height)
    return any(temp_rect.colliderect(blocked) for blocked in blocked_areas)

# Główna pętla gry
clock = pygame.time.Clock()
running = True

while running:
    # Obsługa zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Poruszanie postacią
    keys = pygame.key.get_pressed()
    new_x = char_x
    new_y = char_y

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        new_x -= speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        new_x += speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_y -= speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_y += speed

    # Sprawdź kolizję przed aktualizacją pozycji
    if not check_collision(new_x, new_y):
        char_x = new_x
        char_y = new_y

    # Ograniczenie ruchu do mapy
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

    # Rysowanie wszystkich zablokowanych obszarów
    for rect in blocked_areas:
        pygame.draw.rect(
            screen,
            RED,
            (
                rect.x - camera_x,
                rect.y - camera_y,
                rect.width,
                rect.height
            ),
            2
        )

    pygame.display.update()
    clock.tick(60)

pygame.quit()
