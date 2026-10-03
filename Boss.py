import pygame
import math
import random

WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, max_hp):
        super().__init__()
        self.max_hp = max_hp
        self.hp = max_hp
        self.image = pygame.Surface((80, 80))
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.phase = 1
        self.is_alive = True
        self.bullets = pygame.sprite.Group()

    def update(self, player_rect):
        self.bullets.update()

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def change_phase(self, new_phase):
        """Change boss phase."""
        self.phase = new_phase

    def draw_healthbar(self, surface, cam_x=0, cam_y=0):
        bar_width = 120
        bar_height = 10
        bar_x = (self.rect.centerx - cam_x) - (bar_width // 2)
        bar_y = (self.rect.top - cam_y) - 20

        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

    def draw(self, surface, cam_x=0, cam_y=0):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))
        for bullet in self.bullets:
            surface.blit(bullet.image, (bullet.rect.x - cam_x, bullet.rect.y - cam_y))


class NormalBossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed=5):
        super().__init__()
        self.image = pygame.Surface((12, 12))
        self.image.fill((255, 200, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = 10

    def update(self):
        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)
        if self.rect.right < 0 or self.rect.left > WORLD_WIDTH or self.rect.bottom < 0 or self.rect.top > WORLD_HEIGHT:
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

        self.piggy_rect = pygame.Rect(x - 70, y - 30, 60, 60)
        self.wallet_rect = pygame.Rect(x + 10, y - 30, 60, 60)

        self.piggy_image = pygame.Surface((60, 60))
        self.piggy_image.fill((255, 105, 180))

        self.wallet_image = pygame.Surface((60, 60))
        self.wallet_image.fill((139, 69, 19))

        self.shoot_timer = 0
        self.speed = 1.5

    def update(self, player_rect):
        self.bullets.update()

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 150:
            self.rect.x += int((dx / dist) * self.speed)
            self.rect.y += int((dy / dist) * self.speed)

        self.piggy_rect.center = (self.rect.centerx - 40, self.rect.centery)
        self.wallet_rect.center = (self.rect.centerx + 40, self.rect.centery)

        if self.laser_phase:
            self._update_laser_phase(player_rect)
            return

        self.shoot_timer += 1
        if self.shoot_timer >= 60:
            self.shoot_timer = 0
            self.shoot_dual(player_rect)

    def shoot_dual(self, player_rect):
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
        if not self.piggy_alive: return
        self.piggy_hp -= amount
        if self.piggy_hp <= 0:
            self.piggy_hp = 0
            self.piggy_alive = False
            self.laser_phase = True
            self.change_phase(2)
        self._sync_total_hp()

    def take_damage_wallet(self, amount):
        if not self.wallet_alive: return
        self.wallet_hp -= amount
        if self.wallet_hp <= 0:
            self.wallet_hp = 0
            self.wallet_alive = False
        self._sync_total_hp()

    def _sync_total_hp(self):
        self.hp = self.piggy_hp + self.wallet_hp
        if not self.piggy_alive and not self.wallet_alive:
            self.is_alive = False

    def _update_laser_phase(self, player_rect):
        self.shoot_timer += 1
        if self.shoot_timer >= 40:
            self.shoot_timer = 0
            if self.wallet_alive:
                angle = math.atan2(player_rect.centery - self.wallet_rect.centery, player_rect.centerx - self.wallet_rect.centerx)
                self.bullets.add(NormalBossBullet(self.wallet_rect.centerx, self.wallet_rect.centery, angle, speed=7))

    def draw(self, surface, cam_x=0, cam_y=0):
        if self.piggy_alive:
            surface.blit(self.piggy_image, (self.piggy_rect.x - cam_x, self.piggy_rect.y - cam_y))
        if self.wallet_alive:
            surface.blit(self.wallet_image, (self.wallet_rect.x - cam_x, self.wallet_rect.y - cam_y))
        for bullet in self.bullets:
            surface.blit(bullet.image, (bullet.rect.x - cam_x, bullet.rect.y - cam_y))


class OverdueBillBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=350)
        self.shoot_timer = 0
        self.debt_zones = pygame.sprite.Group()
        self.zone_timer = 0

    def update(self, player_rect):
        super().update(player_rect)
        self.debt_zones.update()

        self.shoot_timer += 1
        if self.shoot_timer >= 90:
            self.shoot_timer = 0
            self.shoot(player_rect)

        self.zone_timer += 1
        if self.zone_timer >= 180:
            self.zone_timer = 0
            self.spawn_debt_zone(player_rect)

    def shoot(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)
        bullet = OverdueBillBullet(self.rect.centerx, self.rect.centery, angle, speed=4)
        self.bullets.add(bullet)

    def spawn_debt_zone(self, player_rect):
        x = max(100, min(player_rect.centerx + random.randint(-150, 150), WORLD_WIDTH - 100))
        y = max(100, min(player_rect.centery + random.randint(-150, 150), WORLD_HEIGHT - 100))
        zone = DebtZone(x, y)
        self.debt_zones.add(zone)

    def draw(self, surface, cam_x=0, cam_y=0):
        for zone in self.debt_zones:
            surface.blit(zone.image, (zone.rect.x - cam_x, zone.rect.y - cam_y))
        super().draw(surface, cam_x, cam_y)


class OverdueBillBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = 20

    def update(self):
        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)
        if self.rect.right < 0 or self.rect.left > WORLD_WIDTH or self.rect.bottom < 0 or self.rect.top > WORLD_HEIGHT:
            self.kill()


class DebtZone(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.image.fill((60, 0, 90, 180))
        self.rect = self.image.get_rect(center=(x, y))
        self.damage_per_tick = 1
        self.lifespan = 600

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()


class CommonSenseBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=600)
        self.attack_damage = 20

    def update(self, player_rect):
        super().update(player_rect)
        self.rect.centerx = max(50, min(WORLD_WIDTH - player_rect.centerx, WORLD_WIDTH - 50))
        self.rect.centery = player_rect.centery

    def on_player_attack(self):
        bullet = CommonSenseBossBullet(self.rect.centerx, self.rect.bottom)
        self.bullets.add(bullet)


class CommonSenseBossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 14))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(midtop=(x, y))
        self.damage = 20

    def update(self):
        self.rect.y += 5
        if self.rect.top > WORLD_HEIGHT:
            self.kill()


class PoisonBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed=4):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((100, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = 13

    def update(self):
        self.rect.x += int(self.dx)
        self.rect.y += int(self.dy)
        if self.rect.right < 0 or self.rect.left > WORLD_WIDTH or self.rect.bottom < 0 or self.rect.top > WORLD_HEIGHT:
            self.kill()


class InterestRateBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=450)
        self.segments = [pygame.Rect(x, y, 40, 40)]
        self.max_segments = 6
        self.speed = 2
        self.positions = [(x, y)]
        self.shoot_timer = 0
        self.grow_timer = 0

    def update(self, player_rect):
        self.bullets.update()

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += int((dx / dist) * self.speed)
            self.rect.y += int((dy / dist) * self.speed)

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
        spacing = 15
        for i, segment in enumerate(self.segments):
            pos_index = min((i + 1) * spacing, len(self.positions) - 1)
            segment.center = self.positions[pos_index]

    def shoot_wave(self, player_rect):
        base_dx = player_rect.centerx - self.rect.centerx
        base_dy = player_rect.centery - self.rect.centery
        base_angle = math.atan2(base_dy, base_dx)

        for i in range(-2, 3):
            angle = base_angle + (i * 0.2)
            self.bullets.add(PoisonBullet(self.rect.centerx, self.rect.centery, angle))

    def draw(self, surface, cam_x=0, cam_y=0):
        for segment in self.segments:
            pygame.draw.rect(surface, (50, 180, 50), (segment.x - cam_x, segment.y - cam_y, segment.width, segment.height))
        super().draw(surface, cam_x, cam_y)