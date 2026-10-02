import pygame
import sys
import math
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Finance Dungeon Crawler")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ==========================================
# 1. CAMERA SYSTEM
# ==========================================

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, max(-(self.width - SCREEN_WIDTH), x))
        y = min(0, max(-(self.height - SCREEN_HEIGHT), y))
        self.camera = pygame.Rect(x, y, self.width, self.height)

camera = Camera(WORLD_WIDTH, WORLD_HEIGHT)

# ==========================================
# 2. BULLETS & PLAYER
# ==========================================

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, is_homing=False, target_group=None):
        super().__init__()
        self.is_homing = is_homing
        self.target_group = target_group
        
        if self.is_homing:
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 0, 255))
            self.damage = 20  # Homing deals 20 DMG
            self.speed = 8
        else:
            self.image = pygame.Surface((6, 12))
            self.image.fill((255, 255, 100))
            self.damage = 7   # Normal deals 7 DMG
            self.speed = 11

        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.angle = -math.pi / 2

    def update(self):
        if self.is_homing and self.target_group:
            closest = None
            min_dist = 999999
            for target in self.target_group:
                if hasattr(target, 'is_alive') and not target.is_alive:
                    continue
                d = math.hypot(target.rect.centerx - self.rect.centerx, target.rect.centery - self.rect.centery)
                if d < min_dist:
                    min_dist = d
                    closest = target
            if closest:
                target_angle = math.atan2(closest.rect.centery - self.rect.centery, closest.rect.centerx - self.rect.centerx)
                self.angle = target_angle

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.rect.right < 0 or self.rect.left > WORLD_WIDTH or self.rect.bottom < 0 or self.rect.top > WORLD_HEIGHT:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed=5, damage=1, color=(255, 200, 0)):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = damage

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.right < 0 or self.rect.left > WORLD_WIDTH or self.rect.bottom < 0 or self.rect.top > WORLD_HEIGHT:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 220, 100), (4, 4, 28, 28), border_radius=6)
        pygame.draw.circle(self.image, (255, 255, 255), (12, 14), 4)
        pygame.draw.circle(self.image, (255, 255, 255), (24, 14), 4)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 100
        self.max_hp = 100
        self.speed = 6
        self.shoot_cooldown = 0
        self.invincible_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def take_damage(self, amount):
        if self.invincible_timer <= 0:
            self.hp -= amount
            self.invincible_timer = 15
            if self.hp <= 0:
                self.hp = 0

    def shoot(self, player_bullets, targets, is_homing=False):
        if self.shoot_cooldown == 0:
            bullet = PlayerBullet(self.rect.centerx, self.rect.top, is_homing=is_homing, target_group=targets)
            player_bullets.add(bullet)
            self.shoot_cooldown = 18 if is_homing else 10
            return True
        return False

    def draw_healthbar(self, surface):
        bar_w, bar_h = 180, 14
        pygame.draw.rect(surface, (80, 0, 0), (10, 40, bar_w, bar_h))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (0, 255, 0), (10, 40, bar_w * ratio, bar_h))
        hp_txt = font.render(f"HP: {self.hp}/{self.max_hp}", True, (255, 255, 255))
        surface.blit(hp_txt, (200, 38))

# ==========================================
# 3. MINIONS (20 HP EACH)
# ==========================================

class MeleeMinion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (230, 40, 80), (15, 15), 14)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 20
        self.max_hp = 20
        self.damage = 2
        self.speed = 2.8

    def update(self, player_rect, enemy_bullets):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def draw_hp(self, surface):
        pos = camera.apply(self)
        bar_w, bar_h = 30, 4
        bx = pos.centerx - (bar_w // 2)
        by = pos.top - 8
        pygame.draw.rect(surface, (100, 0, 0), (bx, by, bar_w, bar_h))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (0, 255, 0), (bx, by, bar_w * ratio, bar_h))


class RangedMinion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (0, 180, 255), [(15, 2), (28, 26), (2, 26)])

        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 20
        self.max_hp = 20
        self.damage = 1
        self.speed = 1.5
        self.shoot_timer = 0

    def update(self, player_rect, enemy_bullets):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 200:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

        self.shoot_timer += 1
        if self.shoot_timer >= 70:
            self.shoot_timer = 0
            angle = math.atan2(dy, dx)
            enemy_bullets.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle, speed=5, damage=self.damage))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def draw_hp(self, surface):
        pos = camera.apply(self)
        bar_w, bar_h = 30, 4
        bx = pos.centerx - (bar_w // 2)
        by = pos.top - 8
        pygame.draw.rect(surface, (100, 0, 0), (bx, by, bar_w, bar_h))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (0, 255, 0), (bx, by, bar_w * ratio, bar_h))

# ==========================================
# 4. BOSSES WITH HORNS & HEALTH BARS
# ==========================================

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, max_hp, name="Boss"):
        super().__init__()
        self.max_hp = max_hp
        self.hp = max_hp
        self.name = name
        self.image = pygame.Surface((70, 70), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.is_alive = True
        self.bullets = pygame.sprite.Group()

    def update(self, player_rect):
        self.bullets.update()

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def draw_healthbar(self, surface):
        bar_w, bar_h = 320, 18
        bar_x = SCREEN_WIDTH // 2 - (bar_w // 2)
        bar_y = 40
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_w * ratio, bar_h))
        title = font.render(f"{self.name}: {self.hp}/{self.max_hp} HP", True, (255, 255, 255))
        surface.blit(title, (bar_x, bar_y - 20))


class PiggyBankWalletBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=200, name="Lvl 1 Boss: Piggy & Wallet Duo")
        self.piggy_hp, self.wallet_hp = 100, 100
        self.piggy_alive, self.wallet_alive = True, True
        self.piggy_rect = pygame.Rect(x - 60, y, 55, 55)
        self.wallet_rect = pygame.Rect(x + 60, y, 55, 55)
        self.shoot_timer = 0

    def draw_duo(self, surface):
        # Draw Piggy with Horns
        if self.piggy_alive:
            p_rect = camera.apply_rect(self.piggy_rect)
            pygame.draw.polygon(surface, (255, 255, 255), [(p_rect.left + 5, p_rect.top), (p_rect.left + 15, p_rect.top), (p_rect.left + 2, p_rect.top - 14)])
            pygame.draw.polygon(surface, (255, 255, 255), [(p_rect.right - 15, p_rect.top), (p_rect.right - 5, p_rect.top), (p_rect.right - 2, p_rect.top - 14)])
            pygame.draw.rect(surface, (255, 105, 180), p_rect, border_radius=10)

        # Draw Wallet with Horns
        if self.wallet_alive:
            w_rect = camera.apply_rect(self.wallet_rect)
            pygame.draw.polygon(surface, (200, 200, 200), [(w_rect.left + 5, w_rect.top), (w_rect.left + 15, w_rect.top), (w_rect.left + 2, w_rect.top - 14)])
            pygame.draw.polygon(surface, (200, 200, 200), [(w_rect.right - 15, w_rect.top), (w_rect.right - 5, w_rect.top), (w_rect.right - 2, w_rect.top - 14)])
            pygame.draw.rect(surface, (139, 69, 19), w_rect, border_radius=6)

    def get_damage_rects(self):
        rects = []
        if self.piggy_alive: rects.append(('piggy', self.piggy_rect))
        if self.wallet_alive: rects.append(('wallet', self.wallet_rect))
        return rects

    def update(self, player_rect):
        self.bullets.update()
        self.shoot_timer += 1
        if self.shoot_timer >= 60:
            self.shoot_timer = 0
            if self.piggy_alive:
                ang = math.atan2(player_rect.centery - self.piggy_rect.centery, player_rect.centerx - self.piggy_rect.centerx)
                self.bullets.add(EnemyBullet(self.piggy_rect.centerx, self.piggy_rect.centery, ang, speed=4.5, damage=5))
            if self.wallet_alive:
                ang = math.atan2(player_rect.centery - self.wallet_rect.centery, player_rect.centerx - self.wallet_rect.centerx)
                self.bullets.add(EnemyBullet(self.wallet_rect.centerx, self.wallet_rect.centery, ang, speed=4.5, damage=5))

    def take_damage_piggy(self, amt):
        if not self.piggy_alive: return
        self.piggy_hp = max(0, self.piggy_hp - amt)
        if self.piggy_hp == 0: self.piggy_alive = False
        self._sync()

    def take_damage_wallet(self, amt):
        if not self.wallet_alive: return
        self.wallet_hp = max(0, self.wallet_hp - amt)
        if self.wallet_hp == 0: self.wallet_alive = False
        self._sync()

    def _sync(self):
        self.hp = self.piggy_hp + self.wallet_hp
        if not self.piggy_alive and not self.wallet_alive: self.is_alive = False


class OverdueBillBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=300, name="Lvl 2 Boss: Overdue Bill")
        self.image = pygame.Surface((60, 100), pygame.SRCALPHA)
        # Horns
        pygame.draw.polygon(self.image, (180, 0, 0), [(5, 20), (18, 20), (0, 0)])
        pygame.draw.polygon(self.image, (180, 0, 0), [(42, 20), (55, 20), (60, 0)])
        # Bill body
        pygame.draw.rect(self.image, (240, 240, 240), (0, 20, 60, 80))
        pygame.draw.rect(self.image, (220, 0, 0), (5, 25, 50, 15))
        self.rect = self.image.get_rect(center=(x, y))
        self.shoot_timer = 0

    def update(self, player_rect):
        super().update(player_rect)
        self.shoot_timer += 1
        if self.shoot_timer >= 45:
            self.shoot_timer = 0
            ang = math.atan2(player_rect.centery - self.rect.centery, player_rect.centerx - self.rect.centerx)
            self.bullets.add(EnemyBullet(self.rect.centerx, self.rect.centery, ang, speed=5.5, damage=8, color=(255, 50, 50)))


class InterestRateBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=450, name="Lvl 3 Boss: Interest Rate Poison Boss")
        self.image = pygame.Surface((70, 80), pygame.SRCALPHA)
        # Horns
        pygame.draw.polygon(self.image, (50, 200, 50), [(15, 20), (28, 20), (5, 0)])
        pygame.draw.polygon(self.image, (50, 200, 50), [(42, 20), (55, 20), (65, 0)])
        # Poison Orb Body
        pygame.draw.circle(self.image, (150, 0, 200), (35, 48), 28)
        self.rect = self.image.get_rect(center=(x, y))
        self.shoot_timer = 0

    def update(self, player_rect):
        super().update(player_rect)
        self.shoot_timer += 1
        if self.shoot_timer >= 35:
            self.shoot_timer = 0
            base_ang = math.atan2(player_rect.centery - self.rect.centery, player_rect.centerx - self.rect.centerx)
            for offset in [-0.4, -0.2, 0, 0.2, 0.4]:
                self.bullets.add(EnemyBullet(self.rect.centerx, self.rect.centery, base_ang + offset, speed=5, damage=13, color=(50, 255, 50)))


class CommonSenseBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=600, name="Lvl 4 Boss: Common Sense Copycat")
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        # Horns
        pygame.draw.polygon(self.image, (255, 215, 0), [(5, 20), (18, 20), (0, 0)])
        pygame.draw.polygon(self.image, (255, 215, 0), [(42, 20), (55, 20), (60, 0)])
        # Body
        pygame.draw.rect(self.image, (255, 180, 0), (0, 20, 60, 60), border_radius=10)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_rect):
        super().update(player_rect)
        self.rect.centerx = WORLD_WIDTH - player_rect.centerx
        self.rect.centery = player_rect.centery - 220

    def copy_attack(self, player_rect):
        ang = math.atan2(player_rect.centery - self.rect.centery, player_rect.centerx - self.rect.centerx)
        self.bullets.add(EnemyBullet(self.rect.centerx, self.rect.centery, ang, speed=7, damage=20, color=(255, 0, 0)))

# ==========================================
# 5. GAME CONTROLLER
# ==========================================

class DungeonGame:
    def __init__(self):
        self.floor = 1
        self.max_floors = 4
        self.targets = {1: 10, 2: 20, 3: 30, 4: 40}
        self.minions_killed = 0
        self.boss_active = False

    def get_target_kills(self):
        return self.targets[self.floor]

    def create_boss(self):
        cx, cy = WORLD_WIDTH // 2, WORLD_HEIGHT // 2 - 200
        if self.floor == 1: return PiggyBankWalletBoss(cx, cy)
        if self.floor == 2: return OverdueBillBoss(cx, cy)
        if self.floor == 3: return InterestRateBoss(cx, cy)
        if self.floor == 4: return CommonSenseBoss(cx, cy)
        return None

# ==========================================
# 6. MAIN GAME LOOP
# ==========================================

game = DungeonGame()
player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2 + 300)

player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
minions = pygame.sprite.Group()
current_boss = None

def spawn_minion_wave():
    while len(minions) < 4:
        px = player.rect.centerx + random.randint(-400, 400)
        py = player.rect.centery + random.randint(-400, 400)
        px = max(100, min(WORLD_WIDTH - 100, px))
        py = max(100, min(WORLD_HEIGHT - 100, py))
        
        if random.random() < 0.5:
            minions.add(MeleeMinion(px, py))
        else:
            minions.add(RangedMinion(px, py))

spawn_minion_wave()

game_over = False
victory = False
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over and not victory:
        # Controls
        keys = pygame.key.get_pressed()
        is_homing = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        if keys[pygame.K_SPACE]:
            targets = [current_boss] if game.boss_active else minions
            fired = player.shoot(player_bullets, targets, is_homing=is_homing)
            if fired and game.boss_active and isinstance(current_boss, CommonSenseBoss):
                current_boss.copy_attack(player.rect)

        # Updates
        player.update()
        camera.update(player)
        player_bullets.update()
        enemy_bullets.update()

        # Minion Logic & Spawning
        if not game.boss_active:
            kills_left = game.get_target_kills() - game.minions_killed
            if len(minions) < 4 and kills_left > 0:
                spawn_minion_wave()

            minions.update(player.rect, enemy_bullets)

            # Player shooting Minions
            for bullet in list(player_bullets):
                hits = pygame.sprite.spritecollide(bullet, minions, False)
                if hits:
                    bullet.kill()
                    for m in hits:
                        if m.take_damage(bullet.damage):
                            game.minions_killed += 1
                            if game.minions_killed >= game.get_target_kills():
                                game.boss_active = True
                                minions.empty()
                                enemy_bullets.empty()
                                current_boss = game.create_boss()
                                break

            # Melee Minions damaging Player (Contact Damage)
            melee_hits = pygame.sprite.spritecollide(player, minions, False)
            for m in melee_hits:
                player.take_damage(m.damage)

        # Boss Logic
        elif game.boss_active and current_boss:
            current_boss.update(player.rect)

            # Boss Bullets damaging player
            b_hits = pygame.sprite.spritecollide(player, current_boss.bullets, True)
            for b in b_hits:
                player.take_damage(b.damage)

            # Player shooting Boss
            if hasattr(current_boss, 'get_damage_rects'):
                for bullet in list(player_bullets):
                    for target, rect in current_boss.get_damage_rects():
                        if rect.colliderect(bullet.rect):
                            bullet.kill()
                            if target == 'piggy': current_boss.take_damage_piggy(bullet.damage)
                            elif target == 'wallet': current_boss.take_damage_wallet(bullet.damage)
                            break
            else:
                hits = pygame.sprite.spritecollide(current_boss, player_bullets, True)
                for bullet in hits:
                    current_boss.take_damage(bullet.damage)

            # Check Boss Defeated
            if not current_boss.is_alive:
                if game.floor < game.max_floors:
                    game.floor += 1
                    game.minions_killed = 0
                    game.boss_active = False
                    current_boss = None
                    enemy_bullets.empty()
                    player_bullets.empty()
                    spawn_minion_wave()
                else:
                    victory = True

        # Enemy Bullets damaging player
        eb_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for b in eb_hits:
            player.take_damage(b.damage)

        if player.hp <= 0:
            game_over = True

    # Drawing Scene
    screen.fill((25, 25, 30))

    # Grid boundary
    dungeon_rect = camera.apply_rect(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))
    pygame.draw.rect(screen, (80, 80, 100), dungeon_rect, 4)

    # Render entities
    if player.invincible_timer % 4 < 2:
        screen.blit(player.image, camera.apply(player))

    for b in player_bullets: screen.blit(b.image, camera.apply(b))
    for b in enemy_bullets: screen.blit(b.image, camera.apply(b))

    if not game.boss_active:
        for m in minions:
            screen.blit(m.image, camera.apply(m))
            m.draw_hp(screen)
    elif current_boss and current_boss.is_alive:
        if hasattr(current_boss, 'draw_duo'):
            current_boss.draw_duo(screen)
        else:
            screen.blit(current_boss.image, camera.apply(current_boss))
        
        for b in current_boss.bullets: screen.blit(b.image, camera.apply(b))
        current_boss.draw_healthbar(screen)

    # HUD Elements
    if not game.boss_active:
        status_str = f"Floor {game.floor}/{game.max_floors} | Minions Killed: {game.minions_killed} / {game.get_target_kills()}"
    else:
        status_str = f"Floor {game.floor}/{game.max_floors} | BOSS BATTLE!"

    header = font.render(status_str + " | [WASD]: Move | [Space]: 7 DMG | [Shift+Space]: 20 DMG Homing", True, (255, 255, 255))
    screen.blit(header, (10, 10))
    player.draw_healthbar(screen)

    if game_over:
        over_txt = font.render("GAME OVER - YOU DIED!", True, (255, 0, 0))
        screen.blit(over_txt, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
    elif victory:
        win_txt = font.render("VICTORY! YOU BEAT ALL FLOORS!", True, (0, 255, 0))
        screen.blit(win_txt, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()