# Racer game - Practice 11
# Extended: coins with different weights (values), enemy speeds up every 5 coin points

import pygame
import random

pygame.init()

W = 400
H = 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Verdana", 50)
font_small = pygame.font.SysFont("Verdana", 20)

# Load car images
player_img = pygame.image.load("Player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 80))
enemy_img = pygame.image.load("Enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (50, 80))

# Three coin types: different point value, color, and size
# Higher value = rarer = smaller circle
COIN_TYPES = [
    {"value": 1, "color": (255, 220, 0),  "radius": 14},  # gold - common
    {"value": 3, "color": (255, 140, 0),  "radius": 11},  # orange - medium
    {"value": 5, "color": (200, 50, 255), "radius": 8},   # purple - rare
]
# Gold appears 6x more often, orange 3x, purple 1x
COIN_WEIGHTS = [6, 3, 1]


def spawn_coin():
    """Pick a random coin type and place it above the screen"""
    ctype = random.choices(COIN_TYPES, weights=COIN_WEIGHTS)[0]
    return {
        "x": random.randint(40, W - 40),
        "y": -30,
        "value": ctype["value"],
        "color": ctype["color"],
        "radius": ctype["radius"],
    }


# Player and enemy rects
player = player_img.get_rect(center=(200, 520))
enemy = enemy_img.get_rect(center=(random.randint(50, W - 50), -60))

# Two coins on road, staggered so they don't appear at the same time
road_coins = [spawn_coin(), spawn_coin()]
road_coins[1]["y"] = -250

score = 0          # number of enemies dodged
coins_total = 0    # total coin points collected
enemy_speed = 5    # how fast enemy falls (increases over time)
game_over = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Press any key to restart after game over
        if event.type == pygame.KEYDOWN and game_over:
            score = 0
            coins_total = 0
            enemy_speed = 5
            player.center = (200, 520)
            enemy.center = (random.randint(50, W - 50), -60)
            road_coins = [spawn_coin(), spawn_coin()]
            road_coins[1]["y"] = -250
            game_over = False

    # Game over screen
    if game_over:
        screen.fill((255, 0, 0))
        screen.blit(font_big.render("Game Over", True, (0, 0, 0)), (40, 250))
        screen.blit(font_small.render(f"Score: {score}  Coins: {coins_total}", True, (255, 255, 255)), (80, 330))
        screen.blit(font_small.render("Press any key to restart", True, (255, 255, 255)), (60, 380))
        pygame.display.update()
        clock.tick(30)
        continue

    # Move player left/right
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.move_ip(-5, 0)
    if keys[pygame.K_RIGHT] and player.right < W:
        player.move_ip(5, 0)

    # Move enemy down, count score when it passes
    enemy.move_ip(0, enemy_speed)
    if enemy.top > H:
        score += 1
        enemy.top = -60
        enemy.centerx = random.randint(40, W - 40)

    # Crash into enemy
    if player.colliderect(enemy):
        game_over = True
        continue

    # Move each coin, check if player collects it
    for coin in road_coins:
        coin["y"] += enemy_speed

        # Fell off screen - respawn above
        if coin["y"] > H + 30:
            coin.update(spawn_coin())
            continue

        # Use a small rect around the coin center for collision
        r = coin["radius"]
        coin_rect = pygame.Rect(coin["x"] - r, int(coin["y"]) - r, r * 2, r * 2)
        if player.colliderect(coin_rect):
            old_total = coins_total
            coins_total += coin["value"]
            # Every time total crosses a multiple of 5, enemy gets faster
            if (coins_total // 5) > (old_total // 5):
                enemy_speed += 1
            coin.update(spawn_coin())

    # Draw road background
    screen.fill((50, 50, 50))
    for y in range(0, H, 40):
        pygame.draw.rect(screen, (255, 255, 255), (W // 2 - 2, y, 4, 20))

    # Draw cars
    screen.blit(player_img, player)
    screen.blit(enemy_img, enemy)

    # Draw coins as colored circles with the value number inside
    for coin in road_coins:
        pygame.draw.circle(screen, coin["color"], (coin["x"], int(coin["y"])), coin["radius"])
        label = font_small.render(str(coin["value"]), True, (0, 0, 0))
        screen.blit(label, (coin["x"] - label.get_width() // 2,
                            int(coin["y"]) - label.get_height() // 2))

    # HUD: score, coin total, current enemy speed
    screen.blit(font_small.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(font_small.render(f"Coins: {coins_total}", True, (255, 220, 0)), (10, 35))
    screen.blit(font_small.render(f"Speed: {enemy_speed}", True, (255, 100, 100)), (W - 120, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
