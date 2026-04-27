import pygame

# Screen dimensions (must match main.py)
W, H = 500, 700

# Fonts are set up after pygame.init() is called in main.py
font_big   = None
font_med   = None
font_small = None


def init_fonts():
    """Call this once after pygame.init() to create the font objects."""
    global font_big, font_med, font_small
    font_big   = pygame.font.SysFont("Verdana", 52)
    font_med   = pygame.font.SysFont("Verdana", 28)
    font_small = pygame.font.SysFont("Verdana", 20)


def draw_button(screen, text, rect, hover=False):
    """Draw a rounded rectangle button. Turns brighter when the mouse is over it."""
    # Pick a lighter color on hover so the player knows it's clickable
    color = (80, 120, 200) if hover else (50, 80, 150)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=8)  # thin border

    # Centre the label text inside the button
    lbl = font_small.render(text, True, (255, 255, 255))
    screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                      rect.centery - lbl.get_height() // 2))


def run_menu(screen, clock):
    """
    Main menu screen.
    Shows the game title and four buttons: Play, Leaderboard, Settings, Quit.
    Returns one of: 'play', 'leaderboard', 'settings', 'quit'.
    """
    # Define the four buttons as Rect objects (x, y, width, height)
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

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check which button was clicked
                for rect, label, result in buttons:
                    if rect.collidepoint(mouse_pos):
                        return result

        # Draw dark background
        screen.fill((20, 20, 40))

        # Draw title
        title = font_big.render("RACER", True, (255, 220, 0))
        screen.blit(title, (W // 2 - title.get_width() // 2, 140))

        # Draw subtitle
        sub = font_small.render("Use arrow keys to dodge enemies", True, (160, 160, 180))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 210))

        # Draw each button, highlighting if the mouse is hovering over it
        for rect, label, result in buttons:
            hover = rect.collidepoint(mouse_pos)
            draw_button(screen, label, rect, hover)

        pygame.display.flip()
        clock.tick(60)


def run_username(screen, clock):
    """
    Username entry screen.
    Player types their name and presses Enter.
    Returns the entered username string (default 'Player' if nothing typed).
    """
    username = ""          # what the player has typed so far
    cursor_visible = True  # blinking cursor flag
    cursor_timer = 0       # counts frames for cursor blink

    # Input box rectangle
    input_box = pygame.Rect(W // 2 - 140, H // 2 - 25, 280, 50)

    while True:
        cursor_timer += 1
        # Blink cursor every 30 frames (0.5 seconds at 60 fps)
        if cursor_timer >= 30:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return username if username else "Player"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Confirm entry; fall back to 'Player' if field is empty
                    return username if username else "Player"
                elif event.key == pygame.K_BACKSPACE:
                    # Delete last character
                    username = username[:-1]
                elif len(username) < 16:
                    # Add typed character (only printable ASCII)
                    if event.unicode.isprintable():
                        username += event.unicode

        # Draw background
        screen.fill((20, 20, 40))

        # Draw heading
        heading = font_med.render("Enter your name:", True, (255, 255, 255))
        screen.blit(heading, (W // 2 - heading.get_width() // 2, H // 2 - 100))

        # Draw input box background
        pygame.draw.rect(screen, (40, 40, 70), input_box, border_radius=8)
        pygame.draw.rect(screen, (120, 160, 255), input_box, 2, border_radius=8)

        # Draw the typed text (with blinking cursor appended)
        display_text = username + ("|" if cursor_visible else " ")
        txt_surface = font_med.render(display_text, True, (255, 255, 255))
        screen.blit(txt_surface, (input_box.x + 10,
                                  input_box.centery - txt_surface.get_height() // 2))

        # Draw hint below the box
        hint = font_small.render("Press Enter to start", True, (150, 150, 180))
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 50))

        pygame.display.flip()
        clock.tick(60)


def run_settings(screen, clock, settings):
    """
    Settings screen.
    Shows toggle controls for Sound, Car Color, and Difficulty.
    Returns the updated settings dict when the player clicks Save & Back.
    """
    # Work on a copy so we can discard changes if needed
    current = settings.copy()

    # Button rectangles
    btn_sound      = pygame.Rect(W // 2 + 30, 200, 160, 44)
    btn_color      = pygame.Rect(W // 2 + 30, 270, 160, 44)
    btn_difficulty = pygame.Rect(W // 2 + 30, 340, 160, 44)
    btn_back       = pygame.Rect(W // 2 - 90, 450, 180, 50)

    # Cycle options for color and difficulty
    color_options      = ["blue", "red", "green"]
    difficulty_options = ["easy", "normal", "hard"]

    # Colors used to preview the selected car color
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
                    # Toggle sound on/off
                    current["sound"] = not current["sound"]
                elif btn_color.collidepoint(mouse_pos):
                    # Cycle to the next car color
                    idx = color_options.index(current["car_color"])
                    current["car_color"] = color_options[(idx + 1) % len(color_options)]
                elif btn_difficulty.collidepoint(mouse_pos):
                    # Cycle to the next difficulty
                    idx = difficulty_options.index(current["difficulty"])
                    current["difficulty"] = difficulty_options[(idx + 1) % len(difficulty_options)]
                elif btn_back.collidepoint(mouse_pos):
                    return current  # save changes and go back

        # Draw background
        screen.fill((20, 20, 40))

        # Title
        title = font_med.render("Settings", True, (255, 220, 0))
        screen.blit(title, (W // 2 - title.get_width() // 2, 130))

        # --- Sound row ---
        lbl = font_small.render("Sound:", True, (200, 200, 220))
        screen.blit(lbl, (60, 213))
        sound_text = "ON" if current["sound"] else "OFF"
        draw_button(screen, sound_text, btn_sound, btn_sound.collidepoint(mouse_pos))

        # --- Car Color row ---
        lbl = font_small.render("Car Color:", True, (200, 200, 220))
        screen.blit(lbl, (60, 283))
        draw_button(screen, current["car_color"].capitalize(), btn_color, btn_color.collidepoint(mouse_pos))
        # Small colour preview square
        preview_rect = pygame.Rect(btn_color.right + 10, btn_color.y + 7, 28, 28)
        pygame.draw.rect(screen, color_preview[current["car_color"]], preview_rect, border_radius=4)

        # --- Difficulty row ---
        lbl = font_small.render("Difficulty:", True, (200, 200, 220))
        screen.blit(lbl, (60, 353))
        draw_button(screen, current["difficulty"].capitalize(), btn_difficulty,
                    btn_difficulty.collidepoint(mouse_pos))

        # --- Save & Back button ---
        draw_button(screen, "Save & Back", btn_back, btn_back.collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(60)


def run_gameover(screen, clock, score, distance, coins):
    """
    Game over screen.
    Shows the player's score, distance and coins collected.
    Returns 'retry' or 'menu' depending on which button was clicked.
    """
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

        # Dark red-tinted background to feel dramatic
        screen.fill((35, 10, 10))

        # "GAME OVER" title in red
        title = font_big.render("GAME OVER", True, (220, 50, 50))
        screen.blit(title, (W // 2 - title.get_width() // 2, 160))

        # Score breakdown lines
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

        # Retry and Main Menu buttons
        draw_button(screen, "Retry",     btn_retry, btn_retry.collidepoint(mouse_pos))
        draw_button(screen, "Main Menu", btn_menu,  btn_menu.collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(60)


def run_leaderboard(screen, clock, entries):
    """
    Leaderboard screen.
    Shows up to 10 entries with rank, name, score, and distance.
    Returns 'back' when the player clicks the Back button.
    """
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

        # Title
        title = font_med.render("Leaderboard", True, (255, 220, 0))
        screen.blit(title, (W // 2 - title.get_width() // 2, 30))

        # Column headers
        header_color = (180, 180, 200)
        screen.blit(font_small.render("#",    True, header_color), (30,  80))
        screen.blit(font_small.render("Name", True, header_color), (70,  80))
        screen.blit(font_small.render("Score",True, header_color), (270, 80))
        screen.blit(font_small.render("Dist", True, header_color), (390, 80))

        # Separator line under headers
        pygame.draw.line(screen, (80, 80, 120), (20, 105), (W - 20, 105), 1)

        if not entries:
            # Nothing recorded yet
            empty = font_small.render("No entries yet. Play to get on the board!", True, (120, 120, 160))
            screen.blit(empty, (W // 2 - empty.get_width() // 2, H // 2 - 20))
        else:
            # Draw each entry row
            for i, entry in enumerate(entries[:10]):
                y = 115 + i * 44

                # Alternate row background for readability
                if i % 2 == 0:
                    pygame.draw.rect(screen, (30, 30, 55), pygame.Rect(20, y - 4, W - 40, 38))

                # Gold color for first place
                row_color = (255, 220, 0) if i == 0 else (210, 210, 220)

                # Truncate long names so they don't overflow
                name = entry.get("name", "?")[:12]

                screen.blit(font_small.render(str(i + 1),            True, row_color), (30,  y))
                screen.blit(font_small.render(name,                  True, row_color), (70,  y))
                screen.blit(font_small.render(str(entry.get("score", 0)),   True, row_color), (270, y))
                screen.blit(font_small.render(str(entry.get("distance", 0)) + "m", True, row_color), (390, y))

        draw_button(screen, "Back", btn_back, btn_back.collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(60)
