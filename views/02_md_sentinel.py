import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.data_loader import load_tier_data
from modules.utils import format_indian_currency

st.title("🛡️ MD Sentinel: Demand Intelligence")
st.markdown("Interactive peak-shaving simulation across Annual, Monthly, and Daily granularities.")

active_tier = st.session_state.get('active_tier', "Tier 2 - Large (500-1,500 Units)")
_, _, md_df, _ = load_tier_data(active_tier)

# --- BULLETPROOF CMD MAPPING ---
cmd_map = {
    "Tier 1 - Mega (1,500+ Units)": 4000,
    "Tier 2 - Large (500-1,500 Units)": 1400,
    "Tier 3 - Mid (200-500 Units)": 900,
    "Tier 4 - Small (<200 Units)": 600
}
cmd = cmd_map.get(active_tier, 1400)
rate_per_kva = 285

# Data Pre-processing for Drill-Down
md_df['Month_Name'] = md_df['Timestamp'].dt.strftime('%b %Y')
md_df['Date_Str'] = md_df['Timestamp'].dt.strftime('%Y-%m-%d')

st.markdown("---")

# --- DRILL-DOWN CONTROLS ---
st.subheader("🔎 Telemetry Drill-Down")
col_m, col_d = st.columns(2)

month_list = ["All Year"] + md_df['Month_Name'].unique().tolist()
selected_month = col_m.selectbox("Select Month:", month_list)

if selected_month != "All Year":
    month_data = md_df[md_df['Month_Name'] == selected_month]
    day_list = ["All Days"] + month_data['Date_Str'].unique().tolist()
    selected_day = col_d.selectbox("Select Day:", day_list)
else:
    selected_day = "All Days"
    col_d.selectbox("Select Day:", ["Select a month first..."], disabled=True)

# Determine View Level and Filter Data
if selected_month == "All Year":
    view_df = md_df
    view_level = "Annual"
    chart_title = "12-Month Peak Demand (Highest kVA per Month)"
elif selected_day == "All Days":
    view_df = md_df[md_df['Month_Name'] == selected_month]
    view_level = "Monthly"
    chart_title = f"Daily Peak Demand for {selected_month}"
else:
    view_df = md_df[md_df['Date_Str'] == selected_day]
    view_level = "Daily"
    chart_title = f"30-Minute Demand Telemetry for {selected_day}"

# Calculate Peak for the Current View
view_peak_kva = view_df['Active_Demand_kVA'].max()
view_peak_percent = (view_peak_kva / cmd) * 100

st.markdown("---")

# --- WHAT-IF SIMULATOR CONTROLS ---
st.subheader("🎛️ Peak-Shaving Simulator")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("#### Set Target Limit")
    target_percent = st.slider(
        "Target Maximum Demand (%)", 
        min_value=40.0, 
        max_value=95.0, 
        value=65.0, 
        step=1.0,
        format="%f%%"
    )
    target_kva = cmd * (target_percent / 100)
    
    # Financial Math based on the View Level
    if target_kva < view_peak_kva:
        kva_shaved = view_peak_kva - target_kva
        if view_level == "Annual":
            projected_savings = kva_shaved * rate_per_kva * 12
            savings_label = "Est. Annual Savings"
        else:
            projected_savings = kva_shaved * rate_per_kva
            savings_label = "Avoided Monthly Penalty"
    else:
        kva_shaved = 0
        projected_savings = 0
        savings_label = "No Penalties Incurred" if view_level != "Annual" else "Est. Annual Savings"

with col2:
    st.markdown("#### Projected Financial Impact")
    s_col1, s_col2, s_col3 = st.columns(3)
    
    s_col1.markdown(f"""
    <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border-left: 4px solid #64748b; height: 100%;">
        <p style="margin:0; font-size: 0.9em; color: #64748b;">Current Peak ({view_level})</p>
        <h3 style="margin:0; color: #0f172a;">{view_peak_percent:.1f}%</h3>
        <p style="margin:0; font-size: 0.8em; color: #e11d48;">{view_peak_kva:,.0f} kVA</p>
    </div>
    """, unsafe_allow_html=True)
    
    s_col2.markdown(f"""
    <div style="background-color: #8b5cf610; padding: 15px; border-radius: 8px; border-left: 4px solid #8b5cf6; height: 100%;">
        <p style="margin:0; font-size: 0.9em; color: #64748b;">Target Limit</p>
        <h3 style="margin:0; color: #8b5cf6;">{target_percent:.1f}%</h3>
        <p style="margin:0; font-size: 0.8em; color: #8b5cf6;">{target_kva:,.0f} kVA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Highlight the savings box in Orange if we are looking at the Monthly/Daily penalty
    savings_color = "#10b981" if view_level == "Annual" else "#f97316"
    
    s_col3.markdown(f"""
    <div style="background-color: {savings_color}10; padding: 15px; border-radius: 8px; border-left: 4px solid {savings_color}; height: 100%;">
        <p style="margin:0; font-size: 0.9em; color: #64748b;">{savings_label}</p>
        <h3 style="margin:0; color: {savings_color};">{format_indian_currency(projected_savings)}</h3>
        <p style="margin:0; font-size: 0.8em; color: {savings_color};">↓ {kva_shaved:,.0f} kVA Shaved</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- DYNAMIC CHART GENERATION ---
st.subheader(f"📈 {chart_title}")

fig = go.Figure()

if view_level == "Annual":
    agg_df = view_df.groupby('Month_Name', sort=False)['Active_Demand_kVA'].max().reset_index()
    # Dynamic Coloring: Highlight the absolute highest month of the year in Orange
    colors = ['#f97316' if val == agg_df['Active_Demand_kVA'].max() else '#3b82f6' for val in agg_df['Active_Demand_kVA']]
    fig.add_trace(go.Bar(x=agg_df['Month_Name'], y=agg_df['Active_Demand_kVA'], name='Monthly Peak', marker_color=colors))

elif view_level == "Monthly":
    agg_df = view_df.groupby('Date_Str', sort=False)['Active_Demand_kVA'].max().reset_index()
    agg_df['Day_Label'] = pd.to_datetime(agg_df['Date_Str']).dt.strftime('%d')
    # Dynamic Coloring: Highlight the specific day that set the monthly bill in Orange
    colors = ['#f97316' if val == agg_df['Active_Demand_kVA'].max() else '#3b82f6' for val in agg_df['Active_Demand_kVA']]
    fig.add_trace(go.Bar(x=agg_df['Day_Label'], y=agg_df['Active_Demand_kVA'], name='Daily Peak', marker_color=colors))

elif view_level == "Daily":
    # Raw 30-min telemetry line chart
    fig.add_trace(go.Scatter(
        x=view_df['Timestamp'].dt.strftime('%H:%M'), 
        y=view_df['Active_Demand_kVA'], 
        name='Actual Demand',
        line=dict(color='#3b82f6', width=2),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    # Highlight the Shaved Peaks (Purple shading above the target line)
    shaved_curve = view_df['Active_Demand_kVA'].clip(lower=target_kva)
    fig.add_trace(go.Scatter(
        x=view_df['Timestamp'].dt.strftime('%H:%M'), 
        y=shaved_curve, 
        name='IIEMS Shaved Load',
        line=dict(color='rgba(255,255,255,0)'),
        fill='tonexty',
        fillcolor='rgba(139, 92, 246, 0.4)' 
    ))

# Common Target Limit Line
x_range = agg_df['Month_Name'] if view_level == "Annual" else (agg_df['Day_Label'] if view_level == "Monthly" else view_df['Timestamp'].dt.strftime('%H:%M'))
fig.add_trace(go.Scatter(
    x=[x_range.iloc[0], x_range.iloc[-1]], 
    y=[target_kva, target_kva], 
    name=f'Target Limit ({target_percent}%)',
    mode='lines',
    line=dict(color='#8b5cf6', width=2, dash='dot')
))

# Common Contract Limit Line
fig.add_trace(go.Scatter(
    x=[x_range.iloc[0], x_range.iloc[-1]], 
    y=[cmd, cmd], 
    name='Contract Limit (100%)',
    mode='lines',
    line=dict(color='#e11d48', width=2, dash='dash')
))

fig.update_layout(
    height=450,
    yaxis=dict(title='Demand (kVA)', range=[0, cmd * 1.1]),
    xaxis=dict(title='Time Period' if view_level != "Daily" else 'Hour of Day (30-Min Intervals)'),
    legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=1),
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)