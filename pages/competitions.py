import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from api import SUPABASE_URL, HEADERS

#test
@st.cache_data(ttl=3600)
def fetch_competition_history(comp_id):
    url = f"{SUPABASE_URL}/rest/v1/competition_ranking?comp_id=eq.{comp_id}&select=*"
    return requests.get(url, headers=HEADERS).json()

@st.cache_data(ttl=3600)
def fetch_competition_metadata(comp_id):
    url = f"{SUPABASE_URL}/rest/v1/competitions?comp_id=eq.{comp_id}&select=name,city,country,date_from&limit=1"
    return requests.get(url, headers=HEADERS).json()

def show_competition_page(comp_id):
    st.header(f"Competition Detail: {comp_id}")
    meta = fetch_competition_metadata(comp_id)
    if not meta:
        st.error("Not found.")
        return

    m = meta[0]
    st.subheader(f"{m['name']} ({m['city']}, {m['country']})")
    st.caption(f"Date: {m['date_from']}")

    df = pd.DataFrame(fetch_competition_history(comp_id))
    if df.empty:
        st.error("No data.")
        return

    col1, col2 = st.columns(2)
    metric = col1.selectbox("Metric", ["perf", "rank"])
    window = col2.radio("Window", ["90", "365"], horizontal=True)

    y_col = f"{metric}{window}avg"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df[y_col], name=metric))
    fig.update_layout(title=f"{metric} {window}d Evolution", xaxis_title="Date", yaxis_title=metric)
    if metric == "rank":
        fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Download Data as CSV", csv, "competition_data.csv", "text/csv")

    if st.button("← Back to main view"):
        st.experimental_set_query_params()
        st.rerun()
