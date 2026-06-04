import os


LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "world_history.txt")
CHRONICLE_FILE = os.path.join(LOG_FOLDER, "chronicles.txt")


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
