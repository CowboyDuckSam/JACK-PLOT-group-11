import pygame
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class MeleeMinion(pygame.sprite.Sprite):
    """Close-range minion with spikes that chases the player closely."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        self.hp = 20
        self.damage = 2
        self.speed = 3
        
        # Red/Pink body with aggressive top spike
        pygame.draw.rect(self.image, (255, 30, 100), (4, 8, 22, 22), border_radius=4)
        pygame.draw.polygon(self.image, (255, 200, 0), [(15, 0), (6, 8), (24, 8)]) # Spiky horn

    def update(self, player_rect, enemy_bullets, dungeon_walls=None):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist != 0:
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed

            # Axis-aligned wall collision checks
            self.rect.x += move_x
            if dungeon_walls:
                for wall in dungeon_walls:
                    if self.rect.colliderect(wall):
                        if move_x > 0: self.rect.right = wall.left
                        elif move_x < 0: self.rect.left = wall.right

            self.rect.y += move_y
            if dungeon_walls:
                for wall in dungeon_walls:
                    if self.rect.colliderect(wall):
                        if move_y > 0: self.rect.bottom = wall.top
                        elif move_y < 0: self.rect.top = wall.bottom

    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))


class RangedMinion(pygame.sprite.Sprite):
    """Long-range minion with styled core and turret look that shoots on cooldown."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        self.hp = 20
        self.damage = 1
        self.speed = 1.5
        self.shoot_cooldown = 90
        self.timer = 0

        # Turquoise body with central firing orb
        pygame.draw.circle(self.image, (0, 200, 255), (15, 15), 14)
        pygame.draw.circle(self.image, (255, 255, 255), (15, 15), 6)
        pygame.draw.circle(self.image, (0, 100, 200), (15, 15), 14, width=2)

    def update(self, player_rect, enemy_bullets, dungeon_walls=None):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        
        if dist != 0:
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed

            # Axis-aligned wall collision checks
            self.rect.x += move_x
            if dungeon_walls:
                for wall in dungeon_walls:
                    if self.rect.colliderect(wall):
                        if move_x > 0: self.rect.right = wall.left
                        elif move_x < 0: self.rect.left = wall.right

            self.rect.y += move_y
            if dungeon_walls:
                for wall in dungeon_walls:
                    if self.rect.colliderect(wall):
                        if move_y > 0: self.rect.bottom = wall.top
                        elif move_y < 0: self.rect.top = wall.bottom

        self.timer += 1
        if self.timer >= self.shoot_cooldown:
            self.shoot(player_rect, enemy_bullets)
            self.timer = 0

    def shoot(self, player_rect, enemy_bullets):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        angle = math.atan2(dy, dx)

        bullet = EnemyBullet(self.rect.centerx, self.rect.centery, angle, speed=5, damage=self.damage)
        enemy_bullets.append(bullet)

    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 220, 0), (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.damage = damage
        self.lifetime = 120

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.lifetime -= 1

    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))