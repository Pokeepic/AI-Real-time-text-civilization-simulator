"""
Agent action system for Observer World.
"""

import random
from dialogue import get_line
from world import LOCATIONS


def handle_talk(sim, agent):
    logs = []

    nearby = [
        other for other in sim.nearby_agents(agent)
        if other.alive and other.name != agent.name
    ]

    if not nearby:
        logs.append(f"{agent.name} wanted to talk, but no one was nearby.")
        return logs

    preferred_targets = [
        other for other in nearby
        if other.name == agent.crush
        or other.name in agent.bonds
        or other.name in agent.family
        or other.age < 18
    ]

    if preferred_targets:
        other = random.choice(preferred_targets)
    else:
        other = random.choice(nearby)

    agent.change_relationship(other.name, "friendship", 2)
    other.change_relationship(agent.name, "friendship", 2)

    agent.social = min(agent.social + 10, 100)
    other.social = min(other.social + 10, 100)

    agent.add_location_affinity(agent.location, 1)
    other.add_location_affinity(other.location, 1)

    logs.append(f"{agent.name} talked with {other.name} at {agent.location}.")

    agent_relationship_line = sim.get_relationship_line(agent, other)
    other_relationship_line = sim.get_relationship_line(other, agent)

    agent_memory_line = sim.get_memory_line(agent)
    other_memory_line = sim.get_memory_line(other)

    if agent_relationship_line and random.random() < 0.5:
        logs.append(f'{agent.name}: "{agent_relationship_line}"')
    elif agent_memory_line and random.random() < 0.35:
        logs.append(f'{agent.name}: "{agent_memory_line}"')
    else:
        logs.append(f'{agent.name}: "{get_line(agent, "survival")}"')

    if other_relationship_line and random.random() < 0.5:
        logs.append(f'{other.name}: "{other_relationship_line}"')
    elif other_memory_line and random.random() < 0.35:
        logs.append(f'{other.name}: "{other_memory_line}"')
    else:
        logs.append(f'{other.name}: "{get_line(other, "survival")}"')

    if random.random() < 0.2:
        sim.handle_teaching(agent, other, logs)

    return logs

def handle_help(sim, agent):
    logs = []

    nearby = [
        other for other in sim.nearby_agents(agent)
        if other.alive and other.name != agent.name
    ]

    if not nearby:
        logs.append(f"{agent.name} wanted to help, but no one was nearby.")
        return logs

    bond_targets = [
        other for other in nearby
        if other.name in agent.family
        or other.name in agent.bonds
        or other.name == agent.crush
    ]

    if bond_targets:
        other = random.choice(bond_targets)
    else:
        other = random.choice(nearby)

    other.energy = min(other.energy + 10, 100)
    other.social = min(other.social + 5, 100)

    agent.change_relationship(other.name, "trust", 4)
    other.change_relationship(agent.name, "trust", 4)

    agent.remember(f"Helped {other.name}.")
    other.remember(f"{agent.name} helped me.")

    other.add_bond(agent.name, "helped me")
    agent.add_bond(other.name, "helped them")

    agent.set_emotion("Connected")
    other.set_emotion("Connected")

    agent.add_location_affinity(agent.location, 2)
    other.add_location_affinity(other.location, 2)

    sim.record_family_alliance(agent, other, "help")

    logs.append(f"{agent.name} helped {other.name} at {agent.location}.")
    logs.append(f"{other.name}'s energy and social improved.")

    return logs

def handle_bond(sim, agent):
    logs = []

    nearby = [
        other for other in sim.nearby_agents(agent)
        if other.alive and other.name != agent.name
    ]

    if not nearby:
        logs.append(f"{agent.name} wanted to bond, but no one was nearby.")
        return logs

    preferred = [
        other for other in nearby
        if other.name == agent.crush
        or other.name in agent.family
        or other.name in agent.bonds
    ]

    if preferred:
        other = random.choice(preferred)
    else:
        other = random.choice(nearby)

    agent.change_relationship(other.name, "friendship", 5)
    other.change_relationship(agent.name, "friendship", 5)

    agent.add_bond(other.name, "shared bonding moment")
    other.add_bond(agent.name, "shared bonding moment")

    agent.set_emotion("Connected")
    other.set_emotion("Connected")

    logs.append(f"{agent.name} bonded with {other.name}.")

    return logs

def handle_learning(sim, agent):
    logs = []

    skill = random.choice(list(agent.skills.keys()))
    gain = random.randint(1, 2)

    agent.improve_skill(skill, gain)
    agent.remember(f"Practiced and learned {skill}.")

    logs.append(f"{agent.name} learned more about {skill}.")
    logs.append(f"{skill.capitalize()} improved to {agent.skills[skill]}.")

    return logs

def handle_patrol(sim, agent):
    logs = []

    agent.energy = max(agent.energy - 10, 0)
    agent.improve_skill("combat", 1)

    sim.village_tension = max(sim.village_tension - 3, 0)

    logs.append(f"{agent.name} patrolled the area.")
    logs.append(f"{agent.name}'s combat improved to {agent.skills['combat']}.")
    logs.append(f"Village tension decreased to {sim.village_tension}.")

    return logs

def handle_teaching(sim, teacher, student, logs):
    if teacher.skills["teaching"] < 2:
        return

    skill = random.choice(list(student.skills.keys()))

    student.improve_skill(skill, 1)
    teacher.improve_skill("teaching", 1)

    student.remember(f"{teacher.name} taught me {skill}.")
    teacher.remember(f"Taught {student.name} about {skill}.")

    student.add_bond(teacher.name, "taught me")
    teacher.add_bond(student.name, "learned from me")

    teacher.set_emotion("Connected")
    student.set_emotion("Connected")

    sim.record_family_alliance(teacher, student, "teaching")

    logs.append(f"{teacher.name} taught {student.name} about {skill} at {teacher.location}.")

def handle_explore(sim, agent):
    logs = []

    new_location = random.choice(LOCATIONS)
    agent.location = new_location

    logs.append(f"{agent.name} explored and moved to {agent.location}.")

    return logs

def handle_sleep(sim, agent):
    logs = []

    agent.energy = min(agent.energy + 30, 100)

    logs.append(f"{agent.name} slept at {agent.location}. Energy restored.")

    return logs

def handle_visit_favorite_place(sim, agent):
    logs = []

    favorite = agent.get_favorite_place()

    if favorite:
        agent.location = favorite
        agent.social = min(agent.social + 5, 100)
        agent.energy = max(agent.energy - 2, 0)

        logs.append(f"{agent.name} visited their favorite place: {favorite}.")
    else:
        logs.append(f"{agent.name} wanted to visit a favorite place, but had none.")

    return logs

def handle_practice(sim, agent):
    logs = []

    skill = random.choice(list(agent.skills.keys()))
    agent.improve_skill(skill, 1)

    logs.append(f"{agent.name} practiced {skill}. {skill.capitalize()} is now {agent.skills[skill]}.")

    return logs

def handle_gather_food(sim, agent):
    logs = []

    food_found = random.randint(5, 20) + agent.skills["hunting"]

    if sim.weather in ["Storm", "Snow"]:
        food_found = max(1, food_found // 2)

    if sim.season == "Winter":
        food_found = max(1, food_found // 2)

    if sim.weather == "Rain":
        food_found += 2

    try:
        from config import get_setting
        food_found = int(food_found * get_setting("resource_multiplier"))
    except Exception:
        pass

    agent.hunger = max(agent.hunger - food_found // 2, 0)

    agent_settlement = sim.get_agent_settlement(agent)

    if agent_settlement:
        agent_settlement["resources"]["food"] += food_found // 2
    else:
        sim.resources["food"] += food_found // 2

    agent.inventory["food"] += max(1, food_found // 4)
    agent.improve_skill("hunting", 1)

    logs.append(f"{agent.name} gathered food at {agent.location}.")
    logs.append(f"{food_found // 2} food was added to shared storage.")
    logs.append(f"{agent.name}'s hunting improved to {agent.skills['hunting']}.")

    return logs

def handle_gather_materials(sim, agent):
    logs = []

    wood = random.randint(3, 10)
    stone = random.randint(1, 6)

    if sim.weather in ["Storm", "Snow"]:
        wood = max(1, wood // 2)
        stone = max(1, stone // 2)

    agent_settlement = sim.get_agent_settlement(agent)

    if agent_settlement and "Basic Tools" in agent_settlement.get("technologies", []):
        wood += 3
        stone += 2
    elif not agent_settlement and "Basic Tools" in sim.technologies:
        wood += 3
        stone += 2

    try:
        from config import get_setting
        wood = int(wood * get_setting("resource_multiplier"))
        stone = int(stone * get_setting("resource_multiplier"))
    except Exception:
        pass

    if agent_settlement:
        agent_settlement["resources"]["wood"] += wood
        agent_settlement["resources"]["stone"] += stone
    else:
        sim.resources["wood"] += wood
        sim.resources["stone"] += stone

    agent.inventory["wood"] += max(1, wood // 3)
    agent.inventory["stone"] += max(1, stone // 3)

    agent.improve_skill("building", 1)

    logs.append(f"{agent.name} gathered materials at {agent.location}.")
    logs.append(f"Shared resources gained: wood +{wood}, stone +{stone}.")
    logs.append(f"{agent.name}'s building improved to {agent.skills['building']}.")

    return logs

def handle_build(sim, agent):
    logs = []

    if sim.current_project is not None and "Shelter" in sim.settlement["buildings"]:
        return sim.work_on_project(agent)

    if "Shelter" in sim.settlement["buildings"]:
        logs.append(f"{agent.name} maintained the shelter.")
        agent.improve_skill("building", 1)
        return logs

    if sim.resources["wood"] < 10 or sim.resources["stone"] < 5:
        logs.append(f"{agent.name} wanted to build, but the group lacked materials.")
        return logs

    sim.resources["wood"] -= 10
    sim.resources["stone"] -= 5

    progress = random.randint(10, 25) + agent.skills["building"]
    sim.settlement["shelter_progress"] += progress

    agent.improve_skill("building", 1)

    logs.append(f"{agent.name} worked on the first shelter.")
    logs.append(f"Shelter progress +{progress}. Total: {sim.settlement['shelter_progress']}/100.")

    if sim.settlement["shelter_progress"] >= 100:
        sim.settlement["buildings"].append("Shelter")

        if sim.settlement["name"] is None:
            sim.settlement["name"] = sim.generate_settlement_name()

        logs.append("A permanent shelter has been completed.")
        logs.append(f"Settlement founded: {sim.settlement['name']}.")

        sim.add_history(f"Settlement founded: {sim.settlement['name']}.")

    return logs