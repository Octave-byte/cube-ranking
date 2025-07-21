import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from api import SUPABASE_URL, HEADERS

@st.cache_data(ttl=3600)
def fetch_player_history(person_id):
    url = f"{SUPABASE_URL}/rest/v1/player_metrics?personId=eq.{person_id}&select=*&order=date.asc"
    return requests.get(url, headers=HEADERS).json()

def show_player_page(person_id):
    st.header(f"Player Detail: {person_id}")
    df = pd.DataFrame(fetch_player_history(person_id))
    if df.empty:
        st.error("No data found.")
        return

    st.subheader(f"Competitions: {df.shape[0]}")

    col1, col2 = st.columns(2)
    metric = col1.selectbox("Metric", ["rank_world", "rank_country"])
    window = col2.radio("Window", ["90", "365"], horizontal=True)

    avg = f"rank{window}avg" if metric == "rank_world" else f"rank{window}avg_national"
    best = f"rank{window}best" if metric == "rank_world" else f"rank{window}best_national"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df[avg], name="Average"))
    fig.add_trace(go.Scatter(x=df["date"], y=df[best], name="Best"))
    fig.update_layout(title="Ranking Evolution", xaxis_title="Date", yaxis_title="Rank", yaxis_autorange="reversed")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Download Data as CSV", csv, "player_data.csv", "text/csv")

    if st.button("← Back to main view"):
        st.experimental_set_query_params()
        st.rerun()
