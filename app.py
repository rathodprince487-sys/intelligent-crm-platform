import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
from datetime import datetime

# ================== CONFIG ==================
import os
BACKEND_BASE = os.getenv("BACKEND_URL", "http://localhost:3000")
EXECUTIONS_API = f"{BACKEND_BASE}/executions"
LEADS_API = f"{BACKEND_BASE}/leads"
STATS_API = f"{BACKEND_BASE}/stats"
LEAD_GEN_API = f"{BACKEND_BASE}/lead-gen"

st.set_page_config(
    page_title="n8n CRM & Sales Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== STYLES ==================

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
/* Main Background */
.stApp {
    background: linear-gradient(to bottom right, #ffffff 0%, #f4f6f9 100%) !important;
    color: #1a1a1a !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
    border-right: 1px solid rgba(0,0,0,0.05);
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {
    color: #333333 !important;
}

/* Navigation - Active Item */
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(90deg, #E3F2FD 0%, #E3F2FD 100%) !important;
    color: #1565C0 !important;
    font-weight: 600;
    border-radius: 8px;
    border: none !important;
    /* Clean "Active" Pill Style */
    margin-left: 4px;
    margin-right: 4px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: transparent; /* Handled by specific rule below */
}

/* Inputs */
.stTextInput > div > div > input, .stSelectbox > div > div > div, .stTextArea > div > div > textarea {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
}

/* Cards */
/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.1);
    border-color: #cbd5e1;
}
.metric-icon {
    font-size: 1.5rem;
    margin-bottom: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: #eff6ff; /* Default Blue bg */
    color: #3b82f6; /* Default Blue text */
}
.metric-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 2.25rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
}

.meeting-card {
    display: flex;
    flex-direction: row;
    align-items: center;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #10b981; /* Green Line Restored */
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    transition: all 0.2s ease;
}
.meeting-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.08);
    border-color: #cbd5e1;
}
.mc-date-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 52px;
    height: 52px;
    background: #f1f5f9;
    border-radius: 10px;
    margin-right: 12px;
    flex-shrink: 0;
}
.mc-month {
    font-size: 0.65rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1;
    margin-bottom: 2px;
}
.mc-day {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1e293b;
    line-height: 1;
}
.mc-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden; /* For truncation */
}
.mc-title { 
    color: #1a202c !important; 
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mc-company { 
    color: #64748b !important;
    font-size: 0.75rem;
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}
.mc-action {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #e0f2f1;
    color: #00695c;
    border: 1px solid #b2dfdb;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
    text-decoration: none !important;
    align-self: flex-start;
    transition: all 0.2s;
}
.mc-action:hover {
    background: #b2dfdb;
    color: #004d40;
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
div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #e0e0e0 !important;
}
div[data-testid="stExpander"] summary {
    background-color: #f8f9fa !important;
    color: #1a1a1a !important;
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


/* Buttons */
div.stButton > button {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border: 1px solid #e0e0e0 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
div.stButton > button:hover {
    background-color: #f8f9fa !important;
    border-color: #1976d2 !important;
    color: #1976d2 !important;
}
/* Primary Button */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
    color: white !important;
    border: none !important;
}

/* Focus States */
.stTextInput > div > div > input:focus,
.stSelectbox > div > div > div:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #1976d2 !important;
    box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1) !important;
    outline: none !important;
}

/* Old .cal-btn removed in favor of .mc-action inside meeting card block */

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
    background-color: transparent !important;
    color: #0D47A1 !important; /* Deep Blue Text */
    border: none !important;
    font-weight: 700 !important;
    /* Minimal left indicator */
    border-left: 3px solid #0D47A1 !important;
    border-radius: 0px 4px 4px 0px !important;
}
div[role="radiogroup"] label:hover {
    background-color: transparent !important; 
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
/* Main Background - Premium Deep Slate */
.stApp {
    background: linear-gradient(to bottom right, #0f172a 0%, #020617 100%) !important;
    color: #cbd5e1 !important; /* Slate 300 - High legibility without harsh white */
}

/* UNIVERSAL TEXT STYLING - Ensure all text is visible in dark mode */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    color: #f8fafc !important; /* Bright white for headers */
}
.stApp p, .stApp span, .stApp div, .stApp label, .stApp li, .stApp td, .stApp th {
    color: #cbd5e1 !important; /* Light grey for body text */
}
.stApp a {
    color: #60a5fa !important; /* Blue for links */
}
.stApp a:hover {
    color: #93c5fd !important;
}
/* Captions and small text */
.stApp .stCaption, .stApp small, .stApp [data-testid="stCaption"] {
    color: #94a3b8 !important;
}
/* Code blocks */
.stApp code, .stApp pre {
    background-color: #1e293b !important;
    color: #e2e8f0 !important;
}

/* Sidebar - Glass-like Dark Pane */
section[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.98) !important; /* Deep Slate 900 */
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}
/* Sidebar Content Text */
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {
    color: #e2e8f0 !important; /* Slate 200 */
}

/* Navigation - Active Item - Premium Amber Pill */
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background: rgba(251, 191, 36, 0.1) !important; /* Amber 400 at 10% */
    color: #fbbf24 !important; /* Amber 400 */
    border: 1px solid rgba(251, 191, 36, 0.2) !important;
    border-radius: 8px;
    box-shadow: 0 0 15px rgba(251, 191, 36, 0.05); /* Subtle Glow */
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.03) !important;
    color: #fff !important;
}

/* Inputs - Integrated Deep Fields */
.stTextInput > div > div > input, .stSelectbox > div > div > div, .stTextArea > div > div > textarea {
    background-color: rgba(30, 41, 59, 0.6) !important; /* Slate 800 Alpha */
    color: #f1f5f9 !important; /* Slate 100 */
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
}
/* Input Focus State */
.stTextInput > div > div > input:focus, .stSelectbox > div > div > div:focus, .stTextArea > div > div > textarea:focus {
    border-color: #fbbf24 !important; /* Amber */
    box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.2) !important;
}

/* Cards (Metric & Meeting) - Layered Surface */
/* Metric Cards - Dark */
.metric-card {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.metric-card:hover {
    transform: translateY(-3px);
    background: rgba(30, 41, 59, 0.6) !important;
    border-color: rgba(251, 191, 36, 0.2) !important; /* Amber hint */
}
.metric-icon {
    font-size: 1.5rem;
    margin-bottom: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    color: #e2e8f0;
}
.metric-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #94a3b8 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 2.25rem;
    font-weight: 800;
    color: #f8fafc !important;
    line-height: 1.1;
}
.meeting-card {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-left: 4px solid #10b981 !important; /* Green Line Restored */
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    display: flex;
    flex-direction: row;
    align-items: center;
}
.mc-date-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 52px;
    height: 52px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    margin-right: 12px;
    flex-shrink: 0;
}
.mc-month {
    font-size: 0.65rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1;
    margin-bottom: 2px;
}
.mc-day {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e2e8f0;
    line-height: 1;
}
.mc-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.mc-title { 
    color: #f8fafc !important; 
    font-weight: 600; 
    font-size: 0.9rem;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mc-company { 
    color: #94a3b8 !important; 
    font-size: 0.75rem;
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mc-action {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(16, 185, 129, 0.1);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.2);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
    text-decoration: none !important;
    align-self: flex-start;
    transition: all 0.2s;
}
.mc-action:hover {
    background: rgba(16, 185, 129, 0.2);
    color: #6ee7b7;
}

/* DataFrames - Clean Dark Grid */
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    background-color: transparent !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}
/* Header Styling - Comprehensive Selectors */
div[data-testid="stDataFrame"] th, 
div[data-testid="stTable"] th,
div[data-testid="stDataFrame"] thead tr th,
div[data-testid="stDataFrame"] thead th,
table thead tr th,
table th,
.stDataFrame th,
[data-testid="stDataFrame"] table th,
[data-testid="stTable"] table th {
    background-color: #1e293b !important; /* Dark Slate Header */
    color: #f8fafc !important;
    font-weight: 600 !important;
    border-bottom: 1px solid #334155 !important;
}
/* Cell Styling */
div[data-testid="stDataFrame"] td, 
div[data-testid="stTable"] td,
table tbody tr td,
table td {
    background-color: #0f172a !important; /* Darker Slate Body */
    color: #cbd5e1 !important;
    border-bottom: 1px solid #1e293b !important;
}

/* Buttons - Subtle Secondary, Vibrant Primary */
div.stButton > button {
    background-color: rgba(255, 255, 255, 0.04) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px;
    font-weight: 500;
}
div.stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-color: #cbd5e1 !important;
    color: #fff !important;
}
/* Primary Action Button - Premium Gradient */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important; /* Amber 500 -> 600 */
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.3);
    font-weight: 600;
}
div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
    transform: translateY(-1px);
}

/* File Uploader - Integrated Dark Style */
div[data-testid="stFileUploader"] > div {
    background-color: rgba(30, 41, 59, 0.3) !important;
    border: 2px dashed rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}
div[data-testid="stFileUploader"] section {
    background-color: transparent !important;
}
div[data-testid="stFileUploader"] svg { fill: #94a3b8 !important; }
div[data-testid="stFileUploader"] small { color: #64748b !important; }
div[data-testid="stFileUploader"] span, div[data-testid="stFileUploader"] p { color: #cbd5e1 !important; }

/* Radio Buttons & Labels - High Contrast */
div[role="radiogroup"] label, 
div[role="radiogroup"] label p,
div[data-testid="stRadio"] label p {
    color: #f1f5f9 !important; /* Bright Text */
    font-weight: 500 !important;
}
/* Widget Label (e.g. "Filter Leads:") */
label[data-testid="stLabel"], 
div[data-testid="stWidgetLabel"] label,
div[data-testid="stWidgetLabel"] p {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
/* Selected Option Highlight */
div[role="radiogroup"] div[aria-checked="true"] label p {
    color: #f59e0b !important; /* Amber Highlight */
    font-weight: 700 !important;
}

/* Expander - Clean Borders */
div[data-testid="stExpander"] {
    background-color: transparent !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}
div[data-testid="stExpander"] summary {
    color: #e2e8f0 !important;
}
div[data-testid="stExpander"] summary:hover {
    color: #fff !important;
    background-color: rgba(255, 255, 255, 0.02) !important;
}

/* Progress Bar */
div[data-testid="stProgress"] > div > div {
    background-color: #f59e0b !important; /* Amber Match */
}

/* Streamlit Alerts / Info Boxes */
div[data-testid="stAlert"] {
    background-color: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #e2e8f0 !important;
}

/* Radio Buttons Modern - Spacing & Visibility */
div[role="radiogroup"] {
    gap: 6px !important;
}
div[role="radiogroup"] label {
    background-color: transparent !important;
    border: 1px solid transparent !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    transition: all 0.2s ease;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background: transparent !important;
    color: #fbbf24 !important; /* Amber 400 */
    border: none !important;
    border-left: 3px solid #fbbf24 !important;
    border-radius: 0px 4px 4px 0px !important;
    box-shadow: none !important;
}
div[role="radiogroup"] label:hover {
    background-color: transparent !important;
    border-color: transparent !important;
    color: #e2e8f0 !important;
    transform: translateX(4px);
}

/* Old .cal-btn removed */
</style>
"""

# ================== HELPER FUNCTIONS ==================
def metric_card(label, value, icon="📊", color="blue"):
    """
    Renders a styled metric card.
    color options: blue, green, amber, purple, rose
    """
    
    # Define color maps for Light/Dark styling adjustments if needed
    # using inline css vars or just relying on helper classes could work, 
    # but let's do a simple inline override for the icon bg
    
    color_map = {
        "blue":   {"bg": "#eff6ff", "text": "#3b82f6", "dark_bg": "rgba(59, 130, 246, 0.1)", "dark_text": "#60a5fa"},
        "green":  {"bg": "#f0fdf4", "text": "#22c55e", "dark_bg": "rgba(34, 197, 94, 0.1)",  "dark_text": "#4ade80"},
        "amber":  {"bg": "#fffbeb", "text": "#f59e0b", "dark_bg": "rgba(245, 158, 11, 0.1)", "dark_text": "#fbbf24"},
        "purple": {"bg": "#f3e8ff", "text": "#a855f7", "dark_bg": "rgba(168, 85, 247, 0.1)", "dark_text": "#c084fc"},
        "rose":   {"bg": "#ffe4e6", "text": "#f43f5e", "dark_bg": "rgba(244, 63, 94, 0.1)",  "dark_text": "#fb7185"},
    }
    
    c = color_map.get(color, color_map["blue"])
    
    # We use a unique ID or class to inject specific colors for this card instance? 
    # Actually, simpler to just inject style attribute on the icon.
    
    # Check Theme (Python side check for rendering slightly different inline styles if strictly needed, 
    # but CSS classes are cleaner. Let's send both vars and let CSS vars handle it? 
    # Streamlit doesn't support CSS vars easily dynamically.
    # We'll use the session state theme.
    
    theme = st.session_state.get("theme", "light")
    icon_bg = c["dark_bg"] if theme == "dark" else c["bg"]
    icon_col = c["dark_text"] if theme == "dark" else c["text"]
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon" style="background-color: {icon_bg}; color: {icon_col};">
            {icon}
        </div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def fetch_data(url):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def update_lead(lead_id, data):
    try:
        requests.put(f"{LEADS_API}/{lead_id}", json=data)
        return True
    except:
        return False

def create_lead(data):
    try:
        requests.post(f"{BACKEND_BASE}/leads", json=data)
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
        requests.delete(f"{LEADS_API}/{lead_id}")
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
if "theme" not in st.session_state:
    st.session_state.theme = "light"

st.markdown(COMMON_CSS, unsafe_allow_html=True)

if st.session_state.theme == "dark":
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# ================== SIDEBAR NAVIGATION ==================
# ================== SIDEBAR NAVIGATION ==================
import base64
import os

def get_sidebar_img_b64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

sb_logo_dark = get_sidebar_img_b64("logo.png")
sb_logo_light = get_sidebar_img_b64("logo_light.png")

if sb_logo_dark and sb_logo_light:
    # Use logo based on ACTIVE THEME state
    target_logo = sb_logo_dark if st.session_state.get("theme") == "dark" else sb_logo_light
    
    st.sidebar.markdown(f"""
    <div style="margin-bottom: 20px;">
        <img src="data:image/png;base64,{target_logo}" style="width: 100%;">
    </div>
    """, unsafe_allow_html=True)
elif sb_logo_dark:
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.title("SHDPIXEL")

# Navigation
page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Dashboard", 
        "🗂 CRM Grid", 
        "📞 Power Dialer", 
        "⚡ Lead Generator", 
        "📜 Lead Gen History",
        "🧠 Spreadsheet Tool",
        "🗺️ Google Maps Scraper"
    ],
    label_visibility="collapsed"
)
st.sidebar.markdown("---") 

    # ... (Rest of Sidebar code remains, skipping to Main Page replacement)

# ... (We will use a separate Replace block for the main page to avoid replacing huge chunks of unrelated code) 
# I will actually split this into two calls for safety or just target the sidebar first. 
# wait, I can only do one replacement per tool call effectively if they are far apart. 
# I'll do Sidebar first.

# --- SETTINGS (Bottom) ---
st.sidebar.header("⚙️ Settings")

# Theme Toggle
if st.session_state.theme == "light":
    if st.sidebar.button("🌙 Switch to Dark Mode", use_container_width=True):
        st.session_state.theme = "dark"
        st.rerun()
else:
    if st.sidebar.button("☀️ Switch to Light Mode", use_container_width=True):
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
                            <div class="mc-date-box">
                                <span class="mc-month">{m_date.strftime('%b').upper()}</span>
                                <span class="mc-day">{m_date.strftime('%d')}</span>
                            </div>
                            <div class="mc-details">
                                <div class="mc-title" title="{comp}">{comp}</div>
                                <div class="mc-company" title="{name}">👤 {name}</div>
                                <a href="{cal_url}" target="_blank" class="mc-action">
                                    📅 Add to Cal
                                </a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
except Exception as e:
    # Fail silently to not break main app
    st.sidebar.caption(f"Syncing calendar... ({e})")

# ================== DASHBOARD ==================
if "Dashboard" in page:
    st.markdown("""
    <div style="margin-bottom: 25px; margin-top: 10px;">
        <h1 style="margin: 0; padding: 0; font-size: 2.2rem; font-weight: 800; display: flex; align-items: center; gap: 15px;">
            <div style="
                display: flex; 
                align-items: center; 
                justify-content: center; 
                width: 50px; 
                height: 50px; 
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
                border-radius: 12px; 
                font-size: 1.6rem; 
                box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
                color: white;
            ">
                📊
            </div>
            <span>CRM Overview</span>
        </h1>
        <p style="margin-left: 65px; margin-top: -5px; opacity: 0.7; font-size: 1rem;">
            Real-time insights and pipeline performance
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fetch all leads directly to calculate custom splits
    leads = fetch_data(LEADS_API)
    df_all = pd.DataFrame(leads)
    
    # ALWAYS RENDER CARDS (Empty or Not)
    # Split Data
    if df_all.empty:
        df_generated = pd.DataFrame(columns=["id", "status"])
        df_crm = pd.DataFrame(columns=["id", "status"])
    else:
        # 1. Generated (Fresh leads, unworked)
        df_generated = df_all[df_all['status'] == 'Generated']
        # 2. CRM (Everything else)
        df_crm = df_all[df_all['status'] != 'Generated']
    
    # --- SECTION 1: LEAD GENERATION ---
    st.subheader("⚡ Lead Generation (Data Mining)")
    c1, c2, c3 = st.columns(3)
    with c1: metric_card("Fresh Leads Available", len(df_generated), icon="✨", color="blue")
    with c2: metric_card("Recent Imports", 0 if df_all.empty else len(df_generated[df_generated['id'].astype(int) > (len(df_all)-10)]), icon="📥", color="purple")
    
    # --- SECTION 2: CRM PIPELINE ---
    st.markdown("---")
    st.subheader("💼 Active Pipeline (CRM)")
    
    # Calculate CRM specific metrics
    crm_total = len(df_crm)
    if not df_crm.empty and 'priority' in df_crm.columns:
        hot_leads = len(df_crm[df_crm['priority'] == 'HOT'])
    else:
        hot_leads = 0
        
    if not df_crm.empty and 'status' in df_crm.columns:
        meetings = len(df_crm[df_crm['status'].str.contains("Meeting", case=False, na=False)])
        closed_won = len(df_crm[df_crm['status'] == 'Closed - Won'])
    else:
        meetings = 0
        closed_won = 0
    
    c_a, c_b, c_c, c_d = st.columns(4)
    with c_a: metric_card("In Pipeline", crm_total, icon="📊", color="blue")
    with c_b: metric_card("Hot Opportunities", hot_leads, icon="🔥", color="rose")
    with c_c: metric_card("Meetings Set", meetings, icon="📅", color="amber")
    with c_d: metric_card("Closed Won", closed_won, icon="🏆", color="green")

    # st.markdown("---")
    # if breakdown:
    #     ...

# ================== CRM GRID (PIPELINE) ==================
if "CRM Grid" in page:
    st.title("🗂 Advanced CRM Grid")
    
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
                            "nextFollowUpDate": str(next_f) if not pd.isna(next_f) else None
                        }
                        
                        if create_lead(payload):
                            count += 1
                        progress_bar.progress(min((idx + 1) / len(import_df), 1.0))
                    
                    st.success(f"Successfully imported {count} leads!")
                    st.rerun()

            except Exception as e:
                st.error(f"Error reading file: {e}")

    # --- Grid Section ---
    leads = fetch_data(LEADS_API)
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
        div[data-testid="stSlider"] {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
            margin-top: -10px !important;
        }
        div[data-testid="stSlider"] label {
            display: none;
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



    # CSS Injection (Updated for new Scale + Conditional Dark Mode)
    # Build dark mode CSS only if theme is dark (and create light mode CSS explicitly if theme is light)
    grid_css_conditional = ""
    
    if st.session_state.get("theme") == "dark":
        grid_css_conditional = """
    /* DARK MODE STYLING FOR CRM GRID */
    div[data-testid="stDataEditor"] canvas {
        filter: invert(1) hue-rotate(180deg) brightness(0.9) contrast(1.1);
    }
    div[data-testid="stDataEditor"], [data-testid="stDataEditor"] * {
        background-color: #0f172a !important;
        color: #cbd5e1 !important;
        border-color: #334155 !important;
    }
    div[data-testid="stDataEditor"] div[style*="background"], div[data-testid="stDataEditor"] div[style*="white"] {
        background-color: #1e293b !important;
    }
    /* Headers */
    div[data-testid="stDataEditor"] thead tr th, [role="columnheader"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }
        """
    else:
        # LIGHT MODE (Explicitly Force White to override any auto-dark behavior)
        grid_css_conditional = """
    /* LIGHT MODE STYLING FOR CRM GRID */
    div[data-testid="stDataEditor"], [data-testid="stDataEditor"] * {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border-color: #e2e8f0 !important;
    }
    div[data-testid="stDataEditor"] canvas {
        filter: none !important;
    }
    /* Headers */
    div[data-testid="stDataEditor"] thead tr th, [role="columnheader"] {
        background-color: #f8f9fa !important;
        color: #334155 !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
        """
    
    st.markdown(f"""
    <style>
    section.main > .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100vw !important;
        width: 100vw !important;
    }}
    div[data-testid="stDataEditor"], div[data-testid="stDataFrame"] {{
        zoom: {scale_val};
        width: {width_str} !important;
        min-width: {width_str} !important;
        max-width: none !important;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    div[data-testid="stDataEditor"] canvas {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    {grid_css_conditional}
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

# ==========================
# TOOL: SPREADSHEET INTELLIGENCE
# ==========================
# ==========================
# TOOL: SPREADSHEET INTELLIGENCE
# ==========================
if "Spreadsheet" in page:
    st.title("🧠 Spreadsheet Intelligence Tool")

    st.markdown("""
    Advanced analysis for Excel workbooks. Splits duplicates/uniques by sheet and finds new rows across files.
    """)

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

    tab1, tab2, tab3 = st.tabs(["📂 Single File Analysis (Dups vs Uniques)", "🔁 1-vs-1 Comparison", "📚 Multi-File vs Baseline"])

    # ==========================
    # TAB 1: SINGLE FILE (ALL SHEETS)
    # ==========================
    with tab1:
        # Define Helper
        def load_excel_safe_single(file_obj, respect_filters=True):
            if not respect_filters:
                file_obj.seek(0)
                return pd.read_excel(file_obj, sheet_name=None), 0

            import openpyxl
            file_obj.seek(0)
            wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=False)
            xls = {}
            total_hidden_skipped = 0
            
            for s_name in wb.sheetnames:
                ws = wb[s_name]
                if ws.sheet_state != 'visible': continue
                    
                data = []
                sheet_hidden_count = 0
                
                rows_iter = ws.iter_rows()
                try:
                    header_row = next(rows_iter)
                    raw_headers = [cell.value for cell in header_row]
                    headers = []
                    counts = {}
                    for i, h in enumerate(raw_headers):
                        h_str = str(h).strip() if h is not None else f"Unnamed: {i}"
                        if h_str == "": h_str = f"Unnamed: {i}"
                        if h_str in counts:
                            counts[h_str] += 1
                            headers.append(f"{h_str}.{counts[h_str]}")
                        else:
                            counts[h_str] = 0
                            headers.append(h_str)
                except StopIteration:
                    continue # Empty sheet

                for row in rows_iter:
                    current_row_idx = row[0].row
                    is_hidden = False
                    if current_row_idx in ws.row_dimensions:
                        dim = ws.row_dimensions[current_row_idx]
                        if dim.hidden: is_hidden = True
                        
                    if is_hidden:
                        sheet_hidden_count += 1
                    else:
                        row_values = [cell.value for cell in row]
                        if len(row_values) < len(headers):
                            row_values += [None] * (len(headers) - len(row_values))
                        elif len(row_values) > len(headers):
                            row_values = row_values[:len(headers)]
                        data.append(row_values)
                
                total_hidden_skipped += sheet_hidden_count
                if data:
                    xls[s_name] = pd.DataFrame(data, columns=headers)
                else:
                    xls[s_name] = pd.DataFrame(columns=headers)
            
            return xls, total_hidden_skipped

        st.markdown("#### 🚀 Single File Duplicate Analysis")
        st.caption("Process a workbook to separate Duplicates and Unique rows into distinct sheets.")

        # STEP 1: UPLOAD
        with st.container(border=True):
            st.markdown("**📁 Step 1: Upload Workbook**")
            f_single = st.file_uploader("Upload Excel Workbook (.xlsx)", type=['xlsx'], key="sit_single")

        if f_single:
            try:
                # STEP 2: CONFIGURE
                with st.container(border=True):
                    st.markdown("**⚙️ Step 2: Configure Analysis**")
                    
                    use_excel_filters = st.checkbox("Respect Excel Filters (Exclude Hidden Rows)", value=True, help="Make sure to SAVE your Excel file with the filters active before uploading.")
                    
                    xls, total_hidden_skipped = load_excel_safe_single(f_single, use_excel_filters)
                    
                    if use_excel_filters:
                        if total_hidden_skipped > 0:
                            st.success(f"✅ Successfully excluded {total_hidden_skipped} hidden rows from analysis.")
                        else:
                            st.warning("⚠️ No hidden rows were detected. Please ensure you SAVED the Excel file with filters applied.")
                    
                    sheet_names = list(xls.keys())
                    
                    # Check for empty sheets
                    valid_sheets = {k: v for k, v in xls.items() if not v.empty}
                    
                    if not valid_sheets:
                        st.error("Workbook contains no data.")
                    else:
                        st.success(f"Loaded {len(valid_sheets)} sheets: {', '.join(valid_sheets.keys())}")
                        
                        # 2. COLUMN SELECTION (Global)
                        all_cols = set()
                        for df in valid_sheets.values():
                            all_cols.update(df.columns.astype(str))
                        
                        target_cols = st.multiselect("Select Duplicate Key Columns (e.g. Email, Phone)", sorted(list(all_cols)))

                if target_cols:
                     if st.button("🚀 Process Workbook", type="primary", use_container_width=True):

                    

                            




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
                                
                                # 1. Identify ALL duplicate instances (for location reporting)
                                all_dups_mask = master_valid.duplicated(subset=norm_keys, keep=False)
                                
                                # Handle empty keys 
                                empty_mask = master_valid[norm_keys].isna().all(axis=1)
                                all_dups_mask = all_dups_mask & (~empty_mask)

                                # 2. Identify ONLY 2nd+ instances (for removal/splitting)
                                # keep='first' marks duplicates as True, except the first one (Unique).
                                split_mask = master_valid.duplicated(subset=norm_keys, keep='first')
                                split_mask = split_mask & (~empty_mask)
                                
                                master_valid['is_duplicate'] = split_mask

                                # 3. Generate Location Map using ALL instances
                                if not master_valid.empty and all_dups_mask.any():
                                    dup_rows_all = master_valid[all_dups_mask].copy()
                                    dup_rows_all['__loc_label'] = dup_rows_all['_sheet'] + " (Row " + (dup_rows_all['_idx'] + 2).astype(str) + ")"
                                    dup_rows_all['__group_key'] = dup_rows_all[norm_keys].apply(tuple, axis=1)
                                    
                                    loc_map = dup_rows_all.groupby('__group_key')['__loc_label'].apply(lambda x: ", ".join(x)).to_dict()
                                    
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
        # Define helper first (cleaner scope)
        def load_excel_safe(file_obj, respect_filters=True):
            """Helper to load excel, respecting hidden rows if requested."""
            if not respect_filters:
                file_obj.seek(0)
                return pd.read_excel(file_obj, sheet_name=None)
            
            import openpyxl
            file_obj.seek(0)
            wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=False)
            res = {}
            for s_name in wb.sheetnames:
                ws = wb[s_name]
                if ws.sheet_state != 'visible': continue
                
                data = []
                rows_iter = ws.iter_rows()
                try:
                    header_row = next(rows_iter)
                    raw_headers = [cell.value for cell in header_row]
                    headers = []
                    counts = {}
                    for i, h in enumerate(raw_headers):
                        h_str = str(h).strip() if h is not None else f"Unnamed: {i}"
                        if h_str == "": h_str = f"Unnamed: {i}"
                        if h_str in counts:
                            counts[h_str] += 1
                            headers.append(f"{h_str}.{counts[h_str]}")
                        else:
                            counts[h_str] = 0
                            headers.append(h_str)
                except StopIteration:
                    continue

                for row in rows_iter:
                    current_row_idx = row[0].row
                    is_hidden = False
                    if current_row_idx in ws.row_dimensions:
                        dim = ws.row_dimensions[current_row_idx]
                        if dim.hidden:
                            is_hidden = True
                    
                    if not is_hidden:
                        row_values = [cell.value for cell in row]
                        if len(row_values) < len(headers):
                            row_values += [None] * (len(headers) - len(row_values))
                        elif len(row_values) > len(headers):
                            row_values = row_values[:len(headers)]
                        data.append(row_values)
                
                if data:
                    res[s_name] = pd.DataFrame(data, columns=headers)
                else:
                    res[s_name] = pd.DataFrame(columns=headers)
            return res

        # UI STRUTURE
        st.markdown("#### 🚀 Compare Two Excel Files")
        st.caption("Identify rows in File B (New) that are missing from File A (Baseline).")

        # STEP 1: UPLOADS
        with st.container(border=True):
            st.markdown("**📁 Step 1: Upload Files**")
            c1, c2 = st.columns(2)
            f_a = c1.file_uploader("File A (Baseline / Old)", type=['xlsx'], key="sit_a_1")
            f_b = c2.file_uploader("File B (New / Update)", type=['xlsx'], key="sit_b_1")

        if f_a and f_b:
            try:
                # 1. READ BOTH
                with st.container(border=True):
                    st.markdown("**⚙️ Step 2: Configure Data**")
                    
                    use_filters_cross = st.checkbox("Respect Excel Filters (Exclude Hidden Rows)", value=True, help="Make sure to SAVE your Excel files with filters active.", key="cross_filter_check_1")

                    xls_a = load_excel_safe(f_a, use_filters_cross)
                    xls_b = load_excel_safe(f_b, use_filters_cross)
                    
                    if not xls_a or not xls_b:
                        st.error("One or both workbooks contain no visible data.")
                    else:
                        all_cols_b = set()
                        for df in xls_b.values():
                            # Clean Unnamed cols for selection
                            clean_cols = [c for c in df.columns if not str(c).startswith("Unnamed")]
                            all_cols_b.update(clean_cols)
                        
                        match_cols = st.multiselect("Select Unique Identifier Columns (e.g. Email, ID)", sorted(list(all_cols_b)), key="ms_1")

                if match_cols and st.button("🚀 Find New Rows in B", type="primary", use_container_width=True, key="btn_1"):
                    
                    # Helper for styling
                    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                    from openpyxl.utils import get_column_letter

                    def format_and_autofit_sheet(ws, df):
                        # 1. Header Style
                        header_font = Font(bold=True, color="FFFFFF")
                        header_fill = PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid") # Green like screenshot
                        center_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
                        
                        # Apply to Row 1
                        for cell in ws[1]:
                            cell.font = header_font
                            cell.fill = header_fill
                            cell.alignment = center_align
                        
                        # 2. Auto-Filter & Freeze Panes
                        ws.auto_filter.ref = ws.dimensions
                        ws.freeze_panes = "A2"
                        
                        # 3. Auto-fit Columns
                        for i, col in enumerate(df.columns, 1):
                            max_len = len(str(col)) + 4
                            col_letter = get_column_letter(i)
                            
                            # Sample data for width
                            for row_x in range(min(len(df), 20)):
                                val = df.iloc[row_x, i-1]
                                if val:
                                    max_len = max(max_len, len(str(val)))
                            
                            # Cap width
                            adjusted_width = min(max_len + 2, 50) 
                            ws.column_dimensions[col_letter].width = adjusted_width
                            
                            # Apply wrap text to all data cells
                            for cell in ws[col_letter]:
                                cell.alignment = Alignment(wrap_text=True, vertical="top")
                                # Reset header align
                                if cell.row == 1:
                                    cell.alignment = center_align

                    with st.spinner("Building baseline from File A..."):
                        baseline_tuples = set()
                        count_a = 0
                        for df in xls_a.values():
                            valid_cols = [c for c in match_cols if c in df.columns]
                            if len(valid_cols) != len(match_cols): continue
                            temp = df[valid_cols].copy()
                            for c in valid_cols:
                                temp[c] = temp[c].apply(normalize_text)
                            temp = temp.dropna(how='all')
                            count_a += len(temp)
                            baseline_tuples.update(list(temp.itertuples(index=False, name=None)))
                        
                    with st.spinner(f"Comparing File B ({len(xls_b)} sheets) against {len(baseline_tuples)} unique baseline records..."):
                        output_b = io.BytesIO()
                        writer_b = pd.ExcelWriter(output_b, engine='openpyxl')
                        total_new = 0
                        results_b = {}
                        
                        for s_name, df in xls_b.items():
                            # Remove 'Unnamed' columns from processing/output
                            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                            
                            valid_cols = [c for c in match_cols if c in df.columns]
                            if len(valid_cols) != len(match_cols): continue
                            temp_b = df.copy()
                            norm_keys = []
                            for c in valid_cols:
                                norm_n = f"__norm_{c}"
                                temp_b[norm_n] = temp_b[c].apply(normalize_text)
                                norm_keys.append(norm_n)
                            temp_b_valid = temp_b.dropna(subset=norm_keys, how='all')
                            temp_b_valid['__tuple'] = temp_b_valid[norm_keys].apply(tuple, axis=1)
                            new_rows_mask = ~temp_b_valid['__tuple'].isin(baseline_tuples)
                            new_rows_df = temp_b_valid[new_rows_mask]
                            
                            # Use cleaned columns for output
                            final_new = new_rows_df[[c for c in df.columns if c in new_rows_df.columns]]
                            
                            cnt = len(final_new)
                            total_new += cnt
                            results_b[s_name] = final_new
                            if cnt > 0:
                                sheet_n = f"{s_name[:20]}_New"
                                final_new.to_excel(writer_b, sheet_name=sheet_n, index=False)
                                # Apply Styling
                                format_and_autofit_sheet(writer_b.sheets[sheet_n], final_new)
                        
                        writer_b.close()
                        
                        c_m1, c_m2, c_m3 = st.columns(3)
                        c_m1.metric("Baseline Rows (A)", count_a)
                        c_m2.metric("Total Rows Processed (B)", sum([len(d) for d in xls_b.values()]))
                        c_m3.metric("New Unique Rows Found", total_new, delta_color="normal")
                        
                        st.markdown("### 🆕 New Rows per Sheet")
                        for s, df_new in results_b.items():
                            cnt = len(df_new)
                            if cnt > 0:
                                with st.expander(f"{s} ({cnt} New Rows)"):
                                    st.warning(f"Found {cnt} rows unique to File B.")
                                    st.dataframe(df_new, use_container_width=True)
                            else:
                                with st.expander(f"{s} (No New Rows)"):
                                    st.success("All rows in this sheet already exist in File A.")
                        
                        # --- FULL PREVIEW SECTION ---
                        st.markdown("---")
                        st.subheader("👁️ Full File Content Preview")
                        st.caption("Browse all generated new rows across all sheets.")
                        
                        valid_sheets_res = [s for s, d in results_b.items() if not d.empty]
                        if valid_sheets_res:
                            sheet_tabs = st.tabs(valid_sheets_res)
                            for i, s_name in enumerate(valid_sheets_res):
                                with sheet_tabs[i]:
                                    st.dataframe(results_b[s_name], height=600, use_container_width=True)
                        else:
                            st.info("No new rows found to preview.")

                        # --- ACTIONS ---
                        # --- ACTIONS ---
                        st.markdown("### 📤 Actions")
                        
                        # Custom Filename Input
                        custom_filename = st.text_input("Output File Name (Optional)", value="comparison_unique_to_B", help="Enter a name for the output Excel file.")
                        final_file_name = custom_filename.strip()
                        if not final_file_name.lower().endswith(".xlsx"):
                            final_file_name += ".xlsx"
                        
                        col_actions = st.columns([1, 1, 2])
                        
                        if total_new > 0:
                            processed_b = output_b.getvalue()
                            
                            # 1. Download Button
                            with col_actions[0]:
                                st.download_button(
                                    label="📥 Download Result",
                                    data=processed_b,
                                    file_name=final_file_name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary"
                                )
                            
                            # 2. Upload to Drive Button (Optional Section)
                            with col_actions[1]:
                                with st.expander("☁️ Save to Google Drive (Optional)"):
                                    import os
                                    has_creds = os.path.exists("service-account.json")
                                    
                                    if not has_creds:
                                        st.warning("Setup Required")
                                        st.caption("To enable one-click uploads, you need a **Google Service Account Key**.")
                                        st.caption("Don't want to set this up? Just use the **Download** button on the left instead!")
                                        
                                        uploaded_key = st.file_uploader("Upload service-account.json", type=['json'], key="sa_uploader")
                                        if uploaded_key:
                                            with open("service-account.json", "wb") as f:
                                                f.write(uploaded_key.getbuffer())
                                            st.success("✅ Credentials saved! refreshing...")
                                            st.rerun()
                                    else:
                                        # Creds exist, try to upload
                                        try:
                                            # Check usage dependencies
                                            try:
                                                from googleapiclient.discovery import build
                                                from google.oauth2 import service_account
                                                from googleapiclient.http import MediaIoBaseUpload
                                            except ImportError:
                                                st.error("Missing Google Libraries.")
                                                if st.button("🔧 Install Google Dependencies"):
                                                    import subprocess, sys
                                                    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"])
                                                    st.rerun()
                                                st.stop()

                                            if st.button("☁️ Upload Now"):
                                                SCOPES = ['https://www.googleapis.com/auth/drive.file']
                                                creds = service_account.Credentials.from_service_account_file(
                                                    'service-account.json', scopes=SCOPES)
                                                drive_service = build('drive', 'v3', credentials=creds)
                                                
                                                file_metadata = {'name': final_file_name}
                                                
                                                media = MediaIoBaseUpload(io.BytesIO(processed_b), 
                                                                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                                                        resumable=True)
                                                
                                                with st.spinner(f"Uploading '{final_file_name}' to Google Drive..."):
                                                    file = drive_service.files().create(body=file_metadata,
                                                                                        media_body=media,
                                                                                        fields='id, webViewLink').execute()
                                                    
                                                st.success(f"✅ Uploaded! [Open in Drive]({file.get('webViewLink')})")
                                                
                                        except Exception as e:
                                            st.error(f"Upload failed: {e}")

            except Exception as e:
                st.error(f" Comparison Error: {e}")

    # ==========================
    # TAB 3: MULTI FILE (Multiple vs One)
    # ==========================
    with tab3:
        # Define Helper First
        def load_excel_safe_multi(file_obj, respect_filters=True):
            # We need to always use openpyxl to get row indices, even if filters are off
            # because we need to map back to the original file for deletion.
            import openpyxl
            file_obj.seek(0)
            wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=False)
            res = {}
            for s_name in wb.sheetnames:
                ws = wb[s_name]
                if ws.sheet_state != 'visible': continue
                
                data = []
                rows_iter = ws.iter_rows()
                try:
                    header_row = next(rows_iter)
                    raw_headers = [cell.value for cell in header_row]
                    headers = []
                    counts = {}
                    for i, h in enumerate(raw_headers):
                        h_str = str(h).strip() if h is not None else f"Unnamed: {i}"
                        if h_str == "": h_str = f"Unnamed: {i}"
                        if h_str in counts:
                            counts[h_str] += 1
                            headers.append(f"{h_str}.{counts[h_str]}")
                        else:
                            counts[h_str] = 0
                            headers.append(h_str)
                except StopIteration:
                        continue

                # Add a special column for Row Index
                headers.append("__row_idx")

                for row in rows_iter:
                    current_row_idx = row[0].row
                    is_hidden = False
                    if respect_filters and current_row_idx in ws.row_dimensions:
                        dim = ws.row_dimensions[current_row_idx]
                        if dim.hidden: is_hidden = True
                    
                    if not is_hidden:
                        row_values = [cell.value for cell in row]
                        # Pad or trim
                        # The headers list now includes __row_idx at the end, so we compare against len(headers)-1
                        expected_cols = len(headers) - 1
                        if len(row_values) < expected_cols:
                            row_values += [None] * (expected_cols - len(row_values))
                        elif len(row_values) > expected_cols:
                            row_values = row_values[:expected_cols]
                        
                        # Append the row index
                        row_values.append(current_row_idx)
                        data.append(row_values)
                
                if data:
                    res[s_name] = pd.DataFrame(data, columns=headers)
                else:
                    res[s_name] = pd.DataFrame(columns=headers)
            return res

        # UI
        st.markdown("#### 🚀 Multi-File Deduplication")
        st.caption("Compares Multiple Files (B) against One Baseline File (A). Outputs Cleaned Versions of B.")

        # STEP 1: UPLOAD
        with st.container(border=True):
            st.markdown("**📁 Step 1: Upload Files**")
            c1, c2 = st.columns(2)
            files_a_multi = c1.file_uploader("Files A (Baseline / Old)", type=['xlsx'], accept_multiple_files=True, key="sit_a_multi")
            files_b_multi = c2.file_uploader("Files B (New / Update)", type=['xlsx'], accept_multiple_files=True, key="sit_b_multi")

        if files_a_multi and files_b_multi:
            try:
                # STEP 2: CONFIGURE
                with st.container(border=True):
                    st.markdown("**⚙️ Step 2: Configure & Process**")
                    
                    use_filters_multi = st.checkbox("Respect Excel Filters (Exclude Hidden Rows)", value=True, help="Make sure to SAVE your Excel files with filters active.", key="cross_filter_check_multi")

                    # Load A (Baseline)
                    xls_a_map = {}
                    for f in files_a_multi:
                        xls_a_map[f.name] = load_excel_safe_multi(f, use_filters_multi)
                    
                    # Load B (Target)
                    xls_b_map = {} 
                    for f in files_b_multi:
                        xls_b_map[f.name] = load_excel_safe_multi(f, use_filters_multi)

                    if not xls_a_map or not xls_b_map:
                        st.error("Baseline or Comparison files contain no visible data.")
                    else:
                        # Collect all columns from B (excluding __row_idx) to choose match cols
                        all_cols_b = set()
                        for f_name, sheets in xls_b_map.items():
                            for df in sheets.values():
                                cols = [c for c in df.columns if c != "__row_idx"]
                                all_cols_b.update(cols)
                        
                        match_cols = st.multiselect("Select Unique Identifier Columns", sorted(list(all_cols_b)), key="multi_col_select")

                    if match_cols:
                        if st.button("🚀 Find New Rows (Clean Files)", type="primary", use_container_width=True, key="btn_multi"):
                            
                            # 1. BUILD BASELINE
                            with st.spinner("Building combined baseline from Files A..."):
                                baseline_tuples = set()
                                count_a = 0
                                for f_name, sheets in xls_a_map.items():
                                    for df in sheets.values():
                                        valid_cols = [c for c in match_cols if c in df.columns]
                                        if len(valid_cols) != len(match_cols): continue
                                        temp = df[valid_cols].copy()
                                        for c in valid_cols:
                                            temp[c] = temp[c].apply(normalize_text)
                                        temp = temp.dropna(how='all')
                                        count_a += len(temp)
                                        baseline_tuples.update(list(temp.itertuples(index=False, name=None)))
                            
                            # 2. PROCESS FILES
                            import zipfile
                            import io
                            import openpyxl

                            # We will create a Zip file containing the "Cleaned" versions of File B
                            zip_buffer = io.BytesIO()
                            
                            with st.spinner("Processing files... Removing duplicates while preserving styles."):
                                processed_count = 0
                                total_removed = 0
                                
                                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                                    
                                    for f_obj in files_b_multi:
                                        f_name = f_obj.name
                                        sheets_data = xls_b_map.get(f_name, {})
                                        
                                        # We need to modify the ORIGINAL file
                                        f_obj.seek(0)
                                        wb = openpyxl.load_workbook(f_obj)
                                        
                                        file_removed_count = 0
                                        
                                        for s_name, df in sheets_data.items():
                                            if s_name not in wb.sheetnames: continue
                                            ws = wb[s_name]

                                            valid_cols = [c for c in match_cols if c in df.columns]
                                            if len(valid_cols) != len(match_cols): continue
                                            
                                            # Normalize and match
                                            temp_b = df.copy()
                                            norm_keys = []
                                            for c in valid_cols:
                                                norm_n = f"__norm_{c}"
                                                temp_b[norm_n] = temp_b[c].apply(normalize_text)
                                                norm_keys.append(norm_n)
                                            
                                            # Identify rows to DELETE (Duplicates)
                                            # Row must NOT be empty in keys to be a duplicate
                                            temp_b_valid = temp_b.dropna(subset=norm_keys, how='all')
                                            temp_b_valid['__tuple'] = temp_b_valid[norm_keys].apply(tuple, axis=1)
                                            
                                            # Mask: True if it IS in baseline (Duplicate)
                                            duplicates_mask = temp_b_valid['__tuple'].isin(baseline_tuples)
                                            
                                            # Get the __row_idx of these duplicates
                                            rows_to_delete = temp_b_valid.loc[duplicates_mask, '__row_idx'].tolist()
                                            
                                            if rows_to_delete:
                                                file_removed_count += len(rows_to_delete)
                                                # Delete rows in descending order to avoid shifting indices
                                                for r_idx in sorted(rows_to_delete, reverse=True):
                                                    ws.delete_rows(r_idx)
                                        
                                        total_removed += file_removed_count
                                        processed_count += 1
                                        
                                        # Save the modified workbook to the zip
                                        out = io.BytesIO()
                                        wb.save(out)
                                        clean_name = f"Cleaned_{f_name}"
                                        zf.writestr(clean_name, out.getvalue())

                                # 3. METRICS & DOWNLOAD
                                c_m1, c_m2 = st.columns(2)
                                c_m1.metric("Baseline Rows (A)", count_a)
                                c_m2.metric("Duplicate Rows Removed from B", total_removed)
                                
                                if processed_count > 0:
                                    zip_buffer.seek(0)
                                    st.success(f"Successfully processed {processed_count} files.")
                                    
                                    st.download_button(
                                        label="📥 Download Cleaned Files (ZIP)",
                                        data=zip_buffer,
                                        file_name="cleaned_files.zip",
                                        mime="application/zip",
                                        type="primary"
                                    )
            except Exception as e:
                st.error(f" Comparison Error: {e}")


# ================== POWER DIALER ==================
if "Power Dialer" in page:
    st.title("📞 Power Dialer Mode")
    
    leads = fetch_data(LEADS_API)
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
    
    # Main Page Filter (Moved from Sidebar)
    # Use key for state management
    filter_choice = st.radio(
        "🎯 **Filter Leads:**",
        ["Today's Follow-ups", "All Leads"],
        index=0,
        horizontal=True,
        key="pd_filter_choice" 
    )
    st.markdown("---") # Visual separator
    
    # Apply Filter
    if filter_choice == "Today's Follow-ups":
        today_str = datetime.now().strftime("%Y-%m-%d")
        mask_active = ~df["status"].str.contains("Closed", case=False, na=False)
        # Include today AND overdue (past dates)
        mask_due = df["nextFollowUpDate"] <= today_str
        
        # EXCLUDE leads already contacted today
        # Ensure lastFollowUpDate is handled safely
        if "lastFollowUpDate" not in df.columns:
            df["lastFollowUpDate"] = None
        df["lastFollowUpDate"] = df["lastFollowUpDate"].astype(str).replace("None", "").replace("nan", "")
        
        mask_not_contacted_today = df["lastFollowUpDate"] != today_str
        
        filtered_df = df[mask_active & mask_due & mask_not_contacted_today]
        
        if filtered_df.empty:
            # Styled Empty State
            is_dark = st.session_state.get("theme", "light") == "dark"
            bg_col = "#1E1E1E" if is_dark else "#F8F9FA"
            border_col = "#333" if is_dark else "#DDD"
            text_col = "#EEE" if is_dark else "#333"
            
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 40px;
                background-color: {bg_col};
                border: 1px dashed {border_col};
                border-radius: 12px;
                margin: 20px 0;
            ">
                <div style="font-size: 3rem; margin-bottom: 10px;">🎉</div>
                <h2 style="color: {text_col}; font-size: 1.5rem; margin-bottom: 8px;">You're all caught up!</h2>
                <p style="color: #888; margin-bottom: 24px;">No remaining follow-ups scheduled for today.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Centered Button for Action
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                def switch_to_all_leads():
                    st.session_state.pd_filter_choice = "All Leads"
                
                st.button("📂 Browse All Leads", type="primary", use_container_width=True, on_click=switch_to_all_leads)
            st.stop()
        
        df = filtered_df
        # st.success(f"Showing {len(df)} leads due.") # Optional inline success
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
        # --- PREMIUM LEAD DETAILS CARD ---
        
        # 1. Determine Date Status Layout
        f_date = lead.get('nextFollowUpDate')
        today_str = datetime.now().strftime("%Y-%m-%d")
        date_badge_html = ""
        
        if f_date:
            try:
                parsed_date = datetime.strptime(str(f_date), "%Y-%m-%d")
                display_date = parsed_date.strftime("%d/%m/%Y")
            except:
                display_date = f_date
            
            if f_date < today_str:
                date_class = "overdue"
                date_icon = "⚠️"
                date_label = "Overdue"
                date_bg = "#ffebee" if current_theme == "light" else "#b71c1c"
                date_fg = "#c62828" if current_theme == "light" else "#ffcdd2"
            elif f_date == today_str:
                date_class = "due"
                date_icon = "📅"
                date_label = "Due Today"
                date_bg = "#fff3e0" if current_theme == "light" else "#e65100"
                date_fg = "#ef6c00" if current_theme == "light" else "#ffe0b2"
            else:
                date_class = "scheduled"
                date_icon = "🗓️"
                date_label = "Scheduled"
                date_bg = "#e3f2fd" if current_theme == "light" else "#0d47a1"
                date_fg = "#1565c0" if current_theme == "light" else "#bbdefb"
                
            date_badge_html = f"""
<div style="background-color: {date_bg}; color: {date_fg}; padding: 10px 16px; border-radius: 8px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; margin-bottom: 20px; width: 100%;">
    <span>{date_icon}</span>
    <span>{date_label}: {display_date}</span>
</div>
"""
        else:
            date_badge_html = f"""
<div style="background-color: {'#f5f5f5' if current_theme=='light' else '#333'}; color: #888; padding: 10px 16px; border-radius: 8px; font-style: italic; margin-bottom: 20px;">
    No scheduled follow-up
</div>
"""
            
        # 2. Status & Priority Colors
        lead_status = lead.get('status', 'Generated')
        status_style_str = get_status_colors(current_theme).get(lead_status, "")
        if not status_style_str:
             status_style_str = "background-color: #eee; color: #555;" # Default
             
        prio_map = {"HOT": "#FF5252", "WARM": "#FFB74D", "COLD": "#4FC3F7"}
        prio_color = prio_map.get(lead.get('priority', 'WARM'), "#999")
        
        # 3. Construct the HTML Card
        details_card = f"""
<div style="padding: 10px 0;">
{date_badge_html}
<div style="display: flex; flex-direction: column; gap: 16px;">
<div style="display: flex; gap: 10px; align-items: center;">
<div style="flex: 1;">
<span style="font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px;">Status</span>
<div style="margin-top: 4px;">
<span style="{status_style_str}; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.9rem;">
{lead_status}
</span>
</div>
</div>
<div style="flex: 1;">
<span style="font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px;">Priority</span>
<div style="margin-top: 4px; display: flex; align-items: center; gap: 6px;">
<div style="width: 10px; height: 10px; border-radius: 50%; background-color: {prio_color};"></div>
<span style="font-weight: 600; font-size: 0.9rem; color: {text_color}">{lead.get('priority', 'WARM')}</span>
</div>
</div>
</div>
<hr style="border: 0; border-top: 1px solid {'#eee' if current_theme=='light' else '#444'}; margin: 5px 0;" />
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="min-width: 24px; font-size: 1.2rem;">📍</div>
<div>
<div style="font-size: 0.8rem; color: #888;">Address</div>
<div style="color: {text_color}; font-size: 0.95rem; line-height: 1.4;">{lead.get('address', 'N/A')}</div>
</div>
</div>
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="min-width: 24px; font-size: 1.2rem;">📞</div>
<div>
<div style="font-size: 0.8rem; color: #888;">Phone</div>
<code style="font-size: 1rem; color: {text_color}; background: {'#f5f5f5' if current_theme=='light' else '#333'}; padding: 2px 6px; border-radius: 4px;">{lead.get('phone', 'No Phone')}</code>
</div>
</div>
<div style="display: flex; align-items: flex-start; gap: 12px;">
<div style="min-width: 24px; font-size: 1.2rem;">📧</div>
<div>
<div style="font-size: 0.8rem; color: #888;">Email</div>
<div style="color: {text_color}; font-size: 0.95rem;">{lead.get('email', 'N/A')}</div>
</div>
</div>
</div>
</div>
"""
        st.markdown("### 📋 Lead Details")
        st.markdown(details_card, unsafe_allow_html=True)
        
        # Notes
        st.markdown("### 📝 Call Notes")
        notes = st.text_area(
            "Add notes about this call",
            value=lead.get('callNotes') or "",
            height=120,
            key=f"notes_{lead['id']}"
        )
        

    
    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        # Get today's date for lastFollowUpDate
        today_date = datetime.now().strftime("%Y-%m-%d")
        today_date_obj = datetime.now().date()
        
        # --- Pre-calculate Next Date Default for Buttons ---
        default_next = today_date_obj + pd.Timedelta(days=1)
        if lead.get('nextFollowUpDate'):
             try:
                 saved_date = pd.to_datetime(lead.get('nextFollowUpDate')).date()
                 if saved_date >= today_date_obj:
                     default_next = saved_date
             except: pass
             
        # Resolve active date value before rendering widget (using dynamic key logic)
        next_date_key = f"next_action_{lead['id']}"
        active_next_date = st.session_state.get(next_date_key, default_next)
        
        def handle_action_click():
            if filter_choice == "All Leads":
                st.session_state.dialer_index += 1
            # If "Today's Follow-ups", we DO NOT increment because the current item will leave the list,
            # so the *next* item will naturally fall into the current index.
        
        if st.button("✅ Interested", use_container_width=True, type="primary"):
            update_lead(lead['id'], {
                "status": "Interested", 
                "priority": "HOT", 
                "callNotes": notes,
                "lastFollowUpDate": today_date
            })
            handle_action_click()
            st.rerun()
        
        # --- MEETING SET DIALOG ---
        @st.dialog("📅 Schedule Meeting")
        def meeting_dialog():
            st.write(f"Schedule meeting with **{lead.get('businessName')}**")
            c1, c2 = st.columns(2)
            m_date = c1.date_input("Date", value=datetime.now().date() + pd.Timedelta(days=1))
            m_time = c2.time_input("Time", value=datetime.now().time())
            
            if st.button("Confirm Meeting", type="primary", use_container_width=True):
                # Combine Date and Time
                full_meeting_ts = pd.Timestamp(datetime.combine(m_date, m_time))
                
                update_lead(lead['id'], {
                    "status": "Meeting set", 
                    "priority": "HOT", 
                    "callNotes": notes,
                    "lastFollowUpDate": today_date,
                    "meetingDate": str(full_meeting_ts),
                    "nextFollowUpDate": str(m_date) # Also set next follow up to the meeting day
                })
                st.success("Meeting Scheduled!")
                time.sleep(1)
                handle_action_click()
                st.rerun()

        if st.button("📅 Meeting Set", use_container_width=True, type="primary"):
            meeting_dialog()
        
        if st.button("🚫 Not Picking", use_container_width=True):
            update_lead(lead['id'], {
                "status": "Not picking", 
                "callNotes": notes,
                "lastFollowUpDate": today_date,
                "nextFollowUpDate": str(active_next_date) # Auto reschedule
            })
            handle_action_click()
            st.rerun()
        
        if st.button("⏰ Call Later", use_container_width=True):
            update_lead(lead['id'], {
                "status": "Asked to call later", 
                "callNotes": notes,
                "lastFollowUpDate": today_date,
                "nextFollowUpDate": str(active_next_date) # Save manual date
            })
            handle_action_click()
            st.rerun()
        
        if st.button("❌ Not Interested", use_container_width=True):
            update_lead(lead['id'], {
                "status": "Not interested", 
                "callNotes": notes,
                "lastFollowUpDate": today_date
            })
            handle_action_click()
            st.rerun()
        
        st.markdown("---")
        
        # --- Next Action Date Picker (Moved Here) ---
        st.markdown("**📅 Schedule Next Action**")
        
        def on_next_date_change():
            # Get the new date value from session state
            new_val = st.session_state[next_date_key]
            if new_val:
                success = update_lead(lead['id'], {
                    "nextFollowUpDate": str(new_val)
                })
                if success:
                    st.toast(f"📅 Next follow-up updated to: {new_val}")
                else:
                    st.error("Failed to update date.")

        st.date_input(
            "Set Date", 
            value=default_next, 
            min_value=today_date_obj, 
            key=next_date_key, 
            label_visibility="collapsed",
            on_change=on_next_date_change
        )
        
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
            try:
                r = requests.post(LEAD_GEN_API, json={"query": query, "location": loc}, timeout=120)
                if r.status_code == 200:
                    st.success("✅ Leads Generated & Saved to CRM!")
                    st.download_button("Download CSV", r.content, f"{query}.csv", "text/csv")
                else:
                    st.error("backend error")
            except Exception as e:
                st.error(f"Error: {e}")
                
    # History moved to Sidebar

# ================== GOOGLE MAPS SCRAPER ==================
if "Google Maps Scraper" in page:
    st.title("🗺️ Google Maps Scraper")
    st.markdown("Scrape business leads directly from Google Maps using Playwright.")

    with st.container(border=True):
        st.subheader("🔍 Search Parameters")
        c1, c2 = st.columns(2)
        target_business = c1.text_input("Business Type", value="Dentist", placeholder="e.g. Architect, Gym, Dentist")
        target_location = c2.text_input("Location", value="Gotri, Vadodara", placeholder="e.g. New York, Mumbai")
        
        start_scrape = st.button("🚀 Start Scraping", type="primary", use_container_width=True)
    
    # --- SHOW EXISTING SCRAPED RESULTS ---
    output_file = "scraped_results.csv"
    if os.path.exists(output_file) and not start_scrape:
        try:
            df_existing = pd.read_csv(output_file)
            if not df_existing.empty:
                st.markdown("---")
                st.subheader(f"📊 Previous Scrape Results ({len(df_existing)} leads)")
                
                # Reorder and Rename Columns
                col_map = {
                    "clinic_name": "Business Name",
                    "phone_number": "Phone Number",
                    "address": "Address",
                    "website_url": "Website",
                    "email": "Email",
                    "place_url": "Maps Link"
                }
                
                df_existing.rename(columns=col_map, inplace=True)
                desired_order = ["Business Name", "Phone Number", "Address", "Website", "Email", "Maps Link"]
                final_cols = [c for c in desired_order if c in df_existing.columns]
                remaining_cols = [c for c in df_existing.columns if c not in final_cols]
                final_cols.extend(remaining_cols)
                df_display_existing = df_existing[final_cols]
                
                st.dataframe(df_display_existing, use_container_width=True, height=400)
                
                # Download and Import buttons
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    csv_data = df_display_existing.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download CSV",
                        csv_data,
                        "previous_scrape_results.csv",
                        "text/csv",
                        key='download-existing-csv',
                        use_container_width=True
                    )
                
                with col_btn2:
                    if st.button("💾 Import to CRM", use_container_width=True, type="primary"):
                        count = 0
                        prog_bar = st.progress(0, text="Importing leads to CRM...")
                        for idx, row in df_display_existing.iterrows():
                            payload = {
                                "businessName": str(row.get('Business Name') or row.get('clinic_name') or "Unknown"),
                                "phone": str(row.get('Phone Number') or row.get('phone_number') or ""),
                                "address": str(row.get('Address') or row.get('address') or ""),
                                "email": str(row.get('Email') or row.get('email') or ""),
                                "status": "Generated",
                                "priority": "WARM"
                            }
                            # Clean 'nan' strings
                            for key in payload:
                                if payload[key] == 'nan':
                                    payload[key] = ""
                            
                            if create_lead(payload):
                                count += 1
                            prog_bar.progress(min((idx+1)/len(df_display_existing), 1.0))
                        
                        st.success(f"✅ Successfully imported {count} leads to CRM!")
                        time.sleep(1.5)
                        st.rerun()
        except Exception as e:
            st.info(f"Could not load previous results: {e}")

    if start_scrape:
        if not target_business or not target_location:
            st.error("Please provide both Business Type and Location.")
        else:
            search_query = f"{target_business} in {target_location}"
            output_file = "scraped_results.csv"
            
            # Remove previous file if exists
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except: pass
            
            scraper_dir = os.path.join(os.getcwd(), "dental_scraper")
            # Output in root
            cmd = [
                "python3", "-m", "scrapy", "crawl", "dental_spider",
                "-a", f"search_query={search_query}",
                "-O", f"../{output_file}"
            ]
            
            status_container = st.empty()
            status_container.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                border-radius: 16px;
                padding: 24px 32px;
                margin: 20px 0;
                box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: pulse 2s ease-in-out infinite;
            ">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="
                        width: 48px;
                        height: 48px;
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        animation: spin 2s linear infinite;
                    ">
                        🚀
                    </div>
                    <div style="flex: 1;">
                        <div style="
                            color: white;
                            font-size: 18px;
                            font-weight: 700;
                            margin-bottom: 4px;
                        ">
                            Agents Deployed!
                        </div>
                        <div style="
                            color: rgba(255, 255, 255, 0.9);
                            font-size: 14px;
                            font-weight: 500;
                        ">
                            Searching for <strong>'{search_query}'</strong>...
                        </div>
                    </div>
                </div>
            </div>
            <style>
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3); }}
                    50% {{ transform: scale(1.02); box-shadow: 0 12px 48px rgba(59, 130, 246, 0.5); }}
                }}
                @keyframes spin {{
                    from {{ transform: rotate(0deg); }}
                    to {{ transform: rotate(360deg); }}
                }}
            </style>
            """, unsafe_allow_html=True)
            
            import subprocess
            import time
            
            # Clean up old progress file
            progress_file = "scraper_progress.txt"
            if os.path.exists(progress_file):
                try:
                    os.remove(progress_file)
                except:
                    pass
            
            try:
                # Run async with Popen to monitor progress
                process = subprocess.Popen(
                    cmd, 
                    cwd=scraper_dir, 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Monitor progress while scraper runs
                last_progress = ""
                while process.poll() is None:
                    # Check if progress file exists and read it
                    if os.path.exists(progress_file):
                        try:
                            with open(progress_file, "r") as f:
                                progress = f.read().strip()
                                if progress and progress != last_progress:
                                    last_progress = progress
                                    # Parse: "1/13|Dentist in Gotri, Vadodara"
                                    parts = progress.split("|")
                                    if len(parts) == 2:
                                        count_info = parts[0]
                                        current_query = parts[1]
                                        
                                        # Update status with current keyword
                                        status_container.markdown(f"""
                                        <div style="
                                            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                                            border-radius: 16px;
                                            padding: 24px 32px;
                                            margin: 20px 0;
                                            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
                                            border: 1px solid rgba(255, 255, 255, 0.2);
                                            animation: pulse 2s ease-in-out infinite;
                                        ">
                                            <div style="display: flex; align-items: center; gap: 16px;">
                                                <div style="
                                                    width: 48px;
                                                    height: 48px;
                                                    background: rgba(255, 255, 255, 0.2);
                                                    border-radius: 50%;
                                                    display: flex;
                                                    align-items: center;
                                                    justify-content: center;
                                                    font-size: 24px;
                                                    animation: spin 2s linear infinite;
                                                ">
                                                    🚀
                                                </div>
                                                <div style="flex: 1;">
                                                    <div style="
                                                        color: white;
                                                        font-size: 18px;
                                                        font-weight: 700;
                                                        margin-bottom: 4px;
                                                    ">
                                                        Agents Deployed! ({count_info})
                                                    </div>
                                                    <div style="
                                                        color: rgba(255, 255, 255, 0.9);
                                                        font-size: 14px;
                                                        font-weight: 500;
                                                    ">
                                                        Now searching: <strong>'{current_query}'</strong>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <style>
                                            @keyframes pulse {{
                                                0%, 100% {{ transform: scale(1); box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3); }}
                                                50% {{ transform: scale(1.02); box-shadow: 0 12px 48px rgba(59, 130, 246, 0.5); }}
                                            }}
                                            @keyframes spin {{
                                                from {{ transform: rotate(0deg); }}
                                                to {{ transform: rotate(360deg); }}
                                            }}
                                        </style>
                                        """, unsafe_allow_html=True)
                        except:
                            pass
                    
                    time.sleep(0.5)  # Check every 500ms
                
                # Wait for process to complete
                process.wait()
                result = process
                
                if result.returncode == 0:
                    status_container.success("✅ Scraping Complete!")
                    
                    if os.path.exists(output_file):
                        df_res = pd.read_csv(output_file)
                        if not df_res.empty:
                            st.subheader(f"Results ({len(df_res)} found)")
                            
                            # Reorder and Rename Columns for better structure
                            # Expected cols: clinic_name, address, phone_number, website_url, email, place_url
                            
                            # 1. Define Mapping
                            col_map = {
                                "clinic_name": "Business Name",
                                "phone_number": "Phone Number",
                                "address": "Address",
                                "website_url": "Website",
                                "email": "Email",
                                "place_url": "Maps Link"
                            }
                            
                            # 2. Rename existing columns
                            df_res.rename(columns=col_map, inplace=True)
                            
                            # 3. Define Output Order
                            desired_order = ["Business Name", "Phone Number", "Address", "Website", "Email", "Maps Link"]
                            
                            # 4. Filter to only columns that exist (in case scraper missed some)
                            final_cols = [c for c in desired_order if c in df_res.columns]
                            
                            # Add any other random columns found at the end
                            remaining_cols = [c for c in df_res.columns if c not in final_cols]
                            final_cols.extend(remaining_cols)
                            
                            df_display = df_res[final_cols]
                            
                            st.dataframe(df_display, use_container_width=True)
                            
                            # --- SAVE TO HISTORY ---
                            try:
                                # Prepare CSV string
                                csv_for_history = df_display.to_csv(index=False)
                                
                                # Send to Backend
                                requests.post(
                                    EXECUTIONS_API, 
                                    json={
                                        "query": target_business, 
                                        "location": target_location, 
                                        "name": f"{target_business}_{target_location}",
                                        "leadsGenerated": len(df_res),
                                        "status": "Success",
                                        "fileContent": csv_for_history
                                    },
                                    timeout=10
                                )
                                st.toast("✅ Scrape automatically saved to History!", icon="💾")
                            except Exception as h_err:
                                print(f"History Save Error: {h_err}")

                            csv = df_display.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "📥 Download CSV",
                                csv,
                                "leads.csv",
                                "text/csv",
                                key='download-csv',
                                type="primary"
                            )
                            
                            # Option to Import to CRM
                            if st.button("💾 Add to CRM"):
                                count = 0
                                prog_bar = st.progress(0)
                                for idx, row in df_display.iterrows():
                                    payload = {
                                        # Map scraped columns to CRM columns
                                        "businessName": str(row.get('clinic_name') or row.get('name') or row.get('Business Name') or target_business),
                                        "phone": str(row.get('phone_number') or row.get('Phone') or row.get('Phone Number') or ""),
                                        "address": str(row.get('address') or row.get('Address') or ""),
                                        "email": str(row.get('email') or row.get('Email') or ""),
                                        "status": "Generated",
                                        "priority": "WARM"
                                    }
                                    if create_lead(payload):
                                        count += 1
                                    prog_bar.progress(min((idx+1)/len(df_res), 1.0))
                                st.success(f"Added {count} leads to CRM!")
                                time.sleep(1)
                                st.rerun()

                        else:
                            st.warning("No data found. Try a broader location or clearer business type.")
                    else:
                        st.error("Output file not generated.")
                else:
                    st.error("Scraper failed.")
                    with st.expander("Show Error Logs"):
                        st.code(result.stderr)
                        
            except Exception as e:
                st.error(f"Execution Error: {e}")

# ================== LEAD GEN HISTORY ==================
if "Lead Gen History" in page:
    st.title("📜 Lead Generation History")

    # --- IMPORT LAST SCRAPE ---
    if os.path.exists("scraped_results.csv"):
        with st.expander("📥 Import Last Local Scrape", expanded=False):
            st.caption("Found 'scraped_results.csv' on disk.")
            
            # Helper to guess basic defaults
            def_q = "Dentist"
            def_l = "Location"
            
            c1, c2 = st.columns(2)
            i_query = c1.text_input("Query Used", def_q, key="imp_q")
            i_loc = c2.text_input("Location Used", def_l, key="imp_l")
            
            # Dynamic default name
            def_name = f"{i_query}_{i_loc}"
            i_name = st.text_input("File Name", value=def_name, key="imp_n")
            
            if st.button("Save to History", type="secondary", key="btn_imp_save"):
                 try:
                     df_last = pd.read_csv("scraped_results.csv")
                     csv_str = df_last.to_csv(index=False)
                     
                     requests.post(EXECUTIONS_API, json={
                         "query": i_query,
                         "location": i_loc,
                         "name": i_name,
                         "leadsGenerated": len(df_last),
                         "status": "Success",
                         "fileContent": csv_str
                     })
                     st.toast("✅ Imported!")
                     time.sleep(1)
                     st.rerun()
                 except Exception as e:
                     st.error(f"Import failed: {e}")
    
    # 1. Fetch Summary List
    executions = fetch_data(EXECUTIONS_API)
    
    if not executions:
        st.info("No history found.")
    else:
        # Convert to DataFrame
        df_hist = pd.DataFrame(executions)
        
        # Display Config
        st.markdown("### 🗂 Past Scrapes")
        
        # Prepare DF for Editor
        disp_cols = ["id", "name", "date", "query", "location", "leadsGenerated", "status"]
        
        # Ensure columns exist safely
        for col in disp_cols:
             if col not in df_hist.columns:
                 df_hist[col] = None

        # Fallback Name if empty
        df_hist["name"] = df_hist.apply(lambda x: x["name"] if (x["name"] and str(x["name"]) != "nan") else f"{x['query']} - {x['location']}", axis=1)

        # Date formatting
        try:
            df_hist["date"] = pd.to_datetime(df_hist["date"]).dt.strftime("%Y-%m-%d %H:%M")
        except: pass
        
        # Configure Grid with Selection
        event = st.dataframe(
            df_hist[disp_cols],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # CHECK SELECTION
        if len(event.selection.rows) > 0:
            selected_idx = event.selection.rows[0]
            # Get ID from the displayed dataframe's index mapping
            selected_row = df_hist.iloc[selected_idx]
            exec_id = selected_row["id"]
            
            st.divider()
            st.markdown(f"### 📂 File: {selected_row['name']}")
            
            # Fetch Full Data (including Content)
            try:
                r_det = requests.get(f"{EXECUTIONS_API}/{exec_id}")
                if r_det.status_code == 200:
                    details = r_det.json()
                    file_content = details.get("fileContent", "")
                    
                    # RENAME UI
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        current_name = details.get("name") or selected_row['name']
                        new_name = c1.text_input("Rename File", value=current_name, key=f"ren_{exec_id}")
                        if c2.button("💾 Update Name", key=f"btn_ren_{exec_id}", use_container_width=True):
                            requests.put(f"{EXECUTIONS_API}/{exec_id}", json={"name": new_name})
                            st.success("✅ Name Updated!")
                            time.sleep(1)
                            st.rerun()

                    # SHOW DATA
                    if file_content:
                        import io
                        try:
                            # Try parsing CSV
                            df_data = pd.read_csv(io.StringIO(file_content))
                            st.write(f"**Rows Found:** {len(df_data)}")
                            st.dataframe(df_data, use_container_width=True)
                            
                            # Download Button
                            st.download_button(
                                "📥 Download CSV",
                                file_content,
                                f"{new_name}.csv",
                                "text/csv",
                                key=f"dl_{exec_id}"
                            )
                        except Exception as parse_err:
                            st.error("Error parsing content.")
                            st.text_area("Raw Content", file_content, height=200)
                    else:
                        st.warning("⚠️ No file content stored for this run.")
                        
                else:
                    st.error("Failed to load details from server.")
            except Exception as e:
                st.error(f"Error fetching details: {e}")
 
 