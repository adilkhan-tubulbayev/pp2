import pygame
import random
import time
import os

# Keep these equal to the window size in main.py.
W, H = 500, 700
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")
SOUND_DIR = os.path.join(ASSET_DIR, "sounds")
FINISH_DISTANCE = 3000 * 100

# Settings store color names, pygame needs RGB values.
CAR_COLORS = {
    "blue":  (50, 100, 220),
    "red":   (220, 50, 50),
    "green": (50, 200, 80),
}

# Difficulty changes how crowded the road becomes.
DIFF_SETTINGS = {
    "easy":   {"obstacle_rate": 0.003, "powerup_rate": 0.004, "max_enemies": 4},
    "normal": {"obstacle_rate": 0.006, "powerup_rate": 0.003, "max_enemies": 5},
    "hard":   {"obstacle_rate": 0.010, "powerup_rate": 0.002, "max_enemies": 6},
}


class Game:
    """One playable racer session."""

    def __init__(self, screen, clock, settings, username):
        self.screen   = screen
        self.clock    = clock
        self.settings = settings
        self.username = username
        self.sound_on = settings.get("sound", False)
        if self.sound_on and not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error:
                self.sound_on = False
        self.sounds = self._load_sounds()

        self.font       = pygame.font.SysFont("Verdana", 20)
        self.font_small = pygame.font.SysFont("Verdana", 16)

        # If the PNG files are missing, the game still runs with drawn rectangles.
        self.player_img = self._load_car_img("Player.png", 45, 75,
                                             CAR_COLORS[settings.get("car_color", "blue")])
        self.enemy_img  = self._load_car_img("Enemy.png",  45, 75, (200, 50, 50))

        self.reset()

    def _load_car_img(self, path, w, h, fallback_color):
        """Load a car image from assets, or create a small fallback car."""
        try:
            img = pygame.image.load(os.path.join(ASSET_DIR, path)).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except Exception:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(surf, fallback_color, (0, 0, w, h), border_radius=6)
            pygame.draw.rect(surf, (200, 200, 200), (5, 5, w - 10, 20))
            return surf

    def _load_sounds(self):
        """Load short sound effects when sound is enabled in settings."""
        if not self.sound_on or not pygame.mixer.get_init():
            return {}

        sounds = {}
        for name in ("coin", "powerup", "crash", "finish"):
            path = os.path.join(SOUND_DIR, f"{name}.wav")
            try:
                sounds[name] = pygame.mixer.Sound(path)
            except pygame.error:
                pass
        return sounds

    def _play_sound(self, name):
        if self.sound_on and name in self.sounds:
            self.sounds[name].play()

    def reset(self):
        # The player starts low enough to have time to react.
        self.player = self.player_img.get_rect(center=(W // 2, H - 100))

        self.enemies = [self._spawn_enemy() for _ in range(2)]
        self.coins = [self._spawn_coin() for _ in range(3)]

        self.obstacles = []
        self.powerups  = []

        self.score       = 0
        self.coins_total = 0
        self.distance    = 0
        self.powerup_bonus = 0

        # base_speed grows slowly, enemy_speed also jumps after enough coins.
        self.base_speed  = 5
        self.enemy_speed = 5

        self.active_powerup = None
        self.shield_active  = False
        self.oil_end        = 0

        self.diff = DIFF_SETTINGS[self.settings.get("difficulty", "normal")]

    def _spawn_enemy(self):
        """Put an enemy above the road so it drives into view."""
        return self.enemy_img.get_rect(
            center=(random.randint(60, W - 60),
                    random.randint(-300, -60))
        )

    def _spawn_coin(self):
        """
        Create a coin with weighted rarity.
        Purple gives more points but appears less often.
        """
        types = [
            {"value": 1, "color": (255, 220, 0),  "r": 14},  # gold
            {"value": 3, "color": (255, 140, 0),  "r": 11},  # orange
            {"value": 5, "color": (180, 50, 255), "r": 8},   # purple
        ]
        t = random.choices(types, weights=[6, 3, 1])[0]
        return {
            "x": random.randint(50, W - 50),
            "y": float(random.randint(-400, -50)),
            "value": t["value"],
            "color": t["color"],
            "r": t["r"],
        }

    def _spawn_obstacle(self):
        """
        Create a road object.
        Some are bad, and nitro is useful if the player touches it.
        """
        otype = random.choices(
            ['oil', 'barrier', 'bump', 'nitro'],
            weights=[4, 2, 3, 2]
        )[0]
        colors = {
            'oil':     (60,  60,  60),
            'barrier': (200, 30,  30),
            'bump':    (220, 140, 0),
            'nitro':   (30,  100, 220),
        }
        sizes = {
            'oil':     (60, 25),
            'barrier': (80, 20),
            'bump':    (70, 15),
            'nitro':   (70, 15),
        }
        w, h = sizes[otype]
        rect = pygame.Rect(random.randint(30, W - 30 - w), -h, w, h)
        return {"rect": rect, "type": otype, "color": colors[otype]}

    def _spawn_powerup(self):
        """
        Create a floating bonus.
        spawn_time is used to remove it if the player ignores it.
        """
        ptype = random.choice(['nitro', 'shield', 'repair'])
        colors = {
            'nitro':  (0,   220, 255),
            'shield': (0,   255, 100),
            'repair': (255, 200, 0),
        }
        rect = pygame.Rect(random.randint(50, W - 70), -40, 40, 40)
        return {
            "rect": rect,
            "type": ptype,
            "color": colors[ptype],
            "spawn_time": time.time(),
        }

    def _current_obstacle_rate(self):
        """The road gets busier the longer the player survives."""
        extra_rate = min(0.012, self.distance / 100000 * 0.001)
        return self.diff["obstacle_rate"] + extra_rate

    def _current_score(self):
        return self.score * 10 + self.distance // 100 + self.coins_total * 5 + self.powerup_bonus

    def run(self):
        """
        Runs until crash, finish distance, or Escape.
        Returning None means the user left the game from the keyboard.
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None

            keys = pygame.key.get_pressed()

            # Oil and nitro change only the player's horizontal movement.
            if self.active_powerup and self.active_powerup["type"] == "nitro":
                spd = 12
            elif time.time() < self.oil_end:
                spd = 2
            else:
                spd = 6

            if keys[pygame.K_LEFT]  and self.player.left  > 0: self.player.move_ip(-spd, 0)
            if keys[pygame.K_RIGHT] and self.player.right < W:  self.player.move_ip( spd, 0)

            current_speed = self.enemy_speed

            self.distance += current_speed
            if self.distance >= FINISH_DISTANCE:
                self._play_sound("finish")
                return self._build_result()

            for e in self.enemies:
                e.move_ip(0, current_speed)

                # Passing an enemy counts as a dodge.
                if e.top > H:
                    self.score += 1
                    e.topleft = self._spawn_enemy().topleft

                    # More enemies appear later, but difficulty sets the cap.
                    if self.score % 10 == 0 and len(self.enemies) < self.diff["max_enemies"]:
                        self.enemies.append(self._spawn_enemy())

                if e.colliderect(self.player):
                    if self.shield_active:
                        self.shield_active = False
                        e.topleft = self._spawn_enemy().topleft
                    else:
                        self._play_sound("crash")
                        return self._build_result()

            for c in self.coins:
                c["y"] += current_speed

                if c["y"] > H + 30:
                    c.update(self._spawn_coin())
                    continue

                # Circles do not have colliderect, so use a small square hitbox.
                r = c["r"]
                crect = pygame.Rect(c["x"] - r, int(c["y"]) - r, r * 2, r * 2)

                if self.player.colliderect(crect):
                    old_total = self.coins_total
                    self.coins_total += c["value"]

                    # Coin milestones make enemies faster.
                    if self.coins_total // 5 > old_total // 5:
                        self.enemy_speed += 1

                    self._play_sound("coin")
                    c.update(self._spawn_coin())

            if random.random() < self._current_obstacle_rate():
                self.obstacles.append(self._spawn_obstacle())

            for obs in self.obstacles[:]:
                obs["rect"].move_ip(0, current_speed)

                if obs["rect"].top > H:
                    self.obstacles.remove(obs)
                    continue

                if obs["rect"].colliderect(self.player):
                    otype = obs["type"]
                    if otype == "barrier":
                        if self.shield_active:
                            self.shield_active = False
                        else:
                            self._play_sound("crash")
                            return self._build_result()
                    elif otype == "oil":
                        self.oil_end = time.time() + 2
                    elif otype == "bump":
                        self.oil_end = time.time() + 0.5
                    elif otype == "nitro":
                        self.active_powerup = {"type": "nitro", "end_time": time.time() + 3}
                    self.obstacles.remove(obs)

            # Keep only one visible bonus so the road stays readable.
            if (random.random() < self.diff["powerup_rate"] and
                    len(self.powerups) == 0 and
                    self.active_powerup is None and
                    not self.shield_active):
                self.powerups.append(self._spawn_powerup())

            for pw in self.powerups[:]:
                pw["rect"].move_ip(0, current_speed)

                # Bonuses disappear if the player ignores them.
                if pw["rect"].top > H or time.time() - pw["spawn_time"] > 8:
                    self.powerups.remove(pw)
                    continue

                if pw["rect"].colliderect(self.player):
                    ptype = pw["type"]
                    if ptype == "nitro":
                        self.active_powerup = {"type": "nitro", "end_time": time.time() + 4}
                        self.powerup_bonus += 20
                    elif ptype == "shield":
                        self.shield_active = True
                        self.powerup_bonus += 10
                    elif ptype == "repair":
                        self.oil_end = 0
                        self.powerup_bonus += 10
                    self._play_sound("powerup")
                    self.powerups.remove(pw)

            if self.active_powerup and time.time() > self.active_powerup["end_time"]:
                self.active_powerup = None

            # The road slowly speeds up even without coin collection.
            self.base_speed  += 0.001
            self.enemy_speed = max(self.enemy_speed, int(self.base_speed))

            self._draw()
            self.clock.tick(60)

    def _build_result(self):
        """Package the end-of-game statistics into a dict."""
        return {
            "score":    self._current_score(),
            "distance": self.distance,
            "coins":    self.coins_total,
            "username": self.username,
        }

    def _draw(self):
        self.screen.fill((45, 45, 45))

        pygame.draw.rect(self.screen, (255, 255, 255), (20, 0, 8, H))
        pygame.draw.rect(self.screen, (255, 255, 255), (W - 28, 0, 8, H))

        # Simple dashed lane divider.
        for y in range(0, H, 40):
            pygame.draw.rect(self.screen, (255, 255, 255), (W // 2 - 2, y, 4, 20))

        for obs in self.obstacles:
            pygame.draw.rect(self.screen, obs["color"], obs["rect"], border_radius=4)
            lbl = self.font_small.render(obs["type"], True, (255, 255, 255))
            self.screen.blit(lbl, (obs["rect"].x + 3, obs["rect"].y + 1))

        for pw in self.powerups:
            pygame.draw.rect(self.screen, pw["color"], pw["rect"], border_radius=6)
            lbl = self.font_small.render(pw["type"][0].upper(), True, (0, 0, 0))
            self.screen.blit(lbl, (
                pw["rect"].centerx - lbl.get_width()  // 2,
                pw["rect"].centery - lbl.get_height() // 2,
            ))

        for c in self.coins:
            pygame.draw.circle(self.screen, c["color"], (c["x"], int(c["y"])), c["r"])
            lbl = self.font_small.render(str(c["value"]), True, (0, 0, 0))
            self.screen.blit(lbl, (
                c["x"] - lbl.get_width()  // 2,
                int(c["y"]) - lbl.get_height() // 2,
            ))

        for e in self.enemies:
            self.screen.blit(self.enemy_img, e)

        if self.shield_active:
            pygame.draw.circle(self.screen, (0, 200, 255), self.player.center, 38, 3)
        self.screen.blit(self.player_img, self.player)

        self.screen.blit(self.font.render(f"Score: {self._current_score()}",   True, (255, 255, 255)), (35, 10))
        self.screen.blit(self.font.render(f"Coins: {self.coins_total}",        True, (255, 220, 0)),   (35, 35))
        self.screen.blit(self.font.render(f"Dist:  {self.distance // 100}m",   True, (200, 200, 200)), (35, 60))
        left = max(0, (FINISH_DISTANCE - self.distance) // 100)
        self.screen.blit(self.font.render(f"Left:  {left}m",                   True, (180, 220, 255)), (35, 85))
        self.screen.blit(self.font.render(f"Spd: {self.enemy_speed}",          True, (255, 100, 100)), (W - 120, 10))

        if self.active_powerup:
            t_left  = self.active_powerup["end_time"] - time.time()
            pw_text = f"{self.active_powerup['type'].upper()} {t_left:.1f}s"
            self.screen.blit(self.font.render(pw_text, True, (0, 255, 200)), (W // 2 - 65, 10))

        if self.shield_active:
            self.screen.blit(self.font.render("SHIELD", True, (0, 255, 100)), (W // 2 - 40, 35))

        if time.time() < self.oil_end:
            self.screen.blit(self.font.render("SLOW", True, (150, 150, 150)), (W // 2 - 30, 60))

        name_lbl = self.font_small.render(self.username, True, (200, 200, 200))
        self.screen.blit(name_lbl, (W - name_lbl.get_width() - 10, H - 28))

        pygame.display.flip()
