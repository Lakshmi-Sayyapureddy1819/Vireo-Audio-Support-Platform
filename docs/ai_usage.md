# AI Usage & Architecture Documentation

## 1. AI Architecture Overview
The platform employs a **bounded, privacy-focused, dual-mode AI architecture**:
- **Deterministic Pattern Engine (Primary):** Regular expressions and heuristic pattern matching handle core intent classification, IVR failure detection, and PII anonymization offline without API latency, cost, or external network dependencies.
- **Optional External LLM Layer (Secondary):** Integrated with Gemini API for batch executive theme extraction and weekly qualitative narrative generation when API keys are configured.

---

## 2. PII Privacy Protection
Before any text is passed to an optional external model, all customer messages undergo strict automated PII scrubbing:
- **Email addresses:** Replaced with `[REDACTED_EMAIL]`
- **Phone numbers:** Replaced with `[REDACTED_PHONE]`
- **Customer names:** Replaced with `[REDACTED_NAME]`

---

## 3. Operational Model Details
- **Provider:** Google Gemini API (or Deterministic Heuristic Engine offline)
- **Model Name:** `gemini-1.5-flash` / `gemini-3.6-flash`
- **Purpose:** Semantic intent classification, IVR failure filtering, and executive summary generation.
- **Batching Strategy:** 1 call per weekly executive report (bounded batch execution). No per-ticket LLM calls to keep costs < $0.01 per run.
- **Estimated Cost:** $0.00 (Offline Mode) / ~$0.0005 per batch run (Online Mode).
- **Fallback Mechanism:** Full deterministic regex fallback (`src/ai_analyzer.py`) ensuring 100% functionality on air-gapped or offline systems.
