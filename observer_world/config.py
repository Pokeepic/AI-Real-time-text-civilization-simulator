CONFIG = {
    "starting_population": 50,
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

ACTIVE_SCENARIO = "peaceful_founders"

SCENARIO_PRESETS = {
    "peaceful_founders": {
        "description": "A kind group trying to build a cooperative society.",
        "kindness_bonus": 25,
        "aggression_bonus": -20,
        "starting_food": 40,
        "starting_wood": 25,
        "starting_stone": 15,
    },

    "violent_survivors": {
        "description": "A tense group with high aggression and low trust.",
        "kindness_bonus": -15,
        "aggression_bonus": 30,
        "starting_food": 20,
        "starting_wood": 15,
        "starting_stone": 10,
    },

    "scholar_village": {
        "description": "Curious founders with strong teaching and research potential.",
        "curiosity_bonus": 30,
        "teaching_bonus": 3,
        "starting_food": 30,
        "starting_wood": 20,
        "starting_stone": 15,
    },

    "merchant_camp": {
        "description": "Social and greedy founders focused on trade and wealth.",
        "social_bonus": 3,
        "greed_bonus": 25,
        "starting_food": 35,
        "starting_wood": 20,
        "starting_stone": 10,
    },

    "exile_colony": {
        "description": "A broken group with high tension and survival pressure.",
        "kindness_bonus": -10,
        "aggression_bonus": 15,
        "starting_food": 15,
        "starting_wood": 10,
        "starting_stone": 5,
        "starting_tension": 40,
    }
}

def get_setting(key):
    preset = DIFFICULTY_PRESETS[ACTIVE_DIFFICULTY]

    if key in preset:
        return preset[key]

    return CONFIG[key]

def get_scenario():
    return SCENARIO_PRESETS[ACTIVE_SCENARIO]
