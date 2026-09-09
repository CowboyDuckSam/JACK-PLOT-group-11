import sys
import math
import random
import pygame
#changed a bit to fix some bugs and to look more tidy and easier for me to work on
# 1. INITIALIZATION & SETUP
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

SUIT_COLORS = {
    "SPADE": COLOR_SPADE,
    "HEART": COLOR_HEART,
    "CLUB": COLOR_CLUB,
    "DIAMOND": COLOR_DIAMOND
}

# --- CUSTOM TIMERS & EVENTS ---
# Trigger event every 500 milliseconds (0.5 seconds)
SPAWN_CARD_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_CARD_EVENT, 500)

# 2. GAME CLASSES

class SpadeProjectile:
    """Ranged arrow shot made of a custom spade polygon."""
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 12
        self.damage = 15
        self.lifetime = 60
        
        rad = math.radians(self.angle)
        self.dx = math.cos(rad) * self.speed
        self.dy = math.sin(rad) * self.speed

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, surface):
        rad = math.radians(self.angle)
        tip = (self.x + math.cos(rad) * 15, self.y + math.sin(rad) * 15)
        left = (self.x + math.cos(rad + 2.4) * 10, self.y + math.sin(rad + 2.4) * 10)
        base = (self.x - math.cos(rad) * 5, self.y - math.sin(rad) * 5)
        right = (self.x + math.cos(rad - 2.4) * 10, self.y + math.sin(rad - 2.4) * 10)

        pygame.draw.polygon(surface, COLOR_SPADE, [tip, left, base, right])


class ClubSlash:
    """Triangle-shaped melee slash arc where the player is facing."""
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = 10
        self.lifetime = 10
        self.reach = 65
        self.spread = 0.6

    def update(self):
        self.lifetime -= 1

    def draw(self, surface):
        rad = math.radians(self.angle)
        origin = (self.x, self.y)
        left_pt = (self.x + math.cos(rad - self.spread) * self.reach, 
                   self.y + math.sin(rad - self.spread) * self.reach)
        right_pt = (self.x + math.cos(rad + self.spread) * self.reach, 
                    self.y + math.sin(rad + self.spread) * self.reach)

        pygame.draw.polygon(surface, COLOR_CLUB, [origin, left_pt, right_pt])
class LaserBeam:
    """Laser beam that lasts 5 seconds (300 frames) and follows player orientation."""
    def __init__(self, player):
        self.player = player
        self.lifetime = 300  # 5 seconds at 60 FPS
        self.total_damage = 20
        self.damage_per_frame = self.total_damage / 300
        self.beam_length = 800

    def update(self):
        self.lifetime -= 1 

    def draw(self, surface):
        # Calculate endpoint based on player's current facing angle
        rad = math.radians(self.player.angle)
        start_pos = self.player.rect.center
        end_x = start_pos[0] + math.cos(rad) * self.beam_length
        end_y = start_pos[1] + math.sin(rad) * self.beam_length

        # Outer glow beam
        pygame.draw.line(surface, COLOR_LASER, start_pos, (end_x, end_y), 18)
        # Inner white core beam
        pygame.draw.line(surface, (255, 255, 255), start_pos, (end_x, end_y), 6)

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
        if self.is_dashing:
            return
            
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


# 3. INSTANTIATE GAME OBJECTS
player = Player(WIDTH // 2, HEIGHT // 2)
projectiles = []
slashes = []
active_lasers = []

# Hand / Queue Data Structures
card_hand = []  # Holds maximum of 5 cards
MAX_HAND_SIZE = 5
SUITS = ["SPADE", "HEART", "CLUB", "DIAMOND"]

# Laser Charge Tracking Variables
charge_timer = 0          # Tracks frames held (180 frames = 3 seconds at 60 FPS)
CHARGE_REQ = 180          # 3 seconds * 60 FPS
is_charging = False

font = pygame.font.SysFont("Arial", 14, bold=True)

# 4. MAIN GAME LOOP
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- TIMER EVENT: GENERATE CARD EVERY 0.5 SECONDS ---
        if event.type == SPAWN_CARD_EVENT:
            if len(card_hand) < MAX_HAND_SIZE:
                card_hand.append(random.choice(SUITS))

        # --- RELEASE LEFT CLICK: EXECUTE SINGLE CARD IF NOT CHARGED ---
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if is_charging and charge_timer < CHARGE_REQ:
                if len(card_hand) > 0:
                    current_card = card_hand.pop(0)

                    if current_card == "SPADE":
                        projectiles.append(SpadeProjectile(player.rect.centerx, player.rect.centery, player.angle))
                    elif current_card == "HEART":
                        player.use_heart_shield()
                    elif current_card == "CLUB":
                        slashes.append(ClubSlash(player.rect.centerx, player.rect.centery, player.angle))
                    elif current_card == "DIAMOND":
                        player.use_diamond_dash(keys)

            # Reset charge state on release
            is_charging = False
            charge_timer = 0

    # --- HOLD LEFT CLICK CHARGE LASER ---
    if mouse_buttons[0]:  # Left mouse button held
        if len(card_hand) >= 4:
            is_charging = True
            charge_timer += 1

            # Fully Charged! Fire Laser Combo
            if charge_timer >= CHARGE_REQ:
                for _ in range(4):
                    card_hand.pop(0)

                active_lasers.append(LaserBeam(player))
                is_charging = False
                charge_timer = 0
        else:
            is_charging = False
            charge_timer = 0

    # --- HOLD LEFT CLICK CHARGE LASER---
    if mouse_buttons[0]:  # Left mouse button is currently held down
        if len(card_hand) >= 4:
            is_charging = True
            charge_timer += 1

            # Fully Charged! Fires laser
            if charge_timer >= CHARGE_REQ:
                # Consume 4 cards from the queue
                for _ in range(4):
                    card_hand.pop(0)

                # Spawn active laser beam
                active_lasers.append(LaserBeam(player))

                # Reset charging state
                is_charging = False
                charge_timer = 0
    else:
        # Not enough cards to charge
        is_charging = False
        charge_timer = 0

    # --- UPDATES ---
    player.update(keys, mouse_pos)
    for laser in active_lasers[:]: 
        laser.update()
        if laser.lifetime <= 0:
            active_lasers.remove(laser)
    for proj in projectiles[:]:
        proj.update()
        if proj.lifetime <= 0 or not screen.get_rect().collidepoint(proj.x, proj.y):
            projectiles.remove(proj)

    for slash in slashes[:]:
        slash.update()
        if slash.lifetime <= 0:
            slashes.remove(slash)

    # --- RENDERING ---
    screen.fill(COLOR_BG)
    for laser in active_lasers:
        laser.draw(screen)
        
    for slash in slashes:
        slash.draw(screen)

    player.draw(screen)

    for proj in projectiles:
        proj.draw(screen)

    # --- DRAW CARD QUEUE HUD ---
    hud_x = 20
    hud_y = HEIGHT - 70
    
    # Label and text
    text_surf = font.render("CARD QUEUE (Left Click to Use First):", True, (200, 200, 200))
    screen.blit(text_surf, (hud_x, hud_y - 25))

    for idx, suit in enumerate(card_hand):
        box_rect = pygame.Rect(hud_x + (idx * 60), hud_y, 50, 50)
        card_color = SUIT_COLORS[suit]
        
        # Highlight first card in line
        border_width = 4 if idx == 0 else 1
        pygame.draw.rect(screen, card_color, box_rect, width=border_width, border_radius=6)
        
        # Render text name inside card
        card_txt = font.render(suit[:4], True, card_color)
        screen.blit(card_txt, (box_rect.x + 5, box_rect.y + 16))

    # Draw Mouse Cursor
    pygame.draw.circle(screen, (255, 255, 255), mouse_pos, 5, width=1)

    pygame.display.flip()
    clock.tick(60)
#end 
pygame.quit()
sys.exit()