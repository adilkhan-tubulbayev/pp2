# Snake game with walls, levels, and speed increase
import pygame
import random

pygame.init()

# Screen settings
WIDTH = 600
HEIGHT = 600
CELL = 20  # size of one grid cell
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
GRAY = (60, 60, 60)

# Starting state
snake = [(15, 15)]         # list of snake cells
direction = (1, 0)         # moving right
score = 0
level = 1
speed = 8

# Create walls around the border + extra walls for higher levels
def make_walls(level):
    walls = set()
    cols = WIDTH // CELL
    rows = HEIGHT // CELL
    # Border walls
    for x in range(cols):
        walls.add((x, 0))
        walls.add((x, rows - 1))
    for y in range(rows):
        walls.add((0, y))
        walls.add((cols - 1, y))
    # Extra wall at level 2
    if level >= 2:
        for x in range(5, 15):
            walls.add((x, rows // 2))
    # Extra wall at level 3
    if level >= 3:
        for y in range(5, 15):
            walls.add((cols // 2, y))
    return walls

walls = make_walls(level)

# Generate random food position, not on snake or wall
def new_food():
    cols = WIDTH // CELL
    rows = HEIGHT // CELL
    while True:
        pos = (random.randint(1, cols - 2), random.randint(1, rows - 2))
        if pos not in snake and pos not in walls:
            return pos

food = new_food()
game_over = False

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Restart on any key when game over
            if game_over:
                snake = [(15, 15)]
                direction = (1, 0)
                score = 0
                level = 1
                speed = 8
                walls = make_walls(level)
                food = new_food()
                game_over = False

            # Change direction (cannot reverse 180 degrees)
            if event.key == pygame.K_UP and direction != (0, 1):
                direction = (0, -1)
            elif event.key == pygame.K_DOWN and direction != (0, -1):
                direction = (0, 1)
            elif event.key == pygame.K_LEFT and direction != (1, 0):
                direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                direction = (1, 0)

    # Show game over screen
    if game_over:
        screen.fill(BLACK)
        screen.blit(font.render("GAME OVER - press any key", True, RED), (150, 280))
        screen.blit(font.render(f"Score: {score}  Level: {level}", True, WHITE), (200, 320))
        pygame.display.flip()
        clock.tick(10)
        continue

    # Move snake - add new head in current direction
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # Check collision with wall or self
    if head in walls or head in snake:
        game_over = True
        continue

    snake.insert(0, head)

    # Check if snake ate food
    if head == food:
        score += 1
        # Level up every 4 points
        if score % 4 == 0:
            level += 1
            speed += 2
            walls = make_walls(level)
        food = new_food()
    else:
        snake.pop()  # remove tail (snake doesn't grow)

    # Draw everything
    screen.fill(BLACK)

    # Draw walls
    for w in walls:
        pygame.draw.rect(screen, GRAY, (w[0] * CELL, w[1] * CELL, CELL, CELL))

    # Draw food
    pygame.draw.rect(screen, RED, (food[0] * CELL, food[1] * CELL, CELL, CELL))

    # Draw snake
    for s in snake:
        pygame.draw.rect(screen, GREEN, (s[0] * CELL, s[1] * CELL, CELL, CELL))

    # Draw score and level
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (WIDTH - 110, 10))

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()
