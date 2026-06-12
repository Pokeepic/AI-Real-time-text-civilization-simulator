import streamlit as st
import os
import zipfile

from agent import Agent
from simulation import Simulation
from save_system import load_world, save_world, delete_save
from config import CONFIG
from export_data import export_agents_csv, export_relationships_csv
from stability import stabilize_sim
from archive import export_story_summary, export_chronicles

APP_VERSION = "Observer World Dashboard v0.8"

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

st.title("Observer World")
st.caption(APP_VERSION)

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
    confirm_reset = st.checkbox("Confirm Reset World")

    if st.button("Reset World"):
        if confirm_reset:
            delete_save()
            st.session_state.sim = create_new_world()
            st.session_state.logs = []
            st.success("World reset.")
            st.rerun()
        else:
            st.warning("Please tick 'Confirm Reset World' before resetting.")

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

tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "Overview",
    "Agents",
    "Settlements",
    "History",
    "Chronicles",
    "Controls",
    "Errors",
    "Notifications",
    "Watchlist",
    "Families",
    "Timeline",
    "Newspaper"
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
            if isinstance(notification, dict):
                st.info(
                    f"Day {notification.get('day')}, Hour {notification.get('hour')}:00 "
                    f"[{notification.get('category')}] {notification.get('message')}"
                )
            else:
                st.info(notification)
    else:
        st.info("No notifications yet.")

    st.subheader("Watchlist Events")

    watchlist_notifications = [
        n for n in getattr(sim, "notifications", [])
        if isinstance(n, dict)
        and n.get("category") == "Watchlist"
    ]

    if watchlist_notifications:
        for notification in reversed(watchlist_notifications[-5:]):
            st.info(
                f"Day {notification.get('day')}, Hour {notification.get('hour')}:00 "
                f"{notification.get('message')}"
            )
    else:
        st.info("No watchlist events yet.")

    st.subheader("Family Watchlist Events")

    family_notifications = [
        n for n in getattr(sim, "notifications", [])
        if isinstance(n, dict)
        and n.get("category") == "Family Watchlist"
    ]

    if family_notifications:
        for notification in reversed(family_notifications[-5:]):
            st.info(
                f"Day {notification['day']}, Hour {notification['hour']}:00 "
                f"{notification['message']}"
            )
    else:
        st.info("No family watchlist events yet.")
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
    st.write(f"**App Version:** {APP_VERSION}")
    st.subheader("Temporary Controls")

    st.write("""
    This is the temporary observer dashboard.

    Use:
    - **Advance 1 Hour** for careful observation.
    - **Run 6 Hours** for short progress.
    - **Run 1 Day** to quickly grow the world.
    - **Run 7 Days** to quickly simulate a longer period.
    - **Save** to store the current world.
    - **Reset World** to start over.

    True real-time mode can be built later using a FastAPI backend + web dashboard.
    """)

    st.divider()

    st.subheader("Export Files")
    if st.button("Export Everything"):
        export_story_summary(sim)
        export_chronicles(sim)
        export_agents_csv(sim)
        export_relationships_csv(sim)
        save_world(sim)

        st.success("Exported story summary, chronicles, agents CSV, relationships CSV, and saved world.")
    
    if st.button("Create Backup ZIP"):
        export_story_summary(sim)
        export_chronicles(sim)
        export_agents_csv(sim)
        export_relationships_csv(sim)
        save_world(sim)

        os.makedirs("exports", exist_ok=True)

        safe_version = APP_VERSION.replace(" ", "_").replace(".", "_")
        zip_path = f"exports/observer_world_backup_{safe_version}.zip"

        files_to_zip = [
            "logs/story_summary.txt",
            "logs/chronicles.txt",
            "logs/world_history.txt",
            "exports/agents.csv",
            "exports/relationships.csv",
            "saves/world_save.pkl",
        ]

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file_path in files_to_zip:
                if os.path.exists(file_path):
                    zipf.write(file_path)

        st.success("Backup ZIP created.")
    
    st.divider()

    st.subheader("Backup Info")

    backup_path = "exports/observer_world_backup.zip"

    if os.path.exists(backup_path):
        backup_size = os.path.getsize(backup_path) / 1024

        st.success("Backup ZIP exists.")
        st.write(f"**File:** {backup_path}")
        st.write(f"**Size:** {backup_size:.2f} KB")
    else:
        st.warning("No backup ZIP created yet.")

    if st.button("Export Story Summary"):
        path = export_story_summary(sim)
        st.success(f"Story summary exported to {path}")

    st.divider()

    st.subheader("Download Files")

    download_files = [
        {
            "label": "Download Story Summary",
            "path": "logs/story_summary.txt",
            "file_name": "story_summary.txt",
            "mime": "text/plain",
        },
        {
            "label": "Download Chronicles",
            "path": "logs/chronicles.txt",
            "file_name": "chronicles.txt",
            "mime": "text/plain",
        },
        {
            "label": "Download Full World History",
            "path": "logs/world_history.txt",
            "file_name": "world_history.txt",
            "mime": "text/plain",
        },
        {
            "label": "Download Agents CSV",
            "path": "exports/agents.csv",
            "file_name": "agents.csv",
            "mime": "text/csv",
        },
        {
            "label": "Download Relationships CSV",
            "path": "exports/relationships.csv",
            "file_name": "relationships.csv",
            "mime": "text/csv",
        },
        {
            "label": "Download Full Backup ZIP",
            "path": f"exports/observer_world_backup_{safe_version}.zip",
            "file_name": f"observer_world_backup_{safe_version}.zip",
            "mime": "application/zip",
        },
    ]

    for item in download_files:
        if os.path.exists(item["path"]):
            with open(item["path"], "rb") as file:
                st.download_button(
                    label=item["label"],
                    data=file,
                    file_name=item["file_name"],
                    mime=item["mime"]
                )
        else:
            st.caption(f"{item['file_name']} not created yet.")
    
    st.divider()

    st.subheader("Clean Up")

    cleanup_col1, cleanup_col2 = st.columns(2)

    with cleanup_col1:
        if st.button("Clear Dashboard Logs"):
            st.session_state.logs = []
            st.success("Dashboard logs cleared.")
            st.rerun()

    with cleanup_col2:
        if st.button("Clear Notifications"):
            sim.notifications = []
            save_world(sim)
            st.success("Notifications cleared.")
            st.rerun()
    
    st.divider()

    st.subheader("Delete Exported Files")
    confirm_delete_files = st.checkbox("Confirm Delete Exported Files")

    delete_col1, delete_col2 = st.columns(2)

    with delete_col1:
        if st.button("Delete Log Files"):
            if confirm_delete_files:
                log_files = [
                    "logs/story_summary.txt",
                    "logs/chronicles.txt",
                    "logs/world_history.txt",
                ]

                for file_path in log_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)

                st.success("Log files deleted.")
                st.rerun()
            else:
                st.warning("Please tick 'Confirm Delete Exported Files' first.")

    with delete_col2:
        if st.button("Delete Export Files"):
            if confirm_delete_files:
                export_files = [
                    "exports/agents.csv",
                    "exports/relationships.csv",
                    "exports/observer_world_backup.zip",
                ]

                for file_path in export_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)

                st.success("Export files deleted.")
                st.rerun()
            else:
                st.warning("Please tick 'Confirm Delete Exported Files' first.")

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

    notifications = getattr(sim, "notifications", [])

    category_filter = st.selectbox(
        "Filter by category",
        ["All"] + sorted(list(set(
            n.get("category", "General") if isinstance(n, dict) else "General"
            for n in notifications
        )))
    )

    filtered_notifications = notifications

    if category_filter != "All":
        filtered_notifications = [
            n for n in notifications
            if isinstance(n, dict) and n.get("category", "General") == category_filter
        ]

    if filtered_notifications:
        for notification in reversed(filtered_notifications[-50:]):
            if isinstance(notification, dict):
                st.info(
                    f"Day {notification.get('day')}, Hour {notification.get('hour')}:00 "
                    f"[{notification.get('category')}] {notification.get('message')}"
                )
            else:
                st.info(notification)
    else:
        st.info("No notifications yet.")

with tab8:
    st.subheader("Agent Watchlist")

    selected_watch = st.multiselect(
        "Choose agents to follow",
        sorted(a.name for a in sim.agents),
        default=sim.watchlist
    )

    sim.watchlist = selected_watch
    save_world(sim)

    st.write("Currently watching:")

    if sim.watchlist:
        st.write(sim.watchlist)
    else:
        st.info("No agents selected.")

with tab9:
    st.subheader("Family Watchlist")

    available_families = sorted(
        set(
            a.surname
            for a in sim.agents
            if getattr(a, "surname", None)
        )
    )

    selected_families = st.multiselect(
        "Choose families to follow",
        available_families,
        default=sim.family_watchlist
    )

    sim.family_watchlist = selected_families
    save_world(sim)

    if sim.family_watchlist:
        st.write("Watching:")
        st.write(sim.family_watchlist)
    else:
        st.info("No families selected.")

    st.divider()

    st.subheader("Family Tree Explorer")

    available_families = sorted(
        set(
            a.surname
            for a in sim.agents
            if getattr(a, "surname", None)
        )
    )

    if available_families:
        selected_family = st.selectbox(
            "Choose a family line",
            available_families
        )

        family_members = [
            a for a in sim.agents
            if getattr(a, "surname", None) == selected_family
        ]

        family_members = sorted(
            family_members,
            key=lambda a: (a.generation, a.age)
        )

        st.write(f"### {selected_family} Family")

        st.dataframe([
            {
                "Full Name": a.get_full_name(),
                "Generation": a.generation,
                "Age": a.age,
                "Alive": a.alive,
                "Role": a.role,
                "Partner": a.partner,
                "Parents": ", ".join(a.parents) if a.parents else "None",
                "Children": ", ".join([
                    child.name for child in sim.agents
                    if a.name in getattr(child, "parents", [])
                ]) or "None",
            }
            for a in family_members
        ], use_container_width=True)

    else:
        st.info("No family lines have formed yet.")

with tab10:
    st.subheader("World Timeline")

    timeline_sources = []

    for event in getattr(sim, "world_history", []):
        timeline_sources.append({
            "Source": "History",
            "Event": event
        })

    for chronicle in getattr(sim, "chronicles", []):
        timeline_sources.append({
            "Source": "Chronicle",
            "Event": chronicle
        })

    for notification in getattr(sim, "notifications", []):
        if isinstance(notification, dict):
            timeline_sources.append({
                "Source": notification.get("category", "Notification"),
                "Event": f"Day {notification.get('day')}, Hour {notification.get('hour')}:00 — {notification.get('message')}"
            })
        else:
            timeline_sources.append({
                "Source": "Notification",
                "Event": notification
            })

    source_options = sorted(set(item["Source"] for item in timeline_sources))

    selected_sources = st.multiselect(
        "Filter timeline sources",
        source_options,
        default=source_options
    )

    search_timeline = st.text_input("Search timeline")

    filtered_timeline = [
        item for item in timeline_sources
        if item["Source"] in selected_sources
    ]

    if search_timeline:
        filtered_timeline = [
            item for item in filtered_timeline
            if search_timeline.lower() in item["Event"].lower()
        ]

    if filtered_timeline:
        for item in filtered_timeline[-100:]:
            st.write(f"**[{item['Source']}]** {item['Event']}")
    else:
        st.info("No timeline events match your filters.")

with tab11:
    st.subheader("Observer World Newspaper")

    notifications = [
        n for n in getattr(sim, "notifications", [])
        if isinstance(n, dict)
    ]

    st.markdown(f"## The {getattr(sim, 'world_name', 'World')} Chronicle")
    st.caption(f"Day {sim.day}, Hour {sim.hour}:00")

    sections = {
        "Leadership": [],
        "Deaths": [],
        "Relationships": [],
        "War & Diplomacy": [],
        "Technology": [],
        "Other News": [],
    }

    for n in notifications[-50:]:
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

    for section_name, events in sections.items():
        st.markdown(f"### {section_name}")

        if events:
            for event in reversed(events[-5:]):
                st.write(f"📰 {event}")
        else:
            st.caption("No news in this section.")
    
    st.divider()

    st.markdown("### Greatest People of All Time")

    great_people = []

    for agent in sim.agents:
        score = 0

        score += agent.get_social_score()
        score += agent.wealth
        score += sum(agent.skills.values())

        if agent.role == "Leader":
            score += 50

        if agent.get_best_friend():
            score += 10

        if agent.partner:
            score += 10

        if agent.completed_goals:
            score += len(agent.completed_goals) * 15

        if not agent.alive:
            score += 10

        great_people.append({
            "Name": agent.get_full_name(),
            "Role": agent.role,
            "Alive": agent.alive,
            "Generation": agent.generation,
            "Score": score,
        })

    great_people = sorted(great_people, key=lambda x: x["Score"], reverse=True)[:10]

    st.dataframe(great_people, use_container_width=True)

    st.divider()

    st.markdown("### Memorial Hall")

    memorial_rows = []

    for record in getattr(sim, "death_records", []):
        memorial_rows.append({
            "Name": record.get("name"),
            "Day": record.get("day"),
            "Hour": record.get("hour"),
            "Role": record.get("role"),
            "Cause": record.get("cause"),
        })

    if memorial_rows:
        st.dataframe(memorial_rows, use_container_width=True)
    else:
        st.info("No deaths recorded yet.")
    
    st.divider()

    st.markdown("### Current World Story Summary")

    alive = [a for a in sim.agents if a.alive]
    dead = [a for a in sim.agents if not a.alive]

    leader_name = getattr(sim, "leader", None) or "no clear leader"
    settlement_name = sim.settlement.get("name") or "the first camp"

    story_summary = f"""
    In the world of **{getattr(sim, 'world_name', 'Unknown')}**, the settlement of **{settlement_name}**
    has reached the **{getattr(sim, 'settlement_stage', 'Camp')}** stage during the **{getattr(sim, 'current_era', 'Age of Survival')}**.

    There are currently **{len(alive)} living people** and **{len(dead)} recorded dead**.
    The current leader is **{leader_name}**.

    The society is culturally known as **{sim.get_culture_identity()}**, with belief tendencies toward **{sim.get_belief_identity()}**.

    So far, the world has recorded **{len(sim.wars)} wars**, **{len(sim.treaties)} treaties**, 
    **{len(sim.technologies)} technologies**, and **{len(sim.laws)} laws**.
    """

    st.info(story_summary)