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