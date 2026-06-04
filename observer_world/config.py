CONFIG = {
    "starting_population": 10,
    "default_speed": 2,
    "autosave_every_hours": 6,

    "birth_chance": 0.01,
    "pregnancy_timer": 5,
    "aging_every_days": 5,

    "weather_sickness_chance": 0.08,
    "max_memories": 15,
    "max_journal_entries": 20,

    "starting_names": [
        "Mira", "Kai", "Lena", "Rook", "Niko",
        "Aria", "Daren", "Nova", "Eli", "Zane"
    ]
}

DIFFICULTY_PRESETS = {
    "peaceful": {
        "birth_chance": 0.02,
        "weather_sickness_chance": 0.03,
        "violence_multiplier": 0.5,
        "resource_multiplier": 1.4,
        "tension_multiplier": 0.7,
    },

    "balanced": {
        "birth_chance": 0.01,
        "weather_sickness_chance": 0.08,
        "violence_multiplier": 1.0,
        "resource_multiplier": 1.0,
        "tension_multiplier": 1.0,
    },

    "harsh": {
        "birth_chance": 0.008,
        "weather_sickness_chance": 0.12,
        "violence_multiplier": 1.2,
        "resource_multiplier": 0.8,
        "tension_multiplier": 1.2,
    },

    "chaotic": {
        "birth_chance": 0.015,
        "weather_sickness_chance": 0.15,
        "violence_multiplier": 1.6,
        "resource_multiplier": 0.7,
        "tension_multiplier": 1.6,
    }
}

ACTIVE_DIFFICULTY = "balanced"

def get_setting(key):
    preset = DIFFICULTY_PRESETS[ACTIVE_DIFFICULTY]

    if key in preset:
        return preset[key]

    return CONFIG[key]
