
import json
import os
import pygame

SAVE_FILE = "save_data.json"

class LoginManager:
    def __init__(self, font, width, height):
        self.font = font
        self.width = width
        self.height = height

        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = "Enter Username & Password (New names Auto-Register)"

        self.logged_in = False
        self.saved_data = None

        # Create the JSON file if there isn't one yet
        if not os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "w") as f:
                json.dump({}, f)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.attempt_login()
            elif event.key == pygame.K_TAB:

                # Swap between typing in Username and Password
                self.active_field = "password" if self.active_field == "username" else "username"

            elif event.key == pygame.K_BACKSPACE:
                if self.active_field == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]

            else:

                # type normal letters
                if event.unicode.isprintable() and len(event.unicode) > 0:
                    if self.active_field == "username":
                        self.username += event.unicode
                    else:
                        self.password += event.unicode

    def attempt_login(self):
        if self.username == "" or self.password == "":
            self.message = "Fields cannot be empty!"
            return

        with open(SAVE_FILE, "r") as f:
            users = json.load(f)


        if self.username in users:
            if users[self.username]["password"] == self.password:
                self.logged_in = True
                self.saved_data = users[self.username]

            else:
                self.message = "Incorrect Password!"
        else:
            new_account = {"password": self.password, "tokens": 0, "floor": 1}
            users[self.username] = new_account
            with open(SAVE_FILE, "w") as f:
                json.dump(users, f)
            self.logged_in = True
            self.saved_data = new_account

    def draw(self, screen):
        # Draw message
        msg_surf = self.font.render(self.message, True, (255, 255, 100))
        screen.blit(msg_surf, msg_surf.get_rect(center=(self.width // 2, self.height // 2 - 100)))

        # Draw username
        u_color = (100, 255, 100) if self.active_field == "username" else (150, 150, 150)
        u_surf = self.font.render(f"Username: {self.username}", True, u_color)
        screen.blit(u_surf, u_surf.get_rect(center=(self.width // 2, self.height // 2 - 20)))

        # Draw password
        p_color = (100, 255, 100) if self.active_field == "password" else (150, 150, 150)
        hidden_pass = "*" * len(self.password)
        p_surf = self.font.render(f"Password: {hidden_pass}", True, p_color)
        screen.blit(p_surf, p_surf.get_rect(center=(self.width // 2, self.height // 2 + 30)))

        # Instructions
        inst = self.font.render("Press TAB to switch fields | ENTER to Login", True, (200, 200, 200))
        screen.blit(inst, inst.get_rect(center=(self.width // 2, self.height // 2 + 120)))

