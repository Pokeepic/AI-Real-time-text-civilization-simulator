import streamlit as st
import pandas as pd
from collections import Counter

from story_generator import (
    generate_world_story_summary,
    generate_weekly_newspaper,
    generate_fallen_heroes_summary,
    generate_family_rivalry_summary,
    generate_civilization_timeline_summary,
    generate_greatest_leader_biography,
    generate_most_influential_family_summary,
    generate_world_ending_report,
    generate_story_export_bundle,
)

def render(sim):
    st.subheader("Observer World Newspaper")

    news_tab1, news_tab2, news_tab3, news_tab4 = st.tabs([
        "News",
        "Reports",
        "Families",
        "Downloads"
    ])

    with news_tab1:

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


    with news_tab2:

        st.markdown("## Report Dashboard")

        alive_agents = [a for a in sim.agents if a.alive]
        alive_count = len(alive_agents)

        death_count = len(getattr(sim, "death_records", []))
        food = sim.resources.get("food", 0)
        food_per_person = food / max(1, alive_count)

        avg_health = (
            sum(a.health for a in alive_agents) / alive_count
            if alive_agents else 0
        )

        children_count = len([
            a for a in alive_agents
            if getattr(a, "age", 0) < 13
        ])

        child_ratio = children_count / max(1, alive_count)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Alive", alive_count)

        with col2:
            st.metric("Deaths", death_count)

        with col3:
            st.metric("Food / Person", f"{food_per_person:.2f}")

        with col4:
            st.metric("Avg Health", f"{avg_health:.1f}")

        col5, col6, col7 = st.columns(3)

        with col5:
            st.metric("Children", children_count)

        with col6:
            st.metric("Child Ratio", f"{child_ratio:.0%}")

        with col7:
            st.metric("World State", getattr(sim, "world_state", "Unknown"))

        if food_per_person < 2:
            st.error("Report warning: food is critically low.")
        elif avg_health < 70:
            st.warning("Report warning: average health is low.")
        elif child_ratio > 0.60:
            st.warning("Report warning: child population is very high.")
        else:
            st.success("Report dashboard: civilization looks stable.")

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

        st.divider()

        st.markdown("### World Ending Report")

        ending_report = generate_world_ending_report(sim)

        st.text_area(
            "World Ending Report",
            ending_report,
            height=350
        )

        st.download_button(
            label="Download World Ending Report",
            data=ending_report,
            file_name=f"world_ending_report_day_{sim.day}.txt",
            mime="text/plain",
            key="download_world_ending_report"
        )

        st.divider()

        st.subheader("Civilization Balance Report")

        alive_agents = [a for a in sim.agents if a.alive]
        alive_count = len(alive_agents)

        food = sim.resources.get("food", 0)
        food_per_person = food / max(1, alive_count)

        death_records = getattr(sim, "death_records", [])
        death_count = len(death_records)

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

        death_causes = Counter(
            record.get("cause", "Unknown")
            for record in death_records
        )

        top_death_cause = "None"

        if death_causes:
            top_death_cause = death_causes.most_common(1)[0][0]

        report = f"""
        Civilization Balance Report
        ===========================

        Day: {sim.day}
        Hour: {sim.hour}
        World State: {sim.world_state}

        Population
        ----------
        Alive Population: {alive_count}
        Deaths Recorded: {death_count}
        Children: {children_count}
        Children Ratio: {child_ratio:.0%}

        Resources
        ---------
        Food: {food}
        Food Per Person: {food_per_person:.2f}

        Health
        ------
        Average Health: {avg_health:.1f}
        Average Hunger: {avg_hunger:.1f}
        Average Energy: {avg_energy:.1f}

        Main Death Cause
        ----------------
        {top_death_cause}

        Balance Status
        --------------
        """

        if alive_count <= 0:
            report += "The civilization has collapsed. No living population remains."
        elif food_per_person < 2:
            report += "Food is critically low. Famine risk is high."
        elif avg_health < 70:
            report += "Average health is low. Disease, injury, or harsh conditions may be too strong."
        elif child_ratio > 0.60:
            report += "The population has too many children. Growth may be unstable."
        elif avg_energy < 35:
            report += "The population is overworked and low on energy."
        else:
            report += "The civilization appears stable. Population, food, and health are within a healthy range."

        st.text_area(
            "Balance Report",
            report,
            height=420
        )

        st.download_button(
            "Download Balance Report",
            data=report,
            file_name="civilization_balance_report.txt",
            mime="text/plain",
            key="download_civilization_balance_report"
        )

        st.divider()

        st.subheader("Violence Report")

        death_records = getattr(sim, "death_records", [])

        violent_deaths = []
        dangerous_agents = Counter()

        for record in death_records:
            cause = record.get("cause", "Unknown")
            victim = record.get("name", "Unknown")

            attacker = None
            violence_type = None

            if cause.startswith("fight with "):
                attacker = cause.replace("fight with ", "")
                violence_type = "Fight"

            elif cause.startswith("severe attack by "):
                attacker = cause.replace("severe attack by ", "")
                violence_type = "Severe Attack"

            elif cause.startswith("punishment"):
                attacker = "Law / Punishment"
                violence_type = "Punishment"

            if attacker:
                dangerous_agents[attacker] += 1

                violent_deaths.append({
                    "Victim": victim,
                    "Cause": cause,
                    "Attacker / Source": attacker,
                    "Type": violence_type
                })

        if not violent_deaths:
            st.info("No violence-related deaths recorded yet.")
        else:
            violent_df = pd.DataFrame(violent_deaths)

            st.metric("Violent Deaths", len(violent_deaths))

            st.markdown("### Most Dangerous Agents")

            dangerous_df = pd.DataFrame(
                dangerous_agents.items(),
                columns=["Agent", "Violent Deaths Caused"]
            ).sort_values("Violent Deaths Caused", ascending=False)

            st.dataframe(
                dangerous_df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Violence Death Records")

            st.dataframe(
                violent_df,
                use_container_width=True,
                hide_index=True
            )

            violence_report = "Violence Report\n"
            violence_report += "===============\n\n"
            violence_report += f"Total Violent Deaths: {len(violent_deaths)}\n\n"
            violence_report += "Most Dangerous Agents:\n"

            for agent_name, count in dangerous_agents.most_common():
                violence_report += f"- {agent_name}: {count} violent deaths caused\n"

            violence_report += "\nViolence Death Records:\n"

            for item in violent_deaths:
                violence_report += (
                    f"- {item['Victim']} died from {item['Cause']} "
                    f"({item['Type']})\n"
                )

            st.download_button(
                "Download Violence Report",
                data=violence_report,
                file_name="violence_report.txt",
                mime="text/plain",
                key="download_violence_report"
            )

        st.divider()

        st.subheader("Crime & Justice Report")

        crime_records = getattr(sim, "crime_records", {})
        laws = getattr(sim, "laws", [])

        crime_rows = []

        if isinstance(crime_records, dict):
            for criminal, crimes in crime_records.items():
                if isinstance(crimes, list):
                    for crime in crimes:
                        if isinstance(crime, dict):
                            crime_rows.append({
                                "Criminal": criminal,
                                "Crime": crime.get("crime", "Unknown"),
                                "Witness": crime.get("witness", "Unknown"),
                                "Day": crime.get("day", "Unknown")
                            })
                        else:
                            crime_rows.append({
                                "Criminal": criminal,
                                "Crime": str(crime),
                                "Witness": "Unknown",
                                "Day": "Unknown"
                            })
                else:
                    crime_rows.append({
                        "Criminal": criminal,
                        "Crime": str(crimes),
                        "Witness": "Unknown",
                        "Day": "Unknown"
                    })

        if not crime_rows:
            st.info("No crimes recorded yet.")
        else:
            crime_df = pd.DataFrame(crime_rows)

            st.metric("Recorded Crimes", len(crime_rows))

            crime_type_counts = Counter(
                row["Crime"] for row in crime_rows
            )

            criminal_counts = Counter(
                row["Criminal"] for row in crime_rows
            )

            st.markdown("### Most Common Crimes")

            crime_type_df = pd.DataFrame(
                crime_type_counts.items(),
                columns=["Crime", "Count"]
            ).sort_values("Count", ascending=False)

            st.dataframe(
                crime_type_df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Repeat Offenders")

            offender_df = pd.DataFrame(
                criminal_counts.items(),
                columns=["Agent", "Crimes"]
            ).sort_values("Crimes", ascending=False)

            st.dataframe(
                offender_df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Crime Records")

            st.dataframe(
                crime_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Current Laws")

        if not laws:
            st.info("No laws have been created yet.")
        else:
            for law in laws:
                st.write(f"- {law}")

        crime_report = "Crime & Justice Report\n"
        crime_report += "======================\n\n"
        crime_report += f"Recorded Crimes: {len(crime_rows)}\n"
        crime_report += f"Active Laws: {len(laws)}\n\n"

        if crime_rows:
            crime_report += "Repeat Offenders:\n"
            for agent_name, count in criminal_counts.most_common():
                crime_report += f"- {agent_name}: {count} crimes\n"

            crime_report += "\nMost Common Crimes:\n"
            for crime, count in crime_type_counts.most_common():
                crime_report += f"- {crime}: {count}\n"

        if laws:
            crime_report += "\nCurrent Laws:\n"
            for law in laws:
                crime_report += f"- {law}\n"

        st.download_button(
            "Download Crime & Justice Report",
            data=crime_report,
            file_name="crime_justice_report.txt",
            mime="text/plain",
            key="download_crime_justice_report"
        )

        st.divider()

        st.subheader("Health & Medicine Report")

        alive_agents = [a for a in sim.agents if a.alive]

        if not alive_agents:
            st.info("No living agents to report.")
        else:
            sick_agents = [
                a for a in alive_agents
                if getattr(a, "sick_days", 0) > 0
            ]

            injured_agents = [
                a for a in alive_agents
                if a.health < 80
            ]

            critical_agents = [
                a for a in alive_agents
                if a.health < 50
            ]

            medics = [
                a for a in alive_agents
                if getattr(a, "role", "") == "Medic"
                or a.skills.get("medicine", 0) >= 6
            ]

            avg_health = sum(a.health for a in alive_agents) / len(alive_agents)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Average Health", f"{avg_health:.1f}")

            with col2:
                st.metric("Sick Agents", len(sick_agents))

            with col3:
                st.metric("Injured Agents", len(injured_agents))

            with col4:
                st.metric("Medics", len(medics))

            st.markdown("### Health Status")

            if avg_health < 70:
                st.error("Health is dangerously low. The civilization may be suffering from disease, injury, or poor survival conditions.")
            elif len(critical_agents) > 0:
                st.warning(f"{len(critical_agents)} agents are critically injured or sick.")
            elif len(medics) == 0:
                st.warning("No medics are available. Sickness and injuries may become dangerous.")
            else:
                st.success("Health and medical support look stable.")

            health_rows = []

            for agent in alive_agents:
                health_rows.append({
                    "Name": agent.name,
                    "Age": getattr(agent, "age", 0),
                    "Role": getattr(agent, "role", "Unknown"),
                    "Health": agent.health,
                    "Hunger": agent.hunger,
                    "Energy": agent.energy,
                    "Sick Days": getattr(agent, "sick_days", 0),
                    "Medicine Skill": agent.skills.get("medicine", 0)
                })

            health_df = pd.DataFrame(health_rows).sort_values(
                ["Health", "Sick Days"],
                ascending=[True, False]
            )

            st.markdown("### Most Vulnerable Agents")

            st.dataframe(
                health_df.head(20),
                use_container_width=True,
                hide_index=True
            )

            health_report = "Health & Medicine Report\n"
            health_report += "========================\n\n"
            health_report += f"Alive Population: {len(alive_agents)}\n"
            health_report += f"Average Health: {avg_health:.1f}\n"
            health_report += f"Sick Agents: {len(sick_agents)}\n"
            health_report += f"Injured Agents: {len(injured_agents)}\n"
            health_report += f"Critical Agents: {len(critical_agents)}\n"
            health_report += f"Medics: {len(medics)}\n\n"

            health_report += "Most Vulnerable Agents:\n"

            for _, row in health_df.head(20).iterrows():
                health_report += (
                    f"- {row['Name']} | Age {row['Age']} | "
                    f"Health {row['Health']} | Hunger {row['Hunger']} | "
                    f"Energy {row['Energy']} | Sick Days {row['Sick Days']}\n"
                )

            st.download_button(
                "Download Health & Medicine Report",
                data=health_report,
                file_name="health_medicine_report.txt",
                mime="text/plain",
                key="download_health_medicine_report"
            )
            
        st.divider()

        st.subheader("Family & Dynasty Report")

        agents = getattr(sim, "agents", [])
        alive_agents = [a for a in agents if a.alive]

        def get_family_name(agent):
            surname = getattr(agent, "surname", None)

            if surname:
                return surname

            name_parts = agent.name.split()

            if len(name_parts) >= 2:
                return name_parts[-1]

            return "Unknown"

        family_rows = {}

        for agent in agents:
            family = get_family_name(agent)

            if family not in family_rows:
                family_rows[family] = {
                    "Family": family,
                    "Total Members": 0,
                    "Living Members": 0,
                    "Dead Members": 0,
                    "Children": 0,
                    "Adults": 0,
                    "Elders": 0,
                    "Average Health": 0,
                    "Members": []
                }

            row = family_rows[family]
            row["Total Members"] += 1
            row["Members"].append(agent)

            if agent.alive:
                row["Living Members"] += 1

                age = getattr(agent, "age", 0)

                if age < 13:
                    row["Children"] += 1
                elif age >= 60:
                    row["Elders"] += 1
                else:
                    row["Adults"] += 1
            else:
                row["Dead Members"] += 1

        for family, row in family_rows.items():
            living_members = [a for a in row["Members"] if a.alive]

            if living_members:
                row["Average Health"] = round(
                    sum(a.health for a in living_members) / len(living_members),
                    1
                )
            else:
                row["Average Health"] = 0

        family_data = []

        for family, row in family_rows.items():
            family_data.append({
                "Family": row["Family"],
                "Total Members": row["Total Members"],
                "Living Members": row["Living Members"],
                "Dead Members": row["Dead Members"],
                "Children": row["Children"],
                "Adults": row["Adults"],
                "Elders": row["Elders"],
                "Average Health": row["Average Health"]
            })

        if not family_data:
            st.info("No family data available yet.")
        else:
            family_df = pd.DataFrame(family_data).sort_values(
                "Living Members",
                ascending=False
            )

            st.markdown("### Major Families")

            st.dataframe(
                family_df.head(20),
                use_container_width=True,
                hide_index=True
            )

            largest_family = family_df.iloc[0]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Families", len(family_df))

            with col2:
                st.metric("Largest Family", largest_family["Family"])

            with col3:
                st.metric("Largest Family Size", int(largest_family["Living Members"]))

            st.markdown("### Family Balance Status")

            if largest_family["Living Members"] > max(10, len(alive_agents) * 0.35):
                st.warning(
                    f"The {largest_family['Family']} family is becoming very dominant."
                )
            elif len(family_df) < 3 and len(alive_agents) > 30:
                st.warning("Family diversity is low. The civilization may be dominated by too few bloodlines.")
            else:
                st.success("Family balance looks stable.")

            family_report = "Family & Dynasty Report\n"
            family_report += "=======================\n\n"
            family_report += f"Total Families: {len(family_df)}\n"
            family_report += f"Largest Family: {largest_family['Family']}\n"
            family_report += f"Largest Living Family Size: {int(largest_family['Living Members'])}\n\n"

            family_report += "Major Families:\n"

            for _, row in family_df.head(20).iterrows():
                family_report += (
                    f"- {row['Family']}: "
                    f"{int(row['Living Members'])} living, "
                    f"{int(row['Dead Members'])} dead, "
                    f"{int(row['Children'])} children, "
                    f"{int(row['Elders'])} elders, "
                    f"avg health {row['Average Health']}\n"
                )

            st.download_button(
                "Download Family & Dynasty Report",
                data=family_report,
                file_name="family_dynasty_report.txt",
                mime="text/plain",
                key="download_family_dynasty_report"
            )

        st.divider()

        st.subheader("Leadership & Faction Report")

        alive_agents = [a for a in sim.agents if a.alive]
        leader_name = getattr(sim, "leader", None)
        factions = getattr(sim, "factions", {})
        faction_conflicts = getattr(sim, "faction_conflicts", [])
        rebellions = getattr(sim, "rebellions", [])

        leader_agent = None

        if leader_name:
            leader_agent = next(
                (a for a in alive_agents if a.name == leader_name),
                None
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Leader", leader_name if leader_name else "None")

        with col2:
            st.metric("Factions", len(factions))

        with col3:
            st.metric("Faction Conflicts", len(faction_conflicts))

        with col4:
            st.metric("Rebellions", len(rebellions))

        st.markdown("### Leadership Status")

        if not leader_name:
            st.warning("The civilization has no leader. Political instability may rise.")
        elif leader_agent is None:
            st.warning("The recorded leader is missing or dead. Leadership may need to update.")
        else:
            st.success(f"{leader_name} is currently leading the civilization.")

            leader_info = {
                "Name": leader_agent.name,
                "Age": getattr(leader_agent, "age", 0),
                "Role": getattr(leader_agent, "role", "Unknown"),
                "Health": leader_agent.health,
                "Social Skill": leader_agent.skills.get("social", 0),
                "Combat Skill": leader_agent.skills.get("combat", 0),
                "Discipline": getattr(leader_agent, "discipline", 0),
                "Pride": getattr(leader_agent, "pride", 0),
                "Aggression": getattr(leader_agent, "aggression", 0),
            }

            st.dataframe(
                pd.DataFrame([leader_info]),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Factions")

        faction_rows = []

        if isinstance(factions, dict):
            for faction_name, faction_data in factions.items():
                if isinstance(faction_data, dict):
                    members = faction_data.get("members", [])
                    leader = faction_data.get("leader", "Unknown")
                    influence = faction_data.get("influence", 0)
                    ideology = faction_data.get("ideology", "Unknown")
                else:
                    members = []
                    leader = "Unknown"
                    influence = 0
                    ideology = str(faction_data)

                faction_rows.append({
                    "Faction": faction_name,
                    "Leader": leader,
                    "Members": len(members),
                    "Influence": influence,
                    "Ideology": ideology
                })

        if not faction_rows:
            st.info("No factions have formed yet.")
        else:
            faction_df = pd.DataFrame(faction_rows).sort_values(
                "Influence",
                ascending=False
            )

            st.dataframe(
                faction_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Political Risk")

        if len(rebellions) > 0:
            st.error("Rebellions have occurred. The civilization has serious political instability.")
        elif len(faction_conflicts) > 5:
            st.warning("Faction conflict is rising. The civilization may become unstable.")
        elif not leader_name and len(alive_agents) > 50:
            st.warning("A large civilization without a leader may become unstable.")
        else:
            st.success("Political stability looks acceptable.")

        leadership_report = "Leadership & Faction Report\n"
        leadership_report += "===========================\n\n"
        leadership_report += f"Leader: {leader_name if leader_name else 'None'}\n"
        leadership_report += f"Factions: {len(factions)}\n"
        leadership_report += f"Faction Conflicts: {len(faction_conflicts)}\n"
        leadership_report += f"Rebellions: {len(rebellions)}\n\n"

        if leader_agent:
            leadership_report += "Current Leader:\n"
            leadership_report += f"- Name: {leader_agent.name}\n"
            leadership_report += f"- Age: {getattr(leader_agent, 'age', 0)}\n"
            leadership_report += f"- Role: {getattr(leader_agent, 'role', 'Unknown')}\n"
            leadership_report += f"- Health: {leader_agent.health}\n"
            leadership_report += f"- Social Skill: {leader_agent.skills.get('social', 0)}\n"
            leadership_report += f"- Combat Skill: {leader_agent.skills.get('combat', 0)}\n\n"

        if faction_rows:
            leadership_report += "Factions:\n"

            for row in faction_rows:
                leadership_report += (
                    f"- {row['Faction']}: "
                    f"Leader {row['Leader']}, "
                    f"Members {row['Members']}, "
                    f"Influence {row['Influence']}, "
                    f"Ideology {row['Ideology']}\n"
                )

        st.download_button(
            "Download Leadership & Faction Report",
            data=leadership_report,
            file_name="leadership_faction_report.txt",
            mime="text/plain",
            key="download_leadership_faction_report"
        )

        st.divider()

        st.subheader("Settlement & Resources Report")

        resources = getattr(sim, "resources", {})
        settlement = getattr(sim, "settlement", {})
        extra_settlements = getattr(sim, "extra_settlements", [])
        buildings = settlement.get("buildings", [])

        alive_agents = [a for a in sim.agents if a.alive]
        alive_count = len(alive_agents)

        food = resources.get("food", 0)
        wood = resources.get("wood", 0)
        stone = resources.get("stone", 0)

        food_per_person = food / max(1, alive_count)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Food", food)

        with col2:
            st.metric("Wood", wood)

        with col3:
            st.metric("Stone", stone)

        with col4:
            st.metric("Food / Person", f"{food_per_person:.2f}")

        col5, col6, col7 = st.columns(3)

        with col5:
            st.metric("Settlement Stage", getattr(sim, "settlement_stage", "Unknown"))

        with col6:
            st.metric("Buildings", len(buildings))

        with col7:
            st.metric("Extra Settlements", len(extra_settlements))

        st.markdown("### Main Settlement")

        settlement_info = {
            "Name": settlement.get("name", "Unnamed Settlement"),
            "Stage": getattr(sim, "settlement_stage", "Camp"),
            "Shelter Progress": settlement.get("shelter_progress", 0),
            "Current Project": getattr(sim, "current_project", None) or "None",
            "Buildings": ", ".join(buildings) if buildings else "None"
        }

        st.dataframe(
            pd.DataFrame([settlement_info]),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Resource Status")

        if food_per_person < 2:
            st.error("Food is critically low. Famine risk is high.")
        elif food_per_person < 3:
            st.warning("Food is low. The civilization may struggle if growth continues.")
        elif food_per_person > 8:
            st.info("Food is abundant. Storage or spoilage may become important.")
        else:
            st.success("Food supply looks balanced.")

        if wood < 20 and stone < 20:
            st.warning("Building materials are low. Construction may slow down.")
        else:
            st.success("Material supply looks acceptable.")

        st.markdown("### Buildings")

        if not buildings:
            st.info("No buildings have been constructed yet.")
        else:
            building_df = pd.DataFrame(
                [{"Building": building} for building in buildings]
            )

            st.dataframe(
                building_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Extra Settlements")

        if not extra_settlements:
            st.info("No extra settlements have formed yet.")
        else:
            settlement_rows = []

            for s in extra_settlements:
                settlement_rows.append({
                    "Name": s.get("name", "Unknown"),
                    "Leader": s.get("leader", "Unknown"),
                    "Population": s.get("population", "Unknown"),
                    "Stage": s.get("stage", "Unknown"),
                    "Relations": s.get("relations", "Unknown"),
                })

            extra_settlement_df = pd.DataFrame(settlement_rows)

            st.dataframe(
                extra_settlement_df,
                use_container_width=True,
                hide_index=True
            )

        settlement_report = "Settlement & Resources Report\n"
        settlement_report += "=============================\n\n"
        settlement_report += f"Day: {sim.day}\n"
        settlement_report += f"Hour: {sim.hour}\n"
        settlement_report += f"Settlement Name: {settlement.get('name', 'Unnamed Settlement')}\n"
        settlement_report += f"Settlement Stage: {getattr(sim, 'settlement_stage', 'Camp')}\n"
        settlement_report += f"Current Project: {getattr(sim, 'current_project', None) or 'None'}\n\n"

        settlement_report += "Resources:\n"
        settlement_report += f"- Food: {food}\n"
        settlement_report += f"- Wood: {wood}\n"
        settlement_report += f"- Stone: {stone}\n"
        settlement_report += f"- Food Per Person: {food_per_person:.2f}\n\n"

        settlement_report += "Buildings:\n"

        if buildings:
            for building in buildings:
                settlement_report += f"- {building}\n"
        else:
            settlement_report += "- None\n"

        settlement_report += "\nExtra Settlements:\n"

        if extra_settlements:
            for s in extra_settlements:
                settlement_report += (
                    f"- {s.get('name', 'Unknown')} | "
                    f"Leader: {s.get('leader', 'Unknown')} | "
                    f"Population: {s.get('population', 'Unknown')} | "
                    f"Stage: {s.get('stage', 'Unknown')}\n"
                )
        else:
            settlement_report += "- None\n"

        st.download_button(
            "Download Settlement & Resources Report",
            data=settlement_report,
            file_name="settlement_resources_report.txt",
            mime="text/plain",
            key="download_settlement_resources_report"
        )

        st.divider()

        st.subheader("Culture & Technology Report")

        culture = getattr(sim, "culture", {})
        beliefs = getattr(sim, "beliefs", {})
        traditions = getattr(sim, "traditions", [])
        technologies = getattr(sim, "technologies", [])
        eras = getattr(sim, "eras", [])
        current_era = getattr(sim, "current_era", "Unknown")
        research_points = getattr(sim, "research_points", 0)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Current Era", current_era)

        with col2:
            st.metric("Technologies", len(technologies))

        with col3:
            st.metric("Traditions", len(traditions))

        with col4:
            st.metric("Research Points", research_points)

        st.markdown("### Culture Identity")

        culture_identity = sim.get_culture_identity() if hasattr(sim, "get_culture_identity") else "Unknown"
        belief_identity = sim.get_belief_identity() if hasattr(sim, "get_belief_identity") else "Unknown"

        st.write(f"**Culture:** {culture_identity}")
        st.write(f"**Belief Identity:** {belief_identity}")

        st.markdown("### Culture Values")

        if not culture:
            st.info("No culture data available yet.")
        else:
            culture_df = pd.DataFrame(
                culture.items(),
                columns=["Culture Trait", "Value"]
            ).sort_values("Value", ascending=False)

            st.bar_chart(
                culture_df,
                x="Culture Trait",
                y="Value"
            )

            st.dataframe(
                culture_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Beliefs")

        if not beliefs:
            st.info("No belief data available yet.")
        else:
            beliefs_df = pd.DataFrame(
                beliefs.items(),
                columns=["Belief", "Strength"]
            ).sort_values("Strength", ascending=False)

            st.bar_chart(
                beliefs_df,
                x="Belief",
                y="Strength"
            )

            st.dataframe(
                beliefs_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Technologies")

        if not technologies:
            st.info("No technologies have been unlocked yet.")
        else:
            tech_df = pd.DataFrame(
                [{"Technology": tech} for tech in technologies]
            )

            st.dataframe(
                tech_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Traditions")

        if not traditions:
            st.info("No traditions have formed yet.")
        else:
            tradition_rows = []

            for tradition in traditions:
                if isinstance(tradition, dict):
                    tradition_rows.append({
                        "Name": tradition.get("name", "Unknown"),
                        "Type": tradition.get("type", "Unknown"),
                        "Strength": tradition.get("strength", "Unknown"),
                        "Description": tradition.get("description", "")
                    })
                else:
                    tradition_rows.append({
                        "Name": str(tradition),
                        "Type": "Unknown",
                        "Strength": "Unknown",
                        "Description": ""
                    })

            tradition_df = pd.DataFrame(tradition_rows)

            st.dataframe(
                tradition_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Eras")

        if not eras:
            st.info("No era history available yet.")
        else:
            era_df = pd.DataFrame(eras)

            st.dataframe(
                era_df,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Cultural Stability")

        if culture:
            dominant_culture_value = max(culture.values()) if culture else 0

            if dominant_culture_value < 10:
                st.warning("Culture is still weak and undefined.")
            elif culture.get("violence", 0) > culture.get("cooperation", 0) + 20:
                st.warning("Violence is becoming a dominant cultural force.")
            elif culture.get("knowledge", 0) > 30:
                st.success("Knowledge culture is growing strongly.")
            elif culture.get("cooperation", 0) > 30:
                st.success("Cooperation culture is strong.")
            else:
                st.info("Culture is developing steadily.")
        else:
            st.info("Culture has not developed enough to evaluate.")

        culture_report = "Culture & Technology Report\n"
        culture_report += "===========================\n\n"
        culture_report += f"Day: {sim.day}\n"
        culture_report += f"Current Era: {current_era}\n"
        culture_report += f"Culture Identity: {culture_identity}\n"
        culture_report += f"Belief Identity: {belief_identity}\n"
        culture_report += f"Research Points: {research_points}\n\n"

        culture_report += "Culture Values:\n"
        if culture:
            for trait, value in sorted(culture.items(), key=lambda item: item[1], reverse=True):
                culture_report += f"- {trait}: {value}\n"
        else:
            culture_report += "- None\n"

        culture_report += "\nBeliefs:\n"
        if beliefs:
            for belief, strength in sorted(beliefs.items(), key=lambda item: item[1], reverse=True):
                culture_report += f"- {belief}: {strength}\n"
        else:
            culture_report += "- None\n"

        culture_report += "\nTechnologies:\n"
        if technologies:
            for tech in technologies:
                culture_report += f"- {tech}\n"
        else:
            culture_report += "- None\n"

        culture_report += "\nTraditions:\n"
        if traditions:
            for tradition in traditions:
                culture_report += f"- {tradition}\n"
        else:
            culture_report += "- None\n"

        culture_report += "\nEras:\n"
        if eras:
            for era in eras:
                culture_report += f"- {era}\n"
        else:
            culture_report += "- None\n"

        st.download_button(
            "Download Culture & Technology Report",
            data=culture_report,
            file_name="culture_technology_report.txt",
            mime="text/plain",
            key="download_culture_technology_report"
        )

        st.divider()

        st.subheader("Workforce & Roles Report")

        alive_agents = [a for a in sim.agents if a.alive]

        role_counts = Counter(
            getattr(a, "role", "Unknown")
            for a in alive_agents
        )

        workforce_rows = []

        for agent in alive_agents:
            workforce_rows.append({
                "Name": agent.name,
                "Age": getattr(agent, "age", 0),
                "Role": getattr(agent, "role", "Unknown"),
                "Health": agent.health,
                "Hunger": agent.hunger,
                "Energy": agent.energy,
                "Best Skill": max(agent.skills, key=agent.skills.get),
                "Best Skill Level": max(agent.skills.values()),
            })

        if not alive_agents:
            st.info("No living workforce available.")
        else:
            col1, col2, col3, col4 = st.columns(4)

            workers = [
                a for a in alive_agents
                if getattr(a, "age", 0) >= 13
            ]

            children = [
                a for a in alive_agents
                if getattr(a, "age", 0) < 13
            ]

            tired_workers = [
                a for a in workers
                if a.energy < 30
            ]

            with col1:
                st.metric("Living Population", len(alive_agents))

            with col2:
                st.metric("Workers 13+", len(workers))

            with col3:
                st.metric("Children", len(children))

            with col4:
                st.metric("Tired Workers", len(tired_workers))

            st.markdown("### Role Distribution")

            role_df = pd.DataFrame(
                role_counts.items(),
                columns=["Role", "Agents"]
            ).sort_values("Agents", ascending=False)

            st.bar_chart(
                role_df,
                x="Role",
                y="Agents"
            )

            st.dataframe(
                role_df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Workforce Table")

            workforce_df = pd.DataFrame(workforce_rows).sort_values(
                ["Role", "Energy"],
                ascending=[True, True]
            )

            st.dataframe(
                workforce_df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Workforce Balance")

            hunters = role_counts.get("Hunter", 0)
            farmers = role_counts.get("Farmer", 0)
            builders = role_counts.get("Builder", 0)
            medics = role_counts.get("Medic", 0)
            guards = role_counts.get("Guard", 0)

            if len(workers) == 0:
                st.error("There are no working-age people. The civilization cannot function.")
            elif len(children) > len(workers):
                st.warning("There are more children than workers. The adult workforce may be under pressure.")
            elif hunters + farmers < max(2, len(alive_agents) * 0.10):
                st.warning("Food-producing roles are low. Food supply may become risky.")
            elif medics == 0 and len(alive_agents) > 50:
                st.warning("No medics are available. Sickness and injury may become dangerous.")
            elif guards == 0 and len(alive_agents) > 80:
                st.warning("No guards are available. Violence may become harder to control.")
            else:
                st.success("Workforce balance looks stable.")

        workforce_report = "Workforce & Roles Report\n"
        workforce_report += "========================\n\n"
        workforce_report += f"Alive Population: {len(alive_agents)}\n"
        workforce_report += f"Workers Age 13+: {len([a for a in alive_agents if getattr(a, 'age', 0) >= 13])}\n"
        workforce_report += f"Children: {len([a for a in alive_agents if getattr(a, 'age', 0) < 13])}\n\n"

        workforce_report += "Role Distribution:\n"

        if role_counts:
            for role, count in role_counts.most_common():
                workforce_report += f"- {role}: {count}\n"
        else:
            workforce_report += "- None\n"

        workforce_report += "\nMost Tired Workers:\n"

        if workforce_rows:
            tired_df = pd.DataFrame(workforce_rows).sort_values("Energy", ascending=True)

            for _, row in tired_df.head(15).iterrows():
                workforce_report += (
                    f"- {row['Name']} | Role: {row['Role']} | "
                    f"Age: {row['Age']} | Health: {row['Health']} | "
                    f"Energy: {row['Energy']} | Best Skill: {row['Best Skill']} {row['Best Skill Level']}\n"
                )
        else:
            workforce_report += "- None\n"

        st.download_button(
            "Download Workforce & Roles Report",
            data=workforce_report,
            file_name="workforce_roles_report.txt",
            mime="text/plain",
            key="download_workforce_roles_report"
        )

        st.divider()

        st.subheader("Social & Relationships Report")

        alive_agents = [a for a in sim.agents if a.alive]

        social_rows = []
        relationship_count = 0
        partner_count = 0
        lonely_agents = []

        for agent in alive_agents:
            relationships = getattr(agent, "relationships", {})
            relationship_count += len(relationships)

            partner = getattr(agent, "partner", None)

            if partner:
                partner_count += 1

            try:
                best_friend = agent.get_best_friend()
            except Exception:
                best_friend = None

            try:
                social_score = agent.get_social_score()
            except Exception:
                social_score = len(relationships)

            if len(relationships) == 0 and not partner:
                lonely_agents.append(agent)

            social_rows.append({
                "Name": agent.name,
                "Age": getattr(agent, "age", 0),
                "Role": getattr(agent, "role", "Unknown"),
                "Partner": partner if partner else "None",
                "Best Friend": best_friend if best_friend else "None",
                "Relationships": len(relationships),
                "Social Score": social_score,
                "Kindness": getattr(agent, "kindness", 0),
                "Aggression": getattr(agent, "aggression", 0),
                "Pride": getattr(agent, "pride", 0),
            })

        if not alive_agents:
            st.info("No living agents available for social report.")
        else:
            avg_relationships = relationship_count / max(1, len(alive_agents))
            partnered_ratio = partner_count / max(1, len(alive_agents))

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Living Agents", len(alive_agents))

            with col2:
                st.metric("Total Relationships", relationship_count)

            with col3:
                st.metric("Avg Relationships", f"{avg_relationships:.1f}")

            with col4:
                st.metric("Partnered Agents", partner_count)

            st.markdown("### Most Social Agents")

            social_df = pd.DataFrame(social_rows)

            st.dataframe(
                social_df.sort_values("Social Score", ascending=False).head(20),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Isolated Agents")

            if lonely_agents:
                lonely_rows = []

                for agent in lonely_agents[:20]:
                    lonely_rows.append({
                        "Name": agent.name,
                        "Age": getattr(agent, "age", 0),
                        "Role": getattr(agent, "role", "Unknown"),
                        "Health": agent.health,
                        "Energy": agent.energy
                    })

                st.dataframe(
                    pd.DataFrame(lonely_rows),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("No completely isolated living agents found.")

            st.markdown("### Social Stability")

            if avg_relationships < 1 and len(alive_agents) > 30:
                st.warning("Average relationships are low. The civilization may feel socially disconnected.")
            elif partnered_ratio < 0.10 and len(alive_agents) > 50:
                st.warning("Few agents have partners. Family growth may slow down.")
            elif len(lonely_agents) > len(alive_agents) * 0.25:
                st.warning("Many agents are isolated. Social systems may need more interaction events.")
            else:
                st.success("Social stability looks healthy.")

        social_report = "Social & Relationships Report\n"
        social_report += "=============================\n\n"
        social_report += f"Alive Population: {len(alive_agents)}\n"
        social_report += f"Total Relationships: {relationship_count}\n"
        social_report += f"Partnered Agents: {partner_count}\n"
        social_report += f"Lonely Agents: {len(lonely_agents)}\n\n"

        social_report += "Most Social Agents:\n"

        if social_rows:
            social_df_for_report = pd.DataFrame(social_rows).sort_values(
                "Social Score",
                ascending=False
            )

            for _, row in social_df_for_report.head(20).iterrows():
                social_report += (
                    f"- {row['Name']} | Role: {row['Role']} | "
                    f"Relationships: {row['Relationships']} | "
                    f"Social Score: {row['Social Score']} | "
                    f"Partner: {row['Partner']} | Best Friend: {row['Best Friend']}\n"
                )
        else:
            social_report += "- None\n"

        social_report += "\nIsolated Agents:\n"

        if lonely_agents:
            for agent in lonely_agents[:20]:
                social_report += f"- {agent.name} | Age {getattr(agent, 'age', 0)} | Role {getattr(agent, 'role', 'Unknown')}\n"
        else:
            social_report += "- None\n"

        st.download_button(
            "Download Social & Relationships Report",
            data=social_report,
            file_name="social_relationships_report.txt",
            mime="text/plain",
            key="download_social_relationships_report"
        )

        st.divider()

        st.subheader("Life Goals & Memories Report")

        alive_agents = [a for a in sim.agents if a.alive]

        goal_rows = []
        completed_goal_rows = []
        memory_rows = []

        for agent in alive_agents:
            life_goal = getattr(agent, "life_goal", None)
            completed_goals = getattr(agent, "completed_goals", [])
            memories = getattr(agent, "memories", [])

            goal_rows.append({
                "Name": agent.name,
                "Age": getattr(agent, "age", 0),
                "Role": getattr(agent, "role", "Unknown"),
                "Life Goal": life_goal if life_goal else "None",
                "Completed Goals": len(completed_goals),
                "Memories": len(memories),
                "Health": agent.health,
                "Energy": agent.energy,
            })

            for goal in completed_goals:
                completed_goal_rows.append({
                    "Name": agent.name,
                    "Completed Goal": goal
                })

            for memory in memories[-5:]:
                memory_rows.append({
                    "Name": agent.name,
                    "Memory": memory
                })

        if not alive_agents:
            st.info("No living agents available for life goals report.")
        else:
            agents_with_goals = len([
                row for row in goal_rows
                if row["Life Goal"] != "None"
            ])

            total_completed_goals = sum(
                row["Completed Goals"]
                for row in goal_rows
            )

            total_memories = sum(
                row["Memories"]
                for row in goal_rows
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Living Agents", len(alive_agents))

            with col2:
                st.metric("Agents With Goals", agents_with_goals)

            with col3:
                st.metric("Completed Goals", total_completed_goals)

            with col4:
                st.metric("Memories", total_memories)

            st.markdown("### Active Life Goals")

            goal_df = pd.DataFrame(goal_rows).sort_values(
                ["Completed Goals", "Memories"],
                ascending=[False, False]
            )

            st.dataframe(
                goal_df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Completed Goals")

            if completed_goal_rows:
                completed_goal_df = pd.DataFrame(completed_goal_rows)

                st.dataframe(
                    completed_goal_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No completed goals yet.")

            st.markdown("### Recent Memories")

            if memory_rows:
                memory_df = pd.DataFrame(memory_rows)

                st.dataframe(
                    memory_df.tail(50),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No memories recorded yet.")

            st.markdown("### Story Depth Status")

            if agents_with_goals < len(alive_agents) * 0.50:
                st.warning("Many agents do not have life goals yet. The world may need stronger personal ambition systems.")
            elif total_memories < len(alive_agents):
                st.warning("Memory count is low. Agents may need more memorable life events.")
            elif total_completed_goals == 0 and sim.day > 20:
                st.info("No goals have been completed yet. Long-term personal stories are still developing.")
            else:
                st.success("Life goals and memories are giving agents stronger personal stories.")

        life_goal_report = "Life Goals & Memories Report\n"
        life_goal_report += "============================\n\n"
        life_goal_report += f"Alive Population: {len(alive_agents)}\n"
        life_goal_report += f"Agents With Goals: {agents_with_goals if alive_agents else 0}\n"
        life_goal_report += f"Completed Goals: {total_completed_goals if alive_agents else 0}\n"
        life_goal_report += f"Total Memories: {total_memories if alive_agents else 0}\n\n"

        life_goal_report += "Active Life Goals:\n"

        if goal_rows:
            for row in goal_rows[:30]:
                life_goal_report += (
                    f"- {row['Name']} | Role: {row['Role']} | "
                    f"Goal: {row['Life Goal']} | "
                    f"Completed: {row['Completed Goals']} | "
                    f"Memories: {row['Memories']}\n"
                )
        else:
            life_goal_report += "- None\n"

        life_goal_report += "\nCompleted Goals:\n"

        if completed_goal_rows:
            for row in completed_goal_rows[:50]:
                life_goal_report += f"- {row['Name']}: {row['Completed Goal']}\n"
        else:
            life_goal_report += "- None\n"

        life_goal_report += "\nRecent Memories:\n"

        if memory_rows:
            for row in memory_rows[-50:]:
                life_goal_report += f"- {row['Name']}: {row['Memory']}\n"
        else:
            life_goal_report += "- None\n"

        st.download_button(
            "Download Life Goals & Memories Report",
            data=life_goal_report,
            file_name="life_goals_memories_report.txt",
            mime="text/plain",
            key="download_life_goals_memories_report"
        )

        st.divider()

        st.subheader("Personality & Emotion Report")

        alive_agents = [a for a in sim.agents if a.alive]

        personality_rows = []
        emotion_counts = Counter()

        def get_agent_emotion(agent):
            return (
                getattr(agent, "emotional_state", None)
                or getattr(agent, "emotion", None)
                or getattr(agent, "current_emotion", None)
                or "Neutral"
            )

        for agent in alive_agents:
            emotion = get_agent_emotion(agent)
            emotion_counts[emotion] += 1

            personality_rows.append({
                "Name": agent.name,
                "Age": getattr(agent, "age", 0),
                "Role": getattr(agent, "role", "Unknown"),
                "Emotion": emotion,
                "Curiosity": getattr(agent, "curiosity", 0),
                "Kindness": getattr(agent, "kindness", 0),
                "Aggression": getattr(agent, "aggression", 0),
                "Discipline": getattr(agent, "discipline", 0),
                "Pride": getattr(agent, "pride", 0),
                "Health": agent.health,
                "Energy": agent.energy,
            })

        if not alive_agents:
            st.info("No living agents available for personality report.")
        else:
            avg_curiosity = sum(getattr(a, "curiosity", 0) for a in alive_agents) / len(alive_agents)
            avg_kindness = sum(getattr(a, "kindness", 0) for a in alive_agents) / len(alive_agents)
            avg_aggression = sum(getattr(a, "aggression", 0) for a in alive_agents) / len(alive_agents)
            avg_discipline = sum(getattr(a, "discipline", 0) for a in alive_agents) / len(alive_agents)
            avg_pride = sum(getattr(a, "pride", 0) for a in alive_agents) / len(alive_agents)

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Curiosity", f"{avg_curiosity:.1f}")

            with col2:
                st.metric("Kindness", f"{avg_kindness:.1f}")

            with col3:
                st.metric("Aggression", f"{avg_aggression:.1f}")

            with col4:
                st.metric("Discipline", f"{avg_discipline:.1f}")

            with col5:
                st.metric("Pride", f"{avg_pride:.1f}")

            st.markdown("### Emotion Distribution")

            emotion_df = pd.DataFrame(
                emotion_counts.items(),
                columns=["Emotion", "Agents"]
            ).sort_values("Agents", ascending=False)

            st.bar_chart(
                emotion_df,
                x="Emotion",
                y="Agents"
            )

            st.dataframe(
                emotion_df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Personality Table")

            personality_df = pd.DataFrame(personality_rows).sort_values(
                ["Aggression", "Pride"],
                ascending=[False, False]
            )

            st.dataframe(
                personality_df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Personality Risk")

            aggressive_agents = [
                a for a in alive_agents
                if getattr(a, "aggression", 0) >= 75
            ]

            kind_agents = [
                a for a in alive_agents
                if getattr(a, "kindness", 0) >= 75
            ]

            disciplined_agents = [
                a for a in alive_agents
                if getattr(a, "discipline", 0) >= 75
            ]

            if avg_aggression > avg_kindness + 15:
                st.warning("Aggression is higher than kindness. Violence risk may increase.")
            elif len(aggressive_agents) > len(alive_agents) * 0.25:
                st.warning("Many agents are highly aggressive. Fights and severe attacks may become common.")
            elif avg_discipline < 35 and len(alive_agents) > 50:
                st.warning("Discipline is low. Crime, laziness, or disorder may rise.")
            elif len(kind_agents) > len(aggressive_agents):
                st.success("Kindness is stronger than aggression. Social stability looks healthy.")
            else:
                st.info("Personality balance looks neutral.")

        personality_report = "Personality & Emotion Report\n"
        personality_report += "============================\n\n"
        personality_report += f"Alive Population: {len(alive_agents)}\n\n"

        if alive_agents:
            personality_report += "Average Personality Traits:\n"
            personality_report += f"- Curiosity: {avg_curiosity:.1f}\n"
            personality_report += f"- Kindness: {avg_kindness:.1f}\n"
            personality_report += f"- Aggression: {avg_aggression:.1f}\n"
            personality_report += f"- Discipline: {avg_discipline:.1f}\n"
            personality_report += f"- Pride: {avg_pride:.1f}\n\n"

            personality_report += "Emotion Distribution:\n"
            for emotion, count in emotion_counts.most_common():
                personality_report += f"- {emotion}: {count}\n"

            personality_report += "\nMost Aggressive Agents:\n"

            aggressive_df = pd.DataFrame(personality_rows).sort_values(
                "Aggression",
                ascending=False
            )

            for _, row in aggressive_df.head(15).iterrows():
                personality_report += (
                    f"- {row['Name']} | Role: {row['Role']} | "
                    f"Emotion: {row['Emotion']} | "
                    f"Aggression: {row['Aggression']} | "
                    f"Kindness: {row['Kindness']} | "
                    f"Discipline: {row['Discipline']}\n"
                )
        else:
            personality_report += "No living agents available.\n"

        st.download_button(
            "Download Personality & Emotion Report",
            data=personality_report,
            file_name="personality_emotion_report.txt",
            mime="text/plain",
            key="download_personality_emotion_report"
        )

        st.divider()

        st.subheader("World Risk & Alerts Report")

        alive_agents = [a for a in sim.agents if a.alive]
        alive_count = len(alive_agents)

        food = sim.resources.get("food", 0)
        food_per_person = food / max(1, alive_count)

        death_records = getattr(sim, "death_records", [])
        death_count = len(death_records)

        children_count = len([
            a for a in alive_agents
            if getattr(a, "age", 0) < 13
        ])

        workers_count = len([
            a for a in alive_agents
            if getattr(a, "age", 0) >= 13
        ])

        child_ratio = children_count / max(1, alive_count)

        avg_health = (
            sum(a.health for a in alive_agents) / alive_count
            if alive_agents else 0
        )

        avg_energy = (
            sum(a.energy for a in alive_agents) / alive_count
            if alive_agents else 0
        )

        critical_energy = len([
            a for a in alive_agents
            if a.energy <= 15
        ])

        critical_health = len([
            a for a in alive_agents
            if a.health <= 50
        ])

        death_causes = Counter(
            record.get("cause", "Unknown")
            for record in death_records
        )

        violent_deaths = sum(
            count for cause, count in death_causes.items()
            if cause.startswith("fight with ")
            or cause.startswith("severe attack by ")
            or cause.startswith("punishment")
        )

        leader_name = getattr(sim, "leader", None)
        factions = getattr(sim, "factions", {})
        rebellions = getattr(sim, "rebellions", [])

        risk_rows = []

        def add_risk(level, category, message):
            risk_rows.append({
                "Level": level,
                "Category": category,
                "Message": message
            })

        # Food risk
        if food_per_person < 2:
            add_risk("High", "Food", "Food is critically low. Famine risk is high.")
        elif food_per_person < 3:
            add_risk("Medium", "Food", "Food is low. Population growth may slow.")

        # Health risk
        if avg_health < 70:
            add_risk("High", "Health", "Average health is dangerously low.")
        elif avg_health < 85:
            add_risk("Medium", "Health", "Average health is weakening.")

        if critical_health > 0:
            add_risk("Medium", "Health", f"{critical_health} agents are critically injured or sick.")

        # Energy risk
        if avg_energy < 35:
            add_risk("Medium", "Energy", "Average energy is low. Agents may be overworked.")

        if critical_energy > alive_count * 0.25:
            add_risk("Medium", "Energy", "Many agents are critically tired.")

        # Age balance risk
        if child_ratio > 0.60:
            add_risk("Medium", "Population", "Too many children. Workforce may be under pressure.")
        elif child_ratio < 0.20 and alive_count > 50:
            add_risk("Medium", "Population", "Too few children. Future growth may weaken.")

        if children_count > workers_count:
            add_risk("Medium", "Workforce", "Children outnumber working-age agents.")

        # Violence risk
        if death_count > 0:
            violence_ratio = violent_deaths / max(1, death_count)

            if violence_ratio > 0.50 and violent_deaths >= 10:
                add_risk("High", "Violence", "Violence is the dominant cause of death.")
            elif violent_deaths >= 5:
                add_risk("Medium", "Violence", "Violent deaths are becoming noticeable.")

        # Political risk
        if not leader_name and alive_count > 50:
            add_risk("Medium", "Leadership", "Large civilization has no leader.")

        if len(rebellions) > 0:
            add_risk("High", "Politics", "Rebellions have occurred.")

        if len(factions) > 5:
            add_risk("Medium", "Politics", "Many factions exist. Political tension may rise.")

        # Default stable message
        if not risk_rows:
            add_risk("Low", "Overall", "No major risks detected. Civilization looks stable.")

        risk_df = pd.DataFrame(risk_rows)

        st.dataframe(
            risk_df,
            use_container_width=True,
            hide_index=True
        )

        high_risks = len([r for r in risk_rows if r["Level"] == "High"])
        medium_risks = len([r for r in risk_rows if r["Level"] == "Medium"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("High Risks", high_risks)

        with col2:
            st.metric("Medium Risks", medium_risks)

        with col3:
            st.metric("Total Alerts", len(risk_rows))

        if high_risks > 0:
            st.error("Civilization has serious risks that need attention.")
        elif medium_risks > 0:
            st.warning("Civilization is stable, but some risks are developing.")
        else:
            st.success("Civilization risk level is low.")

        risk_report = "World Risk & Alerts Report\n"
        risk_report += "==========================\n\n"
        risk_report += f"Day: {sim.day}\n"
        risk_report += f"Alive Population: {alive_count}\n"
        risk_report += f"Food Per Person: {food_per_person:.2f}\n"
        risk_report += f"Average Health: {avg_health:.1f}\n"
        risk_report += f"Average Energy: {avg_energy:.1f}\n"
        risk_report += f"Children Ratio: {child_ratio:.0%}\n"
        risk_report += f"Deaths Recorded: {death_count}\n"
        risk_report += f"Violent Deaths: {violent_deaths}\n\n"

        risk_report += "Risk Alerts:\n"

        for row in risk_rows:
            risk_report += f"- [{row['Level']}] {row['Category']}: {row['Message']}\n"

        st.download_button(
            "Download World Risk Report",
            data=risk_report,
            file_name="world_risk_alerts_report.txt",
            mime="text/plain",
            key="download_world_risk_alerts_report"
        )

        st.divider()

        st.subheader("All Reports Bundle")

        all_reports = "OBSERVER WORLD REPORTS BUNDLE\n"
        all_reports += "=============================\n\n"
        all_reports += f"World: {getattr(sim, 'world_name', 'Unknown')}\n"
        all_reports += f"Day: {sim.day}\n"
        all_reports += f"Hour: {sim.hour}\n"
        all_reports += f"World State: {getattr(sim, 'world_state', 'Unknown')}\n\n"

        try:
            all_reports += "\n\n--- WORLD STORY SUMMARY ---\n\n"
            all_reports += world_summary
        except NameError:
            pass

        try:
            all_reports += "\n\n--- WEEKLY NEWSPAPER ---\n\n"
            all_reports += weekly_news
        except NameError:
            pass

        try:
            all_reports += "\n\n--- FALLEN HEROES ---\n\n"
            all_reports += fallen_heroes
        except NameError:
            pass

        try:
            all_reports += "\n\n--- CIVILIZATION TIMELINE ---\n\n"
            all_reports += timeline_summary
        except NameError:
            pass

        try:
            all_reports += "\n\n--- GREATEST LEADER ---\n\n"
            all_reports += leader_bio
        except NameError:
            pass

        try:
            all_reports += "\n\n--- WORLD ENDING REPORT ---\n\n"
            all_reports += ending_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- CIVILIZATION BALANCE REPORT ---\n\n"
            all_reports += report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- VIOLENCE REPORT ---\n\n"
            all_reports += violence_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- CRIME & JUSTICE REPORT ---\n\n"
            all_reports += crime_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- HEALTH & MEDICINE REPORT ---\n\n"
            all_reports += health_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- FAMILY & DYNASTY REPORT ---\n\n"
            all_reports += family_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- LEADERSHIP & FACTION REPORT ---\n\n"
            all_reports += leadership_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- SETTLEMENT & RESOURCES REPORT ---\n\n"
            all_reports += settlement_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- CULTURE & TECHNOLOGY REPORT ---\n\n"
            all_reports += culture_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- WORKFORCE & ROLES REPORT ---\n\n"
            all_reports += workforce_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- SOCIAL & RELATIONSHIPS REPORT ---\n\n"
            all_reports += social_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- LIFE GOALS & MEMORIES REPORT ---\n\n"
            all_reports += life_goal_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- PERSONALITY & EMOTION REPORT ---\n\n"
            all_reports += personality_report
        except NameError:
            pass

        try:
            all_reports += "\n\n--- WORLD RISK & ALERTS REPORT ---\n\n"
            all_reports += risk_report
        except NameError:
            pass

        st.download_button(
            "Download All Reports Bundle",
            data=all_reports,
            file_name=f"observer_world_reports_day_{sim.day}.txt",
            mime="text/plain",
            key="download_all_reports_bundle"
        )

    with news_tab3:
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

        st.markdown("### Most Influential Family")

        family_summary = generate_most_influential_family_summary(sim)

        st.text_area(
            "Most Influential Family",
            family_summary,
            height=300
        )

        st.download_button(
            label="Download Most Influential Family Summary",
            data=family_summary,
            file_name=f"most_influential_family_day_{sim.day}.txt",
            mime="text/plain",
            key="download_most_influential_family"
        )

    with news_tab4:
        st.markdown("### Full Story Export Bundle")

        story_bundle = generate_story_export_bundle(sim)

        st.download_button(
            label="Download Full Story Bundle",
            data=story_bundle,
            file_name=f"observer_world_story_bundle_day_{sim.day}.txt",
            mime="text/plain",
            key="download_story_bundle"
        )