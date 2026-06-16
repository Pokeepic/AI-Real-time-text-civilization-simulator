import random


FIRST_NAMES = [
    "Amina", "Mira", "Nora", "Lena", "Sena", "Zara", "Elena", "Tara",
    "Kira", "Vera", "Nia", "Luna", "Aria", "Maya", "Rina", "Ilya",
    "Kai", "Rami", "Eli", "Lio", "Daren", "Oren", "Milo", "Soren",
    "Rook", "Toma", "Ilan", "Nova", "Kale", "Ari", "Juno", "Riven",
    "Samir", "Tarek", "Omar", "Nadir", "Malik", "Yusuf", "Hana", "Leila",
    "Anya", "Sofia", "Nadia", "Iris", "Rowan", "Evan", "Talin", "Kian",
    "Alya", "Nahla", "Selene", "Rhea", "Isla", "Mina", "Dalia", "Freya",
    "Yara", "Noor", "Azra", "Maren", "Lyra", "Seren", "Eira", "Mika",
    "Idris", "Rafi", "Zain", "Emir", "Nolan", "Asher", "Theo", "Dima",
    "Ren", "Ciro", "Lucan", "Orin", "Vale", "Cael", "Niko", "Toren"
]


MIDDLE_NAMES = [
    "Ari", "Mira", "Kai", "Lena", "Noor", "Riven", "Sena", "Talin",
    "Yara", "Rowan", "Eli", "Nia", "Oren", "Iris", "Zain", "Aria",
    "Dawn", "River", "Ash", "Moon", "Vale", "Storm", "Hearth", "Ember"
]


LAST_NAMES = [
    "Rahman", "Silva", "Moreno", "Tan", "Haddad", "Ishikawa", "Stone",
    "Vale", "River", "Moon", "Ash", "Hearth", "Storm", "Oak", "Wolf",
    "Sunward", "Mooncrest", "Stonekeeper", "Ashfield", "Riverborn",
    "Valecrest", "Stormwatch", "Oakwood", "Hearthborn", "Dawnfield",
    "Nightvale", "Ironwood", "Goldriver", "Emberfall", "Silverline",
    "Brightwell", "Darkmoor", "Rainsong", "Windmere", "Starfall",
    "Duskwalker", "Lightwood", "Frostvale", "Redfern", "Blackriver",
    "Highfield", "Lowstone", "Glassmere", "Greymark", "Westbrook",
    "Eastvale", "Northwind", "Southmere", "Sunriver", "Moonfield",
    "Amberhall", "Rosewick", "Thornvale", "Mistwood", "Cloudborne",
    "Marrowick", "Elderbranch", "Silverbrook", "Dawnbrook", "Nightbrook"
]


EPITHETS = [
    "the Younger", "the Elder", "the Kind", "the Brave", "the Quiet",
    "the Wanderer", "the Builder", "the Healer", "the Watchful",
    "the Patient", "the Swift", "the Honest", "the Restless",
    "the Dreamer", "the Bold", "the Gentle", "the Wise", "the Lucky",
    "of Dawn", "of River", "of Stone", "of Hearth", "of Moon",
    "of Ash", "of Vale", "of Storm", "of Oak", "of Ember"
]


def generate_unique_name(existing_names):
    """
    Generate a unique natural-looking name without visible numbers.
    This can handle thousands of agents.
    existing_names should be a set of already-used names.
    """

    # Simple full name first
    for _ in range(500):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"

        if name not in existing_names:
            return name

    # Add middle name if simple names are crowded
    for _ in range(1000):
        first = random.choice(FIRST_NAMES)
        middle = random.choice(MIDDLE_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {middle} {last}"

        if name not in existing_names:
            return name

    # Add epithet if population becomes very large
    for _ in range(2000):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        epithet = random.choice(EPITHETS)
        name = f"{first} {last} {epithet}"

        if name not in existing_names:
            return name

    # Final fallback, still no ugly number
    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)
    epithet = random.choice(EPITHETS)

    return f"{first} {middle} {last} {epithet}"

def generate_founder_age():
    """
    Generates a realistic age for starting/founder agents.
    This gives the first village children, adults, older adults, and elders.
    """

    roll = random.random()

    # Small number of teenagers
    if roll < 0.10:
        return random.randint(13, 17)

    # Main working/reproducing population
    if roll < 0.65:
        return random.randint(18, 39)

    # Mature adults
    if roll < 0.88:
        return random.randint(40, 59)

    # Elders
    return random.randint(60, 72)