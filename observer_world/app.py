import streamlit as st

from agent import Agent
from simulation import Simulation
from save_system import load_world, save_world, delete_save
from config import CONFIG
from export_data import export_agents_csv, export_relationships_csv

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

# -----------------------------
# Header
# -----------------------------

st.title("Observer World")

col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)

with col_a:
    if st.button("Advance 1 Hour"):
        logs = sim.tick()
        st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

with col_b:
    if st.button("Run 6 Hours"):
        for _ in range(6):
            logs = sim.tick()
            st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

with col_c:
    if st.button("Run 1 Day"):
        for _ in range(24):
            logs = sim.tick()
            st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

with col_d:
    if st.button("Run 7 Days"):
        for _ in range(24 * 7):
            logs = sim.tick()
            st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

with col_e:
    if st.button("Save"):
        save_world(sim)
        st.success("World saved.")

with col_f:
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

important_words = [
    "died", "born", "leader", "war", "rebellion", "murder",
    "technology", "milestone", "trial", "exiled", "treaty",
    "founded", "completed"
]

show_important_only = st.checkbox("Show important events only")

recent_logs = st.session_state.logs[-100:]

if show_important_only:
    recent_logs = [
        log for log in recent_logs
        if any(word in log.lower() for word in important_words)
    ]

for log in recent_logs[-30:]:
    st.write(log)

# -----------------------------
# Tabs
# -----------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Agents",
    "Settlements",
    "History",
    "Chronicles",
    "Controls"
])

# -----------------------------
# Agents Tab
# -----------------------------

with tab1:
    st.subheader("Agents")

    st.dataframe([
        {
            "Name": a.name,
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
        }
        for a in sim.agents
    ], use_container_width=True)

    selected_name = st.selectbox(
        "Inspect Agent",
        [a.name for a in sim.agents]
    )

    agent = next(a for a in sim.agents if a.name == selected_name)

    st.markdown("### Profile")
    st.write(f"**Name:** {agent.name}")
    st.write(f"**Age:** {agent.age}")
    st.write(f"**Generation:** {agent.generation}")
    st.write(f"**Role:** {agent.role}")
    st.write(f"**Location:** {agent.location}")
    st.write(f"**Health:** {agent.health}")
    st.write(f"**Status:** {agent.status}")
    st.write(f"**Life Goal:** {agent.life_goal}")
    st.write(f"**Completed Goals:** {agent.completed_goals}")
    st.write(f"**Partner:** {agent.partner}")
    st.write(f"**Family:** {agent.family}")
    st.write(f"**Parents:** {agent.parents}")
    st.write(f"**Faction:** {agent.faction}")
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

    st.markdown("### Relationships")
    st.json(agent.relationships)

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