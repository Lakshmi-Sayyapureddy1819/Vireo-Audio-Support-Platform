"""
Unit tests for TASK 4 & TASK 5 — SLA Calculation & Attribution Model.
"""

import pandas as pd
import numpy as np
import pytest
from src.sla_engine import evaluate_sla, generate_weekly_breach_report

def test_sla_targets_and_breach_evaluation():
    # Sample ticket data with different channels and FRTs
    df_sample = pd.DataFrame([
        {"ticket_id": "T1", "channel": "chat", "frt_minutes": 10.0, "status": "resolved", "created_shift": "Day", "response_shift": "Day"}, # Compliant chat (10 min <= 15 min)
        {"ticket_id": "T2", "channel": "chat", "frt_minutes": 25.0, "status": "resolved", "created_shift": "Day", "response_shift": "Day"}, # Breached chat (25 min > 15 min)
        {"ticket_id": "T3", "channel": "voice", "frt_minutes": 110.0, "status": "resolved", "created_shift": "Morning", "response_shift": "Morning"}, # Compliant voice (110 min <= 120 min)
        {"ticket_id": "T4", "channel": "voice", "frt_minutes": 150.0, "status": "resolved", "created_shift": "Night", "response_shift": "Morning"}, # Night unstaffed breach
        {"ticket_id": "T5", "channel": "email", "frt_minutes": 500.0, "status": "closed", "created_shift": "Day", "response_shift": "Day"}, # Breached email (500 min > 480 min)
    ])
    
    eval_df = evaluate_sla(df_sample)
    
    # Check targets
    assert eval_df.loc[eval_df["ticket_id"] == "T1", "sla_target_min"].values[0] == 15
    assert eval_df.loc[eval_df["ticket_id"] == "T3", "sla_target_min"].values[0] == 120
    assert eval_df.loc[eval_df["ticket_id"] == "T5", "sla_target_min"].values[0] == 480
    
    # Check breach flags
    assert not eval_df.loc[eval_df["ticket_id"] == "T1", "is_breach"].values[0]
    assert eval_df.loc[eval_df["ticket_id"] == "T2", "is_breach"].values[0]
    assert not eval_df.loc[eval_df["ticket_id"] == "T3", "is_breach"].values[0]
    assert eval_df.loc[eval_df["ticket_id"] == "T4", "is_breach"].values[0]
    assert eval_df.loc[eval_df["ticket_id"] == "T5", "is_breach"].values[0]
    
    # Check attribution categories
    assert eval_df.loc[eval_df["ticket_id"] == "T2", "breach_category"].values[0] == "Operational (In-Shift Delay)"
    assert eval_df.loc[eval_df["ticket_id"] == "T4", "breach_category"].values[0] == "Structural (Unstaffed Night Backlog)"
    
    # Check SLA credits
    assert eval_df.loc[eval_df["ticket_id"] == "T2", "sla_credit_issued_inr"].values[0] == 350.0
    assert eval_df.loc[eval_df["ticket_id"] == "T1", "sla_credit_issued_inr"].values[0] == 0.0

def test_weekly_report_filtering():
    from src.data_loader import load_and_preprocess_data
    data = load_and_preprocess_data(".")
    tickets_evaluated = evaluate_sla(data["tickets"])
    
    # Test filter by week and channel
    report_all = generate_weekly_breach_report(tickets_evaluated)
    assert len(report_all) > 0
    
    first_week = report_all["created_week"].iloc[0]
    report_filtered = generate_weekly_breach_report(tickets_evaluated, week=first_week, channel="chat")
    assert (report_filtered["created_week"] == first_week).all()
