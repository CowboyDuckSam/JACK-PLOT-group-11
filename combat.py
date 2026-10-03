import pygame
import math
import random

COLOR_SPADE = (180, 70, 255)
COLOR_CLUB = (50, 220, 120)
COLOR_LASER = (0, 255, 255)
COLOR_TOKEN_OUTER = (140, 20, 220)
COLOR_TOKEN_INNER = (255, 215, 0)


class SpadeProjectile:
    """Ranged arrow shot dealing 20 damage."""
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 12
        self.damage = 20  # Spade = 20 Damage
        self.lifetime = 60

        rad = math.radians(self.angle)
        self.dx = math.cos(rad) * self.speed
        self.dy = math.sin(rad) * self.speed

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, surface, cam_x=0, cam_y=0):
        rad = math.radians(self.angle)
        draw_x, draw_y = self.x - cam_x, self.y - cam_y
        tip = (draw_x + math.cos(rad) * 15, draw_y + math.sin(rad) * 15)
        left = (draw_x + math.cos(rad + 2.4) * 10, draw_y + math.sin(rad + 2.4) * 10)
        base = (draw_x - math.cos(rad) * 5, draw_y - math.sin(rad) * 5)
        right = (draw_x + math.cos(rad - 2.4) * 10, draw_y - math.sin(rad - 2.4) * 10)
        pygame.draw.polygon(surface, COLOR_SPADE, [tip, left, base, right])


class ClubSlash:
    """Triangle melee slash arc dealing 15 damage."""
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = 15  # Club = 15 Damage
        self.lifetime = 10
        self.reach = 65
        self.spread = 0.6

    def update(self):
        self.lifetime -= 1

    def draw(self, surface, cam_x=0, cam_y=0):
        rad = math.radians(self.angle)
        draw_x, draw_y = self.x - cam_x, self.y - cam_y
        origin = (draw_x, draw_y)
        left_pt = (draw_x + math.cos(rad - self.spread) * self.reach, draw_y + math.sin(rad - self.spread) * self.reach)
        right_pt = (draw_x + math.cos(rad + self.spread) * self.reach, draw_y + math.sin(rad + self.spread) * self.reach)
        pygame.draw.polygon(surface, COLOR_CLUB, [origin, left_pt, right_pt])


class LaserBeam:
    """Continuous laser beam combo."""
    def __init__(self, player):
        self.player = player
        self.lifetime = 120
        self.beam_length = 800

    def update(self):
        self.lifetime -= 1

    def draw(self, surface, cam_x=0, cam_y=0):
        rad = math.radians(self.player.angle)
        start_x = self.player.rect.centerx - cam_x
        start_y = self.player.rect.centery - cam_y
        end_x = start_x + math.cos(rad) * self.beam_length
        end_y = start_y + math.sin(rad) * self.beam_length

        pygame.draw.line(surface, COLOR_LASER, (start_x, start_y), (end_x, end_y), 18)
        pygame.draw.line(surface, (255, 255, 255), (start_x, start_y), (end_x, end_y), 6)


class Token:
    """Gambling chip token with magnetic attraction."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.friction = 0.88
        self.magnet_distance = 150
        self.magnet_speed = 0.8

    def update(self, player_rect):
        dx = player_rect.centerx - self.x
        dy = player_rect.centery - self.y
        dist = math.hypot(dx, dy)

        if 0 < dist < self.magnet_distance:
            self.vx += (dx / dist) * self.magnet_speed
            self.vy += (dy / dist) * self.magnet_speed
        else:
            self.vx *= self.friction
            self.vy *= self.friction

        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface, cam_x=0, cam_y=0):
        pos = (int(self.x - cam_x), int(self.y - cam_y))
        pygame.draw.circle(surface, COLOR_TOKEN_OUTER, pos, self.radius)
        pygame.draw.circle(surface, COLOR_TOKEN_INNER, pos, self.radius - 3)
        pygame.draw.circle(surface, COLOR_TOKEN_OUTER, pos, 2)