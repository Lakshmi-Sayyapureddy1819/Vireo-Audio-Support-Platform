# Scope & Architectural Decisions Log

## 1. Pushback on Naive Client Request
- **Original Client Brief:** Neha Kulkarni requested a weekly breach report by agent and shift to identify which agents/shifts are breaching most so she can reprimand underperforming agents.
- **Analytical Pushback:** Our data audit revealed that Morning agents were NOT underperforming. Their apparent 36.7% breach rate was caused by inheriting unstaffed overnight queue backlog (0 night agents following the June 30, 2025 Indore reshuffle). When handling tickets created during their own shift, Morning agents achieve an 8.3% breach rate.
- **Resolution:** Implemented a Dual-Attribution Model (Raw Helpdesk vs Operational True In-Shift) and documented the recommendation to rebalance roster hours rather than discipline agents.

---

## 2. Zero-Hire Constraint Adherence
- **Finance Constraint:** Arjun Mehta explicitly stated headcount is frozen through Q4.
- **Architectural Choice:** Rejected hiring recommendations. Formulated a Zero-Hire Roster Rebalance moving 2 existing chat agents in Indore from Day to Night rotation, cutting breach rate from 25.0% to 8.9% and saving ₹474,974/quarter at ₹0 added headcount cost.

---

## 3. Reference Code Cleanup & Hardcoding Elimination
- **Audit Findings:** The reference codebase contained hardcoded assertions and static text numbers from a previous candidate's dataset (e.g. 80.1% night breach share, ₹157,000 savings).
- **Refactoring:** Replaced all static references with dynamic pandas/numpy aggregations computed directly from `data/`.
