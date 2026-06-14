import streamlit as st
from story_generator import generate_agent_biography, export_agent_biography


def render(sim):
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
        
        st.markdown("### Biography")

        bio = generate_agent_biography(agent)

        st.text_area(
            "Generated Biography",
            bio,
            height=300
        )
        if st.button("Export Biography"):
            path = export_agent_biography(agent)
            st.success(f"Biography exported to {path}")
        st.download_button(
            label="Download Biography",
            data=bio,
            file_name=f"biography_{agent.name}.txt",
            mime="text/plain",
            key=f"download_bio_{agent.name}"
        )

    else:
        st.warning("No agents match the current filters.")