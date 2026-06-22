import pandas as pd
import numpy as np
import os

# Tier-specific multipliers (Updated for aggressive 68% - 78% Summer Peaks)
TIERS = {
    "tier1_mega": {"scale": 2.2, "cmd_kva": 4000, "summer_kwh_mult": 1.8, "summer_md_mult": 1.7, "min_pf": 0.94}, 
    "tier2_large": {"scale": 1.1, "cmd_kva": 1400, "summer_kwh_mult": 1.9, "summer_md_mult": 1.75, "min_pf": 0.93}, 
    "tier3_mid": {"scale": 0.8, "cmd_kva": 900, "summer_kwh_mult": 1.7, "summer_md_mult": 1.6, "min_pf": 0.95},   
    "tier4_small": {"scale": 0.45, "cmd_kva": 600, "summer_kwh_mult": 1.6, "summer_md_mult": 1.55, "min_pf": 0.96}  
}

BASE_WINTER_KWH_DAY = 7000
START_DATE = "2025-06-01"
END_DATE = "2026-05-31"

def generate_daily_drilldown(config):
    dates = pd.date_range(START_DATE, END_DATE, freq='D')
    months = dates.month
    
    season_curve = np.where((months >= 3) & (months <= 5), config["summer_kwh_mult"], 1.0)
    total_kwh = BASE_WINTER_KWH_DAY * config["scale"] * season_curve * np.random.normal(1.0, 0.05, len(dates))
    
    df = pd.DataFrame({'Date': dates})
    df['Total_kWh'] = np.round(total_kwh, 2)
    df['Raiser_Mains_kWh'] = np.round(total_kwh * 0.70, 2)
    df['Common_Area_Total_kWh'] = np.round(total_kwh * 0.30, 2)
    
    # --- BROCHURE MIDPOINTS ---
    df['IIEMS_Lighting_kWh'] = np.round(df['Common_Area_Total_kWh'] * 0.35, 2)       
    df['IIEMS_HVAC_Vent_kWh'] = np.round(df['Common_Area_Total_kWh'] * 0.25, 2)      
    df['IIEMS_Water_STP_kWh'] = np.round(df['Common_Area_Total_kWh'] * 0.20, 2)      
    df['IIEMS_Lifts_kWh'] = np.round(df['Common_Area_Total_kWh'] * 0.125, 2)         
    df['IIEMS_Pool_Clubhouse_kWh'] = np.round(df['Common_Area_Total_kWh'] * 0.075, 2)
    
    return df

def generate_monthly_bills(daily_df, config):
    df = daily_df.copy()
    df['Month'] = df['Date'].dt.to_period('M')
    monthly = df.groupby('Month').agg(Actual_kWh=('Total_kWh', 'sum')).reset_index()
    monthly['Month'] = monthly['Month'].dt.to_timestamp()
    
    month_idx = monthly['Month'].dt.month
    
    md_season_curve = np.where((month_idx >= 3) & (month_idx <= 5), config["summer_md_mult"], 1.0)
    base_md = config["cmd_kva"] * 0.45  
    monthly['Recorded_MD_kVA'] = np.round(base_md * md_season_curve * np.random.normal(1.0, 0.05, len(monthly)), 2)
    monthly['Recorded_MD_kVA'] = np.clip(monthly['Recorded_MD_kVA'], 0, config["cmd_kva"] * 0.95) 
    
    pf_curve = np.where((month_idx >= 3) & (month_idx <= 5), config["min_pf"], 0.99)
    monthly['PF'] = np.round(pf_curve + np.random.uniform(0.0, 0.01, len(monthly)), 3)
    monthly['Net_Billed_kWh'] = monthly['Actual_kWh']
    monthly['kVAh'] = np.round(monthly['Net_Billed_kWh'] / monthly['PF'], 2)
    
    monthly['Energy_Charges_INR'] = np.round(monthly['Net_Billed_kWh'] * 8.18, 2)
    monthly['Demand_Charges_INR'] = np.round(monthly['Recorded_MD_kVA'] * 285, 2)
    monthly['MD_Penalty_INR'] = 0 
    monthly['Total_Payable_INR'] = monthly['Energy_Charges_INR'] + monthly['Demand_Charges_INR']
    monthly['Blended_Rate'] = (monthly['Total_Payable_INR'] / monthly['Net_Billed_kWh'].replace(0, 1)).round(2)
    
    return monthly

def generate_annual_telemetry(monthly_df, config):
    dates = pd.date_range(f"{START_DATE} 00:00:00", f"{END_DATE} 23:30:00", freq='30min')
    df = pd.DataFrame({'Timestamp': dates})
    
    df['Hour'] = df['Timestamp'].dt.hour + df['Timestamp'].dt.minute / 60.0
    df['Month_Anchor'] = df['Timestamp'].dt.to_period('M').dt.to_timestamp()
    df['Day_of_Week'] = df['Timestamp'].dt.dayofweek
    df['Date_Only'] = df['Timestamp'].dt.date
    
    morning_peak = np.exp(-0.2 * (df['Hour'] - 8)**2) * 0.6
    evening_peak = np.exp(-0.08 * (df['Hour'] - 20)**2) * 1.0
    baseload = 0.3
    
    is_weekend = df['Day_of_Week'] >= 5
    morning_peak = np.where(is_weekend, np.exp(-0.15 * (df['Hour'] - 9.5)**2) * 0.5, morning_peak)
    baseload = np.where(is_weekend, 0.4, baseload)
    
    df['Raw_Curve'] = morning_peak + evening_peak + baseload
    
    daily_variance = df.groupby('Date_Only')['Timestamp'].transform(lambda x: np.random.uniform(0.7, 1.0))
    df['Raw_Curve'] = df['Raw_Curve'] * daily_variance * np.random.normal(1.0, 0.05, len(df))
    
    df['Active_Demand_kVA'] = 0.0
    for _, row in monthly_df.iterrows():
        month_start = row['Month']
        target_peak = row['Recorded_MD_kVA']
        month_mask = df['Month_Anchor'] == month_start
        raw_month_max = df.loc[month_mask, 'Raw_Curve'].max()
        scalar = target_peak / raw_month_max
        df.loc[month_mask, 'Active_Demand_kVA'] = np.round(df.loc[month_mask, 'Raw_Curve'] * scalar, 2)
        
    df['Contracted_Limit'] = config["cmd_kva"]
    df = df[['Timestamp', 'Active_Demand_kVA', 'Contracted_Limit']]
    return df

def generate_iaq_guard_telemetry():
    # Generate 1 week of data (Starting on a Monday) at 5-minute intervals
    dates = pd.date_range("2026-04-06 00:00:00", "2026-04-12 23:55:00", freq='5min')
    df = pd.DataFrame({'Timestamp': dates})
    df['Hour'] = df['Timestamp'].dt.hour
    df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
    
    co_levels = np.random.normal(8, 2, len(df))
    
    is_weekday = df['DayOfWeek'] < 5
    morning_rush = is_weekday & (df['Hour'] >= 8) & (df['Hour'] <= 10)
    evening_rush = is_weekday & (df['Hour'] >= 17) & (df['Hour'] <= 20)
    
    spike_probability = (morning_rush | evening_rush) & (np.random.random(len(df)) > 0.6)
    co_levels[spike_probability] = np.random.normal(38, 4, sum(spike_probability))
    
    df['CO_ppm'] = np.round(np.clip(co_levels, 0, 100), 1)
    df['Exhaust_Fan_State'] = np.where(df['CO_ppm'] >= 25.0, 1, 0)
    
    return df[['Timestamp', 'CO_ppm', 'Exhaust_Fan_State']]

# --- THE MISSING EXECUTION BLOCK ---
if __name__ == "__main__":
    np.random.seed(42)
    for tier, config in TIERS.items():
        os.makedirs(f"data/{tier}", exist_ok=True)
        
        daily = generate_daily_drilldown(config)
        monthly = generate_monthly_bills(daily, config)
        telemetry = generate_annual_telemetry(monthly, config)
        
        daily.to_csv(f"data/{tier}/Daily_Drilldown.csv", index=False)
        monthly.to_csv(f"data/{tier}/Monthly_Bills.csv", index=False)
        telemetry.to_csv(f"data/{tier}/MD_Sentinel_Annual_30Min.csv", index=False)
    
    generate_iaq_guard_telemetry().to_csv("data/Global_IAQ_Guard_5Min.csv", index=False)
    print("Synthesis complete. Annual 30-Min telemetry aligned with Monthly Ledgers.")