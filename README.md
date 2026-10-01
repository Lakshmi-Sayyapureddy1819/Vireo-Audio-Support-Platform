# Vireo Audio — Support SLA Intelligence & Operations Platform

An enterprise-grade diagnostic platform built to investigate SLA breaches, evaluate historical roster attribution, audit data quality, and model zero-hire financial scenarios for Vireo Audio.

---

## 🎧 Quick Start & System Requirements

### 1. Prerequisites
- Python 3.9+ (Python 3.11 recommended)
- `pip` package manager

### 2. Installation
Clone the repository and install required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Verification Suite & Unit Tests
To run the automated verification pipeline and unit tests:
```bash
python verify_solution.py
python -m pytest
```

### 4. Launch the Interactive Dashboard
To launch the Streamlit operational platform:
```bash
streamlit run app.py
```

---

## 📊 Executive & Operational Features

1. **Executive Diagnostic & Root Cause:** Uncovers the structural origin of SLA breaches following the June 30, 2025 Indore reshuffle.
2. **Weekly Breach Report (Neha's View):** Filterable weekly tracking by week, shift, agent, team, site, and channel with dual attribution toggle.
3. **Agent Scorecards & True Attribution:** Protects team morale by separating in-shift performance from absorbed unstaffed night backlog.
4. **P&L Financial Simulator (Arjun's View):** Interactive zero-hire scenario calculator modeling SLA credit savings under Q4 hiring freeze.
5. **AI Ticket Intelligence:** Regex-based intent classification, IVR failure detection, automated PII scrubbing, and offline fallback.
6. **Data Reconciliation & Audit Suite:** Automated verification of deduplication, timezone conversions, CSAT zero cleaning, and Policy §5 double dips.

---

## 📁 Repository Structure
```text
.
├── app.py                      # Streamlit interactive application entrypoint
├── verify_solution.py          # End-to-end automated verification suite
├── requirements.txt            # Python dependencies
├── src/
│   ├── data_loader.py          # Data ingestion, deduplication, timezone & roster matching
│   ├── sla_engine.py           # SLA targets, breach evaluation & attribution engine
│   ├── financial_engine.py     # P&L calculations, cost standards & zero-hire simulator
│   ├── ai_analyzer.py          # Intent categorization, IVR failure detection & PII scrubbing
│   ├── data_quality.py         # Automated data quality audit engine
│   └── report_generator.py     # Weekly CSV & executive markdown generator
├── tests/
│   ├── test_roster.py          # Unit tests for TASK 3 roster matching logic
│   ├── test_sla.py             # Unit tests for TASK 4 & 5 SLA & attribution
│   ├── test_financial.py       # Unit tests for TASK 6 financial engine
│   └── test_data_quality.py    # Unit tests for TASK 7 data quality engine
├── docs/
│   ├── memo_to_neha_kulkarni.md# One-page non-technical executive memo
│   ├── submission-form.md      # Completed submission form
│   ├── ai_usage.md             # AI architecture & provider documentation
│   ├── prompt_evolution.md     # Prompt engineering & decision log
│   ├── scope_decisions.md      # Scope decisions & client pushback documentation
│   └── screen_recording_guide.md # 3-minute screen recording script
└── data/                       # Authoritative source data directory
```
