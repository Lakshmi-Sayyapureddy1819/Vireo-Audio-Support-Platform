"""
Unit tests for TASK 7 — Data Quality & Audit Engine.
"""

import pytest
from src.data_quality import run_data_quality_audit

def test_data_quality_audit():
    res = run_data_quality_audit(".")
    assert res["raw_total_rows"] == 11816
    assert res["clean_total_rows"] == 11200
    assert res["duplicate_ticket_pairs"] == 616
    assert res["invalid_created_dates"] == 0
    assert res["impossible_frt_count"] == 0
    assert res["impossible_ht_count"] == 0
    assert res["invalid_channel_count"] == 0
    assert res["missing_agent_ids"] == 0
    assert res["unmatched_agent_ids"] == 0
    assert res["double_dip_count"] == 6
