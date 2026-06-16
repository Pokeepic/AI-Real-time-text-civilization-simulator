def generate_agent_biography(agent):
    status = "alive" if agent.alive else "dead"

    bio = f"""
{agent.get_full_name()} is a {status} agent from Generation {agent.generation}.

Role: {agent.role}
Age: {agent.age}
Emotion: {getattr(agent, "emotional_state", "Stable")}
Life Goal: {agent.life_goal or "None"}

Family:
- Partner: {agent.partner or "None"}
- Parents: {agent.parents if agent.parents else "None"}
- Family: {agent.family if agent.family else "None"}

Social:
- Best Friend: {agent.get_best_friend() or "None"}
- Rival: {agent.get_rival() or "None"}
- Social Score: {agent.get_social_score()}

Notable Memories:
{chr(10).join("- " + memory for memory in agent.memories[-5:]) if agent.memories else "- None"}

Journal Highlights:
{chr(10).join("- " + entry for entry in agent.journal[-5:]) if agent.journal else "- None"}
"""

    return bio.strip()

def export_agent_biography(agent):
    bio = generate_agent_biography(agent)

    filename = f"biography_{agent.name}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(bio)

    return filename

def generate_family_summary(sim, surname):
    members = [
        a for a in sim.agents
        if getattr(a, "surname", None) == surname
    ]

    if not members:
        return f"No records found for the {surname} family."

    alive = [a for a in members if a.alive]
    dead = [a for a in members if not a.alive]

    leaders = [a for a in members if a.role == "Leader"]
    generations = sorted(set(a.generation for a in members))

    summary = f"""
The {surname} Family Dynasty

Members: {len(members)}
Living Members: {len(alive)}
Dead Members: {len(dead)}
Generations: {generations}
Family Reputation: {sim.family_reputation.get(surname, 0)}

Notable Members:
{chr(10).join("- " + a.get_full_name() + f" ({a.role}, Gen {a.generation})" for a in members[:10])}

Leaders:
{chr(10).join("- " + a.get_full_name() for a in leaders) if leaders else "- None"}

This family has become part of the history of {getattr(sim, "world_name", "the world")}.
"""

    return summary.strip()

def generate_world_story_summary(sim):
    alive = [a for a in sim.agents if a.alive]
    dead = [a for a in sim.agents if not a.alive]

    summary = f"""
World Story Summary: {getattr(sim, "world_name", "Unknown")}

Day: {sim.day}
Hour: {sim.hour}:00
Era: {getattr(sim, "current_era", "Age of Survival")}
World State: {getattr(sim, "world_state", "Ongoing")}

Population:
- Alive: {len(alive)}
- Dead: {len(dead)}

Settlement:
- Main Settlement: {sim.settlement.get("name") or "None"}
- Stage: {getattr(sim, "settlement_stage", "Camp")}
- Leader: {getattr(sim, "leader", None) or "None"}

Society:
- Culture: {sim.get_culture_identity()}
- Belief: {sim.get_belief_identity()}
- Technologies: {", ".join(sim.technologies) if sim.technologies else "None"}
- Laws: {len(sim.laws)}
- Wars: {len(sim.wars)}
- Treaties: {len(sim.treaties)}

Recent History:
{chr(10).join("- " + event for event in sim.world_history[-10:]) if sim.world_history else "- None"}
"""

    return summary.strip()

def generate_weekly_newspaper(sim):
    recent_notifications = [
        n for n in getattr(sim, "notifications", [])
        if isinstance(n, dict)
        and sim.day - n.get("day", sim.day) <= 7
    ]

    recent_history = getattr(sim, "world_history", [])[-20:]

    sections = {
        "Leadership": [],
        "Deaths": [],
        "Relationships": [],
        "War & Diplomacy": [],
        "Technology": [],
        "Other News": [],
    }

    for n in recent_notifications:
        category = n.get("category", "General")
        line = f"Day {n.get('day')}, Hour {n.get('hour')}:00 — {n.get('message')}"

        if category == "Leadership":
            sections["Leadership"].append(line)
        elif category == "Death":
            sections["Deaths"].append(line)
        elif category == "Relationship":
            sections["Relationships"].append(line)
        elif category in ["War", "Diplomacy"]:
            sections["War & Diplomacy"].append(line)
        elif category == "Technology":
            sections["Technology"].append(line)
        else:
            sections["Other News"].append(line)

    summary = f"""
THE {getattr(sim, "world_name", "WORLD").upper()} WEEKLY CHRONICLE
Day {sim.day}, Hour {sim.hour}:00

Era: {getattr(sim, "current_era", "Age of Survival")}
World State: {getattr(sim, "world_state", "Ongoing")}
Population: {len([a for a in sim.agents if a.alive])}

LEADERSHIP
{chr(10).join("- " + item for item in sections["Leadership"][-5:]) if sections["Leadership"] else "- No major leadership news."}

DEATHS
{chr(10).join("- " + item for item in sections["Deaths"][-5:]) if sections["Deaths"] else "- No major deaths reported."}

RELATIONSHIPS
{chr(10).join("- " + item for item in sections["Relationships"][-5:]) if sections["Relationships"] else "- No major relationship news."}

WAR & DIPLOMACY
{chr(10).join("- " + item for item in sections["War & Diplomacy"][-5:]) if sections["War & Diplomacy"] else "- No war or diplomacy updates."}

TECHNOLOGY
{chr(10).join("- " + item for item in sections["Technology"][-5:]) if sections["Technology"] else "- No technology updates."}

RECENT HISTORY
{chr(10).join("- " + event for event in recent_history[-10:]) if recent_history else "- No recent history recorded."}
"""

    return summary.strip()

def generate_fallen_heroes_summary(sim):
    if not getattr(sim, "death_records", []):
        return "No fallen heroes have been recorded yet."

    lines = ["FALLEN HEROES OF OBSERVER WORLD", ""]

    for record in sim.death_records[-20:]:
        lines.append(
            f"- {record.get('name')} died on Day {record.get('day')} "
            f"at Hour {record.get('hour')}:00. Cause: {record.get('cause')}."
        )

    return "\n".join(lines)

def generate_family_rivalry_summary(sim):
    rivalries = getattr(sim, "family_rivalries", {})

    if not rivalries:
        return "No family rivalries have been recorded yet."

    lines = ["FAMILY RIVALRIES", ""]

    for families, data in rivalries.items():
        score = data.get("score", 0)
        reasons = data.get("reasons", [])

        lines.append(f"{' vs '.join(families)}")
        lines.append(f"Rivalry Score: {score}")
        lines.append("Recent Reasons:")

        if reasons:
            for reason in reasons[-5:]:
                lines.append(f"- {reason}")
        else:
            lines.append("- None")

        lines.append("")

    return "\n".join(lines)

def generate_civilization_timeline_summary(sim):
    lines = ["CIVILIZATION TIMELINE", ""]

    if getattr(sim, "eras", []):
        lines.append("ERAS")
        for era in sim.eras:
            lines.append(f"- {era.get('name')} began on Day {era.get('start_day')}")
        lines.append("")

    if getattr(sim, "milestones", set()):
        lines.append("MILESTONES")
        for milestone in sorted(sim.milestones):
            lines.append(f"- {milestone}")
        lines.append("")

    if getattr(sim, "world_history", []):
        lines.append("RECENT HISTORY")
        for event in sim.world_history[-20:]:
            lines.append(f"- {event}")

    if len(lines) <= 2:
        return "No civilization timeline has formed yet."

    return "\n".join(lines)

def generate_greatest_leader_biography(sim):
    leaders = [
        a for a in sim.agents
        if a.role == "Leader"
    ]

    if not leaders:
        return "No leaders have emerged yet."

    greatest = max(
        leaders,
        key=lambda a: (
            a.generation,
            a.wealth,
            len(a.relationships),
            a.age
        )
    )

    bio = f"""
GREATEST LEADER OF {getattr(sim, "world_name", "THE WORLD").upper()}

Name: {greatest.get_full_name()}
Age: {greatest.age}
Generation: {greatest.generation}
Status: {"Alive" if greatest.alive else "Deceased"}

Leadership Profile:
- Wealth: {greatest.wealth}
- Social Score: {greatest.get_social_score()}
- Best Friend: {greatest.get_best_friend() or "None"}
- Rival: {greatest.get_rival() or "None"}
- Emotional State: {greatest.emotional_state}

Achievements:
- Role: {greatest.role}
- Life Goal: {greatest.life_goal or "None"}
- Completed Goals: {greatest.completed_goals}

Recent Memories:
{chr(10).join("- " + memory for memory in greatest.memories[-5:]) if greatest.memories else "- None"}

Journal Highlights:
{chr(10).join("- " + entry for entry in greatest.journal[-5:]) if greatest.journal else "- None"}

This leader played a significant role in shaping the history of {getattr(sim, "world_name", "the world")}.
"""

    return bio.strip()

def generate_most_influential_family_summary(sim):
    if not getattr(sim, "family_reputation", {}):
        return "No family reputation records exist yet."

    top_family = max(
        sim.family_reputation,
        key=lambda surname: sim.family_reputation.get(surname, 0)
    )

    members = [
        a for a in sim.agents
        if getattr(a, "surname", None) == top_family
    ]

    leaders = [a for a in members if a.role == "Leader"]

    summary = f"""
MOST INFLUENTIAL FAMILY

Family: {top_family}
Reputation: {sim.family_reputation.get(top_family, 0)}
Members: {len(members)}
Living Members: {len([a for a in members if a.alive])}
Generations: {sorted(set(a.generation for a in members))}

Notable Members:
{chr(10).join("- " + a.get_full_name() + f" ({a.role}, Gen {a.generation})" for a in members[:10]) if members else "- None"}

Leaders:
{chr(10).join("- " + a.get_full_name() for a in leaders) if leaders else "- None"}

The {top_family} family has become one of the most influential bloodlines in {getattr(sim, "world_name", "the world")}.
"""

    return summary.strip()

def generate_world_ending_report(sim):
    if sim.world_state not in ["Extinct", "Civilization", "Collapsed", "Dark Age"]:
        return "The world has not reached an ending state yet."

    alive = [a for a in sim.agents if a.alive]
    dead = [a for a in sim.agents if not a.alive]

    report = f"""
WORLD ENDING REPORT

World: {getattr(sim, "world_name", "Unknown")}
Final State: {sim.world_state}
Day: {sim.day}
Hour: {sim.hour}:00

Population:
- Alive: {len(alive)}
- Dead: {len(dead)}

Final Era: {getattr(sim, "current_era", "Unknown")}
Main Settlement: {sim.settlement.get("name") or "None"}
Settlement Stage: {getattr(sim, "settlement_stage", "Camp")}
Leader: {getattr(sim, "leader", None) or "None"}

Collapse / Ending Reasons:
{chr(10).join("- " + reason for reason in getattr(sim, "collapse_reasons", [])) if getattr(sim, "collapse_reasons", []) else "- None recorded"}

Final Culture: {sim.get_culture_identity()}
Final Belief: {sim.get_belief_identity()}

Wars: {len(sim.wars)}
Treaties: {len(sim.treaties)}
Technologies: {len(sim.technologies)}
Milestones: {len(sim.milestones)}

Final History:
{chr(10).join("- " + event for event in sim.world_history[-20:]) if sim.world_history else "- None"}
"""

    return report.strip()

def generate_story_export_bundle(sim):
    sections = [
        generate_world_story_summary(sim),
        generate_weekly_newspaper(sim),
        generate_fallen_heroes_summary(sim),
        generate_family_rivalry_summary(sim),
        generate_civilization_timeline_summary(sim),
        generate_greatest_leader_biography(sim),
        generate_most_influential_family_summary(sim),
        generate_world_ending_report(sim),
    ]

    return "\n\n" + ("=" * 60 + "\n\n").join(sections)