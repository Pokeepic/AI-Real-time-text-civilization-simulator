import streamlit as st
import os

from agent import Agent
from simulation import Simulation
from save_system import load_world, save_world, delete_save
from config import CONFIG
from export_data import export_agents_csv, export_relationships_csv
from stability import stabilize_sim

st.set_page_config(page_title="Observer World", layout="wide")

# -----------------------------
# Create / Load World
# -----------------------------

def create_new_world():
    agents = [Agent(name) for name in CONFIG["starting_names"]]
    return Simulation(agents)


if "sim" not in st.session_state:
    sim = load_world()

    if sim is None:
        sim = create_new_world()

    st.session_state.sim = sim

if "logs" not in st.session_state:
    st.session_state.logs = []


sim = st.session_state.sim

stabilize_sim(sim)
# -----------------------------
# Header
# -----------------------------

st.subheader("World Controls")

control_col1, control_col2, control_col3, control_col4, control_col5, control_col6 = st.columns(6)

with control_col1:
    if st.button("Advance 1 Hour"):
        logs = sim.tick()
        st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

with control_col2:
    if st.button("Run 6 Hours"):
        for _ in range(6):
            logs = sim.tick()
            st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

with control_col3:
    if st.button("Run 1 Day"):
        for _ in range(24):
            logs = sim.tick()
            st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

with control_col4:
    if st.button("Run 7 Days"):
        for _ in range(24 * 7):
            logs = sim.tick()
            st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

with control_col5:
    if st.button("Save"):
        save_world(sim)
        st.success("World saved.")

with control_col6:
    if st.button("Reset World"):
        delete_save()
        st.session_state.sim = create_new_world()
        st.session_state.logs = []
        st.rerun()

# -----------------------------
# Metrics
# -----------------------------

alive_agents = [a for a in sim.agents if a.alive]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Day", sim.day)
col2.metric("Hour", f"{sim.hour}:00")
col3.metric("Population", len(alive_agents))
col4.metric("World State", getattr(sim, "world_state", "Ongoing"))

# -----------------------------
# Recent Events
# -----------------------------

st.subheader("Recent Events")

event_filter = st.selectbox(
    "Event Filter",
    [
        "All",
        "Important",
        "Social",
        "Crime",
        "Family",
        "War/Diplomacy",
        "Technology",
        "Errors",
    ]
)

event_keywords = {
    "Important": [
        "died", "born", "leader", "war", "rebellion", "murder",
        "technology", "milestone", "trial", "exiled", "treaty",
        "founded", "completed", "new era", "settlement"
    ],
    "Social": [
        "talked", "friendship", "trust", "bond", "partner",
        "taught", "learned", "helped"
    ],
    "Crime": [
        "stole", "crime", "trial", "fight", "murder",
        "severe violence", "exiled"
    ],
    "Family": [
        "born", "family", "partner", "pregnant", "child"
    ],
    "War/Diplomacy": [
        "war", "raid", "treaty", "peace", "alliance",
        "diplomacy", "threat"
    ],
    "Technology": [
        "technology", "research", "unlocked", "tools",
        "medicine", "crop rotation"
    ],
    "Errors": [
        "error"
    ],
}

recent_logs = st.session_state.logs[-300:]

if event_filter != "All":
    keywords = event_keywords[event_filter]
    recent_logs = [
        log for log in recent_logs
        if any(keyword in log.lower() for keyword in keywords)
    ]

for log in recent_logs[-40:]:
    if "ERROR" in log:
        st.error(log)
    elif any(word in log.lower() for word in ["died", "murder", "war", "rebellion"]):
        st.warning(log)
    elif any(word in log.lower() for word in ["born", "technology", "milestone", "treaty"]):
        st.success(log)
    else:
        st.write(log)
# -----------------------------
# Tabs
# -----------------------------

tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Agents",
    "Settlements",
    "History",
    "Chronicles",
    "Controls",
    "Errors",
    "Notifications"
])


# -----------------------------
# Agents Tab
# -----------------------------

with tab0:
    st.subheader("World Overview")

    alive = [a for a in sim.agents if a.alive]
    dead = [a for a in sim.agents if not a.alive]
    adults = [a for a in alive if a.age >= 18]
    children = [a for a in alive if a.age < 18]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Alive", len(alive))
    c2.metric("Dead", len(dead))
    c3.metric("Adults", len(adults))
    c4.metric("Children", len(children))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Food", sim.resources.get("food", 0))
    c6.metric("Wood", sim.resources.get("wood", 0))
    c7.metric("Stone", sim.resources.get("stone", 0))
    c8.metric("Tension", sim.village_tension)

    c9, c10, c11, c12 = st.columns(4)
    c9.metric("Wars", len(sim.wars))
    c10.metric("Treaties", len(sim.treaties))
    c11.metric("Technologies", len(sim.technologies))
    c12.metric("Laws", len(sim.laws))

    st.divider()

    st.subheader("Latest Notifications")

    notifications = getattr(sim, "notifications", [])

    if notifications:
        for notification in reversed(notifications[-5:]):
            st.info(notification)
    else:
        st.info("No notifications yet.")

    st.divider()

    st.subheader("World Identity")

    world_col1, world_col2 = st.columns(2)

    with world_col1:
        st.write(f"**World Name:** {getattr(sim, 'world_name', 'Unknown')}")
        st.write(f"**World State:** {getattr(sim, 'world_state', 'Ongoing')}")
        st.write(f"**Era:** {getattr(sim, 'current_era', 'Age of Survival')}")
        st.write(f"**Scenario:** {getattr(sim, 'scenario', 'Unknown')}")

    with world_col2:
        st.write(f"**Main Settlement:** {sim.settlement.get('name') or 'None'}")
        st.write(f"**Settlement Stage:** {getattr(sim, 'settlement_stage', 'Camp')}")
        st.write(f"**Leader:** {getattr(sim, 'leader', None) or 'None'}")
        st.write(f"**Current Project:** {sim.current_project['name'] if sim.current_project else 'None'}")
        st.write(f"**Culture:** {sim.get_culture_identity()}")
        st.write(f"**Belief:** {sim.get_belief_identity()}")

    st.divider()

    st.subheader("Top Agents")

    top_col1, top_col2, top_col3 = st.columns(3)

    with top_col1:
        st.write("**Top Wealth**")
        top_wealth = sorted(alive, key=lambda a: a.wealth, reverse=True)[:5]
        st.dataframe([
            {"Name": a.name, "Wealth": a.wealth, "Role": a.role}
            for a in top_wealth
        ], use_container_width=True)

    with top_col2:
        st.write("**Top Combat**")
        top_combat = sorted(alive, key=lambda a: a.skills.get("combat", 0), reverse=True)[:5]
        st.dataframe([
            {"Name": a.name, "Combat": a.skills.get("combat", 0), "Role": a.role}
            for a in top_combat
        ], use_container_width=True)

    with top_col3:
        st.write("**Top Medicine**")
        top_medicine = sorted(alive, key=lambda a: a.skills.get("medicine", 0), reverse=True)[:5]
        st.dataframe([
            {"Name": a.name, "Medicine": a.skills.get("medicine", 0), "Role": a.role}
            for a in top_medicine
        ], use_container_width=True)

    st.subheader("Family Lines")

    family_counts = {}

    for agent in sim.agents:
        surname = getattr(agent, "surname", None)

        if surname:
            family_counts[surname] = family_counts.get(surname, 0) + 1

    family_data = []

    for surname, count in sorted(
        family_counts.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        family_data.append({
            "Family Name": surname,
            "Members": count,
            "Reputation": sim.family_reputation.get(surname, 0)
        })

    if family_data:
        st.dataframe(family_data, use_container_width=True)
    else:
        st.info("No family lines have formed yet.")

    st.divider()

    st.subheader("Family Rivalries")

    rivalry_rows = []

    for families, data in sim.family_rivalries.items():
        rivalry_rows.append({
            "Families": " vs ".join(families),
            "Score": data.get("score", 0),
            "Recent Reasons": ", ".join(data.get("reasons", [])[-3:])
        })

    if rivalry_rows:
        st.dataframe(rivalry_rows, use_container_width=True)
    else:
        st.info("No family rivalries yet.")

    st.divider()

    st.subheader("Family Alliances")

    alliance_rows = []

    for families, data in sim.family_alliances.items():
        alliance_rows.append({
            "Families": " + ".join(families),
            "Score": data.get("score", 0),
            "Recent Reasons": ", ".join(data.get("reasons", [])[-3:])
        })

    if alliance_rows:
        st.dataframe(alliance_rows, use_container_width=True)
    else:
        st.info("No family alliances yet.")

    st.divider()

    st.subheader("Population by Location")

    location_counts = {}

    for agent in sim.agents:
        if agent.alive:
            location_counts[agent.location] = location_counts.get(agent.location, 0) + 1

    location_data = [
        {"Location": location, "Population": count}
        for location, count in sorted(location_counts.items())
    ]

    st.dataframe(location_data, use_container_width=True)

    st.divider()

    st.subheader("Recent Important Events")

    important_words = [
        "died", "born", "leader", "war", "rebellion", "murder",
        "technology", "milestone", "trial", "exiled", "treaty",
        "founded", "completed", "new era", "settlement", "crime"
    ]

    important_logs = [
        log for log in st.session_state.logs[-500:]
        if any(word in log.lower() for word in important_words)
    ]

    if important_logs:
        for log in important_logs[-20:]:
            st.info(log)
    else:
        st.write("No major events yet.")

    st.divider()

    st.subheader("Current Risks")

    risks = []

    if sim.resources.get("food", 0) < 20:
        risks.append("Low food storage")

    if sim.village_tension >= 70:
        risks.append("High village tension")

    if any(a.health < 40 and a.alive for a in sim.agents):
        risks.append("Some agents are critically injured or sick")

    if any(a.hunger > 85 and a.alive for a in sim.agents):
        risks.append("Some agents are near starvation")

    if sim.wars:
        risks.append("Settlement has experienced war")

    if sim.rebellions:
        risks.append("Rebellion history exists")

    if risks:
        for risk in risks:
            st.warning(risk)
    else:
        st.success("No major risks detected.")
    
    st.divider()

    st.subheader("Quick Charts")

    resource_chart_data = {
        "Food": sim.resources.get("food", 0),
        "Wood": sim.resources.get("wood", 0),
        "Stone": sim.resources.get("stone", 0),
    }

    st.write("**Main Resources**")
    st.bar_chart(resource_chart_data)

    role_counts = {}

    for agent in sim.agents:
        if agent.alive:
            role_counts[agent.role] = role_counts.get(agent.role, 0) + 1

    st.write("**Roles Distribution**")
    st.bar_chart(role_counts)

    status_counts = {}

    for agent in sim.agents:
        status_counts[agent.status] = status_counts.get(agent.status, 0) + 1

    st.write("**Health Status Distribution**")
    st.bar_chart(status_counts)

    emotion_counts = {}

    for agent in sim.agents:
        emotion = getattr(agent, "emotional_state", "Stable")
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    st.write("**Emotional State Distribution**")
    st.bar_chart(emotion_counts)

    st.divider()

    st.subheader("Simulation Summary")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        st.info(f"""
        **World:** {getattr(sim, 'world_name', 'Unknown')}

        **Era:** {getattr(sim, 'current_era', 'Age of Survival')}

        **Main Settlement:** {sim.settlement.get('name') or 'None'}

        **Culture:** {sim.get_culture_identity()}

        **Belief:** {sim.get_belief_identity()}
        """)

    with summary_col2:
        st.info(f"""
        **Population:** {len(alive)}

        **Deaths:** {len(dead)}

        **Wars:** {len(sim.wars)}

        **Treaties:** {len(sim.treaties)}

        **Technologies:** {', '.join(sim.technologies) if sim.technologies else 'None'}
        """)
    
    st.divider()

    st.subheader("Dashboard Health Check")

    health_checks = []

    if not sim.agents:
        health_checks.append("No agents found")

    if not hasattr(sim, "error_log"):
        health_checks.append("Missing error_log attribute")

    if getattr(sim, "error_log", []):
        health_checks.append(f"{len(sim.error_log)} simulation errors recorded")

    if sim.day < 1:
        health_checks.append("Invalid day value")

    if sim.hour < 0 or sim.hour > 23:
        health_checks.append("Invalid hour value")

    if not isinstance(sim.resources, dict):
        health_checks.append("Resources data is broken")

    if health_checks:
        for check in health_checks:
            st.error(check)
    else:
        st.success("Simulation data looks healthy.")
    
    st.divider()

    st.subheader("Project Status")

    status_items = {
        "Autonomous Agents": bool(sim.agents),
        "Families / Generations": any(a.generation > 1 for a in sim.agents),
        "Settlement System": sim.settlement.get("name") is not None,
        "Leadership": getattr(sim, "leader", None) is not None,
        "Culture System": sim.get_culture_identity() != "Undefined",
        "Belief System": sim.get_belief_identity() != "None",
        "Technology System": len(sim.technologies) > 0,
        "Multiple Settlements": len(sim.extra_settlements) > 0,
        "War / Diplomacy": len(sim.wars) > 0 or len(sim.treaties) > 0,
        "Chronicles": len(sim.chronicles) > 0,
        "Error Logging": hasattr(sim, "error_log"),
    }

    for item, active in status_items.items():
        if active:
            st.success(f"✅ {item}")
        else:
            st.info(f"⏳ {item}")
    

with tab1:
    st.subheader("Agents")

    search_query = st.text_input("Search Agent")

    st.subheader("Agent Filters")

    only_alive = st.checkbox("Show only alive agents", value=True)

    role_options = sorted(list(set(a.role for a in sim.agents)))
    selected_roles = st.multiselect("Filter by role", role_options, default=role_options)

    location_options = sorted(list(set(a.location for a in sim.agents)))
    selected_locations = st.multiselect("Filter by location", location_options, default=location_options)

    generation_options = sorted(list(set(a.generation for a in sim.agents)))
    selected_generations = st.multiselect(
        "Filter by generation",
        generation_options,
        default=generation_options
    )

    show_critical_only = st.checkbox("Critical / Injured only")
    show_socially_isolated = st.checkbox("Socially isolated only")

    sort_by = st.selectbox(
        "Sort by",
        [
            "Name",
            "Age",
            "Health",
            "Wealth",
            "Generation",
            "Combat",
            "Medicine",
            "Social Score",
        ]
    )

    filtered_agents = sim.agents

    if search_query:
        filtered_agents = [
            a for a in filtered_agents
            if search_query.lower() in a.name.lower()
        ]

    if only_alive:
        filtered_agents = [a for a in filtered_agents if a.alive]

    filtered_agents = [
        a for a in filtered_agents
        if a.role in selected_roles
        and a.location in selected_locations
        and a.generation in selected_generations
    ]

    if show_critical_only:
        filtered_agents = [
            a for a in filtered_agents
            if a.status in ["Critical", "Injured"]
        ]
    
    if show_socially_isolated:
        filtered_agents = [
            a for a in filtered_agents
            if a.get_social_score() <= 0
        ]

    if sort_by == "Name":
        filtered_agents.sort(key=lambda a: a.name)
    elif sort_by == "Age":
        filtered_agents.sort(key=lambda a: a.age)
    elif sort_by == "Health":
        filtered_agents.sort(key=lambda a: a.health)
    elif sort_by == "Wealth":
        filtered_agents.sort(key=lambda a: a.wealth)
    elif sort_by == "Generation":
        filtered_agents.sort(key=lambda a: a.generation)
    elif sort_by == "Combat":
        filtered_agents.sort(key=lambda a: a.skills.get("combat", 0), reverse=True)
    elif sort_by == "Medicine":
        filtered_agents.sort(key=lambda a: a.skills.get("medicine", 0), reverse=True)
    elif sort_by == "Social Score":
        filtered_agents.sort(key=lambda a: a.get_social_score(), reverse=True)

    st.dataframe([
        {
            "Name": a.get_full_name(),
            "Age": a.age,
            "Generation": a.generation,
            "Alive": a.alive,
            "Status": a.status,
            "Role": a.role,
            "Location": a.location,
            "Health": a.health,
            "Hunger": a.hunger,
            "Energy": a.energy,
            "Social": a.social,
            "Wealth": a.wealth,
            "Goal": a.life_goal,
            "Faction": a.faction,
            "Best Friend": a.get_best_friend(),
            "Rival": a.get_rival(),
            "Emotion": a.emotional_state,
            "Social Score": a.get_social_score(),
        }
        for a in filtered_agents
    ], use_container_width=True)

    if filtered_agents:
        selected = st.selectbox(
            "Inspect Agent",
            [
                f"{a.name} | Gen {a.generation} | {a.role}"
                for a in filtered_agents
            ]
        )

        selected_name = selected.split(" | ")[0]

        agent = next(a for a in sim.agents if a.name == selected_name)

        st.markdown("### Profile")
        st.write(f"**Name:** {agent.name}")
        st.write(f"**Full Name:** {agent.get_full_name()}")
        st.write(f"**Surname:** {agent.surname or 'None'}")
        family_rep = 0

        if agent.surname:
            family_rep = sim.family_reputation.get(agent.surname, 0)

        st.write(f"**Family Reputation:** {family_rep}")
        st.write(f"**Age:** {agent.age}")
        st.write(f"**Generation:** {agent.generation}")
        st.write(f"**Role:** {agent.role}")
        st.write(f"**Location:** {agent.location}")
        st.write(f"**Favorite Place:** {agent.get_favorite_place() or 'None'}")
        st.write(f"**Health:** {agent.health}")
        st.write(f"**Status:** {agent.status}")
        st.write(f"**Emotion:** {agent.emotional_state}")
        st.write(f"**Life Goal:** {agent.life_goal}")
        st.write(f"**Completed Goals:** {agent.completed_goals}")
        st.write(f"**Crush:** {agent.crush or 'None'}")
        children = [
            a.name for a in sim.agents
            if agent.name in getattr(a, "parents", [])
        ]

        siblings = [
            a.name for a in sim.agents
            if a.name != agent.name
            and hasattr(agent, "is_sibling_of")
            and agent.is_sibling_of(a)
        ]

        st.markdown("### Family Tree")
        st.write(f"**Partner:** {agent.partner or 'None'}")
        st.write(f"**Parents:** {agent.parents if agent.parents else 'None'}")
        st.write(f"**Children:** {children if children else 'None'}")
        st.write(f"**Siblings:** {siblings if siblings else 'None'}")
        st.write(f"**Faction:** {agent.faction}")
        st.write(f"**Best Friend:** {agent.get_best_friend() or 'None'}")
        st.write(f"**Rival:** {agent.get_rival() or 'None'}")
        st.write(f"**Social Score:** {agent.get_social_score()}")
        st.write(f"**Wealth:** {agent.wealth}")
        st.write(f"**Debts:** {agent.debts}")
        st.write(f"**Inventory:** {agent.inventory}")

        st.markdown("### Personality")
        st.json({
            "curiosity": agent.curiosity,
            "kindness": agent.kindness,
            "aggression": agent.aggression,
            "discipline": agent.discipline,
            "pride": agent.pride,
            "greed": agent.greed,
            "risk_taking": agent.risk_taking,
        })

        st.markdown("### Skills")
        st.json(agent.skills)

        st.markdown("### Recent Memories")
        st.write(agent.memories[-10:])

        st.markdown("### Journal")
        st.write(agent.journal[-10:])

        st.markdown("### Emotion Timeline")

        if agent.emotion_history:
            emotion_rows = []

            for index, emotion in enumerate(agent.emotion_history[-10:], start=1):
                emotion_rows.append({
                    "Step": index,
                    "Emotion": emotion
                })

            st.dataframe(emotion_rows, use_container_width=True)
        else:
            st.info("No emotion history yet.")

        st.markdown("### Social Summary")

        best_friend = agent.get_best_friend()
        rival = agent.get_rival()

        if best_friend:
            st.success(f"Best friend: {best_friend}")
        else:
            st.info("Best friend: None")

        if rival:
            st.warning(f"Rival: {rival}")
        else:
            st.info("Rival: None")

        st.markdown("### Grudges")

        if agent.grudges:
            st.json(agent.grudges)
        else:
            st.info("No grudges.")

        st.markdown("### Bonds")

        if agent.bonds:
            st.json(agent.bonds)
        else:
            st.info("No bonds.")
        
        st.markdown("### Gossip Memory")

        if agent.gossip_memory:
            st.write(agent.gossip_memory[-10:])
        else:
            st.info("No gossip memory.")

        relationship_count = len(agent.relationships)

        positive_relationships = 0
        negative_relationships = 0

        for rel in agent.relationships.values():
            score = (
                rel.get("trust", 0)
                + rel.get("friendship", 0)
                + rel.get("respect", 0)
                - rel.get("fear", 0)
            )

            if score > 0:
                positive_relationships += 1
            elif score < 0:
                negative_relationships += 1

        st.write(f"**Known Relationships:** {relationship_count}")
        st.write(f"**Positive Relationships:** {positive_relationships}")
        st.write(f"**Negative Relationships:** {negative_relationships}")

        st.markdown("### Relationships")

        relationship_rows = []

        for name, rel in agent.relationships.items():
            score = (
                rel.get("trust", 0)
                + rel.get("friendship", 0)
                + rel.get("respect", 0)
                - rel.get("fear", 0)
            )

            if score > 20:
                label = "Positive"
            elif score < -20:
                label = "Negative"
            else:
                label = "Neutral"

            relationship_rows.append({
                "Name": name,
                "Trust": rel.get("trust", 0),
                "Friendship": rel.get("friendship", 0),
                "Respect": rel.get("respect", 0),
                "Fear": rel.get("fear", 0),
                "Score": score,
                "Type": label,
            })

        if relationship_rows:
            st.dataframe(relationship_rows, use_container_width=True)
        else:
            st.info("No relationships yet.")

    else:
        st.warning("No agents match the current filters.")

# -----------------------------
# Settlements Tab
# -----------------------------

st.subheader("Population by Location")

location_counts = {}

for agent in sim.agents:
    if agent.alive:
        location_counts[agent.location] = location_counts.get(agent.location, 0) + 1

st.dataframe([
    {"Location": location, "Population": count}
    for location, count in location_counts.items()
], use_container_width=True)

with tab2:
    st.subheader("Main Settlement")

    st.json({
        "world": getattr(sim, "world_name", "Unknown"),
        "settlement": sim.settlement,
        "stage": getattr(sim, "settlement_stage", "Camp"),
        "leader": getattr(sim, "leader", None),
        "resources": sim.resources,
        "village_tension": sim.village_tension,
        "culture": sim.get_culture_identity(),
        "belief": sim.get_belief_identity(),
        "laws": sim.laws,
        "traditions": sim.traditions,
        "technologies": sim.technologies,
        "research_points": sim.research_points,
        "current_project": sim.current_project,
    })

    st.subheader("Other Settlements")
    st.json(sim.extra_settlements)

    st.subheader("Factions")
    st.json(sim.factions)

# -----------------------------
# History Tab
# -----------------------------

with tab3:
    st.subheader("World History")

    for event in sim.world_history[-80:]:
        st.write(event)

    st.subheader("Milestones")
    st.write(list(sim.milestones))

    st.subheader("Eras")
    st.json(sim.eras)

    st.subheader("Death Records")
    st.json(sim.death_records)

    st.subheader("Wars")
    st.json(sim.wars)

    st.subheader("Treaties")
    st.json(sim.treaties)

    st.subheader("Rebellions")
    st.json(sim.rebellions)

# -----------------------------
# Chronicles Tab
# -----------------------------

with tab4:
    st.subheader("Daily Chronicles")

    for chronicle in sim.chronicles[-30:]:
        st.write(chronicle)

# -----------------------------
# Controls Tab
# -----------------------------

st.subheader("Export Data")

if st.button("Export Agents CSV"):
    path = export_agents_csv(sim)
    st.success(f"Exported to {path}")

if st.button("Export Relationships CSV"):
    path = export_relationships_csv(sim)
    st.success(f"Exported to {path}")

agents_path = "exports/agents.csv"
relationships_path = "exports/relationships.csv"

if os.path.exists(agents_path):
    with open(agents_path, "rb") as file:
        st.download_button(
            label="Download Agents CSV",
            data=file,
            file_name="agents.csv",
            mime="text/csv"
        )

if os.path.exists(relationships_path):
    with open(relationships_path, "rb") as file:
        st.download_button(
            label="Download Relationships CSV",
            data=file,
            file_name="relationships.csv",
            mime="text/csv"
        )

with tab5:
    st.subheader("Temporary Controls")

    st.write("""
    This is the temporary observer dashboard.

    Use:
    - **Advance 1 Hour** for careful observation.
    - **Run 6 Hours** for short progress.
    - **Run 1 Day** to quickly grow the world.
    - **Save** to store the current world.
    - **Reset World** to start over.

    True real-time mode can be built later using a FastAPI backend + web dashboard.
    """)

with tab6:
    st.subheader("Simulation Errors")

    error_log = getattr(sim, "error_log", [])

    if error_log:
        for error in error_log[-50:]:
            st.error(error)
    else:
        st.success("No errors detected.")

with tab7:
    st.subheader("Notifications")

    if sim.notifications:
        for notification in reversed(sim.notifications[-50:]):
            st.info(notification)
    else:
        st.info("No notifications yet.")