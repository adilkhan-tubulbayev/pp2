import pygame

pygame.init()

# Create window 600x600
WIDTH = 600
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")
clock = pygame.time.Clock()

# Ball settings
RADIUS = 25       # ball radius in pixels
STEP = 20         # how many pixels ball moves per key press
ball_x = WIDTH // 2   # start position - center of screen
ball_y = HEIGHT // 2

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle key presses - move ball if it stays inside the screen
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and ball_y - STEP - RADIUS >= 0:
                ball_y -= STEP
            elif event.key == pygame.K_DOWN and ball_y + STEP + RADIUS <= HEIGHT:
                ball_y += STEP
            elif event.key == pygame.K_LEFT and ball_x - STEP - RADIUS >= 0:
                ball_x -= STEP
            elif event.key == pygame.K_RIGHT and ball_x + STEP + RADIUS <= WIDTH:
                ball_x += STEP

    # Draw white background and red ball
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (ball_x, ball_y), RADIUS)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
