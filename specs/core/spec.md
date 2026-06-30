# Feature Specification: MedStruct AI Core Engine

**Feature Branch**: `main`

**Created**: 2026-06-28

**Status**: Draft

**Input**: User description: "MedStruct AI offline-first, CPU-optimized clinical intelligence system"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Doctor Uploads Voice Note (Priority: P1)

A doctor records a patient visit using a voice recorder and uploads the audio file (.wav) to the system. The system must natively parse this audio into text and store the parsed insight.

**Why this priority**: Core ingestion mechanism needed before deriving any clinical values.
**Independent Test**: Upload a .wav file; assert that the transcribed text accurately reflects the audio and is saved.

**Acceptance Scenarios**:
1. **Given** a .wav file, **When** uploaded, **Then** `whisper.cpp` transcribes the text entirely offline.

---

### User Story 2 - Lab Report Ingestion (Priority: P1)

A doctor uploads a PDF lab report. The system parses the text using local VLMs/LLMs to extract critical health metrics (e.g., blood glucose, cholesterol) into structured schemas.

**Why this priority**: Required for computing the patient risk level.
**Independent Test**: Upload a PDF lab report; assert that JSON structured output with correctly parsed `LabMetric` objects is generated.

**Acceptance Scenarios**:
1. **Given** a PDF report, **When** uploaded, **Then** local Qwen model extracts data matching the `LabMetric` Pydantic schema.

---

### User Story 3 - Derived Risk Computation (Priority: P2)

Upon successful extraction of `LabMetric` objects, the system compares the metric values to standard baselines to determine if they are abnormal. It then aggregates the findings into an overall risk level (Low, Medium, High).

**Why this priority**: Computes the required derived value clinical insight constraint.
**Independent Test**: Provide mock `LabMetric` data containing out-of-bounds cholesterol; assert that the computed risk level is "High".

**Acceptance Scenarios**:
1. **Given** abnormal lab metrics, **When** processed, **Then** the `overall_patient_risk` field is populated with "High".

---

### User Story 4 - Semantic Search (Priority: P3)

A healthcare professional searches for a patient's historical records (e.g., "patients with high cholesterol"). The system queries the local database and returns matching insights.

**Why this priority**: Completes the core value proposition of making data searchable.
**Independent Test**: Search for a known condition in the mock data; assert that the correct `PatientRecord` is returned.

**Acceptance Scenarios**:
1. **Given** a search query, **When** executed, **Then** the local SQLite semantic search retrieves the relevant patient records.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST process audio natively using compiled `whisper.cpp`.
- **FR-002**: System MUST run inferences using local GGUF models (via Ollama/llama.cpp) on CPU.
- **FR-003**: System MUST NOT make any external internet requests.
- **FR-004**: System MUST validate all LLM outputs strictly against Pydantic v2 schemas.
- **FR-005**: System MUST compute and persist a "Derived Risk Level" (Low, Medium, High) for each patient visit based on lab metrics.

### Key Entities 

- **PatientRecord**: First name, last name, DOB, and a list of clinical insights.
- **ClinicalInsight**: Visit date, notes, diagnoses, medications, lab metrics, and overall computed risk level.
- **LabMetric**: Name, value, unit, and an `is_abnormal` boolean.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Full end-to-end pipeline (Audio/PDF -> LLM -> Pydantic -> SQLite) executes with Wi-Fi completely disabled.
- **SC-002**: Pydantic validation successfully coerces 95%+ of local LLM outputs into structured schemas using retry logic.
- **SC-003**: Inference times on CPU are acceptable for interactive use (under 30s per standard document).

## Assumptions

- User hardware supports AVX2 or ARM Neon instructions.
- User can initially connect to the internet to pre-cache the GGUF models before going air-gapped.
- Input data volume is reasonable for SQLite and local file storage.
