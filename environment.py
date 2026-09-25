import pygame


class DungeonEnvironment:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Pre-render the floors so the game runs at a smooth 60 FPS
        self.floors = {}
        self.generate_floor_textures()

    def generate_floor_textures(self):
        for f in range(1, 5):
            surf = pygame.Surface((2000, 2000))

            # Base themes: 1=Stone, 2=Sewer, 3=Lava, 4=Neon
            if f == 1:
                bg_color, grid_color = (40, 40, 40), (20, 20, 20)
            elif f == 2:
                bg_color, grid_color = (10, 40, 10), (5, 20, 5)
            elif f == 3:
                bg_color, grid_color = (60, 10, 10), (30, 0, 0)
            else:
                bg_color, grid_color = (20, 10, 40), (40, 20, 80)

            surf.fill(bg_color)

            # Draw the detailed tiles
            tile_size = 100
            for x in range(0, 2000, tile_size):
                for y in range(0, 2000, tile_size):
                    # Tile borders
                    rect = pygame.Rect(x, y, tile_size, tile_size)
                    pygame.draw.rect(surf, grid_color, rect, 2)

                    # Add details based on the floor
                    if f == 1 and (x + y) % 300 == 0:
                        pygame.draw.circle(surf, (30, 30, 30), (x + 50, y + 50), 10)  # Rocks
                    elif f == 2 and (x + y) % 400 == 0:
                        pygame.draw.circle(surf, (0, 150, 0), (x + 50, y + 50), 15)  # Toxic Puddles
                    elif f == 3 and (x - y) % 400 == 0:
                        pygame.draw.line(surf, (200, 100, 0), (x, y), (x + tile_size, y + tile_size), 4)  # Magma Cracks
                    elif f == 4 and (x + y) % 200 == 0:
                        pygame.draw.rect(surf, (0, 255, 255), (x + 40, y + 40, 20, 20))  # Neon Nodes

            self.floors[f] = surf

    def draw_background(self, screen, floor, cam_x, cam_y):
        # Cap at floor 4 so it doesn't crash if they go higher
        safe_floor = min(floor, 4)
        screen.blit(self.floors[safe_floor], (-cam_x, -cam_y))

    def draw_custom_ui(self, screen, floor, font, health, max_health, tokens, minions_killed, minions_total,
                       boss_spawned):
        safe_floor = min(floor, 4)

        # Themed UI Panels
        if safe_floor == 1:
            ui_color, text_c = (50, 50, 50), (220, 220, 220)
        elif safe_floor == 2:
            ui_color, text_c = (15, 60, 15), (150, 255, 150)
        elif safe_floor == 3:
            ui_color, text_c = (80, 20, 20), (255, 150, 150)
        else:
            ui_color, text_c = (40, 15, 80), (220, 150, 255)

        # Draw UI Background Box
        ui_rect = pygame.Rect(10, 10, 280, 180)
        pygame.draw.rect(screen, ui_color, ui_rect, border_radius=10)
        pygame.draw.rect(screen, text_c, ui_rect, 3, border_radius=10)  # Border

        # Draw Text
        screen.blit(font.render(f"Floor {safe_floor} / 4", True, text_c), (25, 20))
        screen.blit(font.render(f"Health: {health}/{max_health}", True, text_c), (25, 60))
        screen.blit(font.render(f"Tokens: {tokens}", True, text_c), (25, 100))

        if not boss_spawned:
            screen.blit(font.render(f"Minions: {minions_killed}/{minions_total}", True, (255, 255, 255)), (25, 140))
        else:
            screen.blit(font.render("BOSS SPAWNED (B)", True, (255, 50, 50)), (25, 140))