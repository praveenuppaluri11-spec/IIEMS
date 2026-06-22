# views/01_command_center.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from modules.data_loader import load_tier_data
from modules.utils import format_indian_currency

st.title("⚡ Executive Command Center")
st.markdown("Annual baseline performance, pain-point diagnostics, and the Integrated IIEMS Value Proposition.")

active_tier = st.session_state.get('active_tier', "Tier 2 - Large (500-1,500 Units)")
daily_df, monthly_df, md_df, _ = load_tier_data(active_tier)

np.random.seed(42)
monthly_df['PF'] = np.where(monthly_df['Month'].dt.month.isin([3, 4, 5]), np.random.uniform(0.92, 0.95, len(monthly_df)), np.random.uniform(0.98, 1.0, len(monthly_df)))
monthly_df['KVARh'] = monthly_df['Net_Billed_kWh'] * np.tan(np.arccos(monthly_df['PF']))

# --- THE BASELINE PAIN MATRIX ---
st.markdown("### 🩸 12-Month Baseline Diagnostics (The Pain Points)")

metrics = {
    "Consumption (kWh)": {"col": "Net_Billed_kWh", "is_currency": False, "color": "#334155"},
    "Max Demand (kVA)": {"col": "Recorded_MD_kVA", "is_currency": False, "color": "#e11d48"},
    "Power Factor (PF)": {"col": "PF", "is_currency": False, "color": "#f59e0b"},
    "Total Billed (INR)": {"col": "Total_Payable_INR", "is_currency": True, "color": "#10b981"}
}

cols = st.columns(4)
for i, (metric_name, config) in enumerate(metrics.items()):
    col_data = monthly_df[config['col']]
    
    max_val = col_data.max()
    min_val = col_data.min()
    avg_val = col_data.mean()
    
    max_month = monthly_df.loc[col_data.idxmax(), 'Month'].strftime('%b-%y')
    min_month = monthly_df.loc[col_data.idxmin(), 'Month'].strftime('%b-%y')
    
    if config['is_currency']:
        max_str = format_indian_currency(max_val)
        min_str = format_indian_currency(min_val)
        avg_str = format_indian_currency(avg_val)
    elif metric_name == "Power Factor (PF)":
        max_str = f"{max_val:.3f}"
        min_str = f"{min_val:.3f}"
        avg_str = f"{avg_val:.3f}"
    else:
        max_str = f"{max_val:,.0f}"
        min_str = f"{min_val:,.0f}"
        avg_str = f"{avg_val:,.0f}"

    with cols[i]:
        st.markdown(f"""
        <div style="background-color: {config['color']}15; border-left: 5px solid {config['color']}; padding: 15px; border-radius: 5px; height: 100%;">
            <h5 style="color: {config['color']}; margin-top: 0; margin-bottom: 10px;">{metric_name}</h5>
            <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #475569; margin-bottom: 5px;">
                <span>Max ({max_month}):</span> <strong style="color: #0f172a;">{max_str}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #475569; margin-bottom: 5px;">
                <span>Min ({min_month}):</span> <strong style="color: #0f172a;">{min_str}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.9em; color: #475569; border-top: 1px solid #cbd5e1; padding-top: 5px; margin-top: 5px;">
                <span>Average:</span> <strong style="color: #0f172a;">{avg_str}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- THE IIEMS VALUE PROPOSITION (Wealth + Health) ---
st.markdown("### 💎 The IIEMS Value Proposition: Wealth + Health")

# 1. Asset Efficiency Savings
blended_rate = 8.18
annual_facility_savings_kwh = (
    (daily_df['IIEMS_Lighting_kWh'].sum() * 0.65) +
    (daily_df['IIEMS_HVAC_Vent_kWh'].sum() * 0.60) +
    (daily_df['IIEMS_Water_STP_kWh'].sum() * 0.50) +
    (daily_df['IIEMS_Lifts_kWh'].sum() * 0.30) +
    (daily_df['IIEMS_Pool_Clubhouse_kWh'].sum() * 0.50)
)
annual_facility_savings_inr = annual_facility_savings_kwh * blended_rate

# 2. Demand Intelligence Savings
annual_md_savings_inr = monthly_df['Demand_Charges_INR'].sum() * 0.20

total_annual_bill = monthly_df['Total_Payable_INR'].sum()
optimized_bill = total_annual_bill - annual_facility_savings_inr - annual_md_savings_inr

v_col1, v_col2, v_col3 = st.columns(3)

# 🛠️ Define accent colors for each card to create distinct borders
color_wealth = "#3b82f6"  # Blue for Asset Efficiency
color_health = "#8b5cf6"  # Purple for Demand Intelligence
color_wellness = "#10b981" # Green for Wellness

with v_col1:
    st.markdown(f"""
    <div style="background-color: {color_wealth}10; padding: 25px; border-radius: 12px; border: 2px solid {color_wealth}; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h4 style="color: {color_wealth}; margin-top: 0; font-weight: bold;">🛠️ Asset Efficiency </h4>
        <p style="color: #64748b; font-size: 0.95em; margin-bottom: 20px;">Up to 52% reduction in core utility waste via smart sensors, VFDs, and lighting controls across the 5 IIEMS pillars.</p>
        <h2 style="color: #0f172a; margin: 10px 0;">{format_indian_currency(annual_facility_savings_inr)} <span style="font-size: 0.45em; color: #64748b; font-weight: normal;">/ Yr Projected</span></h2>
        <p style="color: {color_wealth}; font-weight: bold; margin-bottom: 0; font-size: 0.9em;">↓ Direct kWh Reduction</p>
    </div>
    """, unsafe_allow_html=True)

with v_col2:
    st.markdown(f"""
    <div style="background-color: {color_health}10; padding: 25px; border-radius: 12px; border: 2px solid {color_health}; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h4 style="color: {color_health}; margin-top: 0; font-weight: bold;">🛡️ Demand Intelligence </h4>
        <p style="color: #64748b; font-size: 0.95em; margin-bottom: 20px;">Continuous load shifting, telemetry monitoring, and diagnostic insights to optimize baseline Maximum Demand by ~20%.</p>
        <h2 style="color: #0f172a; margin: 10px 0;">{format_indian_currency(annual_md_savings_inr)} <span style="font-size: 0.45em; color: #64748b; font-weight: normal;">/ Yr Projected</span></h2>
        <p style="color: {color_health}; font-weight: bold; margin-bottom: 0; font-size: 0.9em;">↓ Base KVA Optimization</p>
    </div>
    """, unsafe_allow_html=True)

with v_col3:
    st.markdown(f"""
    <div style="background-color: {color_wellness}10; padding: 25px; border-radius: 12px; border: 2px solid {color_wellness}; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h4 style="color: {color_wellness}; margin-top: 0; font-weight: bold;">🌬️ Life Safety & Wellness</h4>
        <p style="color: #64748b; font-size: 0.95em; margin-bottom: 20px;">Real-time IAQ Guard monitoring in basements and common areas, ensuring optimal air quality, CO dispersal, and occupant safety.</p>
        <h2 style="color: #0f172a; margin: 10px 0;">Priceless <span style="font-size: 0.45em; color: #64748b; font-weight: normal;"></span></h2>
        <p style="color: {color_wellness}; font-weight: bold; margin-bottom: 0; font-size: 0.9em;">♥ Community Peace of Mind</p>
    </div>
    """, unsafe_allow_html=True)

# --- THE MONTHLY POTENTIAL SAVINGS SUMMARY (Waterfall) ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Monthly Potential Savings Summary")

# 1. Calculate Monthly Averages for the Waterfall
avg_raiser_inr = (daily_df['Raiser_Mains_kWh'].sum() * blended_rate) / 12
avg_common_inr = (daily_df['Common_Area_Total_kWh'].sum() * blended_rate) / 12
avg_md_inr = monthly_df['Demand_Charges_INR'].mean()

current_total = avg_raiser_inr + avg_common_inr + avg_md_inr
asset_savings = avg_common_inr * 0.52
md_savings = avg_md_inr * 0.20
optimized_total = current_total - asset_savings - md_savings

# Custom Waterfall acting as a stacked bridge
fig = go.Figure(go.Waterfall(
    name="Monthly Savings", orientation="v",
    measure=["relative", "relative", "relative", "total", "relative", "relative", "total"],
    x=[
        "Raiser Mains<br>(Flats)", 
        "Common Service<br>(Base)", 
        "MD Charges<br>(Base)", 
        "Current<br>Monthly Bill", 
        "Asset Efficiency<br>(-52% Common)", 
        "Demand Intelligence<br>(-20% MD)", 
        "Optimized<br>Monthly Bill"
    ],
    textposition="outside",
    text=[
        format_indian_currency(avg_raiser_inr),
        format_indian_currency(avg_common_inr),
        format_indian_currency(avg_md_inr),
        format_indian_currency(current_total),
        f"-{format_indian_currency(asset_savings)}",
        f"-{format_indian_currency(md_savings)}",
        format_indian_currency(optimized_total)
    ],
    y=[avg_raiser_inr, avg_common_inr, avg_md_inr, current_total, -asset_savings, -md_savings, 0],
    connector={"line": {"color": "rgb(63, 63, 63)", "width": 2}},
    decreasing={"marker": {"color": color_wellness}}, # Green for savings
    increasing={"marker": {"color": "#64748b"}},      # Slate gray for baseline buildup
    totals={"marker": {"color": color_wealth}}        # Blue for the totals
))

fig.update_layout(
    showlegend=False, 
    margin=dict(l=0, r=0, t=30, b=0),
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(title="INR (₹)", showgrid=True, gridcolor='#e2e8f0')
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("12-Month Performance Trends")

from plotly.subplots import make_subplots

# --- 1. FINANCIAL STACKED GRAPH ---
st.markdown("#### 💰 Expenditure Analysis")

# Dynamic Y-Axis Calculation (Zooms in to 85% of the lowest bill)
min_expenditure = (monthly_df['Total_Payable_INR'].min() / 100000) * 0.85
max_expenditure = (monthly_df['Total_Payable_INR'].max() / 100000) * 1.1

fig1 = make_subplots(specs=[[{"secondary_y": True}]])
fig1.add_trace(go.Bar(x=monthly_df['Month'], y=monthly_df['Energy_Charges_INR']/100000, name='Energy Charges', marker_color='#fdba74'), secondary_y=False)
fig1.add_trace(go.Bar(x=monthly_df['Month'], y=monthly_df['Demand_Charges_INR']/100000, name='MD Charges', marker_color='#bae6fd'), secondary_y=False)

fig1.add_trace(go.Scatter(
    x=monthly_df['Month'], y=monthly_df['Blended_Rate'], 
    name='Blended Rate (₹/kWh)', 
    mode='lines+markers+text',
    text=monthly_df['Blended_Rate'].apply(lambda x: f"₹{x:.2f}"),
    textposition='top center',
    textfont=dict(color='#8b5cf6', size=11),
    line=dict(color='#8b5cf6', width=3)
), secondary_y=True)

fig1.update_layout(
    barmode='stack', 
    height=400,
    yaxis=dict(title='INR (Lakhs)', range=[min_expenditure, max_expenditure]), 
    yaxis2=dict(title='Rate (₹/kWh)', overlaying='y', side='right', showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1),
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig1, use_container_width=True)


# --- 2. MAXIMUM DEMAND TREND ---
st.markdown("#### ⚡ Demand Intelligence")

cmd_map = {
    "Tier 1 - Mega (1,500+ Units)": 4000,
    "Tier 2 - Large (500-1,500 Units)": 1400,
    "Tier 3 - Mid (200-500 Units)": 900,
    "Tier 4 - Small (<200 Units)": 600
}
current_cmd = cmd_map.get(active_tier, 1400)

monthly_df['MD_Percent'] = (monthly_df['Recorded_MD_kVA'] / current_cmd) * 100

# Dynamic Y-Axis Calculation for kVA (Zooms in to 85% of lowest demand)
min_md = monthly_df['Recorded_MD_kVA'].min() * 0.85

fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(go.Bar(x=monthly_df['Month'], y=monthly_df['Recorded_MD_kVA'], name='Max Demand (kVA)', marker_color='#3b82f6'), secondary_y=False)
fig2.add_trace(go.Scatter(x=monthly_df['Month'], y=[current_cmd]*len(monthly_df), name='MD Contract Load', line=dict(color='#e11d48', width=2, dash='dash')), secondary_y=False)

fig2.add_trace(go.Scatter(
    x=monthly_df['Month'], y=monthly_df['MD_Percent'], 
    name='MD % of Contract', 
    mode='lines+markers+text',
    text=monthly_df['MD_Percent'].round(1).astype(str) + '%',
    textposition='top center',
    textfont=dict(color='#8b5cf6', size=11),
    line=dict(color='#8b5cf6', width=3)
), secondary_y=True)

fig2.update_layout(
    barmode='group', 
    height=400,
    yaxis=dict(title='kVA', range=[min_md, current_cmd * 1.05]), 
    yaxis2=dict(title='% of Contract', overlaying='y', side='right', range=[0, 110], showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1),
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig2, use_container_width=True)


# --- 3. UNIT CONSUMPTION & EFFICIENCY ---
st.markdown("#### 📊 Unit Consumption Analysis")

# Dynamic Y-Axis Calculation for Units
min_units = (monthly_df['Net_Billed_kWh'].min() / 1000) * 0.85
max_units = (monthly_df['kVAh'].max() / 1000) * 1.1

fig3 = go.Figure()

fig3.add_trace(go.Bar(x=monthly_df['Month'], y=monthly_df['Net_Billed_kWh']/1000, name='kWh (Actual)', marker_color='#3b82f6', yaxis='y1'))
fig3.add_trace(go.Bar(x=monthly_df['Month'], y=monthly_df['kVAh']/1000, name='kVAh', marker_color='#93c5fd', yaxis='y1'))

# Power Factor line with explicitly formatted 3-decimal text labels
fig3.add_trace(go.Scatter(
    x=monthly_df['Month'], y=monthly_df['PF'], 
    name='Power Factor', 
    mode='lines+markers+text',
    text=monthly_df['PF'].apply(lambda x: f"{x:.3f}"),
    textposition='top center',
    textfont=dict(color='#f59e0b', size=11),
    line=dict(color='#f59e0b', width=3), 
    yaxis='y2'
))

fig3.update_layout(
    barmode='group',
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.15, xanchor="right", x=1),
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(
        title='Units (x1000)', 
        side='left', 
        showgrid=True, gridcolor='#e2e8f0',
        range=[min_units, max_units]
    ),
    yaxis2=dict(
        title='Power Factor', 
        side='right', 
        overlaying='y', 
        range=[0.85, 1.05], 
        showgrid=False
    )
)
st.plotly_chart(fig3, use_container_width=True)