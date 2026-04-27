import pygame
import random
import json
import sys
import os

# Change working directory so config.py finds database.ini
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import DB functions (will fail gracefully if psycopg2 not installed)
try:
    from db import save_session, get_leaderboard, get_personal_best
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────────────────
WIDTH = HEIGHT = 600
CELL = 20
COLS = ROWS = WIDTH // CELL   # 30 columns, 30 rows

# Base colors
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (60,  60,  60)     # wall color
GRAY2  = (90,  90,  90)     # obstacle color (slightly lighter than walls)
RED    = (255, 50,  50)
DARK_BG = (15, 15,  25)     # background color

# Food type definitions: name -> (color, points, lifetime_seconds)
FOOD_TYPES = [
    {"name": "red",    "color": (220,  50,  50), "pts": 1, "life": 8},
    {"name": "orange", "color": (230, 140,  40), "pts": 2, "life": 5},
    {"name": "yellow", "color": (220, 210,  50), "pts": 3, "life": 3},
]
# Weights for random food selection (red is most common)
FOOD_WEIGHTS = [5, 3, 2]

# Poison food settings
POISON_COLOR   = (120, 0, 0)   # dark red
POISON_CHANCE  = 0.30          # 30% chance a poison appears when new food spawns

# Power-up settings
POWERUP_TYPES = {
    "speed":  (0,   255, 255),   # cyan
    "slow":   (255, 150,  0),    # amber
    "shield": (0,   150, 255),   # blue
}
POWERUP_SPAWN_INTERVAL = 15000  # spawn every 15 seconds (ms)
POWERUP_LIFETIME       = 8000   # disappears after 8 seconds (ms)
POWERUP_EFFECT_DURATION = 5000  # effect lasts 5 seconds (ms)

SETTINGS_FILE = "settings.json"

# ── Settings helpers ───────────────────────────────────────────────────────────

def load_settings():
    """Load settings from JSON file, return defaults if file missing"""
    defaults = {"snake_color": [0, 200, 0], "grid": False, "sound": False}
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        # Fill missing keys with defaults
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        return data
    except:
        return defaults

def save_settings(settings):
    """Write settings dict to JSON file"""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# ── Wall / obstacle builders ───────────────────────────────────────────────────

def make_walls(level):
    """Return a set of (x,y) wall positions for the given level"""
    walls = set()
    # Border walls – all cells on the edge of the grid
    for x in range(COLS):
        walls.add((x, 0))
        walls.add((x, ROWS - 1))
    for y in range(ROWS):
        walls.add((0, y))
        walls.add((COLS - 1, y))
    # Level 2: horizontal wall across the middle
    if level >= 2:
        for x in range(5, 15):
            walls.add((x, ROWS // 2))
    # Level 3: vertical wall on the right half
    if level >= 3:
        for y in range(5, 15):
            walls.add((COLS // 2, y))
    return walls

def add_obstacles(walls, snake, foods, level):
    """Add random obstacle blocks for level 3 and above"""
    count = (level - 2) * 3   # 3 blocks at level 3, 6 at level 4, etc.
    added = 0
    attempts = 0
    food_positions = [f["pos"] for f in foods]
    while added < count and attempts < 500:
        attempts += 1
        x = random.randint(2, COLS - 3)
        y = random.randint(2, ROWS - 3)
        pos = (x, y)
        # Don't place too close to snake head
        hx, hy = snake[0]
        if abs(x - hx) < 5 and abs(y - hy) < 5:
            continue
        if pos in walls:
            continue
        if pos in food_positions:
            continue
        walls.add(pos)
        added += 1
    return walls

# ── Food helpers ───────────────────────────────────────────────────────────────

def spawn_food(walls, snake, existing_foods, poison_food):
    """Create a new food item at a random free position"""
    occupied = walls | set(snake)
    occupied |= {f["pos"] for f in existing_foods}
    if poison_food:
        occupied.add(poison_food["pos"])
    free = [(x, y) for x in range(1, COLS - 1)
                   for y in range(1, ROWS - 1)
                   if (x, y) not in occupied]
    if not free:
        return None
    pos = random.choice(free)
    ftype = random.choices(FOOD_TYPES, weights=FOOD_WEIGHTS, k=1)[0]
    return {
        "pos":    pos,
        "color":  ftype["color"],
        "pts":    ftype["pts"],
        "life":   ftype["life"] * 1000,   # convert to ms
        "born":   pygame.time.get_ticks(),
    }

def spawn_poison(walls, snake, foods):
    """Create a poison food item at a random free position"""
    occupied = walls | set(snake)
    occupied |= {f["pos"] for f in foods}
    free = [(x, y) for x in range(1, COLS - 1)
                   for y in range(1, ROWS - 1)
                   if (x, y) not in occupied]
    if not free:
        return None
    pos = random.choice(free)
    return {
        "pos":  pos,
        "born": pygame.time.get_ticks(),
        "life": 7000,   # poison disappears after 7 seconds
    }

def spawn_powerup(walls, snake, foods, poison_food):
    """Spawn a random power-up at a free position"""
    occupied = walls | set(snake)
    occupied |= {f["pos"] for f in foods}
    if poison_food:
        occupied.add(poison_food["pos"])
    free = [(x, y) for x in range(1, COLS - 1)
                   for y in range(1, ROWS - 1)
                   if (x, y) not in occupied]
    if not free:
        return None
    pos = random.choice(free)
    ptype = random.choice(list(POWERUP_TYPES.keys()))
    return {
        "pos":   pos,
        "type":  ptype,
        "color": POWERUP_TYPES[ptype],
        "born":  pygame.time.get_ticks(),
    }

# ── UI helpers ─────────────────────────────────────────────────────────────────

def draw_button(screen, font, text, rect, active=False):
    """Draw a rounded rectangle button and label; returns rect for click detection"""
    color = (70, 130, 180) if not active else (100, 180, 100)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    lbl = font.render(text, True, WHITE)
    screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                      rect.centery - lbl.get_height() // 2))
    return rect

def draw_timer_bar(screen, pos_px, width, ratio, color):
    """Draw a small colored bar below a food item to show time remaining"""
    x, y = pos_px
    bar_w = int(width * ratio)
    pygame.draw.rect(screen, (60, 60, 60), (x, y + CELL - 3, width, 3))
    if bar_w > 0:
        pygame.draw.rect(screen, color, (x, y + CELL - 3, bar_w, 3))

# ── Game state initialization ──────────────────────────────────────────────────

def new_game_state(settings):
    """Return a fresh game state dict"""
    level = 1
    walls = make_walls(level)
    snake = [(15, 15), (14, 15), (13, 15)]   # start in the middle heading right
    foods = []
    now   = pygame.time.get_ticks()
    # Spawn two initial food items
    f1 = spawn_food(walls, snake, foods, None)
    if f1:
        foods.append(f1)
    f2 = spawn_food(walls, snake, foods, None)
    if f2:
        foods.append(f2)
    return {
        "snake":       snake,
        "direction":   (1, 0),       # moving right
        "next_dir":    (1, 0),       # queued direction change
        "walls":       walls,
        "foods":       foods,
        "poison":      None,         # poison food item or None
        "powerup":     None,         # active powerup on field or None
        "score":       0,
        "level":       level,
        "food_eaten":  0,            # count since last level-up
        "base_speed":  8,            # FPS for clock.tick
        "speed_mult":  1.0,          # multiplier from power-ups
        "effect":      None,         # active effect: {"type", "ends_at"}
        "shield":      False,        # shield is active flag
        "last_pu_spawn": now,        # time of last powerup spawn attempt
        "paused":      False,
        "settings":    settings,
        "snake_color": tuple(settings["snake_color"]),
    }

# ── Drawing functions ──────────────────────────────────────────────────────────

def draw_game(screen, state, fonts, personal_best):
    """Draw the entire game screen"""
    screen.fill(DARK_BG)

    # Optional grid lines
    if state["settings"].get("grid"):
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, (30, 30, 40), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, (30, 30, 40), (0, y), (WIDTH, y))

    # Draw walls (border + internal)
    obstacle_set = make_walls(state["level"])  # base walls for color distinction
    for (wx, wy) in state["walls"]:
        if (wx, wy) in obstacle_set:
            color = GRAY
        else:
            color = GRAY2   # random obstacles are slightly lighter
        pygame.draw.rect(screen, color,
                         (wx * CELL, wy * CELL, CELL, CELL))

    now = pygame.time.get_ticks()

    # Draw normal food items with timer bars
    for food in state["foods"]:
        fx, fy = food["pos"]
        pygame.draw.rect(screen, food["color"],
                         (fx * CELL + 2, fy * CELL + 2, CELL - 4, CELL - 4),
                         border_radius=4)
        elapsed  = now - food["born"]
        ratio    = max(0.0, 1.0 - elapsed / food["life"])
        draw_timer_bar(screen, (fx * CELL, fy * CELL), CELL, ratio, food["color"])

    # Draw poison food
    if state["poison"]:
        px, py = state["poison"]["pos"]
        pygame.draw.rect(screen, POISON_COLOR,
                         (px * CELL + 2, py * CELL + 2, CELL - 4, CELL - 4),
                         border_radius=4)
        label = fonts["small"].render("P", True, WHITE)
        screen.blit(label, (px * CELL + 5, py * CELL + 3))
        elapsed = now - state["poison"]["born"]
        ratio   = max(0.0, 1.0 - elapsed / state["poison"]["life"])
        draw_timer_bar(screen, (px * CELL, py * CELL), CELL, ratio, POISON_COLOR)

    # Draw power-up on field
    if state["powerup"]:
        ux, uy = state["powerup"]["pos"]
        pygame.draw.rect(screen, state["powerup"]["color"],
                         (ux * CELL, uy * CELL, CELL, CELL),
                         border_radius=6)
        initial = state["powerup"]["type"][0].upper()
        label = fonts["small"].render(initial, True, BLACK)
        screen.blit(label, (ux * CELL + 5, uy * CELL + 3))

    # Draw snake
    for i, (sx, sy) in enumerate(state["snake"]):
        if i == 0:
            # Head is slightly different shade
            color = tuple(min(255, c + 60) for c in state["snake_color"])
        else:
            color = state["snake_color"]
        pygame.draw.rect(screen, color,
                         (sx * CELL + 1, sy * CELL + 1, CELL - 2, CELL - 2),
                         border_radius=3)

    # HUD: score, level, personal best
    score_txt = fonts["ui"].render(f"Score: {state['score']}", True, WHITE)
    level_txt = fonts["ui"].render(f"Level: {state['level']}", True, WHITE)
    pb_txt    = fonts["ui"].render(f"PB: {personal_best}", True, (180, 180, 180))
    screen.blit(score_txt, (8, 4))
    screen.blit(level_txt, (8, 22))
    screen.blit(pb_txt,    (WIDTH - pb_txt.get_width() - 8, 4))

    # Active power-up effect indicator
    if state["effect"]:
        remaining = max(0, state["effect"]["ends_at"] - now)
        secs = remaining / 1000
        etype = state["effect"]["type"]
        pu_color = POWERUP_TYPES.get(etype, WHITE)
        eff_txt = fonts["ui"].render(f"{etype.upper()} {secs:.1f}s", True, pu_color)
        screen.blit(eff_txt, (WIDTH // 2 - eff_txt.get_width() // 2, 4))

    # Shield active indicator
    if state["shield"]:
        sh_txt = fonts["ui"].render("SHIELD", True, POWERUP_TYPES["shield"])
        screen.blit(sh_txt, (WIDTH // 2 - sh_txt.get_width() // 2, 22))

    # Paused overlay
    if state["paused"]:
        pause_txt = fonts["big"].render("PAUSED", True, WHITE)
        screen.blit(pause_txt, (WIDTH // 2 - pause_txt.get_width() // 2,
                                HEIGHT // 2 - pause_txt.get_height() // 2))

# ── Game update (one tick) ─────────────────────────────────────────────────────

def update_game(state):
    """
    Advance the game by one step.
    Returns: "alive", "dead"
    """
    if state["paused"]:
        return "alive"

    now = pygame.time.get_ticks()

    # Apply queued direction (can't reverse 180 degrees)
    nd = state["next_dir"]
    cd = state["direction"]
    if (nd[0] != -cd[0]) or (nd[1] != -cd[1]):
        state["direction"] = nd

    # Move snake: insert new head, remove tail
    hx, hy = state["snake"][0]
    dx, dy  = state["direction"]
    new_head = (hx + dx, hy + dy)

    # Check wall / self collision
    hit_wall = new_head in state["walls"]
    hit_self = new_head in state["snake"]

    if hit_wall or hit_self:
        # If shield is active, absorb one hit
        if state["shield"]:
            state["shield"] = False
            # Nudge head back (just don't move this tick, keep same head)
            return "alive"
        return "dead"

    state["snake"].insert(0, new_head)

    # Check if head hit poison food
    if state["poison"] and new_head == state["poison"]["pos"]:
        state["poison"] = None
        # Shorten snake by 2 extra (head was already added, so remove 3 tail cells)
        for _ in range(3):
            if len(state["snake"]) > 1:
                state["snake"].pop()
        if len(state["snake"]) <= 1:
            return "dead"
        return "alive"   # don't grow, just got shorter

    # Check if head hit a power-up
    if state["powerup"] and new_head == state["powerup"]["pos"]:
        ptype = state["powerup"]["type"]
        state["powerup"] = None
        if ptype == "speed":
            state["speed_mult"] = 1.5
            state["effect"] = {"type": "speed",  "ends_at": now + POWERUP_EFFECT_DURATION}
        elif ptype == "slow":
            state["speed_mult"] = 0.6
            state["effect"] = {"type": "slow",   "ends_at": now + POWERUP_EFFECT_DURATION}
        elif ptype == "shield":
            state["shield"] = True
            state["effect"] = {"type": "shield", "ends_at": now + POWERUP_EFFECT_DURATION}
        # Power-up doesn't grow snake, remove tail normally
        state["snake"].pop()
        return "alive"

    # Check if head ate a normal food item
    ate = False
    for food in state["foods"][:]:
        if new_head == food["pos"]:
            state["score"]     += food["pts"]
            state["food_eaten"] += 1
            state["foods"].remove(food)
            ate = True
            # Spawn a replacement food
            new_food = spawn_food(state["walls"], state["snake"],
                                  state["foods"], state["poison"])
            if new_food:
                state["foods"].append(new_food)
            # 30% chance to also spawn poison
            if state["poison"] is None and random.random() < POISON_CHANCE:
                state["poison"] = spawn_poison(state["walls"],
                                               state["snake"], state["foods"])
            break

    if not ate:
        state["snake"].pop()   # normal move: remove tail

    # Level up every 4 food items
    if state["food_eaten"] >= 4:
        state["food_eaten"] = 0
        state["level"]      += 1
        state["base_speed"] += 2   # speed increases each level
        # Rebuild walls for new level
        state["walls"] = make_walls(state["level"])
        # Add random obstacles from level 3 onward
        if state["level"] >= 3:
            state["walls"] = add_obstacles(state["walls"], state["snake"],
                                           state["foods"], state["level"])

    # Expire power-up effect
    if state["effect"] and now >= state["effect"]["ends_at"]:
        state["effect"]     = None
        state["speed_mult"] = 1.0
        state["shield"]     = False  # shield expires with effect timer too

    # Expire food items that ran out of time
    state["foods"] = [f for f in state["foods"]
                      if now - f["born"] < f["life"]]
    # Keep at least 2 food items on screen
    while len(state["foods"]) < 2:
        new_food = spawn_food(state["walls"], state["snake"],
                              state["foods"], state["poison"])
        if new_food:
            state["foods"].append(new_food)
        else:
            break

    # Expire poison food
    if state["poison"] and now - state["poison"]["born"] >= state["poison"]["life"]:
        state["poison"] = None

    # Expire power-up on field
    if state["powerup"] and now - state["powerup"]["born"] >= POWERUP_LIFETIME:
        state["powerup"] = None

    # Try to spawn a new power-up if none on field and enough time passed
    if (state["powerup"] is None and
            now - state["last_pu_spawn"] >= POWERUP_SPAWN_INTERVAL):
        state["powerup"]     = spawn_powerup(state["walls"], state["snake"],
                                             state["foods"], state["poison"])
        state["last_pu_spawn"] = now

    return "alive"

# ── Screen: Menu ───────────────────────────────────────────────────────────────

def screen_menu(screen, clock, fonts, settings):
    """
    Show the main menu. Returns (next_state, username) tuple.
    next_state: 'game', 'leaderboard', 'settings', 'quit'
    """
    username      = ""
    input_active  = False
    input_rect    = pygame.Rect(WIDTH // 2 - 150, 200, 300, 40)

    btn_play   = pygame.Rect(WIDTH // 2 - 100, 270, 200, 45)
    btn_lb     = pygame.Rect(WIDTH // 2 - 100, 330, 200, 45)
    btn_set    = pygame.Rect(WIDTH // 2 - 100, 390, 200, 45)
    btn_quit   = pygame.Rect(WIDTH // 2 - 100, 450, 200, 45)

    while True:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", username

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if input_rect.collidepoint(mx, my):
                    input_active = True
                else:
                    input_active = False
                if btn_play.collidepoint(mx, my):
                    return "game", username.strip() or "Player"
                if btn_lb.collidepoint(mx, my):
                    return "leaderboard", username.strip() or "Player"
                if btn_set.collidepoint(mx, my):
                    return "settings", username.strip() or "Player"
                if btn_quit.collidepoint(mx, my):
                    return "quit", username

            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        return "game", username.strip() or "Player"
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif len(username) < 20:
                        # Only add printable characters
                        if event.unicode.isprintable():
                            username += event.unicode
                else:
                    if event.key == pygame.K_RETURN:
                        return "game", username.strip() or "Player"

        # Draw
        screen.fill(DARK_BG)

        title = fonts["title"].render("SNAKE", True, (0, 220, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = fonts["ui"].render("Enter your name:", True, (180, 180, 180))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 175))

        # Username input box
        box_color = (100, 160, 100) if input_active else (70, 70, 90)
        pygame.draw.rect(screen, box_color, input_rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, input_rect, 2, border_radius=6)
        name_txt = fonts["menu"].render(username + ("|" if input_active else ""), True, WHITE)
        screen.blit(name_txt, (input_rect.x + 8,
                               input_rect.centery - name_txt.get_height() // 2))

        draw_button(screen, fonts["menu"], "Play",        btn_play,  active=True)
        draw_button(screen, fonts["menu"], "Leaderboard", btn_lb)
        draw_button(screen, fonts["menu"], "Settings",    btn_set)
        draw_button(screen, fonts["menu"], "Quit",        btn_quit)

        pygame.display.flip()

# ── Screen: Game ───────────────────────────────────────────────────────────────

def screen_game(screen, clock, fonts, settings, username):
    """
    Run the game loop. Returns (next_state, final_score, final_level).
    next_state: 'gameover', 'menu'
    """
    state = new_game_state(settings)

    # Load personal best at start
    personal_best = 0
    if DB_AVAILABLE:
        try:
            personal_best = get_personal_best(username)
        except:
            pass

    while True:
        now = pygame.time.get_ticks()

        # Dynamic FPS from base speed * power-up multiplier
        fps = int(state["base_speed"] * state["speed_mult"])
        clock.tick(max(2, fps))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu", state["score"], state["level"]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu", state["score"], state["level"]
                if event.key == pygame.K_p:
                    state["paused"] = not state["paused"]
                # Direction input
                if not state["paused"]:
                    if event.key == pygame.K_UP:
                        state["next_dir"] = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        state["next_dir"] = (0,  1)
                    elif event.key == pygame.K_LEFT:
                        state["next_dir"] = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        state["next_dir"] = (1,  0)

        result = update_game(state)
        if result == "dead":
            return "gameover", state["score"], state["level"]

        draw_game(screen, state, fonts, personal_best)
        pygame.display.flip()

# ── Screen: Game Over ──────────────────────────────────────────────────────────

def screen_gameover(screen, clock, fonts, username, score, level):
    """
    Show game over screen; auto-save score to DB.
    Returns: 'game' (retry) or 'menu'
    """
    # Save score to database
    save_ok = False
    if DB_AVAILABLE and username:
        try:
            save_session(username, score, level)
            save_ok = True
        except:
            pass

    # Get updated personal best
    personal_best = score
    if DB_AVAILABLE:
        try:
            personal_best = get_personal_best(username)
        except:
            pass

    btn_retry = pygame.Rect(WIDTH // 2 - 110, 380, 100, 44)
    btn_menu  = pygame.Rect(WIDTH // 2 + 10,  380, 100, 44)

    while True:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btn_retry.collidepoint(mx, my):
                    return "game"
                if btn_menu.collidepoint(mx, my):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "game"
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        screen.fill(DARK_BG)

        go_txt = fonts["title"].render("GAME OVER", True, RED)
        screen.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, 120))

        sc_txt = fonts["big"].render(f"Score: {score}", True, WHITE)
        lv_txt = fonts["big"].render(f"Level: {level}", True, WHITE)
        pb_txt = fonts["big"].render(f"Personal Best: {personal_best}", True, (200, 200, 100))
        screen.blit(sc_txt, (WIDTH // 2 - sc_txt.get_width() // 2, 220))
        screen.blit(lv_txt, (WIDTH // 2 - lv_txt.get_width() // 2, 265))
        screen.blit(pb_txt, (WIDTH // 2 - pb_txt.get_width() // 2, 310))

        # Show whether save worked
        if DB_AVAILABLE:
            db_msg = "Score saved!" if save_ok else "Could not save score"
            db_color = (100, 200, 100) if save_ok else (200, 100, 100)
        else:
            db_msg   = "DB not available"
            db_color = (150, 150, 150)
        db_txt = fonts["ui"].render(db_msg, True, db_color)
        screen.blit(db_txt, (WIDTH // 2 - db_txt.get_width() // 2, 356))

        draw_button(screen, fonts["menu"], "Retry [R]", btn_retry, active=True)
        draw_button(screen, fonts["menu"], "Menu",      btn_menu)

        pygame.display.flip()

# ── Screen: Leaderboard ────────────────────────────────────────────────────────

def screen_leaderboard(screen, clock, fonts):
    """Show the top 10 leaderboard from the database. Returns 'menu'."""
    rows = []
    error_msg = ""

    if DB_AVAILABLE:
        try:
            raw = get_leaderboard(10)
            rows = raw
        except Exception as e:
            error_msg = "Could not connect to DB"
    else:
        error_msg = "DB not available (psycopg2 not installed)"

    btn_back = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 60, 120, 40)

    while True:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(event.pos):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    return "menu"

        screen.fill(DARK_BG)

        title = fonts["big"].render("LEADERBOARD", True, (220, 200, 50))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        if error_msg:
            err_txt = fonts["ui"].render(error_msg, True, RED)
            screen.blit(err_txt, (WIDTH // 2 - err_txt.get_width() // 2, 80))
        else:
            # Table header
            header = fonts["ui"].render(
                f"{'#':<4} {'Name':<16} {'Score':<8} {'Lvl':<5} {'Date'}", True, (160, 160, 200))
            screen.blit(header, (20, 70))
            pygame.draw.line(screen, GRAY, (20, 90), (WIDTH - 20, 90))

            for i, (uname, sc, lv, dt) in enumerate(rows):
                # Format date as YYYY-MM-DD
                date_str = dt.strftime("%Y-%m-%d") if dt else "—"
                line = f"{i+1:<4} {uname[:15]:<16} {sc:<8} {lv:<5} {date_str}"
                color = (220, 200, 50) if i == 0 else WHITE   # gold for first place
                row_txt = fonts["ui"].render(line, True, color)
                screen.blit(row_txt, (20, 98 + i * 22))

            if not rows:
                no_txt = fonts["ui"].render("No scores yet. Play a game!", True, (150, 150, 150))
                screen.blit(no_txt, (WIDTH // 2 - no_txt.get_width() // 2, 160))

        draw_button(screen, fonts["menu"], "Back", btn_back)
        pygame.display.flip()

# ── Screen: Settings ───────────────────────────────────────────────────────────

def screen_settings(screen, clock, fonts, settings):
    """
    Show settings screen. Returns updated settings dict.
    """
    # Work on a copy so changes only apply when saved
    local = dict(settings)
    local["snake_color"] = list(settings["snake_color"])

    # Color preset buttons
    color_options = [
        ("Green",  [0,   200,  0]),
        ("Blue",   [0,   100, 255]),
        ("Orange", [255, 140,  0]),
    ]
    btn_colors = [
        pygame.Rect(WIDTH // 2 - 165 + i * 115, 160, 105, 38)
        for i in range(len(color_options))
    ]

    btn_grid  = pygame.Rect(WIDTH // 2 - 80, 240, 160, 40)
    btn_sound = pygame.Rect(WIDTH // 2 - 80, 300, 160, 40)
    btn_save  = pygame.Rect(WIDTH // 2 - 80, 390, 160, 44)

    while True:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return settings   # discard changes
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # Color preset buttons
                for idx, rect in enumerate(btn_colors):
                    if rect.collidepoint(mx, my):
                        local["snake_color"] = color_options[idx][1]
                # Grid toggle
                if btn_grid.collidepoint(mx, my):
                    local["grid"] = not local["grid"]
                # Sound toggle
                if btn_sound.collidepoint(mx, my):
                    local["sound"] = not local["sound"]
                # Save & back
                if btn_save.collidepoint(mx, my):
                    save_settings(local)
                    return local
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return settings   # discard

        screen.fill(DARK_BG)

        title = fonts["big"].render("SETTINGS", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Snake color section
        color_lbl = fonts["ui"].render("Snake Color:", True, (180, 180, 180))
        screen.blit(color_lbl, (WIDTH // 2 - color_lbl.get_width() // 2, 130))
        for idx, (name, col) in enumerate(color_options):
            selected = (local["snake_color"] == col)
            pygame.draw.rect(screen, tuple(col), btn_colors[idx], border_radius=8)
            if selected:
                pygame.draw.rect(screen, WHITE, btn_colors[idx], 3, border_radius=8)
            lbl = fonts["menu"].render(name, True, BLACK)
            r = btn_colors[idx]
            screen.blit(lbl, (r.centerx - lbl.get_width() // 2,
                               r.centery - lbl.get_height() // 2))

        # Grid toggle
        grid_state = "ON" if local["grid"] else "OFF"
        draw_button(screen, fonts["menu"], f"Grid: {grid_state}", btn_grid,
                    active=local["grid"])

        # Sound toggle
        sound_state = "ON" if local["sound"] else "OFF"
        draw_button(screen, fonts["menu"], f"Sound: {sound_state}", btn_sound,
                    active=local["sound"])

        # Preview snake color
        prev_lbl = fonts["ui"].render("Preview:", True, (180, 180, 180))
        screen.blit(prev_lbl, (WIDTH // 2 - 60, 350))
        pygame.draw.rect(screen, tuple(local["snake_color"]),
                         (WIDTH // 2 + 20, 348, 40, 20), border_radius=4)

        draw_button(screen, fonts["menu"], "Save & Back", btn_save, active=True)
        pygame.display.flip()

# ── Main entry point ───────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake — TSIS-4")
    clock = pygame.time.Clock()

    # Set up fonts (use system fallback if custom not available)
    fonts = {
        "title": pygame.font.SysFont("Arial", 64, bold=True),
        "big":   pygame.font.SysFont("Arial", 36, bold=True),
        "menu":  pygame.font.SysFont("Arial", 24),
        "ui":    pygame.font.SysFont("Arial", 18),
        "small": pygame.font.SysFont("Arial", 13, bold=True),
    }

    settings = load_settings()
    state    = "menu"
    username = "Player"
    last_score = 0
    last_level = 1

    while True:
        if state == "menu":
            state, username = screen_menu(screen, clock, fonts, settings)

        elif state == "game":
            next_s, last_score, last_level = screen_game(
                screen, clock, fonts, settings, username)
            state = next_s

        elif state == "gameover":
            state = screen_gameover(
                screen, clock, fonts, username, last_score, last_level)

        elif state == "leaderboard":
            state = screen_leaderboard(screen, clock, fonts)

        elif state == "settings":
            settings = screen_settings(screen, clock, fonts, settings)
            state = "menu"

        elif state == "quit":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
