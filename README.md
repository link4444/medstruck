# MedStruct AI
**Status: Air-Gapped / Local CPU Engine Active**

## Overview
MedStruct AI is an offline-first, CPU-optimized clinical intelligence system designed to ingest unstructured medical inputs (lab report images, handwritten prescription photos, and doctor voice notes) and transform them into highly structured, validated relational datasets.

Healthcare professionals face a growing challenge with medical data isolation and paper decay. Critical patient history is often locked away in unsearchable, unstructured formats, scattered across physical filing cabinets or static image scans. MedStruct AI solves this by deploying a fully local, privacy-preserving AI pipeline that digitizes, parses, and derives insights from these records without ever exposing patient data to the cloud.

## Key Features
- **Multi-modal Ingestion:** Natively process lab report PDFs, handwritten prescription images, and doctor voice notes.
- **Derived Health Summaries:** Not just text extraction—MedStruct AI actively computes clinical insights, evaluating abnormal blood metrics against standard baselines to generate consolidated patient risk levels (Low, Medium, High).
- **Local Semantic Search:** Instantly query patient records, past diagnoses, and medication histories using an entirely local embedding search layer.
- **Interactive Timeline Tracker:** Visual dashboard tracing patient visits, metrics progression, and prescriptions over time.
- **Offline & CPU First:** Operates 100% locally with zero cloud API dependencies. Optimized for CPU execution using AVX2/ARM Neon acceleration with 4-bit quantized GGUF models.

## No-Internet Setup Guide
This guide walks you through setting up MedStruct AI on a completely air-gapped machine.

### 1. Clone the Repository
```bash
git clone https://gitlab.com/your-username/medstruct-ai.git
cd medstruct-ai
```

### 2. Pre-cache GGUF Files and Setup Script
Execute the setup script to prepare the environment and download the necessary quantized models (this step assumes an initial connection to acquire the weights onto a USB drive or local cache, but runtime requires zero internet).
```bash
# Run the environment setup script
bash scripts/setup_env.sh
```

### 3. Load Models into Ollama
Ensure you have Ollama installed locally.
```bash
# Start the Ollama server
ollama serve &

# Create and load the specialized local model from the GGUF file
ollama create medstruct-qwen -f models/Modelfile.qwen
```

### 4. Compile whisper.cpp Locally
Compile the audio inference engine natively on your machine for CPU acceleration.
```bash
cd core/audio/whisper.cpp
make
cd ../../../
```

### 5. Launch the Streamlit App
Initialize the local database and start the frontend interface.
```bash
# Initialize SQLite schemas
python scripts/init_db.py

# Launch the Streamlit presentation dashboard
streamlit run app/main.py
```

## Project Metadata
- [Changelog](CHANGELOG.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- CI Pipeline: Configured with 10 strict checks (Black, Ruff, MyPy, Bandit, Safety, Semantic Commits, etc.) running on local GitLab Runner.
