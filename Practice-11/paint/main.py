# Paint app - Practice 11
# Extended from Practice 10: added square, right triangle, equilateral triangle, rhombus

import pygame
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 13)

# Separate surface so drawings persist between frames
canvas = pygame.Surface((800, 600))
canvas.fill((255, 255, 255))

color = (0, 0, 0)
radius = 5
mode = 'pen'
drawing = False
start_pos = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Original modes
            if event.key == pygame.K_p: mode = 'pen'
            if event.key == pygame.K_r: mode = 'rect'
            if event.key == pygame.K_o: mode = 'circle'
            if event.key == pygame.K_e: mode = 'eraser'
            # New shape modes
            if event.key == pygame.K_s: mode = 'square'      # S = square
            if event.key == pygame.K_t: mode = 'rtriangle'   # T = right triangle
            if event.key == pygame.K_g: mode = 'etriangle'   # G = equilateral triangle
            if event.key == pygame.K_d: mode = 'rhombus'     # D = rhombus (diamond)

            if event.key == pygame.K_c: canvas.fill((255, 255, 255))  # clear

            # Colors 1-7
            if event.key == pygame.K_1: color = (0, 0, 0)
            if event.key == pygame.K_2: color = (255, 0, 0)
            if event.key == pygame.K_3: color = (0, 200, 0)
            if event.key == pygame.K_4: color = (0, 0, 255)
            if event.key == pygame.K_5: color = (255, 255, 0)
            if event.key == pygame.K_6: color = (255, 0, 255)
            if event.key == pygame.K_7: color = (0, 255, 255)

        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            start_pos = event.pos

        # Pen and eraser draw while dragging
        if event.type == pygame.MOUSEMOTION and drawing:
            if mode == 'pen':
                pygame.draw.circle(canvas, color, event.pos, radius)
            if mode == 'eraser':
                pygame.draw.circle(canvas, (255, 255, 255), event.pos, radius * 3)

        # Shapes are drawn on mouse release
        if event.type == pygame.MOUSEBUTTONUP and drawing:
            drawing = False
            sx, sy = start_pos
            ex, ey = event.pos

            if mode == 'rect':
                x = min(sx, ex); y = min(sy, ey)
                w = abs(ex - sx); h = abs(ey - sy)
                pygame.draw.rect(canvas, color, (x, y, w, h), 2)

            elif mode == 'circle':
                r = int(((ex - sx) ** 2 + (ey - sy) ** 2) ** 0.5)
                pygame.draw.circle(canvas, color, (sx, sy), r, 2)

            elif mode == 'square':
                # Force equal width and height - use the smaller side
                side = min(abs(ex - sx), abs(ey - sy))
                # Respect drag direction so shape goes where user aimed
                x = sx if ex >= sx else sx - side
                y = sy if ey >= sy else sy - side
                pygame.draw.rect(canvas, color, (x, y, side, side), 2)

            elif mode == 'rtriangle':
                # Right angle at the start corner
                # Three points: start, directly below start, directly right of start
                p1 = (sx, sy)   # right-angle corner (top-left of bounding box)
                p2 = (sx, ey)   # bottom-left
                p3 = (ex, sy)   # top-right
                pygame.draw.polygon(canvas, color, [p1, p2, p3], 2)

            elif mode == 'etriangle':
                # Equilateral triangle: horizontal drag defines the base length
                base = abs(ex - sx)
                height = int(base * math.sqrt(3) / 2)
                # Base is at the bottom, apex is above
                left  = min(sx, ex)
                right = max(sx, ex)
                p1 = (left,  sy + height)   # bottom-left
                p2 = (right, sy + height)   # bottom-right
                p3 = ((left + right) // 2, sy)  # apex at top-center
                pygame.draw.polygon(canvas, color, [p1, p2, p3], 2)

            elif mode == 'rhombus':
                # Rhombus: four vertices at midpoints of the bounding box edges
                mx = (sx + ex) // 2  # horizontal center
                my = (sy + ey) // 2  # vertical center
                top    = (mx, sy)
                right  = (ex, my)
                bottom = (mx, ey)
                left   = (sx, my)
                pygame.draw.polygon(canvas, color, [top, right, bottom, left], 2)

    screen.blit(canvas, (0, 0))

    # Toolbar (drawn on top of canvas so it's always visible)
    bar = (210, 210, 210)
    screen.blit(font.render("P=Pen  R=Rect  O=Circle  E=Eraser  S=Square  T=RightTri  G=EqTri  D=Rhombus  C=Clear", True, (0, 0, 0), bar), (5, 5))
    screen.blit(font.render("1=Black  2=Red  3=Green  4=Blue  5=Yellow  6=Pink  7=Cyan", True, (0, 0, 0), bar), (5, 20))
    screen.blit(font.render(f"Mode: {mode}", True, (180, 0, 0), bar), (5, 35))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
