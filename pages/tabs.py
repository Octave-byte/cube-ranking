import streamlit as st
import pandas as pd
import requests
from api import SUPABASE_URL, HEADERS
from cache import get_cached_players, get_cached_competitions

@st.cache_data(ttl=3600)
def fetch_player_history(person_id):
    url = f"{SUPABASE_URL}/rest/v1/player_metrics?personId=eq.{person_id}&select=*&order=date.asc&limit=10000"
    return requests.get(url, headers=HEADERS).json()

def show_player_page(person_id):
    st.header(f"Player Detail: {person_id}")
    df = pd.DataFrame(fetch_player_history(person_id))
    if df.empty:
        st.error("No data found.")
        return

    st.subheader(f"Competitions: {df.shape[0]}")

    # Show table with selected metrics
    columns_to_show = [
        "date", "rank90best", "rank365best",
        "average_90", "average_365",
        "rank90avg", "rank365avg",
        "rank90best_national", "rank90avg_national",
        "rank365best_national", "rank365avg_national"
    ]
    available_columns = [col for col in columns_to_show if col in df.columns]
    df_display = df[available_columns].sort_values(by="rank365avg", ascending=True)

    st.dataframe(df_display, use_container_width=True)

    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Download Data as CSV", csv, "player_data.csv", "text/csv")

    if st.button("← Back to main view"):
        st.query_params.clear()
        st.rerun()

def show_players_tab():
    st.header("Rubik's Cube Player Rankings")
    df = pd.DataFrame(get_cached_players())

    countries = df["country"].dropna().unique()
    selected_country = st.selectbox("Filter by country", ["All"] + sorted(countries.tolist()))

    if selected_country != "All":
        df = df[df["country"] == selected_country]

    df_display = df.sort_values("rank365avg", ascending=True)
    st.dataframe(df_display[["name", "country", "rank90avg", "rank365avg"]], use_container_width=True)

def show_competitions_tab():
    st.header("Competition Rankings")
    df = pd.DataFrame(get_cached_competitions())

    countries = df["country"].dropna().unique()
    selected_country = st.selectbox("Filter by country", ["All"] + sorted(countries.tolist()))

    if selected_country != "All":
        df = df[df["country"] == selected_country]

    df_display = df.sort_values("rank365avg_avg", ascending=True)
    st.dataframe(df_display[["name", "city", "country", "date_from", "rank90avg_avg", "rank365avg_avg"]], use_container_width=True)
