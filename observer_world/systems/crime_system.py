"""
Crime and justice system for Observer World.
"""
import random
from utils import clamp
from dialogue import get_line

def record_crime(sim, criminal_name, crime, witness_name):
    if criminal_name not in sim.crime_records:
        sim.crime_records[criminal_name] = []

    sim.crime_records[criminal_name].append({
        "day": sim.day,
        "hour": sim.hour,
        "crime": crime,
        "witness": witness_name
    })

def handle_steal_food(sim, agent):
    logs = []

    if sim.resources["food"] <= 0:
        logs.append(f"{agent.name} considered stealing food, but storage was empty.")
        return logs

    stolen = random.randint(3, 10)
    stolen = min(stolen, sim.resources["food"])

    sim.resources["food"] -= stolen
    agent.hunger = max(agent.hunger - stolen, 0)

    sim.village_tension = clamp(sim.village_tension + 5, 0, 100)

    agent.remember(f"Stole {stolen} food from storage.")

    logs.append(f"{agent.name} secretly stole {stolen} food from storage.")
    logs.append(f"Village tension increased to {sim.village_tension}.")

    caught_chance = 0.35

    if "Storage Hut" in sim.settlement["buildings"]:
        caught_chance += 0.25

    if random.random() < caught_chance:
        witnesses = [
            other for other in sim.agents
            if other.name != agent.name and other.alive
        ]

        if not witnesses:
            return logs

        witness = random.choice(witnesses)

        witness.change_relationship(agent.name, "trust", -15)
        witness.change_relationship(agent.name, "respect", -5)
        agent.change_relationship(witness.name, "fear", 3)

        witness.remember(f"Saw {agent.name} stealing food.")
        agent.remember(f"{witness.name} saw me stealing food.")

        witness.add_grudge(agent.name, "caught stealing food")

        witness.set_emotion("Troubled")
        agent.set_emotion("Desperate")

        logs.append(f"{witness.name} saw {agent.name} stealing.")
        logs.append(f'{witness.name}: "{get_line(witness, "crime")}"')
        logs.append(f"{witness.name}'s trust toward {agent.name} -15.")

        sim.add_history(f"{agent.name} was caught stealing food by {witness.name}.")
        sim.record_family_rivalry(agent, witness, "stealing accusation")

        sim.record_crime(agent.name, "stealing food", witness.name)
        logs.extend(sim.handle_trial(agent, "stealing food"))

    return logs

def handle_fight(sim, agent):
    logs = []

    nearby = [
        other for other in sim.nearby_agents(agent)
        if other.alive and other.age >= 13
    ]

    if not nearby:
        logs.append(f"{agent.name} wanted to fight, but no one was nearby.")
        return logs

    grudge_targets = [
        other for other in nearby
        if other.name in agent.grudges
    ]

    if grudge_targets:
        other = random.choice(grudge_targets)
    else:
        other = random.choice(nearby)

    damage = int(random.randint(5, 20) * get_violence_multiplier())

    other.health = max(other.health - damage, 0)
    agent.energy = max(agent.energy - 15, 0)

    sim.village_tension = clamp(sim.village_tension + 10, 0, 100)

    agent.remember(f"Fought with {other.name}.")
    other.remember(f"Was hurt in a fight with {agent.name}.")

    agent.add_grudge(other.name, "fight")
    other.add_grudge(agent.name, "fight")

    agent.set_emotion("Troubled")
    other.set_emotion("Suffering")

    agent.change_relationship(other.name, "trust", -10)
    other.change_relationship(agent.name, "trust", -10)

    sim.record_family_rivalry(agent, other, "fight")

    logs.append(f"{agent.name} fought {other.name} at {agent.location}.")
    logs.append(f"{other.name}'s health -{damage}.")
    logs.append(f"Village tension increased to {sim.village_tension}.")

    if other.health <= 0:
        other.alive = False
        other.status = "Dead"

        logs.append(f"{other.name} died from the fight.")
        sim.record_death(other, f"fight with {agent.name}", logs)

        sim.record_crime(agent.name, "murder", "unknown")
        logs.extend(sim.handle_trial(agent, "murder"))

    elif sim.village_tension >= 50:
        sim.record_crime(agent.name, "fighting", other.name)
        logs.extend(sim.handle_trial(agent, "fighting"))

    return logs

def get_violence_multiplier():
    try:
        from config import get_setting
        return get_setting("violence_multiplier")
    except Exception:
        return 1.0

def handle_argument(sim, agent):
    logs = []

    nearby = [
        other for other in sim.nearby_agents(agent)
        if other.alive and other.age >= 13
    ]

    if not nearby:
        logs.append(f"{agent.name} wanted to argue, but no one was nearby.")
        return logs

    grudge_targets = [
        other for other in nearby
        if other.name in agent.grudges
    ]

    if grudge_targets:
        other = random.choice(grudge_targets)
    else:
        other = random.choice(nearby)

    agent.change_relationship(other.name, "trust", -3)
    other.change_relationship(agent.name, "trust", -3)

    agent.add_grudge(other.name, "argument")
    other.add_grudge(agent.name, "argument")

    agent.set_emotion("Troubled")
    other.set_emotion("Troubled")

    sim.village_tension = clamp(sim.village_tension + 3, 0, 100)

    agent.remember(f"Argued with {other.name}.")
    other.remember(f"Argued with {agent.name}.")

    sim.record_family_rivalry(agent, other, "argument")

    logs.append(f"{agent.name} argued with {other.name} at {agent.location}.")
    logs.append(f'{agent.name}: "{get_line(agent, "argument")}"')
    logs.append(f'{other.name}: "{get_line(other, "argument")}"')
    logs.append(f"Village tension increased to {sim.village_tension}.")

    return logs

def handle_severe_violence(sim, agent):
    logs = []

    nearby = [
        other for other in sim.nearby_agents(agent)
        if other.alive and other.age >= 13
    ]

    if not nearby:
        logs.append(f"{agent.name} had violent thoughts, but no one was nearby.")
        return logs

    target = random.choice(nearby)

    guards = [
        other for other in sim.nearby_agents(agent)
        if other.alive and other.role == "Guard"
    ]

    hatred = -agent.get_relationship(target.name)["trust"]
    aggression = agent.aggression
    fear = agent.get_relationship(target.name)["fear"]
    tension = sim.village_tension

    violence_score = aggression + hatred + fear + tension

    if "Guard Post" in sim.settlement["buildings"]:
        violence_score -= 25

    if violence_score < 140:
        logs.append(f"{agent.name} nearly attacked {target.name}, but held back.")
        agent.remember(f"Nearly attacked {target.name}, but stopped.")
        return logs

    if guards:
        guard = random.choice(guards)

        stop_chance = 0.35 + guard.skills["combat"] / 150
        stop_chance -= agent.aggression / 400

        logs.append(f"{guard.name} noticed the danger and tried to intervene.")

        if random.random() < stop_chance:
            agent.change_relationship(guard.name, "fear", 8)
            guard.change_relationship(agent.name, "trust", -10)

            sim.village_tension = clamp(sim.village_tension - 5, 0, 100)

            logs.append(f"{guard.name} stopped {agent.name} before the attack became deadly.")
            logs.append(f"{agent.name}'s fear toward {guard.name} +8.")
            logs.append(f"Village tension decreased to {sim.village_tension}.")

            sim.add_history(f"{guard.name} prevented violence by {agent.name}.")
            return logs
        else:
            logs.append(f"{guard.name} failed to stop the attack.")

    damage = int(random.randint(25, 70) * get_violence_multiplier())
    target.health = max(target.health - damage, 0)

    agent.energy = max(agent.energy - 25, 0)
    sim.village_tension = clamp(sim.village_tension + int(20 * get_tension_multiplier()), 0, 100)

    logs.append(f"{agent.name} committed severe violence against {target.name} at {agent.location}.")
    logs.append(f"{target.name}'s health -{damage}.")
    logs.append(f"Village tension increased to {sim.village_tension}.")

    witnesses = [
        other for other in sim.nearby_agents(agent)
        if other.name != target.name and other.alive
    ]

    if witnesses:
        witness = random.choice(witnesses)

        witness.change_relationship(agent.name, "trust", -30)
        witness.change_relationship(agent.name, "fear", 20)
        witness.remember(f"Witnessed {agent.name} violently attack {target.name}.")

        logs.append(f"{witness.name} witnessed the attack.")
        logs.append(f"{witness.name}'s trust toward {agent.name} -30, fear +20.")

        sim.record_crime(agent.name, "severe violence", witness.name)

    else:
        logs.append("No one witnessed the attack directly.")
        sim.record_crime(agent.name, "severe violence", "unknown")

    agent.remember(f"Committed severe violence against {target.name}.")
    target.remember(f"{agent.name} severely attacked me.")

    agent.add_grudge(target.name, "severe attack")
    target.add_grudge(agent.name, "severe attack")

    agent.set_emotion("Troubled")
    target.set_emotion("Suffering")

    sim.record_family_rivalry(agent, target, "severe violence")

    if target.health <= 0:
        target.alive = False
        target.status = "Dead"

        logs.append(f"{target.name} died from the attack.")
        sim.record_death(target, f"severe attack by {agent.name}", logs)

        sim.record_crime(agent.name, "murder", witnesses[0].name if witnesses else "unknown")
        logs.extend(sim.handle_trial(agent, "murder"))

    elif sim.village_tension >= 50:
        logs.extend(sim.handle_trial(agent, "severe violence"))

    return logs

def get_tension_multiplier():
    try:
        from config import get_setting
        return get_setting("tension_multiplier")
    except Exception:
        return 1.0
    
def handle_trial(sim, accused, crime):
    logs = []

    if accused.location == "Exiled Lands":
        return logs

    judges = [
        a for a in sim.agents
        if a.alive
        and a.name != accused.name
        and a.age >= 18
        and a.location == accused.location
    ]

    if not judges:
        logs.append(f"No one was available to judge {accused.name}.")
        return logs

    severity = 0

    if crime == "stealing food":
        severity = 20
    elif crime == "fighting":
        severity = 35
    elif crime == "severe violence":
        severity = 60
    elif crime == "murder":
        severity = 90

    if accused.faction and accused.faction in sim.factions:
        faction = sim.factions[accused.faction]
        faction_influence = faction.get("influence", 0)

        if faction_influence > 50:
            severity -= 10
            logs.append(f"{accused.faction} protected {accused.name} during the trial.")

    average_discipline = sum(j.discipline for j in judges) / len(judges)
    average_kindness = sum(j.kindness for j in judges) / len(judges)

    punishment_score = severity + average_discipline - average_kindness

    logs.append(f"A trial was held for {accused.name}. Crime: {crime}.")
    logs.append(f"Punishment score: {int(punishment_score)}.")

    if punishment_score < 30:
        logs.append(f"{accused.name} was forgiven with a warning.")
        accused.remember(f"Was forgiven after trial for {crime}.")

    elif punishment_score < 60:
        accused.wealth = max(accused.wealth - 3, 0)
        accused.remember(f"Was fined after trial for {crime}.")
        logs.append(f"{accused.name} was fined 3 wealth.")

    elif punishment_score < 85:
        accused.location = "Exiled Lands"
        accused.remember(f"Was exiled for {crime}.")
        logs.append(f"{accused.name} was exiled for {crime}.")
        sim.add_history(f"{accused.name} was exiled for {crime}.")

    else:
        accused.location = "Exiled Lands"
        accused.health = max(accused.health - 30, 0)
        accused.remember(f"Was brutally punished and exiled for {crime}.")
        logs.append(f"{accused.name} was severely punished and exiled.")

        if accused.health <= 0:
            accused.alive = False
            accused.status = "Dead"
            logs.append(f"{accused.name} died from punishment.")
            sim.record_death(accused, f"punishment for {crime}", logs)

    return logs