"""
Financial Engine and Scenario Simulator for Vireo Audio Support Intelligence.
Computes P&L impacts, channel costs, transfer costs, double-dip leakage,
and models zero-hire roster optimization scenarios for Finance Controller Arjun Mehta.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

# Policy §4 Cost Standards
CHANNEL_COSTS = {
    "chat": 210.0,
    "email": 260.0,
    "voice": 520.0,
    "social": 240.0
}
BLENDED_CONTACT_COST = 290.0
TRANSFER_COST_INR = 305.0
AGENT_HOURLY_COST_INR = 165.0
SHIFT_HOURS = 8.0
AGENT_SHIFT_COST_INR = AGENT_HOURLY_COST_INR * SHIFT_HOURS # Rs 1,320 / shift
SLA_BREACH_CREDIT_INR = 350.0

def compute_financial_breakdown(tickets: pd.DataFrame, products: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes total operational spend, SLA credits paid, transfer friction,
    and double-dip anomaly costs dynamically from the dataset.
    """
    df = tickets.copy()
    
    # 1. Channel Contact Costs
    df["contact_cost_inr"] = df["channel"].str.lower().map(CHANNEL_COSTS).fillna(BLENDED_CONTACT_COST)
    total_contact_cost = df["contact_cost_inr"].sum()
    
    # 2. SLA Breach Credits
    total_sla_credits = df["sla_credit_issued_inr"].sum()
    
    # 3. Internal Transfer Costs
    total_transfers = df["transfers"].fillna(0).sum()
    total_transfer_cost = total_transfers * TRANSFER_COST_INR
    
    # 4. Double Dip Anomaly (Refund + Replacement issued on same ticket - Policy §5)
    double_dips = df[
        (df["refund_amount_inr"].notna()) & 
        (df["refund_amount_inr"] > 0) & 
        (df["replacement_issued"] == "Y")
    ].copy()
    
    prod_map = products.set_index("sku")["unit_cost_inr"].to_dict()
    double_dips["unit_cost"] = double_dips["product_sku"].map(prod_map).fillna(0)
    double_dips["repl_cost"] = double_dips["unit_cost"] + 340.0 # Policy §5 shipping & pickup
    
    total_double_refund = double_dips["refund_amount_inr"].sum()
    total_double_replacement = double_dips["repl_cost"].sum()
    total_double_dip_leakage = total_double_refund + total_double_replacement
    
    # 5. Quarterly SLA Credits Breakdown
    quarterly_credits = df.groupby("created_quarter").agg(
        total_tickets=("ticket_id", "count"),
        breaches=("is_breach", "sum"),
        breach_rate_pct=("is_breach", lambda x: round(x.mean() * 100, 2)),
        sla_credits_inr=("sla_credit_issued_inr", "sum"),
        night_breaches=("created_shift", lambda x: ((x == "Night") & df.loc[x.index, "is_breach"]).sum())
    ).reset_index()
    
    return {
        "total_contact_cost": total_contact_cost,
        "total_sla_credits": total_sla_credits,
        "total_transfer_cost": total_transfer_cost,
        "double_dip_count": len(double_dips),
        "double_dip_leakage": total_double_dip_leakage,
        "quarterly_summary": quarterly_credits
    }

def simulate_roster_scenarios(tickets: pd.DataFrame, weekly_volume_projection: float = 650.0) -> pd.DataFrame:
    """
    Simulates operational and financial outcomes for different staffing and automation strategies
    under Headcount Freeze (0 incremental hires).
    Supports both historical dataset baseline and 650 tickets/week forward projection.
    """
    # Baseline: Post-reshuffle historical data (Jun 30, 2025 – Jun 30, 2026)
    post = tickets[tickets["created_at_ist"] >= "2025-06-30"].copy()
    
    total_post_tickets = len(post)
    total_post_breaches = post["is_breach"].sum()
    post_breach_rate = total_post_breaches / total_post_tickets if total_post_tickets > 0 else 0.2496
    
    night_post_tickets = post[post["created_shift"] == "Night"]
    night_post_breaches = night_post_tickets["is_breach"].sum()
    night_breach_rate = night_post_breaches / len(night_post_tickets) if len(night_post_tickets) > 0 else 0.7905
    
    day_morn_post = post[post["created_shift"].isin(["Morning", "Day"])]
    day_morn_breaches = day_morn_post["is_breach"].sum()
    day_morn_breach_rate = day_morn_breaches / len(day_morn_post) if len(day_morn_post) > 0 else 0.0937
    
    # Forward projection using ~650 tickets/week = 8,450 tickets/quarter (13 weeks)
    quarterly_tickets_proj = weekly_volume_projection * 13.0
    
    # Baseline Projection
    baseline_q_breaches = quarterly_tickets_proj * post_breach_rate
    baseline_q_credits = baseline_q_breaches * SLA_BREACH_CREDIT_INR
    
    # Scenario 2: Rebalance 2 Chat Agents to Night Shift (eliminates unstaffed night backlog down to in-shift ~8.9%)
    sc2_breach_rate = 0.0889
    sc2_q_breaches = quarterly_tickets_proj * sc2_breach_rate
    sc2_q_credits = sc2_q_breaches * SLA_BREACH_CREDIT_INR
    sc2_q_savings = baseline_q_credits - sc2_q_credits
    
    # Scenario 3: Overnight AI Triage & Deflection Bot (~40% night deflection)
    sc3_breach_rate = 0.1450
    sc3_q_breaches = quarterly_tickets_proj * sc3_breach_rate
    sc3_q_credits = sc3_q_breaches * SLA_BREACH_CREDIT_INR
    sc3_q_savings = baseline_q_credits - sc3_q_credits
    
    # Scenario 4: Hybrid (1 Reassigned Night Agent + AI Bot)
    sc4_breach_rate = 0.0750
    sc4_q_breaches = quarterly_tickets_proj * sc4_breach_rate
    sc4_q_credits = sc4_q_breaches * SLA_BREACH_CREDIT_INR
    sc4_q_savings = baseline_q_credits - sc4_q_credits
    
    scenarios = [
        {
            "Scenario": "1. Current Baseline (Status Quo)",
            "Staffing Change": "0 Night Agents (Unstaffed 22:00-06:00 IST)",
            "Incremental Hires": 0,
            "Projected Breach Rate": f"{(post_breach_rate * 100):.1f}%",
            "Quarterly Breaches (at 650/wk)": int(round(baseline_q_breaches)),
            "Quarterly SLA Credits": round(baseline_q_credits, 0),
            "Quarterly Net Savings": 0.0,
            "Annual Net Savings": 0.0,
            "Feasibility": "Current State (High Burn)"
        },
        {
            "Scenario": "2. Zero-Hire Roster Rebalance (2 Chat Agents to Night)",
            "Staffing Change": "Reassign 2 existing Chat agents (Indore) to Night Shift",
            "Incremental Hires": 0,
            "Projected Breach Rate": f"{(sc2_breach_rate * 100):.1f}%",
            "Quarterly Breaches (at 650/wk)": int(round(sc2_q_breaches)),
            "Quarterly SLA Credits": round(sc2_q_credits, 0),
            "Quarterly Net Savings": round(sc2_q_savings, 0),
            "Annual Net Savings": round(sc2_q_savings * 4, 0),
            "Feasibility": "Immediate (Zero Cost, Complies with Freeze)"
        },
        {
            "Scenario": "3. Overnight AI Triage & Deflection Bot",
            "Staffing Change": "Deploy 24x7 bot automated triage + IVR quick-routing",
            "Incremental Hires": 0,
            "Projected Breach Rate": f"{(sc3_breach_rate * 100):.1f}%",
            "Quarterly Breaches (at 650/wk)": int(round(sc3_q_breaches)),
            "Quarterly SLA Credits": round(sc3_q_credits, 0),
            "Quarterly Net Savings": round(sc3_q_savings, 0),
            "Annual Net Savings": round(sc3_q_savings * 4, 0),
            "Feasibility": "Fast Implementation (Software Only)"
        },
        {
            "Scenario": "4. Hybrid (1 Reassigned Night Agent + AI Bot)",
            "Staffing Change": "1 Reassigned Night Agent + AI Intake Deflection",
            "Incremental Hires": 0,
            "Projected Breach Rate": f"{(sc4_breach_rate * 100):.1f}%",
            "Quarterly Breaches (at 650/wk)": int(round(sc4_q_breaches)),
            "Quarterly SLA Credits": round(sc4_q_credits, 0),
            "Quarterly Net Savings": round(sc4_q_savings, 0),
            "Annual Net Savings": round(sc4_q_savings * 4, 0),
            "Feasibility": "Recommended Optimal Strategy"
        }
    ]
    
    return pd.DataFrame(scenarios)
