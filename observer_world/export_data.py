import csv
import os

EXPORT_FOLDER = "exports"


def export_agents_csv(sim):
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    path = os.path.join(EXPORT_FOLDER, "agents.csv")

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "name", "age", "generation", "alive", "status", "role",
            "location", "faction", "life_goal", "health", "hunger",
            "energy", "social", "wealth", "partner",
            "curiosity", "kindness", "aggression", "discipline",
            "pride", "greed", "risk_taking",
            "hunting", "building", "farming", "social_skill",
            "teaching", "medicine", "combat"
        ])

        for a in sim.agents:
            writer.writerow([
                a.name, a.age, a.generation, a.alive, a.status, a.role,
                a.location, a.faction, a.life_goal, a.health, a.hunger,
                a.energy, a.social, a.wealth, a.partner,
                a.curiosity, a.kindness, a.aggression, a.discipline,
                a.pride, a.greed, a.risk_taking,
                a.skills["hunting"], a.skills["building"], a.skills["farming"],
                a.skills["social"], a.skills["teaching"], a.skills["medicine"],
                a.skills["combat"]
            ])

    return path


def export_relationships_csv(sim):
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    path = os.path.join(EXPORT_FOLDER, "relationships.csv")

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "agent", "other", "trust", "friendship", "respect", "fear"
        ])

        for agent in sim.agents:
            for other, rel in agent.relationships.items():
                writer.writerow([
                    agent.name,
                    other,
                    rel.get("trust", 0),
                    rel.get("friendship", 0),
                    rel.get("respect", 0),
                    rel.get("fear", 0)
                ])

    return path