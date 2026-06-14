import streamlit as st

from save_system import save_world
from story_generator import generate_family_summary


def render(sim):
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
        
        st.markdown("### Dynasty Summary")

        family_summary = generate_family_summary(sim, selected_family)

        st.text_area(
            "Generated Family Summary",
            family_summary,
            height=300
        )

        st.download_button(
            label="Download Family Summary",
            data=family_summary,
            file_name=f"family_summary_{selected_family}.txt",
            mime="text/plain",
            key=f"download_family_summary_{selected_family}"
        )

    else:
        st.info("No family lines have formed yet.")