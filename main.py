import sys
import pygame
from wheel import FateWheel
from settings import *
from player import Player
from save_system import LoginManager
from environment import DungeonEnvironment
from shop import NeonShop

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JACK PLOT!!!")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)

# starting right at the boot menu
current_state = START_MENU
is_guest = False
login_manager = LoginManager(font, WIDTH, HEIGHT)
char_select_step = "gender"
selected_gender = None
fate_wheel = FateWheel()
env = DungeonEnvironment(WIDTH, HEIGHT)
neon_shop = NeonShop(font, WIDTH, HEIGHT)

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
    # event queue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == LOGIN_SCREEN:
            login_manager.handle_input(event)
            if login_manager.logged_in:
                # safe load: grabs saved health or defaults to 100 for older saves
                player.tokens = login_manager.saved_data.get("tokens", 0)
                current_floor = login_manager.saved_data.get("floor", 1)
                player.max_health = login_manager.saved_data.get("max_health", 100)
                player.health = login_manager.saved_data.get("health", 100)
                current_state = CHAR_SELECT

        # dev test keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_state = LEVEL_SELECT
            elif event.key == pygame.K_2:
                current_state = DUNGEON_ROOM
            elif event.key == pygame.K_3:
                current_state = SHOP_ROOM
            elif event.key == pygame.K_4:
                current_state = GAMEOVER_SCREEN
            elif event.key == pygame.K_5:
                current_state = VICTORY_SCREEN

            # test key to take damage and test the failure screen
            elif event.key == pygame.K_h and current_state == DUNGEON_ROOM:
                player.health -= 25

            # fate wheel & cheat keys
            if current_state == DUNGEON_ROOM:
                if event.key == pygame.K_r and not fate_wheel.active:
                    fate_wheel.open()

                # simulate killing a minion
                elif event.key == pygame.K_k and not boss_spawned:
                    minions_killed += 1
                    player.tokens += 5

                    # open wheel every 5 kills
                    if minions_killed % 5 == 0 and not fate_wheel.active:
                        fate_wheel.open()

                    if minions_killed >= minions_total:
                        boss_spawned = True

                # simulate killing the boss
                elif event.key == pygame.K_b and boss_spawned:
                    player.tokens += 75
                    boss_spawned = False
                    minions_killed = 0
                    current_floor += 1
                    minions_total = current_floor * 10

                    # check if they beat the whole game
                    if current_floor > 4:
                        current_state = VICTORY_SCREEN
                    else:
                        # checkpoint 1: beating the boss (only save if not a guest)
                        if not is_guest:
                            login_manager.save_progress(player, current_floor)
                        current_state = SHOP_ROOM

        # mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos

                # boot screen clicks
                if current_state == START_MENU:
                    if pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 50).collidepoint(mx, my):
                        is_guest = True
                        current_state = CHAR_SELECT
                    elif pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50).collidepoint(mx, my):
                        is_guest = False
                        current_state = LOGIN_SCREEN

                # picking a floor on the map
                elif current_state == LEVEL_SELECT:
                    for i in range(4):
                        floor_num = i + 1
                        btn = pygame.Rect(WIDTH // 2 - 250 + (i * 130), HEIGHT // 2 - 40, 100, 80)

                        # only let them click the floor they are currently on
                        if btn.collidepoint(mx, my) and floor_num == current_floor:
                            current_state = DUNGEON_ROOM

                elif current_state == CHAR_SELECT:
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

                                # draw base eyes
                                pygame.draw.circle(player.surface, (0, 0, 0), (15, 20), 5)
                                pygame.draw.circle(player.surface, (0, 0, 0), (35, 20), 5)

                                # gender details
                                if selected_gender == "Female":
                                    # cute eyelashes
                                    pygame.draw.line(player.surface, (0, 0, 0), (10, 18), (5, 12), 2)
                                    pygame.draw.line(player.surface, (0, 0, 0), (40, 18), (45, 12), 2)

                                    # pink blush
                                    pygame.draw.circle(player.surface, (255, 105, 180), (10, 28), 4)
                                    pygame.draw.circle(player.surface, (255, 105, 180), (40, 28), 4)

                                    # red lips
                                    pygame.draw.ellipse(player.surface, (200, 20, 50), (20, 32, 10, 6))

                                    # little red bow in the hair (top right)
                                    pygame.draw.polygon(player.surface, (220, 20, 20), [(35, 8), (45, 0), (45, 16)])
                                    pygame.draw.polygon(player.surface, (220, 20, 20), [(35, 8), (25, 0), (25, 16)])
                                    pygame.draw.circle(player.surface, (180, 0, 0), (35, 8), 4)

                                elif selected_gender == "Male":
                                    # thick, determined eyebrows
                                    pygame.draw.line(player.surface, (0, 0, 0), (8, 12), (18, 16), 3)
                                    pygame.draw.line(player.surface, (0, 0, 0), (42, 12), (32, 16), 3)

                                    # rugged brown beard covering the bottom
                                    pygame.draw.rect(player.surface, (60, 40, 20), (5, 33, 40, 15))

                                    # little mustache
                                    pygame.draw.rect(player.surface, (60, 40, 20), (15, 28, 20, 4))

                                # straight to the floor map
                                current_state = LEVEL_SELECT

                # clicking the wheel in the dungeon
                elif current_state == DUNGEON_ROOM:
                    if fate_wheel.active:
                        fate_wheel.handle_click(mx, my)

                elif current_state == SHOP_ROOM:
                    action = neon_shop.handle_click(mx, my, player)
                    if action == "NEXT_FLOOR":
                        # checkpoint 2: leaving the shop (only save if not a guest)
                        if not is_guest:
                            login_manager.save_progress(player, current_floor)
                        current_state = LEVEL_SELECT

    # update loop
    keys = pygame.key.get_pressed()
    if current_state == DUNGEON_ROOM:
        # checking if dead
        if player.health <= 0:
            current_state = GAMEOVER_SCREEN

        if fate_wheel.active:
            fate_wheel.update(dt)
            if not fate_wheel.spinning and fate_wheel.result_index is not None and not fate_wheel.result_applied:
                result = fate_wheel.apply_result(player.tokens, player.deck)
                if result:
                    label, player.tokens = result
        else:
            player.update(dt, keys, dungeon_walls)

    # rendering
    # fallback background fill, though most screens draw their own stuff now
    screen.fill(BG_COLORS.get(current_state, (0, 0, 0)))

    # drawing the boot menu
    if current_state == START_MENU:
        draw_text_center("JACK PLOT", -120)

        guest_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 50)
        pygame.draw.rect(screen, (80, 80, 80), guest_btn, border_radius=10)
        screen.blit(font.render("Play as Guest", True, (255, 255, 255)), (guest_btn.x + 60, guest_btn.y + 5))

        log_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50)
        pygame.draw.rect(screen, (50, 100, 200), log_btn, border_radius=10)
        screen.blit(font.render("Login / Create", True, (255, 255, 255)), (log_btn.x + 55, log_btn.y + 5))

    elif current_state == LOGIN_SCREEN:
        login_manager.draw(screen)

    elif current_state == CHAR_SELECT:
        if char_select_step == "gender":
            draw_text_center("CREATE YOUR AVATAR", -80)
            pygame.draw.rect(screen, (50, 150, 255), (WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 40))
            draw_text_center("MALE", -10)
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

    # drawing the floor map
    elif current_state == LEVEL_SELECT:
        draw_text_center("SELECT FLOOR", -120)

        for i in range(4):
            floor_num = i + 1
            btn = pygame.Rect(WIDTH // 2 - 250 + (i * 130), HEIGHT // 2 - 40, 100, 80)

            # colors based on progress (green = done, yellow = current, red = locked)
            if floor_num < current_floor:
                color = (50, 200, 50)
            elif floor_num == current_floor:
                color = (255, 200, 50)
            else:
                color = (200, 50, 50)

            pygame.draw.rect(screen, color, btn, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), btn, 2, border_radius=8)
            screen.blit(font.render(f"F{floor_num}", True, (255, 255, 255)), (btn.x + 30, btn.y + 20))

    elif current_state == DUNGEON_ROOM:
        cam_x = max(0, min(player.rect.centerx - (WIDTH // 2), 2000 - WIDTH))
        cam_y = max(0, min(player.rect.centery - (HEIGHT // 2), 2000 - HEIGHT))

        env.draw_background(screen, current_floor, cam_x, cam_y)

        for wall in dungeon_walls:
            offset_wall = wall.move(-cam_x, -cam_y)
            pygame.draw.rect(screen, (100, 100, 100), offset_wall)

        offset_player = player.rect.move(-cam_x, -cam_y)
        screen.blit(player.surface, offset_player)

        env.draw_custom_ui(screen, current_floor, font, player.health, player.max_health, player.tokens, minions_killed,
                           minions_total, boss_spawned)

        fate_wheel.draw(screen, font)

    elif current_state == SHOP_ROOM:
        neon_shop.draw(screen, player)

    elif current_state == GAMEOVER_SCREEN:
        draw_text_center("Dungeon failed", 0)

    elif current_state == VICTORY_SCREEN:
        draw_text_center("YOU WIN!", 0)

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

pygame.quit()
sys.exit()