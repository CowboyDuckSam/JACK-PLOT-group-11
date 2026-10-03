import pygame


class NeonShop:
    def __init__(self, font, width, height):
        self.font = font
        self.width = width
        self.height = height
        self.message = "Spend your tokens to upgrade Jack!"

        # Button Hitboxes (Rectangles)
        self.btn_heal = pygame.Rect(width // 2 - 250, 200, 200, 80)
        self.btn_max_hp = pygame.Rect(width // 2 + 50, 200, 200, 80)
        self.btn_next = pygame.Rect(width // 2 - 100, 400, 200, 60)

    def draw(self, screen, player):
        # Draw Title & Message
        title = self.font.render("--- NEON SHOP ---", True, (0, 255, 255))
        screen.blit(title, title.get_rect(center=(self.width // 2, 50)))

        msg = self.font.render(self.message, True, (255, 0, 255))
        screen.blit(msg, msg.get_rect(center=(self.width // 2, 100)))

        # Tokens Display
        tok = self.font.render(f"Your Tokens: {player.tokens}", True, (255, 215, 0))
        screen.blit(tok, tok.get_rect(center=(self.width // 2, 150)))

        # Heal Button (Neon Green)
        pygame.draw.rect(screen, (0, 100, 0), self.btn_heal, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 0), self.btn_heal, 3, border_radius=10)
        screen.blit(self.font.render("+20 HP", True, (255, 255, 255)), (self.btn_heal.x + 45, self.btn_heal.y + 10))
        screen.blit(self.font.render("15 Tokens", True, (150, 255, 150)), (self.btn_heal.x + 30, self.btn_heal.y + 45))

        # Max HP Button (Neon Pink)
        pygame.draw.rect(screen, (100, 0, 50), self.btn_max_hp, border_radius=10)
        pygame.draw.rect(screen, (255, 105, 180), self.btn_max_hp, 3, border_radius=10)
        screen.blit(self.font.render("+10 Max HP", True, (255, 255, 255)),
                    (self.btn_max_hp.x + 20, self.btn_max_hp.y + 10))
        screen.blit(self.font.render("30 Tokens", True, (255, 150, 200)),
                    (self.btn_max_hp.x + 30, self.btn_max_hp.y + 45))

        # Next Floor Button (Neon Blue)
        pygame.draw.rect(screen, (0, 50, 100), self.btn_next, border_radius=10)
        pygame.draw.rect(screen, (0, 200, 255), self.btn_next, 3, border_radius=10)
        screen.blit(self.font.render("Next Floor ->", True, (255, 255, 255)),
                    (self.btn_next.x + 20, self.btn_next.y + 10))

    def handle_click(self, mx, my, player):
        # Check Heal Button (+20 HP Healing)
        if self.btn_heal.collidepoint(mx, my):
            if player.tokens >= 15:
                if player.health < player.max_health:
                    player.tokens -= 15
                    player.health = min(player.health + 20, player.max_health)
                    self.message = "Healed 20 HP!"
                else:
                    self.message = "Health is already full!"
            else:
                self.message = "Not enough tokens!"

        # Check Max HP Button (Increases pool ceiling + grants extra health bonus)
        elif self.btn_max_hp.collidepoint(mx, my):
            if player.tokens >= 30:
                player.tokens -= 30
                player.max_health += 10
                player.health += 10  # Expands current health pool alongside the maximum ceiling
                self.message = "Max Health Increased!"
            else:
                self.message = "Not enough tokens!"

        # Check Next Floor Button
        elif self.btn_next.collidepoint(mx, my):
            self.message = "Spend your tokens to upgrade Jack!"
            return "NEXT_FLOOR"

        return None