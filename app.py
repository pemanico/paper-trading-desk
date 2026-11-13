#!/usr/bin/env python3
"""
Paper Trading Visualizer
Small Streamlit app to visualize the skeleton simulation.
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Paper Trading Desk", layout="wide")

st.title("Paper Trading Desk — Visualizer")
st.caption("Skeleton based on professional risk criteria. High rejection rate is expected.")

# Load data
csv_path = Path("paper_log.csv")
if not csv_path.exists():
    st.error("paper_log.csv not found. Run skeleton_paper.py first.")
    st.stop()

df = pd.read_csv(csv_path)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Summary metrics
col1, col2, col3, col4, col5 = st.columns(5)
entered = df[df["decision"] == "ENTER"]
total = len(df)
rej = (df["decision"] == "REJECT").sum()
wins = (entered["pnl_usd"] > 0).sum()
final_eq = df["equity_after"].iloc[-1] if len(df) else 1000
pnl = final_eq - 1000

col1.metric("Candidates", total)
col2.metric("Rejected", f"{rej} ({rej/total*100:.1f}%)")
col3.metric("Entered", len(entered))
col4.metric("Win rate", f"{(wins/len(entered)*100) if len(entered) else 0:.1f}%")
col5.metric("Final equity", f"${final_eq:.2f}", delta=f"${pnl:.2f}")

# Equity curve
st.subheader("Equity Curve")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.index, y=df["equity_after"],
    mode="lines+markers", name="Equity",
    line=dict(color="#00cc96", width=2)
))
fig.update_layout(height=400, margin=dict(l=0, r=0, t=20, b=0),
                  yaxis_title="Equity ($)", xaxis_title="Candidate #")
st.plotly_chart(fig, use_container_width=True)

# Rejection reasons
st.subheader("Rejection Reasons")
rej_df = df[df["decision"] == "REJECT"]
if len(rej_df):
    reason_counts = rej_df["reason"].value_counts().reset_index()
    reason_counts.columns = ["reason", "count"]
    fig2 = px.bar(reason_counts, x="count", y="reason", orientation="h",
                  title="", color="count", color_continuous_scale="Reds")
    fig2.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0),
                       yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No rejections.")

# Trades table
st.subheader("Trade Log")
st.dataframe(
    df[["symbol", "decision", "reason", "size_usd", "risk_usd", "pnl_usd",
        "equity_after", "vol_to_mcap", "funding"]].round(4),
    use_container_width=True,
    height=400
)

st.divider()
st.caption("Next steps: add real API data, live equity, or more filters. This is the visualization layer on top of the skeleton.")
