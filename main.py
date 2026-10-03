import sys
import math
import random
import pygame
from wheel import FateWheel
from settings import *
from player import Player
from save_system import LoginManager
from environment import DungeonEnvironment
from shop import NeonShop
from audio_manager import AudioManager
from combat import SpadeProjectile, ClubSlash, LaserBeam, Token
from enemy import MeleeMinion, RangedMinion, EnemyBullet
from Boss import PiggyBankWalletBoss, OverdueBillBoss, InterestRateBoss, CommonSenseBoss

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Corrected scaling flags
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("JACK PLOT!!!")
clock = pygame.time.Clock()

# Initializing font globally to prevent per-frame recreation
font = pygame.font.SysFont("Arial", 36)

active_enemies = []
enemy_bullets = []
active_boss = None

SPAWN_CARD_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_CARD_EVENT, 500)

SPAWN_ENEMY_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 2000)

SUITS = ["SPADE", "HEART", "CLUB", "DIAMOND"]

projectiles = []
slashes = []
active_lasers = []
dropped_tokens = []

charge_timer = 0.0
CHARGE_REQ = 3.0
is_charging = False

current_state = START_MENU
is_guest = False
login_manager = LoginManager(font, WIDTH, HEIGHT)
char_select_step = "gender"
selected_gender = None
fate_wheel = FateWheel()
env = DungeonEnvironment(WIDTH, HEIGHT)
neon_shop = NeonShop(font, WIDTH, HEIGHT)
audio = AudioManager()

player = Player(WIDTH // 2, HEIGHT // 2)
shop_dice_result = 1
shop_message = "Welcome! 10 Tokens to roll the die."
current_floor = 1
minions_killed = 0
minions_total = 10
boss_spawned = False

shake_timer = 0.0
flash_timer = 0.0


def reset_game_state():
    global active_enemies, enemy_bullets, active_boss, projectiles, slashes, active_lasers, dropped_tokens
    global current_floor, minions_killed, minions_total, boss_spawned
    active_enemies.clear()
    enemy_bullets.clear()
    projectiles.clear()
    slashes.clear()
    active_lasers.clear()
    dropped_tokens.clear()
    active_boss = None
    minions_killed = 0
    boss_spawned = False
    minions_total = current_floor * 10


def draw_text_center(text, y_offset=0):
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)


dt = 0
running = True
while running:
    if current_state in (START_MENU, LOGIN_SCREEN, CHAR_SELECT, LEVEL_SELECT):
        audio.play_bgm("menu_theme")
    elif current_state == DUNGEON_ROOM:
        audio.play_bgm("dark_dungeon")
    elif current_state == SHOP_ROOM:
        audio.play_bgm("neon_chill")
    elif current_state == GAMEOVER_SCREEN:
        audio.play_bgm("game_over_sad")
    elif current_state == VICTORY_SCREEN:
        audio.play_bgm("victory_fanfare")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == LOGIN_SCREEN:
            login_manager.handle_input(event)
            if login_manager.logged_in:
                player.tokens = login_manager.saved_data.get("tokens", 0)
                current_floor = login_manager.saved_data.get("floor", 1)
                player.max_health = login_manager.saved_data.get("max_health", 100)
                player.health = login_manager.saved_data.get("health", 100)
                current_state = CHAR_SELECT

        if event.type == SPAWN_CARD_EVENT and current_state == DUNGEON_ROOM:
            if len(player.deck) < getattr(player, "MAX_HAND_SIZE", 5):
                player.deck.append(random.choice(SUITS))

        if event.type == SPAWN_ENEMY_EVENT and current_state == DUNGEON_ROOM:
            if not boss_spawned and len(active_enemies) < 5 + current_floor:
                offset_x = random.choice([-350, -250, 250, 350])
                offset_y = random.choice([-350, -250, 250, 350])

                spawn_x = max(100, min(player.rect.centerx + offset_x, 1900))
                spawn_y = max(100, min(player.rect.centery + offset_y, 1900))

                if random.random() < 0.5:
                    active_enemies.append(MeleeMinion(spawn_x, spawn_y, floor=current_floor))
                else:
                    active_enemies.append(RangedMinion(spawn_x, spawn_y, floor=current_floor))

        if current_state == DUNGEON_ROOM and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if not fate_wheel.active and len(active_lasers) == 0 and charge_timer < CHARGE_REQ:
                if len(player.deck) > 0:
                    current_card = player.deck.pop(0)
                    if current_card == "SPADE":
                        projectiles.append(SpadeProjectile(player.rect.centerx, player.rect.centery, player.angle))
                        audio.play_sfx("spade")
                    elif current_card == "HEART":
                        player.use_heart_shield()
                        audio.play_sfx("heart")
                    elif current_card == "CLUB":
                        slashes.append(ClubSlash(player.rect.centerx, player.rect.centery, player.angle))
                        audio.play_sfx("club")
                    elif current_card == "DIAMOND":
                        player.use_diamond_dash(pygame.key.get_pressed())
                        audio.play_sfx("diamond")

                    if active_boss and isinstance(active_boss, CommonSenseBoss) and active_boss.is_alive:
                        active_boss.on_player_attack()

            is_charging = False
            charge_timer = 0.0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos

                if current_state == START_MENU:
                    if pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 50).collidepoint(mx, my):
                        audio.play_sfx("click")
                        is_guest = True
                        current_state = CHAR_SELECT
                    elif pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50).collidepoint(mx, my):
                        audio.play_sfx("click")
                        is_guest = False
                        current_state = LOGIN_SCREEN

                elif current_state == LEVEL_SELECT:
                    for i in range(4):
                        floor_num = i + 1
                        btn = pygame.Rect(WIDTH // 2 - 250 + (i * 130), HEIGHT // 2 - 40, 100, 80)
                        if btn.collidepoint(mx, my) and floor_num == current_floor:
                            audio.play_sfx("enter_dungeon")
                            reset_game_state()
                            current_state = DUNGEON_ROOM

                elif current_state == CHAR_SELECT:
                    if char_select_step == "gender":
                        if pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 40).collidepoint(mx, my):
                            audio.play_sfx("click")
                            selected_gender = "Male"
                            char_select_step = "skin"
                        elif pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 40).collidepoint(mx, my):
                            audio.play_sfx("click")
                            selected_gender = "Female"
                            char_select_step = "skin"

                    elif char_select_step == "skin":
                        for i in range(3):
                            box_x = (WIDTH // 2) - 150 + (i * 125)
                            box_y = (HEIGHT // 2) - 30
                            if pygame.Rect(box_x, box_y, 60, 60).collidepoint(mx, my):
                                audio.play_sfx("click")
                                color = SKIN_OPTIONS[selected_gender][i]
                                player.surface.fill(color)

                                pygame.draw.circle(player.surface, (0, 0, 0), (15, 20), 5)
                                pygame.draw.circle(player.surface, (0, 0, 0), (35, 20), 5)

                                if selected_gender == "Female":
                                    pygame.draw.line(player.surface, (0, 0, 0), (10, 18), (5, 12), 2)
                                    pygame.draw.line(player.surface, (0, 0, 0), (40, 18), (45, 12), 2)
                                    pygame.draw.circle(player.surface, (255, 105, 180), (10, 28), 4)
                                    pygame.draw.circle(player.surface, (255, 105, 180), (40, 28), 4)
                                    pygame.draw.ellipse(player.surface, (200, 20, 50), (20, 32, 10, 6))
                                    pygame.draw.polygon(player.surface, (220, 20, 20), [(35, 8), (45, 0), (45, 16)])
                                    pygame.draw.polygon(player.surface, (220, 20, 20), [(35, 8), (25, 0), (25, 16)])
                                    pygame.draw.circle(player.surface, (180, 0, 0), (35, 8), 4)

                                elif selected_gender == "Male":
                                    pygame.draw.line(player.surface, (0, 0, 0), (8, 12), (18, 16), 3)
                                    pygame.draw.line(player.surface, (0, 0, 0), (42, 12), (32, 16), 3)
                                    pygame.draw.rect(player.surface, (60, 40, 20), (5, 33, 40, 15))
                                    pygame.draw.rect(player.surface, (60, 40, 20), (15, 28, 20, 4))

                                current_state = LEVEL_SELECT

                elif current_state == DUNGEON_ROOM:
                    if fate_wheel.active:
                        audio.play_sfx("click")
                        fate_wheel.handle_click(mx, my)

                elif current_state == SHOP_ROOM:
                    action = neon_shop.handle_click(mx, my, player)
                    if action == "NEXT_FLOOR":
                        audio.play_sfx("enter_dungeon")
                        if not is_guest:
                            login_manager.save_progress(player, current_floor)
                        reset_game_state()
                        current_state = LEVEL_SELECT
                    elif action:
                        audio.play_sfx("buy_item")

                elif current_state in (GAMEOVER_SCREEN, VICTORY_SCREEN):
                    audio.play_sfx("click_restart")

                    if not is_guest and current_state == GAMEOVER_SCREEN:
                        login_manager.save_progress(player, current_floor, is_death=True)

                    player.health = 100
                    player.max_health = 100
                    player.tokens = 0
                    current_floor = 1
                    player.deck.clear()
                    reset_game_state()

                    current_state = LEVEL_SELECT

    if shake_timer > 0: shake_timer -= dt
    if flash_timer > 0: flash_timer -= dt

    keys = pygame.key.get_pressed()
    if current_state == DUNGEON_ROOM:
        if player.health <= 0:
            current_state = GAMEOVER_SCREEN

        cam_x = max(0, min(player.rect.centerx - (WIDTH // 2), 2000 - WIDTH))
        cam_y = max(0, min(player.rect.centery - (HEIGHT // 2), 2000 - HEIGHT))

        if fate_wheel.active:
            fate_wheel.update(dt)
            if not fate_wheel.spinning and fate_wheel.result_index is not None and not fate_wheel.result_applied:
                fate_wheel.apply_result(player)
        else:
            mouse_buttons = pygame.mouse.get_pressed()

            if mouse_buttons[0] and len(active_lasers) == 0:
                if len(player.deck) >= 4:
                    is_charging = True
                    charge_timer += dt
                    if charge_timer >= CHARGE_REQ:
                        for _ in range(4): player.deck.pop(0)
                        active_lasers.append(LaserBeam(player))
                        audio.play_sfx("laser")
                        is_charging = False
                        charge_timer = 0
            else:
                is_charging = False
                charge_timer = 0

            player.update(dt, keys, dungeon_walls, pygame.mouse.get_pos(), cam_x, cam_y)

            for laser in active_lasers[:]:
                laser.update()
                if laser.lifetime <= 0: active_lasers.remove(laser)

            for proj in projectiles[:]:
                proj.update()
                if proj.lifetime <= 0: projectiles.remove(proj)

                # Check projectile wall collisions
                proj_rect = pygame.Rect(proj.x - 8, proj.y - 8, 16, 16)
                if any(proj_rect.colliderect(wall) for wall in dungeon_walls):
                    if proj in projectiles: projectiles.remove(proj)
                    continue

            for slash in slashes[:]:
                slash.update()
                if slash.lifetime <= 0: slashes.remove(slash)

            for t in dropped_tokens[:]:
                t.update(player.rect)
                if player.rect.colliderect(t.rect):
                    player.tokens += 1
                    dropped_tokens.remove(t)

            for enemy in active_enemies[:]:
                enemy.update(player.rect, enemy_bullets, dungeon_walls)
                if player.rect.colliderect(enemy.rect):
                    if player.take_damage(getattr(enemy, 'damage', 10)):
                        audio.play_sfx("jack_hurt")
                        shake_timer = 0.2
                        flash_timer = 0.1

            for eb in enemy_bullets[:]:
                eb.update()
                if eb.rect.colliderect(player.rect):
                    if player.take_damage(getattr(eb, 'damage', 5)):
                        audio.play_sfx("jack_hurt")
                        shake_timer = 0.2
                        flash_timer = 0.1
                    enemy_bullets.remove(eb)
                elif getattr(eb, 'lifetime', 1) <= 0:
                    enemy_bullets.remove(eb)
                elif any(eb.rect.colliderect(wall) for wall in dungeon_walls):
                    enemy_bullets.remove(eb)

            for proj in projectiles[:]:
                proj_rect = pygame.Rect(proj.x - 8, proj.y - 8, 16, 16)
                for enemy in active_enemies[:]:
                    if proj_rect.colliderect(enemy.rect) and enemy not in proj.hit_targets:
                        proj.hit_targets.add(enemy)
                        enemy.take_damage(20)
                        if proj in projectiles: projectiles.remove(proj)
                        audio.play_sfx("enemy_hit")
                        if enemy.hp <= 0:
                            if enemy in active_enemies: active_enemies.remove(enemy)
                            minions_killed += 1
                            player.tokens += 2
                            dropped_tokens.append(Token(enemy.rect.centerx, enemy.rect.centery))

                            if minions_killed % 5 == 0 and not fate_wheel.active and not boss_spawned:
                                audio.play_sfx("wheel_open")
                                fate_wheel.open()

                            if minions_killed >= minions_total and not boss_spawned:
                                boss_spawned = True
                                audio.play_sfx("boss_spawn")
                        break

            for slash in slashes[:]:
                slash_rect = pygame.Rect(slash.x - slash.reach, slash.y - slash.reach, slash.reach * 2, slash.reach * 2)
                for enemy in active_enemies[:]:
                    if slash_rect.colliderect(enemy.rect) and enemy not in slash.hit_targets:
                        slash.hit_targets.add(enemy)
                        enemy.take_damage(15)
                        audio.play_sfx("enemy_hit")
                        if enemy.hp <= 0:
                            if enemy in active_enemies: active_enemies.remove(enemy)
                            minions_killed += 1
                            player.tokens += 2
                            dropped_tokens.append(Token(enemy.rect.centerx, enemy.rect.centery))

                            # Fate Wheel triggers every 5 kills
                            if minions_killed % 5 == 0 and not fate_wheel.active and not boss_spawned:
                                audio.play_sfx("wheel_open")
                                fate_wheel.open()

                            if minions_killed >= minions_total and not boss_spawned:
                                boss_spawned = True
                                audio.play_sfx("boss_spawn")

            # Check continuous laser line collisions
            for laser in active_lasers[:]:
                rad = math.radians(player.angle)
                start_pos = player.rect.center
                end_x = start_pos[0] + math.cos(rad) * laser.beam_length
                end_y = start_pos[1] + math.sin(rad) * laser.beam_length

                for enemy in active_enemies[:]:
                    if enemy.rect.clipline(start_pos, (end_x, end_y)):
                        enemy.take_damage(1)
                        if enemy.hp <= 0:
                            if enemy in active_enemies: active_enemies.remove(enemy)
                            minions_killed += 1
                            player.tokens += 2
                            dropped_tokens.append(Token(enemy.rect.centerx, enemy.rect.centery))

                            # Fate Wheel triggers every 5 kills
                            if minions_killed % 5 == 0 and not fate_wheel.active and not boss_spawned:
                                audio.play_sfx("wheel_open")
                                fate_wheel.open()

                            if minions_killed >= minions_total and not boss_spawned:
                                boss_spawned = True
                                audio.play_sfx("boss_spawn")


            if boss_spawned and not active_boss:
                active_enemies.clear()
                spawn_bx = player.rect.centerx + 300
                spawn_by = player.rect.centery
                if current_floor == 1:
                    active_boss = PiggyBankWalletBoss(WIDTH // 2, HEIGHT // 2)
                elif current_floor == 2:
                    active_boss = OverdueBillBoss(WIDTH // 2, HEIGHT // 2)
                elif current_floor == 3:
                    active_boss = InterestRateBoss(WIDTH // 2, HEIGHT // 2)
                elif current_floor == 4:
                    active_boss = CommonSenseBoss(WIDTH // 2, HEIGHT // 2)

            if active_boss and active_boss.is_alive:
                active_boss.update(player.rect)

                for b_bullet in list(active_boss.bullets):
                    if b_bullet.rect.colliderect(player.rect):
                        if player.take_damage(getattr(b_bullet, 'damage', 10)):
                            audio.play_sfx("jack_hurt")
                            shake_timer = 0.2
                            flash_timer = 0.1
                        b_bullet.kill()

                for proj in projectiles[:]:
                    proj_rect = pygame.Rect(proj.x - 8, proj.y - 8, 16, 16)
                    if isinstance(active_boss, PiggyBankWalletBoss):
                        if active_boss.piggy_alive and proj_rect.colliderect(active_boss.piggy_rect):
                            active_boss.take_damage_piggy(20)
                            if proj in projectiles: projectiles.remove(proj)
                            audio.play_sfx("enemy_hit")
                        elif active_boss.wallet_alive and proj_rect.colliderect(active_boss.wallet_rect):
                            active_boss.take_damage_wallet(20)
                            if proj in projectiles: projectiles.remove(proj)
                            audio.play_sfx("enemy_hit")
                    elif proj_rect.colliderect(active_boss.rect):
                        active_boss.take_damage(20)
                        if proj in projectiles: projectiles.remove(proj)
                        audio.play_sfx("enemy_hit")

                for slash in slashes[:]:
                    slash_rect = pygame.Rect(slash.x - slash.reach, slash.y - slash.reach, slash.reach * 2,
                                             slash.reach * 2)
                    if isinstance(active_boss, PiggyBankWalletBoss):
                        if active_boss.piggy_alive and slash_rect.colliderect(
                                active_boss.piggy_rect) and active_boss not in slash.hit_targets:
                            slash.hit_targets.add(active_boss)
                            active_boss.take_damage_piggy(15)
                            audio.play_sfx("enemy_hit")
                        elif active_boss.wallet_alive and slash_rect.colliderect(
                                active_boss.wallet_rect) and active_boss not in slash.hit_targets:
                            slash.hit_targets.add(active_boss)
                            active_boss.take_damage_wallet(15)
                            audio.play_sfx("enemy_hit")
                    elif slash_rect.colliderect(active_boss.rect) and active_boss not in slash.hit_targets:
                        slash.hit_targets.add(active_boss)
                        active_boss.take_damage(15)
                        audio.play_sfx("enemy_hit")

                for laser in active_lasers[:]:
                    rad = math.radians(player.angle)
                    start_pos = player.rect.center
                    end_x = start_pos[0] + math.cos(rad) * laser.beam_length
                    end_y = start_pos[1] + math.sin(rad) * laser.beam_length

                    if isinstance(active_boss, PiggyBankWalletBoss):
                        if active_boss.piggy_alive and active_boss.piggy_rect.clipline(start_pos, (end_x, end_y)):
                            active_boss.take_damage_piggy(1)
                        if active_boss.wallet_alive and active_boss.wallet_rect.clipline(start_pos, (end_x, end_y)):
                            active_boss.take_damage_wallet(1)
                    elif active_boss.rect.clipline(start_pos, (end_x, end_y)):
                        active_boss.take_damage(1)

                if not active_boss.is_alive:
                    player.tokens += 75
                    boss_spawned = False
                    active_boss = None
                    minions_killed = 0
                    current_floor += 1
                    audio.play_sfx("boss_dead")
                    if current_floor > 4:
                        current_state = VICTORY_SCREEN
                    else:
                        current_state = SHOP_ROOM

    screen.fill(BG_COLORS.get(current_state, (0, 0, 0)))

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

    elif current_state == LEVEL_SELECT:
        draw_text_center("SELECT FLOOR", -120)
        for i in range(4):
            floor_num = i + 1
            btn = pygame.Rect(WIDTH // 2 - 250 + (i * 130), HEIGHT // 2 - 40, 100, 80)
            color = (50, 200, 50) if floor_num < current_floor else (
                (255, 200, 50) if floor_num == current_floor else (200, 50, 50))
            pygame.draw.rect(screen, color, btn, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), btn, 2, border_radius=8)
            screen.blit(font.render(f"F{floor_num}", True, (255, 255, 255)), (btn.x + 30, btn.y + 20))

    elif current_state in (DUNGEON_ROOM, GAMEOVER_SCREEN, VICTORY_SCREEN):
        cam_x = max(0, min(player.rect.centerx - (WIDTH // 2), 2000 - WIDTH))
        cam_y = max(0, min(player.rect.centery - (HEIGHT // 2), 2000 - HEIGHT))

        if shake_timer > 0:
            cam_x += random.randint(-8, 8)
            cam_y += random.randint(-8, 8)

        env.draw_background(screen, current_floor, cam_x, cam_y)

        for wall in dungeon_walls:
            offset_wall = wall.move(-cam_x, -cam_y)
            pygame.draw.rect(screen, (100, 100, 100), offset_wall)

        for t in dropped_tokens: t.draw(screen, cam_x, cam_y)
        for proj in projectiles: proj.draw(screen, cam_x, cam_y)
        for slash in slashes: slash.draw(screen, cam_x, cam_y)
        for laser in active_lasers: laser.draw(screen, cam_x, cam_y)

        for eb in enemy_bullets: eb.draw(screen, cam_x, cam_y)
        for enemy in active_enemies: enemy.draw(screen, cam_x, cam_y)

        if active_boss and active_boss.is_alive:
            active_boss.draw(screen, cam_x, cam_y)
            active_boss.draw_healthbar(screen, cam_x, cam_y)

        offset_player = player.rect.move(-cam_x, -cam_y)
        screen.blit(player.surface, offset_player)
        if hasattr(player, 'draw_extras'):
            player.draw_extras(screen, offset_player)

        if is_charging and charge_timer > 0:
            charge_ratio = min(charge_timer / CHARGE_REQ, 1.0)
            pygame.draw.circle(screen, (80, 80, 80), offset_player.center, 40, width=2)
            fill_radius = int(40 * charge_ratio)
            if fill_radius > 0:
                pygame.draw.circle(screen, (0, 255, 255), offset_player.center, fill_radius, width=2)

        if flash_timer > 0:
            flash_surf = pygame.Surface(player.rect.size, pygame.SRCALPHA)
            flash_surf.fill((255, 0, 0, 150))
            screen.blit(flash_surf, offset_player)

        env.draw_custom_ui(screen, current_floor, font, player.health, player.max_health, player.tokens, minions_killed,
                           minions_total, boss_spawned, player)

        if current_state == DUNGEON_ROOM:
            if fate_wheel.active:
                fate_wheel.draw(screen, font)
        elif current_state == GAMEOVER_SCREEN:
            env.draw_end_screen(screen, font, is_victory=False)
        elif current_state == VICTORY_SCREEN:
            env.draw_end_screen(screen, font, is_victory=True)

    elif current_state == SHOP_ROOM:
        neon_shop.draw(screen, player)

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0

pygame.quit()
sys.exit()