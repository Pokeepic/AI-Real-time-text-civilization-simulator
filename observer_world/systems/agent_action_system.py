"""
Agent action system for Observer World.
"""

import random
from dialogue import get_line


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