import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots  # <--- ADD THIS LINE
from modules.data_loader import load_tier_data
from modules.utils import format_indian_currency

st.title("⚙️ Asset Efficiency: Hardware & Retrofits")
st.markdown("Deconstructing the 30% Common Area Baseload into 5 Optimizable Hardware Pillars based on IIEMS standards.")

active_tier = st.session_state.get('active_tier', "Tier 2 - Large (500-1,500 Units)")
daily_df, monthly_df, _, config = load_tier_data(active_tier)

# --- FINANCIAL MATH ---
blended_rate = (monthly_df['Total_Payable_INR'].sum() / monthly_df['Net_Billed_kWh'].sum())

# THE MASTER DICTIONARY (Keys perfectly aligned)
pillars = {
    "Smart Lighting": {"kwh": daily_df['IIEMS_Lighting_kWh'].sum(), "savings_pct": 0.70, "color": "#f59e0b", "icon": "💡"},
    "Common HVAC & Ventilation": {"kwh": daily_df['IIEMS_HVAC_Vent_kWh'].sum(), "savings_pct": 0.40, "color": "#3b82f6", "icon": "❄️"},
    "Centralized Water & STP": {"kwh": daily_df['IIEMS_Water_STP_kWh'].sum(), "savings_pct": 0.50, "color": "#0ea5e9", "icon": "💧"},
    "Elevator Network": {"kwh": daily_df['IIEMS_Lifts_kWh'].sum(), "savings_pct": 0.40, "color": "#8b5cf6", "icon": "🛗"},
    "Pool & Clubhouse": {"kwh": daily_df['IIEMS_Pool_Clubhouse_kWh'].sum(), "savings_pct": 0.50, "color": "#ec4899", "icon": "🏊"}
}

total_common_kwh = sum(p["kwh"] for p in pillars.values())
total_common_inr = total_common_kwh * blended_rate
total_saved_kwh = sum(p["kwh"] * p["savings_pct"] for p in pillars.values())
total_saved_inr = total_saved_kwh * blended_rate
optimized_common_inr = total_common_inr - total_saved_inr
actual_savings_pct = (total_saved_kwh / total_common_kwh) * 100

st.markdown("---")

# --- EXECUTIVE SUMMARY ---
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #64748b; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <p style="margin:0; font-size: 1em; color: #64748b;">Current Annual Common Spend</p>
    <h2 style="margin:0; color: #0f172a;">{format_indian_currency(total_common_inr)}</h2>
    <p style="margin:0; font-size: 0.85em; color: #64748b;">{total_common_kwh:,.0f} kWh consumed</p>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style="background-color: #10b98110; padding: 20px; border-radius: 8px; border-left: 4px solid #10b981; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <p style="margin:0; font-size: 1em; color: #64748b;">IIEMS Avoided Waste</p>
    <h2 style="margin:0; color: #10b981;">{format_indian_currency(total_saved_inr)}</h2>
    <p style="margin:0; font-size: 0.85em; color: #10b981;">↓ {actual_savings_pct:.1f}% Reduction Achieved</p>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style="background-color: #3b82f610; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <p style="margin:0; font-size: 1em; color: #64748b;">Optimized Annual Spend</p>
    <h2 style="margin:0; color: #3b82f6;">{format_indian_currency(optimized_common_inr)}</h2>
    <p style="margin:0; font-size: 0.85em; color: #3b82f6;">Asset Efficiency Applied</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- VISUALIZATION ROW ---
c_chart1, c_chart2 = st.columns([1, 1.2])

with c_chart1:
    st.subheader("🥧 The Common Area Baseload")
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(pillars.keys()), values=[p["kwh"] for p in pillars.values()],
        hole=.4, marker_colors=[p["color"] for p in pillars.values()], textinfo='label+percent'
    )])
    fig_pie.update_layout(height=350, margin=dict(t=10, b=0, l=0, r=0), showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

with c_chart2:
    st.subheader("⚖️ Before vs. After (Financial Impact)")
    names = list(pillars.keys())
    
    # Raw INR values
    current_cost = [(p["kwh"] * blended_rate) for p in pillars.values()]
    saved_cost = [(p["kwh"] * p["savings_pct"] * blended_rate) for p in pillars.values()]
    new_cost = [c - s for c, s in zip(current_cost, saved_cost)]
    
    # Scale to Lakhs for clean axis rendering
    new_cost_lakhs = [c / 1_00_000 for c in new_cost]
    saved_cost_lakhs = [c / 1_00_000 for c in saved_cost]
    
    # Utilize our custom util for the hover text
    hover_new = [format_indian_currency(c) for c in new_cost]
    hover_saved = [format_indian_currency(c) for c in saved_cost]
    
    fig_bar = go.Figure()
    
    fig_bar.add_trace(go.Bar(
        y=names, x=new_cost_lakhs, 
        name='Optimized Spend', orientation='h', marker_color='#3b82f6',
        text=[f"₹{v:.1f}L" for v in new_cost_lakhs], textposition='inside',
        hovertext=hover_new, hoverinfo="text+name"
    ))
    
    fig_bar.add_trace(go.Bar(
        y=names, x=saved_cost_lakhs, 
        name='IIEMS Avoided Waste', orientation='h', marker_color='#10b981',
        text=[f"₹{v:.1f}L" for v in saved_cost_lakhs], textposition='inside',
        hovertext=hover_saved, hoverinfo="text+name"
    ))
    
    fig_bar.update_layout(
        barmode='stack', 
        height=350, 
        margin=dict(t=10, b=40, l=0, r=0), 
        yaxis=dict(autorange="reversed"), 
        xaxis=dict(title="Annual Spend (₹ Lakhs)", tickprefix="₹", ticksuffix="L"),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1), 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# --- THE 5 PILLAR TABS ---
st.subheader("🛠️ Hardware Deep Dives")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { 
        display: flex; width: 100%; gap: 8px; background-color: #f8fafc; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] { 
        flex: 1; height: 55px; background-color: white; border-radius: 8px; font-weight: 600; color: #64748b; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease-in-out; margin: 0;
    }
    .stTabs [data-baseweb="tab"]:hover { background-color: #f1f5f9; border-color: #cbd5e1; color: #0f172a; }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; border: none; box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3); }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 Smart Lighting", "❄️ Common HVAC", "💧 Water Pumps", "🛗 Elevators", "🏊 Pool & Clubhouse"
])

# --- TAB 1: SMART LIGHTING ---
with tab1:
    st.markdown("### 🧮 Interactive Lighting Load Calculator")
    st.markdown("Validate the IIEMS baseline assumptions. The calculator automatically synchronizes the inventory below to match your property's actual billed consumption.")
    
    actual_light_kwh = pillars["Smart Lighting"]["kwh"]
    is_mega = "Mega" in active_tier or "Large" in active_tier
    
    def_b = 3 if is_mega else 1
    def_f = 25 if is_mega else 10 
    def_s = 6 if is_mega else 2   
    
    c_kwh_yr_pre = (def_f * 40 * 15 * 12 * 365) / 1000
    s_kwh_yr_pre = (def_s * def_f * 2 * 20 * 24 * 365) / 1000
    b_kwh_yr_pre = actual_light_kwh - c_kwh_yr_pre - s_kwh_yr_pre
    def_l = int((b_kwh_yr_pre * 1000) / (def_b * 20 * 24 * 365)) if b_kwh_yr_pre > 0 else 150

    c_base, c_corr, c_stair = st.columns(3)
    
    with c_base:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #f59e0b;"><b>🚗 Basements (24x7)</b></div>""", unsafe_allow_html=True)
        st.write("")
        b_count = st.number_input("# of Basements", min_value=0, value=def_b, step=1)
        b_lights = st.number_input("Lights per Basement", min_value=0, value=def_l, step=10)
        b_watts = st.number_input("Wattage per Light (W)", min_value=0, value=20, step=1, key='bw')
    
    with c_corr:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #f59e0b;"><b>🚶 Corridors (12 hrs/day)</b></div>""", unsafe_allow_html=True)
        st.write("")
        f_count = st.number_input("# of Floors / Corridors", min_value=0, value=def_f, step=1)
        c_lights = st.number_input("Lights per Corridor", min_value=0, value=40, step=1)
        c_watts = st.number_input("Wattage per Light (W)", min_value=0, value=15, step=1, key='cw')

    with c_stair:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #f59e0b;"><b>🪜 Stairwells (24x7)</b><br><span style='font-size:12px; color:#64748b;'>*2 lights per floor</span></div>""", unsafe_allow_html=True)
        st.write("")
        s_count = st.number_input("# of Stairwell Shafts", min_value=0, value=def_s, step=1)
        st.number_input("# of Floors (Synced)", value=f_count, disabled=True)
        s_watts = st.number_input("Wattage per Light (W)", min_value=0, value=20, step=1, key='sw')

    b_kwh_yr = (b_count * b_lights * b_watts * 24 * 365) / 1000
    c_kwh_yr = (f_count * c_lights * c_watts * 12 * 365) / 1000
    s_kwh_yr = (s_count * f_count * 2 * s_watts * 24 * 365) / 1000
    calculated_total_kwh = b_kwh_yr + c_kwh_yr + s_kwh_yr
    
    yearly_bill_inr = calculated_total_kwh * blended_rate
    savings_kwh = calculated_total_kwh * 0.70
    savings_inr = savings_kwh * blended_rate

    st.markdown("---")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Calculated Annual Load", f"{calculated_total_kwh:,.0f} kWh", "Inventory Match")
    kpi2.metric("Yearly Lighting Bill", format_indian_currency(yearly_bill_inr), "Current OPEX", delta_color="off")
    kpi3.metric("Projected IIEMS Savings", format_indian_currency(savings_inr), "70% Reduction")
    kpi4.metric("Est. ROI (Years)", "0.75", "Payback Period", delta_color="off")
    
    st.markdown("---")
    
    st.subheader("📉 Pre vs Post IIEMS Commissioning (12-Month Horizon)")
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    b_m, c_m, s_m = b_kwh_yr / 12, c_kwh_yr / 12, s_kwh_yr / 12
    
    b_data = [b_m]*8 + [b_m * 0.3]*4
    c_data = [c_m]*8 + [c_m * 0.3]*4
    s_data = [s_m]*8 + [s_m * 0.3]*4
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Bar(x=months, y=b_data, name="Basements", marker_color="#1e3a8a"))
    fig_line.add_trace(go.Bar(x=months, y=c_data, name="Corridors", marker_color="#3b82f6"))
    fig_line.add_trace(go.Bar(x=months, y=s_data, name="Stairwells", marker_color="#93c5fd"))
    
    fig_line.add_vline(x=7.5, line_width=3, line_dash="dash", line_color="#ef4444")
    fig_line.add_annotation(x=7.5, y=(b_m+c_m+s_m)*1.05, text="IIEMS Commissioned", showarrow=False, font=dict(color="#ef4444", size=14, weight="bold"), xanchor="center", yanchor="bottom")
    
    fig_line.update_layout(barmode='stack', height=400, yaxis=dict(title="Monthly Consumption (kWh)"), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1), plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=0))
    st.plotly_chart(fig_line, use_container_width=True)

# --- TAB 2: COMMON HVAC & VENTILATION ---
# --- TAB 2: COMMON HVAC & VENTILATION ---
with tab2:
    st.markdown("### 🌬️ Common HVAC & Ventilation")
    st.markdown("Common area cooling (Banquet Halls, Gyms) and basement ventilation are huge energy sinks. IIEMS deploys **AJNA millimeter-wave/Doppler radar sensors** to eliminate empty-room cooling, alongside smart controls for axial fans. We continuously monitor compressor power draw to recommend 5-star or VRF retrofits exactly when older assets begin to degrade.")
    
    actual_hvac_kwh = pillars["Common HVAC & Ventilation"]["kwh"]
    
    # Tier-based Intelligent Defaults for Axial Fans and AC Tonnage
    if "Tier 1" in active_tier:
        def_ac_tr, def_axial = 80, 30
    elif "Tier 2" in active_tier:
        def_ac_tr, def_axial = 45, 15
    elif "Tier 3" in active_tier:
        def_ac_tr, def_axial = 30, 6
    else: # Tier 4
        def_ac_tr, def_axial = 24, 0
        
    ac_kw_per_tr = 1.2
    axial_kw = 2.2
    
    # Shift 100% of the allocated HVAC budget to ACs if it is a Tier 4 (no basement fans)
    is_tier4 = "Tier 4" in active_tier
    ac_split = 1.0 if is_tier4 else 0.6
    vent_split = 0.0 if is_tier4 else 0.4
    
    ac_kwh_target = actual_hvac_kwh * ac_split
    vent_kwh_target = actual_hvac_kwh * vent_split
    
    def_ac_hrs = int((ac_kwh_target) / (def_ac_tr * ac_kw_per_tr * 365)) if def_ac_tr > 0 else 0
    def_vent_hrs = int((vent_kwh_target) / (def_axial * axial_kw * 365)) if def_axial > 0 else 0
    
    c_ac, c_vent, c_diag = st.columns(3)
    
    with c_ac:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #3b82f6;"><b>❄️ Common Area ACs</b><br><span style='font-size:12px; color:#64748b;'>Clubhouse, Gym, Yoga Rooms</span></div>""", unsafe_allow_html=True)
        st.write("")
        # Added unique keys here to prevent Streamlit duplicate ID errors
        ac_tr = st.number_input("Total AC Capacity (TR)", min_value=0, value=def_ac_tr, step=2, key="ac_tr")
        ac_hrs = st.number_input("Avg Daily Runtime (Hrs)", min_value=0, value=max(1, def_ac_hrs), step=1, key="ac_hrs")
        ac_kw = st.number_input("Est. kW per TR", min_value=0.0, value=ac_kw_per_tr, step=0.1, key="ac_kw")

    with c_vent:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #3b82f6;"><b>🌀 Basement Ventilation</b><br><span style='font-size:12px; color:#64748b;'>Axial / Jet Fans</span></div>""", unsafe_allow_html=True)
        st.write("")
        if is_tier4:
            st.info("Disabled: Small properties utilize Stilt/Surface parking with natural cross-ventilation.")
            vent_count = 0
            vent_hrs = 0
            vent_kw = 0.0
        else:
            # Added unique keys here as well
            vent_count = st.number_input("# of Axial Fans", min_value=0, value=def_axial, step=1, key="vent_count")
            vent_hrs = st.number_input("Avg Daily Runtime (Hrs)", min_value=0, value=max(0, def_vent_hrs), step=1, key="vent_hrs")
            vent_kw = st.number_input("Motor Rating (kW)", min_value=0.0, value=axial_kw, step=0.1, key="vent_kw")

    with c_diag:
        st.markdown("""<div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; height: 100%;">
        <h4 style="margin-top:0; color:#0f172a;">⚡ Asset Health Engine</h4>
        <p style="font-size: 0.85em; color: #64748b;">We monitor the <b>Power Factor</b> and <b>Current Draw</b> of every major compressor.</p>
        <p style="font-size: 0.85em; color: #64748b;">When an aging AC degrades from 1.2 kW/TR to >1.5 kW/TR, the system automatically triggers an alert calculating the exact ROI of upgrading to a 5-Star VRF system.</p>
        </div>""", unsafe_allow_html=True)

    calc_ac_kwh = ac_tr * ac_kw * ac_hrs * 365
    calc_vent_kwh = vent_count * vent_kw * vent_hrs * 365
    calculated_hvac_kwh = calc_ac_kwh + calc_vent_kwh
    
    yearly_hvac_inr = calculated_hvac_kwh * blended_rate
    savings_hvac_inr = (calculated_hvac_kwh * pillars["Common HVAC & Ventilation"]["savings_pct"]) * blended_rate

    st.markdown("---")
    
    hkpi1, hkpi2, hkpi3, hkpi4 = st.columns(4)
    hkpi1.metric("Calculated Annual Load", f"{calculated_hvac_kwh:,.0f} kWh", "Inventory Match")
    hkpi2.metric("Yearly HVAC/Vent Bill", format_indian_currency(yearly_hvac_inr), "Current OPEX", delta_color="off")
    hkpi3.metric("Projected IIEMS Savings", format_indian_currency(savings_hvac_inr), "40% Reduction")
    hkpi4.metric("Est. ROI (Years)", "2.5", "CapEx Payback", delta_color="off")

    st.markdown("---")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**1. AJNA Occupancy Tracking (24h AC Profile)**")
        hours = pd.date_range("2026-04-01", periods=24, freq="h")
        
        trad_ac = np.where((hours.hour >= 6) & (hours.hour <= 22), 100, 0)
        
        ajna_ac = np.zeros(24)
        ajna_ac[7:9] = 100  
        ajna_ac[18:21] = 100 
        
        fig_ajna = go.Figure()
        fig_ajna.add_trace(go.Scatter(x=hours, y=trad_ac, name="Blind Timer Scheduling", line=dict(color="#94a3b8", width=2, dash="dash"), fill="tozeroy", fillcolor="rgba(148, 163, 184, 0.2)"))
        fig_ajna.add_trace(go.Scatter(x=hours, y=ajna_ac, name="AJNA mmWave Profile", mode="lines", line_shape="hv", line=dict(color="#3b82f6", width=3), fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.4)"))
        fig_ajna.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0), yaxis=dict(title="AC Load (%)", range=[0, 110]), xaxis=dict(tickformat="%H:%M"), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ajna, use_container_width=True)

    with chart_col2:
        st.markdown("**2. Asset Degradation & Retrofit Triggers**")
        months = ["Yr 1", "Yr 2", "Yr 3", "Yr 4", "Yr 5", "Retrofit"]
        
        power_draw = [1.2, 1.25, 1.35, 1.48, 1.65, 0.85] 
        colors = ["#cbd5e1", "#cbd5e1", "#94a3b8", "#f59e0b", "#ef4444", "#10b981"]
        
        fig_deg = go.Figure(data=[go.Bar(x=months, y=power_draw, marker_color=colors, text=[f"{v} kW/TR" for v in power_draw], textposition='auto')])
        fig_deg.add_hline(y=1.4, line_dash="dash", line_color="#ef4444", annotation_text="IIEMS Retrofit Trigger (>1.4 kW/TR)", annotation_position="top left")
        fig_deg.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0), yaxis=dict(title="Efficiency (kW per Ton)"), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_deg, use_container_width=True)

# --- TAB 3: WATER PUMPS & STP ---
# --- TAB 3: CENTRALIZED WATER & STP ---
with tab3:
    st.markdown("### 💧 Centralized Water & STP")
    st.markdown("In large communities, water infrastructure (Borewells, Overhead Transfer Pumps, and STP Aeration) runs on crude 'Direct-On-Line' (DOL) starters. IIEMS installs **Variable Frequency Drives (VFDs)** and PLC pressure transducers. By applying the *Affinity Laws of Fluid Dynamics*, pumps glide smoothly to match exact demand, eliminating kVA spikes and slashing baseline kWh.")
    
    actual_water_kwh = pillars["Centralized Water & STP"]["kwh"]
    is_mega = "Mega" in active_tier or "Large" in active_tier
    is_small = "Small" in active_tier
    
    # Intelligent Defaults modeled on Mega (My Home Mangala) vs Small (Galaxy/Muppa)
    def_bw_count = 15 if is_mega else (2 if is_small else 4)
    def_tp_count = 8 if is_mega else (4 if is_small else 4) # Galaxy has 4 WTP pumps
    def_stp_count = 6 if is_mega else (4 if is_small else 4) # Galaxy has 4 STP pumps
    
    # Standard Motor Sizes based on audit data
    def_bw_hp = 12.5 if is_mega else 7.5
    def_tp_hp = 15.0 if is_mega else 7.5  # Muppa uses 7.5 HP Kirloskar
    def_stp_hp = 10.0 if is_mega else 5.0
    
    # Reverse Engineer the runtimes to perfectly match the allocated load (30% BW, 40% TP, 30% STP)
    bw_kwh_target = actual_water_kwh * 0.30
    tp_kwh_target = actual_water_kwh * 0.40
    stp_kwh_target = actual_water_kwh * 0.30
    
    # HP to kW conversion = 0.746
    def_bw_hrs = int(bw_kwh_target / (def_bw_count * (def_bw_hp * 0.746) * 365)) if def_bw_count > 0 else 0
    def_tp_hrs = int(tp_kwh_target / (def_tp_count * (def_tp_hp * 0.746) * 365)) if def_tp_count > 0 else 0
    def_stp_hrs = int(stp_kwh_target / (def_stp_count * (def_stp_hp * 0.746) * 365)) if def_stp_count > 0 else 0

    # 3-Column Input Layout
    c_bw, c_tp, c_stp = st.columns(3)
    
    with c_bw:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #0ea5e9;"><b>🕳️ Deep Borewells</b><br><span style='font-size:12px; color:#64748b;'>Groundwater Extraction</span></div>""", unsafe_allow_html=True)
        st.write("")
        bw_count = st.number_input("# of Borewell Pumps", min_value=0, value=def_bw_count, step=1)
        bw_hrs = st.number_input("Avg Daily Runtime (Hrs)", min_value=0, value=max(1, def_bw_hrs), step=1, key='bwh')
        bw_hp = st.number_input("Avg Motor Size (HP)", min_value=0.0, value=def_bw_hp, step=1.0, key='bwhp')
    
    with c_tp:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #0ea5e9;"><b>🏗️ OHT Transfer Pumps</b><br><span style='font-size:12px; color:#64748b;'>Surface to Overhead Tanks</span></div>""", unsafe_allow_html=True)
        st.write("")
        tp_count = st.number_input("# of Transfer Pumps", min_value=0, value=def_tp_count, step=1)
        tp_hrs = st.number_input("Avg Daily Runtime (Hrs)", min_value=0, value=max(1, def_tp_hrs), step=1, key='tph')
        tp_hp = st.number_input("Avg Motor Size (HP)", min_value=0.0, value=def_tp_hp, step=1.0, key='tphp')

    with c_stp:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #0ea5e9;"><b>♻️ STP Plant Motors</b><br><span style='font-size:12px; color:#64748b;'>Aeration Blowers & Filtration</span></div>""", unsafe_allow_html=True)
        st.write("")
        stp_count = st.number_input("# of Major STP Motors", min_value=0, value=def_stp_count, step=1)
        stp_hrs = st.number_input("Avg Daily Runtime (Hrs)", min_value=0, value=max(1, def_stp_hrs), step=1, key='stph')
        stp_hp = st.number_input("Avg Motor Size (HP)", min_value=0.0, value=def_stp_hp, step=1.0, key='stphp')

    # Background Math (Converting HP to kW)
    calc_bw_kwh = bw_count * (bw_hp * 0.746) * bw_hrs * 365
    calc_tp_kwh = tp_count * (tp_hp * 0.746) * tp_hrs * 365
    calc_stp_kwh = stp_count * (stp_hp * 0.746) * stp_hrs * 365
    calculated_water_kwh = calc_bw_kwh + calc_tp_kwh + calc_stp_kwh
    
    yearly_water_inr = calculated_water_kwh * blended_rate
    savings_water_kwh = calculated_water_kwh * pillars["Centralized Water & STP"]["savings_pct"] # 50% Reduction
    savings_water_inr = savings_water_kwh * blended_rate

    st.markdown("---")
    
    # 4-Card KPI Row (ROI adjusted for VFD/PLC CapEx)
    wkpi1, wkpi2, wkpi3, wkpi4 = st.columns(4)
    wkpi1.metric("Calculated Annual Load", f"{calculated_water_kwh:,.0f} kWh", "Inventory Match")
    wkpi2.metric("Yearly Water/STP Bill", format_indian_currency(yearly_water_inr), "Current OPEX", delta_color="off")
    wkpi3.metric("Projected IIEMS Savings", format_indian_currency(savings_water_inr), "50% Reduction")
    wkpi4.metric("Est. ROI (Years)", "1.8", "CapEx Payback", delta_color="off")

    st.markdown("---")
    
    # Visual Storytelling Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**1. The MD Penalty Trap: DOL vs VFD Soft-Start**")
        st.markdown("<span style='font-size:12px; color:#64748b;'>Traditional starters pull 600% current on ignition, often triggering peak kVA penalties. VFDs guarantee a smooth 0-to-100% ramp.</span>", unsafe_allow_html=True)
        seconds = np.arange(0, 10, 0.1)
        # DOL spikes to 600% instantly, settles to 100%
        dol_curve = np.where(seconds < 0.5, 0, np.where(seconds < 1.5, 600 * np.exp(-(seconds-0.5)*2), 100))
        # VFD ramps smoothly to 100% over 5 seconds
        vfd_curve = np.where(seconds < 0.5, 0, np.where(seconds < 5.5, 100 * ((seconds-0.5)/5), 100))
        
        fig_start = go.Figure()
        fig_start.add_trace(go.Scatter(x=seconds, y=dol_curve, name="Traditional DOL Starter (600% Spike)", line=dict(color="#ef4444", width=3)))
        fig_start.add_trace(go.Scatter(x=seconds, y=vfd_curve, name="IIEMS VFD Soft-Start", fill="tozeroy", line=dict(color="#0ea5e9", width=3), fillcolor="rgba(14, 165, 233, 0.2)"))
        fig_start.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0), yaxis=dict(title="Starting Current (%)", range=[0, 650]), xaxis=dict(title="Seconds from Ignition"), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_start, use_container_width=True)

    with chart_col2:
        st.markdown("**2. Pump Affinity Law: PID Pressure Control**")
        st.markdown("<span style='font-size:12px; color:#64748b;'>Power consumption drops at the cube of motor speed. Reducing pump frequency to 40Hz cuts power usage by nearly 50%.</span>", unsafe_allow_html=True)
        
        # Affinity Law Curve (Power vs Speed)
        hz = np.arange(25, 51, 1)
        speed_pct = hz / 50.0
        power_pct = (speed_pct ** 3) * 100  # P1/P2 = (N1/N2)^3
        
        fig_aff = go.Figure()
        fig_aff.add_trace(go.Scatter(x=hz, y=power_pct, name="Energy Consumption", mode="lines", fill="tozeroy", line=dict(color="#10b981", width=3), fillcolor="rgba(16, 185, 129, 0.2)"))
        
        # Highlight points
        fig_aff.add_trace(go.Scatter(x=[50], y=[100], mode="markers+text", name="Direct On Line", marker=dict(color="#ef4444", size=10), text=["50 Hz (100% Power)"], textposition="top left"))
        fig_aff.add_trace(go.Scatter(x=[40], y=[51.2], mode="markers+text", name="IIEMS Modulated", marker=dict(color="#3b82f6", size=10), text=["40 Hz (51% Power)"], textposition="top left"))
        
        fig_aff.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0), yaxis=dict(title="Power Draw (%)", range=[0, 120]), xaxis=dict(title="Motor Frequency (Hz)"), showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_aff, use_container_width=True)

# --- TAB 4: ELEVATOR NETWORK ---
# --- TAB 4: ELEVATOR NETWORK ---
with tab4:
    st.markdown("### 🛗 Elevator Network & Deep Sleep Standby")
    st.markdown("A bank of modern elevators (OTIS, Schindler, Johnson) draws massive standby power to keep cabin lights, ventilation, and displays active 24/7. IIEMS forces 'Deep Sleep' during idle periods, dropping standby draw by up to 90%. Furthermore, we continuously map the **Active Power vs. Lifecycle Curve** to identify mechanical degradation (bad actors) before catastrophic failure.")
    
    actual_lift_kwh = pillars["Elevator Network"]["kwh"]
    is_mega = "Mega" in active_tier or "Large" in active_tier
    is_small = "Small" in active_tier
    
    # Intelligent Defaults based on Tier sizes (Matching Galaxy's 14 lifts for Tier 4)
    def_towers = 8 if is_mega else (6 if is_small else 3)
    def_total_lifts = 32 if is_mega else (14 if is_small else 6)
    
    # Reverse Engineer the active hours to perfectly match the allocated Tier load
    standby_watts = 250.0
    active_kw = 7.5
    
    # Assume 20 hours of standby, 4 hours of total active motor run-time per day as baseline
    standby_kwh_target = def_total_lifts * (standby_watts / 1000) * 20 * 365
    active_kwh_target = actual_lift_kwh - standby_kwh_target
    
    def_active_hrs = int(active_kwh_target / (def_total_lifts * active_kw * 365)) if active_kwh_target > 0 else 2
    def_idle_hrs = 24 - max(1, def_active_hrs)

    # 3-Column Input Layout
    c_lift1, c_lift2, c_lift3 = st.columns(3)
    
    with c_lift1:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #8b5cf6;"><b>🏢 Fleet Inventory</b><br><span style='font-size:12px; color:#64748b;'>OTIS, Schindler, Johnson</span></div>""", unsafe_allow_html=True)
        st.write("")
        towers = st.number_input("# of Towers / Blocks", min_value=1, value=def_towers, step=1)
        total_lifts = st.number_input("Total Elevators", min_value=1, value=def_total_lifts, step=1)

    with c_lift2:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #8b5cf6;"><b>⏱️ Daily Usage Profile</b><br><span style='font-size:12px; color:#64748b;'>Active Motor vs Idle Time</span></div>""", unsafe_allow_html=True)
        st.write("")
        active_hrs = st.number_input("Avg Active Hours/Day", min_value=0, value=max(1, def_active_hrs), step=1)
        idle_hrs = st.number_input("Avg Idle Hours/Day", min_value=0, value=max(1, def_idle_hrs), step=1, disabled=True)
        lift_kw = st.number_input("Avg Motor Draw (kW)", min_value=0.0, value=active_kw, step=0.5)

    with c_lift3:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #8b5cf6;"><b>💤 Standby Power</b><br><span style='font-size:12px; color:#64748b;'>Lights, Fans, Inverter Drives</span></div>""", unsafe_allow_html=True)
        st.write("")
        trad_standby = st.number_input("Traditional Standby (W)", min_value=0, value=int(standby_watts), step=10)
        iiems_standby = st.number_input("IIEMS Deep Sleep (W)", min_value=0, value=25, step=5)
        st.info(f"**Target Savings:** {pillars['Elevator Network']['savings_pct']*100:.0f}% of total lift load.")

    # Background Math
    calc_active_kwh = total_lifts * lift_kw * active_hrs * 365
    calc_standby_kwh = total_lifts * (trad_standby / 1000) * (24 - active_hrs) * 365
    calculated_lift_kwh = calc_active_kwh + calc_standby_kwh
    
    yearly_lift_inr = calculated_lift_kwh * blended_rate
    savings_lift_kwh = calculated_lift_kwh * pillars["Elevator Network"]["savings_pct"] 
    savings_lift_inr = savings_lift_kwh * blended_rate

    st.markdown("---")
    
    # 4-Card KPI Row (ROI for API Integrations & Relays is fast)
    lkpi1, lkpi2, lkpi3, lkpi4 = st.columns(4)
    lkpi1.metric("Calculated Annual Load", f"{calculated_lift_kwh:,.0f} kWh", "Inventory Match")
    lkpi2.metric("Yearly Elevator Bill", format_indian_currency(yearly_lift_inr), "Current OPEX", delta_color="off")
    lkpi3.metric("Projected IIEMS Savings", format_indian_currency(savings_lift_inr), "40% Reduction")
    lkpi4.metric("Est. ROI (Years)", "1.5", "CapEx Payback", delta_color="off")

    st.markdown("---")
    
    # Visual Storytelling Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**1. Peak Traffic & Deep Sleep Windows**")
        st.markdown("<span style='font-size:12px; color:#64748b;'>IIEMS identifies high-traffic zones (Morning/Evening commute) and forces Deep Sleep during the massive midday and overnight idle windows.</span>", unsafe_allow_html=True)
        
        hours = np.arange(0, 24, 1)
        # Create a bimodal traffic curve (Peaks at 8 AM and 6 PM)
        traffic = np.exp(-0.2 * (hours - 8.5)**2) * 80 + np.exp(-0.15 * (hours - 18)**2) * 90 + 5
        
        # Sleep activation is inversely proportional to traffic
        sleep_mode = np.where(traffic < 20, 100, 0)
        
        fig_traffic = make_subplots(specs=[[{"secondary_y": True}]])
        fig_traffic.add_trace(go.Scatter(x=hours, y=traffic, name="Lift Traffic (Trips/Hr)", mode="lines", fill="tozeroy", line=dict(color="#64748b", width=2), fillcolor="rgba(100, 116, 139, 0.2)"), secondary_y=False)
        fig_traffic.add_trace(go.Scatter(x=hours, y=sleep_mode, name="Deep Sleep Active", mode="lines", line_shape="hv", fill="tozeroy", line=dict(color="#8b5cf6", width=2), fillcolor="rgba(139, 92, 246, 0.2)"), secondary_y=True)
        
        fig_traffic.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0), xaxis=dict(tickmode='linear', dtick=2), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1), plot_bgcolor='rgba(0,0,0,0)')
        fig_traffic.update_yaxes(title_text="Traffic Density", secondary_y=False, showgrid=False)
        fig_traffic.update_yaxes(title_text="Sleep Status", secondary_y=True, showgrid=False, range=[0, 110], tickvals=[0, 100], ticktext=["OFF", "ON"])
        st.plotly_chart(fig_traffic, use_container_width=True)

    with chart_col2:
        st.markdown("**2. Life vs. Power Consumption Curve (Asset Health)**")
        st.markdown("<span style='font-size:12px; color:#64748b;'>Mechanical wear (guide friction, rope tension) increases power draw over time. IIEMS flags deviating 'bad actors' for targeted maintenance.</span>", unsafe_allow_html=True)
        
        years = np.arange(1, 16, 1)
        # Normal degradation: Starts at 7.5kW, slowly creeps to 8.5kW over 15 years
        normal_curve = 7.5 + (years * 0.06)
        
        # Bad Actor: Starts normal, starts failing at year 5, spikes to 11kW by year 10
        bad_actor = np.where(years <= 4, normal_curve, 7.5 + (years * 0.06) + ((years-4)**1.6 * 0.25))
        
        fig_life = go.Figure()
        fig_life.add_trace(go.Scatter(x=years, y=normal_curve, name="Healthy Fleet Avg", mode="lines", line=dict(color="#10b981", width=3)))
        fig_life.add_trace(go.Scatter(x=years, y=bad_actor, name="Unhealthy Lift (Friction/Wear)", mode="lines", line=dict(color="#ef4444", width=3, dash="dash")))
        
        # Alert Marker
        fig_life.add_trace(go.Scatter(x=[8], y=[bad_actor[7]], mode="markers+text", name="IIEMS Maintenance Alert", marker=dict(color="#f59e0b", size=12, symbol="star"), text=["  Service Alert!"], textposition="middle right"))
        
        fig_life.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0), yaxis=dict(title="Active Draw (kW)", range=[6, 12]), xaxis=dict(title="Asset Age (Years)", tickmode='linear', dtick=2), legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_life, use_container_width=True)

# --- TAB 5: POOL & CLUBHOUSE ---
# --- TAB 5: POOL & CLUBHOUSE ---
with tab5:
    st.markdown("### 🏊 Pool & Amenities Management")
    st.markdown("With major HVAC managed centrally, the Clubhouse footprint is reduced to specialized amenities: **Seasonal Swimming Pools**, dedicated **Clubhouse Lighting** (distinct from basements/corridors), and **3rd-Party Vendor Plugs** (cafeterias, spas). IIEMS enforces strict seasonal schedules—completely shutting down pool filtration from mid-November to mid-February—and introduces sub-metering for vendor bill-backs.")
    
    actual_club_kwh = pillars["Pool & Clubhouse"]["kwh"]
    is_mega = "Mega" in active_tier or "Large" in active_tier
    is_small = "Small" in active_tier
    
    # Intelligent Defaults
    def_pumps = 6 if is_mega else (3 if is_small else 4)
    def_pump_hp = 5.0 if is_mega else 3.0
    
    def_lights = 250 if is_mega else (60 if is_small else 120)
    def_vendors = 4 if is_mega else (1 if is_small else 2)
    
    # Reverse Engineer runtimes to match allocated load (50% Pool, 30% Lighting, 20% Vendors)
    pool_kwh_target = actual_club_kwh * 0.50
    light_kwh_target = actual_club_kwh * 0.30
    vendor_kwh_target = actual_club_kwh * 0.20
    
    # Pool only runs 9 months of the year (~275 days) due to mid-Nov to mid-Feb shutdown
    pool_active_days = 275 
    
    def_pool_hrs = int(pool_kwh_target / (def_pumps * (def_pump_hp * 0.746) * pool_active_days)) if def_pumps > 0 else 0
    def_light_hrs = int(light_kwh_target / (def_lights * 0.015 * 365)) if def_lights > 0 else 0
    def_vendor_kw = (vendor_kwh_target / (def_vendors * 10 * 365)) if def_vendors > 0 else 0.0

    # 3-Column Input Layout
    c_pool, c_light, c_vendor = st.columns(3)
    
    with c_pool:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #ec4899;"><b>🌊 Pool Filtration</b><br><span style='font-size:12px; color:#64748b;'>Seasonal (Off Mid Nov - Mid Feb)</span></div>""", unsafe_allow_html=True)
        st.write("")
        pool_pumps = st.number_input("Total Pool Pumps", min_value=0, value=def_pumps, step=1)
        pool_hrs = st.number_input("Active Daily Runtime (Hrs)", min_value=0, value=max(1, def_pool_hrs), step=1, key='phrs')
        pool_hp = st.number_input("Avg Motor Size (HP)", min_value=0.0, value=def_pump_hp, step=0.5)

    with c_light:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #ec4899;"><b>💡 Clubhouse Lighting</b><br><span style='font-size:12px; color:#64748b;'>Banquet, Gym & Yoga Interiors</span></div>""", unsafe_allow_html=True)
        st.write("")
        club_lights = st.number_input("Total Fixtures", min_value=0, value=def_lights, step=10)
        light_hrs = st.number_input("Avg Daily Runtime (Hrs)", min_value=0, value=max(1, def_light_hrs), step=1, key='lhrs')
        light_watts = st.number_input("Wattage per Light (W)", min_value=0, value=15, step=1)

    with c_vendor:
        st.markdown("""<div style="background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-top: 4px solid #ec4899;"><b>🏪 Vendor Plugs</b><br><span style='font-size:12px; color:#64748b;'>Cafeteria, Spa, Kiosks</span></div>""", unsafe_allow_html=True)
        st.write("")
        vendor_count = st.number_input("# of Sub-Vendors", min_value=0, value=def_vendors, step=1)
        vendor_kw = st.number_input("Avg Draw per Vendor (kW)", min_value=0.0, value=max(0.5, def_vendor_kw), step=0.1)
        vendor_hrs = st.number_input("Daily Operating Hours", min_value=0, value=10, step=1)

    # Background Math
    calc_pool_kwh = pool_pumps * (pool_hp * 0.746) * pool_hrs * pool_active_days
    calc_light_kwh = club_lights * (light_watts / 1000) * light_hrs * 365
    calc_vendor_kwh = vendor_count * vendor_kw * vendor_hrs * 365
    calculated_amenity_kwh = calc_pool_kwh + calc_light_kwh + calc_vendor_kwh
    
    yearly_amenity_inr = calculated_amenity_kwh * blended_rate
    savings_amenity_kwh = calculated_amenity_kwh * pillars["Pool & Clubhouse"]["savings_pct"] # 50% Reduction via isolation & submetering
    savings_amenity_inr = savings_amenity_kwh * blended_rate

    st.markdown("---")
    
    # 4-Card KPI Row
    akpi1, akpi2, akpi3, akpi4 = st.columns(4)
    akpi1.metric("Calculated Annual Load", f"{calculated_amenity_kwh:,.0f} kWh", "Inventory Match")
    akpi2.metric("Yearly Amenities Bill", format_indian_currency(yearly_amenity_inr), "Current OPEX", delta_color="off")
    akpi3.metric("Projected IIEMS Savings", format_indian_currency(savings_amenity_inr), "50% Reduction")
    akpi4.metric("Est. ROI (Years)", "1.1", "CapEx Payback", delta_color="off")

    st.markdown("---")
    
    # Visual Storytelling Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**1. Seasonal Operations (Pool Filtration)**")
        st.markdown("<span style='font-size:12px; color:#64748b;'>IIEMS digitally locks out pool filtration equipment during the winter months (Mid-Nov through Mid-Feb), preventing accidental manual usage.</span>", unsafe_allow_html=True)
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        # Multipliers based on strict seasonality (0.5 for split months)
        season_multipliers = [0, 0.5, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 0]
        
        monthly_pool_kwh = (calc_pool_kwh / 9) # Divide annual by the 9 active months
        pool_chart_data = [monthly_pool_kwh * m for m in season_multipliers]
        
        fig_season = go.Figure()
        fig_season.add_trace(go.Bar(x=months, y=pool_chart_data, marker_color=np.where(np.array(season_multipliers) < 1, '#94a3b8', '#0ea5e9')))
        
        fig_season.add_annotation(x='Jan', y=monthly_pool_kwh*0.5, text="WINTER LOCKOUT", showarrow=False, textangle=-90, font=dict(color="#ef4444", size=10))
        fig_season.add_annotation(x='Dec', y=monthly_pool_kwh*0.5, text="WINTER LOCKOUT", showarrow=False, textangle=-90, font=dict(color="#ef4444", size=10))
        
        fig_season.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0), yaxis=dict(title="Filtration Load (kWh)"), showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_season, use_container_width=True)

    with chart_col2:
        st.markdown("**2. Vendor Sub-Metering & Accountability**")
        st.markdown("<span style='font-size:12px; color:#64748b;'>Independent vendors (spas, cafes) operating inside the clubhouse often draw heavily on the community's master meter. IIEMS sub-meters these lines for direct bill-back recovery.</span>", unsafe_allow_html=True)
        
        # Financial breakdown
        resident_burden = (calc_pool_kwh + calc_light_kwh) * blended_rate
        vendor_burden = calc_vendor_kwh * blended_rate
        
        fig_vendor = go.Figure(data=[go.Pie(
            labels=['Community Absorbed OPEX', 'Vendor Bill-Backs (Recovered)'],
            values=[resident_burden, vendor_burden],
            hole=.5,
            marker_colors=['#cbd5e1', '#10b981'],
            textinfo='label+percent'
        )])
        
        fig_vendor.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0), showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_vendor, use_container_width=True)