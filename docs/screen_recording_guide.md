# 3-Minute Screen Recording Guide & Script

**Total Duration:** 2 minutes 50 seconds (<= 3 minutes)  
**Speaker:** Candidate / AI Lead  

---

### [0:00 - 0:35] Part 1: Problem Statement & Client Pushback
* **Screen:** Open `docs/memo_to_neha_kulkarni.md` and `app.py` Executive Diagnostic tab.
* **Script:**
  > "Hi Neha. You requested a weekly breach report by agent and shift to address high SLA breach rates. However, our initial audit of all 11,200 deduplicated tickets revealed that blaming Morning Shift agents for a 36.7% breach rate is unfair. On June 30, 2025, the Indore night shift was decommissioned, leaving 0 agents on duty overnight while 24x7 Chat remained active. Morning agents were inheriting 8 hours of unstaffed queue backlog. When evaluating tickets created during their own shift, Morning agents achieve an excellent 8.3% breach rate."

---

### [0:35 - 1:20] Part 2: Working AI Tool & Weekly Breach Report Demo
* **Screen:** Switch to Streamlit Dashboard -> `📋 Weekly Breach Report (Neha's View)` and `👥 Agent Scorecards`.
* **Action:** Demonstrate week, shift, team, and channel dropdown filters. Toggle between **Naive View** and **True In-Shift View**.
* **Script:**
  > "Here is the working AI-assisted diagnostic platform. Managers can filter weekly breach performance across week, shift, team, site, and channel. Toggling to 'True In-Shift View' separates unstaffed overnight backlog from true in-shift performance, protecting team morale while targeting coaching where it actually matters."

---

### [1:20 - 2:05] Part 3: Quantified Business Goal & P&L Simulator
* **Screen:** Switch to `💰 P&L Financial Simulator (Arjun's View)`.
* **Action:** Adjust the interactive slider to reassign 2 Chat agents to Night shift.
* **Script:**
  > "Respecting Arjun Mehta's Q4 headcount freeze, we modeled a Zero-Hire Roster Rebalance. Reassigning 2 existing Chat agents to the Night shift reduces quarterly breach rates from 25.0% to 8.9%. At a forward projection of 650 tickets/week, this cuts SLA credit liability from ₹738,192 to ₹263,218, delivering net P&L savings of ₹474,974 per quarter with ₹0 incremental salary spend."

---

### [2:05 - 2:50] Part 4: Code Verification, AI Layer & Discarded Work
* **Screen:** Terminal running `python verify_solution.py` and `python -m pytest`, then showing `src/ai_analyzer.py`.
* **Script:**
  > "All logic is fully testable: our verification suite passes 100% of invariant and data quality tests across all 11,200 tickets. For the AI layer, we discarded per-ticket LLM classification because 11,200 API calls would be slow, costly, and risk PII leakage. Instead, we built an offline regex engine with PII scrubbing and offline fallback, using bounded LLM batch calls only for executive summarization."
