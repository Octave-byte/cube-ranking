import streamlit as st
import pandas as pd
from api import fetch_latest_players, fetch_latest_competitions

# --------------------------
# Player Tab - Preparation
# --------------------------
@st.cache_data(ttl=3600)
def get_cached_players():
    return fetch_latest_players()

player_data = get_cached_players()
players_df = pd.DataFrame(player_data)

# Create WCA Link and internal Name link
players_df["WCA Link"] = players_df["id"].apply(
    lambda x: f"https://www.worldcubeassociation.org/persons/{x}"
)
players_df["Name"] = players_df.apply(
    lambda row: f"[{row['name']}](./players/{row['id']})", axis=1
)

# Convert times from centiseconds to seconds
for col in ["best_365", "average_365", "best_90", "average_90"]:
    players_df[col] = players_df[col] / 100

# Rename columns
players_df = players_df.rename(columns={
    "id": "WCA ID",
    "country": "Country",
    "best_365": "1 Solve - 365d (s)",
    "average_365": "5 Solves - 365d (s)",
    "best_90": "1 Solve - 90d (s)",
    "average_90": "5 Solves - 90d (s)",
    "rank90best": "World Ranking - 1 Solve (90d)",
    "rank90avg": "World Ranking - 5 Solves (90d)",
    "rank365best": "World Ranking - 1 Solve (365d)",
    "rank365avg": "World Ranking - 5 Solves (365d)",
    "rank90best_national": "National Ranking - 1 Solve (90d)",
    "rank90avg_national": "National Ranking - 5 Solves (90d)",
    "rank365best_national": "National Ranking - 1 Solve (365d)",
    "rank365avg_national": "National Ranking - 5 Solves (365d)"
})

# Sort by global 365d average rank
players_df = players_df.sort_values(by="World Ranking - 5 Solves (365d)", ascending=True)

# Set column order
player_columns = ["Name", "Country", "WCA ID", "WCA Link"] + \
    [col for col in players_df.columns if col not in ["Name", "Country", "WCA ID", "WCA Link"]]
players_df = players_df[player_columns]


# --------------------------
# Competition Tab - Preparation
# --------------------------
@st.cache_data(ttl=3600)
def get_cached_competitions():
    return fetch_latest_competitions()

comp_data = get_cached_competitions()
comp_df = pd.DataFrame(comp_data)

# Create internal and WCA links
comp_df["Name"] = comp_df.apply(
    lambda row: f"[{row['name']}](./competitions/{row['comp_id']})",
    axis=1
)
comp_df["WCA Link"] = comp_df["competition_id"].apply(
    lambda x: f"https://www.worldcubeassociation.org/competitions/{x}"
)

# Convert times from centiseconds to seconds
for col in ["perf90avg", "perf365avg"]:
    comp_df[col] = comp_df[col] / 100

# Rename and reformat
comp_df = comp_df.rename(columns={
    "city": "City",
    "country": "Country",
    "date_from": "Competition Date",
    "rank90avg_avg": "Average Ranking - Top 10 (90d)",
    "rank365avg_avg": "Average Ranking - Top 10 (365d)",
    "perf90avg": "Avg Perf - Top 10 (90d)",
    "perf365avg": "Avg Perf - Top 10 (365d)"
})
comp_df["Competition Date"] = pd.to_datetime(comp_df["Competition Date"]).dt.date

# Sort by 365d average ranking
comp_df = comp_df.sort_values(by="Average Ranking - Top 10 (365d)", ascending=True)

# Set column order
comp_columns = ["Name", "City", "Country", "Competition Date", "WCA Link",
                "Average Ranking - Top 10 (90d)", "Average Ranking - Top 10 (365d)",
                "Avg Perf - Top 10 (90d)", "Avg Perf - Top 10 (365d)"]
comp_df = comp_df[comp_columns]


# --------------------------
# Search UI
# --------------------------

st.title("Rubik's Cube Rankings")

# Fetch IDs for routing logic
player_ids = {player["id"] for player in get_cached_players()}
comp_ids = {comp["comp_id"] for comp in get_cached_competitions()}

# Global Search
search_query = st.text_input("🔍 Search for a Player or Competition by ID", "")

if search_query:
    if search_query in player_ids:
        st.success(f"Redirecting to player {search_query}...")
        st.experimental_rerun()  # Rerun to allow dynamic linking
        st.markdown(f'<meta http-equiv="refresh" content="0;url=/players/{search_query}" />', unsafe_allow_html=True)
    elif search_query in comp_ids:
        st.success(f"Redirecting to competition {search_query}...")
        st.experimental_rerun()
        st.markdown(f'<meta http-equiv="refresh" content="0;url=/competitions/{search_query}" />', unsafe_allow_html=True)
    else:
        st.warning("No matching player or competition found.")

# --------------------------
# Streamlit Tabs UI
# --------------------------
st.title("Rubik's Cube Rankings")

tab1, tab2 = st.tabs(["🧑 Players", "🏆 Competitions"])

with tab1:
    st.markdown("### Player Rankings")
    st.dataframe(players_df, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### Top Competitions")
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
