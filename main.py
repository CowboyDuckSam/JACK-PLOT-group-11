import sys
import pygame

pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JACK PLOT!!!")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)

MAIN_MENU = "MAIN_MENU"
DUNGEON_ROOM = "DUNGEON_ROOM"
SHOP_ROOM = "SHOP_ROOM"
GAMEOVER_SCREEN = "GAMEOVER_SCREEN"
VICTORY_SCREEN = "VICTORY_SCREEN"

current_state = MAIN_MENU

player_surface = pygame.Surface((50, 50))
player_surface.fill((0, 255, 150))
player_rect = player_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
player_speed = 5

BG_COLORS = {
    MAIN_MENU: (20, 20, 30),
    DUNGEON_ROOM: (10, 40, 10),
    SHOP_ROOM: (40, 10, 40),
    GAMEOVER_SCREEN: (50, 0, 0),
    VICTORY_SCREEN: (50, 50, 0),
}


def draw_text_center(text, y_offset=0):
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)


running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False