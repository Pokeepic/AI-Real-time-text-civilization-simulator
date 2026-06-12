import os


LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "world_history.txt")
CHRONICLE_FILE = os.path.join(LOG_FOLDER, "chronicles.txt")
STORY_SUMMARY_FILE = os.path.join(LOG_FOLDER, "story_summary.txt")

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