import altair as alt
import pandas as pd
import streamlit as st

from medstruct_ai.db.database import (
    get_all_patients,
    get_metrics_for_charts,
    get_risk_summary,
)


def render_dashboard():
    st.header("Dashboard")
    patients = get_all_patients()

    if not patients:
        st.info(
            "No patient data yet. Upload a lab report or audio note to get started."
        )
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        patient_options = {
            f"{p['first_name']} {p['last_name']}": p["id"] for p in patients
        }
        selected_name = st.selectbox("Select Patient", list(patient_options.keys()))
        patient_id = patient_options[selected_name]

    metric_rows = get_metrics_for_charts(patient_id)

    if metric_rows:
        df = pd.DataFrame(metric_rows)
        df["visit_date"] = pd.to_datetime(df["visit_date"]).dt.date

        metric_names = df["name"].unique().tolist()
        selected_metric = st.selectbox("Lab Metric", metric_names)
        metric_df = df[df["name"] == selected_metric]

        if len(metric_df) > 1:
            chart = (
                alt.Chart(metric_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("visit_date:T", title="Visit Date"),
                    y=alt.Y(
                        "value:Q",
                        title=f"{selected_metric} ({metric_df.iloc[0]['unit']})",
                    ),
                    tooltip=["visit_date", "value", "is_abnormal"],
                )
                .properties(height=300)
            )
            st.altair_chart(chart, width="stretch")
        else:
            st.metric(
                label=f"{selected_metric} ({metric_df.iloc[0]['unit']})",
                value=metric_df.iloc[0]["value"],
                delta="Abnormal" if metric_df.iloc[0]["is_abnormal"] else "Normal",
            )

        st.divider()
        st.subheader("All Metrics — This Visit")

        latest_date = df["visit_date"].max()
        latest_df = df[df["visit_date"] == latest_date]
        for _, row in latest_df.iterrows():
            flag = "⚠️" if row["is_abnormal"] else "✅"
            st.caption(f"{flag} {row['name']}: {row['value']} {row['unit']}")
    else:
        st.info("No lab metrics recorded for this patient.")

    st.divider()
    st.subheader("Risk Overview")

    risk_data = get_risk_summary()
    if risk_data:
        risk_df = pd.DataFrame(risk_data)
        color_scale = alt.Scale(
            domain=["Low", "Medium", "High"],
            range=["green", "orange", "red"],
        )
        bar = (
            alt.Chart(risk_df)
            .mark_bar()
            .encode(
                x=alt.X(
                    "overall_risk:N", title="Risk Level", sort=["Low", "Medium", "High"]
                ),
                y=alt.Y("count:Q", title="Visits"),
                color=alt.Color("overall_risk:N", scale=color_scale, legend=None),
                tooltip=["overall_risk", "count"],
            )
            .properties(height=250)
        )
        st.altair_chart(bar, width="stretch")
    else:
        st.info("No risk assessments yet.")
