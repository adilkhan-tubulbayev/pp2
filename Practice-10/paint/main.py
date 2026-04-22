# Paint app based on nerdparadise.com/programming/pygame/part6
import pygame

pygame.init()

# Create window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# Canvas - separate surface so drawings are saved between frames
canvas = pygame.Surface((800, 600))
canvas.fill((255, 255, 255))

# Drawing settings
color = (0, 0, 0)     # current color - black
radius = 5             # brush size
mode = 'pen'           # current mode: pen, rect, circle, eraser
drawing = False        # is mouse button held down
start_pos = None       # start position for rect/circle

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard - select mode and color
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: mode = 'pen'
            if event.key == pygame.K_r: mode = 'rect'
            if event.key == pygame.K_o: mode = 'circle'
            if event.key == pygame.K_e: mode = 'eraser'
            if event.key == pygame.K_c: canvas.fill((255, 255, 255))  # clear

            # Colors: keys 1-7
            if event.key == pygame.K_1: color = (0, 0, 0)        # black
            if event.key == pygame.K_2: color = (255, 0, 0)      # red
            if event.key == pygame.K_3: color = (0, 255, 0)      # green
            if event.key == pygame.K_4: color = (0, 0, 255)      # blue
            if event.key == pygame.K_5: color = (255, 255, 0)    # yellow
            if event.key == pygame.K_6: color = (255, 0, 255)    # pink
            if event.key == pygame.K_7: color = (0, 255, 255)    # cyan

        # Mouse button pressed - start drawing
        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            start_pos = event.pos

        # Mouse moving while button held - draw for pen/eraser
        if event.type == pygame.MOUSEMOTION and drawing:
            if mode == 'pen':
                pygame.draw.circle(canvas, color, event.pos, radius)
            if mode == 'eraser':
                pygame.draw.circle(canvas, (255, 255, 255), event.pos, radius * 3)

        # Mouse button released - draw shape for rect/circle
        if event.type == pygame.MOUSEBUTTONUP and drawing:
            drawing = False
            end_pos = event.pos

            if mode == 'rect':
                x = min(start_pos[0], end_pos[0])
                y = min(start_pos[1], end_pos[1])
                w = abs(end_pos[0] - start_pos[0])
                h = abs(end_pos[1] - start_pos[1])
                pygame.draw.rect(canvas, color, (x, y, w, h), 2)

            if mode == 'circle':
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                r = int((dx**2 + dy**2) ** 0.5)
                pygame.draw.circle(canvas, color, start_pos, r, 2)

    # Show canvas on screen
    screen.blit(canvas, (0, 0))

    # Toolbar at top
    info = f"Mode: {mode} | P=Pen R=Rect O=Circle E=Eraser C=Clear | 1-7=Colors"
    screen.blit(font.render(info, True, (0, 0, 0), (220, 220, 220)), (5, 5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
