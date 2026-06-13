import random

def update_settlement_stage(sim, logs):
    alive = [
        a for a in sim.agents
        if a.alive
        and a.location != "Exiled Lands"
        and not sim.is_extra_settlement_location(a.location)
    ]

    building_count = len(sim.settlement["buildings"])
    law_count = len(sim.laws)

    old_stage = sim.settlement_stage

    if sim.settlement["name"] is None:
        sim.settlement_stage = "Camp"
    elif len(alive) >= 50 and building_count >= 8 and law_count >= 4:
        sim.settlement_stage = "City"
    elif len(alive) >= 30 and building_count >= 6 and law_count >= 3:
        sim.settlement_stage = "Town"
    elif len(alive) >= 10 and building_count >= 2:
        sim.settlement_stage = "Village"
    else:
        sim.settlement_stage = "Settlement"

    if sim.settlement_stage != old_stage:
        logs.append(f"{sim.settlement['name'] or 'The camp'} has grown into a {sim.settlement_stage}.")
        sim.add_history(f"{sim.settlement['name'] or 'The camp'} became a {sim.settlement_stage}.")

def choose_village_project(sim, logs):
    if sim.settlement["name"] is None:
        return

    if sim.current_project is not None:
        return

    if not sim.leader:
        return

    possible_projects = []

    if "Storage Hut" not in sim.settlement["buildings"]:
        possible_projects.append("Storage Hut")

    if "Farm" not in sim.settlement["buildings"]:
        possible_projects.append("Farm")

    if "Clinic" not in sim.settlement["buildings"]:
        possible_projects.append("Clinic")

    if "Guard Post" not in sim.settlement["buildings"]:
        possible_projects.append("Guard Post")

    if not possible_projects:
        return

    leader = next((a for a in sim.agents if a.name == sim.leader), None)

    if not leader:
        return

    if leader.role == "Leader":
        if sim.resources["food"] < 30:
            project = "Farm"
        elif sim.village_tension > 50:
            project = "Guard Post"
        else:
            project = random.choice(possible_projects)
    else:
        project = random.choice(possible_projects)

    sim.current_project = {
        "name": project,
        "progress": 0,
        "required": 100
    }

    logs.append(f"Leader {sim.leader} proposed a new village project: {project}.")
    sim.add_history(f"{sim.leader} proposed building a {project}.")

def work_on_project(sim, agent):
    logs = []

    if sim.current_project is None:
        return logs

    project_name = sim.current_project["name"]

    wood_cost = 5
    stone_cost = 3

    if sim.resources["wood"] < wood_cost or sim.resources["stone"] < stone_cost:
        logs.append(f"{agent.name} wanted to work on {project_name}, but materials were too low.")
        return logs

    sim.resources["wood"] -= wood_cost
    sim.resources["stone"] -= stone_cost

    progress = random.randint(8, 18) + agent.skills["building"]
    sim.current_project["progress"] += progress

    agent.improve_skill("building", 1)

    logs.append(f"{agent.name} worked on {project_name}.")
    logs.append(
        f"{project_name} progress +{progress}. "
        f"Total: {sim.current_project['progress']}/{sim.current_project['required']}."
    )

    if sim.current_project["progress"] >= sim.current_project["required"]:
        sim.settlement["buildings"].append(project_name)
        logs.append(f"{project_name} has been completed.")
        sim.add_history(f"{project_name} was completed in {sim.settlement['name']}.")

        if project_name == "Farm":
            sim.resources["food"] += 30
            logs.append("The Farm produced its first food. Food +30.")

        elif project_name == "Storage Hut":
            logs.append("The village can now store more supplies safely.")

        elif project_name == "Clinic":
            logs.append("The village now has a place for healing.")

        elif project_name == "Guard Post":
            sim.village_tension = max(sim.village_tension - 15, 0)
            logs.append("The Guard Post made the village feel safer. Village tension -15.")

        sim.current_project = None

    return logs

def apply_building_effects(sim, logs):
    if sim.hour != 6:
        return

    buildings = sim.settlement["buildings"]

    if "Farm" in buildings:
        food_gain = random.randint(15, 30)

        if "Crop Rotation" in sim.technologies:
            food_gain += 15

        sim.resources["food"] += food_gain
        logs.append(f"The Farm produced food. Food +{food_gain}.")

    if "Storage Hut" in buildings:
        if random.random() < 0.15:
            saved_food = random.randint(5, 15)
            sim.resources["food"] += saved_food
            logs.append(f"The Storage Hut preserved supplies. Food saved +{saved_food}.")

    if "Clinic" in buildings:
        for agent in sim.agents:
            if agent.alive and agent.health < 70 and agent.location != "Exiled Lands":
                heal_amount = random.randint(3, 8)
                agent.health = min(agent.health + heal_amount, 100)
                logs.append(f"The Clinic helped {agent.name} recover. Health +{heal_amount}.")

    if "Guard Post" in buildings:
        if sim.village_tension > 0:
            tension_drop = random.randint(3, 8)
            sim.village_tension = max(sim.village_tension - tension_drop, 0)
            logs.append(f"The Guard Post reduced village tension by {tension_drop}.")

    if "Written Records" in sim.technologies and sim.village_tension > 0:
        sim.village_tension = max(sim.village_tension - 2, 0)
        logs.append("Written records helped settle disputes. Village tension -2.")

    if "Council Governance" in sim.technologies and sim.village_tension > 0:
        sim.village_tension = max(sim.village_tension - 4, 0)
        logs.append("Council governance reduced political tension. Village tension -4.")

def apply_extra_settlement_effects(sim, logs):
    if sim.hour != 6:
        return

    for settlement in sim.extra_settlements:
        resources = settlement.get("resources", {})
        buildings = settlement.get("buildings", [])

        if "Farm" in buildings:
            food_gain = random.randint(8, 18)

            if "Crop Rotation" in settlement.get("technologies", []):
                food_gain += 10

            resources["food"] += food_gain
            logs.append(f"{settlement['name']}'s Farm produced food +{food_gain}.")

        if "Guard Post" in buildings and settlement["tension"] > 0:
            tension_drop = random.randint(2, 6)
            settlement["tension"] = max(settlement["tension"] - tension_drop, 0)
            logs.append(f"{settlement['name']}'s Guard Post reduced tension by {tension_drop}.")

def handle_extra_settlement_growth(sim, logs):
    if sim.hour != 14:
        return

    for settlement in sim.extra_settlements:
        resources = settlement.get("resources", {})
        buildings = settlement.get("buildings", [])

        population = len([
            a for a in sim.agents
            if a.alive and a.location == settlement["name"]
        ])

        settlement["population"] = population

        if population <= 0:
            continue

        if "Shelter" not in buildings:
            project = "Shelter"
            wood_cost = 10
            stone_cost = 5

        elif "Farm" not in buildings:
            project = "Farm"
            wood_cost = 15
            stone_cost = 5

        elif "Guard Post" not in buildings and settlement["tension"] > 40:
            project = "Guard Post"
            wood_cost = 20
            stone_cost = 10

        else:
            continue

        if resources.get("wood", 0) >= wood_cost and resources.get("stone", 0) >= stone_cost:
            resources["wood"] -= wood_cost
            resources["stone"] -= stone_cost
            buildings.append(project)

            logs.append(f"{settlement['name']} completed a new building: {project}.")

            if project == "Shelter":
                settlement["stage"] = "Settlement"
                logs.append(f"{settlement['name']} is no longer just a camp.")

            elif project == "Farm":
                resources["food"] += 20
                logs.append(f"{settlement['name']}'s Farm produced food +20.")

            elif project == "Guard Post":
                settlement["tension"] = max(settlement["tension"] - 15, 0)
                logs.append(f"{settlement['name']}'s Guard Post reduced local tension.")

            sim.add_history(f"{settlement['name']} built {project}.")

def update_extra_settlement_leaders(sim, logs):
    if sim.hour != 18:
        return

    for settlement in sim.extra_settlements:
        residents = [
            a for a in sim.agents
            if a.alive
            and a.age >= 18
            and a.location == settlement["name"]
        ]

        if not residents:
            settlement["leader"] = None
            continue

        best_candidate = max(
            residents,
            key=lambda a: (
                a.skills["social"] * 3
                + a.skills["combat"] * 2
                + a.discipline
                + a.aggression // 2
                + a.wealth
            )
        )

        old_leader = settlement.get("leader")

        if old_leader != best_candidate.name:
            settlement["leader"] = best_candidate.name
            logs.append(f"{best_candidate.name} became the leader of {settlement['name']}.")
            sim.add_history(f"{best_candidate.name} became leader of {settlement['name']}.")

def update_extra_settlement_culture(sim, logs):
    if sim.hour != 20:
        return

    for settlement in sim.extra_settlements:
        residents = [
            a for a in sim.agents
            if a.alive and a.location == settlement["name"]
        ]

        if not residents:
            continue

        avg_kindness = sum(a.kindness for a in residents) / len(residents)
        avg_aggression = sum(a.aggression for a in residents) / len(residents)
        avg_discipline = sum(a.discipline for a in residents) / len(residents)

        if avg_kindness > 55:
            settlement["culture"]["cooperation"] += 1

        if avg_aggression > 60 or settlement["tension"] > 60:
            settlement["culture"]["violence"] += 1

        if avg_discipline > 55:
            settlement["culture"]["discipline"] += 1

        if any(a.role == "Teacher" for a in residents):
            settlement["culture"]["knowledge"] += 1

        if any(a.role == "Merchant" for a in residents):
            settlement["culture"]["trade"] += 1

        if any(a.role == "Guard" for a in residents):
            settlement["culture"]["fear"] += 1

def update_extra_settlement_laws(sim, logs):
    if sim.hour != 21:
        return

    for settlement in sim.extra_settlements:
        laws = settlement.get("laws", [])

        if settlement["tension"] > 60 and "No attacks inside the camp" not in laws:
            laws.append("No attacks inside the camp")
            logs.append(f'{settlement["name"]} created a law: "No attacks inside the camp".')
            sim.add_history(f'{settlement["name"]} created law: No attacks inside the camp.')

        if settlement["resources"]["food"] < 10 and "Food must be rationed" not in laws:
            laws.append("Food must be rationed")
            logs.append(f'{settlement["name"]} created a law: "Food must be rationed".')
            sim.add_history(f'{settlement["name"]} created law: Food must be rationed.')

def handle_exile_settlements(sim, logs):
    if sim.hour != 12:
        return

    exiles = [
        a for a in sim.agents
        if a.alive and a.location == "Exiled Lands"
    ]

    if len(exiles) < 3:
        return

    if len(sim.extra_settlements) >= 1:
        return

    founder = max(
        exiles,
        key=lambda a: a.skills["social"] + a.discipline + a.aggression
    )

    settlement_name = sim.generate_settlement_name()

    new_settlement = {
        "name": settlement_name,
        "founder": founder.name,
        "leader": founder.name,
        "population": len(exiles),
        "stage": "Camp",
        "tension": 30,
        "relationship_to_main": -20,
        "resources": {
            "food": 20,
            "wood": 10,
            "stone": 5
        },
        "buildings": [],
        "laws": [],
        "culture": {
            "cooperation": 0,
            "fear": 0,
            "discipline": 0,
            "violence": 0,
            "knowledge": 0,
            "trade": 0
        },
        "technologies": [],
        "research_points": 0,
    }

    sim.extra_settlements.append(new_settlement)

    for exile in exiles:
        exile.location = settlement_name

    logs.append(f"The exiles founded a new camp: {settlement_name}.")
    logs.append(f"Founder: {founder.name}. Population: {len(exiles)}.")
    sim.add_history(f"Exiles founded {settlement_name} under {founder.name}.")

def handle_settlement_relations(sim, logs):
    if sim.hour != 15:
        return

    if not sim.extra_settlements:
        return

    for settlement in sim.extra_settlements:
        relation = settlement["relationship_to_main"]

        if relation >= 40:
            event = random.choice(["trade", "alliance"])
        elif relation <= -40:
            event = random.choice(["raid", "threat"])
        else:
            event = random.choice(["trade", "tension", "nothing"])

        if event == "trade":
            food_gain = random.randint(5, 15)
            sim.resources["food"] += food_gain
            settlement["relationship_to_main"] += 5

            logs.append(f"{settlement['name']} traded with {sim.settlement['name'] or 'the main camp'}.")
            logs.append(f"Main storage gained food +{food_gain}. Relations +5.")

        elif event == "alliance":
            settlement["relationship_to_main"] += 3
            sim.village_tension = max(sim.village_tension - 5, 0)

            logs.append(f"{settlement['name']} reaffirmed friendly ties with the main settlement.")
            logs.append("Village tension -5.")

        elif event == "raid":
            stolen_food = min(sim.resources["food"], random.randint(5, 20))
            sim.resources["food"] -= stolen_food
            settlement["relationship_to_main"] -= 5
            sim.village_tension = min(sim.village_tension + 15, 100)

            logs.append(f"{settlement['name']} raided the main settlement.")
            logs.append(f"Food stolen: {stolen_food}. Relations -5. Tension +15.")

            sim.add_history(f"{settlement['name']} raided the main settlement.")

        elif event == "threat":
            settlement["relationship_to_main"] -= 3
            sim.village_tension = min(sim.village_tension + 8, 100)

            logs.append(f"{settlement['name']} sent threats to the main settlement.")
            logs.append("Relations -3. Village tension +8.")

        elif event == "tension":
            settlement["relationship_to_main"] -= 2

            logs.append(f"Tension grew between {settlement['name']} and the main settlement.")
            logs.append("Relations -2.")

def handle_migration(sim, logs):
    if sim.hour != 10:
        return

    if not sim.extra_settlements:
        return

    extra_settlement = sim.get_first_extra_settlement()

    if not extra_settlement:
        return

    for agent in sim.agents:
        if not agent.alive or agent.age < 18:
            continue

        if agent.location == "Exiled Lands":
            continue

        # Main settlement -> extra settlement
        if agent.location != extra_settlement["name"]:
            desire_to_leave = 0

            if sim.village_tension > 70:
                desire_to_leave += 30

            if sim.leader:
                rel = agent.get_relationship(sim.leader)
                if rel["fear"] > 30 or rel["trust"] < -30:
                    desire_to_leave += 20

            if agent.faction == "Reform Seekers":
                desire_to_leave += 25

            if agent.greed > 70 and extra_settlement["relationship_to_main"] < 0:
                desire_to_leave += 15

            if agent.partner:
                desire_to_leave -= 10

            if random.randint(1, 100) < desire_to_leave:
                agent.location = extra_settlement["name"]
                extra_settlement["population"] += 1

                logs.append(f"{agent.name} migrated to {extra_settlement['name']}.")
                sim.add_history(f"{agent.name} left the main settlement for {extra_settlement['name']}.")

        # Extra settlement -> main settlement
        else:
            desire_to_return = 0

            if extra_settlement["relationship_to_main"] > 20:
                desire_to_return += 20

            if agent.kindness > 70:
                desire_to_return += 15

            if agent.family:
                desire_to_return += 15

            if random.randint(1, 100) < desire_to_return:
                agent.location = "Camp"
                extra_settlement["population"] = max(0, extra_settlement["population"] - 1)

                logs.append(f"{agent.name} returned from {extra_settlement['name']} to the main settlement.")
                sim.add_history(f"{agent.name} returned from {extra_settlement['name']}.")

def handle_diplomacy(sim, logs):
    if sim.hour != 16:
        return

    if not sim.extra_settlements:
        return

    for settlement in sim.extra_settlements:
        relation = settlement["relationship_to_main"]

        if relation < -30:
            diplomacy_chance = 0.08

            if sim.leader:
                leader = next((a for a in sim.agents if a.name == sim.leader), None)
                if leader:
                    diplomacy_chance += leader.skills["social"] / 100

            if settlement.get("leader"):
                other_leader = next((a for a in sim.agents if a.name == settlement["leader"]), None)
                if other_leader:
                    diplomacy_chance += other_leader.skills["social"] / 150

            if random.random() < diplomacy_chance:
                treaty = {
                    "day": sim.day,
                    "hour": sim.hour,
                    "settlement": settlement["name"],
                    "type": "peace talks"
                }

                sim.treaties.append(treaty)

                relation_gain = random.randint(10, 25)
                settlement["relationship_to_main"] += relation_gain
                sim.village_tension = max(sim.village_tension - 10, 0)
                settlement["tension"] = max(settlement["tension"] - 10, 0)

                logs.append(f"Peace talks were held with {settlement['name']}.")
                logs.append(f"Relations improved by {relation_gain}.")
                logs.append("Tension decreased in both settlements.")

                sim.notify(f"Peace talks improved relations with {settlement['name']}.", "Diplomacy")
                sim.add_history(f"Peace talks improved relations with {settlement['name']}.")

        elif relation > 30:
            if random.random() < 0.05:
                treaty = {
                    "day": sim.day,
                    "hour": sim.hour,
                    "settlement": settlement["name"],
                    "type": "friendship pact"
                }

                sim.treaties.append(treaty)
                settlement["relationship_to_main"] += 10

                logs.append(f"{sim.settlement['name'] or 'The main settlement'} and {settlement['name']} signed a friendship pact.")
                sim.notify(f"Friendship pact signed with {settlement['name']}.", "Diplomacy")
                sim.add_history(f"Friendship pact signed with {settlement['name']}.")

def calculate_settlement_power(sim, settlement_name):
    residents = [
        a for a in sim.agents
        if a.alive and a.location == settlement_name
    ]

    if settlement_name == "main":
        residents = [
            a for a in sim.agents
            if a.alive
            and not sim.is_extra_settlement_location(a.location)
            and a.location != "Exiled Lands"
        ]

    power = 0

    for agent in residents:
        power += agent.skills["combat"] * 3
        power += agent.discipline
        power += agent.health // 5

        if agent.role == "Guard":
            power += 15

        if agent.role == "Leader":
            power += 10

    return power


def handle_settlement_war(sim, logs):
    if sim.hour != 23:
        return

    for settlement in sim.extra_settlements:
        relation = settlement["relationship_to_main"]

        if relation > -70:
            continue

        war_chance = 0.08
        war_chance += settlement["tension"] / 300
        war_chance += sim.village_tension / 400

        recent_treaty = any(
            treaty["settlement"] == settlement["name"]
            and sim.day - treaty["day"] <= 5
            for treaty in sim.treaties
        )

        if recent_treaty:
            war_chance -= 0.05

        if random.random() > war_chance:
            continue

        main_power = calculate_settlement_power(sim, "main")
        other_power = calculate_settlement_power(sim, settlement["name"])

        logs.append(f"War broke out between {sim.settlement['name'] or 'the main settlement'} and {settlement['name']}.")
        logs.append(f"Main power: {main_power}. {settlement['name']} power: {other_power}.")

        sim.notify(
            f"War began between {sim.settlement['name'] or 'the main settlement'} and {settlement['name']}.",
            "War"
        )

        war_record = {
            "day": sim.day,
            "hour": sim.hour,
            "enemy": settlement["name"],
            "main_power": main_power,
            "enemy_power": other_power
        }

        sim.wars.append(war_record)

        if main_power >= other_power:
            logs.append("The main settlement defended itself successfully.")
            settlement["relationship_to_main"] += 20
            settlement["tension"] += 10
            sim.village_tension = max(sim.village_tension - 10, 0)

            apply_war_losses(sim, settlement["name"], logs)

            sim.add_history(f"The main settlement won a conflict against {settlement['name']}.")

        else:
            stolen_food = min(sim.resources["food"], random.randint(20, 50))
            sim.resources["food"] -= stolen_food
            sim.village_tension = min(sim.village_tension + 20, 100)
            settlement["relationship_to_main"] -= 10

            logs.append(f"{settlement['name']} overwhelmed the main settlement.")
            logs.append(f"Food lost: {stolen_food}.")

            apply_war_losses(sim, "main", logs)

            sim.add_history(f"{settlement['name']} defeated the main settlement in conflict.")


def apply_war_losses(sim, settlement_name, logs):
    if settlement_name == "main":
        candidates = [
            a for a in sim.agents
            if a.alive
            and not sim.is_extra_settlement_location(a.location)
            and a.location != "Exiled Lands"
        ]
    else:
        candidates = [
            a for a in sim.agents
            if a.alive and a.location == settlement_name
        ]

    if not candidates:
        return

    casualty_count = min(len(candidates), random.randint(0, 2))

    for _ in range(casualty_count):
        victim = random.choice(candidates)
        damage = random.randint(20, 60)

        victim.health = max(victim.health - damage, 0)

        logs.append(f"{victim.name} was injured during the conflict. Health -{damage}.")

        if victim.health <= 0:
            victim.alive = False
            victim.status = "Dead"
            logs.append(f"{victim.name} died from conflict injuries.")
            sim.record_death(victim, "settlement conflict", logs)

        candidates.remove(victim)