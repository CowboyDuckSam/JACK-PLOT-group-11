import pygame


class Player:
    def __init__(self, x, y):
        self.surface = pygame.Surface((50, 50))
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

    def update(self, dt, keys, walls):
        old_x, old_y = self.pos_x, self.pos_y

        # 1. Movement Math
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.pos_x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.pos_x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.pos_y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.pos_y += self.speed * dt

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        # 2. Map Boundaries
        map_bounds = pygame.Rect(0, 0, 2000, 2000)
        self.rect.clamp_ip(map_bounds)
        self.pos_x, self.pos_y = float(self.rect.x), float(self.rect.y)

        # 3. Wall Collisions
        for wall in walls:
            if self.rect.colliderect(wall):
                self.pos_x, self.pos_y = old_x, old_y
                self.rect.x, self.rect.y = int(self.pos_x), int(self.pos_y)
                break
