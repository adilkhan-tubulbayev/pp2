import os
import pygame
from datetime import datetime

from tools import draw_shape, flood_fill


pygame.init()

# Toolbar sits above the canvas, so mouse y needs an offset.
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 720
TOOLBAR_HEIGHT = 105
CANVAS_COLOR = (255, 255, 255)
SAVE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_images")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TSIS 2 Paint")

# Drawings live on this surface. The main screen is only for displaying it.
canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(CANVAS_COLOR)

button_font = pygame.font.SysFont("Arial", 13)
small_font = pygame.font.SysFont("Arial", 11)
text_font = pygame.font.SysFont("Arial", 24)
status_font = pygame.font.SysFont("Arial", 14)

# Each tool has an internal name, a keyboard shortcut, and a button label.
tools = [
    ("pencil", pygame.K_p, "P Pencil"),
    ("line", pygame.K_l, "L Line"),
    ("rectangle", pygame.K_r, "R Rectangle"),
    ("circle", pygame.K_o, "O Circle"),
    ("square", pygame.K_s, "S Square"),
    ("right triangle", pygame.K_t, "T Right triangle"),
    ("equilateral triangle", pygame.K_g, "G Equilateral"),
    ("rhombus", pygame.K_d, "D Rhombus"),
    ("eraser", pygame.K_e, "E Eraser"),
    ("fill", pygame.K_f, "F Fill"),
    ("text", pygame.K_x, "X Text"),
]

# These tools are previewed while dragging and committed on mouse release.
shape_tools = {
    "line",
    "rectangle",
    "circle",
    "square",
    "right triangle",
    "equilateral triangle",
    "rhombus",
}

colors = [
    ((0, 0, 0), "Black"),
    ((220, 0, 0), "Red"),
    ((0, 150, 0), "Green"),
    ((0, 70, 220), "Blue"),
    ((240, 210, 0), "Yellow"),
    ((230, 80, 170), "Pink"),
    ((0, 180, 200), "Cyan"),
]

brush_sizes = [
    (2, pygame.K_1, "1 Small"),
    (5, pygame.K_2, "2 Medium"),
    (10, pygame.K_3, "3 Large"),
]

# Current choices from the toolbar.
current_tool = "pencil"
current_color = (0, 0, 0)
brush_size = 5

# start_pos is for shapes, previous_pos is for smooth pencil lines.
drawing = False
start_pos = None
previous_pos = None

# Text is temporary until Enter, so Escape can still cancel it.
text_active = False
text_pos = None
text_value = ""

# Used for the short "saved" message in the toolbar.
message = ""
message_until = 0
tool_buttons = []
color_buttons = []
size_buttons = []
clear_button = pygame.Rect(0, 0, 0, 0)
save_button = pygame.Rect(0, 0, 0, 0)


def screen_to_canvas(screen_x, screen_y):
    """Convert window coordinates to canvas coordinates."""
    return screen_x, screen_y - TOOLBAR_HEIGHT


def is_on_canvas(pos):
    """Return True when the mouse is inside the drawable area."""
    x, y = screen_to_canvas(pos[0], pos[1])
    return 0 <= x < canvas.get_width() and 0 <= y < canvas.get_height()


def add_tool_buttons():
    """Create the clickable areas for the toolbar."""
    global clear_button, save_button

    x = 8
    y = 6
    tool_buttons.clear()

    for tool_name, key, label in tools:
        button_width = button_font.size(label)[0] + 18

        if x + button_width > SCREEN_WIDTH - 8:
            x = 8
            y += 34

        rect = pygame.Rect(x, y, button_width, 28)
        tool_buttons.append((rect, tool_name, label))
        x += button_width + 6

    x = 8
    y = 72
    color_buttons.clear()

    for color, name in colors:
        rect = pygame.Rect(x, y, 28, 24)
        color_buttons.append((rect, color, name))
        x += 34

    x += 18
    size_buttons.clear()

    for size, key, label in brush_sizes:
        rect = pygame.Rect(x, y, 82, 24)
        size_buttons.append((rect, size, label))
        x += 88

    x += 18
    clear_button = pygame.Rect(x, y, 62, 24)
    save_button = pygame.Rect(x + 68, y, 62, 24)


def draw_button(rect, label, active=False):
    """Draw one simple toolbar button."""
    if active:
        background = (70, 120, 210)
        text_color = (255, 255, 255)
    else:
        background = (255, 255, 255)
        text_color = (20, 20, 20)

    pygame.draw.rect(screen, background, rect)
    pygame.draw.rect(screen, (150, 150, 150), rect, 1)

    text = button_font.render(label, True, text_color)
    text_x = rect.centerx - text.get_width() // 2
    text_y = rect.centery - text.get_height() // 2
    screen.blit(text, (text_x, text_y))


def draw_toolbar():
    """Redraw the toolbar every frame so active buttons stay visible."""
    pygame.draw.rect(screen, (235, 235, 235), (0, 0, SCREEN_WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(screen, (150, 150, 150), (0, TOOLBAR_HEIGHT - 1), (SCREEN_WIDTH, TOOLBAR_HEIGHT - 1))

    for rect, tool_name, label in tool_buttons:
        draw_button(rect, label, current_tool == tool_name)

    for rect, color, name in color_buttons:
        pygame.draw.rect(screen, color, rect)
        border_size = 3 if current_color == color else 1
        pygame.draw.rect(screen, (0, 0, 0), rect, border_size)

    for rect, size, label in size_buttons:
        draw_button(rect, label, brush_size == size)

    draw_button(clear_button, "C Clear")
    draw_button(save_button, "Save")

    status = f"Tool: {current_tool}   Size: {brush_size}px   Ctrl+S saves PNG"
    if text_active:
        status += "   Type text, Enter confirms, Esc cancels"

    status_text = status_font.render(status, True, (20, 20, 20))
    screen.blit(status_text, (save_button.right + 18, 76))

    if message and pygame.time.get_ticks() < message_until:
        saved_text = small_font.render(message, True, (20, 20, 20))
        screen.blit(saved_text, (SCREEN_WIDTH - saved_text.get_width() - 12, TOOLBAR_HEIGHT - 24))


def save_canvas():
    """Save canvas as a timestamped PNG file."""
    global message, message_until

    os.makedirs(SAVE_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"canvas_{timestamp}.png"
    path = os.path.join(SAVE_FOLDER, filename)
    pygame.image.save(canvas, path)

    message = f"Saved: saved_images/{filename}"
    message_until = pygame.time.get_ticks() + 2500


add_tool_buttons()

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Text mode uses normal typing keys, so shortcuts are ignored here.
            if text_active:
                if event.key == pygame.K_RETURN:
                    rendered_text = text_font.render(text_value, True, current_color)
                    canvas.blit(rendered_text, text_pos)
                    text_active = False
                    text_value = ""
                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_value = ""
                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]
                elif event.unicode and event.unicode.isprintable():
                    text_value += event.unicode
                continue

            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                save_canvas()
                continue

            # Single-letter shortcuts are faster during a live demo.
            for tool_name, key, label in tools:
                if event.key == key:
                    current_tool = tool_name
                    break

            # Required brush sizes: small, medium, large.
            for size_px, key, label in brush_sizes:
                if event.key == key:
                    brush_size = size_px

            if event.key == pygame.K_c:
                canvas.fill(CANVAS_COLOR)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Toolbar clicks should not draw on the canvas.
            if mouse_pos[1] < TOOLBAR_HEIGHT:
                for rect, tool_name, label in tool_buttons:
                    if rect.collidepoint(mouse_pos):
                        current_tool = tool_name

                for rect, color, name in color_buttons:
                    if rect.collidepoint(mouse_pos):
                        current_color = color

                for rect, size, label in size_buttons:
                    if rect.collidepoint(mouse_pos):
                        brush_size = size

                if clear_button.collidepoint(mouse_pos):
                    canvas.fill(CANVAS_COLOR)

                if save_button.collidepoint(mouse_pos):
                    save_canvas()

                continue

            click_x, click_y = screen_to_canvas(*mouse_pos)

            if current_tool == "fill":
                flood_fill(canvas, click_x, click_y, current_color)
            elif current_tool == "text":
                text_pos = (click_x, click_y)
                text_value = ""
                text_active = True
            else:
                drawing = True
                start_pos = (click_x, click_y)
                previous_pos = (click_x, click_y)

        elif event.type == pygame.MOUSEMOTION:
            if drawing and is_on_canvas(mouse_pos):
                current_x, current_y = screen_to_canvas(*mouse_pos)

                # Line segments between old and new mouse positions make freehand smooth.
                if current_tool == "pencil":
                    pygame.draw.line(canvas, current_color, previous_pos, (current_x, current_y), brush_size)
                elif current_tool == "eraser":
                    pygame.draw.line(canvas, CANVAS_COLOR, previous_pos, (current_x, current_y), brush_size)

                previous_pos = (current_x, current_y)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing:
                end_x, end_y = screen_to_canvas(*mouse_pos)

                # The final shape is drawn once, after the drag is finished.
                if current_tool in shape_tools:
                    draw_shape(canvas, current_tool, current_color, brush_size, start_pos, (end_x, end_y))

                drawing = False
                start_pos = None
                previous_pos = None

    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    # Preview goes to the screen only, so moving the mouse does not leave marks.
    if drawing and current_tool in shape_tools and start_pos:
        canvas_mouse = screen_to_canvas(*mouse_pos)
        preview_start = (start_pos[0], start_pos[1] + TOOLBAR_HEIGHT)
        preview_end = (canvas_mouse[0], canvas_mouse[1] + TOOLBAR_HEIGHT)
        draw_shape(screen, current_tool, current_color, brush_size, preview_start, preview_end)

    # The blinking cursor is just part of the preview text.
    if text_active and text_pos:
        cursor = "|" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
        preview_text = text_font.render(text_value + cursor, True, current_color)
        screen.blit(preview_text, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

    draw_toolbar()

    pygame.display.flip()

pygame.quit()
