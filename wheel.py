# this is for the Wheel

import math
import random
import pygame

class FateWheel:
    SECTORS = [
        ("SPEED BOOST", "stat_multiplier", ("speed", 1.5, 8.0)),
        ("Token LOSS", "token_loss", None),
        ("CARD UPGRADE", "card_upgrade", None),
        ("HEALTH BOOST", "stat_multiplier", ("max_health", 1.2, 8.0)),
        ("Token LOSS", "token_loss", None),
        ("CARD UPGRADE", "card_upgrade", None),
    ]
    SECTOR_ANGLE = 360 / len(SECTORS)

    def __init__(self):
        self.active = False
        self.spinning = False
        self.angle = 0.0
        self.angular_velocity = 0.0
        self.result_index = None
        self.result_applied = False

    def open(self):
        self.active = True
        self.spinning = False
        self.result_index = None
        self.result_applied = False

    def close(self):
        self.active = False
        self.spinning = False

    def start_spin(self):
        if not self.spinning:
            self.spinning = True
            self.result_applied = False
            self.angular_velocity = random.uniform(900, 1400)

    def update(self, dt):
        if not self.spinning: return

        deceleration = 250
        self.angular_velocity = max(0.0, self.angular_velocity - deceleration * dt)
        self.angle = (self.angle + self.angular_velocity * dt) % 360

        if self.angular_velocity <= 0.0:
            self.spinning = False
            pointer_relative_angle = (360 - self.angle) % 360
            self.result_index = int(pointer_relative_angle // self.SECTOR_ANGLE)

    def apply_result(self, player_tokens, player_deck):
            if self.result_applied or self.result_index is None: return

            label, outcome_type, payload = self.SECTORS[self.result_index]

            if outcome_type == "token_loss":
                player_tokens = 0

            elif outcome_type == "card_upgrade":
                if len(player_deck) < 5:
                    player_deck.append(random.choice(["SPADE", "HEART", "CLUB", "DIAMOND"]))

            self.result_applied = True
            return label, player_tokens

    def draw(self, screen, font):
            if not self.active: return

            center = (screen.get_width() // 2, screen.get_height() // 2)
            radius = 120

            dim = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 160))
            screen.blit(dim, (0, 0))

            colors = [(220, 60, 60), (60, 140, 220), (230, 200, 60),
                      (80, 200, 120), (60, 140, 220), (230, 200, 60)]

            for i in range(len(self.SECTORS)):
                start_deg = self.angle + i * self.SECTOR_ANGLE
                end_deg = start_deg + self.SECTOR_ANGLE
                points = [center]
                for s in range(11):
                    deg = math.radians(start_deg + (end_deg - start_deg) * s / 10)
                    points.append((center[0] + radius * math.sin(deg), center[1] - radius * math.cos(deg)))
                pygame.draw.polygon(screen, colors[i % len(colors)], points)

            pygame.draw.circle(screen, (255, 255, 255), center, radius, 3)

            pygame.draw.polygon(screen, (255, 255, 255), [
                (center[0] - 12, center[1] - radius - 5),
                (center[0] + 12, center[1] - radius - 5),
                (center[0], center[1] - radius + 15),
                ])



