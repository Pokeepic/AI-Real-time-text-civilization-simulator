def generate_research(sim, logs):
    if sim.hour != 17:
        return

    alive = [
        a for a in sim.agents
        if a.alive and a.location != "Exiled Lands"
    ]

    if not alive:
        return

    points = 0

    for agent in alive:
        if agent.role == "Teacher":
            points += 2

        if agent.role == "Medic":
            points += 1

        if agent.role == "Builder":
            points += 1

        points += agent.skills["teaching"] // 5

    if sim.get_culture_identity() == "Knowledge-Seeking Society":
        points += 5

    if "Story Circle" in sim.traditions:
        points += 3

    sim.research_points += points

    if points > 0:
        logs.append(f"The settlement generated {points} research points.")

def unlock_technology(sim, logs):
    tech_tree = [
        {
            "name": "Basic Tools",
            "cost": 30,
            "requirement": lambda: True
        },
        {
            "name": "Crop Rotation",
            "cost": 60,
            "requirement": lambda: "Farm" in sim.settlement["buildings"]
        },
        {
            "name": "Herbal Medicine",
            "cost": 70,
            "requirement": lambda: "Clinic" in sim.settlement["buildings"]
        },
        {
            "name": "Written Records",
            "cost": 90,
            "requirement": lambda: sim.get_culture_identity() == "Knowledge-Seeking Society"
        },
        {
            "name": "Stone Construction",
            "cost": 120,
            "requirement": lambda: "Basic Tools" in sim.technologies
        },
        {
            "name": "Council Governance",
            "cost": 150,
            "requirement": lambda: len(sim.laws) >= 3
        }
    ]

    for tech in tech_tree:
        if tech["name"] in sim.technologies:
            continue

        if sim.research_points >= tech["cost"] and tech["requirement"]():
            sim.research_points -= tech["cost"]
            sim.technologies.append(tech["name"])

            logs.append(f"TECHNOLOGY UNLOCKED: {tech['name']}.")
            sim.notify(f"Technology unlocked: {tech['name']}.", "Technology")
            sim.add_history(f"Technology unlocked: {tech['name']}.")

            return

def generate_extra_settlement_research(sim, logs):
    if sim.hour != 17:
        return

    for settlement in sim.extra_settlements:
        residents = [
            a for a in sim.agents
            if a.alive and a.location == settlement["name"]
        ]

        if not residents:
            continue

        points = 0

        for agent in residents:
            if agent.role == "Teacher":
                points += 2
            if agent.role == "Medic":
                points += 1
            if agent.role == "Builder":
                points += 1

            points += agent.skills["teaching"] // 5

        if sim.get_extra_settlement_culture_identity(settlement) == "Knowledge-Seeking Society":
            points += 5

        settlement["research_points"] += points

        if points > 0:
            logs.append(f"{settlement['name']} generated {points} research points.")

def unlock_extra_settlement_technology(sim, logs):
    for settlement in sim.extra_settlements:
        technologies = settlement.get("technologies", [])
        research_points = settlement.get("research_points", 0)
        buildings = settlement.get("buildings", [])

        tech_tree = [
            {
                "name": "Basic Tools",
                "cost": 30,
                "requirement": lambda: True
            },
            {
                "name": "Crop Rotation",
                "cost": 60,
                "requirement": lambda: "Farm" in buildings
            },
            {
                "name": "Herbal Medicine",
                "cost": 70,
                "requirement": lambda: "Clinic" in buildings
            },
            {
                "name": "Stone Construction",
                "cost": 120,
                "requirement": lambda: "Basic Tools" in technologies
            },
        ]

        for tech in tech_tree:
            if tech["name"] in technologies:
                continue

            if research_points >= tech["cost"] and tech["requirement"]():
                settlement["research_points"] -= tech["cost"]
                settlement["technologies"].append(tech["name"])

                logs.append(f'{settlement["name"]} unlocked technology: {tech["name"]}.')
                sim.add_history(f'{settlement["name"]} unlocked technology: {tech["name"]}.')

                break