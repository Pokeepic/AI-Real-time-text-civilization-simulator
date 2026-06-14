import os


LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "world_history.txt")
CHRONICLE_FILE = os.path.join(LOG_FOLDER, "chronicles.txt")
STORY_SUMMARY_FILE = os.path.join(LOG_FOLDER, "story_summary.txt")
SNAPSHOTS_FILE = os.path.join(LOG_FOLDER, "history_snapshots.txt")
SNAPSHOTS_CSV_FILE = os.path.join(LOG_FOLDER, "history_snapshots.csv")

def archive_logs(sim, logs):
    os.makedirs(LOG_FOLDER, exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        for log in logs:
            file.write(f"Day {sim.day} Hour {sim.hour}:00 — {log}\n")

        if sim.hour == 0:
            file.write("\n--- NEW DAY ---\n\n")


def export_chronicles(sim):
    os.makedirs(LOG_FOLDER, exist_ok=True)

    with open(CHRONICLE_FILE, "w", encoding="utf-8") as file:
        file.write("OBSERVER WORLD CHRONICLES\n")
        file.write("========================\n\n")

        for chronicle in sim.chronicles:
            file.write(chronicle + "\n\n")

def export_story_summary(sim):
    os.makedirs(LOG_FOLDER, exist_ok=True)

    alive = [a for a in sim.agents if a.alive]
    dead = [a for a in sim.agents if not a.alive]

    leader_name = getattr(sim, "leader", None) or "no clear leader"
    settlement_name = sim.settlement.get("name") or "the first camp"

    story_summary = f"""
OBSERVER WORLD STORY SUMMARY
============================

World: {getattr(sim, 'world_name', 'Unknown')}
Settlement: {settlement_name}
Stage: {getattr(sim, 'settlement_stage', 'Camp')}
Era: {getattr(sim, 'current_era', 'Age of Survival')}

Living Population: {len(alive)}
Recorded Dead: {len(dead)}
Leader: {leader_name}

Culture: {sim.get_culture_identity()}
Belief: {sim.get_belief_identity()}

Wars: {len(sim.wars)}
Treaties: {len(sim.treaties)}
Technologies: {len(sim.technologies)}
Laws: {len(sim.laws)}
"""

    with open(STORY_SUMMARY_FILE, "w", encoding="utf-8") as file:
        file.write(story_summary)

    return STORY_SUMMARY_FILE

def export_history_snapshots(sim):
    os.makedirs(LOG_FOLDER, exist_ok=True)

    with open(SNAPSHOTS_FILE, "w", encoding="utf-8") as file:
        file.write("OBSERVER WORLD HISTORY SNAPSHOTS\n")
        file.write("================================\n\n")

        for snapshot in getattr(sim, "history_snapshots", []):
            file.write(str(snapshot) + "\n")

    return SNAPSHOTS_FILE

def export_history_snapshots_csv(sim):
    os.makedirs(LOG_FOLDER, exist_ok=True)

    snapshots = getattr(sim, "history_snapshots", [])

    with open(SNAPSHOTS_CSV_FILE, "w", encoding="utf-8") as file:
        file.write("day,hour,alive,dead,food,wood,stone,tension,wars,technologies,births_total,deaths_total,notifications_total,avg_health,avg_hunger,avg_energy,births_today,deaths_today,growth_rate\n")

        for s in snapshots:
            file.write(
                f"{s.get('day')},{s.get('hour')},{s.get('alive')},{s.get('dead')},"
                f"{s.get('food')},{s.get('wood')},{s.get('stone')},"
                f"{s.get('tension')},{s.get('wars')},{s.get('technologies')}\n"
                f"{s.get('births_total')},{s.get('deaths_total')},{s.get('notifications_total')},"
                f"{s.get('births_today')},{s.get('deaths_today')},"
                f"{s.get('avg_health')},{s.get('avg_hunger')},{s.get('avg_energy')}\n"
                f"{s.get('growth_rate')}\n"
            )

    return SNAPSHOTS_CSV_FILE