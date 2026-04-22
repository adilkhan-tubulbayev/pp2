# Practice 10: Game Development with Pygame - Part 2

Three extended pygame games: racer, snake, and paint app.

## Repository Structure

```
Practice-10/
├── racer/
│   └── main.py       # Racing game with coins
├── snake/
│   └── main.py       # Snake with walls, levels, speed
├── paint/
│   └── main.py       # Paint app with shapes, eraser, colors
└── README.md
```

## How to Run

```bash
pip install pygame
cd racer && python main.py
cd snake && python main.py
cd paint && python main.py
```

## Features

### Racer
- Player car moves left/right with arrow keys
- Enemy cars come from top, avoid them
- Coins appear randomly on the road
- Coin counter in top right corner
- Speed increases over time

### Snake
- Arrow keys to move
- Border walls (collision = game over)
- Food spawns away from walls and snake body
- Level up every 4 foods eaten
- Extra walls appear at higher levels
- Speed increases with each level
- Score and level counter displayed

### Paint
- **P** = Pen, **R** = Rectangle, **O** = Circle, **E** = Eraser
- **1-8** = Color selection (black, red, green, blue, yellow, magenta, cyan, orange)
- **+/-** = Brush size
- **C** = Clear canvas
- **ESC** = Quit

## Resources

- [Coderslegacy Pygame Tutorial](https://coderslegacy.com/python/python-pygame-tutorial/)
- [Nerd Paradise Paint Tutorial](https://nerdparadise.com/programming/pygame/part6)
- [Pygame Documentation](https://www.pygame.org/docs/)
