import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
from datetime import datetime

# ================== CONFIG ==================
BACKEND_BASE = "http://localhost:3000"
EXECUTIONS_API = f"{BACKEND_BASE}/executions"
LEADS_API = f"{BACKEND_BASE}/leads"
STATS_API = f"{BACKEND_BASE}/stats"
LEAD_GEN_API = f"{BACKEND_BASE}/lead-gen"

st.set_page_config(
    page_title="n8n CRM & Sales Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== AUTHENTICATION STATE & PERSISTENCE ==================
import os
import json

SESSION_FILE = ".session"

def save_session(token, user):
    with open(SESSION_FILE, "w") as f:
        json.dump({"token": token, "user": user}, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# Initialize Session
if "token" not in st.session_state:
    saved = load_session()
    if saved:
        st.session_state.token = saved["token"]
        st.session_state.user = saved["user"]
    else:
        st.session_state.token = None
        st.session_state.user = None

if "user" not in st.session_state:
     st.session_state.user = None

def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# ================== SIDEBAR NAVIGATION ==================
import base64
import os

def get_sidebar_img_b64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# Sidebar logic resides below authentication check

# ================== LOGIN / REGISTER UI ==================
if not st.session_state.token:
    # Premium Login UI
    st.markdown("""
    <style>
    /* Full Page Center Background */
    .stApp {
        background: #e0e5ec !important; /* Neumorphic Base */
    }
    
    /* Hide Default Header/Decoration */
    header { visibility: hidden; }
    div[data-testid="stDecoration"] { display: none; }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background-color: #e0e5ec !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: inset 3px 3px 6px #b8b9be, inset -3px -3px 6px #ffffff !important;
        color: #4d5b6b !important;
        padding: 10px 15px !important;
    }
    .stTextInput > div > div > input:focus {
        border: 1px solid #2196F3 !important; /* Subtle focus */
    }
    
    /* Buttons (Primary) */
    div[data-testid="stButton"] button {
        background: linear-gradient(145deg, #2196F3, #1976D2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 5px 5px 10px #b8b9be, -5px -5px 10px #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 7px 7px 14px #b8b9be, -7px -7px 14px #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Centering Layout using Columns
    _, col_center, _ = st.columns([1, 1.5, 1])
    
    with col_center:
        # 1. Logo (Text Based for consistency)
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="
                font-family: 'Inter', sans-serif;
                font-size: 2.5rem;
                font-weight: 800;
                letter-spacing: -1px;
                color: #4d5b6b;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 5px;
            ">
                SHDPIXEL
            </div>
            <div style="font-size: 0.85rem; color: #888; font-weight: 500; letter-spacing: 2px; text-transform: uppercase;">
                CRM & Sales
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Login Form (Simplified, No Tabs, No Card Wrapper)
        st.markdown("<h3 style='text-align: center; color: #4d5b6b; margin-bottom: 20px; font-weight: 600;'>Login</h3>", unsafe_allow_html=True)
        
        l_email = st.text_input("Email Address", key="login_email")
        l_pass = st.text_input("Password", type="password", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True) # Spacer
        
        if st.button("Log In", type="primary", use_container_width=True, key="login_btn"):
            try:
                res = requests.post(f"{BACKEND_BASE}/auth/login", json={"email": l_email, "password": l_pass})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["token"]
                    st.session_state.user = data["user"]
                    save_session(data["token"], data["user"]) 
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error(res.json().get("error", "Login failed"))
            except Exception as e:
                st.error(f"Connection error: {e}")

    st.stop() # 🛑 STOP EXECUTION HERE IF NOT LOGGED IN

# ================== STYLES ==================

# 1. COMMON STYLES (Layout, Fonts, Transitions - Always Applied)
# ================== STYLES ==================

# 1. COMMON STYLES (Layout, Fonts, Transitions - Always Applied)
# 1. COMMON STYLES (Layout, Fonts, Transitions - Always Applied)
COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Clean Header - Keep Toggle Button Visible */
header[data-testid="stHeader"] {
    background: transparent !important;
}
/* Hide the colored decoration bar */
div[data-testid="stDecoration"] {
    display: none;
}
/* Keep the hamburger menu visible but maybe style it? */
/* Streamlit's default is fine, just needs to be visible. */

/* Sidebar Radius Adjustments */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 10px 16px;
    border-radius: 8px;
    margin-bottom: 2px;
    border: 1px solid transparent;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    transform: translateX(3px);
}
/* Hide Radio Circles */
div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
div[role="radiogroup"] label {
    padding-left: 12px !important;
}
</style>
"""

# 2. LIGHT MODE STYLES (Strictly for Light Mode)
LIGHT_CSS = """
<style>
/* Main Background - Neumorphism Base */
.stApp {
    background-color: #e0e5ec !important;
    background-image: none !important;
    color: #4d5b6b !important;
}

/* Sidebar - Neumorphism */
section[data-testid="stSidebar"] {
    background-color: #e0e5ec !important;
    border-right: none !important;
    box-shadow: 5px 0 15px rgba(0,0,0,0.05); /* Soft separation */
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {
    color: #4d5b6b !important;
}

/* Navigation - Uniform Neumorphic Pills */
/* Container adjustment */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 16px; /* Increases spacing between buttons */
    padding: 15px 10px;
}

/* Default State: Soft 3D Button */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: #e0e5ec !important;
    border: none !important;
    border-radius: 12px !important;
    /* Soft Outer Shadow for 3D effect */
    box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
    color: #4d5b6b !important;
    padding: 12px 20px !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    transition: all 0.2s ease;
    margin: 0 !important;
}

/* Hover State */
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    transform: translateY(-2px);
    color: #2196F3 !important;
    box-shadow: 8px 8px 16px #b8b9be, -8px -8px 16px #ffffff !important;
}

/* Active/Selected State: Pressed (Inset) */
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    color: #2196F3 !important; /* Blue active text */
    font-weight: 700;
    /* Inner Shadow for Pressed look */
    box-shadow: inset 4px 4px 8px #b8b9be, inset -4px -4px 8px #ffffff !important;
}

/* Inputs */
.stTextInput > div > div > input, .stSelectbox > div > div > div, .stTextArea > div > div > textarea {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
}

/* Cards */
/* Cards - Neumorphism */
.metric-card {
    background-color: #e0e5ec;
    box-shadow: 9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5);
    border-radius: 20px;
    border: none;
    color: #4d5b6b;
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 12px 12px 20px rgb(163,177,198,0.7), -12px -12px 20px rgba(255,255,255, 0.6);
}
.meeting-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border: 1px solid #e0e0e0;
    border-left: 3px solid #4CAF50;
    color: #1a1a1a;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.meeting-title { 
    color: #1a1a1a !important; 
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 2px;
}
.meeting-company { 
    color: #666 !important;
    font-size: 0.85rem;
    margin-bottom: 4px;
}
.meeting-date {
    color: #4CAF50 !important;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* DataFrames */
div[data-testid="stDataFrame"] {
    background-color: #ffffff !important;
    border: 1px solid #eee !important;
}
div[data-testid="stDataFrame"] th {
    background-color: #f8f9fa !important;
    color: #444 !important;
}
div[data-testid="stDataFrame"] td {
    background-color: #ffffff !important;
    color: #333 !important;
    border-bottom: 1px solid #f0f0f0 !important;
}

/* Data Editor (Edit Mode) - Minimal Light Mode Override */
/* Note: Data editor uses canvas rendering - CSS has limited effect */
/* We only style the container, not the canvas itself */
div[data-testid="stDataEditor"] {
    background-color: #ffffff !important;
}


/* File Uploader - Light Mode */
div[data-testid="stFileUploader"] {
    background-color: #ffffff !important;
}
div[data-testid="stFileUploader"] > div {
    background-color: #f8f9fa !important;
    border: 2px dashed #cbd5e0 !important;
    border-radius: 8px !important;
}
div[data-testid="stFileUploader"] section {
    background-color: #f8f9fa !important;
    color: #1a1a1a !important;
}
div[data-testid="stFileUploader"] small {
    color: #4a5568 !important;
}
div[data-testid="stFileUploader"] svg {
    fill: #4a5568 !important;
}
/* File uploader text - make it darker */
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] label {
    color: #2d3748 !important;
}
/* File uploader buttons */
div[data-testid="stFileUploader"] button {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #cbd5e0 !important;
}
div[data-testid="stFileUploader"] button:hover {
    background-color: #f1f3f5 !important;
}


/* Expander - Light Mode */
/* Expander - Neumorphic */
div[data-testid="stExpander"] {
    background-color: #e0e5ec !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 9px 9px 16px rgb(163,177,198,0.5), -9px -9px 16px rgba(255,255,255, 0.5) !important;
    margin-bottom: 20px;
}
div[data-testid="stExpander"] summary {
    background-color: transparent !important;
    color: #4d5b6b !important;
    font-weight: 600;
}
div[data-testid="stExpander"] summary:hover {
    color: #2196F3 !important;
}
div[data-testid="stExpander"] div[role="button"] p {
    font-size: 1rem !important;
}

/* Slider - Neumorphic Track */
div[data-testid="stSlider"] > div > div > div > div {
    background-color: #e0e5ec !important; /* Track bg */
    border-radius: 10px;
    box-shadow: inset 3px 3px 6px #b8b9be, inset -3px -3px 6px #ffffff;
}
div[data-testid="stSlider"] > div > div > div > div > div { 
    background-color: #2196F3 !important; /* Filled part */
}
/* Slider Thumb */
div[data-testid="stSlider"] > div > div > div > div[role="slider"] {
    background-color: #e0e5ec !important;
    border: 2px solid #f0f0f3;
    box-shadow: 2px 2px 4px #b8b9be, -2px -2px 4px #ffffff;
}

/* Code blocks */
code {
    background-color: #f1f3f5 !important;
    color: #1a1a1a !important;
}
pre {
    background-color: #f8f9fa !important;
    border: 1px solid #e0e0e0 !important;
}


/* Buttons - Neumorphic */
/* Buttons - Neumorphic FORCE */
/* Buttons - Neumorphic FORCE ALL */
div.stButton > button, 
div.stButton > button[kind="secondary"],
div.stButton > button[kind="primary"] {
    background-color: #e0e5ec !important;
    background-image: none !important;
    color: #4d5b6b !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 6px 6px 10px #b8b9be, -6px -6px 10px #ffffff !important;
    transition: all 0.2s ease;
    font-weight: 600 !important;
}

div.stButton > button:hover,
div.stButton > button[kind="secondary"]:hover,
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    color: #2196F3 !important;
    background-color: #e0e5ec !important;
    box-shadow: 7px 7px 12px #b0b1b6, -7px -7px 12px #ffffff !important;
    border: none !important;
}

div.stButton > button:active, 
div.stButton > button:focus:not(:active),
div.stButton > button[kind="secondary"]:active,
div.stButton > button[kind="primary"]:active {
    box-shadow: inset 3px 3px 6px #b8b9be, inset -3px -3px 6px #ffffff !important;
    transform: translateY(1px);
    color: #2196F3 !important;
    background-color: #e0e5ec !important;
    border: none !important;
}

/* Primary Distinction - Just a subtle blue ring inset */
div.stButton > button[kind="primary"] {
    box-shadow: 6px 6px 10px #b8b9be, -6px -6px 10px #ffffff, inset 0 0 0 1px rgba(33, 150, 243, 0.5) !important;
}

/* Focus States */

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > div:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #1976d2 !important;
    box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1) !important;
    outline: none !important;
}

/* Calendar Buttons */
.cal-btn {
    background: linear-gradient(90deg, #2E7D32 0%, #43A047 100%) !important;
    color: white !important;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    text-decoration: none !important;
    display: inline-block;
    font-size: 0.85rem;
    transition: all 0.2s;
}
.cal-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Radio Buttons - Main Area */
div[role="radiogroup"] label {
    color: #1a1a1a !important;
}

/* Streamlit Alerts */
div[data-testid="stAlert"] {
    background-color: #fff !important;
    border: 1px solid #e0e0e0 !important;
    color: #1a1a1a !important;
}

/* Progress Bar */
div[data-testid="stProgress"] > div > div {
    background-color: #1976d2 !important;
}

/* Radio Buttons Styling - Make them visible */
/* Radio Buttons Styling - Modern List View */
div[role="radiogroup"] {
    gap: 6px !important;
}
div[role="radiogroup"] label {
    background-color: transparent !important;
    border: none !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    color: #4a5568 !important;
    margin-bottom: 2px !important;
    transition: all 0.2s ease;
}
div[role="radiogroup"] label[data-checked="true"] {
    background-color: #E3F2FD !important; /* Light Blue Active */
    color: #0D47A1 !important; /* Deep Blue Text */
    border: none !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
div[role="radiogroup"] label:hover {
    background-color: #F1F5F9 !important; /* Light Hover */
    transform: translateX(4px);
    color: #1a1a1a !important;
}
/* Force text visibility in radio labels */
div[role="radiogroup"] label span,
div[role="radiogroup"] label p,
div[role="radiogroup"] label div {
    color: inherit !important;
}

</style>
"""

# 3. DARK MODE STYLES (Strictly for Dark Mode)
DARK_CSS = """
<style>
/* Main Background */
.stApp {
    background: radial-gradient(circle at top left, #141414 0%, #0E1117 100%) !important;
    color: #FAFAFA !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: rgba(30, 30, 35, 0.95) !important;
    border-right: 1px solid #333 !important;
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {
    color: #E0E0E0 !important;
}

/* Navigation - Active Item */
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(90deg, #333 0%, #333 100%) !important;
    color: #FFB74D !important; /* Amber text */
    border: 1px solid #444 !important;
    border-radius: 8px;
    /* border-left: 4px solid #ffb74d !important; This was the old style, removing for pill look */
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: transparent !important;
}

/* Inputs */
.stTextInput > div > div > input, .stSelectbox > div > div > div, .stTextArea > div > div > textarea {
    background-color: #262730 !important;
    color: #E0E0E0 !important;
    border: 1px solid #444 !important;
}

/* Cards */
.metric-card {
    background: linear-gradient(145deg, #1E1E1E 0%, #252525 100%) !important;
    border: 1px solid #333 !important;
    color: #FAFAFA;
}
.meeting-card {
    background: linear-gradient(135deg, #1E1E1E 0%, #252525 100%) !important;
    border: 1px solid #333 !important;
    border-left: 3px solid #4CAF50 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 10px;
}
.meeting-title { 
    color: #FFF !important; 
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 2px;
}
.meeting-company { 
    color: #BBB !important;
    font-size: 0.85rem;
    margin-bottom: 4px;
}
.meeting-date {
    color: #4CAF50 !important;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* DataFrames */
div[data-testid="stDataFrame"] {
    background-color: #1a1a1d !important;
    border: 1px solid #333 !important;
}
div[data-testid="stDataFrame"] table {
    background-color: #1a1a1d !important;
}
div[data-testid="stDataFrame"] th {
    background-color: #222 !important;
    color: #64B5F6 !important;
    border-bottom: 2px solid #444 !important;
}
div[data-testid="stDataFrame"] td {
    background-color: #1a1a1d !important;
    color: #eee !important;
    border-bottom: 1px solid #333 !important;
}

/* Buttons */
div.stButton > button {
    background-color: #2D2D30 !important;
    color: #E0E0E0 !important;
    border: 1px solid #444 !important;
}
div.stButton > button:hover {
    border-color: #F39C12 !important;
    color: #F39C12 !important;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #FF8F00 0%, #FFB300 100%) !important;
    color: white !important;
    border: none !important;
}

/* Focus States */
.stTextInput > div > div > input:focus,
.stSelectbox > div > div > div:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #64B5F6 !important;
    box-shadow: 0 0 0 3px rgba(100, 181, 246, 0.2) !important;
    outline: none !important;
}

/* Calendar Buttons */
.cal-btn {
    background: linear-gradient(90deg, #2E7D32 0%, #43A047 100%) !important;
    color: white !important;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    text-decoration: none !important;
    display: inline-block;
    font-size: 0.85rem;
    transition: all 0.2s;
}
.cal-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

/* Radio Buttons - Main Area */
div[role="radiogroup"] label {
    color: #E0E0E0 !important;
}

/* Streamlit Alerts */
div[data-testid="stAlert"] {
    background-color: #1E1E1E !important;
    border: 1px solid #444 !important;
    color: #E0E0E0 !important;
}

/* Progress Bar */
div[data-testid="stProgress"] > div > div {
    background-color: #FF8F00 !important;
}

/* Meeting Date Color */
.meeting-date { color: #4CAF50 !important; }

/* Radio Buttons Styling - Make them visible */
/* Radio Buttons Styling - Modern List View */
div[role="radiogroup"] {
    gap: 6px !important;
}
div[role="radiogroup"] label {
    background-color: transparent !important;
    border: 1px solid transparent !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    color: #B0B0B0 !important;
    transition: all 0.2s ease;
}
div[role="radiogroup"] label[data-checked="true"] {
    background-color: #2D2D30 !important; /* Dark Grey Active */
    color: #FFB74D !important; /* Amber Text */
    border: 1px solid #444 !important;
}
div[role="radiogroup"] label:hover {
    background-color: #2D2D30 !important;
    border-color: #444 !important;
    color: #E0E0E0 !important;
    transform: translateX(4px);
}
/* Force text visibility in radio labels */
div[role="radiogroup"] label span,
div[role="radiogroup"] label p,
div[role="radiogroup"] label div {
    color: inherit !important;
}

</style>
"""

# ================== HELPER FUNCTIONS ==================
def metric_card(label, value, icon_color="#4CAF50"):
    is_dark = st.session_state.get("theme") == "dark"
    
    if is_dark:
        bg_color = "rgba(30, 41, 59, 0.4)"
        text_main = "#FAFAFA"
        text_sub = "#94a3b8"
        shadow_outer = "none"
        shadow_inner = "none" # Simplify for dark mode or use subtle borders
        border = "1px solid #333"
        inner_circle_bg = "rgba(255,255,255,0.05)"
        inner_circle_shadow = "none"
    else:
        bg_color = "#e0e5ec"
        text_main = "#4d5b6b"
        text_sub = "#8d9bad"
        shadow_outer = "none" # Handled by class usually, but inline here controls structure
        shadow_inner = "inset 6px 6px 12px #a3b1c6, inset -6px -6px 12px #ffffff"
        border = "none"
        inner_circle_bg = "#e0e5ec"
        inner_circle_shadow = "inset 6px 6px 12px #a3b1c6, inset -6px -6px 12px #ffffff"

    # Neumorphic/Modern Circular Design
    html_content = f"""
<div class="metric-card" style="background: {bg_color}; border: {border}; padding: 30px 20px; border-radius: 30px; text-align: center; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <div style="width: 80px; height: 80px; border-radius: 50%; background: {inner_circle_bg}; box-shadow: {inner_circle_shadow}; display: flex; align-items: center; justify-content: center; margin-bottom: 15px;">
        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: {icon_color}; box-shadow: 0 0 10px {icon_color};"></div>
    </div>
    <div style="font-size: 2.2rem; font-weight: 700; color: {text_main}; margin-bottom: 4px;">{value}</div>
    <div style="font-size: 0.9rem; font-weight: 600; color: {text_sub}; text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
    <div style="display: flex; gap: 15px; margin-top: 20px;">
        <div style="width: 30px; height: 10px; border-radius: 10px; background: {inner_circle_bg}; opacity: 0.7;"></div>
        <div style="width: 30px; height: 10px; border-radius: 10px; background: {inner_circle_bg}; opacity: 0.7;"></div>
    </div>
</div>
"""
    # Remove newlines to ensure it treats it as a single html block
    st.markdown(html_content.replace("\n", ""), unsafe_allow_html=True)

def fetch_data(url):
    try:
        r = requests.get(url, headers=get_headers(), timeout=2) # 👈 Added Header
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def update_lead(lead_id, data):
    try:
        requests.put(f"{LEADS_API}/{lead_id}", json=data, headers=get_headers()) # 👈 Added Header
        return True
    except:
        return False

def create_lead(data):
    try:
        requests.post(f"{BACKEND_BASE}/leads", json=data, headers=get_headers()) # 👈 Added Header
        return True
    except:
        return False

# Normalization Helpers
def normalize_text(text):
    if pd.isna(text): return ""
    return str(text).strip().lower()

def normalize_phone(phone):
    if pd.isna(phone): return ""
    s = str(phone).strip()
    # Remove chars
    import re
    s = re.sub(r'[\s\-\+\(\)]', '', s)
    # Remove leading 91 (Indian code) if 12 digits (91 + 10 digits) or just starts with 91 and is long
    if s.startswith('91') and len(s) > 10:
        s = s[2:]
    return s

def delete_lead(lead_id):
    try:
        requests.delete(f"{LEADS_API}/{lead_id}", headers=get_headers()) # 👈 Added Header
        return True
    except:
        return False

import urllib.parse

# ================== STATUS THEME CONFIGURATION ==================
# COLORS UPDATED TO MATCH USER REFERENCE IMAGE (VIBRANT)
STATUS_PALETTE = {
    "Interested":          {"bg": "#DFF5E1", "txt": "#1B5E20"}, # Light Green
    "Not picking":         {"bg": "#F0F0F0", "txt": "#616161"}, # Light Grey
    "Asked to call later": {"bg": "#FFF8E1", "txt": "#8D6E00"}, # Light Yellow
    "Meeting set":         {"bg": "#E3F2FD", "txt": "#0D47A1"}, # Light Blue
    "Meeting Done":        {"bg": "#E0F2F1", "txt": "#004D40"}, # Teal
    "Proposal sent":       {"bg": "#F3E5F5", "txt": "#4A148C"}, # Lavender
    "Follow-up scheduled": {"bg": "#FFE0B2", "txt": "#E65100"}, # Soft Orange
    "Not interested":      {"bg": "#FDECEA", "txt": "#B71C1C"}, # Light Red
    "Closed - Won":        {"bg": "#C8E6C9", "txt": "#1B5E20"}, # Strong Green
    "Closed - Lost":       {"bg": "#ECEFF1", "txt": "#37474F"}, # Soft Dark Grey
    "Generated":           {"bg": "#F5F5F5", "txt": "#616161"}, # Neutral
}

# Add normalized keys to palette (En-dash variants)
STATUS_PALETTE["Closed – Won"] = STATUS_PALETTE["Closed - Won"]
STATUS_PALETTE["Closed – Lost"] = STATUS_PALETTE["Closed - Lost"]

def get_status_colors(theme):
    """
    Returns a dictionary mapping status strings to CSS style strings.
    """
    css_map = {}
    for status, colors in STATUS_PALETTE.items():
        # User defined fixed colors (ignores theme)
        style = f"background-color: {colors['bg']}; color: {colors['txt']}; font-weight: 600; padding: 4px 12px; border-radius: 12px; text-align: center;"
        css_map[status] = style
        
    return css_map

# ================== THEME INJECTION ==================
# ================== THEME INJECTION ==================
if "theme" not in st.session_state:
    st.session_state.theme = "light" # Default to Light (User Requested)

st.markdown(COMMON_CSS, unsafe_allow_html=True)

if st.session_state.theme == "dark":
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# ================== SIDEBAR LAYOUT ==================
# ================== SIDEBAR LAYOUT ==================
# Premium Typography Logo
logo_theme = st.session_state.get("theme", "light")
logo_color = "#FAFAFA" if logo_theme == "dark" else "#1a1a1a"

st.sidebar.markdown(f"""
<div style="text-align: center; margin-bottom: 25px; margin-top: 10px;">
    <div style="
        font-family: 'Inter', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: {logo_color};
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 2px;
    ">
        SHDPIXEL
    </div>
    <div style="font-size: 0.75rem; color: #888; font-weight: 500; letter-spacing: 2px; margin-top: -5px; text-transform: uppercase;">
        CRM & Sales
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) # Spacer

# 1. User Profile Section
if st.session_state.user:
    with st.sidebar.container():
        # Theme-aware colors
        is_dark = st.session_state.theme == "dark"
        p_bg = "rgba(255, 255, 255, 0.05)" if is_dark else "#e0e5ec"
        p_shadow = "none" if is_dark else "inset 3px 3px 7px #cbcced, inset -3px -3px 7px #ffffff"
        p_text_main = "#E0E0E0" if is_dark else "#4d5b6b"
        p_text_sub = "#aaa" if is_dark else "#888"
        p_border = "1px solid #444" if is_dark else "none"
        
        # Role Logic
        user_role = st.session_state.user.get('role', 'User').upper()
        role_color = "#FFC107" if user_role == "HR" else p_text_sub
        role_icon = "👑 " if user_role == "HR" else ""

        st.markdown(f"""
        <div style="
            background: {p_bg};
            padding: 15px;
            border-radius: 15px;
            box-shadow: {p_shadow};
            border: {p_border};
            text-align: center;
            margin-bottom: 20px;
        ">
            <div style="font-size: 1.2rem; font-weight: bold; color: {p_text_main}; margin-bottom: 5px;">
                👤 {st.session_state.user['name']}
            </div>
            <div style="font-size: 0.75rem; color: {role_color}; font-weight: 600; letter-spacing: 1px;">
                {role_icon}{user_role}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("Log Out", key="logout_btn", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            clear_session() 
            st.rerun()

st.sidebar.markdown("---")

# 2. Navigation Section
st.sidebar.markdown("### 📂 Menu")
# Determine Menu Options based on Role
menu_options = ["📊 Dashboard", "🗂 CRM Grid", "📞 Power Dialer", "⚡ Lead Generator", "🖇 Excel Tool"]

if st.session_state.user and st.session_state.user.get('role') == 'HR':
    menu_options.insert(5, "👥 User Management") # Add before/after Excel Tool

page = st.sidebar.radio(
    "Navigate",
    menu_options,
    label_visibility="collapsed"
)

st.sidebar.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True) # Spacer

# 3. Settings Section
with st.sidebar.expander("⚙️ Settings", expanded=True):
    # Theme Toggle
    if st.session_state.theme == "light":
        if st.button("🌙 Dark Mode", use_container_width=True):
            st.session_state.theme = "dark"
            st.rerun()
    else:
        if st.button("☀️ Light Mode", use_container_width=True):
            st.session_state.theme = "light"
            st.rerun()

st.sidebar.markdown("---")



# Hide Decoration Bar Only (Keep Sidebar Toggle)
st.markdown("""
<style>
div[data-testid="stDecoration"] {
    visibility: hidden !important;
}
</style>
""", unsafe_allow_html=True)



# --- UPCOMING MEETINGS WIDGET ---
st.sidebar.markdown("### 📅 Upcoming Meetings")
try:
    # Quick lightweight check
    m_leads_raw = fetch_data(LEADS_API)
    if m_leads_raw:
        m_df = pd.DataFrame(m_leads_raw)
        if "meetingDate" in m_df.columns:
            m_df["meetingDate"] = pd.to_datetime(m_df["meetingDate"], errors='coerce').dt.date
            today = datetime.now().date()
            
            # Filter: Date exists AND is >= Today
            # We treat NaT as null
            future_meetings = m_df[
                (m_df["meetingDate"].notna()) & 
                (m_df["meetingDate"] >= today)
            ].sort_values("meetingDate")
            
            if future_meetings.empty:
                st.sidebar.caption("No upcoming meetings.")
            else:
                for idx, row in future_meetings.iterrows():
                    # Create Link
                    # Re-use logic or quick inline
                    m_date = row["meetingDate"]
                    name = str(row.get("contactName", "Lead")).strip() or "Lead"
                    comp = str(row.get("businessName", "Company")).strip() or "Company"
                    
                    # Generate Link
                    start_str = m_date.strftime("%Y%m%d")
                    end_str = (m_date + pd.Timedelta(days=1)).strftime("%Y%m%d")
                    title = urllib.parse.quote(f"Meeting with {name} ({comp})")
                    details = urllib.parse.quote(f"Phone: {row.get('phone', '')}\nAddress: {row.get('address', '')}")
                    cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&details={details}&dates={start_str}/{end_str}"
                    
                    # Render Card with IMPROVED UI
                    with st.sidebar.container():
                        st.markdown(f"""
                        <div class="meeting-card">
                            <div class="meeting-date">{m_date.strftime('%b %d').upper()}</div>
                            <div class="meeting-title">{name}</div>
                            <div class="meeting-company">{comp}</div>
                            <a href="{cal_url}" target="_blank" class="cal-btn">
                                📅 Add to Calendar
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
except Exception as e:
    # Fail silently to not break main app
    st.sidebar.caption(f"Syncing calendar... ({e})")

# ================== DASHBOARD ==================
if "Dashboard" in page:
# Header Redesign
    from datetime import datetime
    today_str = datetime.now().strftime("%B %d, %Y")
    user_name = st.session_state.user['name'].split()[0] if st.session_state.user else "User"
    
    is_dark = st.session_state.get("theme") == "dark"
    text_main = "#FAFAFA" if is_dark else "#333"
    text_sub = "#aaa" if is_dark else "#666"
    badge_bg = "rgba(33, 150, 243, 0.15)" if is_dark else "#E3F2FD"
    badge_text = "#64B5F6" if is_dark else "#1976d2"

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: end; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 1px solid { 'rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.05)' };">
        <div>
            <div style="font-size: 0.9rem; font-weight: 600; color: {text_sub}; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px;">
                CRM Overview
            </div>
            <div style="font-size: 2.8rem; font-weight: 800; color: {text_main}; letter-spacing: -1.5px; line-height: 1.1;">
                Welcome back,<br><span style="color: {badge_text};">{user_name}</span>.
            </div>
        </div>
        <div style="background: {badge_bg}; color: {badge_text}; padding: 8px 16px; border-radius: 12px; font-weight: 600; font-size: 0.9rem; white-space: nowrap;">
            📅 {today_str}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Fetch ALL leads (Personal + Common) for a complete overview
    leads_personal = fetch_data(f"{LEADS_API}?scope=personal")
    leads_common = fetch_data(f"{LEADS_API}?scope=common")
    
    # Combine results
    leads = leads_personal + leads_common
    df_all = pd.DataFrame(leads)
    
    if df_all.empty:
        st.info("No data available yet.")
    else:
        # Split Data
        # 1. Generated (Fresh leads, unworked)
        df_generated = df_all[df_all['status'] == 'Generated']
        
        # 2. CRM (Everything else)
        df_crm = df_all[df_all['status'] != 'Generated']
        
        # --- SECTION 1: LEAD GENERATION ---
        st.subheader("⚡ Lead Generation (Data Mining)")
        c1, c2, c3 = st.columns(3)
        with c1: metric_card("Fresh Leads Available", len(df_generated), icon_color="#FFC107") # Amber
        with c2: metric_card("Recent Imports", len(df_generated[df_generated['id'].astype(int) > (len(df_all)-10)]), icon_color="#00BCD4") # Cyan
        
        # --- SECTION 2: CRM PIPELINE ---
        st.markdown("---")
        st.subheader("💼 Active Pipeline (CRM)")
        
        # Calculate CRM specific metrics
        crm_total = len(df_crm)
        hot_leads = len(df_crm[df_crm['priority'] == 'HOT'])
        meetings = len(df_crm[df_crm['status'].str.contains("Meeting", case=False, na=False)])
        closed_won = len(df_crm[df_crm['status'] == 'Closed - Won'])
        
        c_a, c_b, c_c, c_d = st.columns(4)
        with c_a: metric_card("In Pipeline", crm_total, icon_color="#2196F3") # Blue
        with c_b: metric_card("Hot Opportunities", hot_leads, icon_color="#FF5722") # Orange
        with c_c: metric_card("Meetings Set", meetings, icon_color="#9C27B0") # Purple
        with c_d: metric_card("Closed Won", closed_won, icon_color="#4CAF50") # Green

    # st.markdown("---")
    # if breakdown:
    #     ...

# ================== CRM GRID (PIPELINE) ==================
if "CRM Grid" in page:
    # --- CRM SCOPE: PERSONAL vs COMMON ---
    col_title, col_toggle = st.columns([2, 1]) # Increase toggle space
    with col_title:
        st.title("🗂 Advanced CRM Grid")
    
    with col_toggle:
        # Custom CSS for the Data Source Toggle (Segmented Control implementation)
        st.markdown("""
        <style>
        /* Segmented Control Container - Premium Dark Look - SCOPED */
        div[role="radiogroup"][aria-label="Data Source"] {
            background-color: #0E1117; 
            padding: 4px;
            border-radius: 10px;
            border: 1px solid #262730;
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }
        
        /* Segment Option (Inactive) - SCOPED */
        div[role="radiogroup"][aria-label="Data Source"] label {
            flex: 1;
            justify-content: center;
            align-items: center;
            border: none !important;
            background-color: transparent !important;
            margin: 0 !important;
            transition: all 0.2s ease;
            color: #9CA3AF !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            padding: 8px 12px !important;
            cursor: pointer;
            white-space: nowrap;
        }
        
        div[role="radiogroup"][aria-label="Data Source"] label:hover {
            color: #E0E0E0 !important;
            background-color: rgba(255,255,255,0.03) !important;
            border-radius: 6px;
        }

        /* Active Segment - The Pill with Gradient or Solid Pop - SCOPED */
        div[role="radiogroup"][aria-label="Data Source"] label:has(input:checked) {
            background-color: #2D2D30 !important;
            background: linear-gradient(135deg, #2D2D30 0%, #252528 100%) !important;
            color: #FFB74D !important; /* Keep the brand Amber */
            box-shadow: 0 2px 5px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: 1px solid #3A3A40 !important;
        }
        
        /* Remove Default Circles if they exist */
        div[role="radiogroup"] label > div:first-child { 
            display: none !important; 
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Restore Toggle so user can see their data in 'Common' if needed
        # Toggle Options depends on Role
        is_hr = st.session_state.user.get('role', 'User') == 'HR'
        if is_hr:
            opts = ["My Leads", "Team Leads", "All Interns"]
        else:
            opts = ["My Leads", "Team Leads"]
            
        scope_view = st.radio("Data Source", opts, index=0, horizontal=True, label_visibility="collapsed") # Default My Leads
        
    if scope_view == "My Leads":
        grid_scope = "personal" 
    elif scope_view == "All Interns":
        grid_scope = "all"
    else:
         grid_scope = "common"

    
    # --- File Import Section ---
    with st.expander("📂 Import Leads (CSV/Excel)"):
        uploaded_file = st.file_uploader("Upload file", type=['csv', 'xlsx'])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded_file)
                else:
                    import_df = pd.read_excel(uploaded_file)
                
                st.write(f"Preview: {len(import_df)} rows found")
                st.dataframe(import_df.head(), use_container_width=True)
                
                if st.button("🚀 Import Now"):
                    count = 0
                    progress_bar = st.progress(0, text="Importing...")
                    
                    for idx, row in import_df.iterrows():
                        # Smarter Mapping based on screenshot
                        # 1. Business Name
                        biz = row.get("Company Name") or row.get("Business Name") or row.get("Company")
                        name = row.get("Name") or row.get("Contact Name") or row.get("Person")
                        
                        # If Company Name is missing, use Name as Business Name (and leave contact empty)
                        if pd.isna(biz) or str(biz).strip() == "":
                            business_name = name if (not pd.isna(name)) else "Unknown Business"
                            contact_name = ""
                        else:
                            business_name = biz
                            contact_name = name if (not pd.isna(name)) else ""

                        # 2. Status & Priority
                        raw_status = row.get("Status")
                        status = raw_status if (not pd.isna(raw_status) and str(raw_status).strip() != "") else "Generated"
                        
                        raw_prio = row.get("Priority")
                        priority = raw_prio if (not pd.isna(raw_prio) and str(raw_prio).upper() in ["HOT", "WARM", "COLD"]) else "WARM"

                        # 3. Dates
                        last_f = row.get("Last Follow up Date") or row.get("Last Follow Up")
                        next_f = row.get("Next Follow-up Date") or row.get("Next Follow Up")

                        # Clean phone
                        phone_val = str(row.get("Phone Number") or row.get("Phone") or row.get("Contact") or "")
                        if phone_val == "nan": phone_val = ""

                        payload = {
                            "businessName": str(business_name),
                            "contactName": str(contact_name),
                            "phone": phone_val,
                            "email": str(row.get("Email") or row.get("Email Address") or ""),
                            "address": str(row.get("Address") or row.get("Location") or ""),
                            "status": str(status),
                            "priority": str(priority),
                            "lastFollowUpDate": str(last_f) if not pd.isna(last_f) else None,
                            "nextFollowUpDate": str(next_f) if not pd.isna(next_f) else None,
                            "targetScope": grid_scope # 👈 PASS SCOPE FROM TOGGLE
                        }
                        
                        if create_lead(payload):
                            count += 1
                        progress_bar.progress(min((idx + 1) / len(import_df), 1.0))
                    
                    st.success(f"Successfully imported {count} leads!")
                    st.rerun()

            except Exception as e:
                st.error(f"Error reading file: {e}")

    # --- Grid Section ---
    
    # Init DF
    df = pd.DataFrame() 

    # If in "All Interns" mode, we have a two-step process
    if grid_scope == "all":
        # Step 1: Check if we have selected an intern
        if "selected_intern" not in st.session_state:
            st.session_state.selected_intern = None
            
        if st.session_state.selected_intern is None:
            # SHOW LIST OF INTERNS
            st.markdown("### 👥 Select an Intern to View CRM")
            
            # Fetch users
            users_list = fetch_data(f"{BACKEND_BASE}/users")
            
            if users_list and isinstance(users_list, list) and len(users_list) > 0:
                # Create a nice grid layout for users
                # Filter out self (HR) and Company/Common CRM
                current_uid = st.session_state.user.get('id')
                
                # Logic: Exclude self, exclude Common CRM (ID 999 or Name check)
                user_buttons = [
                    u for u in users_list 
                    if u['id'] != current_uid and u['id'] != 999 and "Common" not in u['name']
                ]
                
                rows = [user_buttons[i:i+3] for i in range(0, len(user_buttons), 3)]
                
                for row_users in rows:
                    cols = st.columns(3)
                    for idx, u in enumerate(row_users):
                        with cols[idx]:
                            # Card style button
                            role_tag = f" ({u['role']})" if u.get('role') else ""
                            label = f"👤 {u['name']}{role_tag}"
                            if st.button(label, key=f"btn_user_{u['id']}", use_container_width=True):
                                st.session_state.selected_intern = u
                                st.rerun()
            else:
                st.info("No other users found or error fetching.")
                
            st.stop() # Stop rendering the rest of the grid (Toolbar etc)
            
        else:
            # SHOW SELECTED INTERN'S CRM
            target_u = st.session_state.selected_intern
            
            # Header with Back Button
            b_col1, b_col2 = st.columns([1, 4])
            with b_col1:
                # Grey Neumorphic Back Button Style
                if st.button("⬅️ Back to List", use_container_width=True):
                    st.session_state.selected_intern = None
                    st.rerun()
            with b_col2:
                st.markdown(f"### 👁️ Viewing CRM: **{target_u['name']}**")
            
            # Fetch specific user's leads
            leads = fetch_data(f"{LEADS_API}?scope=all&targetUserId={target_u['id']}")
            df = pd.DataFrame(leads)

    else:
        # Standard View (Personal or Common)
        # Fetch Data using variable defined at top of page
        leads = fetch_data(f"{LEADS_API}?scope={grid_scope}")
        df = pd.DataFrame(leads)

    
    # --- CLEANUP DATA (Remove 'nan' visuals) ---
    # Determine text columns to clean
    text_cols = ["businessName", "contactName", "phone", "email", "address", "status", "callNotes", "priority", "calledBy", "meetingBy", "closedBy"]
    for c in text_cols:
        if c in df.columns:
            # Force conversion to string and replace 'nan' variants with empty string
            df[c] = df[c].fillna("").astype(str).replace(["nan", "None", "NAN"], "")

    # --- GRID DATA PREP ---
    # Generate Google Maps Links (Smart Search: Company + Address)
    def create_smart_map_link(row):
        # Get values, handling NaNs
        company = str(row.get("businessName", "")).strip()
        addr = str(row.get("address", "")).strip()
        
        # Filter out 'nan', 'None' strings just in case
        if company.lower() in ["nan", "none"]: company = ""
        if addr.lower() in ["nan", "none"]: addr = ""
        
        # Combine
        full_query = f"{company} {addr}".strip()
        
        if not full_query:
            return None
            
        # Sanitize for URL
        query = full_query.replace(" ", "+")
        return f"https://www.google.com/maps/search/?api=1&query={query}"

    df["map_url"] = df.apply(create_smart_map_link, axis=1)

    # 2. Generate Google Calendar Links (Meeting Reminder)
    def create_google_cal_link(row):
        m_date = row.get("meetingDate")
        # Check for valid date string
        if not m_date or pd.isna(m_date) or str(m_date) == "" or str(m_date) == "None" or str(m_date) == "NaT":
            return None
        
        # Ensure it's a date object
        try:
            m_date_obj = pd.to_datetime(m_date).date()
        except:
            return None

        # Format dates for All Day event (Start / End+1)
        # Format: YYYYMMDD / YYYYMMDD
        start_str = m_date_obj.strftime("%Y%m%d")
        end_date = m_date_obj + pd.Timedelta(days=1)
        end_str = end_date.strftime("%Y%m%d")
        
        # Details
        name = str(row.get("contactName", "")).strip()
        comp = str(row.get("businessName", "")).strip()
        if name in ["nan", "None", ""]: name = "Lead"
        if comp in ["nan", "None", ""]: comp = "Unknown Company"
        
        title = f"Meeting with {name} ({comp})"
        ph = str(row.get('phone', '')).replace("nan","")
        ad = str(row.get('address', '')).replace("nan","")
        details = f"Phone: {ph}\nAddress: {ad}"
        
        # URL Encode
        import urllib.parse
        title_enc = urllib.parse.quote(title)
        details_enc = urllib.parse.quote(details)
        
        return f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title_enc}&details={details_enc}&dates={start_str}/{end_str}"

    # Ensure meetingDate exists
    if "meetingDate" not in df.columns:
        df["meetingDate"] = None

    df["calendar_url"] = df.apply(create_google_cal_link, axis=1)

    # Define columns structure (Logic Order)
    cols = [
        "id", "contactName", "businessName", "phone", "email", "address", "map_url",
        "meetingDate", "calendar_url",
        "lastFollowUpDate", "nextFollowUpDate", "status", "callNotes", 
        "priority", "calledBy", "meetingBy", "closedBy"
    ]
    
    # Columns for DISPLAY
    display_cols = [
        "contactName", "businessName", "phone", "email", "address", "map_url",
        "meetingDate", "calendar_url",
        "lastFollowUpDate", "nextFollowUpDate", "status", "callNotes", 
        "priority", "calledBy", "meetingBy", "closedBy"
    ]
    
    # Use empty DF if no leads, but KEEP columns structure
    if df.empty:
        df = pd.DataFrame(columns=cols)
    else:
        # Ensure all columns exist in data
        for c in cols:
            if c not in df.columns:
                df[c] = None

    # --- DATE REPAIR (CRITICAL FIX) ---
    # Convert string dates to actual datetime.date objects for Streamlit Editor
    for date_col in ["lastFollowUpDate", "nextFollowUpDate", "meetingDate"]:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date

    # --- INIT STATE ---
    # Default State for Toolbar
    if "mode_state" not in st.session_state:
        st.session_state.mode_state = "👁️ Read Only"
    mode = st.session_state.mode_state
    
    # Init Zoom default if not in session, but control handles it via key.
    # We just need a default variable for the first pass calculation.
    zoom_val = 90 
    
    # Init Font Size and Save State
    fs = "16px"
    save_clicked = False 

    # --- RESPONSIVE LAYOUT LOGIC v6 (Fixed Selectors) ---
    scale_val = zoom_val / 100
    
    # 1. Height Logic
    total_content_height = (len(df) + 1) * 35 + 10
    final_height = min(total_content_height, 20000) 
    final_height = max(final_height, 200)

    # 2. Width Logic (Python Calculated)
    # We calculate the inverse percentage to force the element to fill the visual screen.
    # e.g. Zoom 0.8 -> Width 125vw.
    width_val = 99.0 / scale_val
    width_str = f"{width_val:.2f}vw"
    
    # --- CUSTOM TOOLBAR UI ---
    st.markdown("""<div style="margin-bottom: 10px;"></div>""", unsafe_allow_html=True)
    
    toolbar_c1, toolbar_c2, toolbar_c3 = st.columns([1.2, 3, 1.8])
    
    with toolbar_c1:
        # Custom CSS for Slider to make it compact
        st.markdown("""
        <style>
        /* Compact Slider Container */
        div[data-testid="stSlider"] {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            margin-top: -5px !important;
            height: 40px !important;
        }
        
        /* HIDE LABELS & VALUES AGGRESSIVELY */
        div[data-testid="stSlider"] label { display: none !important; }
        
        /* The number popup (Red text 90 etc) */
        div[data-testid="stSlider"] div[data-testid="stThumbValue"],
        div[data-testid="stSlider"] .stThumbValue,
        div[data-testid="stSlider"] div[role="slider"] > div { 
            display: none !important; 
            opacity: 0 !important; 
            visibility: hidden !important; 
            height: 0 !important;
            width: 0 !important;
            pointer-events: none !important;
            color: transparent !important;
        }
        
        /* The min/max labels below if exist */
        div[data-testid="stSliderTickBar"] { display: none !important; }
        
        /* 1. Track (Background) -> Neumorphic Inset - GREY */
        div[data-testid="stSlider"] > div > div > div > div {
             background: #e0e5ec !important;
             box-shadow: inset 2px 2px 5px #b8b9be, inset -3px -3px 7px #ffffff !important;
             height: 8px !important;
             border-radius: 10px;
        }
        
        /* 2. Filled Track (Progress) -> Blue Gradient */
        div[data-testid="stSlider"] > div > div > div > div > div {
             background: linear-gradient(90deg, #2196F3, #64B5F6) !important;
             height: 8px !important;
             border-radius: 10px;
        }
        
        /* 3. Thumb (Handle) -> Neumorphic Button look */
        div[data-testid="stSlider"] > div > div > div > div[role="slider"] {
             background-color: #e0e5ec !important;
             border: none !important;
             box-shadow: 3px 3px 6px #b8b9be, -3px -3px 6px #ffffff !important;
             width: 20px !important;
             height: 20px !important;
             top: -6px !important; 
        }
        
        /* Remove any other text content inside */
        div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] { display: none !important; }
        
        /* Hover Effect on Thumb */
        div[data-testid="stSlider"] > div > div > div > div[role="slider"]:hover {
             transform: scale(1.1);
             cursor: grab;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("**🔎 Zoom Level**", unsafe_allow_html=True)
        new_zoom = st.slider("Zoom", 50, 100, 90, 10, label_visibility="collapsed", key="zoom_slider_real")
        

        # Update vars based on real slider
        scale_val = new_zoom / 100 
        width_val = 99.0 / scale_val
        width_str = f"{width_val:.2f}vw"

    with toolbar_c2:
         st.write("") # Spacer

    with toolbar_c3:
        st.write("⚙️ **Actions**")
        # Split into smaller cols for better layout - gap="small" for tighter look
        ac1, ac2, ac3 = st.columns([1, 1, 1], gap="small") 
        
        with ac1:
             # Edit/Read Toggle
             if mode == "👁️ Read Only":
                 if st.button("✏️ Edit", use_container_width=True, key="btn_edit_mode"):
                     st.session_state.mode_state = "✏️ Edit" 
                     st.rerun() 
             else:
                 if st.button("👁️ Read", use_container_width=True, key="btn_read_mode"):
                    st.session_state.mode_state = "👁️ Read Only"
                    st.rerun()
        
        with ac2:
            # Wrap Toggle - Replaced with Button for better aesthetics ("Image or something")
            # We use a button that toggles state interactively
            current_wrap = st.session_state.get("wrap_text", False)
            btn_label = "📏 Table" if current_wrap else "↩️ Wrap"
            btn_help = "Switch to Standard Table" if current_wrap else "Switch to Wrapped View"
            
            if st.button(btn_label, use_container_width=True, help=btn_help, key="wrap_btn_toggle"):
                st.session_state.wrap_text = not current_wrap
                st.rerun()
                
        # --- FORCE CSS INJECTION FOR THESE BUTTONS ---
        st.markdown("""
        <style>
        /* Force Buttons in Action Toolbar to look like Unified Grey Neumorphic */
        /* Target buttons within columns to ensure they all look consistent (Edit, Wrap, Save) */
        div[data-testid="column"] button {
            background-color: #e0e5ec !important;
            color: #4d5b6b !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: 6px 6px 10px #b8b9be, -6px -6px 10px #ffffff !important;
            transition: all 0.2s ease !important;
            height: 42px !important;
            font-weight: 600 !important;
        }

        /* Hover State */
        div[data-testid="column"] button:hover {
            transform: translateY(-2px);
            color: #2196F3 !important;
            box-shadow: 8px 8px 15px #b0b1b6, -8px -8px 15px #ffffff !important;
        }

        /* Active/Pressed State */
        div[data-testid="column"] button:active {
            box-shadow: inset 3px 3px 6px #b8b9be, inset -3px -3px 6px #ffffff !important;
            background-color: #e0e5ec !important;
        }
        
        /* Specifically ensure Primary (Save) button follows suit if desired, or keep it distinct? 
           User asked to make 'Wrap' like 'Edit and Save'. In the image, 'Save' was Grey too. 
           So we override Primary styles for consistency in this toolbar. */
        div[data-testid="column"] button[kind="primary"] {
            background-color: #e0e5ec !important;
            color: #4d5b6b !important;
        }
        div[data-testid="column"] button[kind="primary"]:hover {
             color: #2196F3 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        with ac3:
             if mode == "✏️ Edit":
                 # In Wrap Mode, we don't need the save button because the Modal handles it individually.
                 # But we keep it for Standard Grid.
                 if not st.session_state.get("wrap_text", False):
                    save_clicked = st.button("💾 Save", type="primary", use_container_width=True, key="btn_save")
                 else:
                    st.button("💾 Save", disabled=True, use_container_width=True, key="btn_save_disabled", help="Use the inline edit buttons in Wrap Mode")
             else:
                 # Standardize button size by adding text even in read only
                 st.button("💾 Save", disabled=True, use_container_width=True, key="btn_save_read_only")



    # CSS Injection (Updated for new Scale)
    st.markdown(f"""
    <style>
    /* 1. Force Main Container to Edges */
    section.main > .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100vw !important;
        width: 100vw !important;
    }}
    
    /* 2. Target the Dataframe Container - Force Width & Zoom */
    div[data-testid="stDataEditor"], div[data-testid="stDataFrame"] {{
        zoom: {scale_val};
        width: {width_str} !important;
        min-width: {width_str} !important;
        max-width: none !important;
        display: block;
        margin-left: 0 !important;
        margin-right: 0 !important;
        
        /* Shadow for visual framing */
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    
    /* 3. Aggressively target inner children to ensure they inherit the width */
    div[data-testid="stDataEditor"] > div, 
    div[data-testid="stDataFrame"] > div,
    div[data-testid="stDataEditor"] canvas,
    div[data-testid="stDataFrame"] canvas {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    # Sync Options with Palette Keys to ensure 100% match
    status_keys = list(STATUS_PALETTE.keys())
    # Add "Generated" if it's not in the main palette but used in data
    if "Generated" not in status_keys: status_keys.insert(0, "Generated")
    
    status_options = status_keys
    users_list = ["Vyonish", "Satyajit"]

    grid_config = {
        "id": st.column_config.NumberColumn("ID", disabled=True),
        "contactName": st.column_config.TextColumn("Name"),
        "businessName": st.column_config.TextColumn("Company Name", required=True),
        "phone": st.column_config.TextColumn("Phone Number"),
        "email": st.column_config.TextColumn("Email"),
        "address": st.column_config.TextColumn("Address"),
        "map_url": st.column_config.LinkColumn("Map", display_text="Open Map 🗺️"),
        "meetingDate": st.column_config.DateColumn("Meeting Date", format="DD/MM/YYYY"),
        "calendar_url": st.column_config.LinkColumn("Reminder", display_text="📅 Add to Calendar"),
        "lastFollowUpDate": st.column_config.DateColumn("Last Follow up Date", format="DD/MM/YYYY"),
        "nextFollowUpDate": st.column_config.DateColumn("Next Follow-up Date", format="DD/MM/YYYY"),
        "status": st.column_config.SelectboxColumn("Status", options=status_options, required=True),
        "callNotes": st.column_config.TextColumn("Notes", width="large"),
        "priority": st.column_config.SelectboxColumn("Priority", options=["HOT", "WARM", "COLD"], required=True),
        "calledBy": st.column_config.SelectboxColumn("Called By", options=users_list),
        "meetingBy": st.column_config.SelectboxColumn("Meeting by", options=users_list),
        "closedBy": st.column_config.SelectboxColumn("Closed By", options=users_list),
    }

    # --- HELPER: STYLING FUNCTIONS ---
    def get_status_style(val):
        """
        Returns CSS style string for a given status value.
        """
        if not val or pd.isna(val):
            return ""
            
        status_val = str(val).strip()
        
        # Get palette (theme agnostic)
        status_colors = get_status_colors("light")
        
        # Pre-process keys for fuzzy matching
        status_lookup = {k.lower(): v for k, v in status_colors.items()}
        
        style_found = ""
        
        # A. Exact Match
        if status_val in status_colors:
            style_found = status_colors[status_val]
        
        # B. Case-Insensitive Match
        elif status_val.lower() in status_lookup:
            style_found = status_lookup[status_val.lower()]
            
        # C. Fuzzy Dash Match
        else:
            variants = [
                status_val.replace('-', '–'), # hyphen to en-dash
                status_val.replace('–', '-'), # en-dash to hyphen
            ]
            for v in variants:
                if v in status_colors:
                    style_found = status_colors[v]
                    break
                if v.lower() in status_lookup:
                    style_found = status_lookup[v.lower()]
                    break
        
        return style_found

    def get_user_style(val):
        """
        Returns CSS for specific users.
        """
        if not val or pd.isna(val):
            return ""
        
        val_str = str(val).strip()
        user_colors = {
            "Satyajit": "background-color: #E040FB; color: white; border-radius: 12px; padding: 2px 8px;", 
            "Vyonish": "background-color: #B2FF59; color: black; border-radius: 12px; padding: 2px 8px;"
        }
        return user_colors.get(val_str, "")

    def get_user_style(val):
        """
        Returns CSS for specific users.
        """
        if not val or pd.isna(val):
            return ""
        
        val_str = str(val).strip()
        user_colors = {
            "Satyajit": "background-color: #E040FB; color: white; border-radius: 12px; padding: 2px 8px;", 
            "Vyonish": "background-color: #B2FF59; color: black; border-radius: 12px; padding: 2px 8px;"
        }
        return user_colors.get(val_str, "")

    # --- DIALOG FOR EDITING (Supported in St 1.43) ---
    @st.dialog("✏️ Edit Lead Details")
    def edit_lead_dialog(lead_id, current_data):
        with st.form(f"edit_form_{lead_id}"):
            # Layout fields
            c1, c2 = st.columns(2)
            new_name = c1.text_input("Name", value=current_data.get("contactName", ""))
            new_biz = c2.text_input("Business Name", value=current_data.get("businessName", ""))
            
            c3, c4 = st.columns(2)
            new_phone = c3.text_input("Phone", value=current_data.get("phone", ""))
            new_email = c4.text_input("Email", value=current_data.get("email", ""))
            
            new_addr = st.text_area("Address", value=current_data.get("address", ""))
            
            c5, c6, c7 = st.columns(3)
            new_status = c5.selectbox("Status", options=status_options, index=status_options.index(current_data.get("status")) if current_data.get("status") in status_options else 0)
            new_prio = c6.selectbox("Priority", options=["HOT", "WARM", "COLD"], index=["HOT", "WARM", "COLD"].index(current_data.get("priority")) if current_data.get("priority") in ["HOT", "WARM", "COLD"] else 1)
            
            # Dates
            d1 = current_data.get("meetingDate")
            d2 = current_data.get("nextFollowUpDate")
            try:
                # Handle various date formats/types
                if isinstance(d1, str): d1 = pd.to_datetime(d1).date()
                if isinstance(d2, str): d2 = pd.to_datetime(d2).date()
            except: pass
            
            new_meet = c5.date_input("Meeting Date", value=d1 if d1 else None)
            new_next = c6.date_input("Next Follow-up", value=d2 if d2 else None)
            
            new_notes = st.text_area("Notes", value=current_data.get("callNotes", ""))
            
            if st.form_submit_button("💾 Save Changes", type="primary"):
                # Construct payload
                updates = {
                    "contactName": new_name,
                    "businessName": new_biz,
                    "phone": new_phone,
                    "email": new_email,
                    "address": new_addr,
                    "status": new_status,
                    "priority": new_prio,
                    "callNotes": new_notes,
                    "meetingDate": str(new_meet) if new_meet else None,
                    "nextFollowUpDate": str(new_next) if new_next else None
                }
                
                if update_lead(lead_id, updates):
                    st.success("Saved!")
                    st.session_state["edit_trigger"] = None # Clear trigger
                    st.rerun()
                else:
                    st.error("Failed to update.")

    # Check for Edit Trigger explicitly
    if "edit_trigger" in st.session_state and st.session_state.edit_trigger:
        t_id = st.session_state.edit_trigger
        # Find row
        row_data = df[df["id"] == int(t_id)].iloc[0].to_dict()
        edit_lead_dialog(t_id, row_data)
        st.session_state.edit_trigger = None # Reset after showing? No, let dialog handle it.

    # --- RENDER GRID ---
    # Determine Logic State
    is_wrap = st.session_state.get("wrap_text", False)
    
    # --- COMMON SETUP FOR BOTH VIEWS ---
    base_props = {'font-size': fs, 'height': 'auto'}
    # Colors for Styler
    if st.session_state.theme == "dark":
            base_props.update({
                'background-color': '#262730', 
                'color': '#E0E0E0',
                'border-color': '#444'
            })
            header_bg = "#333"
            header_col = "#E0E0E0"
            border_col = "#444"
    else:
            base_props.update({
                'background-color': '#ffffff',
                'color': '#1a1a1a',
                'border-color': '#e0e0e0'
            })
            header_bg = "#f8f9fa"
            header_col = "#444"
            border_col = "#e0e0e0"

    # Prepare Display DF
    display_df = df[display_cols].copy()
    display_df['status'] = display_df['status'].astype(str)
    
    # Rename 'status' to 'Status' for styling consistency
    display_df.rename(columns={"status": "Status"}, inplace=True)

    if is_wrap:
        # --- HTML WRAPPED VIEW ---
        
        # 1. Convert Links to HTML
        def make_link(url, text, icon=""):
            if not url or str(url) in ["None", "nan", ""]: return ""
            return f'<a href="{url}" target="_blank" style="text-decoration:none; color:#1976d2; font-weight:500;">{icon} {text}</a>'
        
        display_df['map_url'] = display_df['map_url'].apply(lambda x: make_link(x, "Open Map", "🗺️"))
        display_df['calendar_url'] = display_df['calendar_url'].apply(lambda x: make_link(x, "Add to Cal", "📅"))
        
        # 2. Rename cols for nicer headers
        # Note: We do this only for HTML view to avoid breaking st.dataframe column config matching
        display_df_html = display_df.copy()
        display_df_html.rename(columns={
            "contactName": "Name", "businessName": "Business", "phone": "Phone", 
            "email": "Email", "address": "Address", "map_url": "Map", 
            "calendar_url": "Reminder", "meetingDate": "Meeting Date",
            "lastFollowUpDate": "Last Follow-up", "nextFollowUpDate": "Next Follow-up",
            "callNotes": "Notes", "priority": "Priority", 
            "calledBy": "Called By", "meetingBy": "Meeting By", "closedBy": "Closed By"
        }, inplace=True)

        # --- GOOGLE SHEETS STYLE STATUS CHIPS (HTML) ---
        def make_status_chip(val):
            if not val or str(val) == "nan": return ""
            style = get_status_style(val) # Returns "bg:..; col:..; ..."
            return f'<div style="{style} display: inline-block; white-space: nowrap; font-size: 0.85rem; margin: 0;">{val}</div>'

        display_df_html['Status'] = display_df_html['Status'].apply(make_status_chip)
        
        # --- ADD EDIT BUTTON (If in Edit Mode) ---
        # The user triggers this by clicking the 'Edit ID' button we inject.
        # Streamlit doesn't support onclick -> python easily in raw HTML. 
        # Hack: We use a column configure in `st.dataframe` usually, but we are in HTML.
        # Solution: We can't easily trigger the python callback from raw HTML to open the specific ID dialog without a rerun.
        # HOWEVER, we can use `st.column_config.LinkColumn` in `st.dataframe`... NO, we are using `to_html`.
        # Agent Decision: For "Wrap in Edit Mode", we will simply display the `st.dataframe` WITH `st.column_config.TextColumn` wrapped?
        # WAIT! Streamlit 1.35+ added `width="large"` but no max-height wrap.
        # Let's use the 'Link Query Param' trick.
        
        if mode == "✏️ Edit":
            # Add Actions Column
            # Self-href to same page with query param ?edit_id=<ID>
            # We must detect current URL? No, just ?edit_id=...
            # This triggers a reload, which we catch at top of script?
            # Actually easier: We use a button in the toolbar to 'Edit Selected' if the user can select?
            # No, user wants row alignment.
            
            # Let's try rendering `st.button` for each row? Too slow.
            # Let's use the Query Param Link hack.
            
            df_ids = df["id"].tolist()
            display_df_html.insert(0, "Action", [f'<a href="?edit_id={i}" target="_self" style="text-decoration:none;">✏️ Edit</a>' for i in df_ids])
            
            # CHECK QUERY PARAMS HERE (Local catch)
            qp = st.query_params
            if "edit_id" in qp:
                edit_id = qp["edit_id"]
                # Clear param to prevent loop
                # st.query_params.clear() # This might refresh again. 
                # Better: Set session state trigger and clear.
                st.session_state.edit_trigger = edit_id
                st.query_params.clear()
                st.rerun()

        # 3. Apply Styler
        # Note: We must map styles using the NEW column names
        styled_html = display_df_html.style\
            .map(get_user_style, subset=['Called By', 'Meeting By', 'Closed By'])\
            .hide(axis="index")\
            .set_properties(**base_props)\
            .format({"Last Follow-up": "{:%d/%m/%Y}", "Next Follow-up": "{:%d/%m/%Y}", "Meeting Date": "{:%d/%m/%Y}"}, na_rep="")\
            .to_html(escape=False)

        # 4. Inject Custom Table CSS (Google Sheets Look)
        table_css = f"""
        <style>
        .wrap-table-container {{
            max-height: {final_height}px;
            overflow-y: auto;
            border: 1px solid {border_col};
            border-radius: 4px; /* Sharper corners like generic sheet container */
            background-color: {base_props.get('background-color', '#fff')};
            
            /* ZOOM & WIDTH LOGIC */
            zoom: {scale_val};
            width: {width_str} !important;
            min-width: {width_str} !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            display: block;
        }}
        .wrap-table-container table {{
            width: 100%;
            border-collapse: collapse; /* Critical for grid lines */
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            table-layout: fixed; /* Helps with aggressive wrapping */
        }}
        .wrap-table-container th {{
            background-color: {header_bg};
            color: {header_col};
            position: sticky;
            top: 0;
            z-index: 10;
            padding: 8px 6px; /* Tighter headers */
            text-align: left;
            font-weight: 600;
            border: 1px solid {border_col}; /* Full Grid */
            font-size: 0.85rem;
        }}
        .wrap-table-container td {{
            padding: 6px 8px; /* Sheets-like density */
            border: 1px solid {border_col}; /* Full Grid */
            border-top: none; /* Collapse fix */
            color: {base_props.get('color', '#333')};
            
            /* ALIGNMENT */
            vertical-align: middle;
            text-align: left;
            
            /* WRAPPING MAGIC */
            white-space: normal !important; 
            word-wrap: break-word;
        }}
        /* Specific column tweaks */
        .wrap-table-container td:nth-child(2) {{ font-weight: 600; }} /* Business Name */
        </style>
        """
        
        st.markdown(table_css, unsafe_allow_html=True)
        st.markdown(f'<div class="wrap-table-container">{styled_html}</div>', unsafe_allow_html=True)

    else:
        # NORMAL MODE (Edit or Read)
        # If Edit Mode -> st.data_editor
        # If Read Mode -> st.dataframe
        # BUT user wanted "Wrap in Edit Mode". We handled that above by allowing 'Edit' links in Wrap.
        # Now we handle 'Edit Mode' WITHOUT wrap (Standard Grid).
        
        if mode == "✏️ Edit":
             st.caption("📍 Standard Grid Edit (No Wrap). Double-click cells to modify.")
             edited_df = st.data_editor(
                df[cols],
                column_config=grid_config,
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic",
                key="crm_grid",
                height=int(final_height),
                column_order=display_cols 
            )
             if save_clicked:
                # ... save logic reuse ...
                changes = st.session_state.get("crm_grid", {})
                edited_rows = changes.get("edited_rows", {})
                added_rows = changes.get("added_rows", [])
                deleted_rows = changes.get("deleted_rows", [])
                
                count = 0
                if edited_rows:
                    for index, updates in edited_rows.items():
                        if index < len(df):
                            lead_id = int(df.iloc[index]["id"])
                            if update_lead(lead_id, updates):
                                count += 1
                if added_rows:
                    for row in added_rows:
                        if not row.get("businessName"): row["businessName"] = "New Business"
                        if create_lead(row):
                            count += 1
                if deleted_rows:
                    for index in deleted_rows:
                            if index < len(df):
                                lead_id = int(df.iloc[index]["id"])
                                if delete_lead(lead_id):
                                    count += 1
                if count > 0:
                    st.success(f"Processed {count} changes!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("No changes to save.")
        
        else:
             # Standard Read Only
            styled_df = display_df.style\
                .map(get_status_style, subset=['Status'])\
                .map(get_user_style, subset=['calledBy', 'meetingBy', 'closedBy'])\
                .set_properties(**base_props)\
                .format({"lastFollowUpDate": "{:%d/%m/%Y}", "nextFollowUpDate": "{:%d/%m/%Y}"}, na_rep="")
                
            read_only_config = grid_config.copy()
            if "status" in read_only_config: del read_only_config["status"]
            
            # Force hide index
            st.dataframe(
                styled_df, 
                column_config=read_only_config,
                use_container_width=True, 
                height=int(final_height),
                hide_index=True
            )

# ================== SPREADSHEET INTELLIGENCE TOOL ==================
if "Excel Tool" in page:
    st.title("🧠 Spreadsheet Intelligence Tool")
    st.markdown("Advanced analysis for Excel workbooks. Splits duplicates/uniques by sheet and finds new rows across files.")

    import io
    import re
    # Ensure openpyxl is installed for Excel writing (standard in streamlit envs)

    # --- HELPERS ---
    def normalize_text(text):
        """Strict normalization: lower, trim, remove special chars. Returns None for noise."""
        if pd.isna(text):
            return None
        s = str(text).strip().lower()
        if s in ["", "none", "nan", "null"]:
            return None
        # Remove special characters (keep alphanumeric and spaces)
        s = re.sub(r'[^a-zA-Z0-9\s]', '', s)
        return s if s.strip() != "" else None

    tab1, tab2 = st.tabs(["📂 Single File Analysis (Dups vs Uniques)", "🔁 Cross-File Comparison (New Rows)"])

    # ==========================
    # TAB 1: SINGLE FILE (ALL SHEETS)
    # ==========================
    with tab1:
        st.subheader("Split Duplicates & Uniques (Preserving Sheets)")
        st.info("Uploaded workbook will be processed to separate Duplicates and Unique rows into distinct sheets.")

        f_single = st.file_uploader("Upload Excel Workbook (.xlsx)", type=['xlsx'], key="sit_single")

        if f_single:
            try:
                # 1. READ ALL SHEETS
                xls = pd.read_excel(f_single, sheet_name=None)
                sheet_names = list(xls.keys())
                
                # Check for empty sheets
                valid_sheets = {k: v for k, v in xls.items() if not v.empty}
                
                if not valid_sheets:
                    st.error("Workbook contains no data.")
                else:
                    st.success(f"Loaded {len(valid_sheets)} sheets: {', '.join(valid_sheets.keys())}")
                    
                    # 2. COLUMN SELECTION (Global)
                    # We grab columns from the first sheet or union of all? 
                    # Usually better to check common columns or just picked from first sheet as primary.
                    # For safety, let's list all unique columns found across valid sheets.
                    all_cols = set()
                    for df in valid_sheets.values():
                        all_cols.update(df.columns.astype(str))
                    
                    target_cols = st.multiselect("Select Duplicate Key Columns (e.g. Email, Phone)", sorted(list(all_cols)))

                    if target_cols and st.button("🚀 Process Workbook", type="primary"):
                        with st.spinner("Analyzing across all sheets..."):
                            
                            # A. PREPARE GLOBAL DATASET FOR DETECTION
                            # We need to track: (SheetName, OriginalIndex) -> NormalizedKey
                            global_rows = []
                            
                            for s_name, df in valid_sheets.items():
                                # Check if target cols exist in this sheet
                                missing = [c for c in target_cols if c not in df.columns]
                                if missing:
                                    # Skip or handle? Let's treat missing cols as None
                                    pass
                                
                                # Normalize
                                temp_df = df.copy()
                                temp_df['_sheet'] = s_name
                                temp_df['_idx'] = temp_df.index
                                
                                # normalization
                                norm_vals = []
                                for c in target_cols:
                                    if c in df.columns:
                                        # Apply norm
                                        temp_df[f'__norm_{c}'] = temp_df[c].apply(normalize_text)
                                    else:
                                        temp_df[f'__norm_{c}'] = None
                                
                                global_rows.append(temp_df)
                            
                            if not global_rows:
                                st.error("No data found to process.")
                            else:
                                master_df = pd.concat(global_rows, ignore_index=True)
                                
                                # Norm Cols Key
                                norm_keys = [f'__norm_{c}' for c in target_cols]
                                
                                # Do NOT drop rows with empty keys, preserve them as Unique
                                master_valid = master_df.copy()
                                
                                # DETECT DUPLICATES (Global Scope)
                                # duplicated matches NaNs as duplicates. We want to avoid that for empty keys.
                                dup_mask = master_valid.duplicated(subset=norm_keys, keep=False)
                                
                                # If all key columns are None, do NOT count as duplicate (treat as Unique)
                                empty_mask = master_valid[norm_keys].isna().all(axis=1)
                                dup_mask = dup_mask & (~empty_mask)
                                
                                # Mark them in master
                                master_valid['is_duplicate'] = dup_mask

                                # ------------------------------------------
                                # NEW: Find where the duplicates are located
                                # ------------------------------------------
                                if not master_valid.empty and dup_mask.any():
                                    # Group by keys to find all locations
                                    # We need to preserve the index to map back
                                    dup_rows = master_valid[dup_mask].copy()
                                    
                                    # Create a display label "SheetName:Row"
                                    # Adjust index to be 1-based for users
                                    dup_rows['__loc_label'] = dup_rows['_sheet'] + " (Row " + (dup_rows['_idx'] + 2).astype(str) + ")"
                                    
                                    # Group by norm_keys and aggregate locations
                                    # We must handle multiple keys.
                                    # Create a tuple key for grouping
                                    dup_rows['__group_key'] = dup_rows[norm_keys].apply(tuple, axis=1)
                                    
                                    # Group and join
                                    loc_map = dup_rows.groupby('__group_key')['__loc_label'].apply(lambda x: ", ".join(x)).to_dict()
                                    
                                    # Map back to master_valid
                                    # For each row, the "found_in" is the full list minus itself (optional, or just show all)
                                    # Showing ALL locations is usually clearer: "Found in: Sheet1 (Row 5), Sheet2 (Row 10)"
                                    
                                    master_valid['__group_key'] = master_valid[norm_keys].apply(tuple, axis=1)
                                    master_valid['duplicate_locations'] = master_valid['__group_key'].map(loc_map)
                                else:
                                    master_valid['duplicate_locations'] = None
                                
                                # Now we map back to splitting Dups vs Uniques per sheet
                                # Create Output Excel
                                output = io.BytesIO()
                                writer = pd.ExcelWriter(output, engine='openpyxl')
                                
                                total_dups = 0
                                total_uniques = 0
                                
                                results_summary = {} # {sheet: {'dups': count, 'uniques': count}}
                                
                                for s_name in valid_sheets.keys():
                                    # Get rows belonging to this sheet from valid set
                                    sheet_subset = master_valid[master_valid['_sheet'] == s_name]
                                    
                                    # Split
                                    dups_df = sheet_subset[sheet_subset['is_duplicate'] == True]
                                    uniques_df = sheet_subset[sheet_subset['is_duplicate'] == False]
                                    
                                    # Clean helper cols
                                    # Retrieve original rows using index is tricky after concat/drop.
                                    # Better: Use the stored original index or just columns.
                                    # We have original columns in sheet_subset. Just drop helpers.
                                    drop_cols = ['_sheet', '_idx', 'is_duplicate'] + norm_keys
                                    
                                    # For original DF cols
                                    orig_cols = list(valid_sheets[s_name].columns)
                                    
                                    # Add 'duplicate_locations' to dups output
                                    final_dups = dups_df[orig_cols + ['duplicate_locations']]
                                    final_uniques = uniques_df[orig_cols]
                                    
                                    total_dups += len(final_dups)
                                    total_uniques += len(final_uniques)
                                    results_summary[s_name] = {'dups': len(final_dups), 'uniques': len(final_uniques)}
                                    
                                    # Write to Excel
                                    if not final_dups.empty:
                                        final_dups.to_excel(writer, sheet_name=f"{s_name[:20]}_Dups", index=False)
                                    if not final_uniques.empty:
                                        final_uniques.to_excel(writer, sheet_name=f"{s_name[:20]}_Uniques", index=False)
                                
                                writer.close()
                                
                                # UI METRICS
                                m1, m2, m3 = st.columns(3)
                                m1.metric("Rows Scanned", len(master_valid))
                                m2.metric("Total Duplicates", total_dups, delta_color="inverse")
                                m3.metric("Total Unique", total_uniques)
                                
                                st.markdown("### 📋 Sheet Breakdown")
                                for s in valid_sheets.keys():
                                    # Filter again for display logic
                                    sub = master_valid[master_valid['_sheet'] == s]
                                    d_rows = sub[sub['is_duplicate'] == True]
                                    u_count = len(sub) - len(d_rows)
                                    
                                    # Restore original cols for display
                                    orig_cols = list(valid_sheets[s].columns)
                                    d_disp = d_rows[orig_cols + ['duplicate_locations']]
                                    
                                    with st.expander(f"{s} (Dups: {len(d_disp)} | Uniques: {u_count})"):
                                        if not d_disp.empty:
                                            st.warning(f"Found {len(d_disp)} duplicates.")
                                            st.dataframe(d_disp, use_container_width=True)
                                        else:
                                            st.success("No duplicates in this sheet.")
                                            
                                        if u_count > 0:
                                            st.info(f"Sheet contains {u_count} unique rows.")

                                # DOWNLOAD
                                processed_data = output.getvalue()
                                st.download_button(
                                    label="📥 Download Split Workbook (XLSX)",
                                    data=processed_data,
                                    file_name="processed_workbook.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary"
                                )

            except Exception as e:
                st.error(f"Error: {e}")

    # ==========================
    # TAB 2: CROSS FILE (A vs B)
    # ==========================
    with tab2:
        st.subheader("Find New Rows (Unique to B)")
        st.info("Compares File B against File A. Outputs ONLY rows in B that do not exist in A.")

        c1, c2 = st.columns(2)
        f_a = c1.file_uploader("File A (Baseline / Old)", type=['xlsx'], key="sit_a")
        f_b = c2.file_uploader("File B (New / Update)", type=['xlsx'], key="sit_b")

        if f_a and f_b:
            try:
                # 1. READ BOTH
                xls_a = pd.read_excel(f_a, sheet_name=None)
                xls_b = pd.read_excel(f_b, sheet_name=None)
                
                # 2. COL SELECT
                # Grab cols from B (since we are filtering B)
                all_cols_b = set()
                for df in xls_b.values():
                    all_cols_b.update(df.columns.astype(str))
                
                match_cols = st.multiselect("Match Columns (Must exist in both files)", sorted(list(all_cols_b)))

                if match_cols and st.button("🚀 Find New Rows in B", type="primary"):
                    with st.spinner("Building baseline from File A..."):
                        
                        # BUILD BASELINE SET FROM A (All sheets)
                        baseline_tuples = set()
                        count_a = 0
                        
                        for df in xls_a.values():
                            # Check cols
                            valid_cols = [c for c in match_cols if c in df.columns]
                            if len(valid_cols) != len(match_cols):
                                continue # Skip processing if cols don't match? Or process partially? Strict: Skip
                            
                            # Normalize & Tuple
                            # We create a temp df to normalize
                            temp = df[valid_cols].copy()
                            for c in valid_cols:
                                temp[c] = temp[c].apply(normalize_text)
                            
                            # Dropna
                            temp = temp.dropna(how='all')
                            count_a += len(temp)
                            
                            # Convert to tuples for set
                            # We use .itertuples(index=False, name=None) for speed
                            baseline_tuples.update(list(temp.itertuples(index=False, name=None)))
                        
                    # PROCESS B
                    with st.spinner(f"Comparing File B ({len(xls_b)} sheets) against {len(baseline_tuples)} unique baseline records..."):
                        output_b = io.BytesIO()
                        writer_b = pd.ExcelWriter(output_b, engine='openpyxl')
                        
                        total_new = 0
                        results_b = {}
                        
                        for s_name, df in xls_b.items():
                            valid_cols = [c for c in match_cols if c in df.columns]
                            if len(valid_cols) != len(match_cols):
                                continue 
                            
                            # Normalize B
                            temp_b = df.copy()
                            norm_keys = []
                            for c in valid_cols:
                                norm_n = f"__norm_{c}"
                                temp_b[norm_n] = temp_b[c].apply(normalize_text)
                                norm_keys.append(norm_n)
                            
                            # Drop empty keys
                            temp_b_valid = temp_b.dropna(subset=norm_keys, how='all')
                            
                            # Check existence
                            # Create tuple column
                            temp_b_valid['__tuple'] = temp_b_valid[norm_keys].apply(tuple, axis=1)
                            
                            # Filter: Keep if tuple NOT in baseline
                            new_rows_mask = ~temp_b_valid['__tuple'].isin(baseline_tuples)
                            
                            new_rows_df = temp_b_valid[new_rows_mask]
                            
                            # Clean output
                            final_new = new_rows_df[df.columns] # Original cols
                            
                            cnt = len(final_new)
                            total_new += cnt
                            results_b[s_name] = cnt
                            
                            if cnt > 0:
                                final_new.to_excel(writer_b, sheet_name=f"{s_name[:20]}_New", index=False)
                        
                        writer_b.close()
                        
                        # METRICS
                        c_m1, c_m2, c_m3 = st.columns(3)
                        c_m1.metric("Baseline Rows (A)", count_a)
                        c_m2.metric("Total Rows Processed (B)", sum([len(d) for d in xls_b.values()]))
                        c_m3.metric("New Unique Rows Found", total_new, delta_color="normal")
                        
                        st.markdown("### 🆕 New Rows per Sheet")
                        for s, n in results_b.items():
                            if n > 0:
                                st.success(f"Sheet '{s}': {n} new rows")
                            else:
                                st.caption(f"Sheet '{s}': No new rows")
                                
                        if total_new > 0:
                            processed_b = output_b.getvalue()
                            st.download_button(
                                label="📥 Download Comparison Result (XLSX)",
                                data=processed_b,
                                file_name="comparison_unique_to_B.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary"
                            )
                        else:
                            st.success("Analysis complete. File B contains no new data relative to File A.")

            except Exception as e:
                st.error(f" Comparison Error: {e}")

# ================== POWER DIALER ==================
if "Power Dialer" in page:
    st.title("📞 Power Dialer Mode")
    
    # Fetch ALL leads for Dialing (Personal + Team)
    leads_personal = fetch_data(f"{LEADS_API}?scope=personal")
    leads_common = fetch_data(f"{LEADS_API}?scope=common")
    leads = leads_personal + leads_common
    if not leads:
        st.info("No leads found.")
        st.stop()
        
    df = pd.DataFrame(leads)
    
    # Filter Logic
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Ensure nextFollowUpDate is handled
    if "nextFollowUpDate" not in df.columns:
        df["nextFollowUpDate"] = None
        
    # Convert properly to string
    df["nextFollowUpDate"] = df["nextFollowUpDate"].astype(str).replace("None", "").replace("nan", "")
    
    
    # Sidebar Filter
    st.sidebar.markdown("### 🎯 Filter Leads")
    filter_choice = st.sidebar.radio(
        "Show:",
        ["Today's Follow-ups", "All Leads"],
        index=0
    )
    
    # Apply Filter
    if filter_choice == "Today's Follow-ups":
        today_str = datetime.now().strftime("%Y-%m-%d")
        mask_active = ~df["status"].str.contains("Closed", case=False, na=False)
        # Include today AND overdue (past dates)
        mask_due = df["nextFollowUpDate"] <= today_str
        filtered_df = df[mask_active & mask_due]
        
        if filtered_df.empty:
            st.success("✅ No follow-ups scheduled for today! Great job.")
            if st.button("Load All Leads instead?"):
                st.info("Switch the filter in the sidebar to 'All Leads' to see everyone.")
            st.stop()
        
        df = filtered_df
        st.sidebar.success(f"Showing {len(df)} leads due.")
    else:
        df = df

    # Session State for Current Index
    if "dialer_index" not in st.session_state:
        st.session_state.dialer_index = 0
        
    # Validation
    if st.session_state.dialer_index >= len(df):
        st.session_state.dialer_index = 0
        
    lead = df.iloc[st.session_state.dialer_index]
    
    # Premium Progress Section
    current_theme = st.session_state.get("theme", "light")
    progress_value = (st.session_state.dialer_index + 1) / len(df)
    progress_percent = int(progress_value * 100)
    
    # Theme colors
    card_bg = "#1E1E1E" if current_theme == "dark" else "#F8F9FA"
    text_color = "#FAFAFA" if current_theme == "dark" else "#1a1a1a"
    accent_color = "#FF8F00" if current_theme == "dark" else "#1976d2"
    bar_bg = "#2D2D30" if current_theme == "dark" else "#E0E0E0"
    
    # Progress Card with Metrics
    progress_card_html = f"""
    <div style="
        background: {card_bg};
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="color: {text_color}; margin: 0; font-size: 1.2rem; font-weight: 600;">
                    📊 Lead {st.session_state.dialer_index + 1} of {len(df)}
                </h3>
                <p style="color: {'#BBB' if current_theme == 'dark' else '#666'}; margin: 4px 0 0 0; font-size: 0.9rem;">
                    {progress_percent}% Complete
                </p>
            </div>
            <div style="display: flex; gap: 24px;">
                <div style="text-align: center;">
                    <div style="color: {'#BBB' if current_theme == 'dark' else '#666'}; font-size: 0.8rem; margin-bottom: 4px;">Completed</div>
                    <div style="color: {accent_color}; font-size: 1.5rem; font-weight: 700;">{st.session_state.dialer_index}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: {'#BBB' if current_theme == 'dark' else '#666'}; font-size: 0.8rem; margin-bottom: 4px;">Remaining</div>
                    <div style="color: {text_color}; font-size: 1.5rem; font-weight: 700;">{len(df) - st.session_state.dialer_index}</div>
                </div>
            </div>
        </div>
        <div style="
            width: 100%;
            height: 6px;
            background-color: {bar_bg};
            border-radius: 10px;
            overflow: hidden;
        ">
            <div style="
                width: {progress_percent}%;
                height: 100%;
                background: linear-gradient(90deg, {accent_color} 0%, {accent_color}dd 100%);
                border-radius: 10px;
                transition: width 0.3s ease;
            "></div>
        </div>
    </div>
    """
    st.markdown(progress_card_html, unsafe_allow_html=True)
    
    # Main Lead Card - Premium Design
    card_bg = "#1E1E1E" if current_theme == "dark" else "#FFFFFF"
    card_border = "#333" if current_theme == "dark" else "#E0E0E0"
    text_color = "#FAFAFA" if current_theme == "dark" else "#1a1a1a"
    
    lead_card_html = f"""
    <div style="
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h2 style="color: {text_color}; margin: 0 0 8px 0; font-size: 1.8rem;">
            🏢 {lead.get('businessName', 'Unknown Business')}
        </h2>
        <p style="color: {'#BBB' if current_theme == 'dark' else '#666'}; margin: 0 0 16px 0; font-size: 1rem;">
            {lead.get('contactName', 'No contact name')}
        </p>
    </div>
    """
    st.markdown(lead_card_html, unsafe_allow_html=True)
    
    # Lead Details in Columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 📋 Lead Information")
        
        # Follow-up Date with urgency
        f_date = lead.get('nextFollowUpDate')
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        if f_date:
            try:
                parsed_date = datetime.strptime(str(f_date), "%Y-%m-%d")
                display_date = parsed_date.strftime("%d/%m/%Y")
            except:
                display_date = f_date
            
            if f_date < today_str:
                st.error(f"⚠️ **Overdue:** {display_date}")
            elif f_date == today_str:
                st.warning(f"📅 **Due Today:** {display_date}")
            else:
                st.info(f"📅 **Scheduled:** {display_date}")
        else:
            st.caption("No specific follow-up date set")
        
        # Contact Details
        st.markdown(f"""
        **📍 Address:** {lead.get('address', 'N/A')}
        
        **📞 Phone:** `{lead.get('phone', 'No Phone')}`
        
        **📧 Email:** {lead.get('email', 'N/A')}
        """)
        
        # Status Badge Logic
        lead_status = lead.get('status', 'Generated')
        status_style_str = get_status_colors(current_theme).get(lead_status, "")
        
        if status_style_str:
             st.markdown(f"""
             **🎯 Priority:** {lead.get('priority', 'N/A')}
             
             **📊 Current Status:** <span style="{status_style_str}; padding: 4px 10px; border-radius: 12px; font-weight: 500; display: inline-block;">{lead_status}</span>
             """, unsafe_allow_html=True)
        else:
             st.markdown(f"""
             **🎯 Priority:** {lead.get('priority', 'N/A')}
             
             **📊 Current Status:** {lead_status}
             """)
        
        # Notes Card Design
        st.markdown(f"""
        <div style="margin-top: 20px; margin-bottom: 8px;">
            <div style="font-size: 1.1rem; font-weight: 600; color: {text_color}; display: flex; align-items: center; gap: 8px;">
                📝 Investigation Notes
            </div>
            <div style="font-size: 0.85rem; color: {'#BBB' if current_theme == 'dark' else '#666'}; margin-bottom: 5px;">
                Capture key details, next steps, and observations.
            </div>
        </div>
        <style>
        /* Targeted Text Area Styling for Dialer */
        div[data-testid="stTextArea"] textarea {{
            background-color: { '#262730' if current_theme == 'dark' else '#f8f9fa' } !important;
            border: 1px solid { '#444' if current_theme == 'dark' else 'transparent' } !important;
            box-shadow: { 'inset 0 2px 4px rgba(0,0,0,0.5)' if current_theme == 'dark' else 'inset 3px 3px 6px #cbcced, inset -3px -3px 6px #ffffff' } !important;
            border-radius: 12px !important;
            padding: 15px !important;
            font-size: 1rem !important;
            color: { '#E0E0E0' if current_theme == 'dark' else '#4d5b6b' } !important;
            transition: all 0.3s ease;
        }}
        div[data-testid="stTextArea"] textarea:focus {{
            box-shadow: { '0 0 0 2px #FF8F00' if current_theme == 'dark' else 'inset 4px 4px 8px #cbcced, inset -4px -4px 8px #ffffff' } !important;
            background-color: { '#2D2D30' if current_theme == 'dark' else '#ffffff' } !important;
            outline: none !important;
            border: 1px solid transparent !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        notes = st.text_area(
            "Notes",
            value=lead.get('callNotes') or "",
            height=180,
            key=f"notes_{lead['id']}",
            label_visibility="collapsed",
            placeholder="Type your notes here..."
        )
    
    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        # Get today's date for lastFollowUpDate
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        if st.button("✅ Interested", use_container_width=True, type="primary"):
            update_lead(lead['id'], {
                "status": "Interested", 
                "priority": "HOT", 
                "callNotes": notes,
                "lastFollowUpDate": today_date
            })
            st.session_state.dialer_index += 1
            st.rerun()
        
        if st.button("📅 Meeting Set", use_container_width=True, type="primary"):
            update_lead(lead['id'], {
                "status": "Meeting set", 
                "priority": "HOT", 
                "callNotes": notes,
                "lastFollowUpDate": today_date
            })
            st.session_state.dialer_index += 1
            st.rerun()
        
        if st.button("🚫 Not Picking", use_container_width=True):
            update_lead(lead['id'], {
                "status": "Not picking", 
                "callNotes": notes,
                "lastFollowUpDate": today_date
            })
            st.session_state.dialer_index += 1
            st.rerun()
        
        if st.button("⏰ Call Later", use_container_width=True):
            update_lead(lead['id'], {
                "status": "Asked to call later", 
                "callNotes": notes,
                "lastFollowUpDate": today_date
            })
            st.session_state.dialer_index += 1
            st.rerun()
        
        if st.button("❌ Not Interested", use_container_width=True):
            update_lead(lead['id'], {
                "status": "Not interested", 
                "callNotes": notes,
                "lastFollowUpDate": today_date
            })
            st.session_state.dialer_index += 1
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.dialer_index == 0)):
                st.session_state.dialer_index -= 1
                st.rerun()
        
        with nav_col2:
            if st.button("⏭️ Skip", use_container_width=True):
                st.session_state.dialer_index += 1
                st.rerun()

# ================== LEAD GENERATOR ==================
if "Lead Generator" in page:
    st.title("⚡ Lead Factory")
    
    with st.form("gen_form"):
        c1, c2 = st.columns(2)
        query = c1.text_input("Business Type", "Dentist")
        loc = c2.text_input("Location", "New York")
        submitted = st.form_submit_button("Start Mining Leads", type="primary")
        
    if submitted:
        with st.spinner("Disconnecting from matrix... (Scraping)"):
                # Call your backend API
                import requests
                try:
                    # Pass user token in headers
                    response = requests.post(
                        LEAD_GEN_API, 
                        json={"query": query, "location": loc},
                        headers=get_headers() # 👈 Added Header
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Leads generated successfully!")
                        # Offer download
                        st.download_button(
                            label="📥 Download CSV",
                            data=response.content,
                            file_name=f"leads_{query}_{loc}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error(f"Failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
                
    # --- HISTORY SECTION (Embedded) ---
    st.divider()
    st.subheader("📜 Execution History")
    
    data = fetch_data(EXECUTIONS_API)
    
    if not data:
        st.info("No execution history found.")
    else:
        # Convert to DataFrame
        history_df = pd.DataFrame(data)
        
        # Style logic reused from CRM Grid (Premium Dark)
        base_props = {'font-size': '14px', 'height': 'auto'}
        if st.session_state.theme == "dark":
            base_props.update({
                'background-color': '#1a1a1d', # Match Premium CSS
                'color': '#E0E0E0',
                'border-color': '#333'
            })
        else:
             base_props.update({'border-color': '#e0e0e0'})

        # Apply Styling
        if not history_df.empty:
            styled_history = history_df.style.set_properties(**base_props)

            st.dataframe(
                styled_history, 
                use_container_width=True, 
                hide_index=True
            )
        else:
             st.dataframe(history_df, use_container_width=True)
 