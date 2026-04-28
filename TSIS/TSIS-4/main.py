import pygame
import random
import json
import sys
import os

# Keep database.ini and settings.json relative to this folder.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# The game can still open without psycopg2; it just skips DB features.
try:
    from db import init_db, save_session, get_leaderboard, get_personal_best
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

WIDTH = HEIGHT = 600
CELL = 20
COLS = ROWS = WIDTH // CELL

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (60,  60,  60)
GRAY2  = (90,  90,  90)
RED    = (255, 50,  50)
DARK_BG = (15, 15,  25)

# Higher-value food stays on the field for less time.
FOOD_TYPES = [
    {"name": "red",    "color": (220,  50,  50), "pts": 1, "life": 8},
    {"name": "orange", "color": (230, 140,  40), "pts": 2, "life": 5},
    {"name": "yellow", "color": (220, 210,  50), "pts": 3, "life": 3},
]
FOOD_WEIGHTS = [5, 3, 2]

POISON_COLOR   = (120, 0, 0)
POISON_CHANCE  = 0.30

POWERUP_TYPES = {
    "speed":  (0,   255, 255),
    "slow":   (255, 150,  0),
    "shield": (0,   150, 255),
}
POWERUP_SPAWN_INTERVAL = 15000
POWERUP_LIFETIME       = 8000
POWERUP_EFFECT_DURATION = 5000

SETTINGS_FILE = "settings.json"
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds")

def load_settings():
    """Read settings.json, or use defaults on the first run."""
    defaults = {"snake_color": [0, 200, 0], "grid": False, "sound": False}
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        return data
    except:
        return defaults

def save_settings(settings):
    """Store settings chosen in the settings screen."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def load_sounds(settings):
    """Load short effects only when sound is enabled."""
    if not settings.get("sound"):
        return {}
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error:
            return {}

    sounds = {}
    for name in ("eat", "powerup", "poison", "shield", "level", "gameover"):
        path = os.path.join(SOUND_DIR, f"{name}.wav")
        try:
            sounds[name] = pygame.mixer.Sound(path)
        except pygame.error:
            pass
    return sounds

def play_sound(sounds, name):
    if name in sounds:
        sounds[name].play()

def make_walls(level):
    """Build the border wall around the field."""
    walls = set()
    for x in range(COLS):
        walls.add((x, 0))
        walls.add((x, ROWS - 1))
    for y in range(ROWS):
        walls.add((0, y))
        walls.add((COLS - 1, y))
    return walls

def add_obstacles(walls, snake, foods, level, poison_food=None, powerup=None):
    """Add random blocks after level 2."""
    count = (level - 2) * 3
    added = 0
    attempts = 0
    food_positions = [f["pos"] for f in foods]
    blocked = set(food_positions)
    if poison_food:
        blocked.add(poison_food["pos"])
    if powerup:
        blocked.add(powerup["pos"])

    while added < count and attempts < 500:
        attempts += 1
        x = random.randint(2, COLS - 3)
        y = random.randint(2, ROWS - 3)
        pos = (x, y)
        hx, hy = snake[0]
        if abs(x - hx) < 5 and abs(y - hy) < 5:
            continue
        if pos in walls:
            continue
        if pos in blocked:
            continue
        walls.add(pos)
        added += 1
    return walls

def spawn_food(walls, snake, existing_foods, poison_food):
    """Pick a free cell for normal food."""
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
        "life":   ftype["life"] * 1000,
        "born":   pygame.time.get_ticks(),
    }

def spawn_poison(walls, snake, foods):
    """Poison uses the same free-cell logic but gives bad effect."""
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
        "life": 7000,
    }

def spawn_powerup(walls, snake, foods, poison_food):
    """Spawn one visible power-up at a free cell."""
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

def draw_button(screen, font, text, rect, active=False):
    """Draw a menu button."""
    color = (70, 130, 180) if not active else (100, 180, 100)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    lbl = font.render(text, True, WHITE)
    screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                      rect.centery - lbl.get_height() // 2))
    return rect

def draw_timer_bar(screen, pos_px, width, ratio, color):
    """Show how much lifetime a food item has left."""
    x, y = pos_px
    bar_w = int(width * ratio)
    pygame.draw.rect(screen, (60, 60, 60), (x, y + CELL - 3, width, 3))
    if bar_w > 0:
        pygame.draw.rect(screen, color, (x, y + CELL - 3, bar_w, 3))

def new_game_state(settings):
    """Create all values needed for a new game."""
    level = 1
    walls = make_walls(level)
    snake = [(15, 15), (14, 15), (13, 15)]
    foods = []
    now   = pygame.time.get_ticks()
    f1 = spawn_food(walls, snake, foods, None)
    if f1:
        foods.append(f1)
    f2 = spawn_food(walls, snake, foods, None)
    if f2:
        foods.append(f2)
    return {
        "snake":       snake,
        "direction":   (1, 0),
        "next_dir":    (1, 0),
        "walls":       walls,
        "foods":       foods,
        "poison":      None,
        "powerup":     None,
        "score":       0,
        "level":       level,
        "food_eaten":  0,
        "base_speed":  8,
        "speed_mult":  1.0,
        "effect":      None,
        "shield":      False,
        "last_pu_spawn": now,
        "paused":      False,
        "settings":    settings,
        "snake_color": tuple(settings["snake_color"]),
        "sounds":      load_sounds(settings),
    }

def draw_game(screen, state, fonts, personal_best):
    """Draw one frame of the game."""
    screen.fill(DARK_BG)

    # Grid is only visual, it does not affect movement.
    if state["settings"].get("grid"):
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, (30, 30, 40), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, (30, 30, 40), (0, y), (WIDTH, y))

    obstacle_set = make_walls(state["level"])
    for (wx, wy) in state["walls"]:
        if (wx, wy) in obstacle_set:
            color = GRAY
        else:
            color = GRAY2
        pygame.draw.rect(screen, color,
                         (wx * CELL, wy * CELL, CELL, CELL))

    now = pygame.time.get_ticks()

    for food in state["foods"]:
        fx, fy = food["pos"]
        pygame.draw.rect(screen, food["color"],
                         (fx * CELL + 2, fy * CELL + 2, CELL - 4, CELL - 4),
                         border_radius=4)
        elapsed  = now - food["born"]
        ratio    = max(0.0, 1.0 - elapsed / food["life"])
        draw_timer_bar(screen, (fx * CELL, fy * CELL), CELL, ratio, food["color"])

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

    if state["powerup"]:
        ux, uy = state["powerup"]["pos"]
        pygame.draw.rect(screen, state["powerup"]["color"],
                         (ux * CELL, uy * CELL, CELL, CELL),
                         border_radius=6)
        initial = state["powerup"]["type"][0].upper()
        label = fonts["small"].render(initial, True, BLACK)
        screen.blit(label, (ux * CELL + 5, uy * CELL + 3))

    for i, (sx, sy) in enumerate(state["snake"]):
        if i == 0:
            color = tuple(min(255, c + 60) for c in state["snake_color"])
        else:
            color = state["snake_color"]
        pygame.draw.rect(screen, color,
                         (sx * CELL + 1, sy * CELL + 1, CELL - 2, CELL - 2),
                         border_radius=3)

    score_txt = fonts["ui"].render(f"Score: {state['score']}", True, WHITE)
    level_txt = fonts["ui"].render(f"Level: {state['level']}", True, WHITE)
    pb_txt    = fonts["ui"].render(f"PB: {personal_best}", True, (180, 180, 180))
    screen.blit(score_txt, (8, 4))
    screen.blit(level_txt, (8, 22))
    screen.blit(pb_txt,    (WIDTH - pb_txt.get_width() - 8, 4))

    if state["effect"]:
        remaining = max(0, state["effect"]["ends_at"] - now)
        secs = remaining / 1000
        etype = state["effect"]["type"]
        pu_color = POWERUP_TYPES.get(etype, WHITE)
        eff_txt = fonts["ui"].render(f"{etype.upper()} {secs:.1f}s", True, pu_color)
        screen.blit(eff_txt, (WIDTH // 2 - eff_txt.get_width() // 2, 4))

    if state["shield"]:
        sh_txt = fonts["ui"].render("SHIELD", True, POWERUP_TYPES["shield"])
        screen.blit(sh_txt, (WIDTH // 2 - sh_txt.get_width() // 2, 22))

    if state["paused"]:
        pause_txt = fonts["big"].render("PAUSED", True, WHITE)
        screen.blit(pause_txt, (WIDTH // 2 - pause_txt.get_width() // 2,
                                HEIGHT // 2 - pause_txt.get_height() // 2))

def update_game(state):
    """Move the snake one cell and update timers/collisions."""
    if state["paused"]:
        return "alive"

    now = pygame.time.get_ticks()

    # The snake cannot turn directly into itself.
    nd = state["next_dir"]
    cd = state["direction"]
    if (nd[0] != -cd[0]) or (nd[1] != -cd[1]):
        state["direction"] = nd

    hx, hy = state["snake"][0]
    dx, dy  = state["direction"]
    new_head = (hx + dx, hy + dy)

    hit_wall = new_head in state["walls"]
    hit_self = new_head in state["snake"]

    if hit_wall or hit_self:
        if state["shield"]:
            state["shield"] = False
            play_sound(state["sounds"], "shield")
            # Shield cancels this tick instead of moving into the wall/body.
            return "alive"
        play_sound(state["sounds"], "gameover")
        return "dead"

    state["snake"].insert(0, new_head)

    if state["poison"] and new_head == state["poison"]["pos"]:
        state["poison"] = None
        play_sound(state["sounds"], "poison")
        # Remove extra tail cells because the new head was already inserted.
        for _ in range(3):
            if len(state["snake"]) > 1:
                state["snake"].pop()
        if len(state["snake"]) <= 1:
            play_sound(state["sounds"], "gameover")
            return "dead"
        return "alive"

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
            state["speed_mult"] = 1.0
            state["shield"] = True
            state["effect"] = None
        play_sound(state["sounds"], "powerup")
        # Power-ups do not grow the snake.
        state["snake"].pop()
        return "alive"

    ate = False
    for food in state["foods"][:]:
        if new_head == food["pos"]:
            state["score"]     += food["pts"]
            state["food_eaten"] += 1
            state["foods"].remove(food)
            play_sound(state["sounds"], "eat")
            ate = True
            new_food = spawn_food(state["walls"], state["snake"],
                                  state["foods"], state["poison"])
            if new_food:
                state["foods"].append(new_food)
            if state["poison"] is None and random.random() < POISON_CHANCE:
                state["poison"] = spawn_poison(state["walls"],
                                               state["snake"], state["foods"])
            break

    if not ate:
        state["snake"].pop()

    if state["food_eaten"] >= 4:
        state["food_eaten"] = 0
        state["level"]      += 1
        state["base_speed"] += 2
        play_sound(state["sounds"], "level")
        state["walls"] = make_walls(state["level"])
        if state["level"] >= 3:
            state["walls"] = add_obstacles(state["walls"], state["snake"],
                                           state["foods"], state["level"],
                                           state["poison"], state["powerup"])

    if state["effect"] and now >= state["effect"]["ends_at"]:
        state["effect"]     = None
        state["speed_mult"] = 1.0

    state["foods"] = [f for f in state["foods"]
                      if now - f["born"] < f["life"]]
    # Keep the game playable if timed food disappears.
    while len(state["foods"]) < 2:
        new_food = spawn_food(state["walls"], state["snake"],
                              state["foods"], state["poison"])
        if new_food:
            state["foods"].append(new_food)
        else:
            break

    if state["poison"] and now - state["poison"]["born"] >= state["poison"]["life"]:
        state["poison"] = None

    if state["powerup"] and now - state["powerup"]["born"] >= POWERUP_LIFETIME:
        state["powerup"] = None

    if (state["powerup"] is None and
            state["effect"] is None and
            not state["shield"] and
            now - state["last_pu_spawn"] >= POWERUP_SPAWN_INTERVAL):
        state["powerup"]     = spawn_powerup(state["walls"], state["snake"],
                                             state["foods"], state["poison"])
        state["last_pu_spawn"] = now

    return "alive"

def screen_menu(screen, clock, fonts, settings):
    """Menu with username input and navigation buttons."""
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
                        if event.unicode.isprintable():
                            username += event.unicode
                else:
                    if event.key == pygame.K_RETURN:
                        return "game", username.strip() or "Player"

        screen.fill(DARK_BG)

        title = fonts["title"].render("SNAKE", True, (0, 220, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = fonts["ui"].render("Enter your name:", True, (180, 180, 180))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 175))

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

def screen_game(screen, clock, fonts, settings, username):
    """Run one game and return where the app should go next."""
    state = new_game_state(settings)

    personal_best = 0
    if DB_AVAILABLE:
        try:
            personal_best = get_personal_best(username)
        except:
            pass

    while True:
        now = pygame.time.get_ticks()

        # Speed power-ups change FPS, because snake movement happens once per tick.
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

def screen_gameover(screen, clock, fonts, username, score, level):
    """Save the result and show retry/menu buttons."""
    save_ok = False
    if DB_AVAILABLE and username:
        try:
            save_session(username, score, level)
            save_ok = True
        except:
            pass

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

def screen_leaderboard(screen, clock, fonts):
    """Show top scores loaded from PostgreSQL."""
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
            header = fonts["ui"].render(
                f"{'#':<4} {'Name':<16} {'Score':<8} {'Lvl':<5} {'Date'}", True, (160, 160, 200))
            screen.blit(header, (20, 70))
            pygame.draw.line(screen, GRAY, (20, 90), (WIDTH - 20, 90))

            for i, (uname, sc, lv, dt) in enumerate(rows):
                date_str = dt.strftime("%Y-%m-%d") if dt else "—"
                line = f"{i+1:<4} {uname[:15]:<16} {sc:<8} {lv:<5} {date_str}"
                color = (220, 200, 50) if i == 0 else WHITE
                row_txt = fonts["ui"].render(line, True, color)
                screen.blit(row_txt, (20, 98 + i * 22))

            if not rows:
                no_txt = fonts["ui"].render("No scores yet. Play a game!", True, (150, 150, 150))
                screen.blit(no_txt, (WIDTH // 2 - no_txt.get_width() // 2, 160))

        draw_button(screen, fonts["menu"], "Back", btn_back)
        pygame.display.flip()

def screen_settings(screen, clock, fonts, settings):
    """Settings screen. Escape discards unsaved changes."""
    local = dict(settings)
    local["snake_color"] = list(settings["snake_color"])

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
                return settings
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for idx, rect in enumerate(btn_colors):
                    if rect.collidepoint(mx, my):
                        local["snake_color"] = color_options[idx][1]
                if btn_grid.collidepoint(mx, my):
                    local["grid"] = not local["grid"]
                if btn_sound.collidepoint(mx, my):
                    local["sound"] = not local["sound"]
                if btn_save.collidepoint(mx, my):
                    save_settings(local)
                    return local
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return settings

        screen.fill(DARK_BG)

        title = fonts["big"].render("SETTINGS", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

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

        grid_state = "ON" if local["grid"] else "OFF"
        draw_button(screen, fonts["menu"], f"Grid: {grid_state}", btn_grid,
                    active=local["grid"])

        sound_state = "ON" if local["sound"] else "OFF"
        draw_button(screen, fonts["menu"], f"Sound: {sound_state}", btn_sound,
                    active=local["sound"])

        prev_lbl = fonts["ui"].render("Preview:", True, (180, 180, 180))
        screen.blit(prev_lbl, (WIDTH // 2 - 60, 350))
        pygame.draw.rect(screen, tuple(local["snake_color"]),
                         (WIDTH // 2 + 20, 348, 40, 20), border_radius=4)

        draw_button(screen, fonts["menu"], "Save & Back", btn_save, active=True)
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake — TSIS-4")
    clock = pygame.time.Clock()

    # Built-in fonts are enough here.
    fonts = {
        "title": pygame.font.SysFont("Arial", 64, bold=True),
        "big":   pygame.font.SysFont("Arial", 36, bold=True),
        "menu":  pygame.font.SysFont("Arial", 24),
        "ui":    pygame.font.SysFont("Arial", 18),
        "small": pygame.font.SysFont("Arial", 13, bold=True),
    }

    if DB_AVAILABLE:
        try:
            init_db()
        except:
            pass

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
