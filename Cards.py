import pygame
from sys import exit
import random  # Needed for choosing random cards

# 1. Initialize Pygame & Setup Window
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.displaay.set_caption("JACK PLOT!!!")
clock = pygame.time.Clock()

# Create a font for rendering text on the screen
font = pygame.font.Font(None, 40)

# 2. Card Game State Variables
card_pool = ["Spade", "Clove", "Heart", "Diamond"]
equipped_cards = []  # List to hold currently equipped cards (Max 4)

# 3. Create a Custom Timer Event
# USEREVENT + 1 avoids conflicts with internal Pygame events
CARD_SPAWN_EVENT = pygame.USEREVENT + 1  
# Trigger CARD_SPAWN_EVENT every 500 milliseconds (0.5 seconds)
pygame.time.set_timer(CARD_SPAWN_EVENT, 500)  

while True:
    # --- EVENT LOOP (Inputs & Timers) ---
    for event in pygame.event.get():
        # Handle closing the window cleanly
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        # Handle Card Spawning Timer
        if event.type == CARD_SPAWN_EVENT:
            if len(equipped_cards) < 4:
                # Randomly choose a card and add it to our hand
                new_card = random.choice(card_pool)
                equipped_cards.append(new_card)
                print(f"Generated: {new_card} | Current Hand: {equipped_cards}")
            else:
                print("Hand is full! Cannot equip more cards.")

        # Keyboard Input: Press SPACE to use/discard the first card
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if len(equipped_cards) > 0:
                    removed_card = equipped_cards.pop(0)  # Remove the oldest card
                    print(f"Used: {removed_card} | Current Hand: {equipped_cards}")

    # --- DRAWING / RENDERING ---
    # Wipe the screen with a clean dark gray background
    screen.fill((40, 40, 40))

    # Render Instructions Text
    instr_surf = font.render("Press SPACE to use/discard the oldest card", True, "White")
    screen.blit(instr_surf, (80, 50))

    # Render Current Inventory Header
    hand_count_text = f"Equipped Cards ({len(equipped_cards)}/4):"
    header_surf = font.render(hand_count_text, True, "Light Gray")
    screen.blit(header_surf, (80, 150))

    # Render each card horizontally across the screen
    for index, card in enumerate(equipped_cards):
        # Choose card color based on type
        text_color = "Red" if card in ["Heart", "Diamond"] else "Black"
        
        # Create a card label surface
        card_surf = font.render(card, True, text_color)
        
        # Create a visual box background for each card
        card_rect = pygame.Rect(80 + (index * 170), 200, 140, 80)
        pygame.draw.rect(screen, "White", card_rect, border_radius=10)
        pygame.draw.rect(screen, "Dark Gray", card_rect, width=3, border_radius=10)
        
        # Draw the card text in the center of its box
        text_rect = card_surf.get_rect(center=card_rect.center)
        screen.blit(card_surf, text_rect)

    # Update display and cap frame rate to 60 FPS
    pygame.display.update()
    clock.tick(60)