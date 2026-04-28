import math
import pygame


def flood_fill(surface, start_x, start_y, fill_color):
    """Flood fill from one pixel using exact color matching."""
    width, height = surface.get_size()

    if not (0 <= start_x < width and 0 <= start_y < height):
        return

    target_color = surface.get_at((start_x, start_y))[:3]
    new_color = fill_color[:3]

    if target_color == new_color:
        return

    stack = [(start_x, start_y)]
    surface.set_at((start_x, start_y), new_color)

    while stack:
        x, y = stack.pop()

        for next_x, next_y in (
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ):
            if not (0 <= next_x < width and 0 <= next_y < height):
                continue

            if surface.get_at((next_x, next_y))[:3] == target_color:
                surface.set_at((next_x, next_y), new_color)
                stack.append((next_x, next_y))


def draw_shape(surface, tool, color, size, start_pos, end_pos):
    """Shared drawing code for line and shape tools."""
    start_x, start_y = start_pos
    end_x, end_y = end_pos

    if tool == "line":
        pygame.draw.line(surface, color, start_pos, end_pos, size)

    elif tool == "rectangle":
        x = min(start_x, end_x)
        y = min(start_y, end_y)
        width = abs(end_x - start_x)
        height = abs(end_y - start_y)
        pygame.draw.rect(surface, color, (x, y, width, height), size)

    elif tool == "circle":
        center_x = (start_x + end_x) // 2
        center_y = (start_y + end_y) // 2
        radius = max(abs(end_x - start_x), abs(end_y - start_y)) // 2
        pygame.draw.circle(surface, color, (center_x, center_y), radius, size)

    elif tool == "square":
        side = max(abs(end_x - start_x), abs(end_y - start_y))
        x = start_x if end_x >= start_x else start_x - side
        y = start_y if end_y >= start_y else start_y - side
        pygame.draw.rect(surface, color, (x, y, side, side), size)

    elif tool == "right triangle":
        points = [
            (start_x, start_y),
            (end_x, start_y),
            (start_x, end_y),
        ]
        pygame.draw.polygon(surface, color, points, size)

    elif tool == "equilateral triangle":
        base = abs(end_x - start_x)
        height = int(base * math.sqrt(3) / 2)
        top_x = (start_x + end_x) // 2

        if end_y >= start_y:
            top_y = start_y - height
            base_y = start_y
        else:
            top_y = start_y + height
            base_y = start_y

        points = [
            (start_x, base_y),
            (end_x, base_y),
            (top_x, top_y),
        ]
        pygame.draw.polygon(surface, color, points, size)

    elif tool == "rhombus":
        middle_x = (start_x + end_x) // 2
        middle_y = (start_y + end_y) // 2
        points = [
            (middle_x, start_y),
            (end_x, middle_y),
            (middle_x, end_y),
            (start_x, middle_y),
        ]
        pygame.draw.polygon(surface, color, points, size)
