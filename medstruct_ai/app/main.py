import tempfile
from datetime import date
from pathlib import Path

import fitz
import streamlit as st

from medstruct_ai.app.components.charts import render_dashboard
from medstruct_ai.app.components.timeline import render_timeline
from medstruct_ai.core.audio.transcriber import transcribe_audio
from medstruct_ai.core.parser import parse_lab_metrics
from medstruct_ai.core.schemas import ClinicalInsight, PatientRecord
from medstruct_ai.core.vision.extractor import extract_clinical_data_from_image
from medstruct_ai.db.database import (init_db,
                                      insert_patient_record)

st.set_page_config(page_title="MedStruct AI", layout="wide")

init_db()

st.title("MedStruct AI")
st.markdown("Offline-first clinical intelligence system")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Patient Records", "Upload"])

if page == "Dashboard":
    render_dashboard()

elif page == "Patient Records":
    render_timeline()

elif page == "Upload":
    st.header("Upload Medical Data")

    upload_type = st.radio(
        "Select input type",
        ["Audio Note (.wav)", "Lab Report / Prescription (PDF/Image)"],
    )

    if upload_type == "Audio Note (.wav)":
        uploaded_file = st.file_uploader("Choose a WAV audio file", type=["wav"])

        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            with st.spinner("Transcribing audio..."):
                try:
                    transcription = transcribe_audio(tmp_path)
                    st.success("Transcription complete")
                    st.text_area("Transcribed Text", transcription, height=200)

                    st.divider()
                    st.subheader("Save to Patient Record")

                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name")
                        last_name = st.text_input("Last Name")
                    with col2:
                        dob = st.date_input("Date of Birth", value=date(1980, 1, 1))
                        visit_date = st.date_input("Visit Date", value=date.today())

                    if st.button("Save Transcription"):
                        if not first_name or not last_name:
                            st.error("First name and last name are required.")
                        else:
                            record = PatientRecord(
                                first_name=first_name.strip(),
                                last_name=last_name.strip(),
                                dob=dob,
                                insights=[
                                    ClinicalInsight(
                                        visit_date=visit_date,
                                        notes=transcription,
                                    )
                                ],
                            )
                            pid = insert_patient_record(record)
                            st.success(
                                f"Saved transcription for {first_name} {last_name} "
                                f"(Patient ID: {pid})"
                            )
                except Exception as e:
                    st.error(f"Transcription failed: {e}")
                finally:
                    Path(tmp_path).unlink(missing_ok=True)

    elif upload_type == "Lab Report / Prescription (PDF/Image)":
        uploaded_file = st.file_uploader(
            "Choose a PDF or image file",
            type=["pdf", "png", "jpg", "jpeg"],
        )

        if uploaded_file is not None:
            file_type = Path(uploaded_file.name).suffix.lower()

            with tempfile.NamedTemporaryFile(suffix=file_type, delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                if file_type == ".pdf":
                    doc = fitz.open(tmp_path)
                    page = doc[0]
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    img_path = tmp_path + ".png"
                    with open(img_path, "wb") as f:
                        f.write(img_bytes)
                    doc.close()
                    image_path_for_vlm = img_path
                else:
                    image_path_for_vlm = tmp_path

                with st.spinner("Extracting clinical data using local VLM..."):
                    extracted = extract_clinical_data_from_image(image_path_for_vlm)
                    st.success("Extraction complete")
                    st.text_area("Extracted Data", extracted, height=200)

                    st.divider()
                    st.subheader("Save to Patient Record")

                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name")
                        last_name = st.text_input("Last Name")
                    with col2:
                        dob = st.date_input("Date of Birth", value=date(1980, 1, 1))
                        visit_date = st.date_input("Visit Date", value=date.today())

                    lab_metrics = parse_lab_metrics(extracted)
                    if lab_metrics:
                        st.info(f"Detected {len(lab_metrics)} lab metric(s).")
                        for m in lab_metrics:
                            flag = "⚠️" if m.is_abnormal else "✅"
                            st.caption(f"{flag} {m.name}: {m.value} {m.unit}")

                    if st.button("Save Extraction"):
                        if not first_name or not last_name:
                            st.error("First name and last name are required.")
                        else:
                            record = PatientRecord(
                                first_name=first_name.strip(),
                                last_name=last_name.strip(),
                                dob=dob,
                                insights=[
                                    ClinicalInsight(
                                        visit_date=visit_date,
                                        notes=extracted,
                                        lab_metrics=lab_metrics,
                                    )
                                ],
                            )
                            pid = insert_patient_record(record)
                            st.success(
                                f"Saved extraction for {first_name} {last_name} "
                                f"(Patient ID: {pid}) — {len(lab_metrics)} lab metrics"
                            )
            except Exception as e:
                st.error(f"Extraction failed: {e}")
            finally:
                Path(tmp_path).unlink(missing_ok=True)
                if file_type == ".pdf":
                    pdf_img = tmp_path + ".png"
                    Path(pdf_img).unlink(missing_ok=True)
