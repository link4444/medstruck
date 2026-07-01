# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-01
### Added
- Local VLM Extraction pipeline using Qwen3-VL (8B) and Llama 3.2 Vision (11B) models.
- Audio ingestion Python wrapper for whisper.cpp.
- UI Audio and Image uploaders with background VLM extraction.
- FTS5 Semantic Search across patients, diagnoses, medications, and notes.
- Patient Timeline Dashboard and Analytical Health Charts using Altair.
- Local GitLab Runner CI pipeline with formatting, linting, and security scans.
- `medstruct-qwen` local text model configuration using Pydantic JSON enforcement.

### Changed
- Re-architected project structure into `medstruct_ai` unified package.
- Tuned local CPU threading (N-1 cores) for heavy VLM/LLM workloads to ensure UI stability.
- Increased VLM Context Window for Qwen-VL image token size processing.

### Fixed
- Fixed module resolution bugs with `medstruct_ai` absolute imports.
