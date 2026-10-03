import math
import random
import pygame


class FateWheel:
    SECTORS = [
        ("SPEED BOOST", "stat_multiplier", ("speed", 1.25)),
        ("Token PENALTY", "token_loss", 0.5),
        ("CARD UPGRADE", "card_upgrade", None),
        ("HEALTH BOOST", "stat_multiplier", ("max_health", 1.20)),
        ("Token PENALTY", "token_loss", 0.5),
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

        self.btn_rect = pygame.Rect(0, 0, 160, 50)
        self.anim_y = 0
        self.anim_alpha = 0
        self.show_anim = False
        self.anim_text = ""

    def open(self):
        self.active = True
        self.spinning = False
        self.result_index = None
        self.result_applied = False
        self.show_anim = False

    def close(self):
        self.active = False
        self.spinning = False

    def handle_click(self, mx, my):
        if not self.active: return

        if self.btn_rect.collidepoint(mx, my):
            if not self.spinning and self.result_index is None:
                self.start_spin()
            elif not self.spinning and self.result_index is not None:
                self.close()

    def start_spin(self):
        if not self.spinning:
            self.spinning = True
            self.result_applied = False
            self.show_anim = False
            self.angular_velocity = random.uniform(900, 1400)

    def update(self, dt):
        if self.show_anim:
            self.anim_y -= 40 * dt
            self.anim_alpha = max(0, self.anim_alpha - 100 * dt)

        if not self.spinning: return

        deceleration = 250
        self.angular_velocity = max(0.0, self.angular_velocity - deceleration * dt)
        self.angle = (self.angle + self.angular_velocity * dt) % 360

        if self.angular_velocity <= 0.0:
            self.spinning = False
            pointer_relative_angle = (360 - self.angle) % 360
            self.result_index = int(pointer_relative_angle // self.SECTOR_ANGLE)

            self.anim_text = self.SECTORS[self.result_index][0]
            self.anim_y = 200
            self.anim_alpha = 255
            self.show_anim = True

    def apply_result(self, player):
        if self.result_applied or self.result_index is None: return

        label, outcome_type, payload = self.SECTORS[self.result_index]

        if outcome_type == "token_loss":
            player.tokens = int(player.tokens * payload)
        elif outcome_type == "card_upgrade":
            if len(player.deck) < player.MAX_HAND_SIZE:
                player.deck.append(random.choice(["SPADE", "HEART", "CLUB", "DIAMOND"]))
        elif outcome_type == "stat_multiplier":
            stat_name, mult = payload
            if stat_name == "speed":
                player.speed = int(player.speed * mult)
            elif stat_name == "max_health":
                player.max_health = int(player.max_health * mult)
                player.health = min(player.max_health, player.health + 20)

        self.result_applied = True
        return label

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

            mid_deg = start_deg + (self.SECTOR_ANGLE / 2)
            rad_mid = math.radians(mid_deg)
            text_x = center[0] + (radius * 0.6) * math.sin(rad_mid)
            text_y = center[1] - (radius * 0.6) * math.cos(rad_mid)

            label_surf = pygame.font.SysFont("Arial", 12, bold=True).render(self.SECTORS[i][0][:10], True, (255, 255, 255))
            rot_surf = pygame.transform.rotate(label_surf, -mid_deg)
            screen.blit(rot_surf, rot_surf.get_rect(center=(text_x, text_y)))

        pygame.draw.circle(screen, (255, 255, 255), center, radius, 3)

        pygame.draw.polygon(screen, (255, 255, 255), [
            (center[0] - 12, center[1] - radius - 5),
            (center[0] + 12, center[1] - radius - 5),
            (center[0], center[1] - radius + 15),
        ])

        self.btn_rect.center = (center[0], center[1] + radius + 40)
        if self.result_index is not None:
            btn_color, btn_text = (200, 100, 0), "COLLECT"
        elif not self.spinning:
            btn_color, btn_text = (0, 150, 100), "SPIN!"
        else:
            btn_color, btn_text = (100, 100, 100), "SPINNING..."

        pygame.draw.rect(screen, btn_color, self.btn_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.btn_rect, 2, border_radius=10)
        t_surf = font.render(btn_text, True, (255, 255, 255))
        screen.blit(t_surf, t_surf.get_rect(center=self.btn_rect.center))

        if self.show_anim:
            anim_surf = font.render(self.anim_text, True, (255, 215, 0))
            anim_surf.set_alpha(int(self.anim_alpha))
            screen.blit(anim_surf, anim_surf.get_rect(center=(center[0], self.anim_y)))