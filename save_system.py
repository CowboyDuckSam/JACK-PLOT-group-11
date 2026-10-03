import json
import os
import pygame
import base64

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

        self._ensure_save_file()

    def _ensure_save_file(self):
        if not os.path.exists(SAVE_FILE):
            self._write_save({})
        else:
            try:
                self._read_save()
            except (json.JSONDecodeError, ValueError):
                print("Save file corrupted. Creating a new safe backup.")
                self._write_save({})

    def _read_save(self):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)

    def _write_save(self, data):
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def _encode(self, text):
        return base64.b64encode(text.encode()).decode()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.attempt_login()
            elif event.key == pygame.K_TAB:
                self.active_field = "password" if self.active_field == "username" else "username"
            elif event.key == pygame.K_BACKSPACE:
                if self.active_field == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]
            else:
                if event.unicode.isprintable() and len(event.unicode) > 0:
                    if self.active_field == "username":
                        self.username += event.unicode
                    else:
                        self.password += event.unicode

    def attempt_login(self):
        if self.username == "" or self.password == "":
            self.message = "Fields cannot be empty!"
            return

        users = self._read_save()
        encoded_pass = self._encode(self.password)

        if self.username in users:
            if users[self.username].get("password") == encoded_pass:
                self.logged_in = True
                self.saved_data = users[self.username]
            else:
                self.message = "Incorrect Password!"
        else:
            new_account = {"password": encoded_pass, "tokens": 0, "floor": 1, "max_health": 100, "health": 100}
            users[self.username] = new_account
            self._write_save(users)
            self.logged_in = True
            self.saved_data = new_account

    def draw(self, screen):
        msg_surf = self.font.render(self.message, True, (255, 255, 100))
        screen.blit(msg_surf, msg_surf.get_rect(center=(self.width // 2, self.height // 2 - 100)))

        u_color = (100, 255, 100) if self.active_field == "username" else (150, 150, 150)
        u_surf = self.font.render(f"Username: {self.username}", True, u_color)
        screen.blit(u_surf, u_surf.get_rect(center=(self.width // 2, self.height // 2 - 20)))

        p_color = (100, 255, 100) if self.active_field == "password" else (150, 150, 150)
        hidden_pass = "*" * len(self.password)
        p_surf = self.font.render(f"Password: {hidden_pass}", True, p_color)
        screen.blit(p_surf, p_surf.get_rect(center=(self.width // 2, self.height // 2 + 30)))

        inst = self.font.render("Press TAB to switch fields | ENTER to Login", True, (200, 200, 200))
        screen.blit(inst, inst.get_rect(center=(self.width // 2, self.height // 2 + 120)))

    def save_progress(self, player, floor, is_death=False):
        if not self.logged_in: return

        users = self._read_save()

        users[self.username]["tokens"] = player.tokens

        if not is_death:
            users[self.username]["floor"] = max(users[self.username].get("floor", 1), floor)

        users[self.username]["max_health"] = player.max_health
        users[self.username]["health"] = 100 if is_death else player.health

        self._write_save(users)
        print("Checkpoint Auto-Saved!")