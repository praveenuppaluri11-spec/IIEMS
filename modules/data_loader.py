# modules/data_loader.py
import pandas as pd
import os
import streamlit as st

@st.cache_data
def load_tier_data(selected_tier):
    """Loads the specific CSVs based on the tier selected in the UI."""
    
    tier_folder_map = {
        "Tier 1 - Mega (1,500+ Units)": "tier1_mega",
        "Tier 2 - Large (500-1,500 Units)": "tier2_large",
        "Tier 3 - Mid (200-500 Units)": "tier3_mid",
        "Tier 4 - Small (<200 Units)": "tier4_small"
    }
    
    folder_name = tier_folder_map.get(selected_tier, "tier2_large")
    base_path = os.path.join("data", folder_name)
    
    # Load specific community tier data
    daily_df = pd.read_csv(os.path.join(base_path, "Daily_Drilldown.csv"))
    monthly_df = pd.read_csv(os.path.join(base_path, "Monthly_Bills.csv"))
    md_df = pd.read_csv(os.path.join(base_path, "MD_Sentinel_Annual_30Min.csv"), parse_dates=['Timestamp'])
 
    # Load global IAQ telemetry
    iaq_df = pd.read_csv(os.path.join("data", "Global_IAQ_Guard_5Min.csv"))
    
    # Ensure datetime parsing for time-series charts
    monthly_df['Month'] = pd.to_datetime(monthly_df['Month'])
    md_df['Timestamp'] = pd.to_datetime(md_df['Timestamp'])
    
    return daily_df, monthly_df, md_df, iaq_df