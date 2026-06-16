import random

LOCATIONS = [
    "Forest",
    "River",
    "Hill",
    "Camp",
    "Plains",
    "Exiled Lands"
]

FIRST_NAMES = [
    "Ari", "Kai", "Mira", "Lio", "Nora", "Eli", "Rami", "Sena",
    "Tara", "Juno", "Kira", "Daren", "Nova", "Rook", "Lena", "Oren",
    "Milo", "Zara", "Ilan", "Vera", "Toma", "Nia", "Soren", "Kale"
]


def generate_random_agent_name(index):
    base = random.choice(FIRST_NAMES)
    return f"{base}{index}"