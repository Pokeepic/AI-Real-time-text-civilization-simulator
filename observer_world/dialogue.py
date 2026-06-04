import random


def personality_style(agent):
    if agent.aggression > 75:
        return "sharp"
    if agent.kindness > 75:
        return "warm"
    if agent.curiosity > 75:
        return "curious"
    if agent.pride > 75:
        return "proud"
    return "neutral"


def get_line(agent, topic):
    style = personality_style(agent)

    lines = {
        "survival": {
            "warm": [
                "We should make sure no one is left hungry.",
                "If we share what we find, we all survive."
            ],
            "sharp": [
                "Sentiment will not keep us alive.",
                "Move faster. Hunger does not wait."
            ],
            "curious": [
                "There must be patterns in this place.",
                "If we observe carefully, we can learn how to survive here."
            ],
            "proud": [
                "I will not be useless in this place.",
                "Others may panic. I will not."
            ],
            "neutral": [
                "We need food, shelter, and a plan.",
                "Survival comes first."
            ]
        },
        "argument": {
            "warm": [
                "I do not want this to become worse.",
                "Please, calm down. We can still fix this."
            ],
            "sharp": [
                "You are testing my patience.",
                "Say one more careless thing."
            ],
            "curious": [
                "Why do you keep acting against the group?",
                "There has to be a reason for this behavior."
            ],
            "proud": [
                "Do not speak to me like I am beneath you.",
                "I know my worth."
            ],
            "neutral": [
                "This is becoming a problem.",
                "We need to settle this."
            ]
        },
        "teaching": {
            "warm": [
                "Let me show you slowly.",
                "You are improving. Do not rush."
            ],
            "sharp": [
                "Watch carefully. I will not explain twice.",
                "Mistakes cost time. Focus."
            ],
            "curious": [
                "Notice the small details. That is where learning begins.",
                "Try asking why it works, not just how."
            ],
            "proud": [
                "I learned this through effort. Respect the lesson.",
                "Few understand this as well as I do."
            ],
            "neutral": [
                "Here is how it works.",
                "Pay attention to the method."
            ]
        },
        "crime": {
            "warm": [
                "Why would you do this to us?",
                "People trusted you."
            ],
            "sharp": [
                "You thought no one would notice?",
                "There will be consequences."
            ],
            "curious": [
                "What pushed you this far?",
                "Was it hunger, greed, or fear?"
            ],
            "proud": [
                "You dishonored yourself.",
                "I would never lower myself like this."
            ],
            "neutral": [
                "This cannot be ignored.",
                "The group needs to respond."
            ]
        }
    }

    return random.choice(lines.get(topic, lines["survival"]).get(style, lines[topic]["neutral"]))
