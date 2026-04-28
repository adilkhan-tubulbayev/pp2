import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
LEADERBOARD_FILE = os.path.join(DATA_DIR, 'leaderboard.json')

# First run defaults.
DEFAULT_SETTINGS = {
    "sound": False,
    "car_color": "blue",    # choices: blue, red, green
    "difficulty": "normal"  # choices: easy, normal, hard
}


def load_settings():
    """Read settings.json, or use defaults on the first run."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Save menu settings between runs."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


def load_leaderboard():
    """Read saved scores, or start with an empty board."""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    return []


def save_leaderboard(entries):
    """Keep only the best ten results in the JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    entries.sort(key=lambda x: x['score'], reverse=True)
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(entries[:10], f, indent=2)
