# Implementation Plan: MedStruct AI Core Engine

**Branch**: `main` | **Date**: 2026-06-28 | **Spec**: specs/core/spec.md

**Input**: Feature specification from `specs/core/spec.md`

## Summary

MedStruct AI is an offline-first, CPU-optimized clinical intelligence system designed to ingest unstructured medical inputs and transform them into highly structured, validated relational datasets with derived clinical insights.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Streamlit, Pydantic v2, Ollama (python client)

**Storage**: SQLite3

**Testing**: pytest

**Target Platform**: Local PC/Server (macOS/Linux)

**Project Type**: Web Dashboard + Local Inference Pipeline

**Performance Goals**: Sub-30 second inference per document

**Constraints**: MUST be air-gapped (no external APIs). MUST be CPU optimized via AVX2.

**Scale/Scope**: Single local user clinic dashboard.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Offline-First**: Validated. All tools (SQLite, whisper.cpp, Ollama) are local.
- **CPU-First**: Validated. whisper.cpp and llama.cpp/Ollama run locally on CPU.
- **Derived Value**: Validated. Business logic will compute High/Med/Low risk based on extracted values.
- **Copyleft**: GPLv3 applied.

## Project Structure

### Documentation (this feature)

```text
specs/core/
├── spec.md              
├── plan.md              # This file
└── tasks.md             
```

### Source Code (repository root)

```text
medstruct_ai/
├── app/
│   ├── main.py          # Streamlit UI
│   └── components/      # UI pieces
├── core/
│   ├── schemas.py       # Pydantic v2
│   ├── inference.py     # Ollama wrappers
│   ├── audio/           # whisper.cpp integration
│   └── logic.py         # Risk derivation logic
├── db/
│   ├── database.py      # SQLite connection & ORM
│   └── queries.py
├── scripts/
│   ├── setup_env.sh
│   └── init_db.py
└── models/              # Local GGUF cache
```

**Structure Decision**: A modular monolith isolating Streamlit (app) from business logic (core) and persistence (db), allowing for easy local testing.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| C++ Compilation | CPU Audio | Pure python whisper implementations are too slow/memory heavy for pure CPU. |
