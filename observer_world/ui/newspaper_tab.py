import streamlit as st

from story_generator import (
    generate_world_story_summary,
    generate_weekly_newspaper,
    generate_fallen_heroes_summary,
    generate_family_rivalry_summary,
    generate_civilization_timeline_summary,
    generate_greatest_leader_biography,
)

def render(sim):
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

    st.divider()

    st.markdown("### Generated World Story Summary")

    world_summary = generate_world_story_summary(sim)

    st.text_area(
        "World Story Summary",
        world_summary,
        height=300
    )

    st.download_button(
        label="Download World Story Summary",
        data=world_summary,
        file_name=f"world_story_summary_{getattr(sim, 'world_name', 'world')}.txt",
        mime="text/plain",
        key="download_world_story_summary"
    )

    st.divider()

    st.markdown("### Weekly Newspaper Summary")

    weekly_news = generate_weekly_newspaper(sim)

    st.text_area(
        "Weekly Chronicle",
        weekly_news,
        height=350
    )

    st.download_button(
        label="Download Weekly Chronicle",
        data=weekly_news,
        file_name=f"weekly_chronicle_day_{sim.day}.txt",
        mime="text/plain",
        key="download_weekly_chronicle"
    )

    st.divider()

    st.markdown("### Fallen Heroes Summary")

    fallen_heroes = generate_fallen_heroes_summary(sim)

    st.text_area(
        "Fallen Heroes",
        fallen_heroes,
        height=250
    )

    st.download_button(
        label="Download Fallen Heroes Summary",
        data=fallen_heroes,
        file_name=f"fallen_heroes_day_{sim.day}.txt",
        mime="text/plain",
        key="download_fallen_heroes"
    )

    st.divider()

    st.markdown("### Family Rivalry Summary")

    rivalry_summary = generate_family_rivalry_summary(sim)

    st.text_area(
        "Family Rivalries",
        rivalry_summary,
        height=300
    )

    st.download_button(
        label="Download Family Rivalry Summary",
        data=rivalry_summary,
        file_name=f"family_rivalries_day_{sim.day}.txt",
        mime="text/plain",
        key="download_family_rivalries"
    )

    st.divider()

    st.markdown("### Civilization Timeline Summary")

    timeline_summary = generate_civilization_timeline_summary(sim)

    st.text_area(
        "Civilization Timeline",
        timeline_summary,
        height=300
    )

    st.download_button(
        label="Download Civilization Timeline",
        data=timeline_summary,
        file_name=f"civilization_timeline_day_{sim.day}.txt",
        mime="text/plain",
        key="download_civilization_timeline"
    )

    st.divider()

    st.markdown("### Greatest Leader Biography")

    leader_bio = generate_greatest_leader_biography(sim)

    st.text_area(
        "Greatest Leader",
        leader_bio,
        height=350
    )

    st.download_button(
        label="Download Greatest Leader Biography",
        data=leader_bio,
        file_name=f"greatest_leader_day_{sim.day}.txt",
        mime="text/plain",
        key="download_greatest_leader"
    )