"""
World system for Observer World.
"""
import random

def update_season(sim):
    season_index = (sim.day // 20) % 4
    seasons = ["Spring", "Summer", "Autumn", "Winter"]
    sim.season = seasons[season_index]

def update_weather(sim):
    weather_by_season = {
        "Spring": ["Clear", "Rain", "Wind"],
        "Summer": ["Clear", "Heat", "Wind"],
        "Autumn": ["Clear", "Rain", "Wind"],
        "Winter": ["Snow", "Clear", "Storm"]
    }

    sim.weather = random.choice(
        weather_by_season.get(sim.season, ["Clear"])
    )

def generate_world_name(sim):
    prefixes = ["Eld", "Aru", "Nora", "Vey", "Sol", "Mira", "Kael", "Orin"]
    suffixes = ["mere", "vale", "reach", "hollow", "fall", "spire", "wood", "heim"]

    return random.choice(prefixes) + random.choice(suffixes)

def generate_settlement_name(sim):
    first = ["First", "Old", "New", "Stone", "River", "Ash", "Sun", "Moon"]
    second = ["Hearth", "Hollow", "Rest", "Crossing", "Gate", "Field", "Watch"]

    return random.choice(first) + " " + random.choice(second)

def generate_child_name(sim):
    prefixes = ["Ari", "Kai", "Mira", "Lio", "Nora", "Eli", "Rami", "Sena"]
    suffixes = ["an", "el", "ra", "mi", "ko", "na", "ren", "la"]

    return random.choice(prefixes) + random.choice(suffixes)

def generate_surname(sim):
    roots = ["Hearth", "River", "Stone", "Ash", "Moon", "Sun", "Vale", "Wolf", "Oak", "Storm"]
    endings = ["born", "field", "watch", "wood", "crest", "ward", "line", "keeper"]

    return random.choice(roots) + random.choice(endings)

def notify(sim, message, category="General"):
    sim.notifications.append({
        "day": sim.day,
        "hour": sim.hour,
        "category": category,
        "message": message,
    })

    if len(sim.notifications) > 100:
        sim.notifications.pop(0)


def notify_agent_event(sim, agent_name, message):
    if agent_name in sim.watchlist:
        sim.notify(
            f"[WATCHLIST] {agent_name}: {message}",
            "Watchlist"
        )


def notify_family_event(sim, surname, message):
    if surname and surname in sim.family_watchlist:
        sim.notify(
            f"[{surname.upper()}] {message}",
            "Family Watchlist"
        )

def add_history(sim, event):
    record = f"Day {sim.day}, {sim.hour}:00 — {event}"
    sim.world_history.append(record)

    if len(sim.world_history) > 50:
        sim.world_history.pop(0)

def create_daily_chronicle(sim, logs):
    if not sim.daily_events:
        return

    important_keywords = [
        "died", "born", "founded", "leader", "war", "rebellion",
        "technology", "milestone", "trial", "exiled", "treaty",
        "completed", "fulfilled", "murder", "settlement"
    ]

    important_events = [
        event for event in sim.daily_events
        if any(keyword in event.lower() for keyword in important_keywords)
    ]

    if important_events:
        summary = f"Day {sim.day - 1} Chronicle: " + " ".join(important_events[:5])
    else:
        alive_count = len([a for a in sim.agents if a.alive])
        summary = f"Day {sim.day - 1} Chronicle: The day passed quietly. Population alive: {alive_count}."

    sim.chronicles.append(summary)

    if len(sim.chronicles) > 30:
        sim.chronicles.pop(0)

    logs.append(summary)
    sim.daily_events = []