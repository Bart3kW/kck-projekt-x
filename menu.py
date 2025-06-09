import pygame
import sys

def load_image(name):
    return pygame.image.load(name).convert_alpha()

# Zmienna globalna do jednokrotnego załadunku
assets_loaded = False
background = None
menu_banner = None
buttons = []
close_button = None

button_names = [
    "lib/graphic/menu/ZalogujButton.png",
    "lib/graphic/menu/RejestracjaButton.png",
    "lib/graphic/menu/ZaprosButton.png",
    "lib/graphic/menu/UstawieniaButton.png",
    "lib/graphic/menu/ZapisButton.png",
    "lib/graphic/menu/WyjscieButton.png"  # <- przycisk wyjścia
]

def draw_menu(screen):
    global assets_loaded, background, menu_banner, buttons, close_button

    if not assets_loaded:
        background = load_image("lib/graphic/menu/Background.png")
        menu_banner = load_image("lib/graphic/menu/Menu.png")
        buttons = [load_image(name) for name in button_names]
        close_button = load_image("lib/graphic/menu/X.png")
        assets_loaded = True

    bg_width, bg_height = screen.get_size()

    # Wycentrowanie tła + przesunięcie w górę
    offset_y = -40
    bg_rect = background.get_rect(center=screen.get_rect().center)
    bg_rect.y += offset_y
    screen.blit(background, bg_rect.topleft)

    # Pozycja banera
    menu_y_offset = bg_rect.y + 80
    menu_pos = (bg_width // 2 - menu_banner.get_width() // 2, menu_y_offset)
    screen.blit(menu_banner, menu_pos)

    # Przycisk zamykania X
    x_offset_x = 130
    x_offset_y = -10
    x_button_pos = (
        menu_pos[0] + menu_banner.get_width() - close_button.get_width() // 2 + x_offset_x,
        menu_pos[1] + x_offset_y
    )

    # Przyciski menu
    start_y = menu_pos[1] + menu_banner.get_height() + 40
    button_spacing = 20
    button_positions = []

    for i, btn in enumerate(buttons):
        x = bg_width // 2 - btn.get_width() // 2
        y = start_y + i * (btn.get_height() + button_spacing)
        button_positions.append((x, y))

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]

    for i, (btn, pos) in enumerate(zip(buttons, button_positions)):
        rect = btn.get_rect(topleft=pos)
        if rect.collidepoint(mouse_pos):
            scaled_btn = pygame.transform.scale(
                btn, (int(btn.get_width() * 0.9), int(btn.get_height() * 0.9))
            )
            scaled_pos = (
                pos[0] + (btn.get_width() - scaled_btn.get_width()) // 2,
                pos[1] + (btn.get_height() - scaled_btn.get_height()) // 2
            )
            screen.blit(scaled_btn, scaled_pos)
            rect = scaled_btn.get_rect(topleft=scaled_pos)

            # Kliknięcie „Wyjście”
            if mouse_click and i == len(buttons) - 1:
                pygame.quit()
                sys.exit()
        else:
            screen.blit(btn, pos)

    # Obsługa zamknięcia X
    x_rect = close_button.get_rect(topleft=x_button_pos)
    if x_rect.collidepoint(mouse_pos):
        scaled_x = pygame.transform.scale(
            close_button,
            (int(close_button.get_width() * 0.9), int(close_button.get_height() * 0.9))
        )
        scaled_x_pos = (
            x_button_pos[0] + (close_button.get_width() - scaled_x.get_width()) // 2,
            x_button_pos[1] + (close_button.get_height() - scaled_x.get_height()) // 2
        )
        screen.blit(scaled_x, scaled_x_pos)
        x_rect = scaled_x.get_rect(topleft=scaled_x_pos)
    else:
        screen.blit(close_button, x_button_pos)

    return x_rect
