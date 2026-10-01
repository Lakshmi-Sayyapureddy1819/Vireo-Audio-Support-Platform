"""
Data Loader and Preprocessing Module for Vireo Audio Support Intelligence.
Handles data ingestion, deduplication, UTC to IST timestamp conversion,
and dynamic historical agent roster mapping across date windows.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

def match_agent_roster(agent_id: str, ticket_date: Any, agents_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Deterministically matches an agent_id and ticket_date against historical roster windows.
    Handles boundary dates, shift changes, missing to_date, overlapping assignments,
    and unmatched agent IDs.
    """
    agent_rows = agents_df[agents_df["agent_id"] == agent_id]
    
    if len(agent_rows) == 0:
        return {
            "agent_name": "Unassigned",
            "agent_site": "Unknown",
            "agent_team": "Unknown",
            "agent_shift": "Unknown",
            "agent_tier": np.nan
        }
    
    # Filter where from_date <= ticket_date <= to_date
    if isinstance(ticket_date, (pd.Timestamp, pd.DatetimeIndex)):
        t_date = ticket_date.date()
    elif isinstance(ticket_date, str):
        t_date = pd.to_datetime(ticket_date).date()
    else:
        t_date = ticket_date
        
    matches = agent_rows[
        (agent_rows["from_date_dt"] <= t_date) &
        (agent_rows["to_date_dt"] >= t_date)
    ]
    
    if len(matches) == 0:
        # Fallback to closest or most recent assignment if unassigned date window
        matches = agent_rows.sort_values(by="from_date_dt", ascending=False)
        
    # If multiple matches (overlapping assignments), pick the most recent assignment by from_date
    selected = matches.sort_values(by="from_date_dt", ascending=False).iloc[0]
    
    return {
        "agent_name": selected["name"],
        "agent_site": selected["site"],
        "agent_team": selected["team"],
        "agent_shift": selected["shift"],
        "agent_tier": selected["tier"]
    }

def load_and_preprocess_data(base_path: str = ".") -> Dict[str, pd.DataFrame]:
    """
    Loads all datasets, handles flexible CSV filenames (agent.csv/agents.csv, customer.csv/customers.csv),
    deduplicates tickets, normalizes timezones from UTC to IST, maps roster assignments dynamically,
    and returns a clean dictionary of DataFrames.
    """
    base_dir = Path(base_path)
    if (base_dir / "data").exists():
        data_dir = base_dir / "data"
    else:
        data_dir = base_dir
    
    # Flexible filename checking
    agent_file = data_dir / "agents.csv" if (data_dir / "agents.csv").exists() else data_dir / "agent.csv"
    customer_file = data_dir / "customers.csv" if (data_dir / "customers.csv").exists() else data_dir / "customer.csv"
    
    # 1. Load CSVs
    tickets_raw = pd.read_csv(data_dir / "tickets.csv")
    agents_raw = pd.read_csv(agent_file)
    orders_raw = pd.read_csv(data_dir / "orders.csv")
    customers_raw = pd.read_csv(customer_file)
    products_raw = pd.read_csv(data_dir / "products.csv")
    
    # 2. Deduplicate tickets (Favor 'helpdesk' source over 'legacy_fd')
    tickets_sorted = tickets_raw.sort_values(by=["ticket_id", "source_system"], ascending=[True, True])
    tickets_dedup = tickets_sorted.drop_duplicates(subset=["ticket_id"], keep="first").reset_index(drop=True)
    
    # 3. Clean CSAT: Policy §8 states blank means no response and must be excluded, not treated as 0.
    tickets_dedup["csat_score_cleaned"] = tickets_dedup["csat_score"].replace(0.0, np.nan)
    
    # 4. Convert timestamps from UTC (API export) to IST (Operating hours)
    for col in ["created_at", "first_response_at", "resolved_at"]:
        tickets_dedup[col + "_utc"] = pd.to_datetime(tickets_dedup[col], errors="coerce", utc=True)
        tickets_dedup[col + "_ist"] = tickets_dedup[col + "_utc"].dt.tz_convert("Asia/Kolkata")
    
    # 5. Calculate First Response Time (FRT) and Handle Time (HT) in minutes
    tickets_dedup["frt_minutes"] = (
        tickets_dedup["first_response_at_utc"] - tickets_dedup["created_at_utc"]
    ).dt.total_seconds() / 60.0
    
    tickets_dedup["handle_time_minutes"] = (
        tickets_dedup["resolved_at_utc"] - tickets_dedup["first_response_at_utc"]
    ).dt.total_seconds() / 60.0
    
    # 6. Shift Definitions (IST):
    # Morning: 06:00 - 14:00 IST
    # Day:     14:00 - 22:00 IST
    # Night:   22:00 - 06:00 IST
    def get_ist_shift(dt):
        if pd.isna(dt):
            return np.nan
        h = dt.hour
        if 6 <= h < 14:
            return "Morning"
        elif 14 <= h < 22:
            return "Day"
        else:
            return "Night"
            
    tickets_dedup["created_shift"] = tickets_dedup["created_at_ist"].apply(get_ist_shift)
    tickets_dedup["response_shift"] = tickets_dedup["first_response_at_ist"].apply(get_ist_shift)
    tickets_dedup["resolved_shift"] = tickets_dedup["resolved_at_ist"].apply(get_ist_shift)
    
    # 7. Dynamic Agent Roster Matching
    agents_clean = agents_raw.copy()
    agents_clean["from_date_dt"] = pd.to_datetime(agents_clean["from_date"]).dt.date
    agents_clean["to_date_dt"] = pd.to_datetime(agents_clean["to_date"]).dt.date.fillna(pd.to_datetime("2099-12-31").date())
    
    # Map each ticket to agent roster assignment based on ticket creation / response date
    tickets_dedup["ticket_date"] = tickets_dedup["created_at_ist"].dt.date
    
    agent_records = []
    for idx, row in tickets_dedup.iterrows():
        aid = row["agent_id"]
        t_date = row["ticket_date"]
        matched_info = match_agent_roster(aid, t_date, agents_clean)
        agent_records.append(matched_info)
            
    agent_df = pd.DataFrame(agent_records)
    tickets_final = pd.concat([tickets_dedup, agent_df], axis=1)
    
    # 8. Add Week, Month, and Quarter helpers (in IST)
    created_naive = tickets_final["created_at_ist"].dt.tz_localize(None)
    tickets_final["created_week"] = created_naive.dt.to_period("W-SUN").astype(str)
    tickets_final["created_month"] = created_naive.dt.to_period("M").astype(str)
    tickets_final["created_quarter"] = created_naive.dt.to_period("Q").astype(str)
    
    return {
        "tickets": tickets_final,
        "agents": agents_clean,
        "orders": orders_raw,
        "customers": customers_raw,
        "products": products_raw
    }

if __name__ == "__main__":
    data = load_and_preprocess_data(".")
    print(f"Data successfully loaded. Clean tickets count: {len(data['tickets'])}")
