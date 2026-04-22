import pygame
import os

pygame.init()
pygame.mixer.init()

# Create window
screen = pygame.display.set_mode((400, 250))
pygame.display.set_caption("Music Player")
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()

# Load all music files from music/ folder
playlist = []
if os.path.exists("music"):
    for f in sorted(os.listdir("music")):
        if f.endswith(('.mp3', '.wav', '.ogg')):
            playlist.append("music/" + f)

# Player state
current = 0
playing = False

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # P - play current track
            if event.key == pygame.K_p and playlist:
                pygame.mixer.music.load(playlist[current])
                pygame.mixer.music.play()
                playing = True

            # S - stop
            elif event.key == pygame.K_s:
                pygame.mixer.music.stop()
                playing = False

            # N - next track
            elif event.key == pygame.K_n and playlist:
                current = (current + 1) % len(playlist)
                pygame.mixer.music.load(playlist[current])
                pygame.mixer.music.play()
                playing = True

            # B - previous track
            elif event.key == pygame.K_b and playlist:
                current = (current - 1) % len(playlist)
                pygame.mixer.music.load(playlist[current])
                pygame.mixer.music.play()
                playing = True

            # Q - quit
            elif event.key == pygame.K_q:
                running = False

    # Draw interface
    screen.fill((255, 255, 255))

    # Track name
    name = os.path.basename(playlist[current]) if playlist else "No tracks"
    screen.blit(font.render(f"Track: {name}", True, (0, 0, 0)), (20, 20))
    screen.blit(font.render(f"Track {current + 1} of {len(playlist)}", True, (100, 100, 100)), (20, 50))

    # Status
    status_color = (0, 180, 0) if playing else (200, 0, 0)
    status_text = "Playing" if playing else "Stopped"
    screen.blit(font.render(f"Status: {status_text}", True, status_color), (20, 90))

    # Controls help
    screen.blit(font.render("P=Play  S=Stop  N=Next  B=Back  Q=Quit", True, (100, 100, 100)), (20, 140))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
