# TSIS Report — What Was Added vs Practice Base

## TSIS-1: PhoneBook

### Base (Practice 7–8)
| File | Feature |
|------|---------|
| phonebook.py | CRUD: insert, query by name/phone, update name/phone, delete by name/phone |
| phonebook.py | CSV import, console menu (10 options) |
| functions.sql | `search_contacts(pattern)` — searches name or phone |
| functions.sql | `get_contacts_paginated(limit, offset)` — returns id, name, phone |
| procedures.sql | `upsert_contact` — insert or update if name exists |
| procedures.sql | `insert_many_contacts` — bulk insert with phone validation |
| procedures.sql | `delete_contact` — delete by name or phone |

### Added in TSIS-1
| File | What was added |
|------|---------------|
| schema.sql | `groups` table (Family/Work/Friend/Other), `phones` table (multiple numbers per contact) |
| schema.sql | ALTER phonebook: added `email`, `birthday`, `group_id`, `created_at` columns |
| procedures.sql | `add_phone(name, phone, type)` — adds extra phone to existing contact |
| procedures.sql | `move_to_group(name, group)` — moves contact to group, creates group if missing |
| procedures.sql | `search_contacts` — UPDATED: now also searches email and all extra phones via JOIN |
| procedures.sql | `get_contacts_paginated` — UPDATED: now returns email, birthday, group_name |
| phonebook.py | `filter_by_group(group)` — show contacts from one category |
| phonebook.py | `search_by_email(pattern)` — partial email search |
| phonebook.py | `sort_contacts(by)` — sort by name / birthday / date added |
| phonebook.py | `paginated_nav()` — interactive next/prev/quit navigation using DB function |
| phonebook.py | `export_json()` — exports all contacts with phones and group to JSON |
| phonebook.py | `import_json()` — imports from JSON, asks skip/overwrite on duplicate |
| phonebook.py | `add_phone_menu()` / `move_group_menu()` — console wrappers for new procedures |
| contacts.csv | Extended with email, birthday, group columns |

---

## TSIS-2: Paint

### Base (Practice 10–11)
| Feature | Key |
|---------|-----|
| Pen (draw circles while dragging) | P |
| Rectangle | R |
| Circle | O |
| Eraser | E |
| Clear canvas | C |
| Colors 1–7 | 1–7 |
| Square | S |
| Right triangle | T |
| Equilateral triangle | G |
| Rhombus | D |

### Added in TSIS-2
| Feature | Key | Description |
|---------|-----|-------------|
| Pencil (smooth lines) | P | Uses `draw.line` between consecutive positions instead of circles |
| Straight line | L | Live preview while dragging, committed on release |
| Brush sizes | [ ] \ | Small (2px), Medium (5px), Large (10px) |
| Flood fill | F | BFS fill from click point with current color |
| Save canvas | Ctrl+S | Saves as `canvas_YYYYMMDD_HHMMSS.png` |
| Text tool | X | Click to place, type text, Enter to confirm, Esc to cancel |
| All shapes now respect brush_size | — | Width parameter applied to all shape outlines |

---

## TSIS-3: Racer

### Base (Practice 10–11)
| Feature | Description |
|---------|-------------|
| Player car | Left/right movement with arrow keys |
| One enemy car | Falls down, respawns at top, score++ on dodge |
| Weighted coins | 3 types (gold=1, orange=3, purple=5), 2 on screen |
| Enemy speed up | +1 speed every 5 coin points |
| Game over screen | Press any key to restart |

### Added in TSIS-3
| File | Feature |
|------|---------|
| main.py | State machine: menu → username → game → gameover → (leaderboard/settings) |
| ui.py | Main menu with Play, Leaderboard, Settings, Quit buttons + hover effects |
| ui.py | Username entry screen with blinking cursor |
| ui.py | Settings screen: sound toggle, car color (blue/red/green), difficulty (easy/normal/hard) |
| ui.py | Game over screen: score, distance, coins, Retry / Main Menu buttons |
| ui.py | Leaderboard screen: top 10 with rank, name, score, distance |
| racer.py | Multiple enemy cars (grows with score) |
| racer.py | Road obstacles: oil spill (2s slowdown), barrier (game over), bump (brief slow), nitro strip (speed boost) |
| racer.py | Power-ups: Nitro (4s speed), Shield (absorbs one hit), Repair (clears oil) |
| racer.py | Shield glow effect around player car |
| racer.py | Distance meter on HUD |
| racer.py | Difficulty scaling (obstacle spawn rate by difficulty setting) |
| racer.py | Score = dodged enemies + distance/100 |
| persistence.py | `load_settings` / `save_settings` → settings.json |
| persistence.py | `load_leaderboard` / `save_leaderboard` → leaderboard.json (top 10) |
| settings.json | Default settings file |
| leaderboard.json | Persistent top 10 scores |

---

## TSIS-4: Snake

### Base (Practice 10–11)
| Feature | Description |
|---------|-------------|
| Grid 30×30 | CELL=20px, 600×600 window |
| Border walls | Always present; extra walls at level 2 and 3 |
| Arrow key movement | No 180° reversal |
| Level up | Every 4 food items, speed +2 |
| Weighted food | Red=1pt/8s, Orange=2pt/5s, Yellow=3pt/3s |
| Food timer bars | White bar shrinks as food ages, disappears on timeout |

### Added in TSIS-4
| File | Feature |
|------|---------|
| main.py | State machine: menu → game → gameover → (leaderboard/settings) |
| main.py | Username text input on menu screen |
| main.py | Main menu: Play, Leaderboard, Settings, Quit |
| main.py | Poison food (dark red, "P" label) — shortens snake by 2, game over if length ≤ 1 |
| main.py | Power-ups: Speed boost (1.5× speed / 5s), Slow (0.6× / 5s), Shield (one collision ignored) |
| main.py | Obstacles from level 3: random wall blocks, safe spawn (5-cell distance from snake head) |
| main.py | Grid overlay toggle from settings |
| main.py | Personal best (PB) shown during gameplay |
| main.py | Game over: auto-saves to DB, shows PB |
| main.py | Settings screen: snake color presets, grid ON/OFF, sound ON/OFF, saves to settings.json |
| main.py | Leaderboard screen: top 10 from DB with rank/name/score/level/date |
| main.py | Graceful DB error handling (shows message if no connection) |
| db.py | `get_or_create_player(username)` — find or insert player |
| db.py | `save_session(username, score, level)` — save game result |
| db.py | `get_leaderboard(limit=10)` — fetch top scores |
| db.py | `get_personal_best(username)` — fetch player's best score |
| schema.sql | `players` table (id, username UNIQUE) |
| schema.sql | `game_sessions` table (id, player_id FK, score, level_reached, played_at) |
| settings.json | Snake color, grid overlay, sound preferences |
| config.py | DB config loader from database.ini |
