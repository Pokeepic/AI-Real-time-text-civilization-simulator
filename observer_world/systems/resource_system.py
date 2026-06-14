"""
Resource system for Observer World.
"""


def consume_daily_food(sim, logs):
    if sim.hour != 7:
        return

    alive = [a for a in sim.agents if a.alive]

    if not alive:
        return

    food_needed = len(alive)

    if sim.resources.get("food", 0) >= food_needed:
        sim.resources["food"] -= food_needed

        for agent in alive:
            agent.hunger = max(agent.hunger - 10, 0)

        logs.append(f"The settlement consumed {food_needed} food for daily meals.")

    else:
        shortage = food_needed - sim.resources.get("food", 0)
        sim.resources["food"] = 0

        for agent in alive:
            agent.hunger = min(agent.hunger + 15, 100)

        sim.village_tension = min(sim.village_tension + 5, 100)

        logs.append(f"Food shortage occurred. Missing food: {shortage}.")
        logs.append("Hunger and village tension increased.")

def spoil_excess_food(sim, logs):
    if sim.hour != 6:
        return

    food = sim.resources.get("food", 0)

    if food <= 100:
        return

    spoiled = int((food - 100) * 0.10)

    if spoiled <= 0:
        return

    sim.resources["food"] = max(food - spoiled, 0)

    logs.append(f"Some stored food spoiled. Food -{spoiled}.")

def enforce_storage_capacity(sim, logs):
    if sim.hour != 6:
        return

    capacity = 150

    if "Storage Hut" in sim.settlement["buildings"]:
        capacity += 250

    if "Stone Construction" in sim.technologies:
        capacity += 200

    food = sim.resources.get("food", 0)

    if food > capacity:
        lost = food - capacity
        sim.resources["food"] = capacity
        logs.append(f"Food exceeded storage capacity. Excess food lost: {lost}.")

def enforce_material_storage_capacity(sim, logs):
    if sim.hour != 6:
        return

    capacity = 200

    if "Storage Hut" in sim.settlement["buildings"]:
        capacity += 300

    if "Stone Construction" in sim.technologies:
        capacity += 300

    for resource in ["wood", "stone"]:
        amount = sim.resources.get(resource, 0)

        if amount > capacity:
            lost = amount - capacity
            sim.resources[resource] = capacity
            logs.append(f"{resource.capitalize()} exceeded storage capacity. Excess lost: {lost}.")