import streamlit as st
import pandas as pd
from cache import get_cached_players, get_cached_competitions

def show_players_tab():
    st.header("Rubik's Cube Player Rankings")
    df = pd.DataFrame(get_cached_players())

    countries = df["country"].dropna().unique()
    selected_country = st.selectbox("Filter by country", ["All"] + sorted(countries.tolist()))
    metric = st.selectbox("Sort by", ["rank90avg", "rank365avg"])
    order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)

    if selected_country != "All":
        df = df[df["country"] == selected_country]

    df = df.sort_values(metric, ascending=(order == "Ascending"))
    st.dataframe(df[["name", "country", "rank90avg", "rank365avg"]], use_container_width=True)

def show_competitions_tab():
    st.header("Competition Rankings")
    df = pd.DataFrame(get_cached_competitions())

    countries = df["country"].dropna().unique()
    selected_country = st.selectbox("Filter by country", ["All"] + sorted(countries.tolist()))
    metric = st.selectbox("Sort by", ["rank90avg_avg", "rank365avg_avg"])
    order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)

    if selected_country != "All":
        df = df[df["country"] == selected_country]

    df = df.sort_values(metric, ascending=(order == "Ascending"))
    st.dataframe(df[["name", "city", "country", "date_from", "rank90avg_avg", "rank365avg_avg"]], use_container_width=True)
