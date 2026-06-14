def record_world_snapshot(sim):
    if not hasattr(sim, "history_snapshots"):
        sim.history_snapshots = []

    alive = [a for a in sim.agents if a.alive]
    dead = [a for a in sim.agents if not a.alive]

    avg_health = 0
    avg_hunger = 0
    avg_energy = 0

    if alive:
        avg_health = sum(a.health for a in alive) / len(alive)
        avg_hunger = sum(a.hunger for a in alive) / len(alive)
        avg_energy = sum(a.energy for a in alive) / len(alive)

    births_today = len([
        a for a in sim.agents
        if getattr(a, "age", 0) == 0
    ])

    deaths_today = len([
        record for record in sim.death_records
        if record.get("day") == sim.day
    ])

    previous_alive = alive_count = len(alive)
    growth_rate = 0

    if getattr(sim, "history_snapshots", []):
        previous_alive = sim.history_snapshots[-1].get("alive", alive_count)

        if previous_alive > 0:
            growth_rate = (
                (alive_count - previous_alive) / previous_alive
            ) * 100

    snapshot = {
        "day": sim.day,
        "hour": sim.hour,
        "alive": len(alive),
        "dead": len(dead),
        "food": sim.resources.get("food", 0),
        "wood": sim.resources.get("wood", 0),
        "stone": sim.resources.get("stone", 0),
        "tension": sim.village_tension,
        "wars": len(sim.wars),
        "technologies": len(sim.technologies),
        "births_total": len([a for a in sim.agents if getattr(a, "age", 0) == 0]),
        "deaths_total": len(sim.death_records),
        "notifications_total": len(sim.notifications),
        "avg_health": avg_health,
        "avg_hunger": avg_hunger,
        "avg_energy": avg_energy,
        "food_per_person": sim.resources.get("food", 0) / max(len(alive), 1),
        "births_today": births_today,
        "deaths_today": deaths_today,
        "growth_rate": growth_rate,
    }

    sim.history_snapshots.append(snapshot)

    if len(sim.history_snapshots) > 1000:
        sim.history_snapshots.pop(0)