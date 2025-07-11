import pygame
import time
import menu  # Upewnij się, że ten moduł istnieje i działa poprawnie
import requests
import json
import os

from pygame.locals import *

pygame.init()

# --- Ustawienia sieciowe ---
SERVER_URL = "http://127.0.0.1:5000"

# --- Ustawienia okna ---
infoObject = pygame.display.Info()
screen_width = infoObject.current_w
screen_height = infoObject.current_h
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gra z portalami i kryształem")

# --- Fonty ---
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 28)
button_font = pygame.font.Font(None, 36)
quiz_player_font = pygame.font.Font(None, 30)

# --- Kolory ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 120, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
INPUT_TEXT_COLOR = WHITE

# --- Plik do zapamiętania użytkownika ---
REMEMBER_ME_FILE = 'remember_me.json'

# --- Wczytanie tła dla ekranu logowania ---
LOGIN_BACKGROUND_PATH = 'lib/graphic/menu/Background.png'
try:
    LOGIN_BACKGROUND_IMAGE = pygame.image.load(LOGIN_BACKGROUND_PATH).convert_alpha()
    LOGIN_BACKGROUND_SCALE = 0.5
    scaled_login_bg_width = int(screen_width * 0.4)
    scaled_login_bg_height = int(screen_height * LOGIN_BACKGROUND_SCALE)
    LOGIN_BACKGROUND_IMAGE = pygame.transform.scale(LOGIN_BACKGROUND_IMAGE, (scaled_login_bg_width, scaled_login_bg_height))
    LOGIN_BACKGROUND_RECT = LOGIN_BACKGROUND_IMAGE.get_rect(center=(screen_width // 2, screen_height // 2))
except pygame.error:
    print(f"Błąd: Nie można załadować obrazu {LOGIN_BACKGROUND_PATH}. Upewnij się, że plik istnieje i jest w odpowiednim katalogu.")
    LOGIN_BACKGROUND_IMAGE = pygame.Surface((screen_width, screen_height))
    LOGIN_BACKGROUND_IMAGE.fill(BLACK)
    LOGIN_BACKGROUND_RECT = LOGIN_BACKGROUND_IMAGE.get_rect(center=(screen_width // 2, screen_height // 2))


# Wczytanie map
try:
    map_width = 2800
    map_height = 2800
    background = pygame.image.load('lib/graphic/maps/main/map.png').convert()
except pygame.error:
    print("Błąd: Nie można załadować map.png.")
    background = pygame.Surface((map_width, map_height))
    background.fill(BLACK)

# Wczytanie mapy kolizji (czerwony = zablokowany)
try:
    collision_map = pygame.image.load('lib/graphic/maps/main/collision_map.png').convert()
except pygame.error:
    print("Błąd: Nie można załadować collision_map.png.")
    collision_map = pygame.Surface((map_width, map_height))
    collision_map.fill(BLACK)

# Wczytanie wnętrza budynku
try:
    interior_background = pygame.image.load('lib/graphic/maps/interior/interior_map.png').convert()
    interior_collision = pygame.image.load('lib/graphic/maps/interior/interior_collision.png').convert()
    interior_width = interior_background.get_width()
    interior_height = interior_background.get_height()
except pygame.error:
    print("Błąd: Nie można załadować interior_map.png lub interior_collision.png.")
    interior_width = 1000
    interior_height = 1000
    interior_background = pygame.Surface((interior_width, interior_height))
    interior_background.fill(BLACK)
    interior_collision = pygame.Surface((interior_width, interior_height))
    interior_collision.fill(BLACK)


# Wczytanie animacji postaci
try:
    character_idle = pygame.image.load('lib/graphic/character/character.png').convert_alpha()
    walk_right = [pygame.image.load(f'lib/graphic/character/character{i}.png').convert_alpha() for i in range(1, 5)]
    walk_left  = [pygame.image.load(f'lib/graphic/character/character{i}.png').convert_alpha() for i in range(5, 9)]
    walk_up    = [pygame.image.load(f'lib/graphic/character/character{i}.png').convert_alpha() for i in range(9, 11)]
    walk_down  = [pygame.image.load(f'lib/graphic/character/character{i}.png').convert_alpha() for i in range(11, 13)]
    character_look_left = pygame.image.load('lib/graphic/character/characterlookleft.png').convert_alpha()
    character_look_right = pygame.image.load('lib/graphic/character/characterlookright.png').convert_alpha()
except pygame.error:
    print("Błąd: Nie można załadować obrazków postaci. Upewnij się, że ścieżki są poprawne.")
    character_idle = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(character_idle, BLUE, (25,25), 25)
    walk_right = [character_idle] * 4
    walk_left = [character_idle] * 4
    walk_up = [character_idle] * 2
    walk_down = [character_idle] * 2
    character_look_left = character_idle
    character_look_right = character_idle


# Portal i kryształ
try:
    portal1_pos = (1838, 152)
    portal2_pos = (1437, 2305)
    portal_image_idle = pygame.image.load("lib/graphic/portal/EmptyPortal.png").convert_alpha()
    portal_waiting = [pygame.image.load(f"lib/graphic/portal/PortalWaiting{i}.png").convert_alpha() for i in range(1, 5)]
    portal_working = [pygame.image.load(f"lib/graphic/portal/PortalWorking{i}.png").convert_alpha() for i in range(1, 5)]
except pygame.error:
    print("Błąd: Nie można załadować obrazków portalu.")
    portal_image_idle = pygame.Surface((100,100), pygame.SRCALPHA)
    pygame.draw.circle(portal_image_idle, (255,0,255), (50,50), 50)
    portal_waiting = [portal_image_idle] * 4
    portal_working = [portal_image_idle] * 4

portal_frame = 0
portal_timer = 0

# Posąg startowy (spawn)
try:
    spawn_pos = (1350, 1560)
    spawn_image = pygame.image.load("lib/graphic/others/Spawn.png").convert_alpha()
except pygame.error:
    print("Błąd: Nie można załadować obrazka spawna.")
    spawn_image = pygame.Surface((100,100), pygame.SRCALPHA)
    pygame.draw.rect(spawn_image, (100,100,100), spawn_image.get_rect())


try:
    crystal_pos = (2565, 688)
    crystal_image = pygame.image.load("lib/graphic/others/Crystal.png").convert_alpha()
except pygame.error:
    print("Błąd: Nie można załadować obrazka kryształu.")
    crystal_image = pygame.Surface((50,50), pygame.SRCALPHA)
    pygame.draw.rect(crystal_image, (0,255,255), crystal_image.get_rect())

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
try:
    rack_image = pygame.image.load("lib/graphic/menu/Rack.png").convert_alpha()
    rack_original = rack_image
    rack_hovered = pygame.transform.scale(rack_image, (int(rack_image.get_width() * 0.9), int(rack_image.get_height() * 0.9)))
    rack_rect = rack_image.get_rect()
    rack_rect.topright = (screen_width - 10, 10)
except pygame.error:
    print("Błąd: Nie można załadować obrazka Rack.png.")
    rack_image = pygame.Surface((50,50), pygame.SRCALPHA)
    pygame.draw.rect(rack_image, GRAY, rack_image.get_rect())
    rack_original = rack_image
    rack_hovered = pygame.transform.scale(rack_image, (int(rack_image.get_width() * 0.9), int(rack_image.get_height() * 0.9)))
    rack_rect = rack_image.get_rect()
    rack_rect.topright = (screen_width - 10, 10)

menu_open = False

# Stan gry
current_map = "outside"
# Usunięto zmienne transition_alpha i transition_speed, transition_state
# Bo nie chcemy animacji ściemniania
interior_trigger = (2290, 290) # Pozycja wejścia do budynku na mapie zewnętrznej
exit_trigger = (1767, 655) # Pozycja wyjścia z budynku na mapie wewnętrznej
interior_spawn = (interior_width // 2, interior_height // 2) # Pozycja postaci po wejściu do budynku
outside_spawn = interior_trigger # Pozycja postaci po wyjściu z budynku (przy wejściu)

# --- Nowe elementy dla quizu ---
# Pozycja triggera quizu na mapie interior
QUIZ_TRIGGER_POS = (interior_width // 2, interior_height // 2 - 50) # Przykładowa pozycja na interior
QUIZ_TRIGGER_RADIUS = 70 # Promień triggera
QUIZ_TRIGGER_TEXT = "Pytanie 1"

quiz_active = False # Czy quiz jest aktywny (czyli w trybie poczekalni/gry)
quiz_state = "idle" # "idle", "lobby", "question_phase"
quiz_players = [] # Lista graczy w poczekalni quizu, zaczynamy pusto
host_username = "" # Zmienna do przechowywania nazwy zalogowanego gospodarza

# Klasa do wyświetlania listy użytkowników i wyszukiwania
class UserListPopup:
    def __init__(self, x, y, width, height, users, host_name):
        self.rect = pygame.Rect(x, y, width, height)
        self.background_color = BLACK
        self.border_color = WHITE
        self.users = users
        self.filtered_users = users
        self.search_input = InputBox(x + 10, y + 10, width - 20, 30, placeholder_text="Szukaj użytkownika")
        self.scroll_offset = 0
        self.item_height = 40
        self.visible_items = (height - 50) // self.item_height # Ile elementów mieści się na raz
        self.host_name = host_name # Nazwa gospodarza, aby nie wyświetlać go na liście

    def handle_event(self, event):
        self.search_input.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Obsługa scrollowania
                if event.button == 4: # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - self.item_height)
                elif event.button == 5: # Scroll down
                    max_scroll = max(0, len(self.filtered_users) * self.item_height - (self.rect.height - 50))
                    self.scroll_offset = min(max_scroll, self.scroll_offset + self.item_height)
                
                # Obsługa kliknięć na użytkowników/przycisk zaproszenia
                display_area_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 50, self.rect.width - 10, self.rect.height - 55)

                for i, user in enumerate(self.filtered_users):
                    item_y_on_popup_surface = i * self.item_height - self.scroll_offset
                    # Przetwarzamy pozycję na ekranie
                    item_y_on_screen = display_area_rect.y + item_y_on_popup_surface
                    
                    # Sprawdź, czy pozycja kliknięcia mieści się w prostokącie elementu
                    if display_area_rect.x <= event.pos[0] <= display_area_rect.x + display_area_rect.width and \
                       item_y_on_screen <= event.pos[1] <= item_y_on_screen + self.item_height:
                        
                        invite_button_rect = pygame.Rect(display_area_rect.width - 75, item_y_on_popup_surface + 5, 70, 30) # Ta pozycja jest względna do temp_surface
                        # Musimy przeliczyć na pozycję globalną dla collidepoint
                        global_invite_button_rect = invite_button_rect.copy()
                        global_invite_button_rect.x += display_area_rect.x
                        global_invite_button_rect.y += display_area_rect.y

                        if global_invite_button_rect.collidepoint(event.pos) and event.button == 1:
                            return user  
        return None

    def update_filter(self):
        search_text = self.search_input.text.lower()
        current_quiz_player_names = [p.split(' ')[0] for p in quiz_players]
        self.filtered_users = [user for user in self.users if search_text in user.lower() and user != self.host_name and user not in current_quiz_player_names]
        self.scroll_offset = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.background_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        self.search_input.draw(screen)

        display_area_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 50, self.rect.width - 10, self.rect.height - 55)
        
        temp_surface = pygame.Surface(display_area_rect.size, pygame.SRCALPHA)

        for i, user in enumerate(self.filtered_users):
            item_y_on_temp_surface = i * self.item_height - self.scroll_offset
            if item_y_on_temp_surface < -(self.item_height) or item_y_on_temp_surface >= display_area_rect.height:
                continue

            user_text_surface = small_font.render(user, True, WHITE)
            temp_surface.blit(user_text_surface, (5, item_y_on_temp_surface + 5))

            invite_button_rect = pygame.Rect(display_area_rect.width - 75, item_y_on_temp_surface + 5, 70, 30)
            pygame.draw.rect(temp_surface, BLUE, invite_button_rect)
            invite_text_surface = small_font.render("Zaproś", True, WHITE)
            invite_text_rect = invite_text_surface.get_rect(center=invite_button_rect.center)
            temp_surface.blit(invite_text_surface, invite_text_rect)
            
        screen.blit(temp_surface, display_area_rect.topleft)

# Funkcje kolizji
def is_blocked(x, y, map_type):
    """Sprawdza czy dany piksel jest zablokowany (czerwony) na konkretnej mapie kolizji."""
    if map_type == "outside":
        map_surface = collision_map
        w, h = map_width, map_height
    else: # map_type == "interior"
        map_surface = interior_collision
        w, h = interior_width, interior_height
        
    if 0 <= x < w and 0 <= y < h:
        color = map_surface.get_at((int(x), int(y)))
        return color.r == 255 and color.g == 0 and color.b == 0
    return True  # traktuj poza mapą jako zablokowane

def check_collision(new_x, new_y):
    """Sprawdza kolizję dla 4 rogów postaci na aktualnej mapie."""
    corners = [
        (new_x, new_y),
        (new_x + char_width - 1, new_y),
        (new_x, new_y + char_height - 1),
        (new_x + char_width - 1, new_y + char_height - 1)
    ]
    
    return any(is_blocked(x, y, current_map) for x, y in corners)

def is_near(x1, y1, x2, y2, distance=50):
    """Sprawdza czy pozycje są blisko siebie."""
    return abs(x1 - x2) < distance and abs(y1 - y2) < distance

def is_inside_circle(px, py, circle_x, circle_y, radius):
    """Sprawdza, czy punkt (px, py) jest wewnątrz okręgu."""
    distance = ((px - circle_x)**2 + (py - circle_y)**2)**0.5
    return distance <= radius

# Funkcja start_transition jest teraz zbędna, ponieważ nie ma ściemniania.
# Możemy ją usunąć lub zostawić pustą, jeśli jest gdzieś wywoływana.
def start_transition():
    pass # Nic nie robi, bo nie ma przejścia z efektem ściemniania

# --- Logika ekranu logowania ---
class InputBox:
    def __init__(self, x, y, w, h, text='', placeholder_text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.placeholder_text = placeholder_text
        self.txt_surface = font.render(self.text, True, INPUT_TEXT_COLOR)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_width = w

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.color = LIGHT_GRAY
                self.cursor_visible = True
                self.cursor_timer = 0
            else:
                self.active = False
                self.color = GRAY
            self.txt_surface = font.render(self.text, True, INPUT_TEXT_COLOR)
        if event.type == pygame.KEYDOWN:
            if self.active:
                self.cursor_visible = True
                self.cursor_timer = 0

                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = GRAY
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode.isprintable():
                        self.text += event.unicode
                self.txt_surface = font.render(self.text, True, INPUT_TEXT_COLOR)
                self.rect.w = max(self.max_width, self.txt_surface.get_width() + 10)


    def update(self):
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
        else:
            self.cursor_visible = False

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
        if self.text:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        elif self.placeholder_text and not self.active:
            placeholder_surface = font.render(self.placeholder_text, True, GRAY)
            screen.blit(placeholder_surface, (self.rect.x + 5, self.rect.y + 5))

        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + self.txt_surface.get_width()
            cursor_y = self.rect.y + 5
            cursor_height = self.txt_surface.get_height()
            pygame.draw.line(screen, INPUT_TEXT_COLOR, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)


class ImageButton:
    def __init__(self, x, y, image_path, action=None):
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            print(f"Błąd: Nie można załadować obrazka {image_path}. Używam domyślnego przycisku.")
            self.original_image = pygame.Surface((150, 50), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, BLUE, self.original_image.get_rect(), border_radius=5)
            font_temp = pygame.font.Font(None, 30)
            text_surf = font_temp.render(os.path.basename(image_path).replace(".png", ""), True, WHITE)
            text_rect = text_surf.get_rect(center = self.original_image.get_rect().center)
            self.original_image.blit(text_surf, text_rect)

        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.action = action

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    return self.action()
        return False

class TextButton:
    def __init__(self, x, y, width, height, text, color, text_color, action=None):
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy() # Aktualna pozycja i rozmiar dla rysowania
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action
        self.font = small_font
        self.is_hovered = False

        # Tworzymy powierzchnię dla normalnego stanu
        self.original_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._draw_button_on_surface(self.original_surface, self.color, self.text, self.text_color, self.font)

        # Tworzymy powierzchnię dla stanu najechany (5% mniejsza)
        hover_width = int(width * 0.95)
        hover_height = int(height * 0.95)
        self.hover_surface = pygame.Surface((hover_width, hover_height), pygame.SRCALPHA)
        self._draw_button_on_surface(self.hover_surface, self.color, self.text, self.text_color, self.font)

        self.current_display_surface = self.original_surface # Powierzchnia, która będzie rysowana
        self.current_display_rect = self.original_rect.copy() # Rect używany do rysowania

    def _draw_button_on_surface(self, surface, color, text, text_color, font):
        """Pomocnicza funkcja do rysowania przycisku na danej powierzchni."""
        surface.fill((0,0,0,0)) # Wyczyść powierzchnię (przezroczyste tło)
        pygame.draw.rect(surface, color, surface.get_rect())
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=surface.get_rect().center)
        surface.blit(text_surface, text_rect)

    def update_position(self, new_x, new_y):
        """Aktualizuje pozycję PRZYCISKU. To ustawia jego oryginalną pozycję."""
        self.original_rect.topleft = (new_x, new_y)
        # Przy aktualizacji pozycji, resetujemy stan najechania i aktualną pozycję rysowania
        self.is_hovered = False
        self.current_display_surface = self.original_surface
        self.current_display_rect = self.original_rect.copy()

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        
        # Sprawdzamy najechanie na oryginalny prostokąt, ale zmieniamy rect do rysowania
        if self.original_rect.collidepoint(mouse_pos):
            if not self.is_hovered:
                self.is_hovered = True
                # Oblicz nową, zmniejszoną pozycję i rozmiar
                new_width = int(self.original_rect.width * 0.95)
                new_height = int(self.original_rect.height * 0.95)
                # Obliczamy nową pozycję, aby przycisk zmniejszał się do środka
                new_x = self.original_rect.centerx - new_width // 2
                new_y = self.original_rect.centery - new_height // 2

                self.current_display_rect = pygame.Rect(new_x, new_y, new_width, new_height)
                self.current_display_surface = self.hover_surface
        else:
            if self.is_hovered:
                self.is_hovered = False
                self.current_display_rect = self.original_rect.copy()
                self.current_display_surface = self.original_surface

        screen.blit(self.current_display_surface, self.current_display_rect)


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Sprawdź kliknięcie na ORYGINALNYM PROSTOKĄCIE (aby obszar klikalny był stały)
            if self.original_rect.collidepoint(event.pos) and event.button == 1: # event.button == 1 to lewy przycisk myszy
                if self.action:
                    return self.action()
        return False


class Checkbox:
    def __init__(self, x, y, size, text, checked=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.checked = checked
        self.text = text
        self.size = size

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, GREEN, (self.rect.x + 3, self.rect.y + self.size // 2),
                                             (self.rect.x + self.size // 2, self.rect.y + self.size - 3), 3)
            pygame.draw.line(screen, GREEN, (self.rect.x + self.size // 2, self.rect.y + self.size - 3),
                                             (self.rect.x + self.size - 3, self.rect.y + 3), 3)
            
        text_surface = small_font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + self.size + 10, self.rect.y + (self.size - text_surface.get_height()) // 2))

def load_remembered_user():
    if os.path.exists(REMEMBER_ME_FILE):
        try:
            with open(REMEMBER_ME_FILE, 'r') as f:
                data = json.load(f)
                return data.get('username', '')
        except json.JSONDecodeError:
            return ''
    return ''

def save_remembered_user(username):
    with open(REMEMBER_ME_FILE, 'w') as f:
        json.dump({'username': username}, f)

def clear_remembered_user():
    if os.path.exists(REMEMBER_ME_FILE):
        os.remove(REMEMBER_ME_FILE)

def login_screen():
    global host_username
    remembered_username = load_remembered_user()
    
    center_x = LOGIN_BACKGROUND_RECT.centerx
    center_y = LOGIN_BACKGROUND_RECT.centery

    input_box_width = 300
    input_box_height = 50
    input_spacing = 60

    username_input_y = center_y - input_box_height - input_spacing // 2
    username_input = InputBox(center_x - input_box_width // 2, username_input_y, input_box_width, input_box_height, text=remembered_username, placeholder_text="Nazwa użytkownika")
    
    password_input_y = center_y + input_spacing // 2 - input_box_height // 2
    password_input = InputBox(center_x - input_box_width // 2, password_input_y, input_box_width, input_box_height, placeholder_text="Hasło")

    checkbox_size = 20
    remember_me_checkbox_y = password_input.rect.bottom + 15
    remember_me_checkbox = Checkbox(center_x - input_box_width // 2, remember_me_checkbox_y, checkbox_size, "Zapamiętaj nazwę użytkownika", checked=(remembered_username != ''))

    login_message = ""
    message_color = WHITE

    def attempt_login():
        nonlocal login_message, message_color
        if not username_input.text or not password_input.text:
            login_message = "Proszę wypełnić wszystkie pola."
            message_color = RED
            return False
        try:
            response = requests.post(f"{SERVER_URL}/login", json={
                "username": username_input.text,
                "password": password_input.text
            })
            if response.status_code == 200:
                login_message = "Logowanie udane!"
                message_color = GREEN
                if remember_me_checkbox.checked:
                    save_remembered_user(username_input.text)
                else:
                    clear_remembered_user()
                host_username = username_input.text
                return True
            else:
                login_message = response.json().get("message", "Błąd logowania.")
                message_color = RED
                return False
        except requests.exceptions.ConnectionError:
            login_message = "Nie można połączyć się z serwerem. Upewnij się, że serwer jest uruchomiony."
            message_color = RED
            return False
        except Exception as e:
            login_message = f"Wystąpił nieoczekiwany błąd: {e}"
            message_color = RED
            return False

    def attempt_register():
        nonlocal login_message, message_color
        if not username_input.text or not password_input.text:
            login_message = "Proszę wypełnić wszystkie pola."
            message_color = RED
            return
        try:
            response = requests.post(f"{SERVER_URL}/register", json={
                "username": username_input.text,
                "password": password_input.text
            })
            if response.status_code == 201:
                login_message = "Rejestracja udana! Możesz się teraz zalogować."
                message_color = GREEN
                username_input.text = ""
                password_input.text = ""
                username_input.txt_surface = font.render(username_input.text, True, INPUT_TEXT_COLOR)
                password_input.txt_surface = font.render(password_input.text, True, INPUT_TEXT_COLOR)
            else:
                login_message = response.json().get("message", "Błąd rejestracji.")
                message_color = RED
        except requests.exceptions.ConnectionError:
            login_message = "Nie można połączyć się z serwerem. Upewnij się, że serwer jest uruchomiony."
            message_color = RED
        except Exception as e:
            login_message = f"Wystąpił nieoczekiwany błąd: {e}"
            message_color = RED

    login_button_image_path = 'lib/graphic/menu/ZalogujButton.png'
    register_button_image_path = 'lib/graphic/menu/RejestracjaButton.png'

    login_button = ImageButton(0, 0, login_button_image_path, attempt_login)
    register_button = ImageButton(0, 0, register_button_image_path, attempt_register)

    button_y_offset = 120
    login_button_x = center_x - login_button.rect.width - 5
    login_button_y = center_y + button_y_offset
    login_button.rect.topleft = (login_button_x, login_button_y)

    register_button_x = center_x + 5
    register_button_y = center_y + button_y_offset
    register_button.rect.topleft = (register_button_x, register_button_y)


    running_login_screen = True
    logged_in = False

    while running_login_screen:
        screen.fill(BLACK)
        screen.blit(LOGIN_BACKGROUND_IMAGE, LOGIN_BACKGROUND_RECT)

        title_text = font.render("Witaj! Zaloguj się lub Zarejestruj", True, WHITE)
        title_rect = title_text.get_rect(center=(screen_width // 2, LOGIN_BACKGROUND_RECT.top - 30))
        screen.blit(title_text, title_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            username_input.handle_event(event)
            password_input.handle_event(event)
            remember_me_checkbox.handle_event(event)
            
            if login_button.handle_event(event):
                logged_in = True
                running_login_screen = False
            register_button.handle_event(event)

        username_input.update()
        password_input.update()

        username_input.draw(screen)
        password_input.draw(screen)
        remember_me_checkbox.draw(screen)
        login_button.draw(screen)
        register_button.draw(screen)

        if login_message:
            message_surface = small_font.render(login_message, True, message_color)
            message_rect = message_surface.get_rect(center=(screen_width // 2, LOGIN_BACKGROUND_RECT.bottom + 30))
            screen.blit(message_surface, message_rect)

        pygame.display.flip()
        clock.tick(30)

    return logged_in


# --- Główna pętla gry ---
clock = pygame.time.Clock()
running = True

# Popup do zapraszania użytkowników
invite_popup = None
# Mockowa lista aktywnych użytkowników (do zastąpienia przez serwer)
MOCK_ACTIVE_USERS = ["Gracz1", "Gracz2", "Gracz3", "Asia", "Tomek", "Anna", "Zenek", "Krzysiek", "Ola", "Piotr"]

# Funkcja do "zapraszania" gracza (na razie print)
def send_invite(invited_user):
    global quiz_players
    # Pobierz same nazwy graczy bez "(Gospodarz)"
    current_quiz_player_names = [p.split(' ')[0] for p in quiz_players]

    # Sprawdzamy, czy użytkownik już jest na liście (tylko nazwa)
    # i czy liczba graczy nie przekracza limitu (3)
    if invited_user not in current_quiz_player_names and len(quiz_players) < 3:
        quiz_players.append(invited_user)
        print(f"Zaproszenie wysłane do {invited_user}")
        return True
    print(f"Nie można zaprosić {invited_user}. Już jest na liście lub lista pełna.")
    return False

# Funkcja do otwierania popupu zapraszania
def open_invite_popup():
    global invite_popup
    popup_width = 300
    popup_height = 400
    popup_x = screen_width // 2 - popup_width // 2
    popup_y = screen_height // 2 - popup_height // 2
    invite_popup = UserListPopup(popup_x, popup_y, popup_width, popup_height, MOCK_ACTIVE_USERS, host_username)


if login_screen():
    # Upewnij się, że gospodarz jest dodany tylko raz i jest pierwszy
    if host_username and not any(host_username in p.split(' ')[0] for p in quiz_players):
        quiz_players.insert(0, f"{host_username} (Gospodarz)")
    print("Użytkownik zalogowany, uruchamiam grę...")
else:
    print("Logowanie nieudane lub zamknięto ekran logowania, wychodzę z gry...")
    running = False

# --- Zmienna do kontrolowania wysokości panelu quizu ---
QUIZ_PANEL_OFFSET_Y = 100 

### ZMIANY DLA PRZYCISKÓW ZAPROŚ I SLOTÓW GRACZY ###
# Przygotowanie listy przycisków "Zaproś"
# Tworzymy tylko DWA przyciski, bo pierwszy slot jest dla gospodarza
invite_buttons = []
for _ in range(2): 
    invite_buttons.append(TextButton(0, 0, 70, 30, "Zaproś", BLUE, WHITE, open_invite_popup))
### KONIEC ZMIAN DLA PRZYCISKÓW ZAPROŚ I SLOTÓW GRACZY ###


while running:
    keys = pygame.key.get_pressed()
    interact = False # Resetuj interact na początku każdej klatki

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                interact = True # Ustaw interact na True tylko przy naciśnięciu E
            elif event.key == pygame.K_ESCAPE: # Dodano obsługę ESCAPE dla zamykania menu
                if menu_open:
                    menu_open = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not menu_open and rack_rect.collidepoint(pygame.mouse.get_pos()):
                menu_open = True
            elif menu_open:
                x_rect = menu.draw_menu(screen)
                if x_rect and x_rect.collidepoint(pygame.mouse.get_pos()):
                    menu_open = False
            # Obsługa eventów dla popupu zapraszania
            if invite_popup:
                invited_user = invite_popup.handle_event(event)
                if invited_user:
                    send_invite(invited_user)
                    invite_popup.update_filter() # Odśwież listę po zaproszeniu


    # Tylko jeśli nie teleportujemy się, quiz nie jest aktywny i menu nie jest otwarte, pozwól na ruch
    if not teleporting and not quiz_active and not menu_open:
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = speed

        new_x = char_x + dx
        new_y = char_y + dy
        
        # Sprawdź kolizje na bieżącej mapie
        if not check_collision(new_x, new_y):
            char_x = new_x
            char_y = new_y

        # Ograniczenie pozycji postaci do granic mapy
        if current_map == "outside":
            char_x = max(0, min(char_x, map_width - char_width))
            char_y = max(0, min(char_y, map_height - char_height))
        else: # interior
            char_x = max(0, min(char_x, interior_width - char_width))
            char_y = max(0, min(char_y, interior_height - char_height))

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

    # --- Logika zmiany map ---
    # Wejście do budynku
    if current_map == "outside" and is_near(char_x, char_y, *interior_trigger, distance=70):
        if interact:
            current_map = "interior"
            char_x, char_y = interior_spawn[0] - char_width // 2, interior_spawn[1] - char_height // 2
            print("Wszedłeś do budynku.")

    # Wyjście z budynku
    if current_map == "interior" and is_near(char_x, char_y, *exit_trigger, distance=70):
        if interact:
            current_map = "outside"
            char_x, char_y = outside_spawn[0] - char_width // 2, outside_spawn[1] - char_height // 2
            print("Wyszedłeś z budynku.")

    # --- Interakcja z kryształem ---
    if not crystal_taken and current_map == "outside" and is_near(char_x, char_y, *crystal_pos):
        if interact:
            crystal_taken = True
            print("Kryształ zebrany!") # Do celów debugowania

    # --- Interakcja z portalami ---
    for idx, (px, py) in enumerate([portal1_pos, portal2_pos]):
        if is_near(char_x, char_y, px, py):
            if crystal_taken and interact: # Sprawdź, czy naciśnięto 'E' i masz kryształ
                if not portal_active:
                    portal_active = True
                    print(f"Portal {idx+1} aktywowany!") # Do celów debugowania
                elif portal_active and not teleporting:
                    teleporting = True
                    teleport_cooldown = 30 # Czas, w którym portal animuje i postać jest ukryta
                    character = None # Ukryj postać
                    # Ustaw cel teleportacji na drugi portal
                    teleport_target = portal2_pos if (px, py) == portal1_pos else portal1_pos
                    print(f"Rozpoczynam teleportację z portalu {idx+1} do {teleport_target}!") # Do celów debugowania

    # --- Animacja portali ---
    if portal_active or teleporting: # Animuj portale, jeśli są aktywne lub w trakcie teleportacji
        portal_timer += 1
        if portal_timer >= 10: # Prędkość animacji portalu
            portal_timer = 0
            portal_frame = (portal_frame + 1) % 4 # 4 klatki animacji

    # --- Obsługa teleportacji (przeniesienie postaci po odliczeniu cooldownu) ---
    if teleporting:
        if teleport_cooldown > 0:
            teleport_cooldown -= 1
        else:
            char_x, char_y = teleport_target # Przenieś postać
            teleporting = False # Zakończ teleportację
            character = character_idle # Przywróć postać
            last_move_time = time.time() # Zresetuj czas bezczynności
            print("Teleportacja zakończona!") # Do celów debugowania
            # Jeśli portal ma się wyłączyć po teleportacji, odkomentuj poniższą linię:
            # portal_active = False


    # --- Logika quizu ---
    if current_map == "interior":
        if is_inside_circle(char_x + char_width // 2, char_y + char_height // 2, QUIZ_TRIGGER_POS[0], QUIZ_TRIGGER_POS[1], QUIZ_TRIGGER_RADIUS):
            if interact and quiz_state == "idle":
                quiz_active = True
                quiz_state = "lobby" # Przejdź do poczekalni quizu
                print("Wszedłeś w obszar quizu!")

    # --- Rysowanie ---
    # Obliczanie pozycji kamery
    if current_map == "outside":
        cam_map_width = map_width
        cam_map_height = map_height
        current_bg = background
    else: # interior
        cam_map_width = interior_width
        cam_map_height = interior_height
        current_bg = interior_background

    camera_x = char_x + char_width // 2 - screen_width // 2
    camera_y = char_y + char_height // 2 - screen_height // 2
    camera_x = max(0, min(camera_x, cam_map_width - screen_width))
    camera_y = max(0, min(camera_y, cam_map_height - screen_height))

    # Rysowanie tła
    screen.blit(current_bg, (0, 0), (camera_x, camera_y, screen_width, screen_height))

    # Rysowanie portali (tylko na mapie zewnętrznej)
    if current_map == "outside":
        for px, py in [portal1_pos, portal2_pos]:
            if teleporting:
                # Podczas teleportacji, portale mają animację "working"
                frame = portal_working[portal_frame]
            elif portal_active:
                # Gdy portal jest aktywny (po zebraniu kryształu i pierwszej interakcji), ma animację "waiting"
                frame = portal_waiting[portal_frame]
            else:
                # W przeciwnym razie, portal jest w stanie "idle"
                frame = portal_image_idle
            screen.blit(frame, (px - camera_x, py - camera_y))

    # Rysowanie kryształu, jeśli nie został zebrany (tylko na mapie zewnętrznej)
    if not crystal_taken and current_map == "outside":
        screen.blit(crystal_image, (crystal_pos[0] - camera_x, crystal_pos[1] - camera_y))

    # Rysowanie spawnu (tylko na mapie zewnętrznej)
    if current_map == "outside":
        screen.blit(spawn_image, (spawn_pos[0] - camera_x, spawn_pos[1] - camera_y))
    
    # Rysowanie triggera quizu (tylko na mapie interior)
    if current_map == "interior":
        quiz_trigger_screen_pos = (QUIZ_TRIGGER_POS[0] - camera_x, QUIZ_TRIGGER_POS[1] - camera_y)
        pygame.draw.circle(screen, RED, quiz_trigger_screen_pos, QUIZ_TRIGGER_RADIUS, 2)
        quiz_text_surface = small_font.render(QUIZ_TRIGGER_TEXT, True, WHITE)
        quiz_text_rect = quiz_text_surface.get_rect(center=quiz_trigger_screen_pos)
        screen.blit(quiz_text_surface, quiz_text_rect)

    # Rysowanie postaci, jeśli nie jest w trakcie teleportacji (czyli character nie jest None)
    if character:
        screen.blit(character, (char_x - camera_x, char_y - camera_y))

    # Rysowanie przycisku menu
    mouse_pos = pygame.mouse.get_pos()
    current_rack = rack_hovered if rack_rect.collidepoint(mouse_pos) else rack_original
    current_rack_rect = current_rack.get_rect(topright=rack_rect.topright)
    screen.blit(current_rack, current_rack_rect)

    # Rysowanie menu, jeśli otwarte
    if menu_open:
        menu.draw_menu(screen) # Upewnij się, że menu.py działa poprawnie i rysuje się na screen


    # --- Rysowanie panelu quizu, jeśli jest aktywny ---
    if quiz_active:
        panel_height = 250 # Stała wysokość panelu quizu
        panel_rect = pygame.Rect(screen_width // 2 - 300, screen_height - panel_height - QUIZ_PANEL_OFFSET_Y, 600, panel_height)
        pygame.draw.rect(screen, BLACK, panel_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, panel_rect, 2, border_radius=10)

        title_quiz_text = font.render("Poczekalnia Quizu", True, WHITE)
        title_quiz_rect = title_quiz_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 20))
        screen.blit(title_quiz_text, title_quiz_rect)

        # Wyświetlanie graczy i przycisków zaproś
        player_slot_start_y = panel_rect.y + 60
        player_slot_height = 40
        for i in range(3): # Maksymalnie 3 graczy (Gospodarz + 2 zaproszonych)
            slot_y = player_slot_start_y + i * player_slot_height
            
            player_name = quiz_players[i] if i < len(quiz_players) else f"Wolny slot {i+1}"
            
            # Kolor dla gospodarza
            player_color = GREEN if i == 0 and host_username in player_name else WHITE
            
            player_text_surface = quiz_player_font.render(player_name, True, player_color)
            screen.blit(player_text_surface, (panel_rect.x + 20, slot_y + 5))

            # Przycisk "Zaproś" tylko dla wolnych slotów (poza gospodarzem)
            if i > 0 and i >= len(quiz_players) and len(quiz_players) < 3:
                invite_btn = invite_buttons[i-1] # Pobierz odpowiedni przycisk
                invite_btn.update_position(panel_rect.right - 100, slot_y + 5) # Aktualizuj pozycję przycisku
                invite_btn.draw(screen) # Rysuj przycisk

                # Obsługa zdarzeń dla przycisków zaproszenia (tylko jeśli quiz jest aktywny)
                if quiz_active: # Upewnij się, że przyciski reagują tylko w quiz_active
                    invite_btn.handle_event(event) # Przekazujemy eventy do przycisku


    # Rysowanie popupu zapraszania, jeśli jest aktywny
    if invite_popup:
        invite_popup.draw(screen)
        invite_popup.update_filter() # Aktualizuj filtr za każdym razem, gdy rysujesz

    # Aktualizacja wyświetlania
    pygame.display.update()
    clock.tick(60) # Ograniczenie klatek na sekundę do 60

pygame.quit()
