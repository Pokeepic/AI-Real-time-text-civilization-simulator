import streamlit as st


def render(sim):
    st.header("Overview")

    alive_agents = [a for a in sim.agents if a.alive]

    snapshots = getattr(sim, "history_snapshots", [])

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Population", len(alive_agents))

    with col2:
        st.metric("Day", sim.day)

    with col3:
        st.metric("Hour", f"{sim.hour}:00")

    with col4:
        st.metric("World State", sim.world_state)
    
    with col5:
        st.metric("Snapshots", len(snapshots))

    st.subheader("Resources")

    resource_data = {
        "Food": sim.resources["food"],
        "Wood": sim.resources["wood"],
        "Stone": sim.resources["stone"],
    }

    st.table(resource_data)

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

    food_per_person = sim.resources.get("food", 0) / max(len(alive), 1)

    if food_per_person < 3:
        risks.append("Food per person is dangerously low")

    if sim.resources.get("wood", 0) < 10:
        risks.append("Wood storage is low")

    if sim.resources.get("stone", 0) < 10:
        risks.append("Stone storage is low")

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