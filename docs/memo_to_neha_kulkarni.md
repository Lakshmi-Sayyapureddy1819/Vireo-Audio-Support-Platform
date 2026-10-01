# MEMORANDUM

**TO:** Neha Kulkarni, Support Operations Manager  
**FROM:** AI Operations & Support Intelligence Lead  
**DATE:** October 1, 2026  
**SUBJECT:** Operational SLA Breach Investigation, Agent Attribution Analysis & Zero-Hire Action Plan  

---

### Executive Summary

You requested a weekly breach report by agent and shift to identify which teams are breaching SLA targets most severely, enabling targeted operational conversations.

Our audit of all **11,200 deduplicated support tickets** (Jan 2025 – Jun 2026) reveals a critical operational insight: **the apparent Morning Shift breach crisis is a structural scheduling artifact, not an agent performance failure.**

Standard helpdesk exports attribute SLA breaches to whichever agent resolves the ticket. However, following the **June 30, 2025 Indore reshuffle**, the Indore Night Shift (22:00–06:00 IST) was left completely unstaffed (0 agents), while customer policy continued promising 24x7 Chat with a 15-minute response SLA. Consequently, overnight tickets sit in queue for up to 8 hours until Morning agents clock in at 06:00 IST. When Morning agents resolve these pre-breached tickets, standard software falsely blames them.

---

### Key Operational Findings

1. **The 'Wall of Red' is Unstaffed Night Queue Accumulation:**
   - Prior to July 2025, overall breach rates were healthy at **9.2%**.
   - Post-reshuffle, night-created tickets suffered a **79.1% breach rate** (1,581 breaches out of 2,000 night tickets), accounting for **70.8% of all SLA credit liabilities**.

2. **Fair Agent Attribution (True In-Shift Performance):**
   - When evaluating tickets submitted *during* their working shift, **Morning Shift agents achieve an 8.3% breach rate**, outperforming the Day Shift (8.9%).
   - Reprimanding Morning agents penalizes top performers for clearing unstaffed structural backlog.

3. **Weekly Breach Report Delivery:**
   - We have deployed an interactive, filterable Weekly Breach Report tool allowing you to view operational performance by **week, shift, agent, team, site, and channel**.
   - The tool includes a toggle between **Naive Helpdesk View** and **True In-Shift View** to protect team morale while pinpointing genuine coaching needs.

---

### Quantified Business Goal & Zero-Hire Action Plan

Under Finance Controller Arjun Mehta’s headcount freeze, hiring is off the table. We recommend a **Zero-Hire Roster Rebalance**:

* **Action:** Reassign **2 Chat agents** from the Indore Day rotation back to the Indore Night Shift (22:00–06:00 IST) and deploy automated off-hours bot triage for basic tracking/pairing inquiries.
* **Goal:** Reduce quarterly SLA breach rate from **25.0% to ~8.9%**, eliminating unstaffed queue accumulation.
* **Financial Impact:** Reduces quarterly SLA credit payout from **₹738,192** to **₹263,218**, saving **₹474,974 per quarter** (~₹1.90 Million annually) with **₹0 incremental salary spend**.

---

### Recommended Next Steps

1. **Adopt Operational Attribution Reporting:** Shift standard management reviews from resolving-agent blame to creation-shift attribution.
2. **Execute Roster Rebalance:** Coordinate with Indore team leads to reinstate 2-agent overnight chat coverage immediately.
3. **Audit Double-Dip Anomalies:** Finance to audit 6 flagged orders (₹22,775 value) where both refund and replacement were issued contrary to Policy §5.
