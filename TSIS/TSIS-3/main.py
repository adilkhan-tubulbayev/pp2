"""Entry point for the racer game."""

import pygame
import sys

from persistence import load_settings, save_settings, load_leaderboard, save_leaderboard
from ui          import init_fonts, run_menu, run_username, run_settings, run_gameover, run_leaderboard
from racer       import Game

pygame.init()

W, H = 500, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer – TSIS-3")
clock = pygame.time.Clock()

# Pygame fonts must be created after pygame.init().
init_fonts()

settings    = load_settings()
leaderboard = load_leaderboard()
username    = "Player"

# Each screen returns the next state, so the main loop stays simple.
state = 'menu'

while True:

    if state == 'menu':
        state = run_menu(screen, clock)

    elif state == 'play':
        username = run_username(screen, clock)

        game   = Game(screen, clock, settings, username)
        result = game.run()

        if result:
            entry = {
                "name":     username,
                "score":    result["score"],
                "distance": result["distance"] // 100,
                "coins":    result["coins"],
            }
            leaderboard.append(entry)
            save_leaderboard(leaderboard)
            leaderboard = load_leaderboard()

            next_state = run_gameover(screen, clock,
                                      result["score"],
                                      result["distance"] // 100,
                                      result["coins"])
            state = 'play' if next_state == 'retry' else 'menu'
        else:
            # Escape from the game goes back to menu without saving a score.
            state = 'menu'

    elif state == 'leaderboard':
        run_leaderboard(screen, clock, leaderboard)
        state = 'menu'

    elif state == 'settings':
        settings = run_settings(screen, clock, settings)
        save_settings(settings)
        state = 'menu'

    elif state == 'quit':
        pygame.quit()
        sys.exit()
