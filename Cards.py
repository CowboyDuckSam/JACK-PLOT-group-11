import sys
import math
import random
import os
import pygame

# Import abilities, enemies, and bosses
from combat import SpadeProjectile, ClubSlash, LaserBeam, Token
from enemy import MeleeMinion, RangedMinion
from Boss import PiggyBankWalletBoss, OverdueBillBoss, InterestRateBoss, CommonSenseBoss

# 1. INITIALIZATION & SETUP
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JACK PLOT")
clock = pygame.time.Clock()

# --- COLOR PALETTE ---
COLOR_BG = (20, 15, 30)
COLOR_PLAYER = (240, 240, 240)
COLOR_DIAMOND = (255, 60, 60)
COLOR_HEART = (255, 100, 150)
COLOR_SPADE = (180, 70, 255)
COLOR_CLUB = (50, 220, 120)
COLOR_LASER = (0, 255, 255)
COLOR_TOKEN_OUTER = (140, 20, 220)
COLOR_TOKEN_INNER = (255, 215, 0)

SUIT_COLORS = {
    "SPADE": COLOR_SPADE,
    "HEART": COLOR_HEART,
    "CLUB": COLOR_CLUB,
    "DIAMOND": COLOR_DIAMOND
}

# --- AUDIO ASSETS ---
ASSET_DIR = os.path.join(os.path.dirname(__file__), "sound_assets")

try:
    SOUND_SPADE = pygame.mixer.Sound(os.path.join(ASSET_DIR, "spade.wav"))
    SOUND_CLUB = pygame.mixer.Sound(os.path.join(ASSET_DIR, "club.wav"))
    SOUND_HEART = pygame.mixer.Sound(os.path.join(ASSET_DIR, "heart.wav"))
    SOUND_DIAMOND = pygame.mixer.Sound(os.path.join(ASSET_DIR, "diamond.wav"))
    SOUND_LASER = pygame.mixer.Sound(os.path.join(ASSET_DIR, "laser.wav"))
except pygame.error:
    dummy_sound = pygame.mixer.Sound(buffer=bytes([0]*100))
    SOUND_SPADE = SOUND_CLUB = SOUND_HEART = SOUND_DIAMOND = SOUND_LASER = dummy_sound

SPAWN_CARD_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_CARD_EVENT, 500)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.base_speed = 4
        self.angle = 0.0
        self.shield_hp = 0
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_dir = pygame.math.Vector2(0, 0)
        self.dash_speed = 18

    def update(self, keys, mouse_pos):
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        self.angle = math.degrees(math.atan2(dy, dx))

        if self.is_dashing:
            self.rect.x += self.dash_dir.x * self.dash_speed
            self.rect.y += self.dash_dir.y * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            move_vec = pygame.math.Vector2(0, 0)
            if keys[pygame.K_a]: move_vec.x -= 1
            if keys[pygame.K_d]: move_vec.x += 1
            if keys[pygame.K_w]: move_vec.y -= 1
            if keys[pygame.K_s]: move_vec.y += 1

            if move_vec.length_squared() > 0:
                move_vec = move_vec.normalize()
                self.rect.x += move_vec.x * self.base_speed
                self.rect.y += move_vec.y * self.base_speed

        self.rect.clamp_ip(screen.get_rect())

    def use_diamond_dash(self, keys):
        if self.is_dashing: return
        move_vec = pygame.math.Vector2(0, 0)
        if keys[pygame.K_a]: move_vec.x -= 1
        if keys[pygame.K_d]: move_vec.x += 1
        if keys[pygame.K_w]: move_vec.y -= 1
        if keys[pygame.K_s]: move_vec.y += 1

        if move_vec.length_squared() > 0:
            self.dash_dir = move_vec.normalize()
        else:
            rad = math.radians(self.angle)
            self.dash_dir = pygame.math.Vector2(math.cos(rad), math.sin(rad))

        self.is_dashing = True
        self.dash_timer = 10

    def use_heart_shield(self):
        self.shield_hp = 20

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_PLAYER, self.rect, border_radius=4)
        rad = math.radians(self.angle)
        end_x = self.rect.centerx + math.cos(rad) * 24
        end_y = self.rect.centery + math.sin(rad) * 24
        pygame.draw.line(surface, (0, 0, 0), self.rect.center, (end_x, end_y), 4)

        if self.shield_hp > 0:
            pygame.draw.circle(surface, COLOR_HEART, self.rect.center, 28, width=3)


# Setup Game Entities
player = Player(WIDTH // 2, HEIGHT // 2)
projectiles = []
slashes = []
active_lasers = []
minions = [MeleeMinion(200, 150), RangedMinion(700, 150)]
current_boss = PiggyBankWalletBoss(WIDTH // 2, 100)  # Level 1 Boss (200 HP)

tokens = []
player_tokens = 0

card_hand = []
MAX_HAND_SIZE = 5
SUITS = ["SPADE", "HEART", "CLUB", "DIAMOND"]

charge_timer = 0
CHARGE_REQ = 180
is_charging = False

font = pygame.font.SysFont("Arial", 14, bold=True)

# MAIN GAME LOOP
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == SPAWN_CARD_EVENT and len(card_hand) < MAX_HAND_SIZE:
            card_hand.append(random.choice(SUITS))

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            for _ in range(5):
                tokens.append(Token(player.rect.centerx, player.rect.centery))

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if len(active_lasers) == 0 and is_charging and charge_timer < CHARGE_REQ:
                if len(card_hand) > 0:
                    current_card = card_hand.pop(0)

                    if current_card == "SPADE":
                        projectiles.append(SpadeProjectile(player.rect.centerx, player.rect.centery, player.angle))
                        SOUND_SPADE.play()
                    elif current_card == "HEART":
                        player.use_heart_shield()
                        SOUND_HEART.play()
                    elif current_card == "CLUB":
                        slashes.append(ClubSlash(player.rect.centerx, player.rect.centery, player.angle))
                        SOUND_CLUB.play()
                    elif current_card == "DIAMOND":
                        player.use_diamond_dash(keys)
                        SOUND_DIAMOND.play()

                    # Trigger CommonSenseBoss copied attack
                    if isinstance(current_boss, CommonSenseBoss) and current_boss.is_alive:
                        current_boss.on_player_attack()

            is_charging = False
            charge_timer = 0

    # Charge Laser
    if mouse_buttons[0] and len(active_lasers) == 0:
        if len(card_hand) >= 4:
            is_charging = True
            charge_timer += 1
            if charge_timer >= CHARGE_REQ:
                for _ in range(4): card_hand.pop(0)
                active_lasers.append(LaserBeam(player))
                SOUND_LASER.play()
                is_charging = False
                charge_timer = 0
        else:
            is_charging = False
            charge_timer = 0
    else:
        if len(active_lasers) > 0:
            is_charging = False
            charge_timer = 0

    # --- UPDATES & COLLISION LINKING ---
    player.update(keys, mouse_pos)

    # 1. SPADE DAMAGE COLLISION (20 DMG)
    for proj in projectiles[:]:
        proj.update()
        if proj.lifetime <= 0 or not screen.get_rect().collidepoint(proj.x, proj.y):
            if proj in projectiles: projectiles.remove(proj)
            continue

        proj_rect = pygame.Rect(proj.x - 8, proj.y - 8, 16, 16)

        # Damage Minions
        for minion in minions[:]:
            if proj_rect.colliderect(minion.rect):
                minion.take_damage(20)  # Spade = 20 DMG
                if minion.hp <= 0:
                    for _ in range(5): tokens.append(Token(minion.rect.centerx, minion.rect.centery))
                    minions.remove(minion)
                if proj in projectiles: projectiles.remove(proj)
                break

        # Damage Bosses
        if current_boss and current_boss.is_alive and proj in projectiles:
            if isinstance(current_boss, PiggyBankWalletBoss):
                if current_boss.piggy_alive and proj_rect.colliderect(current_boss.piggy_rect):
                    current_boss.take_damage_piggy(20)
                    projectiles.remove(proj)
                elif current_boss.wallet_alive and proj_rect.colliderect(current_boss.wallet_rect):
                    current_boss.take_damage_wallet(20)
                    projectiles.remove(proj)
            elif proj_rect.colliderect(current_boss.rect):
                current_boss.take_damage(20)
                projectiles.remove(proj)

    # 2. CLUB SLASH DAMAGE COLLISION (15 DMG)
    for slash in slashes[:]:
        slash.update()
        if slash.lifetime <= 0:
            slashes.remove(slash)
            continue

        slash_rect = pygame.Rect(slash.x - slash.reach, slash.y - slash.reach, slash.reach * 2, slash.reach * 2)

        for minion in minions[:]:
            if slash_rect.colliderect(minion.rect):
                minion.take_damage(15)  # Club = 15 DMG
                if minion.hp <= 0:
                    for _ in range(5): tokens.append(Token(minion.rect.centerx, minion.rect.centery))
                    minions.remove(minion)

        if current_boss and current_boss.is_alive:
            if isinstance(current_boss, PiggyBankWalletBoss):
                if current_boss.piggy_alive and slash_rect.colliderect(current_boss.piggy_rect):
                    current_boss.take_damage_piggy(15)
                if current_boss.wallet_alive and slash_rect.colliderect(current_boss.wallet_rect):
                    current_boss.take_damage_wallet(15)
            elif slash_rect.colliderect(current_boss.rect):
                current_boss.take_damage(15)

    # 3. LASER BEAM DAMAGE COLLISION
    for laser in active_lasers[:]:
        laser.update()
        if laser.lifetime <= 0:
            active_lasers.remove(laser)
            continue

        rad = math.radians(player.angle)
        start_pos = player.rect.center
        end_x = start_pos[0] + math.cos(rad) * laser.beam_length
        end_y = start_pos[1] + math.sin(rad) * laser.beam_length

        for minion in minions[:]:
            if minion.rect.clipline(start_pos, (end_x, end_y)):
                minion.take_damage(1)
                if minion.hp <= 0:
                    for _ in range(5): tokens.append(Token(minion.rect.centerx, minion.rect.centery))
                    minions.remove(minion)

        if current_boss and current_boss.is_alive:
            if isinstance(current_boss, PiggyBankWalletBoss):
                if current_boss.piggy_alive and current_boss.piggy_rect.clipline(start_pos, (end_x, end_y)):
                    current_boss.take_damage_piggy(1)
                if current_boss.wallet_alive and current_boss.wallet_rect.clipline(start_pos, (end_x, end_y)):
                    current_boss.take_damage_wallet(1)
            elif current_boss.rect.clipline(start_pos, (end_x, end_y)):
                current_boss.take_damage(1)

    # Update Enemies & Bosses
    for minion in minions: minion.update(player.rect, [])
    if current_boss and current_boss.is_alive: current_boss.update(player.rect)

    # Update Tokens
    for token in tokens[:]:
        token.update(player.rect)
        if player.rect.colliderect(token.rect):
            player_tokens += 1
            tokens.remove(token)

    # --- RENDERING ---
    screen.fill(COLOR_BG)

    for laser in active_lasers: laser.draw(screen)
    for slash in slashes: slash.draw(screen)
    for proj in projectiles: proj.draw(screen)
    for token in tokens: token.draw(screen)

    player.draw(screen)

    for minion in minions: minion.draw(screen)
    if current_boss and current_boss.is_alive:
        screen.blit(current_boss.image, current_boss.rect)
        current_boss.draw_healthbar(screen)

    # Charge Ring Indicator
    if is_charging and charge_timer > 0:
        charge_ratio = charge_timer / CHARGE_REQ
        pygame.draw.circle(screen, (80, 80, 80), player.rect.center, 36, width=2)
        fill_radius = int(36 * charge_ratio)
        if fill_radius > 0:
            pygame.draw.circle(screen, COLOR_LASER, player.rect.center, fill_radius, width=2)

    # HUD Card Queue
    hud_x = 20
    hud_y = HEIGHT - 70
    text_surf = font.render("CARD QUEUE (Left Click = Use | Hold 3s = Laser):", True, (200, 200, 200))
    screen.blit(text_surf, (hud_x, hud_y - 25))

    for idx, suit in enumerate(card_hand):
        box_rect = pygame.Rect(hud_x + (idx * 60), hud_y, 50, 50)
        card_color = SUIT_COLORS[suit]
        border_width = 4 if idx == 0 else 1
        pygame.draw.rect(screen, card_color, box_rect, width=border_width, border_radius=6)
        card_txt = font.render(suit[:4], True, card_color)
        screen.blit(card_txt, (box_rect.x + 5, box_rect.y + 16))

    # HUD Token Counter
    token_str = f"TOKENS: {player_tokens}"
    token_surf = font.render(token_str, True, COLOR_TOKEN_INNER)
    token_rect = token_surf.get_rect(topright=(WIDTH - 20, 20))
    bg_box = token_rect.inflate(12, 8)
    pygame.draw.rect(screen, (10, 10, 20), bg_box, border_radius=4)
    pygame.draw.rect(screen, COLOR_TOKEN_OUTER, bg_box, width=2, border_radius=4)
    screen.blit(token_surf, token_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()