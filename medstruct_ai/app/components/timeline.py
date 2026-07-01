
import streamlit as st

from medstruct_ai.db.database import get_all_patients, get_patient_record


def render_timeline():
    st.header("Patient Records")

    patients = get_all_patients()
    if not patients:
        st.info("No patient data yet.")
        return

    selected_id = None
    search_query = st.text_input(
        "Search patients by name, diagnosis, medication, or notes",
        placeholder="e.g. hypertension, amoxicillin, cough",
    )

    if search_query:
        from medstruct_ai.db.queries import search_patients

        results = search_patients(search_query)
        if results:
            st.success(f"Found {len(results)} result(s)")
            for r in results:
                with st.expander(
                    f"{r['patient_name']} — {r['visit_date']}"
                    f"{'  ⚠️ ' + r['overall_risk'] if r['overall_risk'] else ''}"
                ):
                    if r["diagnoses"]:
                        st.markdown(f"**Diagnoses:** {r['diagnoses']}")
                    if r["medications"]:
                        st.markdown(f"**Medications:** {r['medications']}")
                    if r["notes"]:
                        st.text_area("Notes", r["notes"], height=80, disabled=True)
        else:
            st.warning("No results found.")
        st.divider()

    col1, col2 = st.columns([1, 2])
    with col1:
        patient_options = {
            f"{p['first_name']} {p['last_name']} (DOB: {p['dob']})": p["id"]
            for p in patients
        }
        selected_label = st.selectbox("Select Patient", list(patient_options.keys()))
        selected_id = patient_options[selected_label]

    if selected_id is None:
        return

    record = get_patient_record(selected_id)
    if record is None:
        st.warning("Patient not found.")
        return

    insights = sorted(record.insights, key=lambda i: i.visit_date)

    st.subheader(f"{record.first_name} {record.last_name}")
    st.caption(f"Date of Birth: {record.dob}")

    if not insights:
        st.info("No visits recorded.")
        return

    st.markdown("### Visit Timeline")

    for i, insight in enumerate(insights):
        is_last = i == len(insights) - 1
        risk_color = (
            "green"
            if insight.overall_risk == "Low"
            else (
                "orange"
                if insight.overall_risk == "Medium"
                else "red" if insight.overall_risk == "High" else "gray"
            )
        )
        risk_badge = (
            f":{risk_color}[**{insight.overall_risk}**]"
            if insight.overall_risk
            else "No risk assessment"
        )

        cols = st.columns([1, 10])
        with cols[0]:
            st.markdown(f"**{insight.visit_date}**")
        with cols[1]:
            st.markdown(f"Risk: {risk_badge}")

        tcols = st.columns([1, 5, 5])
        with tcols[0]:
            st.write("")
        with tcols[1]:
            if insight.diagnoses:
                st.markdown("**Diagnoses**")
                for d in insight.diagnoses:
                    st.markdown(f"- {d}")
            if insight.medications:
                st.markdown("**Medications**")
                for m in insight.medications:
                    st.markdown(f"- {m}")
        with tcols[2]:
            if insight.lab_metrics:
                st.markdown("**Lab Metrics**")
                for lm in insight.lab_metrics:
                    flag = "⚠️" if lm.is_abnormal else "✅"
                    st.markdown(f"- {flag} {lm.name}: {lm.value} {lm.unit}")
        if insight.notes:
            with st.expander("Notes"):
                st.write(insight.notes)

        if not is_last:
            st.divider()
