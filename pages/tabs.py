import streamlit as st
import pandas as pd
from api import fetch_latest_players, fetch_latest_competitions

@st.cache_data(ttl=3600)
def get_cached_players():
    return fetch_latest_players()

@st.cache_data(ttl=3600)
def get_cached_competitions():
    return fetch_latest_competitions()

def show_players_tab():
    data = get_cached_players()
    df = pd.DataFrame(data)

    # Convert times from centiseconds to seconds
    for col in ["best_365", "average_365", "best_90", "average_90"]:
        df[col] = df[col] / 100

    # Add WCA Link
    df["WCA Link"] = df["id"].apply(
        lambda x: f"https://www.worldcubeassociation.org/persons/{x}"
    )

    # Rename columns
    df = df.rename(columns={
        "id": "WCA ID",
        "name": "Name",
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

    # Sort
    df = df.sort_values(by="World Ranking - 5 Solves (365d)", ascending=True)

    # Reorder WCA Link to be the last column
    cols = [col for col in df.columns if col != "WCA Link"] + ["WCA Link"]
    df = df[cols]

    # Display DataFrame with selection capability
    event = st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Handle row selection for navigation
    if len(event.selection.rows) > 0:
        selected_idx = event.selection.rows[0]
        # Get original ID before column rename
        original_data = pd.DataFrame(get_cached_players())
        selected_person = original_data.iloc[selected_idx]['id']
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"Selected: {selected_person}")
        with col2:
            if st.button(f"View Player Details", type="primary"):
                # Navigate to player page using session state
                st.session_state.current_view = 'player'
                st.session_state.selected_person_id = selected_person
                st.rerun()

def show_competitions_tab():
    data = get_cached_competitions()
    df = pd.DataFrame(data)

    # Remove rows with any missing values
    df = df.dropna()

    # Add WCA Link column
    df["WCA Link"] = df["competition_id"].apply(
        lambda x: f"https://www.worldcubeassociation.org/competitions/{x}"
    )

    for col in ["perf90avg", "perf365avg"]:
        df[col] = df[col] / 100

    # Rename columns
    df = df.rename(columns={
        "name": "Name",
        "city": "City",
        "country": "Country",
        "date_from": "Competition Date",
        "rank90avg_avg": "Average Ranking - Top 10 (90d)",
        "rank365avg_avg": "Average Ranking - Top 10 (365d)",
        "perf90avg": "Avg Perf - Top 10 (90d)",
        "perf365avg": "Avg Perf - Top 10 (365d)"
    })

    # Format date
    df["Competition Date"] = pd.to_datetime(df["Competition Date"]).dt.date

    # Sort
    df = df.sort_values(by="Average Ranking - Top 10 (365d)", ascending=True)

    # Reorder WCA Link to the end
    cols = [col for col in df.columns if col != "WCA Link"] + ["WCA Link"]
    df = df[cols]

    # Display DataFrame with selection capability
    event = st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Handle row selection for navigation
    if len(event.selection.rows) > 0:
        selected_idx = event.selection.rows[0]
        # Get original competition_id before column operations
        original_data = pd.DataFrame(get_cached_competitions()).dropna()
        selected_comp = original_data.iloc[selected_idx]['competition_id']
        comp_name = original_data.iloc[selected_idx]['name']
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"Selected: {comp_name} ({selected_comp})")
        with col2:
            if st.button(f"View Competition Details", type="primary"):
                # Navigate to competition page using session state
                st.session_state.current_view = 'competition'
                st.session_state.selected_comp_id = selected_comp
                st.rerun()