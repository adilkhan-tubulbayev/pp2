import psycopg2
import os
from config import load_config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def init_db():
    """Run schema.sql so the game can save scores."""
    config = load_config()
    schema_path = os.path.join(BASE_DIR, "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as file:
        schema_sql = file.read()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()


def get_or_create_player(username):
    """Return the player id, creating the player when needed."""
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute("INSERT INTO players(username) VALUES(%s) RETURNING id", (username,))
            pid = cur.fetchone()[0]
        conn.commit()
    return pid

def save_session(username, score, level):
    """Store one finished game."""
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                pid = row[0]
            else:
                cur.execute("INSERT INTO players(username) VALUES(%s) RETURNING id", (username,))
                pid = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO game_sessions(player_id, score, level_reached) VALUES(%s, %s, %s)",
                (pid, score, level)
            )
        conn.commit()

def get_leaderboard(limit=10):
    """Read the best scores for the leaderboard screen."""
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.username, gs.score, gs.level_reached, gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()

def get_personal_best(username):
    """Return this player's best score, or zero before their first game."""
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT MAX(gs.score)
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    WHERE p.username = %s
                """, (username,))
                result = cur.fetchone()[0]
                return result if result else 0
    except:
        return 0
