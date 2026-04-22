# Racer game based on coderslegacy.com pygame tutorial
import pygame
import random
import time

pygame.init()

# Screen size
W = 400
H = 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

# Fonts
font_big = pygame.font.SysFont("Verdana", 50)
font_small = pygame.font.SysFont("Verdana", 20)

# Load images and scale them
player_img = pygame.image.load("Player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 80))

enemy_img = pygame.image.load("Enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (50, 80))

coin_img = pygame.image.load("coin.png").convert_alpha()
coin_img = pygame.transform.scale(coin_img, (30, 30))

# Player position
player = player_img.get_rect(center=(200, 520))

# Enemy position (starts above the screen)
enemy = enemy_img.get_rect(center=(random.randint(50, W - 50), -60))

# Coin position
coin = coin_img.get_rect(center=(random.randint(50, W - 50), -30))

# Game variables
speed = 5
score = 0
coins = 0
game_over = False

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Press any key to restart after game over
        if event.type == pygame.KEYDOWN and game_over:
            speed = 5
            score = 0
            coins = 0
            player.center = (200, 520)
            enemy.center = (random.randint(50, W - 50), -60)
            coin.center = (random.randint(50, W - 50), -30)
            game_over = False

    # Show game over screen and wait for key press
    if game_over:
        screen.fill((255, 0, 0))
        screen.blit(font_big.render("Game Over", True, (0, 0, 0)), (40, 250))
        screen.blit(font_small.render(f"Score: {score}  Coins: {coins}", True, (255, 255, 255)), (100, 330))
        screen.blit(font_small.render("Press any key to restart", True, (255, 255, 255)), (80, 380))
        pygame.display.update()
        clock.tick(30)
        continue

    # Player controls - left/right arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.move_ip(-5, 0)
    if keys[pygame.K_RIGHT] and player.right < W:
        player.move_ip(5, 0)

    # Move enemy down, respawn at top when it goes off screen
    enemy.move_ip(0, speed)
    if enemy.top > H:
        score += 1
        enemy.top = -60
        enemy.centerx = random.randint(40, W - 40)

    # Move coin down, respawn at top when it goes off screen
    coin.move_ip(0, speed)
    if coin.top > H:
        coin.top = -30
        coin.centerx = random.randint(40, W - 40)

    # Player collects coin
    if player.colliderect(coin):
        coins += 1
        coin.top = -30
        coin.centerx = random.randint(40, W - 40)

    # Player hits enemy - game over
    if player.colliderect(enemy):
        game_over = True
        continue

    # Speed increases slowly over time
    speed += 0.002

    # Draw road (gray background)
    screen.fill((50, 50, 50))

    # Dashed center line
    for y in range(0, H, 40):
        pygame.draw.rect(screen, (255, 255, 255), (W // 2 - 2, y, 4, 20))

    # Draw player, enemy, coin images
    screen.blit(player_img, player)
    screen.blit(enemy_img, enemy)
    screen.blit(coin_img, coin)

    # Draw score and coins counter
    screen.blit(font_small.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(font_small.render(f"Coins: {coins}", True, (255, 255, 0)), (W - 120, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
