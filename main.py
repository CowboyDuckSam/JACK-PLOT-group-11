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
player_max_health = 100
player_health = 100
player_chips = 0

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
    # B. EVENT HANDLING QUEUE
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Temporary controls to test our Finite State Machine (FSM)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_state = MAIN_MENU
            elif event.key == pygame.K_2:
                current_state = DUNGEON_ROOM
            elif event.key == pygame.K_3:
                current_state = SHOP_ROOM
            elif event.key == pygame.K_4:
                current_state = GAMEOVER_SCREEN
            elif event.key == pygame.K_5:
                current_state = VICTORY_SCREEN

    # C. INPUT & GAME LOGIC UPDATE (Only move if in the Dungeon)
    keys = pygame.key.get_pressed()
    if current_state == DUNGEON_ROOM:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_rect.y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_rect.y += player_speed

        # Keep player within screen bounds
        player_rect.clamp_ip(screen.get_rect())

    # D. RENDERING
    # 1. Fill the background based on the current state
    screen.fill(BG_COLORS[current_state])

    # 2. Draw elements specific to the current state
    if current_state == MAIN_MENU:
        draw_text_center("JACK PLOT: MAIN MENU", -20)
        draw_text_center("(Press 2 for Dungeon)", 20)

    elif current_state == DUNGEON_ROOM:
        # Draw the player
        screen.blit(player_surface, player_rect)
        draw_text_center("DUNGEON ROOM", -100)
        draw_text_center("(Press 3 for Shop)", -60)
        health_text = font.render(f"Health: {player_health}/{player_max_health}", True, (255, 100, 100))
        chips_text = font.render(f"Chips: {player_chips}", True, (255, 215, 0))
        screen.blit(health_text, (20, 20))
        screen.blit(chips_text, (20, 60))

    elif current_state == SHOP_ROOM:
        draw_text_center("NEON SHOP", -20)
        draw_text_center("(Press 1 for Menu)", 20)

    elif current_state == GAMEOVER_SCREEN:
        draw_text_center("GAME OVER", 0)

    elif current_state == VICTORY_SCREEN:
        draw_text_center("YOU WIN!", 0)

    # E. DISPLAY FLIP & CLOCK TICK
    pygame.display.flip()  # Update the screen
    clock.tick(60)  # Limit to 60 FPS

    # CLEANUP (Runs after the while loop exits)
pygame.quit()
sys.exit()