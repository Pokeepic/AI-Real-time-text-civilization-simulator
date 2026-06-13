import random

def update_culture(sim, logs):
    if sim.hour != 20:
        return

    alive = [
        a for a in sim.agents
        if a.alive and a.location != "Exiled Lands"
    ]

    if not alive:
        return

    avg_kindness = sum(a.kindness for a in alive) / len(alive)
    avg_aggression = sum(a.aggression for a in alive) / len(alive)
    avg_discipline = sum(a.discipline for a in alive) / len(alive)

    teachers = len([a for a in alive if a.role == "Teacher"])
    merchants = len([a for a in alive if a.role == "Merchant"])
    guards = len([a for a in alive if a.role == "Guard"])

    if avg_kindness > 55:
        sim.culture["cooperation"] += 1

    if avg_aggression > 60 or sim.village_tension > 60:
        sim.culture["violence"] += 1

    if avg_discipline > 55:
        sim.culture["discipline"] += 1

    if teachers > 0:
        sim.culture["knowledge"] += teachers

    if merchants > 0:
        sim.culture["trade"] += merchants

    if guards > 0 and sim.village_tension > 30:
        sim.culture["fear"] += guards

    dominant = max(sim.culture, key=sim.culture.get)

    if sim.culture[dominant] > 0:
        logs.append(f"The culture of {sim.settlement['name'] or 'the camp'} is slowly leaning toward {dominant}.")

def get_culture_identity(sim):
    dominant = max(sim.culture, key=sim.culture.get)

    if sim.culture[dominant] < 10:
        return "Undefined"

    identities = {
        "cooperation": "Cooperative Society",
        "fear": "Fear-Driven Society",
        "discipline": "Disciplined Society",
        "violence": "Violent Society",
        "knowledge": "Knowledge-Seeking Society",
        "trade": "Trade-Oriented Society"
    }

    return identities.get(dominant, "Undefined")

def create_tradition(sim, logs):
    if sim.hour != 21:
        return

    identity = sim.get_culture_identity()

    if identity == "Undefined":
        return

    if len(sim.traditions) >= 3:
        return

    tradition_map = {
        "Cooperative Society": "Sharing Feast",
        "Fear-Driven Society": "Night Watch",
        "Disciplined Society": "Training Day",
        "Violent Society": "Trial of Strength",
        "Knowledge-Seeking Society": "Story Circle",
        "Trade-Oriented Society": "Market Day"
    }

    tradition = tradition_map.get(identity)

    if tradition and tradition not in sim.traditions:
        sim.traditions.append(tradition)
        logs.append(f"New tradition created: {tradition}.")
        sim.add_history(f"A new tradition began: {tradition}.")

def run_traditions(sim, logs):
    if sim.day % 7 != 0 or sim.hour != 18:
        return

    for tradition in sim.traditions:
        logs.append(f"Tradition held: {tradition}.")

        if tradition == "Sharing Feast":
            if sim.resources["food"] >= 20:
                sim.resources["food"] -= 20
                sim.village_tension = max(sim.village_tension - 15, 0)

                for agent in sim.agents:
                    if agent.alive and agent.location != "Exiled Lands":
                        agent.social = min(agent.social + 20, 100)

                logs.append("The Sharing Feast reduced tension and raised social bonds.")
            else:
                logs.append("The Sharing Feast failed because there was not enough food.")
                sim.village_tension += 8

        elif tradition == "Night Watch":
            sim.village_tension = max(sim.village_tension - 8, 0)

            for agent in sim.agents:
                if agent.alive and agent.role == "Guard":
                    agent.improve_skill("combat", 1)

            logs.append("The Night Watch made the settlement feel safer.")

        elif tradition == "Training Day":
            for agent in sim.agents:
                if agent.alive and agent.age >= 13 and agent.location != "Exiled Lands":
                    agent.discipline = min(agent.discipline + 1, 100)
                    agent.improve_skill("combat", 1)

            logs.append("Training Day improved discipline and combat readiness.")

        elif tradition == "Trial of Strength":
            fighters = [
                a for a in sim.agents
                if a.alive and a.age >= 18 and a.location != "Exiled Lands"
            ]

            if len(fighters) >= 2:
                winner = random.choice(fighters)
                winner.improve_skill("combat", 2)
                winner.wealth += 2
                sim.village_tension += 5
                logs.append(f"{winner.name} won the Trial of Strength.")

        elif tradition == "Story Circle":
            for agent in sim.agents:
                if agent.alive and agent.age < 18 and agent.location != "Exiled Lands":
                    agent.improve_skill("teaching", 1)
                    agent.improve_skill("social", 1)

            logs.append("The Story Circle helped children learn from village stories.")

        elif tradition == "Market Day":
            for agent in sim.agents:
                if agent.alive and agent.age >= 13 and agent.location != "Exiled Lands":
                    agent.wealth += 1
                    agent.improve_skill("social", 1)

            logs.append("Market Day increased wealth and social skill.")

def update_beliefs(sim, logs):
    if sim.hour != 22:
        return

    if sim.weather in ["Storm", "Snow"]:
        sim.beliefs["nature_spirits"] += 1

    if sim.death_records:
        sim.beliefs["ancestor_memory"] += 1

    if sim.leader:
        sim.beliefs["leader_destiny"] += 1

    if "Clinic" in sim.settlement["buildings"]:
        sim.beliefs["healing_faith"] += 1

    if "Trial of Strength" in sim.traditions:
        sim.beliefs["strength_worship"] += 1

    dominant = max(sim.beliefs, key=sim.beliefs.get)

    if sim.beliefs[dominant] > 5:
        logs.append(f"A shared belief is forming around {dominant.replace('_', ' ')}.")

def get_belief_identity(sim):
    dominant = max(sim.beliefs, key=sim.beliefs.get)

    if sim.beliefs[dominant] < 8:
        return "None"

    names = {
        "nature_spirits": "Belief in Nature Spirits",
        "ancestor_memory": "Ancestor Reverence",
        "leader_destiny": "Chosen Leader Myth",
        "healing_faith": "Faith in Healers",
        "strength_worship": "Cult of Strength"
    }

    return names.get(dominant, "None")

def update_era(sim, logs):
    alive = [a for a in sim.agents if a.alive]

    new_era = sim.current_era

    if sim.wars:
        new_era = "Age of War"

    elif sim.technologies:
        new_era = "Age of Innovation"

    elif sim.extra_settlements:
        new_era = "Age of Expansion"

    elif sim.settlement_stage in ["Village", "Town", "City"]:
        new_era = "Age of Settlement"

    elif len(alive) >= 15:
        new_era = "Age of Growth"

    if new_era != sim.current_era:
        sim.current_era = new_era

        era_record = {
            "name": new_era,
            "start_day": sim.day
        }

        sim.eras.append(era_record)

        logs.append(f"NEW ERA BEGINS: {new_era}.")
        sim.add_history(f"New era began: {new_era}.")

def unlock_milestone(sim, key, text, logs):
    if key in sim.milestones:
        return

    sim.milestones.add(key)
    logs.append(f"MILESTONE UNLOCKED: {text}")
    sim.add_history(f"Milestone unlocked: {text}")

def check_milestones(sim, logs):
    alive = [a for a in sim.agents if a.alive]
    dead = [a for a in sim.agents if not a.alive]
    children = [a for a in alive if a.age < 18]

    if "Shelter" in sim.settlement["buildings"]:
        sim.unlock_milestone("first_shelter", "First permanent shelter built.", logs)

    if sim.leader:
        sim.unlock_milestone("first_leader", f"{sim.leader} became the first leader.", logs)

    if sim.laws:
        sim.unlock_milestone("first_law", "The first law was created.", logs)

    if children:
        sim.unlock_milestone("first_child", "The first child was born.", logs)

    if dead:
        sim.unlock_milestone("first_death", "The first death was recorded.", logs)

    if len(alive) >= 20:
        sim.unlock_milestone("population_20", "Population reached 20.", logs)

    if len(sim.settlement["buildings"]) >= 4:
        sim.unlock_milestone("village_complete", "The village became a developed settlement.", logs)

    if any(record["crime"] == "murder" for records in sim.crime_records.values() for record in records):
        sim.unlock_milestone("first_murder", "The first murder was recorded.", logs)

    if any(a.generation >= 2 and a.age >= 18 for a in sim.agents):
        sim.unlock_milestone("generation_2_adult", "The second generation reached adulthood.", logs)

    if sim.settlement_stage == "Village":
        sim.unlock_milestone("became_village", "The settlement became a village.", logs)

    if sim.settlement_stage == "Town":
        sim.unlock_milestone("became_town", "The settlement became a town.", logs)

    if sim.settlement_stage == "City":
        sim.unlock_milestone("became_city", "The settlement became a city.", logs)

    if sim.extra_settlements:
        sim.unlock_milestone("second_settlement", "A second settlement was founded.", logs)

    if any(s["relationship_to_main"] >= 50 for s in sim.extra_settlements):
        sim.unlock_milestone("first_alliance", "The first alliance between settlements formed.", logs)

    if any(s["relationship_to_main"] <= -50 for s in sim.extra_settlements):
        sim.unlock_milestone("settlement_rivalry", "A serious rivalry between settlements began.", logs)

    if any(sim.is_extra_settlement_location(a.location) for a in sim.agents):
        sim.unlock_milestone("first_migration", "The first migration between settlements occurred.", logs)

    if sim.wars:
        sim.unlock_milestone("first_war", "The first war between settlements occurred.", logs)

    if sim.treaties:
        sim.unlock_milestone("first_treaty", "The first diplomatic treaty was signed.", logs)

    if sim.world_state == "Dark Age":
        sim.unlock_milestone("dark_age", "The world entered a dark age.", logs)

    if sim.world_state == "Civilization":
        sim.unlock_milestone("civilization_success", "The society became a civilization.", logs)

    if sim.world_state == "Extinct":
        sim.unlock_milestone("extinction", "All agents died.", logs)

    if any(a.get_best_friend() for a in sim.agents):
        sim.unlock_milestone("first_friendship", "The first close friendship formed.", logs)

    if any(a.get_rival() for a in sim.agents):
        sim.unlock_milestone("first_rivalry", "The first rivalry formed.", logs)

    if any("mourned the death" in " ".join(a.memories).lower() for a in sim.agents):
        sim.unlock_milestone("first_mourning", "The first mourning was recorded.", logs)

    connected_count = len([
        a for a in sim.agents
        if getattr(a, "emotional_state", "Stable") == "Connected"
    ])

    alive_count = len([a for a in sim.agents if a.alive])

    if alive_count > 0 and connected_count >= alive_count // 2:
        sim.unlock_milestone("connected_society", "Half the living population feels socially connected.", logs)