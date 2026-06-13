"""
Health system for Observer World.
"""

import random


def handle_heal(sim, medic):
    logs = []

    patients = [
        agent for agent in sim.nearby_agents(medic)
        if agent.alive and agent.health < 80
    ]

    if not patients:
        logs.append(f"{medic.name} wanted to heal, but no one nearby needed treatment.")
        return logs

    bonded_patients = [
        patient for patient in patients
        if patient.name in medic.family
        or patient.name in medic.bonds
    ]

    if bonded_patients:
        patient = min(bonded_patients, key=lambda a: a.health)
    else:
        patient = min(patients, key=lambda a: a.health)

    heal_amount = random.randint(8, 18) + medic.skills["medicine"]

    if "Clinic" in sim.settlement["buildings"]:
        heal_amount += 5

    if "Herbal Medicine" in sim.technologies:
        heal_amount += 8

    patient.health = min(patient.health + heal_amount, 100)

    medic.improve_skill("medicine", 1)

    patient.remember(f"{medic.name} healed me.")
    medic.remember(f"Healed {patient.name}.")

    patient.add_bond(medic.name, "healed me")
    medic.add_bond(patient.name, "treated them")

    medic.set_emotion("Connected")
    patient.set_emotion("Connected")

    sim.record_family_alliance(medic, patient, "healing")

    logs.append(f"{medic.name} healed {patient.name}.")
    logs.append(f"{patient.name}'s health +{heal_amount}.")
    logs.append(f"{medic.name}'s medicine improved to {medic.skills['medicine']}.")

    return logs

def apply_weather_effects(sim, agent, logs):
    if sim.weather not in ["Storm", "Snow"]:
        return

    sickness_chance = get_weather_sickness_chance()

    if random.random() < sickness_chance:
        damage = random.randint(5, 15)

        agent.health = max(agent.health - damage, 0)
        agent.remember(f"Suffered from harsh weather: {sim.weather}.")

        logs.append(f"{agent.name} suffered from {sim.weather}. Health -{damage}.")

        if agent.health <= 0:
            agent.alive = False
            agent.status = "Dead"

def get_weather_sickness_chance():
    try:
        from config import get_setting
        return get_setting("weather_sickness_chance")
    except Exception:
        return 0.08
    
def record_death(sim, agent, cause, logs=None):
    for record in sim.death_records:
        if record["name"] == agent.name:
            return

    death_record = {
        "name": agent.name,
        "day": sim.day,
        "hour": sim.hour,
        "cause": cause,
        "role": agent.role
    }

    sim.death_records.append(death_record)

    memorial = f"{agent.name}, the {agent.role}, died on Day {sim.day} at {sim.hour}:00. Cause: {cause}."
    sim.memorials.append(memorial)

    sim.add_history(f"{agent.name} died. Cause: {cause}.")
    sim.notify(f"{agent.name} died. Cause: {cause}.", "Death")
    sim.notify_agent_event(agent.name, f"died ({cause}).")
    sim.notify_family_event(agent.surname, f"{agent.get_full_name()} died.")

    mourning_logs = []
    sim.handle_mourning(agent, mourning_logs)

    for mourning_log in mourning_logs:
        sim.add_history(mourning_log)

    if logs is not None:
        logs.extend(mourning_logs)

def check_world_state(sim, logs):
    alive = [a for a in sim.agents if a.alive]

    main_alive = [
        a for a in sim.agents
        if a.alive
        and a.location != "Exiled Lands"
        and not sim.is_extra_settlement_location(a.location)
    ]

    if len(alive) == 0:
        sim.world_state = "Extinct"
        reason = "All agents have died."

    elif len(main_alive) == 0 and not sim.extra_settlements:
        sim.world_state = "Collapsed"
        reason = "The main settlement collapsed with no surviving offshoots."

    elif sim.village_tension >= 100 and sim.wars:
        sim.world_state = "Dark Age"
        reason = "War and tension pushed society into a dark age."

    elif len(alive) >= 100 and sim.settlement_stage == "City":
        sim.world_state = "Civilization"
        reason = "The society successfully became a city civilization."

    else:
        return

    if reason not in sim.collapse_reasons:
        sim.collapse_reasons.append(reason)
        logs.append(f"WORLD STATE CHANGED: {sim.world_state}.")
        logs.append(f"Reason: {reason}")
        sim.add_history(f"World state changed to {sim.world_state}: {reason}")