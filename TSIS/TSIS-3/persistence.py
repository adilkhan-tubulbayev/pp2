import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
LEADERBOARD_FILE = os.path.join(DATA_DIR, 'leaderboard.json')

# These are the default values when no settings file exists yet
DEFAULT_SETTINGS = {
    "sound": False,
    "car_color": "blue",    # choices: blue, red, green
    "difficulty": "normal"  # choices: easy, normal, hard
}


def load_settings():
    """Load settings from file. If file missing, return defaults."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Write settings dict to the JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


def load_leaderboard():
    """Load leaderboard list from file. Returns empty list if file missing."""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    return []


def save_leaderboard(entries):
    """Sort entries by score descending and keep only the top 10."""
    os.makedirs(DATA_DIR, exist_ok=True)
    entries.sort(key=lambda x: x['score'], reverse=True)
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(entries[:10], f, indent=2)
