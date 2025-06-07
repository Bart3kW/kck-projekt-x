import pygame
import time
import menu

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
background = pygame.image.load('map.png').convert()

# Wczytanie mapy kolizji (czerwony = zablokowany)
collision_map = pygame.image.load('collision_map.png').convert()

# Wczytanie animacji postaci
character_idle = pygame.image.load('character.png').convert_alpha()
walk_right = [pygame.image.load(f'character{i}.png').convert_alpha() for i in range(1, 5)]
walk_left  = [pygame.image.load(f'character{i}.png').convert_alpha() for i in range(5, 9)]
walk_up    = [pygame.image.load(f'character{i}.png').convert_alpha() for i in range(9, 11)]
walk_down  = [pygame.image.load(f'character{i}.png').convert_alpha() for i in range(11, 13)]
character_look_left = pygame.image.load('characterlookleft.png').convert_alpha()
character_look_right = pygame.image.load('characterlookright.png').convert_alpha()

# Portal i kryształ
portal1_pos = (1838, 152)
portal2_pos = (1437, 2305)
portal_image_idle = pygame.image.load("EmptyPortal.png").convert_alpha()
portal_waiting = [pygame.image.load(f"PortalWaiting{i}.png").convert_alpha() for i in range(1, 5)]
portal_working = [pygame.image.load(f"PortalWorking{i}.png").convert_alpha() for i in range(1, 5)]
portal_frame = 0
portal_timer = 0

# Posąg startowy (spawn)
spawn_pos = (1350, 1560)
spawn_image = pygame.image.load("Spawn.png").convert_alpha()

crystal_pos = (2565, 688)
crystal_image = pygame.image.load("Crystal.png").convert_alpha()
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
rack_image = pygame.image.load("Rack.png").convert_alpha()
rack_original = rack_image
rack_hovered = pygame.transform.scale(rack_image, (int(rack_image.get_width() * 0.9), int(rack_image.get_height() * 0.9)))
rack_rect = rack_image.get_rect()
rack_rect.topright = (screen_width - 10, 10)
menu_open = False

# Funkcje kolizji
def is_blocked(x, y):
    """Sprawdza czy dany piksel jest zablokowany (czerwony)"""
    if 0 <= x < map_width and 0 <= y < map_height:
        color = collision_map.get_at((int(x), int(y)))
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
    return any(is_blocked(x, y) for x, y in corners)

def is_near(x1, y1, x2, y2, distance=50):
    """Sprawdza czy pozycje są blisko siebie"""
    return abs(x1 - x2) < distance and abs(y1 - y2) < distance

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
                x_rect = menu.draw_menu(screen)
                if x_rect.collidepoint(pygame.mouse.get_pos()):
                    menu_open = False

    dx, dy = 0, 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = speed
    if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = speed

    new_x = char_x + dx
    new_y = char_y + dy
    if not check_collision(new_x, new_y):
        char_x = new_x
        char_y = new_y

    char_x = max(0, min(char_x, map_width - char_width))
    char_y = max(0, min(char_y, map_height - char_height))
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
    if not crystal_taken and is_near(char_x, char_y, *crystal_pos):
        if interact:
            crystal_taken = True

    # Interakcja z portalami
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

    # Animacja portali
    if portal_active:
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

    camera_x = char_x + char_width // 2 - screen_width // 2
    camera_y = char_y + char_height // 2 - screen_height // 2
    camera_x = max(0, min(camera_x, map_width - screen_width))
    camera_y = max(0, min(camera_y, map_height - screen_height))

    screen.blit(background, (0, 0), (camera_x, camera_y, screen_width, screen_height))

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

    if character:
        screen.blit(character, (char_x - camera_x, char_y - camera_y))

    mouse_pos = pygame.mouse.get_pos()
    current_rack = rack_hovered if rack_rect.collidepoint(mouse_pos) else rack_original
    current_rack_rect = current_rack.get_rect(topright=rack_rect.topright)
    screen.blit(current_rack, current_rack_rect)

    if menu_open:
        menu.draw_menu(screen)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
