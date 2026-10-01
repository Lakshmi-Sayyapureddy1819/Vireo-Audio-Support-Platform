# Prompt Evolution & Engineering Log

## 1. Initial Exploration Prompts
- **Goal:** Analyze raw customer messages for intent classification and IVR failure detection.
- **Initial Iteration:** Standard zero-shot LLM prompt asking to classify every ticket individually.
- **Issues Encountered:** High latency (11,200 API calls needed), high cost, PII leakage risks, potential non-deterministic classification.
- **Decision:** Shifted to a regex-based deterministic engine for ticket classification, reserving LLM prompting strictly for batch executive summaries.

---

## 2. Refined Batch Summarization Prompt
- **System Prompt:**
  ```text
  You are an expert Support Operations AI Analyst for Vireo Audio.
  Summarize top operational friction points and customer dissatisfaction themes from the provided intent breakdown table.
  Do not mention PII. Keep output concise, structured, and actionable for C-level executives.
  ```
- **Outcome:** Produced consistent, high-impact executive insights with 0 PII exposure and deterministic fallback capability.
