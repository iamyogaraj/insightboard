import streamlit as st
import pandas as pd
import plotly.express as px

def insight_dashboard_app():
    st.title("📊 Oogway Insights Dashboard")

    try:
        df = pd.read_csv("task_data.csv", parse_dates=["SubmissionTime"])
    except FileNotFoundError:
        st.warning("No task data found yet. Users need to submit via QC Radar.")
        return

    if "username" not in st.session_state or "role" not in st.session_state:
        st.error("User not authenticated.")
        return

    current_user = st.session_state["username"]
    role = st.session_state["role"]

    st.markdown(f"### 👤 Welcome, {current_user} ({role})")

    if role == "admin":
        st.markdown("#### 📋 All Users Leaderboard")

        leaderboard = (
            df.groupby("UserID")
              .agg(Tasks=("TaskID", "count"),
                   Avg_Accuracy=("QC_Passed", "mean"),
                   Last_Submission=("SubmissionTime", "max"))
              .reset_index()
              .sort_values("Avg_Accuracy", ascending=False)
        )
        leaderboard["Avg_Accuracy"] = leaderboard["Avg_Accuracy"].round(2)
        st.dataframe(leaderboard, use_container_width=True)

        fig = px.bar(leaderboard, x="UserID", y="Avg_Accuracy", text="Tasks",
                     title="Accuracy by User", color="Avg_Accuracy",
                     color_continuous_scale="greens")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.markdown("#### 🧠 Your QC Performance")

        user_data = df[df["UserID"] == current_user]
        if user_data.empty:
            st.info("You haven't submitted any tasks yet. Head to the QC Radar!")
            return

        total_tasks = user_data.shape[0]
        avg_accuracy = round(user_data["QC_Passed"].mean(), 2)
        last_time = user_data["SubmissionTime"].max().strftime("%b %d, %Y %I:%M %p")

        st.metric("📦 Total Tasks", total_tasks)
        st.metric("🎯 Avg Accuracy", f"{avg_accuracy}%")
        st.metric("🕒 Last Submission", last_time)

        st.markdown("#### 📅 Task Timeline")
        timeline = user_data.sort_values("SubmissionTime", ascending=True)
        fig2 = px.line(timeline, x="SubmissionTime", y="QC_Passed", markers=True,
                       title="Accuracy Over Time")
        fig2.update_traces(line=dict(color="#00BFFF"))
        st.plotly_chart(fig2, use_container_width=True)
