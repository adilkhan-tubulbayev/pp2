# Snake game - Practice 11
# Extended: foods with different weights (values), foods disappear after a timer

import pygame
import random
import time

pygame.init()

WIDTH = 600
HEIGHT = 600
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 15)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
GRAY  = (60, 60, 60)

# Three food types: different values and lifetimes
# Higher value = disappears faster so it's harder to catch
FOOD_TYPES = [
    {"value": 1, "color": (255, 50, 50),  "lifetime": 8},  # red:    +1 point, lasts 8s
    {"value": 2, "color": (255, 165, 0),  "lifetime": 5},  # orange: +2 points, lasts 5s
    {"value": 3, "color": (255, 255, 0),  "lifetime": 3},  # yellow: +3 points, lasts 3s
]


def make_walls(level):
    """Border walls always present; extra internal walls added at level 2 and 3"""
    walls = set()
    cols = WIDTH // CELL
    rows = HEIGHT // CELL
    for x in range(cols):
        walls.add((x, 0))
        walls.add((x, rows - 1))
    for y in range(rows):
        walls.add((0, y))
        walls.add((cols - 1, y))
    if level >= 2:
        for x in range(5, 15):
            walls.add((x, rows // 2))
    if level >= 3:
        for y in range(5, 15):
            walls.add((cols // 2, y))
    return walls


def spawn_food(snake, walls):
    """Pick a random food type and place it at a free cell"""
    cols = WIDTH // CELL
    rows = HEIGHT // CELL
    ftype = random.choice(FOOD_TYPES)
    while True:
        pos = (random.randint(1, cols - 2), random.randint(1, rows - 2))
        if pos not in snake and pos not in walls:
            return {
                "pos": pos,
                "value": ftype["value"],
                "color": ftype["color"],
                "lifetime": ftype["lifetime"],
                "born": time.time(),  # timestamp when food appeared
            }


snake = [(15, 15)]
direction = (1, 0)
score = 0
level = 1
speed = 8
walls = make_walls(level)

# Keep 3 food items on screen at all times
foods = [spawn_food(snake, walls) for _ in range(3)]

game_over = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Restart
            if game_over:
                snake = [(15, 15)]
                direction = (1, 0)
                score = 0
                level = 1
                speed = 8
                walls = make_walls(level)
                foods = [spawn_food(snake, walls) for _ in range(3)]
                game_over = False

            # Change direction (no 180-degree reversal)
            if event.key == pygame.K_UP    and direction != (0, 1):  direction = (0, -1)
            elif event.key == pygame.K_DOWN  and direction != (0, -1): direction = (0, 1)
            elif event.key == pygame.K_LEFT  and direction != (1, 0):  direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and direction != (-1, 0): direction = (1, 0)

    # Game over screen
    if game_over:
        screen.fill(BLACK)
        screen.blit(font.render("GAME OVER - press any key", True, (255, 50, 50)), (100, 280))
        screen.blit(font.render(f"Score: {score}  Level: {level}", True, WHITE), (200, 320))
        pygame.display.flip()
        clock.tick(10)
        continue

    now = time.time()

    # Remove expired foods, then refill back to 3
    foods = [f for f in foods if now - f["born"] < f["lifetime"]]
    while len(foods) < 3:
        foods.append(spawn_food(snake, walls))

    # Move snake: calculate new head position
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # Collision with wall or self
    if head in walls or head in snake:
        game_over = True
        continue

    snake.insert(0, head)

    # Check if head landed on any food
    eaten = next((f for f in foods if f["pos"] == head), None)
    if eaten:
        score += eaten["value"]
        foods.remove(eaten)
        foods.append(spawn_food(snake, walls))
        # Level up every 4 points
        if score % 4 == 0:
            level += 1
            speed += 2
            walls = make_walls(level)
    else:
        snake.pop()  # no food eaten, remove tail so length stays the same

    # Draw
    screen.fill(BLACK)

    # Walls
    for w in walls:
        pygame.draw.rect(screen, GRAY, (w[0] * CELL, w[1] * CELL, CELL, CELL))

    # Food items: colored square + value label + timer bar at the bottom of the cell
    for f in foods:
        fx, fy = f["pos"]
        pygame.draw.rect(screen, f["color"], (fx * CELL, fy * CELL, CELL, CELL))

        # White bar shrinks as the food ages: full width = full lifetime
        time_left = f["lifetime"] - (now - f["born"])
        bar_w = int(CELL * time_left / f["lifetime"])
        pygame.draw.rect(screen, WHITE, (fx * CELL, fy * CELL + CELL - 3, bar_w, 3))

        # Value number on the food square
        lbl = font_small.render(str(f["value"]), True, BLACK)
        screen.blit(lbl, (fx * CELL + 4, fy * CELL + 2))

    # Snake
    for s in snake:
        pygame.draw.rect(screen, GREEN, (s[0] * CELL, s[1] * CELL, CELL, CELL))

    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (WIDTH - 110, 10))

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()
