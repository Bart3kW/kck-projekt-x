import pygame
import time

pygame.init()

# Ustawienia okna
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gra z animacją kierunkową i bezczynnością")

# Wczytanie mapy
map_width = 2800
map_height = 2800
background = pygame.image.load('map.png').convert()

# Wczytanie wszystkich klatek animacji
character_idle = pygame.image.load('character.png').convert_alpha()

walk_right = [pygame.image.load(f'character{i}.png').convert_alpha() for i in range(1, 5)]
walk_left  = [pygame.image.load(f'character{i}.png').convert_alpha() for i in range(5, 9)]
walk_up    = [pygame.image.load(f'character{i}.png').convert_alpha() for i in range(9, 11)]
walk_down  = [pygame.image.load(f'character{i}.png').convert_alpha() for i in range(11, 13)]

# Klatki idle-look
character_look_left = pygame.image.load('characterlookleft.png').convert_alpha()
character_look_right = pygame.image.load('characterlookright.png').convert_alpha()

# Początkowa pozycja postaci
character = character_idle
char_width = character.get_width()
char_height = character.get_height()
char_x = (map_width - char_width) // 2
char_y = (map_height - char_height) // 2

# Ruch i animacja
speed = 5
walk_timer = 0
walk_frame = 0
last_direction = "down"

# Bezczynność
last_move_time = time.time()
idle_stage = 0
idle_triggered = False

clock = pygame.time.Clock()
running = True

# Lista zablokowanych obszarów
blocked_areas = [
    pygame.Rect(0, 194, 768 - 0, 230 - 194),
    pygame.Rect(0, 0, 329 - 0, 2800 - 0),
    pygame.Rect(66, 2243, 825 - 66, 2800 - 2243),
    pygame.Rect(785, 2556, 2800 - 785, 2800 - 2556),
    pygame.Rect(1770, 1936, 2800 - 1770, 2354 - 1936),
    pygame.Rect(2489, 1075, 2800 - 2489, 1959 - 1075),
    pygame.Rect(1778, 1115, 2647 - 1778, 1283 - 1115),
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

# Funkcja kolizji
def check_collision(new_x, new_y):
    temp_rect = pygame.Rect(new_x, new_y, char_width, char_height)
    return any(temp_rect.colliderect(rect) for rect in blocked_areas)

# Główna pętla
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx = -speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx = speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy = -speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy = speed

    # Przemieszczanie postaci
    new_x = char_x + dx
    new_y = char_y + dy
    if not check_collision(new_x, new_y):
        char_x = new_x
        char_y = new_y

    # Ograniczenia ruchu
    char_x = max(0, min(char_x, map_width - char_width))
    char_y = max(0, min(char_y, map_height - char_height))

    # Czy się ruszamy
    moving = dx != 0 or dy != 0

    if moving:
        walk_timer += 1
        if walk_timer >= 8:
            walk_timer = 0
            walk_frame = (walk_frame + 1)

        # Kierunek dominujący
        if abs(dx) >= abs(dy):
            if dx > 0:
                direction = "right"
                frames = walk_right
            else:
                direction = "left"
                frames = walk_left
        else:
            if dy > 0:
                direction = "down"
                frames = walk_down
            else:
                direction = "up"
                frames = walk_up

        last_direction = direction
        character = frames[walk_frame % len(frames)]

        # Resetuj idle
        last_move_time = time.time()
        idle_triggered = False
        idle_stage = 0

    else:
        # Bezczynność
        current_time = time.time()

        if not idle_triggered and current_time - last_move_time >= 10:
            idle_triggered = True
            idle_stage = 1
            idle_stage_start = current_time

        if idle_triggered:
            if idle_stage == 1:
                character = character_look_left
                if current_time - idle_stage_start >= 1:
                    idle_stage = 2
                    idle_stage_start = current_time
            elif idle_stage == 2:
                character = character_look_right
                if current_time - idle_stage_start >= 1:
                    idle_stage = 0
                    idle_triggered = False
                    last_move_time = current_time
                    character = character_idle
        else:
            character = character_idle
            walk_timer = 0
            walk_frame = 0

    # Kamera
    camera_x = char_x + char_width // 2 - screen_width // 2
    camera_y = char_y + char_height // 2 - screen_height // 2
    camera_x = max(0, min(camera_x, map_width - screen_width))
    camera_y = max(0, min(camera_y, map_height - screen_height))

    # Rysowanie
    screen.blit(background, (0, 0), (camera_x, camera_y, screen_width, screen_height))
    screen.blit(character, (char_x - camera_x, char_y - camera_y))
    # Rysowanie zablokowanych obszarów (debug)
    for rect in blocked_areas:
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            (rect.x - camera_x, rect.y - camera_y, rect.width, rect.height),
            2
        )
    pygame.display.update()
    clock.tick(60)

pygame.quit()
