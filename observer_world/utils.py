def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def find_agent(agents, name):
    return next((a for a in agents if a.name == name), None)


def living_agents(agents):
    return [a for a in agents if a.alive]


def active_agents(agents):
    return [a for a in agents if a.alive and a.location != "Exiled Lands"]


def safe_random_choice(items):
    if not items:
        return None
    import random
    return random.choice(items)
