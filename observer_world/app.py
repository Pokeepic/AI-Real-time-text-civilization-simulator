import streamlit as st
import os
import zipfile

from agent import Agent
from simulation import Simulation
from save_system import load_world, save_world, delete_save
from config import CONFIG
from export_data import export_agents_csv, export_relationships_csv
from stability import stabilize_sim
from name_generator import generate_unique_name, generate_founder_age

from ui.overview_tab import render as render_overview
from ui.agents_tab import render as render_agents
from ui.settlements_tab import render as render_settlements
from ui.history_tab import render as render_history
from ui.chronicles_tab import render as render_chronicles
from ui.controls_tab import render as render_controls
from ui.errors_tab import render as render_errors
from ui.notifications_tab import render as render_notifications
from ui.watchlist_tab import render as render_watchlist
from ui.families_tab import render as render_families
from ui.timeline_tab import render as render_timeline
from ui.newspaper_tab import render as render_newspaper
from ui.charts_tab import render as render_charts
from archive import export_story_summary, export_chronicles, export_history_snapshots, export_history_snapshots_csv

APP_VERSION = "Observer World Dashboard v0.8"
safe_version = APP_VERSION.replace(" ", "_").replace(".", "_")

st.set_page_config(page_title="Observer World", layout="wide")

# -----------------------------
# Create / Load World
# -----------------------------

def create_new_world():
    starting_population = CONFIG.get("starting_population", len(CONFIG["starting_names"]))

    existing_names = set()
    agents = []

    for _ in range(starting_population):
        name = generate_unique_name(existing_names)
        existing_names.add(name)

        agent = Agent(name)
        agent.age = generate_founder_age()

        agents.append(agent)
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

if not getattr(sim, "history_snapshots", []):
    from history_tracker import record_world_snapshot
    record_world_snapshot(sim)

st.title("Observer World")
st.caption(APP_VERSION)

with st.sidebar:
    st.header("Observer World")
    st.write(f"**Version:** {APP_VERSION}")
    st.write(f"**Day:** {sim.day}")
    st.write(f"**Hour:** {sim.hour}:00")
    st.write(f"**Population:** {len([a for a in sim.agents if a.alive])}")
    st.write(f"**World State:** {getattr(sim, 'world_state', 'Ongoing')}")

    st.divider()

    st.write("### Quick Tips")
    st.write("- Use **Overview** for the main dashboard.")
    st.write("- Use **Agents** to inspect people.")
    st.write("- Use **Notifications** for major events.")
    st.write("- Use **Timeline** for history.")
    st.write("- Use **Controls** for export/backup.")

    st.divider()

    st.write("### Quick Controls")

    if st.button("Sidebar: Advance 1 Hour"):
        logs = sim.tick()
        st.session_state.logs.extend(logs)
        save_world(sim)
        st.rerun()

    if st.button("Sidebar: Save World"):
        save_world(sim)
        st.success("World saved.")

    if st.button("Sidebar: Export Everything"):
        export_story_summary(sim)
        export_chronicles(sim)
        export_history_snapshots(sim)
        export_history_snapshots_csv(sim)
        export_agents_csv(sim)
        export_relationships_csv(sim)
        save_world(sim)
        st.success("Everything exported.")
    
    st.divider()

    st.write("### Watchlist Summary")

    watchlist = getattr(sim, "watchlist", [])
    family_watchlist = getattr(sim, "family_watchlist", [])

    if watchlist:
        st.write("**Agents:**")
        for name in watchlist:
            st.write(f"- {name}")
    else:
        st.caption("No watched agents.")

    if family_watchlist:
        st.write("**Families:**")
        for family in family_watchlist:
            st.write(f"- {family}")
    else:
        st.caption("No watched families.")
    
    st.divider()

    st.write("### Recent Notifications")

    notifications = getattr(sim, "notifications", [])

    if notifications:
        for notification in reversed(notifications[-5:]):
            if isinstance(notification, dict):
                st.caption(
                    f"Day {notification.get('day')}, Hour {notification.get('hour')}:00 "
                    f"[{notification.get('category')}] {notification.get('message')}"
                )
            else:
                st.caption(notification)
    else:
        st.caption("No notifications yet.")
    
    st.divider()

    st.write("### Risk Alerts")

    risk_alerts = []

    if sim.resources.get("food", 0) < 20:
        risk_alerts.append("Low food")

    if sim.village_tension >= 70:
        risk_alerts.append("High tension")

    if any(a.alive and a.health < 40 for a in sim.agents):
        risk_alerts.append("Critical health cases")

    if any(a.alive and a.hunger > 85 for a in sim.agents):
        risk_alerts.append("Starvation risk")

    if getattr(sim, "error_log", []):
        risk_alerts.append("Simulation errors detected")

    if risk_alerts:
        for alert in risk_alerts:
            st.warning(alert)
    else:
        st.success("No major risks.")
    
    st.divider()

    st.write("### World Identity")

    st.write(f"**World:** {getattr(sim, 'world_name', 'Unknown')}")
    st.write(f"**Settlement:** {sim.settlement.get('name') or 'None'}")
    st.write(f"**Stage:** {getattr(sim, 'settlement_stage', 'Camp')}")
    st.write(f"**Era:** {getattr(sim, 'current_era', 'Age of Survival')}")
    st.write(f"**Leader:** {getattr(sim, 'leader', None) or 'None'}")

    st.divider()

    st.write("### Major Family Lines")

    family_counts = {}

    for agent in sim.agents:
        surname = getattr(agent, "surname", None)

        if surname:
            family_counts[surname] = family_counts.get(surname, 0) + 1

    top_families = sorted(
        family_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )[:5]

    if top_families:
        for surname, count in top_families:
            st.write(f"**{surname}:** {count} members")
    else:
        st.caption("No family lines yet.")
    
    st.divider()

    st.write("### Notable Agents")

    alive_agents = [a for a in sim.agents if a.alive]

    if alive_agents:
        top_social = max(alive_agents, key=lambda a: a.get_social_score())
        top_wealth = max(alive_agents, key=lambda a: a.wealth)
        top_combat = max(alive_agents, key=lambda a: a.skills.get("combat", 0))

        st.write(f"**Most Social:** {top_social.get_full_name()} ({top_social.get_social_score()})")
        st.write(f"**Wealthiest:** {top_wealth.get_full_name()} ({top_wealth.wealth})")
        st.write(f"**Strongest:** {top_combat.get_full_name()} ({top_combat.skills.get('combat', 0)})")
    else:
        st.caption("No living agents.")
    
    st.divider()

    st.write("### System Counts")

    st.write(f"**Notifications:** {len(getattr(sim, 'notifications', []))}")
    st.write(f"**Chronicles:** {len(getattr(sim, 'chronicles', []))}")
    st.write(f"**Milestones:** {len(getattr(sim, 'milestones', []))}")
    st.write(f"**Wars:** {len(getattr(sim, 'wars', []))}")
    st.write(f"**Treaties:** {len(getattr(sim, 'treaties', []))}")
    st.write(f"**Errors:** {len(getattr(sim, 'error_log', []))}")

    st.divider()

    st.caption("Observer World is running in temporary Streamlit dashboard mode.")
    st.caption("True real-time mode will require a FastAPI backend later.")

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

tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
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
    "Newspaper",
    "Charts"
])

with tab0:
    render_overview(sim)
    

with tab1:
    render_agents(sim)

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
    render_settlements(sim)

with tab3:
    render_history(sim)

with tab4:
    render_chronicles(sim)

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
    render_controls(sim, APP_VERSION, safe_version)

with tab6:
    render_errors(sim)

with tab7:
    render_notifications(sim)

with tab8:
    render_watchlist(sim)

with tab9:
    render_families(sim)

with tab10:
    render_timeline(sim)

with tab11:
    render_newspaper(sim)

with tab12:
    render_charts(sim)