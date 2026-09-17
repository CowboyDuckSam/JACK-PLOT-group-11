import sys
import pygame
from wheel import FateWheel


pygame.init()
WIDTH, HEIGHT = 960, 540
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
fate_wheel = FateWheel()


player_surface = pygame.Surface((50, 50))
player_surface.fill((0, 255, 150))
player_rect = player_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
player_speed = 300
player_pos_x = float(player_rect.x)
player_pos_y = float(player_rect.y)
player_max_health = 100
player_health = 100
player_chips = 0
player_deck = []  # To tracks the active cards Jack holds
wall_rect = pygame.Rect(500, 100, 50, 200)  # A placeholder obstacle (x, y, width, height)
shop_dice_result = 1
shop_message = "Welcome! 10 Chips to roll the die."



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


dt = 0
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

            # For the fate wheel
            if current_state == DUNGEON_ROOM:
                if event.key == pygame.K_r and not fate_wheel.active:
                    fate_wheel.open()

                elif event.key == pygame.K_SPACE and fate_wheel.active and not fate_wheel.spinning and fate_wheel.result_index is None:
                    fate_wheel.start_spin()

                elif event.key == pygame.K_RETURN and fate_wheel.active and fate_wheel.result_index is not None:
                    fate_wheel.close()

    # C. INPUT & GAME LOGIC UPDATE (Only move if in the Dungeon)
    keys = pygame.key.get_pressed()
    if current_state == DUNGEON_ROOM:

        if fate_wheel.active:
            fate_wheel.update(dt)

            if not fate_wheel.spinning and fate_wheel.result_index is not None and not fate_wheel.result_applied:
                result = fate_wheel.apply_result(player_chips, player_deck)
                if result:
                    label, player_chips = result  # Update the chips

        else:
            old_x, old_y = player_pos_x, player_pos_y

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_pos_x -= player_speed * dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_pos_x += player_speed * dt
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_pos_y -= player_speed * dt
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_pos_y += player_speed * dt

            # Keep player within screen bounds
            player_rect.x = int(player_pos_x)
            player_rect.y = int(player_pos_y)

            map_bounds = pygame.Rect(0, 0, 2000, 2000)
            player_rect.clamp_ip(map_bounds)
            player_pos_x, player_pos_y = float(player_rect.x), float(player_rect.y)

            if player_rect.colliderect(wall_rect):
                player_pos_x, player_pos_y = old_x, old_y
                player_rect.x, player_rect.y = int(player_pos_x), int(player_pos_y)

    # D. RENDERING

    # 1. Fill the background based on the current state
    screen.fill(BG_COLORS[current_state])

    # 2. Draw elements specific to the current state
    if current_state == MAIN_MENU:
        draw_text_center("JACK PLOT: MAIN MENU", -20)
        draw_text_center("(Press 2 for Dungeon)", 20)

    elif current_state == DUNGEON_ROOM:
        # 1. cam offset
        cam_x = player_rect.centerx - (WIDTH // 2)
        cam_y = player_rect.centery - (HEIGHT // 2)

        # Keep camera inside the 2000x2000 map bounds
        cam_x = max(0, min(cam_x, 2000 - WIDTH))
        cam_y = max(0, min(cam_y, 2000 - HEIGHT))

        # 2.  draw the world
        floor_rect = pygame.Rect(0 - cam_x, 0 - cam_y, 2000, 2000)
        pygame.draw.rect(screen, (20, 30, 20), floor_rect)

        # Shift the wall by the camera offset
        offset_wall = wall_rect.move(-cam_x, -cam_y)
        pygame.draw.rect(screen, (100, 100, 100), offset_wall)

        # Shift the player by the camera offset
        offset_player = player_rect.move(-cam_x, -cam_y)
        screen.blit(player_surface, offset_player)

        # 3. draw UI (no offsets, so it sticks to the screen)
        health_text = font.render(f"Health: {player_health}/{player_max_health}", True, (255, 100, 100))
        chips_text = font.render(f"Chips: {player_chips}", True, (255, 215, 0))
        screen.blit(health_text, (20, 20))
        screen.blit(chips_text, (20, 60))

        # Draw the FateWheel on top of everything!
        fate_wheel.draw(screen, font)


    elif current_state == SHOP_ROOM:
        draw_text_center("NEON SHOP", -20)
        draw_text_center("(Press 1 for Menu)", 20)

    elif current_state == GAMEOVER_SCREEN:
        draw_text_center("GAME OVER", 0)

    elif current_state == VICTORY_SCREEN:
        draw_text_center("YOU WIN!", 0)

    # E. DISPLAY FLIP & CLOCK TICK
    pygame.display.flip()  # Update the screen
    dt = clock.tick(60) / 1000.0  # Limit to 60 FPS AND calculate Delta Time!


    # CLEANUP (Runs after the while loop exits)
pygame.quit()
sys.exit()