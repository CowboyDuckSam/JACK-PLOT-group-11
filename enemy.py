import pygame
import math


class MeleeMinion(pygame.sprite.Sprite):
    def __init__(self, x, y, floor=1):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.max_hp = 20 + (floor * 10)
        self.hp = self.max_hp
        self.damage = 8 + (floor * 3)
        self.speed = 3 + (floor * 0.2)

        pygame.draw.rect(self.image, (255, 30, 100), (4, 8, 22, 22), border_radius=4)
        pygame.draw.polygon(self.image, (255, 200, 0), [(15, 0), (6, 8), (24, 8)])

    def take_damage(self, amount):
        self.hp -= amount

    def update(self, player_rect, enemy_bullets, dungeon_walls=None):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist != 0:
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed

            self.pos_x += move_x
            self.rect.x = int(self.pos_x)
            if dungeon_walls:
                for wall in dungeon_walls:
                    if self.rect.colliderect(wall):
                        if move_x > 0:
                            self.rect.right = wall.left
                        elif move_x < 0:
                            self.rect.left = wall.right
                        self.pos_x = self.rect.x

            self.pos_y += move_y
            self.rect.y = int(self.pos_y)
            if dungeon_walls:
                for wall in dungeon_walls:
                    if self.rect.colliderect(wall):
                        if move_y > 0:
                            self.rect.bottom = wall.top
                        elif move_y < 0:
                            self.rect.top = wall.bottom
                        self.pos_y = self.rect.y

        self.rect.clamp_ip(pygame.Rect(0, 0, 2000, 2000))
        self.pos_x, self.pos_y = self.rect.x, self.rect.y

    def draw(self, surface, cam_x=0, cam_y=0):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))


class RangedMinion(pygame.sprite.Sprite):
    def __init__(self, x, y, floor=1):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.max_hp = 20 + (floor * 5)
        self.hp = self.max_hp
        self.damage = 1 + int(floor * 0.5)
        self.speed = 1.5 + (floor * 0.1)
        self.shoot_cooldown = max(30, 90 - (floor * 5))
        self.timer = 0

        pygame.draw.circle(self.image, (0, 200, 255), (15, 15), 14)
        pygame.draw.circle(self.image, (255, 255, 255), (15, 15), 6)
        pygame.draw.circle(self.image, (0, 100, 200), (15, 15), 14, width=2)

    def take_damage(self, amount):
        self.hp -= amount

    def update(self, player_rect, enemy_bullets, dungeon_walls=None):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist != 0:
            move_x = (dx / dist) * self.speed
            move_y = (dy / dist) * self.speed

            self.pos_x += move_x
            self.rect.x = int(self.pos_x)
            if dungeon_walls:
                for wall in dungeon_walls:
                    if self.rect.colliderect(wall):
                        if move_x > 0:
                            self.rect.right = wall.left
                        elif move_x < 0:
                            self.rect.left = wall.right
                        self.pos_x = self.rect.x

            self.pos_y += move_y
            self.rect.y = int(self.pos_y)
            if dungeon_walls:
                for wall in dungeon_walls:
                    if self.rect.colliderect(wall):
                        if move_y > 0:
                            self.rect.bottom = wall.top
                        elif move_y < 0:
                            self.rect.top = wall.bottom
                        self.pos_y = self.rect.y

        self.rect.clamp_ip(pygame.Rect(0, 0, 2000, 2000))
        self.pos_x, self.pos_y = self.rect.x, self.rect.y

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

    def draw(self, surface, cam_x=0, cam_y=0):
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
        self.pos_x = float(x)
        self.pos_y = float(y)

    def update(self):
        self.pos_x += self.dx
        self.pos_y += self.dy
        self.rect.center = (int(self.pos_x), int(self.pos_y))
        self.lifetime -= 1

    def draw(self, surface, cam_x=0, cam_y=0):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))