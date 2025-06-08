import pygame
import time
import menu
from pygame.locals import *

pygame.init()

# Ustawienia okna
infoObject = pygame.display.Info()
screen_width = infoObject.current_w
screen_height = infoObject.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gra z portalami i kryształem")

# Wczytanie mapy
map_width = 2800
map_height = 2800
background = pygame.image.load('lib/graphic/maps/main/map.png').convert()

# Wczytanie mapy kolizji (czerwony = zablokowany)
collision_map = pygame.image.load('lib/graphic/maps/main/collision_map.png').convert()

# Wczytanie wnętrza budynku
interior_background = pygame.image.load('lib/graphic/maps/interior/interior_map.png').convert()
interior_collision = pygame.image.load('lib/graphic/maps/interior/interior_collision.png').convert()
interior_width = interior_background.get_width()
interior_height = interior_background.get_height()

# Wczytanie animacji postaci
character_idle = pygame.image.load('lib/graphic/character/character.png').convert_alpha()
walk_right = [pygame.image.load(f'lib/graphic/character/character{i}.png').convert_alpha() for i in range(1, 5)]
walk_left  = [pygame.image.load(f'lib/graphic/character/character{i}.png').convert_alpha() for i in range(5, 9)]
walk_up    = [pygame.image.load(f'lib/graphic/character/character{i}.png').convert_alpha() for i in range(9, 11)]
walk_down  = [pygame.image.load(f'lib/graphic/character/character{i}.png').convert_alpha() for i in range(11, 13)]
character_look_left = pygame.image.load('lib/graphic/character/characterlookleft.png').convert_alpha()
character_look_right = pygame.image.load('lib/graphic/character/characterlookright.png').convert_alpha()

# Portal i kryształ
portal1_pos = (1838, 152)
portal2_pos = (1437, 2305)
portal_image_idle = pygame.image.load("lib/graphic/portal/EmptyPortal.png").convert_alpha()
portal_waiting = [pygame.image.load(f"lib/graphic/portal/PortalWaiting{i}.png").convert_alpha() for i in range(1, 5)]
portal_working = [pygame.image.load(f"lib/graphic/portal/PortalWorking{i}.png").convert_alpha() for i in range(1, 5)]
portal_frame = 0
portal_timer = 0

# Posąg startowy (spawn)
spawn_pos = (1350, 1560)
spawn_image = pygame.image.load("lib/graphic/others/Spawn.png").convert_alpha()

crystal_pos = (2565, 688)
crystal_image = pygame.image.load("lib/graphic/others/Crystal.png").convert_alpha()
crystal_taken = False

portal_active = False
teleporting = False
teleport_cooldown = 0

# Pozycja postaci
character = character_idle
char_width = character.get_width()
char_height = character.get_height()
char_x = spawn_pos[0] + (spawn_image.get_width() // 2) - (char_width // 2)
char_y = spawn_pos[1] - char_height

# Ruch i animacja
speed = 5
walk_timer = 0
walk_frame = 0
last_direction = "down"

# Bezczynność
last_move_time = time.time()
idle_stage = 0
idle_triggered = False

# Przycisk menu
rack_image = pygame.image.load("lib/graphic/menu/Rack.png").convert_alpha()
rack_original = rack_image
rack_hovered = pygame.transform.scale(rack_image, (int(rack_image.get_width() * 0.9), int(rack_image.get_height() * 0.9)))
rack_rect = rack_image.get_rect()
rack_rect.topright = (screen_width - 10, 10)
menu_open = False

# Stan gry
current_map = "outside"  # "outside" lub "interior"
transition_alpha = 0
transition_speed = 10
transition_state = "idle"  # "fade_out", "fade_in", "idle"
interior_trigger = (2290, 290)    # wejście do budynku
exit_trigger = (1767, 655)        # wyjście z budynku (na mapie interior)
interior_spawn = (interior_width // 2, interior_height // 2)
outside_spawn = interior_trigger  # przy wyjściu wracamy w okolice trigera wejścia

# Funkcje kolizji
def is_blocked(x, y, map_type="outside"):
    """Sprawdza czy dany piksel jest zablokowany (czerwony)"""
    if map_type == "outside":
        map_surface = collision_map
        w, h = map_width, map_height
    else:
        map_surface = interior_collision
        w, h = interior_width, interior_height
    
    if 0 <= x < w and 0 <= y < h:
        color = map_surface.get_at((int(x), int(y)))
        return color.r == 255 and color.g == 0 and color.b == 0
    return True  # traktuj poza mapą jako zablokowane

def check_collision(new_x, new_y):
    """Sprawdza kolizję dla 4 rogów postaci"""
    corners = [
        (new_x, new_y),
        (new_x + char_width - 1, new_y),
        (new_x, new_y + char_height - 1),
        (new_x + char_width - 1, new_y + char_height - 1)
    ]
    
    map_type = "interior" if current_map == "interior" else "outside"
    return any(is_blocked(x, y, map_type) for x, y in corners)

def is_near(x1, y1, x2, y2, distance=50):
    """Sprawdza czy pozycje są blisko siebie"""
    return abs(x1 - x2) < distance and abs(y1 - y2) < distance

def start_transition():
    global transition_state, transition_alpha
    transition_state = "fade_out"
    transition_alpha = 0

clock = pygame.time.Clock()
running = True

while running:
    keys = pygame.key.get_pressed()
    interact = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                interact = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not menu_open and rack_rect.collidepoint(pygame.mouse.get_pos()):
                menu_open = True
            elif menu_open:
                # Assuming menu.py has a draw_menu function that returns the 'x' button rect
                x_rect = menu.draw_menu(screen)
                if x_rect.collidepoint(pygame.mouse.get_pos()):
                    menu_open = False

    # Obsługa przejścia między mapami
    if transition_state == "fade_out":
        transition_alpha += transition_speed
        if transition_alpha >= 255:
            transition_alpha = 255
            # Zmiana mapy
            if current_map == "outside":
                current_map = "interior"
                char_x = interior_spawn[0] - char_width // 2
                char_y = interior_spawn[1] - char_height // 2
            else:
                current_map = "outside"
                char_x = outside_spawn[0] - char_width // 2
                char_y = outside_spawn[1] - char_height // 2 + 50
            transition_state = "fade_in"
            
    elif transition_state == "fade_in":
        transition_alpha -= transition_speed
        if transition_alpha <= 0:
            transition_alpha = 0
            transition_state = "idle"

    # Ruch tylko gdy nie ma aktywnej animacji przejścia
    if transition_state == "idle":
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = speed

        new_x = char_x + dx
        new_y = char_y + dy
        
        if current_map == "interior":
            max_x = interior_width - char_width
            max_y = interior_height - char_height
        else:
            max_x = map_width - char_width
            max_y = map_height - char_height
            
        if not check_collision(new_x, new_y):
            char_x = new_x
            char_y = new_y

        char_x = max(0, min(char_x, max_x))
        char_y = max(0, min(char_y, max_y))
        moving = dx != 0 or dy != 0

        if moving:
            walk_timer += 1
            if walk_timer >= 8:
                walk_timer = 0
                walk_frame = (walk_frame + 1)

            if abs(dx) >= abs(dy):
                direction = "right" if dx > 0 else "left"
                frames = walk_right if dx > 0 else walk_left
            else:
                direction = "down" if dy > 0 else "up"
                frames = walk_down if dy > 0 else walk_up

            last_direction = direction
            character = frames[walk_frame % len(frames)]
            last_move_time = time.time()
            idle_triggered = False
            idle_stage = 0
        else:
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

        # Interakcja z kryształem
        if not crystal_taken and current_map == "outside" and is_near(char_x, char_y, *crystal_pos):
            if interact:
                crystal_taken = True

        # Interakcja z portalami
        if current_map == "outside":
            for idx, (px, py) in enumerate([portal1_pos, portal2_pos]):
                if is_near(char_x, char_y, px, py):
                    if crystal_taken and interact:
                        if not portal_active:
                            portal_active = True
                        elif portal_active and not teleporting:
                            teleporting = True
                            teleport_cooldown = 30
                            character = None
                            teleport_target = portal2_pos if (px, py) == portal1_pos else portal1_pos

        # Interakcja z triggerem wejścia (na zewnątrz)
        if current_map == "outside" and is_near(char_x, char_y, *interior_trigger) and interact:
            start_transition()

        # Interakcja z triggerem wyjścia (wewnątrz budynku)
        if current_map == "interior" and is_near(char_x, char_y, *exit_trigger) and interact:
            start_transition()

        # Animacja portali
        if portal_active and current_map == "outside":
            portal_timer += 1
            if portal_timer >= 10:
                portal_timer = 0
                portal_frame = (portal_frame + 1) % 4

        # Teleportacja
        if teleporting:
            if teleport_cooldown > 0:
                teleport_cooldown -= 1
            else:
                char_x, char_y = teleport_target
                teleporting = False
                character = character_idle
                last_move_time = time.time()

    # Kamera
    if current_map == "interior":
        camera_x = char_x + char_width // 2 - screen_width // 2
        camera_y = char_y + char_height // 2 - screen_height // 2
        camera_x = max(0, min(camera_x, interior_width - screen_width))
        camera_y = max(0, min(camera_y, interior_height - screen_height))
    else:
        camera_x = char_x + char_width // 2 - screen_width // 2
        camera_y = char_y + char_height // 2 - screen_height // 2
        camera_x = max(0, min(camera_x, map_width - screen_width))
        camera_y = max(0, min(camera_y, map_height - screen_height))

    # Rysowanie
    if current_map == "interior":
        screen.blit(interior_background, (0, 0), (camera_x, camera_y, screen_width, screen_height))
    else:
        screen.blit(background, (0, 0), (camera_x, camera_y, screen_width, screen_height))

    if current_map == "outside":
        for px, py in [portal1_pos, portal2_pos]:
            if teleporting:
                frame = portal_working[portal_frame]
            elif portal_active:
                frame = portal_waiting[portal_frame]
            else:
                frame = portal_image_idle
            screen.blit(frame, (px - camera_x, py - camera_y))

        if not crystal_taken:
            screen.blit(crystal_image, (crystal_pos[0] - camera_x, crystal_pos[1] - camera_y))

        screen.blit(spawn_image, (spawn_pos[0] - camera_x, spawn_pos[1] - camera_y))

    if character and not teleporting:
        screen.blit(character, (char_x - camera_x, char_y - camera_y))

    # Przycisk menu
    mouse_pos = pygame.mouse.get_pos()
    current_rack = rack_hovered if rack_rect.collidepoint(mouse_pos) else rack_original
    current_rack_rect = current_rack.get_rect(topright=rack_rect.topright)
    screen.blit(current_rack, current_rack_rect)

    if menu_open:
        menu.draw_menu(screen)

    # Animacja przejścia
    if transition_state != "idle":
        s = pygame.Surface((screen_width, screen_height))
        s.set_alpha(transition_alpha)
        s.fill((0, 0, 0))
        screen.blit(s, (0,0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
