import streamlit as st
import os

# Configure the main page layout
st.set_page_config(
    page_title="IIEMS Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    /* 1. Main App Background: A very soft cool-gray to make white cards pop */
    .stApp {
        background-color: #f1f5f9;
    }
    
    /* 2. Sidebar Navigation: A distinctly darker slate for clear separation */
    [data-testid="stSidebar"] {
        background-color: #e2e8f0 !important;
    }
    
    /* 3. Deepen the default text color so it remains crisp */
    .stApp, [data-testid="stSidebar"] {
        color: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: LOGO & NAVIGATION ---
if os.path.exists("assets/logo.png"):
    st.sidebar.image("assets/logo.png", use_container_width=True)

st.sidebar.title("⚡ Navigation")

# 💎 Premium Brand Menu
page_selection = st.sidebar.radio(
    "Go to:", 
    ["Executive Command Center", "MD Sentinel", "Asset Efficiency", "IAQ Guard"] 
)

# --- GLOBAL HEADER ---
st.markdown("""
<div style="
    background-image: linear-gradient(to right, rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.3)), url('https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2000&auto=format&fit=crop');
    background-size: cover;
    background-position: center 60%;
    padding: 40px 40px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
">
    <h1 style="color: white; margin: 0; font-size: 3.2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">IIEMS Command Center</h1>
    <p style="color: #cbd5e1; font-size: 1.3rem; margin-top: 5px; margin-bottom: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">Intelligent Energy Management for High-Rise Communities</p>
</div>
""", unsafe_allow_html=True)

# --- HORIZONTAL COMMUNITY SELECTOR (Equidistant Tabs) ---
st.markdown("### 🏢 Select Community Profile")

tiers = [
    "Tier 1 - Mega (1,500+ Units)", 
    "Tier 2 - Large (500-1,500 Units)", 
    "Tier 3 - Mid (200-500 Units)", 
    "Tier 4 - Small (<200 Units)"
]

# Initialize session state if it doesn't exist
if 'active_tier' not in st.session_state:
    st.session_state['active_tier'] = tiers[1]

# Create 4 equal columns for the buttons
cols = st.columns(4)

# Custom CSS to style the buttons so they look like accent blocks
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-weight: bold;
        border-radius: 8px;
        transition: all 0.3s;
    }
</style>
""", unsafe_allow_html=True)

for idx, tier in enumerate(tiers):
    with cols[idx]:
        is_active = (st.session_state['active_tier'] == tier)
        # If active, make the button Red/Accent color. If not, make it secondary.
        button_type = "primary" if is_active else "secondary"
        
        if st.button(tier, key=f"tier_btn_{idx}", type=button_type, use_container_width=True):
            st.session_state['active_tier'] = tier
            st.rerun()

st.markdown("---")

# --- PAGE ROUTER ---
if page_selection == "Executive Command Center":
    with open("views/01_command_center.py", encoding="utf-8") as f:
        exec(f.read())
elif page_selection == "MD Sentinel":
    with open("views/02_md_sentinel.py", encoding="utf-8") as f:
        exec(f.read())
elif page_selection == "Asset Efficiency":
    with open("views/03_asset_efficiency.py", encoding="utf-8") as f:
        exec(f.read())
elif page_selection == "IAQ Guard":
    with open("views/04_iaq_guard.py", encoding="utf-8") as f:
        exec(f.read())