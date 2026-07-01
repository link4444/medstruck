# MedStruct AI Constitution

## Core Principles

### I. Offline-First & Privacy-Centric
MedStruct AI MUST operate entirely air-gapped. Zero cloud APIs, no external web requests. Patient data must never leave the local machine. This is non-negotiable for HIPAA compliance and operational security.

### II. CPU-First Local Execution
Inference must be optimized for local CPU hardware. The system MUST leverage AVX2/ARM Neon acceleration utilizing 4-bit quantized GGUF models (e.g., Qwen-2.5-3B-Instruct / Gemma-3-4B) and natively compiled `whisper.cpp`.

### III. Derived Value Feature
The system MUST NOT just extract text. It MUST actively compute clinical insights (e.g., evaluate abnormal blood metrics against standard baselines) and output a consolidated patient risk level (Low, Medium, High).

### IV. Strong Copyleft
All code MUST be protected via the GNU General Public License v3 (GPLv3) to satisfy strict open-source and hackathon constraints.

## Governance
Version: 1.0.0 | Ratified: 2026-06-28 | Last Amended: 2026-06-28
