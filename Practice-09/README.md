# Practice 9: Game Development with Pygame - Part 1

Three pygame applications: clock, music player, and moving ball game.

## Repository Structure

```
Practice-09/
├── mickeys_clock/
│   ├── main.py              # Analog clock with rotating hands
│   └── images/
│       └── mickeyclock.jpeg  # Reference image
├── music_player/
│   ├── main.py              # Keyboard-controlled music player
│   └── music/               # Put .mp3/.wav/.ogg files here
├── moving_ball/
│   └── main.py              # Red ball moved by arrow keys
├── requirements.txt
└── README.md
```

## How to Run

```bash
pip install pygame
cd mickeys_clock && python main.py    # Clock
cd music_player && python main.py     # Music player (add .wav files to music/)
cd moving_ball && python main.py      # Moving ball (arrow keys)
```

## Controls

- **Music Player**: P=Play, S=Stop, N=Next, B=Back, Q=Quit
- **Moving Ball**: Arrow keys, ball stays within screen boundaries

## Resources

- [Nerd Paradise Pygame Tutorial](https://nerdparadise.com/programming/pygame)
- [Pygame Documentation](https://www.pygame.org/docs/)
