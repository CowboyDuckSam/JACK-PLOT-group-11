import pygame
import sys
import math
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Finance Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ==========================================
# 1. BULLETS & PLAYER
# ==========================================

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = 8
        self.damage = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((35, 35))
        self.image.fill((0, 220, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 100
        self.max_hp = 100
        self.speed = 5
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

        self.rect.clamp_ip(screen.get_rect())

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def take_damage(self, amount):
        if self.invincible_timer == 0:
            self.hp -= amount
            self.invincible_timer = 30  # Invincibility frames
            if self.hp <= 0:
                self.hp = 0

    def shoot(self, player_bullets):
        if self.shoot_cooldown == 0:
            player_bullets.add(PlayerBullet(self.rect.centerx, self.rect.top))
            self.shoot_cooldown = 12
            return True
        return False

    def draw_healthbar(self, surface):
        bar_width = 180
        bar_height = 14
        pygame.draw.rect(surface, (100, 0, 0), (10, 40, bar_width, bar_height))
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (0, 255, 0), (10, 40, bar_width * ratio, bar_height))
        hp_text = font.render(f"HP: {self.hp}/{self.max_hp}", True, (255, 255, 255))
        surface.blit(hp_text, (200, 38))

# ==========================================
# 2. MINIONS (WITH HEALTH & ATTACKS)
# ==========================================

class MeleeMinion(pygame.sprite.Sprite):
    """Chases the player directly and deals contact damage."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((28, 28))
        self.image.fill((255, 50, 100))  # Magenta
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 30
        self.max_hp = 30
        self.damage = 10
        self.speed = 2.2

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

    def draw_hp(self, surface):
        bar_w = 30
        bar_h = 4
        bx = self.rect.centerx - (bar_w // 2)
        by = self.rect.top - 8
        pygame.draw.rect(surface, (100, 0, 0), (bx, by, bar_w, bar_h))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (0, 255, 0), (bx, by, bar_w * ratio, bar_h))


class RangedMinion(pygame.sprite.Sprite):
    """Keeps distance and shoots at the player."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((28, 28))
        self.image.fill((0, 180, 255))  # Cyan
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 25
        self.max_hp = 25
        self.damage = 8
        self.speed = 1.2
        self.shoot_timer = 0

    def update(self, player_rect, enemy_bullets):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 180:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

        self.shoot_timer += 1
        if self.shoot_timer >= 80:
            self.shoot_timer = 0
            angle = math.atan2(dy, dx)
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, angle, speed=4, damage=self.damage)
            enemy_bullets.add(bullet)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    def draw_hp(self, surface):
        bar_w = 30
        bar_h = 4
        bx = self.rect.centerx - (bar_w // 2)
        by = self.rect.top - 8
        pygame.draw.rect(surface, (100, 0, 0), (bx, by, bar_w, bar_h))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (0, 255, 0), (bx, by, bar_w * ratio, bar_h))


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 220, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = damage

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# ==========================================
# 3. BOSSES
# ==========================================

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, max_hp):
        super().__init__()
        self.max_hp = max_hp
        self.hp = max_hp
        self.image = pygame.Surface((60, 60))
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
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
        bar_width = 120
        bar_height = 8
        bar_x = self.rect.centerx - (bar_width // 2)
        bar_y = self.rect.top - 15
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * ratio, bar_height))


class PiggyBankWalletBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=200)
        self.piggy_hp = 100
        self.wallet_hp = 100
        self.piggy_alive = True
        self.wallet_alive = True

        self.piggy_rect = pygame.Rect(x - 60, y, 50, 50)
        self.wallet_rect = pygame.Rect(x + 60, y, 50, 50)
        self.shoot_timer = 0

    def draw_duo(self, surface):
        if self.piggy_alive:
            pygame.draw.rect(surface, (255, 105, 180), self.piggy_rect)
        if self.wallet_alive:
            pygame.draw.rect(surface, (139, 69, 19), self.wallet_rect)

    def get_damage_rects(self):
        rects = []
        if self.piggy_alive:
            rects.append(('piggy', self.piggy_rect))
        if self.wallet_alive:
            rects.append(('wallet', self.wallet_rect))
        return rects

    def update(self, player_rect):
        self.bullets.update()
        self.shoot_timer += 1
        if self.shoot_timer >= 65:
            self.shoot_timer = 0
            self.shoot_dual(player_rect)

    def shoot_dual(self, player_rect):
        if self.piggy_alive:
            angle = math.atan2(player_rect.centery - self.piggy_rect.centery, player_rect.centerx - self.piggy_rect.centerx)
            self.bullets.add(EnemyBullet(self.piggy_rect.centerx, self.piggy_rect.centery, angle, speed=4, damage=7))
        if self.wallet_alive:
            angle = math.atan2(player_rect.centery - self.wallet_rect.centery, player_rect.centerx - self.wallet_rect.centerx)
            self.bullets.add(EnemyBullet(self.wallet_rect.centerx, self.wallet_rect.centery, angle, speed=4, damage=7))

    def take_damage_piggy(self, amount):
        if not self.piggy_alive: return
        self.piggy_hp -= amount
        if self.piggy_hp <= 0:
            self.piggy_hp = 0
            self.piggy_alive = False
        self._sync()

    def take_damage_wallet(self, amount):
        if not self.wallet_alive: return
        self.wallet_hp -= amount
        if self.wallet_hp <= 0:
            self.wallet_hp = 0
            self.wallet_alive = False
        self._sync()

    def _sync(self):
        self.hp = self.piggy_hp + self.wallet_hp
        if not self.piggy_alive and not self.wallet_alive:
            self.is_alive = False


class OverdueBillBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=300)
        self.shoot_timer = 0

    def update(self, player_rect):
        super().update(player_rect)
        self.shoot_timer += 1
        if self.shoot_timer >= 60:
            self.shoot_timer = 0
            angle = math.atan2(player_rect.centery - self.rect.centery, player_rect.centerx - self.rect.centerx)
            self.bullets.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle, speed=5, damage=12))

# ==========================================
# 4. LEVEL MANAGER
# ==========================================

class LevelManager:
    def __init__(self):
        self.rooms = ["SPAWN", "ENEMIES", "SHOP", "BOSS"]
        self.current_room_index = 0
        self.current_level = 1

    def get_current_room(self):
        return self.rooms[self.current_room_index]

    def advance_room(self, minions_alive, boss_alive):
        current = self.get_current_room()

        # Lock room until enemies or boss are clear
        if current == "ENEMIES" and minions_alive:
            print("Defeat all minions first!")
            return False, None
        if current == "BOSS" and boss_alive:
            print("Defeat the boss first!")
            return False, None

        # Level Up after BOSS
        if current == "BOSS" and not boss_alive:
            self.current_level += 1
            self.current_room_index = 0
            print(f"--- LEVEL {self.current_level} ---")
            return True, self.get_boss()

        self.current_room_index = (self.current_room_index + 1) % len(self.rooms)
        print(f"Entering Room: {self.get_current_room()}")
        return False, None

    def get_boss(self):
        if self.current_level == 1:
            return PiggyBankWalletBoss(400, 100)
        else:
            return OverdueBillBoss(400, 100)

    def spawn_minions(self):
        group = pygame.sprite.Group()
        group.add(MeleeMinion(200, 150))
        group.add(MeleeMinion(600, 150))
        group.add(RangedMinion(400, 120))
        return group

# ==========================================
# 5. MAIN GAME LOOP
# ==========================================

level_mgr = LevelManager()
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)

player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

minions = pygame.sprite.Group()
current_boss = level_mgr.get_boss()

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                minions_left = len(minions) > 0
                boss_left = current_boss.is_alive if current_boss else False
                
                level_up, new_boss = level_mgr.advance_room(minions_left, boss_left)
                
                if level_mgr.get_current_room() == "ENEMIES" and len(minions) == 0:
                    minions = level_mgr.spawn_minions()
                
                if level_up and new_boss:
                    current_boss = new_boss
                    enemy_bullets.empty()
                    player_bullets.empty()

    # Controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        player.shoot(player_bullets)

    # Updates
    player.update()
    player_bullets.update()
    enemy_bullets.update()

    room = level_mgr.get_current_room()

    # --- ENEMIES ROOM LOGIC ---
    if room == "ENEMIES":
        minions.update(player.rect, enemy_bullets)
        
        # Player bullets hit Minions
        for bullet in list(player_bullets):
            hits = pygame.sprite.spritecollide(bullet, minions, False)
            if hits:
                bullet.kill()
                for m in hits:
                    m.take_damage(bullet.damage)

        # Minions touch player (Melee contact damage)
        melee_hits = pygame.sprite.spritecollide(player, minions, False)
        for m in melee_hits:
            player.take_damage(m.damage)

    # --- BOSS ROOM LOGIC ---
    elif room == "BOSS" and current_boss and current_boss.is_alive:
        current_boss.update(player.rect)

        # Boss bullets hit player
        hits = pygame.sprite.spritecollide(player, current_boss.bullets, True)
        for b in hits:
            player.take_damage(getattr(b, 'damage', 10))

        # Player bullets hit Boss
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

    # Enemy bullets hit player
    eb_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for b in eb_hits:
        player.take_damage(b.damage)

    # --- DRAWING ---
    screen.fill((25, 25, 30))

    if player.invincible_timer % 4 < 2:
        screen.blit(player.image, player.rect)

    player_bullets.draw(screen)
    enemy_bullets.draw(screen)

    if room == "ENEMIES":
        minions.draw(screen)
        for m in minions:
            m.draw_hp(screen)
        if len(minions) == 0:
            txt = font.render("ROOM CLEAR! Press ENTER to move to SHOP", True, (0, 255, 0))
            screen.blit(txt, (240, 280))

    elif room == "BOSS" and current_boss:
        if current_boss.is_alive:
            if hasattr(current_boss, 'draw_duo'):
                current_boss.draw_duo(screen)
            else:
                screen.blit(current_boss.image, current_boss.rect)
            current_boss.draw_healthbar(screen)
            current_boss.bullets.draw(screen)
        else:
            txt = font.render("BOSS DEFEATED! Press ENTER for Next Level", True, (0, 255, 0))
            screen.blit(txt, (230, 280))

    # UI Header & Player HP
    header = font.render(f"Level {level_mgr.current_level} | Room: {room} | [WASD]: Move | [Space]: Shoot | [ENTER]: Next Room", True, (255, 255, 255))
    screen.blit(header, (10, 10))
    player.draw_healthbar(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()