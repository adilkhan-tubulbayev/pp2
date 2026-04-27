import pygame
import math
from datetime import datetime

pygame.init()

# Window and canvas setup
SCREEN_W, SCREEN_H = 800, 650
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint App - TSIS 2")

# Canvas is a separate surface (800x600), drawn onto the screen below the toolbar
canvas = pygame.Surface((800, 600))
canvas.fill((255, 255, 255))

# Fonts
font = pygame.font.SysFont("Arial", 12)
font_text = pygame.font.SysFont("Arial", 20)

# Color palette: keys 1-7
colors = {
    pygame.K_1: (0, 0, 0),        # black
    pygame.K_2: (255, 0, 0),      # red
    pygame.K_3: (0, 200, 0),      # green
    pygame.K_4: (0, 0, 255),      # blue
    pygame.K_5: (255, 255, 0),    # yellow
    pygame.K_6: (255, 105, 180),  # pink
    pygame.K_7: (0, 255, 255),    # cyan
}

# Current drawing state
color = (0, 0, 0)
mode = 'pen'
brush_size = 5

# Mouse dragging state
drawing = False
start_pos = None
prev_pos = None

# Text tool state
text_active = False
text_pos = None
text_input = ''


def flood_fill(surface, x, y, fill_color):
    """Fill a region with fill_color starting from (x, y)."""
    target = surface.get_at((x, y))[:3]
    fill = fill_color[:3] if len(fill_color) > 3 else fill_color
    if target == fill:
        return
    W, H = surface.get_size()
    stack = [(x, y)]
    visited = set()
    visited.add((x, y))
    while stack:
        cx, cy = stack.pop()
        surface.set_at((cx, cy), fill_color)
        for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in visited:
                if surface.get_at((nx, ny))[:3] == target:
                    visited.add((nx, ny))
                    stack.append((nx, ny))


def canvas_pos(screen_x, screen_y):
    """Convert screen coordinates to canvas coordinates (canvas starts at y=50)."""
    return screen_x, screen_y - 50


def draw_toolbar():
    """Draw the toolbar background and instruction text."""
    pygame.draw.rect(screen, (220, 220, 220), (0, 0, SCREEN_W, 50))
    line1 = "P=Pen L=Line R=Rect O=Circle E=Eraser S=Square T=RTri G=EqTri D=Rhombus F=Fill X=Text C=Clear"
    line2 = "[=Small ]=Med  \\=Large | 1-7=Colors | Ctrl+S=Save"
    typing_hint = "Typing: " + text_input if text_active else ''
    line3 = f"Mode: {mode} | Size: {brush_size} | {typing_hint}"
    screen.blit(font.render(line1, True, (0, 0, 0)), (4, 4))
    screen.blit(font.render(line2, True, (0, 0, 0)), (4, 18))
    screen.blit(font.render(line3, True, (50, 50, 200)), (4, 32))


def draw_shape_preview(surf, sx, sy, ex, ey):
    """Draw the current shape preview from start to end point onto surf."""
    if mode == 'rect':
        x = min(sx, ex)
        y = min(sy, ey)
        w = abs(ex - sx)
        h = abs(ey - sy)
        pygame.draw.rect(surf, color, (x, y, w, h), brush_size)

    elif mode == 'circle':
        cx = (sx + ex) // 2
        cy = (sy + ey) // 2
        rx = abs(ex - sx) // 2
        ry = abs(ey - sy) // 2
        r = max(rx, ry)
        pygame.draw.circle(surf, color, (cx, cy), r, brush_size)

    elif mode == 'square':
        side = max(abs(ex - sx), abs(ey - sy))
        dx = side if ex >= sx else -side
        dy = side if ey >= sy else -side
        x = min(sx, sx + dx)
        y = min(sy, sy + dy)
        pygame.draw.rect(surf, color, (x, y, side, side), brush_size)

    elif mode == 'rtriangle':
        # Right angle at start corner
        p1 = (sx, sy)
        p2 = (ex, sy)
        p3 = (sx, ey)
        pygame.draw.polygon(surf, color, [p1, p2, p3], brush_size)

    elif mode == 'eqtriangle':
        # Base is horizontal drag; height = base * sqrt(3) / 2
        base = abs(ex - sx)
        height = int(base * math.sqrt(3) / 2)
        top_x = (sx + ex) // 2
        top_y = sy - height
        p1 = (sx, sy)
        p2 = (ex, sy)
        p3 = (top_x, top_y)
        pygame.draw.polygon(surf, color, [p1, p2, p3], brush_size)

    elif mode == 'rhombus':
        # Vertices at midpoints of bounding box edges
        mx = (sx + ex) // 2
        my = (sy + ey) // 2
        p1 = (mx, sy)   # top
        p2 = (ex, my)   # right
        p3 = (mx, ey)   # bottom
        p4 = (sx, my)   # left
        pygame.draw.polygon(surf, color, [p1, p2, p3, p4], brush_size)

    elif mode == 'line':
        pygame.draw.line(surf, color, (sx, sy), (ex, ey), brush_size)


clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)

    # Get current mouse position in canvas coordinates
    mx, my = pygame.mouse.get_pos()
    cmx, cmy = canvas_pos(mx, my)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---- Keyboard events ----
        elif event.type == pygame.KEYDOWN:

            # Text tool input takes priority when text_active
            if text_active:
                if event.key == pygame.K_RETURN:
                    # Render text permanently onto canvas
                    text_surface = font_text.render(text_input, True, color)
                    canvas.blit(text_surface, text_pos)
                    text_active = False
                    text_input = ''
                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_input = ''
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        text_input += event.unicode
                continue  # Skip mode-switching keys while typing

            # Save canvas with Ctrl+S
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"canvas_{timestamp}.png"
                pygame.image.save(canvas, filename)
                print(f"Canvas saved as {filename}")
                continue

            # Mode switches
            if event.key == pygame.K_p:
                mode = 'pen'
            elif event.key == pygame.K_l:
                mode = 'line'
            elif event.key == pygame.K_r:
                mode = 'rect'
            elif event.key == pygame.K_o:
                mode = 'circle'
            elif event.key == pygame.K_e:
                mode = 'eraser'
            elif event.key == pygame.K_s:
                mode = 'square'
            elif event.key == pygame.K_t:
                mode = 'rtriangle'
            elif event.key == pygame.K_g:
                mode = 'eqtriangle'
            elif event.key == pygame.K_d:
                mode = 'rhombus'
            elif event.key == pygame.K_f:
                mode = 'fill'
            elif event.key == pygame.K_x:
                mode = 'text'
            elif event.key == pygame.K_c:
                canvas.fill((255, 255, 255))

            # Brush sizes
            elif event.key == pygame.K_LEFTBRACKET:
                brush_size = 2
            elif event.key == pygame.K_RIGHTBRACKET:
                brush_size = 5
            elif event.key == pygame.K_BACKSLASH:
                brush_size = 10

            # Color keys 1-7
            elif event.key in colors:
                color = colors[event.key]

        # ---- Mouse button down ----
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Ignore clicks in the toolbar area
                if my < 50:
                    continue

                cx, cy = canvas_pos(event.pos[0], event.pos[1])

                if mode == 'fill':
                    # Flood fill at click position
                    if 0 <= cx < 800 and 0 <= cy < 600:
                        flood_fill(canvas, cx, cy, color)

                elif mode == 'text':
                    # Start text input at this position
                    text_pos = (cx, cy)
                    text_input = ''
                    text_active = True

                else:
                    # Begin drawing for all other modes
                    drawing = True
                    start_pos = (cx, cy)
                    prev_pos = (cx, cy)

        # ---- Mouse motion ----
        elif event.type == pygame.MOUSEMOTION:
            if drawing and my >= 50:
                cx, cy = canvas_pos(event.pos[0], event.pos[1])

                if mode == 'pen':
                    # Draw a line from previous position to current (smooth pencil)
                    if prev_pos is not None:
                        pygame.draw.line(canvas, color, prev_pos, (cx, cy), brush_size)
                    prev_pos = (cx, cy)

                elif mode == 'eraser':
                    # Erase by drawing white circles
                    if prev_pos is not None:
                        pygame.draw.line(canvas, (255, 255, 255), prev_pos, (cx, cy), brush_size * 3)
                    prev_pos = (cx, cy)

                else:
                    # Shape modes: just update prev_pos for preview
                    prev_pos = (cx, cy)

        # ---- Mouse button up ----
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                cx, cy = canvas_pos(event.pos[0], event.pos[1])

                if mode in ('rect', 'circle', 'square', 'rtriangle', 'eqtriangle', 'rhombus', 'line'):
                    # Draw final shape permanently onto canvas
                    sx, sy = start_pos
                    draw_shape_preview(canvas, sx, sy, cx, cy)

                drawing = False
                start_pos = None
                prev_pos = None

    # ---- Draw everything to screen ----

    # Draw canvas onto screen (canvas starts 50px down for toolbar)
    screen.blit(canvas, (0, 50))

    # Live preview for shapes being dragged (drawn on screen, not canvas)
    if drawing and start_pos is not None and mode in ('rect', 'circle', 'square', 'rtriangle', 'eqtriangle', 'rhombus', 'line'):
        sx, sy = start_pos
        ex, ey = cmx, cmy
        draw_shape_preview(screen, sx + 0, sy + 50, ex, ey + 50)

    # Live text preview (drawn on screen, not canvas)
    if text_active and text_pos is not None:
        preview = font_text.render(text_input + "|", True, color)
        # text_pos is in canvas coords, add 50 to get screen coords
        screen.blit(preview, (text_pos[0], text_pos[1] + 50))

    # Draw toolbar on top
    draw_toolbar()

    pygame.display.flip()

pygame.quit()
