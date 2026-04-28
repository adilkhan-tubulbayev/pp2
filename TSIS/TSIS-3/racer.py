import pygame
import random
import time
import os

# Screen dimensions (must match main.py)
W, H = 500, 700
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FINISH_DISTANCE = 3000 * 100

# Maps setting string to an actual RGB color for the player car
CAR_COLORS = {
    "blue":  (50, 100, 220),
    "red":   (220, 50, 50),
    "green": (50, 200, 80),
}

# How often obstacles and extra enemies spawn per frame for each difficulty
DIFF_SETTINGS = {
    "easy":   {"obstacle_rate": 0.003, "powerup_rate": 0.004, "max_enemies": 4},
    "normal": {"obstacle_rate": 0.006, "powerup_rate": 0.003, "max_enemies": 5},
    "hard":   {"obstacle_rate": 0.010, "powerup_rate": 0.002, "max_enemies": 6},
}


class Game:
    """
    Contains all game logic: initialisation, the main loop, drawing, and collision handling.
    """

    def __init__(self, screen, clock, settings, username):
        self.screen   = screen
        self.clock    = clock
        self.settings = settings
        self.username = username

        # Two font sizes used for the on-screen HUD
        self.font       = pygame.font.SysFont("Verdana", 20)
        self.font_small = pygame.font.SysFont("Verdana", 16)

        # Load car images; fall back to coloured rectangles if the PNG files are missing
        self.player_img = self._load_car_img("Player.png", 45, 75,
                                             CAR_COLORS[settings.get("car_color", "blue")])
        self.enemy_img  = self._load_car_img("Enemy.png",  45, 75, (200, 50, 50))

        # Set up the initial game state
        self.reset()

    # ------------------------------------------------------------------
    # Helper – load an image or draw a simple placeholder rectangle
    # ------------------------------------------------------------------
    def _load_car_img(self, path, w, h, fallback_color):
        """Try to load a PNG. If not found, draw a simple car shape instead."""
        try:
            img = pygame.image.load(os.path.join(BASE_DIR, path)).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except Exception:
            # Build a surface that looks vaguely like a car
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(surf, fallback_color, (0, 0, w, h), border_radius=6)
            pygame.draw.rect(surf, (200, 200, 200), (5, 5, w - 10, 20))  # windshield strip
            return surf

    # ------------------------------------------------------------------
    # Reset all game state to start a fresh game
    # ------------------------------------------------------------------
    def reset(self):
        # Player starts in the horizontal centre near the bottom of the screen
        self.player = self.player_img.get_rect(center=(W // 2, H - 100))

        # Start with two enemy cars falling from above
        self.enemies = [self._spawn_enemy() for _ in range(2)]

        # Start with three coins on screen
        self.coins = [self._spawn_coin() for _ in range(3)]

        # Obstacles and power-ups start empty; they spawn during play
        self.obstacles = []   # each entry: {rect, type, color}
        self.powerups  = []   # each entry: {rect, type, color, spawn_time}

        # Scoring counters
        self.score       = 0   # increments each time an enemy passes
        self.coins_total = 0   # total coin value collected
        self.distance    = 0   # pixels scrolled (converted to metres for display)
        self.powerup_bonus = 0

        # Speed values – both increase as the game progresses
        self.base_speed  = 5   # slowly drifts up over time
        self.enemy_speed = 5   # jumps when the player collects coins

        # Power-up state
        self.active_powerup = None  # {type, end_time} or None
        self.shield_active  = False
        self.oil_end        = 0     # timestamp when the oil slow-down expires

        # Cache the difficulty spawn rates
        self.diff = DIFF_SETTINGS[self.settings.get("difficulty", "normal")]

    # ------------------------------------------------------------------
    # Spawn helpers
    # ------------------------------------------------------------------
    def _spawn_enemy(self):
        """Create an enemy Rect above the visible screen at a random x position."""
        return self.enemy_img.get_rect(
            center=(random.randint(60, W - 60),
                    random.randint(-300, -60))
        )

    def _spawn_coin(self):
        """
        Return a coin dict.
        Three types with different rarity:
          gold (value 1, most common), orange (value 3), purple (value 5, rare).
        """
        types = [
            {"value": 1, "color": (255, 220, 0),  "r": 14},  # gold
            {"value": 3, "color": (255, 140, 0),  "r": 11},  # orange
            {"value": 5, "color": (180, 50, 255), "r": 8},   # purple
        ]
        # Weighted random choice – gold is 6x more likely than purple
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
        Return an obstacle dict.
        Types:
          oil     – slows the player for 2 seconds (grey rectangle)
          barrier – instant game over unless shield is active (red)
          bump    – small slowdown (orange)
          nitro   – brief speed boost for the player (blue)
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
        Return a power-up dict.
        Types:
          nitro  – speed boost for 4 seconds (cyan)
          shield – absorbs one collision (green)
          repair – clears the oil slow-down (yellow)
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
        """Obstacle frequency grows with distance so difficulty scales during play."""
        extra_rate = min(0.012, self.distance / 100000 * 0.001)
        return self.diff["obstacle_rate"] + extra_rate

    def _current_score(self):
        return self.score * 10 + self.distance // 100 + self.coins_total * 5 + self.powerup_bonus

    # ------------------------------------------------------------------
    # Main game loop
    # ------------------------------------------------------------------
    def run(self):
        """
        Run the game until the player crashes or presses Escape.
        Returns a result dict {score, distance, coins, username} on crash,
        or None if the player pressed Escape.
        """
        while True:
            # --- Event handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None  # player wants to go back to the menu

            # --- Player movement ---
            keys = pygame.key.get_pressed()

            # Determine movement speed based on active effects
            if self.active_powerup and self.active_powerup["type"] == "nitro":
                spd = 12   # turbo mode from nitro power-up
            elif time.time() < self.oil_end:
                spd = 2    # dragging through oil
            else:
                spd = 6    # normal speed

            if keys[pygame.K_LEFT]  and self.player.left  > 0: self.player.move_ip(-spd, 0)
            if keys[pygame.K_RIGHT] and self.player.right < W:  self.player.move_ip( spd, 0)

            current_speed = self.enemy_speed  # everything scrolls at this speed

            # --- Distance tracker ---
            self.distance += current_speed
            if self.distance >= FINISH_DISTANCE:
                return self._build_result()

            # --- Move enemies downward ---
            for e in self.enemies:
                e.move_ip(0, current_speed)

                # If enemy scrolled off the bottom, respawn it above the screen
                if e.top > H:
                    self.score += 1  # player survived one enemy pass
                    e.topleft = self._spawn_enemy().topleft

                    # Every 10 dodges, add one more enemy up to the difficulty limit
                    if self.score % 10 == 0 and len(self.enemies) < self.diff["max_enemies"]:
                        self.enemies.append(self._spawn_enemy())

                # Check if enemy hit the player
                if e.colliderect(self.player):
                    if self.shield_active:
                        # Shield absorbs the hit; respawn enemy
                        self.shield_active = False
                        e.topleft = self._spawn_enemy().topleft
                    else:
                        # Game over – return the result
                        return self._build_result()

            # --- Move coins downward and check collection ---
            for c in self.coins:
                c["y"] += current_speed

                # Respawn coin when it scrolls past the bottom
                if c["y"] > H + 30:
                    c.update(self._spawn_coin())
                    continue

                # Build a small rect around the coin for collision detection
                r = c["r"]
                crect = pygame.Rect(c["x"] - r, int(c["y"]) - r, r * 2, r * 2)

                if self.player.colliderect(crect):
                    old_total = self.coins_total
                    self.coins_total += c["value"]

                    # Every 5 coin-points, the enemy speed goes up by 1
                    if self.coins_total // 5 > old_total // 5:
                        self.enemy_speed += 1

                    c.update(self._spawn_coin())  # replace collected coin

            # --- Spawn and move obstacles ---
            if random.random() < self._current_obstacle_rate():
                self.obstacles.append(self._spawn_obstacle())

            for obs in self.obstacles[:]:
                obs["rect"].move_ip(0, current_speed)

                # Remove obstacles that scrolled past the bottom
                if obs["rect"].top > H:
                    self.obstacles.remove(obs)
                    continue

                # Check if obstacle hit the player
                if obs["rect"].colliderect(self.player):
                    otype = obs["type"]
                    if otype == "barrier":
                        if self.shield_active:
                            self.shield_active = False  # shield tanks the barrier
                        else:
                            return self._build_result()
                    elif otype == "oil":
                        self.oil_end = time.time() + 2     # slow for 2 seconds
                    elif otype == "bump":
                        self.oil_end = time.time() + 0.5   # very brief slowdown
                    elif otype == "nitro":
                        # Obstacle nitro strip gives a short speed boost
                        self.active_powerup = {"type": "nitro", "end_time": time.time() + 3}
                    self.obstacles.remove(obs)

            # --- Spawn and move power-ups ---
            if (random.random() < self.diff["powerup_rate"] and
                    len(self.powerups) == 0 and
                    self.active_powerup is None and
                    not self.shield_active):
                self.powerups.append(self._spawn_powerup())

            for pw in self.powerups[:]:
                pw["rect"].move_ip(0, current_speed)

                # Remove power-ups that left the screen or have been on screen too long (8 s)
                if pw["rect"].top > H or time.time() - pw["spawn_time"] > 8:
                    self.powerups.remove(pw)
                    continue

                # Check if player picked up the power-up
                if pw["rect"].colliderect(self.player):
                    ptype = pw["type"]
                    if ptype == "nitro":
                        self.active_powerup = {"type": "nitro", "end_time": time.time() + 4}
                        self.powerup_bonus += 20
                    elif ptype == "shield":
                        self.shield_active = True
                        self.powerup_bonus += 10
                    elif ptype == "repair":
                        self.oil_end = 0  # repair clears one bad effect immediately
                        self.powerup_bonus += 10
                    self.powerups.remove(pw)

            # --- Expire the active power-up when its timer runs out ---
            if self.active_powerup and time.time() > self.active_powerup["end_time"]:
                self.active_powerup = None

            # --- Gradually increase base speed over time ---
            self.base_speed  += 0.001
            self.enemy_speed = max(self.enemy_speed, int(self.base_speed))

            # --- Draw everything and cap at 60 fps ---
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

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _draw(self):
        # --- Road background ---
        self.screen.fill((45, 45, 45))

        # Road edges (white strips)
        pygame.draw.rect(self.screen, (255, 255, 255), (20, 0, 8, H))
        pygame.draw.rect(self.screen, (255, 255, 255), (W - 28, 0, 8, H))

        # Dashed centre line – one short white segment every 40 pixels
        for y in range(0, H, 40):
            pygame.draw.rect(self.screen, (255, 255, 255), (W // 2 - 2, y, 4, 20))

        # --- Obstacles ---
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, obs["color"], obs["rect"], border_radius=4)
            # Small label so the player can learn what each obstacle does
            lbl = self.font_small.render(obs["type"], True, (255, 255, 255))
            self.screen.blit(lbl, (obs["rect"].x + 3, obs["rect"].y + 1))

        # --- Power-ups (rounded squares with a single capital letter) ---
        for pw in self.powerups:
            pygame.draw.rect(self.screen, pw["color"], pw["rect"], border_radius=6)
            lbl = self.font_small.render(pw["type"][0].upper(), True, (0, 0, 0))
            self.screen.blit(lbl, (
                pw["rect"].centerx - lbl.get_width()  // 2,
                pw["rect"].centery - lbl.get_height() // 2,
            ))

        # --- Coins (circles with the coin value printed inside) ---
        for c in self.coins:
            pygame.draw.circle(self.screen, c["color"], (c["x"], int(c["y"])), c["r"])
            lbl = self.font_small.render(str(c["value"]), True, (0, 0, 0))
            self.screen.blit(lbl, (
                c["x"] - lbl.get_width()  // 2,
                int(c["y"]) - lbl.get_height() // 2,
            ))

        # --- Enemy cars ---
        for e in self.enemies:
            self.screen.blit(self.enemy_img, e)

        # --- Player car (with an optional shield ring) ---
        if self.shield_active:
            # Draw a glowing blue circle around the player to show the shield
            pygame.draw.circle(self.screen, (0, 200, 255), self.player.center, 38, 3)
        self.screen.blit(self.player_img, self.player)

        # --- HUD (top-left corner) ---
        self.screen.blit(self.font.render(f"Score: {self._current_score()}",   True, (255, 255, 255)), (35, 10))
        self.screen.blit(self.font.render(f"Coins: {self.coins_total}",        True, (255, 220, 0)),   (35, 35))
        self.screen.blit(self.font.render(f"Dist:  {self.distance // 100}m",   True, (200, 200, 200)), (35, 60))
        left = max(0, (FINISH_DISTANCE - self.distance) // 100)
        self.screen.blit(self.font.render(f"Left:  {left}m",                   True, (180, 220, 255)), (35, 85))
        self.screen.blit(self.font.render(f"Spd: {self.enemy_speed}",          True, (255, 100, 100)), (W - 120, 10))

        # --- Active power-up timer (centre top) ---
        if self.active_powerup:
            t_left  = self.active_powerup["end_time"] - time.time()
            pw_text = f"{self.active_powerup['type'].upper()} {t_left:.1f}s"
            self.screen.blit(self.font.render(pw_text, True, (0, 255, 200)), (W // 2 - 65, 10))

        if self.shield_active:
            self.screen.blit(self.font.render("SHIELD", True, (0, 255, 100)), (W // 2 - 40, 35))

        if time.time() < self.oil_end:
            self.screen.blit(self.font.render("SLOW", True, (150, 150, 150)), (W // 2 - 30, 60))

        # --- Player name (bottom-right corner) ---
        name_lbl = self.font_small.render(self.username, True, (200, 200, 200))
        self.screen.blit(name_lbl, (W - name_lbl.get_width() - 10, H - 28))

        pygame.display.flip()
