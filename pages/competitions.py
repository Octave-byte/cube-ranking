import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from api import SUPABASE_URL, HEADERS
import uuid

#test
@st.cache_data(ttl=3600)
def fetch_competition_history(comp_id):
    url = f"{SUPABASE_URL}/rest/v1/competition_ranking?comp_id=eq.{comp_id}&select=*"
    return requests.get(url, headers=HEADERS).json()

@st.cache_data(ttl=3600)
def fetch_competition_metadata(comp_id):
    url = f"{SUPABASE_URL}/rest/v1/competitions?comp_id=eq.{comp_id}&select=id, name,city,country,date_from"
    return requests.get(url, headers=HEADERS).json()

def show_competition_page(comp_id):
    st.header(f"Competition Detail: {comp_id}")
    meta = fetch_competition_metadata(comp_id)
    meta_df = pd.DataFrame(meta)  
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
    df = df.merge(meta_df[["id", "date_from"]], how="left", left_on="competition_id", right_on="id")

    # Convert performance data from centiseconds to seconds
    perf_columns = [col for col in df.columns if 'perf' in col and col != 'date_from']
    for col in perf_columns:
        if col in df.columns:
            df[col] = df[col] / 100

    col1, col2 = st.columns(2)
    metric = col1.selectbox("Metric", ["perf", "rank"])
    window = col2.radio("Window", ["90", "365"], horizontal=True)

    # Construct y-axis column name
    y_col = f"{'rank' if metric == 'rank' else 'perf'}{window}avg"
    if metric == "rank":
        y_col += "_avg"  

    # Create the plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date_from"], 
        y=df[y_col], 
        name=f"{metric.capitalize()} {window}d",
        mode='lines+markers'
    ))
    
    # Configure layout based on metric type
    if metric == "rank":
        fig.update_layout(
            title=f"Rank - {window}d Top 10 Avg",
            xaxis_title="Competition Date",
            yaxis_title="Rank",
            yaxis=dict(autorange="reversed")  # Lower rank numbers are better
        )
    else:  # performance
        fig.update_layout(
            title=f"Performance - {window}d Top 10 Avg",
            xaxis_title="Competition Date",
            yaxis_title="Performance (seconds)",
            yaxis=dict(autorange=True)  # Reset autorange for performance
        )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Download Data as CSV", csv, "competition_data.csv", "text/csv")

    # Back button (placed at the end of the function)
if st.button("← Back to main view"):
    st.query_params.clear()
    st.query_params.update({"uuid": str(uuid.uuid4())})  # force rerun recognition
    st.rerun()