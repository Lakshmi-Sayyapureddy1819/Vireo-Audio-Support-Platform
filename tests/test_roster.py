"""
Unit tests for TASK 3 — Critical Agent Roster Logic.
Tests:
1. Boundary dates (from_date and to_date exact match)
2. Shift changes (e.g. Tarun Mishra A3002 moving from Night to Day on 2025-06-30)
3. Missing to_date (open-ended assignment filled with 2099-12-31)
4. Overlapping assignments (handling multiple matches gracefully)
5. Unmatched assignments (fallback for unknown agent IDs)
"""

import pandas as pd
import numpy as np
import pytest
from src.data_loader import match_agent_roster

@pytest.fixture
def sample_agents():
    data = [
        # A3002: Tarun Mishra changes shift on 2025-06-30
        {"agent_id": "A3002", "name": "Tarun Mishra", "site": "Indore", "team": "Chat Frontline", "shift": "Night", "tier": 1, "from_date": "2023-02-12", "to_date": "2025-06-29"},
        {"agent_id": "A3002", "name": "Tarun Mishra", "site": "Indore", "team": "Chat Frontline", "shift": "Day", "tier": 1, "from_date": "2025-06-30", "to_date": None},
        # A3005: Open ended assignment
        {"agent_id": "A3005", "name": "Sameer Joshi", "site": "Bengaluru", "team": "Chat Frontline", "shift": "Morning", "tier": 1, "from_date": "2021-07-28", "to_date": None},
        # Overlapping test agent
        {"agent_id": "A9999", "name": "Overlap Agent", "site": "Bengaluru", "team": "Chat Frontline", "shift": "Morning", "tier": 1, "from_date": "2025-01-01", "to_date": "2025-12-31"},
        {"agent_id": "A9999", "name": "Overlap Agent", "site": "Bengaluru", "team": "Chat Frontline", "shift": "Night", "tier": 1, "from_date": "2025-06-01", "to_date": "2025-08-31"},
    ]
    df = pd.DataFrame(data)
    df["from_date_dt"] = pd.to_datetime(df["from_date"]).dt.date
    df["to_date_dt"] = pd.to_datetime(df["to_date"]).dt.date.fillna(pd.to_datetime("2099-12-31").date())
    return df

def test_shift_change_and_boundaries(sample_agents):
    # Before shift change (2025-06-29) -> Night
    res_before = match_agent_roster("A3002", pd.to_datetime("2025-06-29"), sample_agents)
    assert res_before["agent_shift"] == "Night"
    assert res_before["agent_name"] == "Tarun Mishra"
    
    # On boundary date of shift change (2025-06-30) -> Day
    res_after = match_agent_roster("A3002", pd.to_datetime("2025-06-30"), sample_agents)
    assert res_after["agent_shift"] == "Day"
    assert res_after["agent_name"] == "Tarun Mishra"

def test_missing_to_date(sample_agents):
    # Ticket in 2026 for agent with missing to_date
    res = match_agent_roster("A3005", pd.to_datetime("2026-05-15"), sample_agents)
    assert res["agent_shift"] == "Morning"
    assert res["agent_site"] == "Bengaluru"

def test_overlapping_assignments(sample_agents):
    # Ticket during overlapping period (2025-07-01) -> selects most recent assignment by from_date
    res = match_agent_roster("A9999", pd.to_datetime("2025-07-01"), sample_agents)
    assert res["agent_shift"] == "Night"

def test_unmatched_agent(sample_agents):
    # Non-existent agent_id
    res = match_agent_roster("UNKNOWN_99", pd.to_datetime("2025-05-01"), sample_agents)
    assert res["agent_name"] == "Unassigned"
    assert res["agent_site"] == "Unknown"
