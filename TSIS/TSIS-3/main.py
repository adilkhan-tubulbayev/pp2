"""
main.py – Entry point for the TSIS-3 Racer game.

Run this file with:  python main.py
or:                  python3 main.py

The state machine below drives the whole application:
  menu  ->  (play) username -> game -> gameover -> menu/play
        ->  (leaderboard)  -> menu
        ->  (settings)     -> menu
        ->  (quit)         exit
"""

import pygame
import sys

# Import our own modules
from persistence import load_settings, save_settings, load_leaderboard, save_leaderboard
from ui          import init_fonts, run_menu, run_username, run_settings, run_gameover, run_leaderboard
from racer       import Game

# -----------------------------------------------------------------------
# Pygame initialisation
# -----------------------------------------------------------------------
pygame.init()

W, H = 500, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer – TSIS-3")
clock = pygame.time.Clock()

# Fonts must be created after pygame.init()
init_fonts()

# -----------------------------------------------------------------------
# Load persistent data from disk
# -----------------------------------------------------------------------
settings    = load_settings()
leaderboard = load_leaderboard()
username    = "Player"   # default name; overwritten by the username screen

# -----------------------------------------------------------------------
# Main state machine
# -----------------------------------------------------------------------
state = 'menu'

while True:

    # ---- Main menu ----
    if state == 'menu':
        # run_menu returns one of: 'play', 'leaderboard', 'settings', 'quit'
        state = run_menu(screen, clock)

    # ---- Play ----
    elif state == 'play':
        # Ask the player for their name before starting
        username = run_username(screen, clock)

        # Create a new Game instance and run it
        game   = Game(screen, clock, settings, username)
        result = game.run()  # returns a dict on crash, or None if player pressed Escape

        if result:
            # Save result to leaderboard
            entry = {
                "name":     username,
                "score":    result["score"],
                "distance": result["distance"] // 100,  # convert pixels to metres
                "coins":    result["coins"],
            }
            leaderboard.append(entry)
            save_leaderboard(leaderboard)
            leaderboard = load_leaderboard()  # reload sorted top-10

            # Show the game-over screen and decide what to do next
            next_state = run_gameover(screen, clock,
                                      result["score"],
                                      result["distance"] // 100,
                                      result["coins"])
            state = 'play' if next_state == 'retry' else 'menu'
        else:
            # Player pressed Escape – go straight back to menu
            state = 'menu'

    # ---- Leaderboard ----
    elif state == 'leaderboard':
        run_leaderboard(screen, clock, leaderboard)
        state = 'menu'

    # ---- Settings ----
    elif state == 'settings':
        settings = run_settings(screen, clock, settings)
        save_settings(settings)   # persist changes to settings.json
        state = 'menu'

    # ---- Quit ----
    elif state == 'quit':
        pygame.quit()
        sys.exit()
