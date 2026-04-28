import pygame

# Same window size as main.py.
W, H = 500, 700

font_big   = None
font_med   = None
font_small = None


def init_fonts():
    """Create fonts after pygame.init(); pygame needs the video system ready."""
    global font_big, font_med, font_small
    font_big   = pygame.font.SysFont("Verdana", 52)
    font_med   = pygame.font.SysFont("Verdana", 28)
    font_small = pygame.font.SysFont("Verdana", 20)


def draw_button(screen, text, rect, hover=False):
    """Small helper used by all menu screens."""
    color = (80, 120, 200) if hover else (50, 80, 150)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=8)

    lbl = font_small.render(text, True, (255, 255, 255))
    screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                      rect.centery - lbl.get_height() // 2))


def run_menu(screen, clock):
    """Main menu. Returns the next screen name."""
    btn_play        = pygame.Rect(W // 2 - 100, 260, 200, 50)
    btn_leaderboard = pygame.Rect(W // 2 - 100, 330, 200, 50)
    btn_settings    = pygame.Rect(W // 2 - 100, 400, 200, 50)
    btn_quit        = pygame.Rect(W // 2 - 100, 470, 200, 50)

    buttons = [
        (btn_play,        "Play",        'play'),
        (btn_leaderboard, "Leaderboard", 'leaderboard'),
        (btn_settings,    "Settings",    'settings'),
        (btn_quit,        "Quit",        'quit'),
    ]

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, label, result in buttons:
                    if rect.collidepoint(mouse_pos):
                        return result

        screen.fill((20, 20, 40))

        title = font_big.render("RACER", True, (255, 220, 0))
        screen.blit(title, (W // 2 - title.get_width() // 2, 140))

        sub = font_small.render("Use arrow keys to dodge enemies", True, (160, 160, 180))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 210))

        for rect, label, result in buttons:
            hover = rect.collidepoint(mouse_pos)
            draw_button(screen, label, rect, hover)

        pygame.display.flip()
        clock.tick(60)


def run_username(screen, clock):
    """Read the player name before starting a run."""
    username = ""
    cursor_visible = True
    cursor_timer = 0

    input_box = pygame.Rect(W // 2 - 140, H // 2 - 25, 280, 50)

    while True:
        cursor_timer += 1
        # Manual cursor blink because this is a plain pygame surface.
        if cursor_timer >= 30:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return username if username else "Player"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return username if username else "Player"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 16:
                    if event.unicode.isprintable():
                        username += event.unicode

        screen.fill((20, 20, 40))

        heading = font_med.render("Enter your name:", True, (255, 255, 255))
        screen.blit(heading, (W // 2 - heading.get_width() // 2, H // 2 - 100))

        pygame.draw.rect(screen, (40, 40, 70), input_box, border_radius=8)
        pygame.draw.rect(screen, (120, 160, 255), input_box, 2, border_radius=8)

        display_text = username + ("|" if cursor_visible else " ")
        txt_surface = font_med.render(display_text, True, (255, 255, 255))
        screen.blit(txt_surface, (input_box.x + 10,
                                  input_box.centery - txt_surface.get_height() // 2))

        hint = font_small.render("Press Enter to start", True, (150, 150, 180))
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 50))

        pygame.display.flip()
        clock.tick(60)


def run_settings(screen, clock, settings):
    """Settings screen. Changes are returned only after Save & Back."""
    current = settings.copy()

    btn_sound      = pygame.Rect(W // 2 + 30, 200, 160, 44)
    btn_color      = pygame.Rect(W // 2 + 30, 270, 160, 44)
    btn_difficulty = pygame.Rect(W // 2 + 30, 340, 160, 44)
    btn_back       = pygame.Rect(W // 2 - 90, 450, 180, 50)

    color_options      = ["blue", "red", "green"]
    difficulty_options = ["easy", "normal", "hard"]

    color_preview = {
        "blue":  (50, 100, 220),
        "red":   (220, 50, 50),
        "green": (50, 200, 80),
    }

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return current
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_sound.collidepoint(mouse_pos):
                    current["sound"] = not current["sound"]
                elif btn_color.collidepoint(mouse_pos):
                    idx = color_options.index(current["car_color"])
                    current["car_color"] = color_options[(idx + 1) % len(color_options)]
                elif btn_difficulty.collidepoint(mouse_pos):
                    idx = difficulty_options.index(current["difficulty"])
                    current["difficulty"] = difficulty_options[(idx + 1) % len(difficulty_options)]
                elif btn_back.collidepoint(mouse_pos):
                    return current

        screen.fill((20, 20, 40))

        title = font_med.render("Settings", True, (255, 220, 0))
        screen.blit(title, (W // 2 - title.get_width() // 2, 130))

        lbl = font_small.render("Sound:", True, (200, 200, 220))
        screen.blit(lbl, (60, 213))
        sound_text = "ON" if current["sound"] else "OFF"
        draw_button(screen, sound_text, btn_sound, btn_sound.collidepoint(mouse_pos))

        lbl = font_small.render("Car Color:", True, (200, 200, 220))
        screen.blit(lbl, (60, 283))
        draw_button(screen, current["car_color"].capitalize(), btn_color, btn_color.collidepoint(mouse_pos))
        # The small square shows the selected car color without starting a game.
        preview_rect = pygame.Rect(btn_color.right + 10, btn_color.y + 7, 28, 28)
        pygame.draw.rect(screen, color_preview[current["car_color"]], preview_rect, border_radius=4)

        lbl = font_small.render("Difficulty:", True, (200, 200, 220))
        screen.blit(lbl, (60, 353))
        draw_button(screen, current["difficulty"].capitalize(), btn_difficulty,
                    btn_difficulty.collidepoint(mouse_pos))

        draw_button(screen, "Save & Back", btn_back, btn_back.collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(60)


def run_gameover(screen, clock, score, distance, coins):
    """Game over screen with retry/menu choice."""
    btn_retry = pygame.Rect(W // 2 - 210, 430, 190, 54)
    btn_menu  = pygame.Rect(W // 2 + 20,  430, 190, 54)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'menu'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_retry.collidepoint(mouse_pos):
                    return 'retry'
                if btn_menu.collidepoint(mouse_pos):
                    return 'menu'

        screen.fill((35, 10, 10))

        title = font_big.render("GAME OVER", True, (220, 50, 50))
        screen.blit(title, (W // 2 - title.get_width() // 2, 160))

        lines = [
            (f"Score:    {score}",    (255, 255, 255)),
            (f"Distance: {distance}m", (200, 200, 200)),
            (f"Coins:    {coins}",    (255, 220, 0)),
        ]
        y = 270
        for text, color in lines:
            surf = font_med.render(text, True, color)
            screen.blit(surf, (W // 2 - surf.get_width() // 2, y))
            y += 48

        draw_button(screen, "Retry",     btn_retry, btn_retry.collidepoint(mouse_pos))
        draw_button(screen, "Main Menu", btn_menu,  btn_menu.collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(60)


def run_leaderboard(screen, clock, entries):
    """Show the best saved runs."""
    btn_back = pygame.Rect(W // 2 - 90, H - 90, 180, 50)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'back'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mouse_pos):
                    return 'back'

        screen.fill((20, 20, 40))

        title = font_med.render("Leaderboard", True, (255, 220, 0))
        screen.blit(title, (W // 2 - title.get_width() // 2, 30))

        header_color = (180, 180, 200)
        screen.blit(font_small.render("#",    True, header_color), (30,  80))
        screen.blit(font_small.render("Name", True, header_color), (70,  80))
        screen.blit(font_small.render("Score",True, header_color), (270, 80))
        screen.blit(font_small.render("Dist", True, header_color), (390, 80))

        pygame.draw.line(screen, (80, 80, 120), (20, 105), (W - 20, 105), 1)

        if not entries:
            empty = font_small.render("No entries yet. Play to get on the board!", True, (120, 120, 160))
            screen.blit(empty, (W // 2 - empty.get_width() // 2, H // 2 - 20))
        else:
            for i, entry in enumerate(entries[:10]):
                y = 115 + i * 44

                if i % 2 == 0:
                    pygame.draw.rect(screen, (30, 30, 55), pygame.Rect(20, y - 4, W - 40, 38))

                row_color = (255, 220, 0) if i == 0 else (210, 210, 220)

                # Names are trimmed because this table uses fixed columns.
                name = entry.get("name", "?")[:12]

                screen.blit(font_small.render(str(i + 1),            True, row_color), (30,  y))
                screen.blit(font_small.render(name,                  True, row_color), (70,  y))
                screen.blit(font_small.render(str(entry.get("score", 0)),   True, row_color), (270, y))
                screen.blit(font_small.render(str(entry.get("distance", 0)) + "m", True, row_color), (390, y))

        draw_button(screen, "Back", btn_back, btn_back.collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(60)
