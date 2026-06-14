import pandas as pd
import streamlit as st


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