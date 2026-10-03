import pygame
import math

# Screen dimensions for bullet cleanup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class MeleeMinion(pygame.sprite.Sprite):
    """Close-range minion that chases the player closely."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 128))
        self.rect = self.image.get_rect(center=(x, y))

        self.hp = 20
        self.damage = 2
        self.speed = 3

    def update(self, player_rect, enemy_bullets):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

    # Added draw method for scrolling camera
    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))

class RangedMinion(pygame.sprite.Sprite):
    """Long-range minion that keeps distance and shoots."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 180, 255))
        self.rect = self.image.get_rect(center=(x, y))

        self.hp = 20
        self.damage = 1
        self.speed = 1
        self.shoot_cooldown = 90
        self.timer = 0

    def update(self, player_rect, enemy_bullets):
        """Move slowly toward the player and fire on a cooldown."""
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

        self.timer += 1
        if self.timer >= self.shoot_cooldown:
            self.shoot(player_rect, enemy_bullets)
            self.timer = 0

    def shoot(self, player_rect, enemy_bullets):
        """Fire a bullet toward the player's current position."""
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)

        bullet = EnemyBullet(self.rect.centerx, self.rect.centery, angle, speed=5, damage=self.damage)
        #Swapped .add() for .append() to support standard Python lists
        enemy_bullets.append(bullet)

    # Added draw method for scrolling camera
    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = damage
        self.lifetime = 120 # added lifetime tracker for main.py cleanup

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.lifetime -= 1 # decrement lifetime instead of static screen kill

    # Added draw method for scrolling camera
    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))