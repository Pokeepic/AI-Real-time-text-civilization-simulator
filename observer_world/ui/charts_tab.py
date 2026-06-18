import pandas as pd
import streamlit as st
from collections import Counter


def render(sim):
    st.subheader("World Charts")

    snapshots = getattr(sim, "history_snapshots", [])

    if not snapshots:
        st.info("No history snapshots yet. Run the simulation for at least 1 day.")
        return

    df = pd.DataFrame(snapshots)

    st.subheader("Chart Summary")

    latest = snapshots[-1]

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    summary_col1.metric("Latest Population", latest.get("alive", 0))
    summary_col2.metric("Latest Dead", latest.get("dead", 0))
    summary_col3.metric("Latest Food", latest.get("food", 0))
    summary_col4.metric("Latest Tension", latest.get("tension", 0))

    st.divider()

    st.write("### Population")
    st.line_chart(df.set_index("day")[["alive", "dead"]])

    st.write("### Population Growth Rate")

    if "growth_rate" in df.columns:
        st.line_chart(df.set_index("day")["growth_rate"])
    else:
        st.info("No growth rate data yet.")
    
    st.write("### Growth Status")

    latest_growth = latest.get("growth_rate", 0)

    if latest_growth > 20:
        st.warning("Population is growing very quickly.")
    elif latest_growth < -10:
        st.error("Population is declining sharply.")
    else:
        st.success("Population growth looks stable.")

    st.write("### Resources")
    st.line_chart(df.set_index("day")[["food", "wood", "stone"]])

    st.write("### Material Storage")

    material_columns = []

    for column in ["wood", "stone"]:
        if column in df.columns:
            material_columns.append(column)

    if material_columns:
        st.line_chart(df.set_index("day")[material_columns])
    else:
        st.info("No material data yet.")

    st.write("### Food Per Person")

    if "food_per_person" in df.columns:
        st.line_chart(df.set_index("day")["food_per_person"])
    else:
        st.info("No food per person data yet.")

    st.write("### Food Balance Status")

    latest_food_per_person = latest.get("food_per_person", 0)

    if latest_food_per_person > 50:
        st.warning("Food storage is very high. Economy may still need balancing.")
    elif latest_food_per_person < 3:
        st.error("Food per person is dangerously low.")
    else:
        st.success("Food balance looks reasonable.")

    st.write("### Tension")
    st.line_chart(df.set_index("day")["tension"])

    st.write("### Progress")
    st.line_chart(df.set_index("day")[["wars", "technologies"]])

    st.write("### Life Events")

    life_event_columns = []

    for column in ["births_total", "deaths_total", "notifications_total"]:
        if column in df.columns:
            life_event_columns.append(column)

    if life_event_columns:
        st.line_chart(df.set_index("day")[life_event_columns])
    else:
        st.info("No life event data yet.")

    st.write("### Daily Births and Deaths")

    daily_life_columns = []

    for column in ["births_today", "deaths_today"]:
        if column in df.columns:
            daily_life_columns.append(column)

    if daily_life_columns:
        st.line_chart(df.set_index("day")[daily_life_columns])
    else:
        st.info("No daily birth/death data yet.")

    st.write("### Agent Condition")

    condition_columns = []

    for column in ["avg_health", "avg_hunger", "avg_energy"]:
        if column in df.columns:
            condition_columns.append(column)

    if condition_columns:
        st.line_chart(df.set_index("day")[condition_columns])
    else:
        st.info("No condition data yet.")
    
    st.write("### Resource Trend Status")

    if len(df) >= 2:
        previous = df.iloc[-2]

        food_change = latest.get("food", 0) - previous.get("food", 0)
        wood_change = latest.get("wood", 0) - previous.get("wood", 0)
        stone_change = latest.get("stone", 0) - previous.get("stone", 0)

        if food_change < 0:
            st.warning(f"Food decreased since last snapshot: {food_change}")
        else:
            st.success(f"Food increased or stayed stable: +{food_change}")

        if wood_change < 0:
            st.warning(f"Wood decreased since last snapshot: {wood_change}")
        else:
            st.success(f"Wood increased or stayed stable: +{wood_change}")

        if stone_change < 0:
            st.warning(f"Stone decreased since last snapshot: {stone_change}")
        else:
            st.success(f"Stone increased or stayed stable: +{stone_change}")
    else:
        st.info("Need at least 2 snapshots for trend status.")
    
    st.write("### Tension Trend Status")

    if len(df) >= 2:
        previous = df.iloc[-2]

        tension_change = latest.get("tension", 0) - previous.get("tension", 0)

        if tension_change > 10:
            st.error(f"Tension increased sharply: +{tension_change}")
        elif tension_change > 0:
            st.warning(f"Tension increased: +{tension_change}")
        elif tension_change < 0:
            st.success(f"Tension decreased: {tension_change}")
        else:
            st.info("Tension stayed the same.")
    else:
        st.info("Need at least 2 snapshots for tension trend.")

    st.subheader("Deaths by Cause")

    death_records = getattr(sim, "death_records", [])

    if not death_records:
        st.info("No deaths recorded yet.")
    else:
        death_causes = Counter(
            record.get("cause", "Unknown")
            for record in death_records
        )

        death_df = pd.DataFrame(
            death_causes.items(),
            columns=["Cause", "Deaths"]
        ).sort_values("Deaths", ascending=False)

        st.bar_chart(
            death_df,
            x="Cause",
            y="Deaths"
        )

        st.dataframe(
            death_df,
            use_container_width=True,
            hide_index=True
        )

        csv = death_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Deaths by Cause CSV",
            data=csv,
            file_name="deaths_by_cause.csv",
            mime="text/csv",
            key="download_deaths_by_cause_csv"
        )
    
    st.subheader("Civilization Balance Trends")

    snapshots = getattr(sim, "history_snapshots", [])

    if not snapshots:
        st.info("No history snapshots yet. Run the simulation for at least 1 day.")
    else:
        snapshot_df = pd.DataFrame(snapshots)

        if "day" in snapshot_df.columns:
            snapshot_df = snapshot_df.sort_values("day")

        # Population trend
        if "alive" in snapshot_df.columns:
            st.markdown("### Population Over Time")
            st.line_chart(
                snapshot_df,
                x="day",
                y="alive"
            )

        # Food per person trend
        if "food_per_person" in snapshot_df.columns:
            st.markdown("### Food Per Person")
            st.line_chart(
                snapshot_df,
                x="day",
                y="food_per_person"
            )

        # Health trend
        if "avg_health" in snapshot_df.columns:
            st.markdown("### Average Health")
            st.line_chart(
                snapshot_df,
                x="day",
                y="avg_health"
            )

        # Hunger and energy trend
        trend_cols = []

        if "avg_hunger" in snapshot_df.columns:
            trend_cols.append("avg_hunger")

        if "avg_energy" in snapshot_df.columns:
            trend_cols.append("avg_energy")

        if trend_cols:
            st.markdown("### Hunger and Energy")
            st.line_chart(
                snapshot_df,
                x="day",
                y=trend_cols
            )

        csv = snapshot_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Balance Trends CSV",
            data=csv,
            file_name="balance_trends.csv",
            mime="text/csv",
            key="download_balance_trends_csv"
        )
    
    st.subheader("Age Groups")

    alive_agents = [a for a in sim.agents if a.alive]

    if not alive_agents:
        st.info("No living agents to show age groups.")
    else:
        age_groups = {
            "Children 0-12": len([
                a for a in alive_agents
                if getattr(a, "age", 0) < 13
            ]),
            "Teenagers 13-17": len([
                a for a in alive_agents
                if 13 <= getattr(a, "age", 0) <= 17
            ]),
            "Adults 18-44": len([
                a for a in alive_agents
                if 18 <= getattr(a, "age", 0) <= 44
            ]),
            "Older Adults 45-59": len([
                a for a in alive_agents
                if 45 <= getattr(a, "age", 0) <= 59
            ]),
            "Elders 60-74": len([
                a for a in alive_agents
                if 60 <= getattr(a, "age", 0) <= 74
            ]),
            "Very Old 75+": len([
                a for a in alive_agents
                if getattr(a, "age", 0) >= 75
            ]),
        }

        age_df = pd.DataFrame(
            age_groups.items(),
            columns=["Age Group", "Agents"]
        )

        st.bar_chart(
            age_df,
            x="Age Group",
            y="Agents"
        )

        st.dataframe(
            age_df,
            use_container_width=True,
            hide_index=True
        )

        children = age_groups["Children 0-12"]
        child_ratio = children / max(1, len(alive_agents))

        st.markdown("### Age Balance Warning")

        if child_ratio > 0.55:
            st.warning(
                f"High child population: {child_ratio:.0%}. "
                "Birth rate may need to slow down or children need time to mature."
            )
        elif child_ratio < 0.25:
            st.info(
                f"Low child population: {child_ratio:.0%}. "
                "The civilization may have weak future growth."
            )
        else:
            st.success(
                f"Healthy child population: {child_ratio:.0%}."
            )

        csv = age_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Age Groups CSV",
            data=csv,
            file_name="age_groups.csv",
            mime="text/csv",
            key="download_age_groups_csv"
        )
    
    st.subheader("Births vs Deaths")

    snapshots = getattr(sim, "history_snapshots", [])

    if not snapshots:
        st.info("No birth/death history yet. Run the simulation for at least 1 day.")
    else:
        snapshot_df = pd.DataFrame(snapshots)

        if "day" in snapshot_df.columns:
            snapshot_df = snapshot_df.sort_values("day")

        daily_cols = []

        if "births_today" in snapshot_df.columns:
            daily_cols.append("births_today")

        if "deaths_today" in snapshot_df.columns:
            daily_cols.append("deaths_today")

        if daily_cols:
            st.markdown("### Daily Births and Deaths")
            st.line_chart(
                snapshot_df,
                x="day",
                y=daily_cols
            )
        else:
            st.info("Daily birth/death data is not available yet.")

        total_cols = []

        if "births_total" in snapshot_df.columns:
            total_cols.append("births_total")

        if "deaths_total" in snapshot_df.columns:
            total_cols.append("deaths_total")

        if total_cols:
            st.markdown("### Total Births and Deaths")
            st.line_chart(
                snapshot_df,
                x="day",
                y=total_cols
            )

        # Current balance summary
        total_births = snapshot_df["births_total"].iloc[-1] if "births_total" in snapshot_df.columns else 0
        total_deaths = snapshot_df["deaths_total"].iloc[-1] if "deaths_total" in snapshot_df.columns else len(getattr(sim, "death_records", []))

        st.markdown("### Birth / Death Balance")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Births", int(total_births))

        with col2:
            st.metric("Total Deaths", int(total_deaths))

        with col3:
            st.metric("Net Growth", int(total_births - total_deaths))

        if total_births > total_deaths * 4 and total_births > 50:
            st.warning("Births are much higher than deaths. Population may grow too fast.")
        elif total_deaths > total_births and total_deaths > 20:
            st.error("Deaths are higher than births. Civilization may be declining.")
        else:
            st.success("Birth and death balance looks stable.")
    
    st.subheader("Civilization Balance Summary")

    alive_agents = [a for a in sim.agents if a.alive]
    alive_count = len(alive_agents)

    food = sim.resources.get("food", 0)
    food_per_person = food / max(1, alive_count)

    death_count = len(getattr(sim, "death_records", []))

    children_count = len([
        a for a in alive_agents
        if getattr(a, "age", 0) < 13
    ])

    child_ratio = children_count / max(1, alive_count)

    if alive_agents:
        avg_health = sum(a.health for a in alive_agents) / alive_count
        avg_hunger = sum(a.hunger for a in alive_agents) / alive_count
        avg_energy = sum(a.energy for a in alive_agents) / alive_count
    else:
        avg_health = 0
        avg_hunger = 0
        avg_energy = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Alive Population", alive_count)

    with col2:
        st.metric("Food / Person", f"{food_per_person:.2f}")

    with col3:
        st.metric("Average Health", f"{avg_health:.1f}")

    with col4:
        st.metric("Deaths", death_count)

    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric("Average Hunger", f"{avg_hunger:.1f}")

    with col6:
        st.metric("Average Energy", f"{avg_energy:.1f}")

    with col7:
        st.metric("Children Ratio", f"{child_ratio:.0%}")

    st.markdown("### Balance Status")

    if alive_count <= 0:
        st.error("Civilization has no living population.")
    elif food_per_person < 2:
        st.error("Food is critically low. Famine risk is high.")
    elif food_per_person < 3:
        st.warning("Food is low. Population growth may slow down.")
    elif avg_health < 70:
        st.warning("Average health is low. Disease, injury, or harsh conditions may be too strong.")
    elif child_ratio > 0.60:
        st.warning("Too many children. Birth rate may be too high or children need more time to mature.")
    elif child_ratio < 0.20 and alive_count > 50:
        st.warning("Too few children. Long-term population growth may weaken.")
    elif avg_energy < 35:
        st.warning("Average energy is low. Agents may be overworked.")
    else:
        st.success("Civilization balance looks stable.")