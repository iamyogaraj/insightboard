# insight_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

def render_dashboard():
    # 1) Page styling
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
      html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f9fafa;
      }
      .kpi-card {
        background: white;
        border-radius: 0.6rem;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: 0.2s ease-in-out;
      }
      .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
      }
      .kpi-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 0.4rem;
      }
      .kpi-value {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
      }
      .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 2rem;
        color: #333;
      }
      .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.85rem;
        margin-top: 2rem;
        padding-bottom: 1rem;
      }
    </style>
    """, unsafe_allow_html=True)

    # 2) Live clock
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz).strftime("%A, %d %b %Y • %H:%M:%S %Z")
    st.markdown(f"<div style='text-align:right; color:#777;'>{now}</div>", unsafe_allow_html=True)

    # 3) Header
    st.markdown("## 📊 InsightOps Executive Dashboard")
    st.markdown("A clean and clear view of your operational metrics and trends")

    # 4) KPI Cards
    st.markdown('<div class="section-header">Today’s Key Metrics</div>', unsafe_allow_html=True)
    kpi_data = [
        ("Total Drivers", "1,428", "+24"),
        ("Compliance Rate", "96.7%", "▲1.2%"),
        ("Avg. Processing Time", "3.2 min", "▼45s")
    ]
    col1, col2, col3 = st.columns(3)
    for (label, value, delta), col in zip(kpi_data, [col1, col2, col3]):
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
              <div class='kpi-label'>{label}</div>
              <div class='kpi-value'>{value}</div>
              <div style='color: #198754; font-size: 0.85rem;'>{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    # 5) Trend Charts
    st.markdown('<div class="section-header">QC Activity & Accuracy</div>', unsafe_allow_html=True)
    df = pd.DataFrame({
        "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "QC Checks": [218, 245, 267, 254],
        "Accuracy": [93.5, 96.1, 97.4, 98.2]
    })
    colA, colB = st.columns(2)
    with colA:
        fig1 = px.bar(df, x="Week", y="QC Checks", text_auto=".2s", color_discrete_sequence=["#0d6efd"])
        fig1.update_layout(margin=dict(t=10, b=20, l=0, r=0), height=280)
        st.plotly_chart(fig1, use_container_width=True)
    with colB:
        fig2 = px.line(df, x="Week", y="Accuracy", markers=True, color_discrete_sequence=["#6f42c1"])
        fig2.update_layout(margin=dict(t=10, b=20, l=0, r=0), height=280, yaxis_tickformat=".1f%%")
        st.plotly_chart(fig2, use_container_width=True)

    # 6) Recent Activity
    st.markdown('<div class="section-header">Recent Activity</div>', unsafe_allow_html=True)
    activity_log = [
        ("MVR Processed", "James W.", "2 min ago", "✅ Completed"),
        ("IFTA Report", "Auto Bot", "1 hr ago", "⌛ Pending"),
        ("New Driver Added", "Sarah J.", "3 hrs ago", "✔ Verified"),
        ("License Alert", "System", "Yesterday", "⚠ Attention Needed")
    ]
    for action, by, when, status in activity_log:
        st.markdown(f"- **{action}** by *{by}* • {when} — {status}")

    # 7) Quick Actions
    st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
    colX, colY, colZ = st.columns(3)
    if colX.button("🔄 Process New MVRs"):
        st.success("MVR pipeline triggered")
    if colY.button("📥 Upload New Data"):
        st.info("Upload dialog opened")
    if colZ.button("➕ Add New Driver"):
        st.success("Driver registration form ready")

    # 8) Footer
    st.markdown(f"<div class='footer'>● Dashboard operational • Last sync: {now}</div>", unsafe_allow_html=True)
