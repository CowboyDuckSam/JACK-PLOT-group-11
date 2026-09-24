import pygame

# DISPLAY
WIDTH, HEIGHT = 960, 540


# GAME STATES
CHAR_SELECT = "CHAR_SELECT"
MAIN_MENU = "MAIN_MENU"
DUNGEON_ROOM = "DUNGEON_ROOM"
SHOP_ROOM = "SHOP_ROOM"
GAMEOVER_SCREEN = "GAMEOVER_SCREEN"
VICTORY_SCREEN = "VICTORY_SCREEN"
LOGIN_SCREEN = "LOGIN_SCREEN"

Skin_options = {
    "Male": [(50, 150, 255), (0, 50, 200), (100, 200, 255)],
    "Female": [(255, 100, 200), (200, 0, 100), (255, 180, 220)]
}

# COLORS
BG_COLORS = {
    MAIN_MENU: (20, 20, 30),
    DUNGEON_ROOM: (10, 40, 10),
    SHOP_ROOM: (40, 10, 40),
    GAMEOVER_SCREEN: (50, 0, 0),
    VICTORY_SCREEN: (50, 50, 0),
    CHAR_SELECT: (15, 15, 25),
    LOGIN_SCREEN: (20, 20, 40),
}

# AVATAR
SKIN_OPTIONS = {
    "Male": [(50, 150, 255), (0, 50, 200), (100, 200, 255)],
    "Female": [(255, 100, 200), (200, 0, 100), (255, 180, 220)]
}

# Map Design
dungeon_walls = [
    # Borders
    pygame.Rect(0, 0, 2000, 50),
    pygame.Rect(0, 0, 50, 2000),
    pygame.Rect(1950, 0, 50, 2000),
    pygame.Rect(0, 1950, 2000, 50),
    # Obstacles
    pygame.Rect(500, 500, 300, 50),
    pygame.Rect(1200, 800, 50, 400),
    pygame.Rect(400, 1200, 200, 200),
    pygame.Rect(1500, 300, 150, 150),
]

