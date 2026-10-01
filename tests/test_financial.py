"""
Unit tests for Financial Engine & Scenario Simulator.
"""

import pytest
import pandas as pd
from src.data_loader import load_and_preprocess_data
from src.sla_engine import evaluate_sla
from src.financial_engine import compute_financial_breakdown, simulate_roster_scenarios

def test_financial_breakdown_and_scenarios():
    data = load_and_preprocess_data(".")
    tickets_evaluated = evaluate_sla(data["tickets"])
    fin = compute_financial_breakdown(tickets_evaluated, data["products"])
    
    assert fin["total_sla_credits"] == 812000.0
    assert fin["double_dip_count"] == 6
    assert fin["double_dip_leakage"] == 22775.0
    assert fin["total_transfer_cost"] == 1129 * 305.0
    
    scenarios = simulate_roster_scenarios(tickets_evaluated, weekly_volume_projection=650.0)
    assert len(scenarios) == 4
    assert scenarios.iloc[0]["Quarterly Net Savings"] == 0.0
    assert scenarios.iloc[1]["Quarterly Net Savings"] > 0.0
