import pygame
import math
import time

pygame.init()

# Create window
screen = pygame.display.set_mode((500, 550))
pygame.display.set_caption("Mickey's Clock")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)

# Load background (Mickey image)
bg = pygame.image.load("images/mickeyclock.jpeg")
bg = pygame.transform.scale(bg, (500, 500))

# Load hand images
right_hand = pygame.image.load("images/right-hand.png")
right_hand = pygame.transform.scale(right_hand, (55, 75))

left_hand = pygame.image.load("images/left-hand.png")
left_hand = pygame.transform.flip(left_hand, True, False)  # flip horizontally for left hand
left_hand = pygame.transform.scale(left_hand, (55, 75))

# Clock center (Mickey's shoulders)
CENTER = (250, 260)

# Create arm sprite: hand image on top + arm line down to pivot point
def make_arm(hand_img, length):
    surface = pygame.Surface((80, length), pygame.SRCALPHA)
    # Arm line (from hand down to pivot point)
    pygame.draw.line(surface, (0, 0, 0), (40, 55), (40, length), 5)
    # Hand image at top center
    surface.blit(hand_img, (40 - hand_img.get_width() // 2, 0))
    return surface

# Minute arm (right) is longer, second arm (left) is shorter
minute_arm = make_arm(right_hand, 170)
second_arm = make_arm(left_hand, 145)

# Draw arm rotated to the given angle
def draw_arm(arm, angle):
    # Rotate image (pygame rotates counter-clockwise, so we negate)
    rotated = pygame.transform.rotate(arm, -angle)
    # Calculate offset so pivot stays at CENTER
    offset = pygame.math.Vector2(0, -arm.get_height() // 2).rotate(angle)
    rect = rotated.get_rect(center=(CENTER[0] + offset.x, CENTER[1] + offset.y))
    screen.blit(rotated, rect)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw background
    screen.fill((255, 255, 255))
    screen.blit(bg, (0, 0))

    # Get current time
    now = time.localtime()
    minutes = now.tm_min
    seconds = now.tm_sec

    # Calculate angles: 360 / 60 = 6 degrees per second/minute
    min_angle = minutes * 6 + seconds * 0.1
    sec_angle = seconds * 6

    # Draw arms
    draw_arm(minute_arm, min_angle)   # right hand = minutes
    draw_arm(second_arm, sec_angle)   # left hand = seconds

    # Center dot (shoulder)
    pygame.draw.circle(screen, (0, 0, 0), CENTER, 5)

    # Digital time at the bottom
    text = font.render(f"{minutes:02d}:{seconds:02d}", True, (0, 0, 0))
    screen.blit(text, (220, 510))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
