"""
SLA Engine for Vireo Audio Support Intelligence.
Computes service level targets, breach flags, attribution models (Raw Helpdesk vs Operational True In-Shift),
and generates agent scorecards, weekly breach reports, and multi-dimensional breakdowns.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional

# Policy §3 SLA targets in minutes
SLA_TARGETS = {
    "chat": 15,
    "voice": 120,    # 2 hours
    "social": 240,   # 4 hours
    "email": 480     # 8 hours
}

# Policy §3 SLA Breach Credit standard
SLA_BREACH_CREDIT_INR = 350.0

def evaluate_sla(tickets: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates SLA compliance for all tickets, assigning SLA targets,
    breach flags, breach magnitude, and dual attribution flags.
    """
    df = tickets.copy()
    
    # 1. Map SLA Target
    df["sla_target_min"] = df["channel"].str.lower().map(SLA_TARGETS)
    
    # 2. SLA Breach Flag
    df["is_breach"] = (df["frt_minutes"] > df["sla_target_min"]).fillna(False)
    
    # 3. Breach Delay (minutes over target)
    df["breach_delay_min"] = np.maximum(0, df["frt_minutes"] - df["sla_target_min"])
    
    # 4. Attribution Classification (Fair Operational Attribution vs Raw Helpdesk)
    # Structural (Night Queue Backlog) vs Operational (In-Shift Delay) vs Spillover
    def classify_attribution(row):
        if not row["is_breach"]:
            return "Compliant"
        if row["created_shift"] == "Night":
            return "Structural (Unstaffed Night Backlog)"
        elif row["created_shift"] != row["response_shift"]:
            return "Queue Carryover (Cross-Shift Spillover)"
        else:
            return "Operational (In-Shift Delay)"
            
    df["breach_category"] = df.apply(classify_attribution, axis=1)
    
    # 5. Financial Breach Credit Eligible Flag
    # Credit is issued upon ticket resolution or closure
    df["sla_credit_issued_inr"] = np.where(
        df["is_breach"] & df["status"].isin(["resolved", "closed"]),
        SLA_BREACH_CREDIT_INR,
        0.0
    )
    
    return df

def generate_shift_summary(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates a comparison between Creation Shift (True Root Cause)
    and Agent Shift (Naive Helpdesk Attribution).
    """
    # Creation Shift Summary (Where breaches actually happen)
    creation_summary = df.groupby("created_shift").agg(
        total_tickets=("ticket_id", "count"),
        total_breaches=("is_breach", "sum"),
        breach_rate=("is_breach", lambda x: round(x.mean() * 100, 2)),
        sla_credits_inr=("sla_credit_issued_inr", "sum"),
        median_frt_min=("frt_minutes", "median")
    ).reset_index()
    
    # Agent Shift Summary (Where helpdesk naively blames)
    agent_summary = df.groupby("agent_shift").agg(
        total_tickets=("ticket_id", "count"),
        total_breaches=("is_breach", "sum"),
        breach_rate=("is_breach", lambda x: round(x.mean() * 100, 2)),
        sla_credits_inr=("sla_credit_issued_inr", "sum")
    ).reset_index()
    
    return creation_summary, agent_summary

def generate_agent_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a granular agent scorecard distinguishing between:
    - Naive Breach Rate (Total resolved breaches / Total tickets)
    - True In-Shift Breach Rate (Breaches on tickets created during agent's shift)
    - Unfair Backlog Absorbed (Breaches inherited from unstaffed night queue)
    """
    scorecards = []
    
    for aid, group in df.groupby("agent_id"):
        name = group["agent_name"].iloc[0]
        shift = group["agent_shift"].iloc[0]
        site = group["agent_site"].iloc[0]
        team = group["agent_team"].iloc[0]
        tier = group["agent_tier"].iloc[0]
        
        total_resolved = len(group)
        total_breaches = group["is_breach"].sum()
        naive_rate = (total_breaches / total_resolved * 100) if total_resolved > 0 else 0.0
        
        # Tickets created during the agent's assigned shift
        own_shift_tickets = group[group["created_shift"] == shift]
        own_shift_count = len(own_shift_tickets)
        own_shift_breaches = own_shift_tickets["is_breach"].sum()
        true_shift_rate = (own_shift_breaches / own_shift_count * 100) if own_shift_count > 0 else 0.0
        
        # Night backlog tickets absorbed
        night_backlog_tickets = group[group["created_shift"] == "Night"]
        night_backlog_breaches = night_backlog_tickets["is_breach"].sum()
        
        avg_csat = group["csat_score_cleaned"].mean()
        
        scorecards.append({
            "agent_id": aid,
            "name": name,
            "site": site,
            "team": team,
            "shift": shift,
            "tier": tier,
            "tickets_resolved": total_resolved,
            "naive_breaches": total_breaches,
            "naive_breach_rate_pct": round(naive_rate, 2),
            "in_shift_tickets": own_shift_count,
            "in_shift_breaches": own_shift_breaches,
            "true_in_shift_breach_rate_pct": round(true_shift_rate, 2),
            "night_breaches_absorbed": night_backlog_breaches,
            "avg_csat": round(avg_csat, 2) if pd.notna(avg_csat) else None
        })
        
    res = pd.DataFrame(scorecards)
    return res.sort_values(by="naive_breaches", ascending=False).reset_index(drop=True)

def generate_weekly_breach_report(
    df: pd.DataFrame, 
    week: Optional[str] = None,
    shift: Optional[str] = None,
    agent_id: Optional[str] = None,
    team: Optional[str] = None,
    site: Optional[str] = None,
    channel: Optional[str] = None
) -> pd.DataFrame:
    """
    Produces the weekly breach report requested by Neha Kulkarni,
    filterable by week, shift, agent, team, site, and channel.
    """
    filtered = df.copy()
    if week and week != "All":
        filtered = filtered[filtered["created_week"] == week]
    if shift and shift != "All":
        filtered = filtered[filtered["agent_shift"] == shift]
    if agent_id and agent_id != "All":
        filtered = filtered[filtered["agent_id"] == agent_id]
    if team and team != "All":
        filtered = filtered[filtered["agent_team"] == team]
    if site and site != "All":
        filtered = filtered[filtered["agent_site"] == site]
    if channel and channel != "All":
        filtered = filtered[filtered["channel"].str.lower() == channel.lower()]
        
    if len(filtered) == 0:
        return pd.DataFrame(columns=[
            "created_week", "agent_shift", "agent_id", "agent_name", "agent_site", "agent_team",
            "total_tickets", "total_breaches", "naive_breach_rate_pct", "night_backlog_breaches",
            "in_shift_breaches", "true_in_shift_breach_rate_pct", "total_credits_inr", "avg_csat"
        ])
    
    weekly = filtered.groupby(["created_week", "agent_shift", "agent_id", "agent_name", "agent_site", "agent_team"]).agg(
        total_tickets=("ticket_id", "count"),
        total_breaches=("is_breach", "sum"),
        naive_breach_rate_pct=("is_breach", lambda x: round(x.mean() * 100, 2)),
        night_backlog_breaches=("breach_category", lambda x: (x == "Structural (Unstaffed Night Backlog)").sum()),
        in_shift_breaches=("breach_category", lambda x: (x == "Operational (In-Shift Delay)").sum()),
        total_credits_inr=("sla_credit_issued_inr", "sum"),
        avg_csat=("csat_score_cleaned", lambda x: round(x.dropna().mean(), 2) if len(x.dropna()) > 0 else np.nan)
    ).reset_index()
    
    weekly["true_in_shift_breach_rate_pct"] = np.where(
        weekly["total_tickets"] > 0,
        round((weekly["in_shift_breaches"] / weekly["total_tickets"]) * 100, 2),
        0.0
    )
    
    return weekly.sort_values(by=["created_week", "total_breaches"], ascending=[False, False])
