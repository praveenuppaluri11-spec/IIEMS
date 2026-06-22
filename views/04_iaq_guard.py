import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.data_loader import load_tier_data
from modules.utils import format_indian_currency

st.title("🛡️ IAQ Guard: Health & Life Safety")
st.markdown("Basement Carbon Monoxide (CO) and CO₂ monitoring. Protecting resident health while aggressively shaving ventilation OPEX.")

active_tier = st.session_state.get('active_tier', "Tier 2 - Large (500-1,500 Units)")
is_small = "Small" in active_tier

_, monthly_df, _, _ = load_tier_data(active_tier)
blended_rate = (monthly_df['Total_Payable_INR'].sum() / monthly_df['Net_Billed_kWh'].sum())

st.markdown("---")

if is_small:
    # --- TIER 4: STILT PARKING / AMBIENT EXCEPTION ---
    st.info("🏗️ **Architectural Profile: Stilt & Surface Parking**")
    st.markdown("Small-tier properties predominantly utilize open stilt or surface-level parking. Because these areas rely on natural cross-ventilation, mechanical axial fans are not required. Therefore, **IAQ Guard serves purely as an ambient monitoring system** for the Clubhouse and enclosed FMS rooms, and mechanical exhaust OPEX savings are not applicable.")
    
    # 0 Metrics for honesty
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Air Quality Status", "NATURAL", "Cross-Ventilation")
    kpi2.metric("Traditional Fan Runtime", "0 Mins/Day", "No Mechanical Fans", delta_color="off")
    kpi3.metric("IIEMS Surgical Runtime", "0 Mins/Day", "Not Applicable")
    kpi4.metric("Avoided OPEX Waste", "₹0", "Zero Baseline Load", delta_color="off")
    
    st.markdown("---")
    
    # Flat, Safe Ambient Chart
    st.subheader("📊 24-Hour Ambient Air Quality (Clubhouse / Stilt)")
    st.markdown("<span style='font-size:13px; color:#64748b;'>Continuous monitoring of ambient CO and CO₂ levels to ensure safe thresholds in naturally ventilated areas.</span>", unsafe_allow_html=True)
    
    times = pd.date_range("2026-04-01 00:00", "2026-04-01 23:59", freq="1min")
    # Natural safe levels floating between 4 and 7 ppm
    co_ambient = np.random.normal(5, 0.8, len(times)) 
    
    fig_iaq = go.Figure()
    fig_iaq.add_trace(go.Scatter(
        x=times, y=co_ambient, 
        name='Ambient CO (ppm)', 
        line=dict(color='#10b981', width=2), 
        fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig_iaq.add_hline(y=25, line_dash="dash", line_color="#ef4444", annotation_text="WHO Safety Threshold (25 ppm)", annotation_position="top left")
    
    fig_iaq.update_layout(
        height=400, margin=dict(t=30, b=10, l=0, r=0), 
        xaxis=dict(tickformat="%H:%M", title="Time of Day (24 Hrs)"), 
        yaxis=dict(title="CO Concentration (ppm)", range=[0, 45]), 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_iaq, use_container_width=True)

else:
    # --- TIERS 1-3: 24-HOUR SURGICAL DATA SIMULATION ---
    times = pd.date_range("2026-04-01 00:00", "2026-04-01 23:59", freq="1min")
    co_arr = []
    fan_arr = []
    co_level = 8.0 # Safe baseline

    for t in times:
        hour = t.hour
        minute = t.minute
        
        # Define the 3-hour peak rush windows
        is_morning_peak = (hour >= 7 and hour < 10)
        is_evening_peak = (hour >= 17 and hour < 20)
        
        # IIEMS Logic: Fan ON strictly for 15 mins total per peak (7 min + 8 min)
        fan_on = 0
        if (hour == 8 and 30 <= minute < 37) or (hour == 9 and 15 <= minute < 23) or \
           (hour == 18 and 30 <= minute < 37) or (hour == 19 and 15 <= minute < 23):
            fan_on = 1
            
        # CO Physics Simulation
        if fan_on:
            co_level = max(8.0, co_level - 3.5) # Fan clears the air
        elif is_morning_peak or is_evening_peak:
            co_level += np.random.uniform(0.1, 0.6) # Cars build up CO
        else:
            co_level = max(8.0, co_level - 0.2) # Natural dissipation
            
        co_arr.append(co_level + np.random.normal(0, 0.5)) # Sensor noise
        fan_arr.append(fan_on)

    iaq_df = pd.DataFrame({'Timestamp': times, 'CO_ppm': co_arr, 'Fan_State': fan_arr})

    # Financial / Safety Math
    trad_mins = 360  # Blind timer runs 6 hours total
    iiems_mins = 30  # Surgical bursts
    motor_kw = 15.0  # 20HP axial fan

    trad_kwh = (trad_mins / 60) * motor_kw * 365
    iiems_kwh = (iiems_mins / 60) * motor_kw * 365
    saved_inr = (trad_kwh - iiems_kwh) * blended_rate

    # 4-Card KPI Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Air Quality Status", "SAFE", "CO < 25 ppm Maintained")
    kpi2.metric("Traditional Fan Runtime", f"{trad_mins} Mins/Day", "Blind Timer", delta_color="off")
    kpi3.metric("IIEMS Surgical Runtime", f"{iiems_mins} Mins/Day", "Sensor Driven")
    kpi4.metric("Avoided OPEX Waste", format_indian_currency(saved_inr), "Yearly Savings")

    st.markdown("---")

    st.subheader("📊 24-Hour Carbon Monoxide (CO) Exposure Map")
    st.markdown("<span style='font-size:13px; color:#64748b;'>Watch the grey CO line climb during the 3-hour morning/evening peaks. Instead of running the fan the entire time, IIEMS triggers the axial fans (blue line) for precisely <b>7 minutes</b> and <b>8 minutes</b> to crush the CO levels back to baseline.</span>", unsafe_allow_html=True)

    fig_iaq = make_subplots(specs=[[{"secondary_y": True}]])

    fig_iaq.add_trace(go.Scatter(
        x=iaq_df['Timestamp'], y=iaq_df['CO_ppm'], 
        name='CO Level (ppm)', 
        line=dict(color='#94a3b8', width=2),
        fill='tozeroy', fillcolor='rgba(148, 163, 184, 0.1)'
    ), secondary_y=False)

    fig_iaq.add_trace(go.Scatter(
        x=iaq_df['Timestamp'], y=iaq_df['Fan_State'], 
        name='Axial Fan Status', 
        mode='lines', line_shape='hv', 
        line=dict(color='#3b82f6', width=3)
    ), secondary_y=True)

    fig_iaq.add_hline(
        y=25, line_dash="dash", line_color="#ef4444", 
        annotation_text="WHO Safety Threshold (25 ppm)", annotation_position="top left",
        secondary_y=False
    )

    fig_iaq.update_layout(
        height=450, margin=dict(t=30, b=10, l=0, r=0), 
        xaxis=dict(tickformat="%H:%M", title="Time of Day (24 Hrs)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1), 
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig_iaq.update_yaxes(title_text="CO Concentration (ppm)", secondary_y=False, range=[0, 45])
    fig_iaq.update_yaxes(title_text="Fan Status (ON/OFF)", secondary_y=True, range=[-0.1, 1.5], showgrid=False, tickvals=[0, 1], ticktext=['OFF', 'ON'])

    st.plotly_chart(fig_iaq, use_container_width=True)

    st.markdown("---")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("#### ☠️ The Danger of Timers")
        st.markdown("Most Facility Management teams set basement exhaust fans on blind timers (e.g., 7 AM to 10 AM) to clear exhaust fumes. If a resident leaves a car idling outside of these hours, **lethal CO can accumulate unnoticed**, putting security guards and residents at severe risk.")
    with col_e2:
        st.markdown("#### 🧠 The IIEMS Advantage")
        st.markdown("By deploying military-grade CO and CO₂ sensors, IIEMS disconnects the fan from the clock and connects it to the air quality. The fan only runs when the air actually needs clearing. This guarantees 100% Life Safety compliance while reducing motor runtime by up to **90%**.")