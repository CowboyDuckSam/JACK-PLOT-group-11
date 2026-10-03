import pygame
import math


class Player:
    def __init__(self, x, y):
        self.surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.surface.fill((0, 255, 150))
        self.rect = self.surface.get_rect(center=(x, y))

        self.speed = 300
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

        # Stats and Inventory
        self.max_health = 100
        self.health = 100
        self.tokens = 0
        self.wheel_spins_available = 1
        self.deck = []
        self.MAX_HAND_SIZE = 5

        # Combat Mechanics & i-Frames
        self.angle = 0.0
        self.shield_hp = 0
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_dir = pygame.math.Vector2(0, 0)
        self.dash_speed = 1000
        self.i_frames = 0.0

    def update(self, dt, keys, walls, mouse_pos, cam_x, cam_y):
        if self.i_frames > 0:
            self.i_frames -= dt

        # Aiming calculation based on camera offset
        world_mouse_x = mouse_pos[0] + cam_x
        world_mouse_y = mouse_pos[1] + cam_y
        dx = world_mouse_x - self.rect.centerx
        dy = world_mouse_y - self.rect.centery
        self.angle = math.degrees(math.atan2(dy, dx))

        old_x, old_y = self.pos_x, self.pos_y

        # Movement & Dashing
        if self.is_dashing:
            self.pos_x += self.dash_dir.x * self.dash_speed * dt
            self.pos_y += self.dash_dir.y * self.dash_speed * dt
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            move_vec = pygame.math.Vector2(0, 0)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_vec.x -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_vec.x += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]: move_vec.y -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: move_vec.y += 1

            if move_vec.length_squared() > 0:
                move_vec = move_vec.normalize()
                self.pos_x += move_vec.x * self.speed * dt
                self.pos_y += move_vec.y * self.speed * dt

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        # Map Boundaries
        map_bounds = pygame.Rect(0, 0, 2000, 2000)
        self.rect.clamp_ip(map_bounds)
        self.pos_x, self.pos_y = float(self.rect.x), float(self.rect.y)

        # Wall Collisions
        for wall in walls:
            if self.rect.colliderect(wall):
                self.pos_x, self.pos_y = old_x, old_y
                self.rect.x, self.rect.y = int(self.pos_x), int(self.pos_y)
                break

    def take_damage(self, amount):
        if self.i_frames > 0:
            return False

        if self.shield_hp > 0:
            self.shield_hp -= amount
            if self.shield_hp < 0:
                self.health += self.shield_hp
                self.shield_hp = 0
        else:
            self.health -= amount

        self.i_frames = 0.5  # half second invincibility
        return True

    def use_diamond_dash(self, keys):
        if self.is_dashing: return
        move_vec = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_vec.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_vec.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: move_vec.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: move_vec.y += 1

        if move_vec.length_squared() > 0:
            self.dash_dir = move_vec.normalize()
        else:
            rad = math.radians(self.angle)
            self.dash_dir = pygame.math.Vector2(math.cos(rad), math.sin(rad))

        self.is_dashing = True
        self.dash_timer = 0.2

    def use_heart_shield(self):
        self.shield_hp = 20

    def draw_extras(self, surface, offset_rect):
        rad = math.radians(self.angle)
        end_x = offset_rect.centerx + math.cos(rad) * 35
        end_y = offset_rect.centery + math.sin(rad) * 35
        pygame.draw.line(surface, (0, 0, 0), offset_rect.center, (end_x, end_y), 4)

        if self.shield_hp > 0:
            pygame.draw.circle(surface, (255, 100, 150), offset_rect.center, 35, width=3)