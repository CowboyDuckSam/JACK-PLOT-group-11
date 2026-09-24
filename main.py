import sys
import pygame
from wheel import FateWheel
from settings import *
from player import Player
from save_system import LoginManager

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JACK PLOT!!!")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)


current_state = LOGIN_SCREEN
login_manager = LoginManager(font, WIDTH, HEIGHT)
char_select_step = "gender"
selected_gender = None
fate_wheel = FateWheel()



player = Player(WIDTH // 2, HEIGHT // 2)
shop_dice_result = 1
shop_message = "Welcome! 10 Tokens to roll the die."
current_floor = 1
minions_killed = 0
minions_total = 10
boss_spawned = False



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

        if current_state == LOGIN_SCREEN:
            login_manager.handle_input(event)
            if login_manager.logged_in:
                # LOAD THE SAVED TOKENS AND WHATNOT

                player.tokens = login_manager.saved_data["tokens"]
                current_floor = login_manager.saved_data["floor"]
                current_state = CHAR_SELECT

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

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                mx, my = event.pos

                if current_state == CHAR_SELECT:
                    if char_select_step == "gender":
                        if pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 40).collidepoint(mx, my):
                            selected_gender = "Male"
                            char_select_step = "skin"

                        elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 40).collidepoint(mx, my):
                            selected_gender = "Female"
                            char_select_step = "skin"

                    elif char_select_step == "skin":
                        for i in range(3):
                            box_x = (WIDTH // 2) - 150 + (i * 125)
                            box_y = (HEIGHT // 2) - 30

                            if pygame.Rect(box_x, box_y, 60, 60).collidepoint(mx, my):
                                color = SKIN_OPTIONS[selected_gender][i]
                                player.surface.fill(color)

                                # Draw eyes
                                pygame.draw.circle(player.surface, (0, 0, 0), (15, 20), 5)
                                pygame.draw.circle(player.surface, (0, 0, 0), (35, 20), 5)

                                # Gender details
                                if selected_gender == "Female":
                                    pygame.draw.circle(player.surface, (255, 105, 180), (10, 28), 4)

                                elif selected_gender == "Male":
                                    pygame.draw.rect(player.surface, (0, 0, 0), (20, 35, 10, 3))

                                current_state = MAIN_MENU



    # C. INPUT & GAME LOGIC UPDATE (Only move if in the Dungeon)
    keys = pygame.key.get_pressed()
    if current_state == DUNGEON_ROOM:

        if fate_wheel.active:
            fate_wheel.update(dt)

            if not fate_wheel.spinning and fate_wheel.result_index is not None and not fate_wheel.result_applied:
                result = fate_wheel.apply_result(player.tokens, player.deck)
                if result:
                    label, player.tokens = result  # Update the tokens

        else:
            player.update(dt, keys, dungeon_walls)

    # D. RENDERING

    # Fill the background based on the current state
    screen.fill(BG_COLORS[current_state])

    if current_state == LOGIN_SCREEN:
        login_manager.draw(screen)

    # write text specific to the current state
    if current_state == CHAR_SELECT:
        if char_select_step == "gender":
            draw_text_center("CREATE YOUR AVATAR", -80)

            # Draw Male button (blue)
            pygame.draw.rect(screen, (50, 150, 255), (WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 40))
            draw_text_center("MALE", -10)

            # Draw Female button (pink)
            pygame.draw.rect(screen, (255, 105, 180), (WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 40))
            draw_text_center("FEMALE", 40)

        elif char_select_step == "skin":
            draw_text_center(f"{selected_gender} Selected. Choose a Skin:", -120)

            skins = SKIN_OPTIONS[selected_gender]
            for i, color in enumerate(skins):
                box_x = (WIDTH // 2) - 150 + (i * 125)
                box_y = (HEIGHT // 2) - 30

                pygame.draw.rect(screen, color, (box_x, box_y, 60, 60))
                num_text = font.render(str(i + 1), True, (255, 255, 255))
                screen.blit(num_text, (box_x + 20, box_y + 80))

            draw_text_center("Click a skin to select", 150)


    if current_state == MAIN_MENU:
        draw_text_center("JACK PLOT: MAIN MENU", -20)
        draw_text_center("(Press 2 for Dungeon)", 20)

    elif current_state == DUNGEON_ROOM:
        # 1. cam offset
        cam_x = player.rect.centerx - (WIDTH // 2)
        cam_y = player.rect.centery - (HEIGHT // 2)

        # Keep camera inside the 2000x2000 map bounds
        cam_x = max(0, min(cam_x, 2000 - WIDTH))
        cam_y = max(0, min(cam_y, 2000 - HEIGHT))

        # 2.  draw the world
        floor_rect = pygame.Rect(0 - cam_x, 0 - cam_y, 2000, 2000)
        pygame.draw.rect(screen, (20, 30, 20), floor_rect)

        # Shift the wall by the camera offset
        for wall in dungeon_walls:
            offset_wall = wall.move(-cam_x, -cam_y)
            pygame.draw.rect(screen, (100, 100, 100), offset_wall)

        # Shift the player by the camera offset
        offset_player = player.rect.move(-cam_x, -cam_y)
        screen.blit(player.surface, offset_player)

        # 3. draw UI (no offsets, so it sticks to the screen)
        health_text = font.render(f"Health: {player.health}/{player.max_health}", True, (255, 100, 100))
        tokens_text = font.render(f"Token: {player.tokens}", True, (255, 215, 0))
        screen.blit(health_text, (20, 20))
        screen.blit(tokens_text, (20, 60))

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