# insight_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

def render_dashboard():
    # ---- THEME CSS (Bamboo + Glass + Po float) ----
    st.markdown(r"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Mandali&display=swap');
      body {
        background: url('https://i.imgur.com/9QHCfI5.jpg') no-repeat center/cover fixed;
        font-family: 'Mandali', sans-serif;
        color: #fff;
      }
      .glass {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(8px);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      }
      .float-po {
        float: right;
        width: 120px;
        animation: float 4s ease-in-out infinite;
      }
      @keyframes float {
        0%,100% { transform: translateY(0); }
        50%   { transform: translateY(-10px); }
      }
      .timeline {
        position: relative;
        padding-left: 1.2rem;
        border-left: 3px solid #FFD700;
      }
      .timeline-item {
        margin-bottom: 1rem;
        padding-left: 0.8rem;
      }
      .timeline-item::before {
        content: '🐼';
        position: absolute;
        left: -1.3rem;
      }
      .quick-card {
        background: rgba(255,255,255,0.08);
        padding: 1rem;
        border-radius: 0.75rem;
        text-align: center;
        transition: transform .2s;
      }
      .quick-card:hover {
        transform: scale(1.05);
      }
    </style>
    """, unsafe_allow_html=True)

    # ---- LIVE CLOCK ----
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz).strftime("%A, %d %b %Y  %H:%M:%S %Z")
    st.markdown(f"<div style='text-align:right; color:#eee;'>{now}</div>", unsafe_allow_html=True)

    # ---- HEADER ----
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<h1 style="margin:0; color:#FFD700;">🌸 Oogway Insights</h1>', unsafe_allow_html=True)
    st.markdown('<p style="margin:0; color:#f0e6a8;">“When the path you walk always leads back to yourself, you never get anywhere.”</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- WELCOME + PO ----
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    col1, col2 = st.columns([1,3])
    with col1:
        st.image("https://static.wikia.nocookie.net/dreamworks/images/e/e1/Oogway_Profile.jpg/revision/latest?cb=20240208192611", caption="Master Oogway", width=140)
    with col2:
        st.markdown("""
          <h3 style="margin-top:0;">Welcome, Kiddo</h3>
          <p>Embrace stillness. Let your insights flow like water.</p>
          <p><b>142</b> MVRs processed  |  <b>98%</b> accuracy</p>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- PERFORMANCE CARDS ----
    kpis = [
      ("Total Drivers", "1,428", "+24"),
      ("Compliance Rate", "96.7%", "+1.2%"),
      ("Avg Proc Time", "3.2 min", "−45s")
    ]
    cols = st.columns(3, gap="large")
    for (t, v, d), c in zip(kpis, cols):
        with c:
            st.markdown(f"""
              <div class="glass" style="text-align:center;">
                <h4 style="margin:0;">{t}</h4>
                <p style="font-size:1.8rem; margin:0.2rem 0;">{v}</p>
                <small style="color:#8f8;">{d}</small>
              </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ---- WEEKLY QC MINI-CHARTS ----
    st.markdown("### 📊 Weekly QC Trends")
    df = pd.DataFrame({
      "Week":["W1","W2","W3","W4"],
      "Checks":[218,245,267,254],
      "Accuracy":[93.5,96.1,97.4,98.2]
    })
    bar = px.bar(df, x="Week", y="Checks", text_auto=".2s", color_discrete_sequence=["#FFD700"])
    bar.update_layout(margin=dict(t=5,b=20,l=0,r=0), height=220, plot_bgcolor="rgba(0,0,0,0)")
    bar.update_traces(textposition="outside")
    line = px.line(df, x="Week", y="Accuracy", markers=True, color_discrete_sequence=["#00FA9A"])
    line.update_layout(margin=dict(t=5,b=20,l=0,r=0), height=220, plot_bgcolor="rgba(0,0,0,0)")
    line.update_traces(line=dict(width=2), marker=dict(size=7))
    colA, colB = st.columns(2)
    with colA: st.plotly_chart(bar, use_container_width=True)
    with colB: st.plotly_chart(line, use_container_width=True)

    st.markdown("---")

    # ---- RECENT ACTIVITY TIMELINE ----
    st.markdown("### 🕒 Recent Activity")
    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    items = [
      ("MVR Processed","James","2 min ago"),
      ("IFTA Report","Auto Bot","1 hr ago"),
      ("New Driver","Sarah","3 hrs ago"),
      ("License Alert","System","Yesterday")
    ]
    for act, who, when in items:
        st.markdown(f"""
          <div class="timeline-item">
            <b>{act}</b> by *{who}* — {when}
          </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- QUICK ACTIONS ----
    st.markdown("### ⚡ Quick Actions")
    actions = [("🔄","Process MVRs"),("📑","Generate IFTA"),("➕","Add Driver")]
    qcols = st.columns(len(actions), gap="medium")
    for (ico, lbl), qc in zip(actions, qcols):
        with qc:
            st.markdown(f"""
              <div class="quick-card">
                <div style="font-size:1.8rem;">{ico}</div>
                <p style="margin:0.5rem 0 0;">{lbl}</p>
              </div>
            """, unsafe_allow_html=True)

    # ---- FOOTER STATUS ----
    st.markdown(f"""
      <div style="text-align:center; padding:1rem 0; color:#ccc;">
        ● Operational   |   Last sync: {now}
      </div>
    """, unsafe_allow_html=True)