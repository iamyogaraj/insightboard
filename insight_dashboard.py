# insight_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
from datetime import datetime
import pytz

def render_dashboard():
    # ---- 1) GLOBAL CSS & STARFIELD ANIMATION ----
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;700&display=swap');

      body, .css-1d391kg { /* .css-1d391kg targets the main content area */
        font-family: 'Rajdhani', sans-serif;
        background: #000;
        color: #f0f0f0;
      }
      /* starfield background */
      .stApp {
        background: url('https://i.imgur.com/8Km9tLL.png') center/cover fixed;
      }
      /* glass cards */
      .glass {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(8px);
        border-radius: 0.75rem;
        padding: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
      }
      .glass:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.7);
      }
      /* neon headings */
      .neon {
        color: #0ff;
        text-shadow:
          0 0 4px #0ff,
          0 0 8px #0ff,
          0 0 16px #0ff,
          0 0 32px #08f;
      }
      /* footer */
      .footer {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        padding: 1rem 0;
      }
    </style>

    <!-- starfield animation -->
    <canvas id="stars"></canvas>
    <script>
      const c=document.getElementById("stars"),ctx=c.getContext("2d");
      c.width=window.innerWidth; c.height=window.innerHeight;
      let stars=Array.from({length:400},()=>({
        x:Math.random()*c.width, y:Math.random()*c.height,
        r:Math.random()*1.2, d:Math.random()*0.5+0.2
      }));
      function draw(){
        ctx.clearRect(0,0,c.width,c.height);
        ctx.fillStyle="rgba(255,255,255,0.8)";
        stars.forEach(s=>{
          ctx.globalAlpha=s.d; ctx.beginPath();
          ctx.arc(s.x,s.y,s.r,0,2*Math.PI); ctx.fill();
        });
        requestAnimationFrame(draw);
      }
      draw();
    </script>
    """, unsafe_allow_html=True)

    # ---- 2) SIDEBAR FILTERS & LIVE CLOCK ----
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    st.sidebar.markdown(f"### 🕒 {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    st.sidebar.markdown("---")
    start_date = st.sidebar.date_input("Start date", now.date())
    end_date   = st.sidebar.date_input("End date", now.date())
    st.sidebar.markdown("---")
    region = st.sidebar.selectbox("Region", ["All", "North", "South", "East", "West"])

    # ---- 3) HEADER ----
    st.markdown(f"<h1 class='neon'>⚔️ Cyber Samurai Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#aaa;'>Date range: {start_date} → {end_date} | Region: {region}</p>", unsafe_allow_html=True)

    # ---- 4) KPI GLASS CARDS ----
    total_drivers = 1428 + np.random.randint(-20,20)
    compliance    = round(96.5 + np.random.rand(),1)
    avg_time      = round(3 + np.random.rand(),2)
    kpi_cols = st.columns(3, gap="large")
    for (lbl,val,delta),col in zip(
      [("Drivers", total_drivers, f"{np.random.randint(-5,5)}"),
       ("Compliance %", f"{compliance}%", "+1.2%"),
       ("Avg Proc Time", f"{avg_time} min", "−0.5")],
      kpi_cols
    ):
        with col:
            st.markdown(f"""
              <div class="glass">
                <h4 style="margin:0">{lbl}</h4>
                <p style="font-size:1.8rem; margin:0.2rem 0;">{val}</p>
                <small style="color:#6f6;">{delta}</small>
              </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ---- 5) BAR & LINE CHARTS ----
    dates = pd.date_range(start_date, end_date, freq='W')
    checks   = np.random.randint(200,300, size=len(dates))
    accuracy = np.random.uniform(92,99, size=len(dates))
    df_trends = pd.DataFrame({"Week":dates.strftime("%b %d"), "Checks":checks, "Accuracy":accuracy})

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df_trends, x="Week", y="Checks", 
                     color="Checks", color_continuous_scale="turbo")
        fig.update_layout(margin=dict(t=20,b=20,l=0,r=0), height=300,
                          plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.line(df_trends, x="Week", y="Accuracy", markers=True,
                       line_shape="spline", color_discrete_sequence=["#0ff"])
        fig2.update_layout(margin=dict(t=20,b=20,l=0,r=0), height=300,
                           plot_bgcolor="rgba(0,0,0,0)",
                           yaxis_tickformat=".1f%%")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ---- 6) SCATTER MAP (PYDECK) ----
    st.markdown("### 📍 Driver Geo-Map")
    # sample coords
    coords = pd.DataFrame({
      "lat": np.random.uniform(28.4,28.8,30),
      "lon": np.random.uniform(77.0,77.4,30)
    })
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=pdk.ViewState(latitude=28.6, longitude=77.2, zoom=10),
        layers=[pdk.Layer("ScatterplotLayer", data=coords,
                          get_position=["lon","lat"], get_radius=400,
                          get_color=[0,200,255,140])]
    )
    st.pydeck_chart(deck, use_container_width=True)

    st.markdown("---")

    # ---- 7) DATA TABLE PREVIEW ----
    st.markdown("### 📋 Data Preview")
    df_preview = pd.DataFrame({
      "DriverID": np.arange(1,21),
      "Region": np.random.choice(["North","South","East","West"],20),
      "Score": np.random.randint(60,100,20)
    })
    st.dataframe(df_preview.style.background_gradient(cmap='turbo', axis=0), height=300)

    st.markdown("---")

    # ---- 8) QUICK ACTION BUTTONS ----
    st.markdown("### ⚡ Quick Actions")
    a1, a2, a3 = st.columns(3)
    if a1.button("🔄 Reprocess MVRs"):
        st.toast("Reprocessing kicked off!")
    if a2.button("📑 Export Report"):
        st.toast("Download ready!", icon="✅")
    if a3.button("➕ New Driver"):
        st.toast("Open driver form…", icon="👤")

    # ---- 9) FOOTER ----
    st.markdown(f"<div class='footer'>● Live &amp; Locked In | Last update: {now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
