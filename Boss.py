import pygame
import math
import random

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540


class Boss(pygame.sprite.Sprite):
    """Base class for all bosses in the game."""

    def __init__(self, x, y, max_hp):
        super().__init__()
        self.max_hp = max_hp
        self.hp = max_hp
        self.image = pygame.Surface((60, 60))
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.phase = 1
        self.is_alive = True
        self.bullets = pygame.sprite.Group()

    def update(self, player_rect):
        """Update boss behavior."""
        self.bullets.update()

    def take_damage(self, amount):
        """Apply damage to the boss."""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def draw_healthbar(self, surface):
        """Draw health bar above the boss."""
        bar_width = 120
        bar_height = 8
        bar_x = self.rect.centerx - (bar_width // 2)
        bar_y = self.rect.top - 15

        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        health_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

    def change_phase(self, new_phase):
        """Change boss phase."""
        self.phase = new_phase


class NormalBossBullet(pygame.sprite.Sprite):
    """Standard boss bullet used by Level 1 (7 damage)."""

    def __init__(self, x, y, angle, speed=4):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 200, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = 7

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class PiggyBankWalletBoss(Boss):
    """Level 1 boss - duo fight (Piggy Bank + Wallet), 200 HP total."""

    def __init__(self, x, y):
        super().__init__(x, y, max_hp=200)
        self.piggy_hp = 100
        self.wallet_hp = 100
        self.piggy_alive = True
        self.wallet_alive = True
        self.laser_phase = False

        self.piggy_rect = pygame.Rect(x - 60, y, 50, 50)
        self.wallet_rect = pygame.Rect(x + 60, y, 50, 50)

        self.shoot_timer = 0

    def update(self, player_rect):
        """Update both enemies, or laser maze phase if one has died."""
        self.bullets.update()

        if self.laser_phase:
            self._update_laser_phase(player_rect)
            return

        self.shoot_timer += 1
        if self.shoot_timer >= 70:
            self.shoot_timer = 0
            self.shoot_dual(player_rect)

    def shoot_dual(self, player_rect):
        """Fire normal bullets from both enemies if alive."""
        if self.piggy_alive:
            dx = player_rect.centerx - self.piggy_rect.centerx
            dy = player_rect.centery - self.piggy_rect.centery
            angle = math.atan2(dy, dx)
            self.bullets.add(NormalBossBullet(self.piggy_rect.centerx, self.piggy_rect.centery, angle))

        if self.wallet_alive:
            dx = player_rect.centerx - self.wallet_rect.centerx
            dy = player_rect.centery - self.wallet_rect.centery
            angle = math.atan2(dy, dx)
            self.bullets.add(NormalBossBullet(self.wallet_rect.centerx, self.wallet_rect.centery, angle))

    def take_damage_piggy(self, amount):
        """Apply damage to Piggy Bank specifically."""
        if not self.piggy_alive:
            return
        self.piggy_hp -= amount
        if self.piggy_hp <= 0:
            self.piggy_hp = 0
            self.piggy_alive = False
            self.laser_phase = True
            self.change_phase(2)
        self._sync_total_hp()

    def take_damage_wallet(self, amount):
        """Apply damage to Wallet specifically."""
        if not self.wallet_alive:
            return
        self.wallet_hp -= amount
        if self.wallet_hp <= 0:
            self.wallet_hp = 0
            self.wallet_alive = False
        self._sync_total_hp()

    def _sync_total_hp(self):
        """Keep the shared hp/is_alive in sync with both enemies."""
        self.hp = self.piggy_hp + self.wallet_hp
        if not self.piggy_alive and not self.wallet_alive:
            self.is_alive = False

    def _update_laser_phase(self, player_rect):
        """Laser maze behavior once Piggy Bank dies."""
        self.shoot_timer += 1
        if self.shoot_timer >= 45:
            self.shoot_timer = 0
            angle = 0
            self.bullets.add(NormalBossBullet(0, self.rect.centery, angle, speed=6))


class OverdueBillBoss(Boss):
    """Level 2 boss - fires homing bullets and creates damaging floor zones. 350 HP."""

    def __init__(self, x, y):
        super().__init__(x, y, max_hp=350)
        self.shoot_timer = 0
        self.debt_zones = pygame.sprite.Group()
        self.zone_timer = 0

    def update(self, player_rect):
        """Update bullets, zones, and timed attacks."""
        super().update(player_rect)
        self.debt_zones.update()

        self.shoot_timer += 1
        if self.shoot_timer >= 90:
            self.shoot_timer = 0
            self.shoot(player_rect)

        self.zone_timer += 1
        if self.zone_timer >= 180:
            self.zone_timer = 0
            self.spawn_debt_zone()

    def shoot(self, player_rect):
        """Fire a homing bullet toward the player."""
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)

        bullet = OverdueBillBullet(self.rect.centerx, self.rect.centery, angle, speed=4)
        self.bullets.add(bullet)

    def spawn_debt_zone(self):
        """Create a damaging floor zone."""
        x = random.randint(40, SCREEN_WIDTH - 40)
        y = SCREEN_HEIGHT - 100

        zone = DebtZone(x, y)
        self.debt_zones.add(zone)


class OverdueBillBullet(pygame.sprite.Sprite):
    """A homing bullet that moves toward the player. 20 damage."""

    def __init__(self, x, y, angle, speed):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = 20

    def update(self):
        """Move the bullet along its firing angle."""
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class DebtZone(pygame.sprite.Sprite):
    """A static damaging floor tile with a limited lifespan."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.image.fill((60, 0, 90, 180))
        self.rect = self.image.get_rect(center=(x, y))
        self.damage_per_tick = 1
        self.lifespan = 600

    def update(self):
        """Count down and remove the zone once its lifespan ends."""
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()


class CommonSenseBoss(Boss):
    """Level 4 boss - mirrors the player's position and copies their attacks. 600 HP."""

    def __init__(self, x, y):
        super().__init__(x, y, max_hp=600)
        self.attack_damage = 20

    def update(self, player_rect):
        """Update bullets and mirror the player's position."""
        super().update(player_rect)

        self.rect.centerx = SCREEN_WIDTH - player_rect.centerx
        self.rect.centery = player_rect.centery

    def on_player_attack(self):
        """Called when player attacks to copy attack."""
        bullet = CommonSenseBossBullet(self.rect.centerx, self.rect.bottom)
        self.bullets.add(bullet)


class CommonSenseBossBullet(pygame.sprite.Sprite):
    """The boss's copied attack. 20 damage."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 12))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(midtop=(x, y))
        self.damage = 20

    def update(self):
        """Move the bullet downward."""
        self.rect.y += 4
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class PoisonBullet(pygame.sprite.Sprite):
    """Poison bullet fired by the Interest Rate boss. 13 damage."""

    def __init__(self, x, y, angle, speed=4):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((100, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = 13

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class InterestRateBoss(Boss):
    """Level 3 boss - growing snake body, fires poison bullet waves. 450 HP."""

    def __init__(self, x, y):
        super().__init__(x, y, max_hp=450)
        self.segments = [pygame.Rect(x, y, 40, 40)]
        self.max_segments = 6
        self.speed = 2
        self.positions = [(x, y)]
        self.move_timer = 0
        self.shoot_timer = 0
        self.grow_timer = 0

    def update(self, player_rect):
        """Move head toward player, trail segments behind, and fire poison waves."""
        self.bullets.update()

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

        self.positions.insert(0, self.rect.center)
        if len(self.positions) > 200:
            self.positions.pop()

        self._update_segments()

        self.shoot_timer += 1
        if self.shoot_timer >= 50:
            self.shoot_timer = 0
            self.shoot_wave(player_rect)

        self.grow_timer += 1
        if self.grow_timer >= 300 and len(self.segments) < self.max_segments:
            self.grow_timer = 0
            self.segments.append(pygame.Rect(self.rect.x, self.rect.y, 40, 40))
            self.speed += 0.3

    def _update_segments(self):
        """Place each segment along past positions."""
        spacing = 15
        for i, segment in enumerate(self.segments):
            pos_index = min((i + 1) * spacing, len(self.positions) - 1)
            segment.center = self.positions[pos_index]

    def shoot_wave(self, player_rect):
        """Fire a wave of poison bullets."""
        base_dx = player_rect.centerx - self.rect.centerx
        base_dy = player_rect.centery - self.rect.centery
        base_angle = math.atan2(base_dy, base_dx)

        for i in range(-2, 3):
            angle = base_angle + (i * 0.2)
            self.bullets.add(PoisonBullet(self.rect.centerx, self.rect.centery, angle))