from boss import PiggyBankWalletBoss, OverdueBillBoss, InterestRateBoss, CommonSenseBoss


class LevelManager:
    def __init__(self):
        self.rooms = ["SPAWN", "ENEMIES", "SHOP", "BOSS"]
        self.current_room_index = 0
        self.current_level = 1
        self.max_levels = 4

    def get_current_room(self):
        return self.rooms[self.current_room_index]

    def advance_room(self, boss_alive=True):
        """Advance to the next room, or advance level if boss is dead in BOSS room."""
        current_room = self.get_current_room()

        # Prevent leaving BOSS room if boss is still alive
        if current_room == "BOSS" and boss_alive:
            print("Defeat the boss before moving on!")
            return None

        # If in BOSS room and boss is dead, advance to next Level Spawn
        if current_room == "BOSS" and not boss_alive:
            if self.current_level < self.max_levels:
                self.current_level += 1
                self.current_room_index = 0
                print(f"--- LEVEL {self.current_level} STARTED ---")
                return self.spawn_boss_for_level()
            else:
                print("Game Completed! You beat all bosses!")
                return None

        # Standard room progression
        self.current_room_index = (self.current_room_index + 1) % len(self.rooms)
        print(f"Entering: {self.get_current_room()} Room (Level {self.current_level})")
        return None

    def spawn_boss_for_level(self):
        """Instantiate the correct boss object based on current level."""
        if self.current_level == 1:
            return PiggyBankWalletBoss(400, 100)
        elif self.current_level == 2:
            return OverdueBillBoss(400, 100)
        elif self.current_level == 3:
            return InterestRateBoss(400, 100)
        elif self.current_level == 4:
            return CommonSenseBoss(400, 100)
        return None