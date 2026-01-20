import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
from datetime import datetime
import subprocess
import sys
import os
import socket
import platform
import json
import streamlit.components.v1 as components
from components.sidebar import render_sidebar_toggle

# --- PLAYWRIGHT SETUP FOR CLOUD ---
# Ensure browsers are installed (essential for Streamlit Cloud)
if not os.path.exists(".browser_installed"):
    try:
        print("🔧 Installing Playwright Browsers (First Run)...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        with open(".browser_installed", "w") as f: 
            f.write("done")
        print("✅ Playwright Browsers Installed.")
    except Exception as e:
        print(f"⚠️ Failed to install browsers: {e}")

# ================== BACKEND AUTO-START ==================
@st.cache_resource
def start_backend_server():
    """
    Checks if the backend is running on port 3000.
    If not, starts 'node server.js' as a background process.
    """
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    if not is_port_in_use(3000):
        # Start server
        print("🚀 Starting Backend & Dependencies...")
        
        # 1. Install Node modules if missing
        if not os.path.exists("node_modules"):
            print("📦 Installing Node modules...")
            try:
                subprocess.run(["npm", "install"], check=True)
                print("✅ Node dependencies installed.")
            except Exception as e:
                print(f"❌ npm install failed: {e}")

        # 2. Install Playwright Browsers (CRITICAL for Scraper)
        # We check a flag or just run it (it's fast if already installed)
        print("🎭 Ensuring Playwright browsers...")
        try:
             subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
             print("✅ Playwright chromium installed.")
        except Exception as e:
             print(f"⚠️ Playwright install warning: {e}")

        # 3. Start Server
        try:
            # Run node server.js in background
            subprocess.Popen(
                ["node", "server.js"], 
                cwd=os.getcwd(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(5)  # Give it 5 seconds to boot
            print("✅ Backend launch command sent.")
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
    else:
        print("✅ Backend already running.")

# Initialize Backend
start_backend_server()

# ================== CONFIG ==================
BACKEND_BASE = os.getenv("BACKEND_URL", "http://localhost:3000")
EXECUTIONS_API = f"{BACKEND_BASE}/executions"
LEADS_API = f"{BACKEND_BASE}/leads"
STATS_API = f"{BACKEND_BASE}/stats"
LEAD_GEN_API = f"{BACKEND_BASE}/lead-gen"

# Detect Environment
IS_LIVE_ENV = platform.system() == "Linux"

st.set_page_config(
    page_title="n8n CRM & Sales Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render the collapsible sidebar toggle (Must be called early)
render_sidebar_toggle()

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

/* Hide Markdown Header Anchors (Chain Icon) */
/* Hide Markdown Header Anchors (Chain Icon) */
.stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
.stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a {
    display: none !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
a.anchor-link, a[class*="anchor"] {
    display: none !important;
}
/* Aggressive hiding for the SVG icon specifically */
h1 a svg, h2 a svg, h3 a svg {
    display: none !important;
}

/* Sidebar Width Fix - COMMENTED OUT TO ALLOW COLLAPSE */
/*
section[data-testid="stSidebar"] {
    min-width: 250px !important;
    max-width: 300px !important;
}
*/

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

/* --- MOBILE RESPONSIVE OPTIMIZATIONS --- */
@media only screen and (max-width: 768px) {
    /* Maximize horizontal space */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 3rem !important;
    }

    /* Stack flex containers vertically if needed */
    .row-widget.stHorizontal {
        flex-direction: column !important;
    }
    
    /* Ensure cards take full width */
    .metric-card, .meeting-card {
        width: 100% !important;
        margin-bottom: 12px !important;
    }
    
    /* Adjust Font Sizes */
    h1 { font-size: 1.75rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.25rem !important; }
    
    /* Improve Grid Scroll */
    div[data-testid="stDataEditor"] {
        width: 100% !important;
        overflow-x: auto !important;
        display: block !important;
    }
    
    /* Make buttons larger for touch */
    div.stButton > button {
        width: 100% !important;
        min-height: 48px !important;
        margin-bottom: 8px !important;
    }
    
    /* Hide decorative status bar on mobile to save space */
    footer { display: none !important; }
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

/* Meeting Card Styles - FIXED */
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
    cursor: pointer; /* Clickable indication */
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
    min-width: 0; /* CRITICAL for text-overflow to work in flex */
}
.mc-title { 
    color: #1a202c !important; 
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 4px;
    white-space: nowrap; /* Force single line */
    text-overflow: ellipsis;
    line-height: 1.2;
}
.mc-company { 
    color: #64748b !important;
    font-size: 0.85rem;
    margin-bottom: 0; /* Remove bottom margin since button is gone */
    white-space: nowrap;
    text-overflow: ellipsis;
    line-height: 1.3;
}
/* Removed .mc-action as button is gone */
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


/* --- Font Awesome for Sidebar Icons --- */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css');

/* Base Sidebar Icon Style */
section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
    font-family: "Font Awesome 6 Free"; 
    font-weight: 900; 
    -moz-osx-font-smoothing: grayscale; 
    -webkit-font-smoothing: antialiased; 
    display: inline-block; 
    font-style: normal; 
    font-variant: normal; 
    text-rendering: auto; 
    line-height: 1; 
    width: 24px; 
    text-align: center; 
    margin-right: 12px; 
    font-size: 1.1rem;
    color: inherit; /* Inherit color from label (grey or blue) */
}

/* 1. Dashboard */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1)::before {
    content: "" !important;
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAAAXNSR0IArs4c6QAAIABJREFUeF7t3Qe8bVV17/FfVBQBewG72ABjiTWaZyyIYq+xYBRjzYtgQ7GbWN6zBLtiieVZYtdYsCtYYiyQWBNAsVewI8UCyltD1zlcrufec/bZc+49x5q//fmcz4uPvcca8zvW3ed/1tp7rT9jOY8rA1cH9gT2AHYHLgzsAuw8/iynM7eqwB8Ffg6cMv4cD3x1/DkGOBL4sVBNCVwE+MvxPeVK4/vKrlu8n1ygqW5tpkeBlfeTk4GfAN8AvjL+fBE4etEof7agDV4IuAOw9/iz24K262YUqCFwBvBl4Ajgg8BHgNNrbMia2xTYAdgH2Hd8T7kKsKj3M8eiQA2BHwIfHd9X3gH8rMZGtqxZ8x/MOYFbDyln/+EvplsB8b99KDBFgROGvzjfCLwW+PwUF9jQmq45vqfsB1y0ob5sRYGSAr8F3jccHX/N+P/G/y7+qBEAzgXcG3gicMniHVtQgbYF/gN4JnBY222m6+4GwKOB26Tr3IYVmE8g/sB4LvBC4NT5Sp311SUDQPyF/9DhnOnBQJyP86FAzwLxOYHHjofzenaYd+1xmP/pwLXnLeTrFUgu8KPxj4sIAqeVWEupAHCj4Zf+ocCfl2jKGgpMSOA9wIOA705oTYtYysXGN7t7LWJjbkOBRALxgeQDgQ/P2/O8AeA8w6f3XzSek5u3F1+vwFQFfgkcBLxyqgssvK4HDt8IehYQ7y8+FFDgTwXig8ivHj4o+BAgvlWwqcc8ASC+yvcW/+rflLsv6lPg7cORgPsBJ/a5/HVXHb/wXzp83fIe6z7TJyigQAjE1wjvBsTXCGd+bDYA3Gf4BO6LgR1n3qIvUKBvgfgHe/vxH27fEmdd/V7Au4AriqKAAjMJ/Ar43+O3kGZ64WYCQHwSNz6Us5nXztScT1ZgogLx/d7bAp+a6PpmXdZ1gPf64eFZ2Xy+AqsCcUrgKcP/etIsJrP8Ej/b+FWEOOfgQwEF5hOI83Z/M15IaL5KuV99y+E04lu9+mfuIdp9MwLPGz9vFIFg3ccsAeA5w7nLh69b0ScooMBGBeLiHvG99rk/zbvRDTb2vJsMl+99/3BEMa4d4kMBBcoIxOn5AzZSaqMB4PHA/9lIQZ+jgAIzCcQ3BOIX4edmelX+J19tWPfHgfPnX4orUKA5gceMX6PdbmMbCQDxgb/4+tJGntucgg0pkEAgbjZ0PeDbCXot0WLc/OszXsq3BKU1FFhTIE4BxBV5X7c9n/V+qV8V+OyQJM4tsgIKVBU4aripUFzutso1v6t2PlvxuInPJ8bAM9srfbYCCswi8OvhM0bXH27E94VtvWh7ASBuzRtvSnHLXh8KKFBfID5n84j6m1nqFl4APHipHbhxBfoROG64L8m1hveVk9Za8vYCQNyFKO7k50MBBRYjEIft4g6a8cG4KT7iq4/xXf/1jjxOce2uSYFlCbxqvADZn2x/W/8Qbwh8zH+oy5qX2+1Y4DvDFTbjKpunTMxgJ+B/hsuXXnZi63I5CrQuEH9Y7D3+Tj9Lr2sFgLirX5wziCtz+VBAgcULPBX4x8VvtuoW4+Jh8clkHwoosHiBCN/X2PougmsFgEcOF+U4ZPH9uUUFFBgFfjPeY+PrExG5EvBlIP648KGAAssRiOv4xIWCVh9bB4A4TPdNv56znOm4VQW2EHgF8ICJiMRdy+IrST4UUGB5AicA8RXcuHfAHx5bB4CHjZf7XV6LblkBBULgtPHGONmvDXBpID6J7F//7tcKLF8gvoHzorUCQPwDjUOOl1x+j3aggALjP9TsX5k7FHiQ01RAgSYEvgtcYeV6I1seAbgTEPcr96GAAm0IxGWCLwac2kY7M3cRpxTjKofnmfmVvkABBWoJ3GH8Ou5ZTgG8Y/j0f/wHHwoo0I7AfsPFuN7UTjszdfK3w18b/zrTK3yyAgrUFog/9ONOpKsB4ILAD7wrV2136ysws8D7xosDzfzCBl7wAWDfBvqwBQUUOFMgLjd+8eGKnD9dOQVwv+Hcf3zq2IcCCrQlcDpwEeAXbbW1bjfxR8WPgLOv+0yfoIACixaIm/y9eiUAvAGIQ40+FFCgPYHbA+9ur63tduRnipINzHa7Eoi7BO4fASB+4vD/bl0t38UqkEfg+cMRgPiKbqbHC4EDMzVsrwp0JBC/8y8Rv/zjuuNxmUAfCijQpkBcRe9qbba2za7+e7yaYbK2bVeBbgT2igBwj+GCI6/vZskuVIF8Ar8bLs+9MxCXCM7wONd4MyPP/2eYlj32KnD3CABPnuCNR3odqOuerkAcqTsmyfKuMl77P0m7tqlAlwL/FAEgvmN8ty6X76IVyCNwR+CdSdq9M/C2JL3apgK9CrwhAsBRwLV7FXDdCiQReFSiu3Q+GnhGElfbVKBXgaMiAHwNuHyvAq5bgSQCTxtuEPT4JL0+HXhMkl5tU4FeBY6LABC3CLxorwKuW4EkAvG1uock6TXuNnZAkl5tU4FeBY6PAHAKEDft8KGAAu0KvBqIq3dleESv987QqD0q0LHAKREAfr/FPQE6tnDpCjQt8Fbgrk13eGZzbxmuLXKXJL3apgK9CpwRAeCMXlfvuhVIJGAASDQsW1Ugg4ABIMOU7FEBMAC4FyigQFEBA0BRTospUE3AAFCN1sIK9ClgAOhz7q46n4ABIN/M7FiBpgUMAE2Px+YUWBUwALgzKKBAUQEDQFFOiylQTcAAUI3Wwgr0KWAA6HPurjqfgAEg38zsWIGmBQwATY/H5hTwFID7gAIK1BEwANRxtaoCpQU8AlBa1HoKdC5gAOh8B3D5aQQMAGlGZaMK5BAwAOSYk10qYABwH1BAgaICBoCinBZToJqAAaAarYUV6FPAANDn3F11PgEDQL6Z2bECTQsYAJoej80psCpgAHBnUECBogIGgKKcFlOgmoABoBqthRXoU8AA0OfcXXU+AQNAvpnZsQJNCxgAmh6PzSngKQD3AQUUqCNgAKjjalUFSgt4BKC0qPUU6FzAAND5DuDy0wgYANKMykYVyCFgAMgxJ7tUwADgPqCAAkUFDABFOS2mQDUBA0A1Wgsr0KeAAaDPubvqfAIGgHwzs2MFmhYwADQ9HptTYFXAAODOoIACRQUMAEU5LaZANQEDQDVaCyvQp4ABoM+5u+p8AgaAfDOzYwWaFjAAND0em1PAUwDuAwooUEfAAFDH1aoKlBbwCEBpUesp0LmAAaDzHcDlpxEwAKQZlY0qkEPAAJBjTnapgAHAfUABBYoKGACKclpMgWoCBoBqtBZWoE8BA0Cfc3fV+QQMAPlmZscKNC1gAGh6PDanwKqAAcCdQQEFigoYAIpyWkyBagIGgGq0FlagTwEDQJ9zd9X5BAwA+WZmxwo0LWAAaHo8NqeApwDcBxRQoI6AAaCOq1UVKC3gEYDSotZToHMBA0DnO4DLTyNgAEgzKhtVIIeAASDHnOxSAQOA+4ACChQVMAAU5bSYAtUEDADVaC2sQJ8CBoA+5+6q8wkYAPLNzI4VaFrAAND0eGxOgVUBA4A7gwIKFBUwABTltJgC1QQMANVoLaxAnwIGgD7n7qrzCRgA8s3MjhVoWsAA0PR4bE4BTwG4DyigQB0BA0AdV6sqUFrAIwClRa2nQOcCBoDOdwCXn0bAAJBmVDaqQA4BA0COOdmlAgYA9wEFFCgqYAAoymkxBaoJGACq0VpYgT4FDAB9zt1V5xMwAOSbmR0r0LSAAaDp8dicAqsCBgB3BgUUKCpgACjKaTEFqgkYAKrRWliBPgUMAH3O3VXnEzAA5JuZHSvQtIABoOnx2JwCngJwH1BAgToCBoA6rlZVoLSARwBKi1pPgc4FDACd7wAuP42AASDNqGxUgRwCBoAcc7JLBQwA7gMKKFBUwABQlNNiClQTMABUo7WwAn0KGAD6nLurzidgAMg3MztWoGkBA0DT47E5BVYFDADuDAooUFTAAFCU02IKVBMwAFSjtbACfQoYAPqcu6vOJ2AAyDczO1agaQEDQNPjsTkFPAXgPqCAAnUEDAB1XK2qQGkBjwCUFrWeAp0LGAA63wFcfhoBA0CaUdmoAjkEDAA55mSXChgA3AcUUKCogAGgKKfFFKgmYACoRmthBfoUMAD0OXdXnU/AAJBvZnasQNMCBoCmx2NzCqwKGADcGRRQoKiAAaAop8UUqCZgAKhGa2EF+hQwAPQ5d1edT8AAkG9mdqxA0wIGgKbHY3MKeArAfUABBeoIGADquFpVgdICHgEoLWo9BToXMAB0vgO4/DQCBoA0o7JRBXIIGAByzMkuFTAAuA8ooEBRAQNAUU6LKVBNwABQjdbCCvQpYADoc+6uOp+AASDfzOxYgaYFDABNj8fmFFgVMAC4MyigQFEBA0BRTospUE3AAFCN1sIK9ClgAOhz7q46n4ABIN/M7FiBpgUMAE2Px+YU8BSA+4ACCtQRMADUcbWqAqUFPAJQWtR6CnQuYADofAdw+WkEDABpRmWjCuQQMADkmJNdKmAAcB9QQIGiAgaAopwWU6CagAGgGq2FFehTwADQ59xddT4BA0C+mdmxAk0LGACaHo/NKbAqYABwZ1BAgaICBoCinBZToJqAAaAarYUV6FPAANDn3F11PgEDQL6Z2bECTQsYAJoej80p4CkA9wEFFKgjYACo42pVBUoLeASgtKj1FOhcwADQ+Q7g8tMIGADSjMpGFcghYADIMSe7VMAA4D6ggAJFBQwARTktpkA1AQNANVoLK9CngAGgz7m76nwCBoB8M7NjBZoWMAA0PR6bU2BVwADgzqCAAkUFIgCcDpy9aFWLKaBAaYE3AfuVLlqp3luAu1SqbVkFFCgkEAHgROC8hepZRgEF6gi8AnhAndLFqxoAipNaUIHyAhEAvgdconxpKyqgQEGB5wCPKFivZikDQE1daytQSCACwLHAHoXqWUYBBeoIPHko+6Q6pYtXNQAUJ7WgAuUFIgB8HLhh+dJWVECBggIHAC8uWK9mKQNATV1rK1BIIALAy4fTAPcvVM8yCihQR2Af4PA6pYtXNQAUJ7WgAuUFIgA8EjikfGkrKqBAQYFLjZ/XKViyWikDQDVaCytQTiACwG2Aw8qVtJICChQWOHn8ps4ZhevWKmcAqCVrXQUKCkQAuBDwI+BsBetaSgEFygl8BLhZuXLVKxkAqhO7AQXmF4gAEI8vAlebv5wVFFCggsDjgKdXqFurpAGglqx1FSgosBIAngs8rGBdSymgQDmB6wGfLVeueiUDQHViN6DA/AIrAeAWwPvnL2cFBRQoLPBTYLfxkt2FS1crZwCoRmthBcoJrASAcwDfHd9oylW3kgIKzCtwKHDgvEUW/HoDwILB3ZwCmxFYCQDxWk8DbEbQ1yhQVyDb4f/QMADU3SesrkARgS0DwDWAzxWpahEFFCgh8NWkl+k2AJSYvjUUqCywZQCITX0MuFHlbVpeAQU2JvAg4CUbe2pTzzIANDUOm1FgbYGtA0B81/hDYimgwNIFjgcuB/xq6Z3M3oABYHYzX6HAwgW2DgDRwKeA6y+8EzeogAJbChw0fi4no4oBIOPU7Lk7gbUCwN6JbjrS3cBccBcC3wT+POlf/zEgA0AXu6mLzC6wVgCINb0B2C/74uxfgaQCt0t+fw4DQNIdz7b7EthWAIgLjxw7HII8X18crlaBpQu8G7j90ruYrwEDwHx+vlqBhQhsKwDExu8HvGIhXbgRBRQIgbjqX3wdNy7KlflhAMg8PXvvRmB7ASAQXgvcqxsNF6rA8gTiVr93HALAu5bXQrEtGwCKUVpIgXoC6wWAnYGjgL3qtWBlBRQADgEeNREJA8BEBukypi2wXgCI1e8BfBK48LQpXJ0CSxN4H3AH4LSldVB2wwaAsp5WU6CKwEYCQGz4OsARwC5VurCoAv0KHAncFDh5QgQGgAkN06VMV2CjASAE9h3PT55ruhyuTIGFChw9BOsbjh/+W+iGK2/MAFAZ2PIKlBCYJQDE9m4MvNOvB5agt0bnAvHZmlsDP56ggwFggkN1SdMTmDUAhMBVgA8Al5gehytSYCECHwHuBJy0kK0tfiMGgMWbu0UFZhbYTACIjVxm+GbAm4G/nHmLvkCBfgXiq37PBh4LnD5hBgPAhIfr0qYjsNkAEALnGN7EngA8ETjbdEhciQJVBE4cL6719irV2ypqAGhrHnajwJoC8wSAlYK3BA4FdtdYAQXWFIjL+x44gSv8bXS8BoCNSvk8BZYoUCIARPvnHu5c9ujxZ8clrsdNK9CSwPeAuK3vW1tqagG9GAAWgOwmFJhXoFQAWOnjcsDjxssHn3Pe5ny9AkkFfjBcM+NZwEsT39J3HnoDwDx6vlaBBQmUDgArbV8aOBjYHzjvgtbiZhRYtsBXgecBrxo+6PebZTezxO0bAJaI76YV2KhArQCwsv04HXCz8YhAXOp0h4025vMUSCLwC+Cw8cZZhwPxSf/eHwaA3vcA159CoHYA2BLhfMCNxsue7g3sOX6TIAWUTSowCsQlez87Xho7Lo/9nxP/St9mBm8A2Iyar1FgwQKLDABbLy0+I3CF8WZD8dmBuNlQ3GsgfuIuhD4UWKbAz8fr88cv/BOArwBxiP+7y2wqybYNAEkGZZt9CywzAPQt7+oVmK6AAWC6s3VlExIwAExomC5FgUYEDACNDMI2FNiegAHA/UMBBUoLGABKi1pPgQoCBoAKqJZUoHMBA0DnO4DLzyFgAMgxJ7tUIJOAASDTtOy1WwEDQLejd+EKVBMwAFSjtbAC5QQMAOUsraSAAn8UMAC4JyiQQMAAkGBItqhAMgEDQLKB2W6fAgaAPufuqhWoKWAAqKlrbQUKCRgACkFaRgEFVgUMAO4MCiQQMAAkGJItKpBMwACQbGC226eAAaDPubtqBWoKGABq6lpbgUICBoBCkJZRQAFPAbgPKJBJwACQaVr2qkAOAY8A5JiTXXYuYADofAdw+QpUEDAAVEC1pAKlBQwApUWtp4ACBgD3AQUSCBgAEgzJFhVIJmAASDYw2+1TwADQ59xdtQI1BQwANXWtrUAhAQNAIUjLKKDAqoABwJ1BgQQCBoAEQ7JFBZIJGACSDcx2+xQwAPQ5d1etQE0BA0BNXWsrUEjAAFAI0jIKKOApAPcBBTIJGAAyTcteFcgh4BGAHHOyy84FDACd7wAuX4EKAgaACqiWVKC0gAGgtKj1FFDAAOA+oEACAQNAgiHZogLJBAwAyQZmu30KGAD6nLurVqCmgAGgpq61FSgkYAAoBGkZBRRYFTAAuDMokEDAAJBgSLaoQDIBA0CygdlunwIGgD7n7qoVqClgAKipa20FCgkYAApBWkYBBTwF4D6gQCYBA0CmadmrAjkEPAKQY0522bmAAaDzHcDlK1BBwABQAdWSCpQWMACUFrWeAgoYANwHFEggYABIMCRbVCCZgAEg2cBst08BA0Cfc3fVCtQUMADU1LW2AoUEDACFIC2jgAKrAgYAdwYFEggYABIMyRYVSCZgAEg2MNvtU8AA0OfcXbUCNQUMADV1ra1AIQEDQCFIyyiggKcA3AcUyCRgAMg0LXtVIIeARwByzMkuOxcwAHS+A7h8BSoIGAAqoFpSgdICywwA5wKuCOwBXA64ELALsPP4U3qt1lNgFoFfAKeMP8cDXwG+CnwHOGOWQh0+1wDQ4dBdcj6BRQaACwI3AvYef+IX/9nzkdlx5wKnAp8Fjhh/jgRO79xk6+UbANwhFEggUDsA7AjcFtgfuAVwjgQmtqjALAJxpOCw4SjWa4HDPTrwBzoDwCx7kM9VYEkCtQLAZYdDpwcD9wLOs6S1uVkFFi3wNeB5wCuBXy964w1tzwDQ0DBsRYFtCZQOAFcCHgv8LbCD7Ap0KhCfGXg28JLxMwS9MRgAepu4600pUCoA7AQ8avir5zFAfLjPhwIKwPeBx42nB3ryMAD0NG3XmlagRACIc/wvAi6dVsHGFagr8D7gQcC3626mmeoGgGZGYSMKbFtgngAQh/ifOv7lP08d56NADwK/BO4PvLWDxRoAOhiyS8wvsNlf3LuPn/S9dn4CV6DAwgTi+gHPH0PzaQvb6uI3ZABYvLlbVGBmgc0EgGsBcUjzojNvzRcooEAIxNcF7wicNFEOA8BEB+uypiUwawC4CfBO4LzTYnA1Cixc4D+BWwE/XviW62/QAFDf2C0oMLfALAHglsA7/JT/3OYWUGBF4JjhaoI3BH4yMRIDwMQG6nKmKbDRAHDd8bBlXKvfhwIKlBM4arw09snlSi69kgFg6SOwAQXWF9hIANgL+PfxZj3rV/QZCigwq8AHx0tmT+WDgQaAWfcAn6/AEgTWCwDxF3/8hbLnEnpzkwr0JPCc4UOBj5jIgg0AExmky5i2wHoB4HXAPadN4OoUaEIgviJ45/FzNk00NEcTBoA58HypAosS2F4AeCDwskU14nYUUICfA9eYwBUDDQDuzAokENhWANgNOBY4X4I12KICUxL4ABDfuMn8MABknp69dyOwrQDwZuCu3Si4UAXaErjDcCTgXW21NFM3BoCZuHyyAssRWCsA7AN8eDntuFUFFBhPAVx5uGTwqUk1DABJB2fbfQmsFQCOBK7TF4OrVaA5gUcCz26uq401ZADYmJPPUmCpAlsHgH2BOAfpQwEFlitwPHA54FfLbWNTWzcAbIrNFymwWIGtA8Anhiv+/fViW3BrCiiwDYEDhptuvTihjgEg4dBsuT+BLQPANYerkf1XfwSuWIFmBY4D9gDiGgGZHgaATNOy124FtgwAzwMe2q2EC1egTYG/Aj7dZmvb7MoAkGxgttunwEoAOAfwPWDXPhlctQLNCrwEeFCz3a3dmAEg2cBst0+BlQAQ9yV/b58ErlqBpgV+Ngbz05vu8qzNGQASDctW+xVYCQAe/u93H3Dl7QtcH/hM+22udmgASDQsW+1XYCUAfAm4ar8MrlyBpgUeDzyt6Q49ApBoPLaqwB8FIgBcFIjvHK93Z0DNFFBgOQKHA3GFziwPjwBkmZR9di0Qv/RvAxzWtYKLV6BtgZOB8yb6OqABoO39ye4UWD0CEJccPUQPBRRoWuBS4zd1mm5ybM4AkGFK9ti9QBwBePnwxnL/7iUEUKBtgTgFEKcCMjwMABmmZI/dC0QA+Dhww+4lBFCgbYEDgUPbbnG1OwNAkkHZZt8CEQCOHS832reEq1egbYEnD+09qe0WDQBJ5mObCvxBIALA94GL66GAAk0LPBc4qOkOz2zOIwBJBmWbfQtEADhx/IRx3xKuXoG2BV4xhPUHtN2iRwCSzMc2FVg9AhCXGD27Hgoo0LTAm4D9mu7QIwBJxmObCvxRII4AZLvVqLNToEeBtwJ3TbJwTwEkGZRt9i1gAOh7/q4+j4ABIM+s7FSBFAIGgBRjskkFMAC4EyigQFEBA0BRTospUE3AAFCN1sIK9ClgAOhz7q46n4ABIN/M7FiBpgUMAE2Px+YUWBUwALgzKKBAUQEDQFFOiylQTcAAUI3Wwgr0KWAA6HPurjqfgAEg38zsWIGmBQwATY/H5hTwFID7gAIK1BEwANRxtaoCpQU8AlBa1HoKdC5gAOh8B3D5aQQyBYC4bPHd0sjaqAJ9CvzOANDn4F11PoFMASBuXHS/fMR2rEBXAicaALqat4tNLJApAMStix+W2NrWFehB4LsGgB7G7BqnIJApADwVeMIU0F2DAhMWONoAMOHpurRJCWQKAAcCL5yUvotRYHoCHzMATG+ormiaApkCwM2BD05zDK5KgckIvMwAMJlZupCJC2QKAJcBvjXxebg8BbILHGQAyD5C++9FIFMAOBtwErBTL8NxnQokFLi1ASDh1Gy5S4FMASAGdARwky4n5aIVaF/g98CuBoD2B2WHCoRAtgDwROApjk4BBZoU+DxwTQNAk7OxKQX+RCBbAPhfwCedowIKNCnwLOBgA0CTs7EpBdIHgB2AE4ALOEsFFGhOIL6p82EDQHNzsSEF1hTIdgQgFvFS4O+dpwIKNCUQwfySw8W6TjcANDUXm1FgmwIZA4CnAdyhFWhP4NnAI6MtA0B7w7EjBdYSyBgA4v3lq8AVHKkCCjQj8BfAFw0AzczDRhRYVyBjAIhFeVngdUfrExRYmEB8PfemK1vzCMDC3N2QAnMJZA0AOwJfBy4+1+p9sQIKlBCIX/4RAv7wMACUILWGAvUFsgaAkDl4uCrgP9cncgsKKLAdgc8M9+i4/pb/3QDg/qJADoHMAWBn4Gjg0jmo7VKByQmcAdwY+IQBYHKzdUEdCGQOADGeOwL/1sGcXKICLQq8Frj31o15BKDFUdmTAn8qkD0AxIreA9za4SqgwEIFfgnsOVyT44cGgIW6uzEFiglMIQDEbYLjGuReHbDYbmEhBdYV+DvgNWs9yyMA69r5BAWaEJhCAAjI2ww3IXn3+AHkJmBtQoEJC7xxuBbHPba1PgPAhCfv0iYlMJUAEEN5LvCwSU3HxSjQnkBchOvawEkGgPaGY0cKzCIwpQAQNwo6DNh3FgCfq4ACGxb4EXAD4LjtvcIjABv29IkKLFVgSgEgIHeKu5EBf7VUVTeuwPQETh1uxb3PELA/vd7SDADrCfnfFWhDYGoBIFQvPH4vea82iO1CgfQCvwZuN4brdRdjAFiXyCco0ITAFANAwF5wPB3gkYAmdjObSCxwMnCnjf7yj3UaABJP29a7EphqAIghxpUCY3237GqiLlaBcgLHj/9+vjBLSQPALFo+V4HlCUw5AIRqfDDwmeO3A+J9yYcCCmxMIM713x34zsaefuazDACzivl8BZYjMPUAsKJ6W+DV46mB5Ui7VQVyCMT1/V843mzrt5tp2QCwGTVfo8DiBXoJACEbVww81MsGL34nc4tpBOIW2wcMd/f74DwdGwDm0fO1CixOoKcAsOXRgBcMRwQuuzhmt6RA0wKnAS8BHjf85X/KvJ0aAOYV9PUKLEagxwAQsnG9gH8Yrmb2COBii6FNs5btAAAWFElEQVR2Kwo0JxCH+ON6/k8f7ur3zVLdGQBKSVpHgboCvQaAFdUdhw853Xf8kOAV61JbXYFmBE4E4la+hwDfLd2VAaC0qPUUqCPQewDYUvVawP7AfsNnBS5Sh9uqCixN4HfAR4HXAW8vcah/WysxACxtxm5YgZkEDAB/ynUO4DrATYYrCu4NXG+8psBMsD5ZgSULnA4cAxwBHD5eHTP+8q/+MABUJ3YDChQRMABsjPFSwB7AlYYPS+0K7DL+XGBjL/dZClQTiA/txdX64ufH47n8Y4H4RP+mvsY3b6cGgHkFfb0CixEwACzG2a0o0I2AAaCbUbvQ5AIGgOQDtH0FWhMwALQ2EftRYG0BA4B7hgIKFBUwABTltJgC1QQMANVoLaxAnwIGgD7n7qrzCRgA8s3MjhVoWsAA0PR4bE6BVQEDgDuDAgoUFTAAFOW0mALVBAwA1WgtrECfAgaAPufuqvMJGADyzcyOFWhawADQ9HhsTgFPAbgPKKBAHQEDQB1XqypQWsAjAKVFradA5wIGgM53AJefRsAAkGZUNqpADgEDQI452aUCBgD3AQUUKCpgACjKaTEFqgkYAKrRWliBPgUMAH3O3VXnEzAA5JuZHSvQtIABoOnx2JwCqwIGAHcGBRQoKmAAKMppMQWqCRgAqtFaWIE+BQwAfc7dVecTMADkm5kdK9C0gAGg6fHYnAKeAnAfUECBOgIGgDquVlWgtIBHAEqLWk+BzgUMAJ3vAC4/jYABIM2obFSBHAIGgBxzsksFDADuAwooUFTAAFCU02IKVBMwAFSjtbACfQoYAPqcu6vOJ2AAyDczO1agaQEDQNPjsTkFVgUMAO4MCihQVMAAUJTTYgpUEzAAVKO1sAJ9ChgA+py7q84nYADINzM7VqBpAQNA0+OxOQU8BeA+oIACdQQMAHVcrapAaQGPAJQWtZ4CnQsYADrfAVx+GgEDQJpR2agCOQQMADnmZJcKGADcBxRQoKiAAaAop8UUqCZgAKhGa2EF+hQwAPQ5d1edT8AAkG9mdqxA0wIGgKbHY3MKrAoYANwZFFCgqIABoCinxRSoJmAAqEZrYQX6FDAA9Dl3V51PwACQb2Z2rEDTAgaApsdjcwp4CsB9QAEF6ggYAOq4WlWB0gIeASgtaj0FOhcwAHS+A7j8NAIGgDSjslEFcggYAHLMyS4VMAC4DyigQFEBA0BRTospUE3AAFCN1sIK9ClgAOhz7q46n4ABIN/M7FiBpgUMAE2Px+YUWBUwALgzKKBAUQEDQFFOiylQTcAAsD5tvJ9dGtgDuBKwG7Dz+HP+9V/uMxSoKnAKED8nAz8FvgF8BTgO+E3VLW+juAFgGepuU4HZBQwAf2q2A3BdYO/xJ/7vnWan9RUKLFXgd8CxwBHjz8eBny+iIwPAIpTdhgLzCxgAzjS81vDX0/7APYALz09rBQWaEvg98GngtcORrDeMRwyqNGgAqMJqUQWKC/QeAM4N3H/4y+ihwOWL61pQgTYFfjns768bTmMdAny7dIsGgNKi1lOgjkCvAWAX4EHAQcCudWitqkDzAqcB/wo8DfhaqW4NAKUkraNAXYEeA8BtgRcCl6lLa3UF0ghEEHgJ8PgSpwYMAGnmbqOdC/QUAHYf3+T27XzmLl+BbQl8Czhg+BDs++YhMgDMo+drFVicQC8B4PbDX/z/D7jA4mjdkgIpBc4Yj5AdDPx2MyswAGxGzdcosHiBqQeAcwLPGr4f/eDF07pFBVILHAncDYijAjM9DAAzcflkBZYmMOUAEBfreRtwi6XpumEFcgucANwK+NwsyzAAzKLlcxVYnsBUA8AFgfcA118erVtWYBICcYXBOwMf2uhqDAAblfJ5CixXYIoB4CLDFfw+Aey5XFq3rsBkBOKSwvE5mg9uZEUGgI0o+RwFli8wtQAQl+z9iH/5L3/HsoPJCZwK3Az41HorMwCsJ+R/V6ANgSkFgPjA33uBfdqgtQsFJifwkyFg32C82dA2F2cAmNzcXdBEBaYUAF7gp/0nupe6rJYE4i6Dcd+Mk7bVlAGgpXHZiwLbFphKAIir+70LiPceHwooUFfgTcNRgP0MAHWRra5AbYEpBIC4wl98Ten8tbGsr4ACqwL3A161lodHANxLFMghMIUAEOf947vKPhRQYHECcUfBvYAfbL1JA8DihuCWFJhHIHsA+Bsg1uBDAQUWL/D64S6C9zQALB7eLSpQQiBzAIhb+h4DXLIEhDUUUGBmgbhvwE2Bj275So8AzOzoCxRYikDmAPBo4BlLUXOjCiiwIvBZ4HoGAHcIBfIJZA0AOwLfAC6Wj9yOFZicQFx74/CVVXkEYHLzdUETFcgaAOLufvG9fx8KKLB8gTgFsLcBYPmDsAMFZhHIGADiD4y4GMnlZ1moz1VAgaoC1wC+EFvwCEBVZ4srUEwgYwCIS5H+ezEBCymgQAmB5wxXB3yEAaAEpTUUWIxAxgDwsuG7xw9cDI9bUUCBDQr8CLgEcLpHADYo5tMUWLJAtgCwAxBvNF71b8k7jptXYA2BW8Qtgw0A7hsK5BDIFgA8/J9jv7LLPgWeDTzSANDn8F11PoFsAeAfh88YPTkfsx0r0IXA54FrGgC6mLWLnIBAtgAQXze68QTcXYICUxT4PbCrAWCKo3VNUxTIFADONt6DfKcpDsI1KTARgVsbACYySZcxeYFMAeAywLcmPxEXqEBugYMMALkHaPf9CGQKADePTxj3MxpXqkBKgZcZAFLOzaY7FMgUALz8b4c7qEtOJ/AxA0C6mdlwpwKZAsBTh4uMPKHTOblsBbIIHG0AyDIq++xdIFMAeB7w0N4H5voVaFzgewaAxidkewqMApkCwCuA+zk5BRRoWuBEA0DT87E5BVYFMgWANwF3c3YKKNC0wO8MAE3Px+YUSBkA3gLcxdkpoEDbAgaAtudjdwqsCGQ6AmAAcL9VIIGAASDBkGxRAcAA4G6ggAJFBQwARTktpkA1AQNANVoLK9CngAGgz7m76nwCBoB8M7NjBZoWMAA0PR6bU2BVwADgzqCAAkUFDABFOS2mQDUBA0A1Wgsr0KeAAaDPubvqfAIGgHwzs2MFmhYwADQ9HptTwFMA7gMKKFBHwABQx9WqCpQW8AhAaVHrKdC5gAGg8x3A5acRMACkGZWNKpBDwACQY052qYABwH1AAQWKChgAinJaTIFqAgaAarQWVqBPAQNAn3N31fkEDAD5ZmbHCjQtYABoejw2p8CqgAHAnUEBBYoKGACKclpMgWoCBoBqtBZWoE8BA0Cfc3fV+QQMAPlmZscKNC1gAGh6PDangKcA3AcUUKCOgAGgjqtVFSgt4BGA0qLWU6BzAQNA5zuAy08jYABIMyobVSCHgAEgx5zsUgEDgPuAAgoUFTAAFOW0mALVBAwA1WgtrECfAgaAPufuqvMJGADyzcyOFWhawADQ9HhsToFVAQOAO4MCChQVMAAU5bSYAtUEDADVaC2sQJ8CBoA+5+6q8wkYAPLNzI4VaFrAAND0eGxOAU8BuA8ooEAdAQNAHVerKlBawCMApUWtp0DnAgaAzncAl59GwACQZlQ2qkAOAQNAjjnZpQIGAPcBBRQoKmAAKMppMQWqCRgAqtFaWIE+BQwAfc7dVecTMADkm5kdK9C0gAGg6fHYnAKrAgYAdwYFFCgqYAAoymkxBaoJGACq0VpYgT4FDAB9zt1V5xMwAOSbmR0r0LSAAaDp8dicAp4CcB9QQIE6AgaAOq5WVaC0gEcASotaT4HOBQwAne8ALj+NgAEgzahsVIEcAgaAHHOySwUMAO4DCihQVMAAUJTTYgpUEzAAVKO1sAJ9ChgA+py7q84nYADINzM7VqBpAQNA0+OxOQVWBQwA7gwKKFBUwABQlNNiClQTMABUo7WwAn0KGAD6nLurzidgAMg3MztWoGkBA0DT47E5BTwF4D6ggAJ1BAwAdVytqkBpAY8AlBa1ngKdCxgAOt8BXH4aAQNAmlHZqAI5BAwAOeZklwoYANwHFFCgqIABoCinxRSoJmAAqEZrYQX6FDAA9Dl3V51PwACQb2Z2rEDTAgaApsdjcwqsChgA3BkUUKCogAGgKKfFFKgmYACoRmthBfoUMAD0OXdXnU/AAJBvZnasQNMCBoCmx2NzCngKwH1AAQXqCBgA6rhaVYHSAh4BKC1qPQU6FzAAdL4DuPw0AgaANKOyUQVyCBgAcszJLhUwALgPKKBAUQEDQFFOiylQTcAAUI3Wwgr0KWAA6HPurjqfgAEg38zsWIGmBQwATY/H5hRYFTAAuDMooEBRAQNAUU6LKVBNwABQjdbCCvQpYADoc+6uOp+AASDfzOxYgaYFDABNj8fmFPAUgPuAAgrUETAA1HG1qgKlBTwCUFrUegp0LmAA6HwHcPlpBAwAaUZlowrkEDAA5JiTXSpgAHAfUECBogIGgKKcFlOgmoABoBqthRXoU8AA0OfcXXU+AQNAvpnZsQJNCxgAmh6PzSmwKmAAcGdQQIGiAgaAopwWU6CagAGgGq2FFehTwADQ59xddT4BA0C+mdmxAk0LGACaHo/NKeApAPcBBRSoI2AAqONqVQVKC3gEoLSo9RToXMAA0PkO4PLTCBgA0ozKRhXIIWAAyDEnu1TAAOA+oIACRQUMAEU5LaZANQEDQDVaCyvQp4ABoM+5u+p8AgaAfDOzYwWaFjAAND0em1NgVcAA4M6ggAJFBQwARTktpkA1AQNANVoLK9CngAGgz7m76nwCBoB8M7NjBZoWMAA0PR6bU8BTAO4DCihQR8AAUMfVqgqUFvAIQGlR6ynQuYABoPMdwOWnETAApBmVjSqQQ8AAkGNOdqmAAcB9QAEFigoYAIpyWkyBagIGgGq0FlagTwEDQJ9zd9X5BAwA+WZmxwo0LWAAaHo8NqfAqoABwJ1BAQWKChgAinJaTIFqAgaAarQWVqBPAQNAn3N31fkEDAD5ZmbHCjQtYABoejw2p4CnANwHFFCgjoABoI6rVRUoLeARgNKi1lOgcwEDQOc7gMtPI2AASDMqG1Ugh4ABIMec7FIBA4D7gAIKFBUwABTltJgC1QQMANVoLaxAnwIGgD7n7qrzCRgA8s3MjhVoWiACwO+B+H99KKBAuwIGgHZnY2cKZBQ4I37xnwLslLF7e1agI4FXA/dJst7o9d5JerVNBXoVOCUCwAnARXsVcN0KJBF4IfCQJL2+CDggSa+2qUCvAsdHAPgacPleBVy3AkkEngY8PkmvTwcek6RX21SgV4HjIgAcBVy7VwHXrUASgUcBhyTq9ZlJerVNBXoVODICwJuAu/Uq4LoVSCJwR+CdSXq9M/C2JL3apgK9CrwhAsCTh28C/GOvAq5bgSQCVx6C+jFJer0K8OUkvdqmAr0K/FMEgHsAr+9VwHUrkEDgdGAX4DcJeo0WzzV+u+jsSfq1TQV6FLh7BIC9gKN7XL1rViCJwJeAqyfpdaXNOAIQRwJ8KKBAmwJ7rlwA6PvAxdvs0a4U6F7gecDDkym8AHhwsp5tV4FeBH4AXGIlAMQpgDgV4EMBBdoTuB1wWHttbbej+NDivyXr2XYV6EXgdcD+KwHgvsAre1m561QgkUCc/7/wcATgxEQ9R6sXGC4G9GPAzwEkG5ztdiHwd8BrVgLABYE4JBAf3vGhgALtCLwXuE077czUyfuBW8z0Cp+sgAK1BX47nvL/6ZY3AYrDdXHYzocCCrQjcPfhg7pvbqedmTrxG0YzcflkBRYiENfouEtsacsA4Dm7hdi7EQU2LPBLYDfgVxt+RVtPPDfwQ+B8bbVlNwp0LXB74N1bB4BzAl8HLtk1jYtXoB2BTDcA2paaNwZqZ3+yEwW+A1xhuK/IaVsHgPjfDwXiK0c+FFBguQLxD/SKwy2Av73cNube+qXGG47FHxg+FFBguQIHAoeutLDlKYD4/9tx+GrAN4CLLbdHt65A9wL/Mhw+//uJKLxqCDL3mchaXIYCWQWOBy635SnFrQNALOwg4NlZV2jfCkxA4NdAXPv/mxNYSywhDjn+D+BRgIkM1GWkFIgj/HGBrtXHWgHgHMB/DRfxuFrKJdq0AvkF4gZdT8q/jLOs4P8Cj5vYmlyOAlkE/nv44N81V879rzS9VgCI//bXwMe3+pZAloXapwKZBeKDuHEN/TgKMKVHfCMgjgLsPqVFuRYFEgicMfw+v8n4O/0s7W4rAMSTPG+XYLK2OCmB+Id6S+CDk1rVmYu5FfAe/7CY6HRdVqsCLx8u9PfAtZrbXgDYGThqvFtgqwuzLwWmJHAI8KgpLWiNtTwXeNjE1+jyFGhF4KtD6L42cNKsASCeH4ciPwvs1Mpq7EOBiQocOZ56i8t0Tvmxw3go8vpTXqRrU6ABgTiNeL3hCr9f3FYv2zsCsPKa/YFXe9iugXHawlQF4mp58Q81LtLRw+OywKfHqxz2sF7XqMCiBeJ04j2BN2xvwxsJAPH6Rw/XCHjGolfg9hToQCAu93tj4PMdrHXLJV4V+MRw4bHzd7Zul6vAIgQOBp613oY2GgCiTlwbIK4R4EMBBcoIxOH+WwMfKVMuXZUIPnHHwLgAmQ8FFCgjEJfffvBGSs0SAOK5z/EDPBth9TkKrCtwMnAn4MPrPnPaT9h3+KxR3J1sl2kv09UpsBCB+EM9/vqPUwDrPmYJACvF4mpC8Unezbx23YZ8ggIdCPwMuM14HryD5a67xPiU8vuGa5RfZN1n+gQFFFhLIH7hP2X4DzNdQGyzv8TvNdwv4GVAXNzDhwIKbFzgaOAOwHEbf0kXz9wDeCewZxerdZEKlBM4FXjAeh/4W2tzmw0AUWuv4Xrlbxm/KlhuKVZSYLoCrwP+YThEd8p0lzjXyuIPirhW+f3nquKLFehH4FjgrsCXN7PkeQJAbC/O2z1/vNPXvLU207+vUSCDwC/Gz868JkOzDfR43/HzRudroBdbUKBFgTjk/wrg4fP8QVHql3bcOyDuMRxf7fGhgAJnCrx1/ETuCaLMJLDbcAGyfx6/y1zqfWqmBnyyAo0KfAk4APjkvP2V/IcVV/iKph4D7DpvY75egeQCnwIeO37XPflSltp+3MTkaeOFkpbaiBtXYMkCxwNPB14MnF6il5IBYKWfcw33Mb/30OATgEuVaNIaCiQS+I/hw7HPBA5L1HOGVm8wXpAsvj3hQ4GeBOIKofEV/H8Z/g38quTCawSAlf7iiEDc/SsuJRwXO4lg4EOBKQrEpXzfCLx2e9fdnuLCl7CmvxjfU/bzUsJL0HeTixL4zXjnzHhPiYtlnVZjwzUDwJb9XmC41OntgZsOh0T3HpLMxWssxpoKLEjg9+Mv+iOADw038Tkc+N2Ctu1m/ihw9uEc6D7Azcf3lKsN34M+mzgKJBb4PhDvKfF+8m7g57XXsqgAsPU64ru+Vx/+aorv/sb/vft4EZD4VkHchtirgtWevPXXE4h/fHG1vviJD/B9BYhbax4zHNmKO/f9dL0C/veFClx4uJjQdcf3k3hfudL4WaR4L4mf+CPEhwLLFFh5P4mvAf94OFX+TSC+xhfvLXHHvvi/F/r4/472Evuqlno/AAAAAElFTkSuQmCC') !important;
    background-size: 20px 20px !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
}
/* 2. CRM Grid (People) */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2)::before {
    content: "" !important;
    background-image: url('data:image/png;base64,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') !important;
    background-size: 20px 20px !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
}
/* 3. Power Dialer */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3)::before {
    content: "" !important;
    background-image: url('data:image/png;base64,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') !important;
    background-size: 20px 20px !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
}
/* 4. Lead Generator (Commented Out)
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4)::before {
    content: "" !important;
    background-image: url('data:image/png;base64,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VQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPwZ9mpLAAAWEUlEQVSmBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RN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') !important;
    background-size: 20px 20px !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
}
*/
/* 4. Scraped Leads (Modified Index from 5) */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4)::before {
    content: "" !important;
    background-image: url('data:image/png;base64,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VQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPwZ9mpLAAAWEUlEQVSmBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNXq9pF3SqvsKf1DSf/CVS60UvT4tdQue4jdIurWnVHqVp0g6K30rng38nKQ/9JRKr8L7P5247gYIAHVnM1Zn35F0p7E2tsR2TpH0giXWH3PV90p63pgbXHBb35Z05wXXHXu1wySdPfZGF9zev5X0iQXXHXs13v9jixfaHgGg0DBW1MrfS7rnirY9z2bfIulV86ywwte+VdLLV7j9zW76a5LuvdkXr/h1Pynpf6+4h81u/uGS/nKzL17x63j/r3gAq9w8AWCV+jW2fZ6kx9RoZYddHCPpPQ36jBZfKOmdDXo9R9LjG/QZLd5F0jeb9HpXSd9q0ivv/yaDymiTAJCh2qvmyZJe1KDln5b05w36jBYPkXR+g15PGn6pHtegz40WrxqC1d2K93ulpH2K97hle7z/Gw3L3SoBwC3ar16cWPeB4m3/cPZd9f8p3udGe7vN/gLctXi/caJiXLHQZYmTAONkwMrLmZKOrNzgVr3x/m80LHerBAC3aL96ew0n110h6VaFW4+PKR9XuL9ttfZnw6cA8alF1SWuAIi/VL9RtcFt9BWfVMVfrJWXYwfXd1ducKveeP83Gpa7VQKAW7RnverfA3b6/n/jCKh+HkCcpR5nq3da4uP/ywtfuhiX1N1jOAckvqrotPD+7zQtY68EACNm41LPGs4Gf3/R/uNj/30lXV20v+21FSetXSbp9kX7PkrS6UV721FbH5X0s0X7/oikw4v2tqO2eP83HJqjZQKAQ7F/jdtIukTSvQruyn+T9LKCfW2mpTjJ7sWbeeHIr/n68Mv/JyRdN/J2HZt79HDVyicdhRJqPErSBQl1s0vy/s8WLlqfAFB0MCtoq+JH1tdK2n/2se8KSJbeZNxf4aKCnwJ0/Eply2FU/Mi641cqW5ry/l/67d6vAAGg38yyOo7bAcfNS/5V1gYWqPsfJb1pgfUqrfJrkl5fqKHPSIqb6sRJgF2XA4eP2j8rKf5yrbDEJyn/crj9899UaGbBHnj/LwjXeTUCQOfp+Xs/eDgx7H9Juq2/9NwV/0rSv2n6MfWWOxuXAv6FpIfMLeBfIS6nDNP45dl9iVAV4arC8trhKpo3VGhkyR54/y8J2G11AkC3ieX3e/xwzX18777KJe5PHj+MvrLKJozbvv9w4tqnJd3RWHORUnE+Qoc7FG5m3+Iv1riTYdx0aZXLuZLiOQWdP1HZ0o/3/yqPppG3TQAYGbzJ5k4czrp/6Yp6/afZWd4fX9H2szb7WEkfk7SqmwP9dpM7Ps7jH7fc/ZSkB8yzkvG1X5IUJ/51ue3vZned9/9mpZq/jgDQfIBJ7cdNgU4d/gKPS8XGXOK71F9o9NjXeW3imfZx6d3YX7HEJZ7PHT4yv3Hehhu8Pk60jL/C46qGMZe4aiZuThVXVKzbwvt/3Sa6nf0hAExk0AvsZhwb/1XSKxZYd5FV4mP/eI56/DBf5yUevvMHIz6COWb4K5JuWmPUuEHQn0h66Ej7eKGkJw6fqPzjSNtbxWZ4/69CfeRtEgBGBm+4uSOGxwX/rqQ9E3uPk9Li/ulfTtxGpdL3m92DP84cz1q+N9zi+QWSPpi1gWJ146uVCDvxHXbmcpqkuIyyy3MplrXg/b+sYOH1CQCFh1OotbgT3wkJXwl8X9JbZrXjDPUpLXEJW9zb/tcl3cG8438s6SWS4lnvU1vi0dbxvAD3eQERTuPJiWdPDXR2J07e/2s4eALAGg41cZfi4Ta/Otzt7NAltxG/+E+Z/fKPe7tPeYl7x79quG3wLxpuGBQ3o3nj7MS4KZvGpwFxzkO47rckxN8Nc3nzcJfM963BJalLUtz8cCve/8sqFlqfAFBoGI1aeeDwcf0zZ/c9j/+9meUHs3sM/J6keGRqt3v7b2Yfl3nNnYcbycTjeeOrkJ+a42qBOBP9Q7OTCzvfiGYZu+2tG5cKxgOPnjH7vz++yY3Ed/txFcoZkiJUrcslfpvc/Z2+jPf/Tol6vIAA0GNOlbvcezgB62HDd80HDOcKxBnZ8XH27rNf8HFiX1zLH7+Y4i6DU/nedNl5xQOEHj4zjbPb7zTcmyECQtwaOb7bv1TSxTPTK5fd2ETWj591Bw1XmDxIUtyXIY7bja9erpEUjmH6hdm/dT5p0jly3v9OzZFrEQBGBmdzCCCAAAIIVBAgAFSYAj0ggAACCCAwsgABYGRwNocAAggggEAFAQJAhSnQAwIIIIAAAiMLEABGBmdzCCCAAAIIVBAgAFSYAj0ggAACCCAwsgABYGRwNocAAggggEAFAQJAhSnQAwIIIIAAAiMLEABGBmdzCCCAAAIIVBAgAFSYAj0ggAACCCAwsgABYGRwNocAAggggEAFAQJAhSnQAwIIIIAAAiMLEABGBmdzCCCAAAIIVBAgAFSYAj0ggAACCCAwsgABYGRwNocAAggggEAFAQJAhSnQAwIIIIAAAiMLEABGBmdzCCCAAAIIVBAgAFSYAj0ggAACCCAwsgABYGRwNocAAggggEAFAQJAhSnQAwIIIIAAAiMLEABGBmdzCCCAAAIIVBCIAHC9pF0qNLOTHj4s6ckN+qRFBBBAAAEEygtEAPi+pNuX71Q6V9KhDfqkRQQQQAABBMoLRAC4WtKe5TuVPi/pwQ36pEUEEEAAAQTKC0QAuFzS3ct3Kv1A0u6SbmzQKy0igAACCCBQWiACQPxlfVDpLv9fcwdIurhJr7SJAAIIIIBAWYEIAOdLOqRsh7ds7FhJ727SK20igAACCCBQViACwJmSfr5sh7ds7EOSjmjSK20igAACCCBQViACwNsk/XLZDm/Z2HWz8xW+2aRf2kQAAQQQQKCkQASAl0h6R8nutt3ULw1XLZzYqF9aRQABBBBAoJxABICflfTRcp1tv6HLJP2EpB826plWEUAAAQQQKCUQAeA+kr5SqqudNxNfWbx95y/jFQgggAACCCCwLYEIAPHvO8O5AHdsRPRdSQ+QdEWjnmkVAQQQQACBMgLxyz+W/ynpp8p0tblGPiHpCdwYaHNYvAoBBBBAAIEtBTYCQJxU99KGNK8fen5dw75pGQEEEEAAgZUKbASAp0r6/ZV2stjGbxq+BniBpPcutjprIYAAAgggME2BjQCwr6Q4u77jcoOkYyT9Tsfm6RkBBBBAAIFVCGwEgNj2RZL2X0UThm3GJwFvHE5ojK8EeFiQAZQSCCCAAALrLbBlAOh6HsCWEzpH0tGzJxyu9+TYOwQQQAABBJYQ2DIAHCbp7CVqVVn1e7NPAk7iZkFVRkIfCCCAAALVBLYMALtKumq4wc4e1ZpcsJ/LJf2mpPdL4tkBCyKyGgIIIIDAegpsGQBiD+OX5bPWbFfjAULxycafzh59/LeS4sRBFgQQQAABBCYrsHUA+PeS/njNNeIZAnHr4yslXcPXBGs+bXYPAQQQWA+B70u6VtLfS7pY0l8uezfcrQPAbSRdKmnv9fBiLxBAAAEEEFhbgbh678OSTpP0xXn3cusAEOu/SdKr5y3E6xFAAAEEEEBgZQLnSfr12Vfdm2piWwEgHrUb35Nv679tqigvQgABBBBAAIGVCHxkdmv/r+1s69v7Jf8nkn5mZyvz3xFAAAEEEECgnEBcDv9CSWfsqLPtBYDHSjq33C7REAIIIIAAAghsVuDtkl4uKe6W+/8tO/qY/zOS/vVmt8LrEEAAAQQQQKCcwOmSnr2t2+TvKAAcLulD5XaFhhBAAAEEEEBgHoF3D5e+H7v1CjsKAPHfLhzuC/DQebbCaxFAAAEEEECgnMDxkt6xZVc7O9N/XZ4PUG4SNIQAAggggMCIAnETvEdIiq/3b152FgDiNVwRMOKE2BQCCCCAAAJJAp+TdLCk6zcbAA6QFCvFXQJZEEAAAQQQQKCvQFwe+K7NBoB43Zslvarv/tI5AggggAACCMxu938/Sddt5iuAELv97FOAuEsgCwIIIIAAAgj0FYin/p622QAQuxk3Bzpnk+cN9GWhcwQQQAABBNZbIG70d+g8ASA4TpzdY3i9adg7BBBAAAEE1lfgRkn7zBsAdpX0F5Iesr4u7BkCCCCAAAJrL/D0eQNAiBw4CwG7rz0PO4gAAggggMB6Cpy0SAAIiiMkncX5AOt5VLBXCCCAAAJrL3DuogEgZN46e8rQ2iuxgwgggAACCKyZwNeWCQC3kvQBSU9bMxR2BwEEEEAAgXUX+PYyASBwbivpY5Iet+5S7B8CCCCAAAJrJHD9sgEgLO4o6fzZ/YXXyIZdQQABBBBAYG0FrnUEgNC523BTgQskxe0FWRBAAAEEEECgtsA/uAJA7OZ+kj5OCKg9cbpDAAEEEEBA0oXOALDxSUCcExCPG2RBAAEEEEAAgZoCcz0LYLO7cAdJfyDpsM2uwOsQQAABBBBAYFSB49yfAGx0H1cHvF/S00fdHTaGAAIIIIAAApsRODArAMTG4z4BJ0h6JXcM3MwseA0CCCCAAAKjCFwy3Mfn/pkBYGMvDpV0uqS9RtktNoIAAggggAACOxL4NUlvHCMARBP3kPQ/JD2SmSCAAAIIIIDAygR+IOm+kq4YKwDEnt5a0n/hK4GVDZ0NI4AAAgggcJKk44JhzACwwf7Tkk6ePVaYUSCAAAIIIIDAOALfknSApG+sKgDEdm8j6WWS4nuIuGyQBQEEEEAAAQRyBZ4/fCX/3o1NrOITgC137+6S3iTpqNx9pjoCCCCAAAKTFoj78zx1S4FVB4CNXuJpgq+V9KhJj4edRwABBBBAwC/wudnv1+9WDAAbPT1a0mu4i6B/+lREAAEEEJikwFdnv/yv2Hrvq3wCsHVfD5H0ckm/MFyruMskR8ZOI4AAAgggsJzAFyU9QdJl2ypTNQBs9BrXKj5P0tGS9lnOgbURQAABBBCYjMCZwy/+X5R0i4/9K38FsL3JxD0E4o6CT5P0ZEl7TmaE7CgCCCCAAAKbF4hL/V695dn+21u1+icA2+o7HjQU9xKIjzXi3wM378IrEUAAAQQQWEuBuMNfXOL3ho3r/He2lx0DwNb7tLekR8z+PXx4FPFBkvbY2Y7z3xFAAAEEEFgDgb+dPW/nFElXzrM/6xAAtrW/+0l6wPBI4ntLiv99T0l3k3TX2b/dZrcmvuM8WLwWAQQQQACBFQlcIyn+XSrpYkkXSjpP0pcW7ef/As71hAZwlrD0AAAAAElFTkSuQmCC') !important;
    background-size: 20px 20px !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
}
/* 6. Spreadsheet Tool */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(5)::before {
    content: "" !important;
    background-image: url('data:image/png;base64,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') !important;
    background-size: 20px 20px !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
}
/* 7. Google Maps Scraper */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(6)::before {
    content: "" !important;
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAAAXNSR0IArs4c6QAAIABJREFUeF7snQd4VFXax//nTk0mjZ6E3qUKSUB6JiAgdsVAEkBREUUsdJJgAdvuqqvrWhZc/VQIsIu9AAoKSO+dFHrvLT2Zycz59kxQQUpm5pa59845z5MnaM55y+/c5L5zyvsS8MYJcAKaJtD5vftqWEykoZvSGnAZwincEQQkDJSGU0ptIMRKKSwCgYkCZhBqAoiJuokJxF1BQMohoJxQlIHQUriFUgi0DEApiFBK4C5xu1FKDKREcAvFRHAfF06eO7Bs6rIKTYPTufEUELa3RMMKghZEQAsANSlFBAXCCRAOiggiIJxShF/6fxFg/7+yFVKggACFhKCQulEIggLK/rvy/xUAOEvd2G2k2N0+D4cI4NY5Ut25R3TnEXeIE9AwAftUu9ERW6ut4HS3opQ2dhNSn7hpLCitDYrq1PNShw2UWkBhopQKoIFxmAiEgsBJBFIGQkrYS4EScoEAZ0FwWiDkOBXIEerGAQiuratHfX06MJbqW+u6m1DDDLR0w/Oib0kpWlCgJQGaAbAo5H05BfYSII8Q7KZu5AnAbgeQd0suzilkA1fjIwEeAPgIjHfnBEQRoCD2T5PruKmxtavMcRt1uW+hbtSFm9akbmqjbmoUJV/Fg4lA3EQgpRBwjgjCcRDsIxCyKcFGl8uydt0zs9mnSt6qILC+LeobKtAHBL0Bz1ddlUM7BmAJKJa4jPil804cUbm9QWMeDwCCZqq5o0oS6DkvuZbRYWjvJmgvuNGcEqERQBsDaAgg5HdbKOCucIOyLxf9/d/uCgrQAH20VxLUZbqIQFxsmwECOUdAjsJANwkQfgl3lSxa+MzC8gCZFXC1m5uhFjUjCW70BkEfVH6y13LbC4pfIGAJcWBp3F6c0bIzWradBwBanj1ue8AJDFgwwFJ6oVor4kZ7Smh7ELQHRXsAdcQaxwIC6nJXBgVOCrfT5fl3oJb8xfrj93gCEIPAziAch0CyDYKwirrpD6ue+nKX3zJVPnDLTejmJngA8Lzw2wHQ699qFuXuAPCLQPFFx1ysVvnU6Mo8vT5Uupok7ow6CNjnpNYkLnqLm5D2hLIXPtoTeA5XKbps73a6wb4oCwjYv4MxKGBvRLalYCAXYSQHiEC2gOIn85nz32j1cOLGtmhKKjD0f1sjwwA0VcdTr7gV+0AxixqRlbAT+xTXHmQKeQAQZBPO3fWSANurn5vaEpR0J6Dd3UB3Qj0ve1W2q4ICZ5AeyCaEGozkHAzCdiIIC6ngmqnmw4fb26Ga04VBoHgQQDdVPlyBM2o1CGaaDJjXfgcuBM4M/WrmAYB+55Z75gMB+yfDrdRY1okQ0h0U3UA8f4xr+CBCVV0ppXCXu+F2uCq/gjUgYCsFRqFEMJA9MGAZQGavHv3VhkBO1lI7jFGncYcbGAaKOxU8qR9It8XoLgfBDwIw62JtzE9aBn79VAzNy8byAEAikFyMtgj0mznM5hDcSYDbDtDuFCSOsDvyOm3UTeF28ICATS8xkApiEI4RI1lLgBmrRn+1VIlp39MMlnwTHiHA5EuHQZVQqzcdhyjwt0gn/q/5XgTtwVCpJpUHAFKR5HJUT6BP1pDWLrgHALjtf6eQe4IodkdadWwuDwhc5S7PLYRgbcRAnIJRyIaBfE0thnfXjPj8vJQsNsYjlJTgcQATAcRIKTuIZZ0A8AYNxYyETSgJYg6iXOcBgCh8fLCaCXT/+JFwk7m0DwUdACLcRkAbqNneQNrGAgAWCLjKKrcMgrYRQDAK54hJWCGAzlg5+usf/WWxthkiTGY8BYqxLAufv3L4uBsSYEmn3nY68F6XvZ7shLz5QIAHAD7A4l3VT6DPnNT2LkoGgNLbAHQHYFK/1eqy0LM6wIKBcpfnO/vvYG1su0AwCnmCQfjGaXa+u+6x705VxWJ1a1S3UoyhwNMAoqrqz38uCYGLBHi3jOAf3bIh6QqOJNapVAgPAFQ6Mdws7wkkzU6Lp26kUIJB/FO+99y87clWBNjKQLBvFbCb+ILJcFIwCF9WWJwv/zkY2BgPEynxfNp/HkCYt3x5P0kJFAF4mYbi7YRNcEoqWYfCeACgw0kNBpfYJ/0KSgcTNxkMErR3phWfarZVUFFa4QkIgvncwKVg4JhgFOaZjObX3nh7bluB4H0ArRWfFK7wWgSy3RSjO+Wymx+8XY8ADwD4s6EZAr1mDm4lEMNgEDoYwE2aMVynhrKrhS5PMFDhSWMcjC2itBz3r9+FzvuOBqP76veZYrZLwITO2TipfmOVt5AHAMoz5xp9IGCfNbQZgXsQJTTlUkpUH0bzrkoR8GwT/LYyEARnBgRK0SvnIO7anIsQB19pVuo581NPPiF4fm82PhgEBPEJ16vp8QDAzyeKD5OPALuj7xScgynwGEC6yKeJS5aDgOc2waWVAT3WLWh05gJSV29H/XP5cuDjMuUjsIUSjErIxjr5VGhLMg8AtDVfurY2MWtwJ1AyghCSCiBc184GgXPs9oAnECipqKxXoPFmcLtx78Yc9N65T7eVeTQ+Rd6YTynB2whBOj8kqN8KU948CLyPCgjYPxkeBaNjKAgdAeBmFZjETZCBANsiqCipPC+gxVWBGkUleHTpJrBP/7xpnwAB1hOKwR1zcVD73vjvAV8B8J8dHymCQO/Zab3clD4GeEqeWkWI4kM1ROC3VQEWDGjlFkGHQycwbMVWvtevoefMS1MvAngkPgdfe9lfd914AKC7KVWvQz1mp1UzuOkICBih5sp66iWoL8vUvipgdLs9J/zt2Qf0BZ57cwUBSvGuVcCEttlwBBsaHgAE24wHwF/73JRG1CWMJaCP/i9/ty0AJnCVKibAVgUqip2eswJqyTpYq7DYs+Tf4Cz7kMhbEBDYRA0YnLAT+4LA199d5AFAMM22wr56DvVBmECAgf/LzmVQWD1XpzUCFKgodaKiiOUVCNyhwbgDxzF05VZYnbzqrNYeIZH2FlCCEQnZ+FykHM0M5wGAZqZKI4ZSkMS5qXfCDfbi76URq7mZKiPADgtWFDnBkg0p2W7fuht3bs5VUiXXpTICFHghIQcvq8wsWczhAYAsWINPqP2T4VZqKhtGQMbxLH3BN/9yeew5J8C2B8rkzd9CKEXyup18v1+uidSaXIL34rLxLAGUjUAV5sQDAIWB601d5cE+PAVCnyJAbb35x/1RBwFPDYJip6cOgdTXCNlhv4d+3YL4A8fU4Sy3Qi0E/msheFDPhwN5AKCWR01jdgzIGhJRSlxjQQmrfhapMfO5uRolwGoOVBQ5PDkFpGgWZwVGLtmAVsfOSCGOy9AZAQIsNhPc3zYbrMqg7hoPAHQ3pfI6ZJ+XHEYdxqcJMBFANXm1cemcwLUJsEDAWeTw3Bzwt4WVOTB60Vo05Cf9/UUYHOMoNlA3bk/YjbN6c5gHAHqbUZn86TovOcTiNIyGm0wCQS2Z1HCxnIBPBNjWgLPI6Uk57EurXlSKp39agzr5uvxg5wsK3tc7AnkE6B+Xg0PedddGLx4AaGOeAmblgAUDLGUXIh+nlGQAiA6YIVwxJ3ADAp5AoJAdFqw6EKhdUIwxC1YhqqSMM+UEfCFwTACSOuZgjy+D1NyXBwBqnp0A2hY/Y6Qp3FbwKECmAKgXQFO4ak7AawKs6FBFoeO6twYiS8owYf5K1Cgs8Vom78gJ/EaAAiwtZPeEHJzQAxUeAOhhFqX0gYLY56SlgdJXADSSUjSXxQkoRcDtcMNZUH5FHoEQhxNjF6xCvfMFSpnB9eiRAMU26kBiwn5ovh40DwD0+ID66VPv2Wmd3ZT+A0BXP0XwYZyAqgiwswHOQgeMDhee+mkNmp88pyr7uDGaJfBrQSluSzoITe8j8QBAs8+fdIb3nZsS63CTvxCKYeAloqUDyyWpgoDgphg2bwXa7+P3/FUxIfox4ut9OUgeBMibpUpGXjwAkBGu2kWz7H0wlY8HwA748SI9ap8wbp9fBJIXbECXLXv9GssHcQI3JEDwYXw2HtcqJR4AaHXmRNqdODstmVD6BoCGIkXx4ZyAagnc9usO9F25U7X2ccO0T4AAL8fl4AUtesIDAC3Omgibe88aHOcmAtvn7ylCDB/KCaieQLfNezFw4QbV28kN1D4BQjAqLhvTteYJDwC0NmN+2tt/XnL18nLD65SQhwkg+CmGD+MENEGg/vHzeHrmYhgCWFZYE6C4kVIRcAgCenTcBU1FnDwAkGr6VSzHnpUymIL8kxfrUfEkcdMkIxBS5sC4j35E9fxiyWRyQZyAFwQOChZ07LgVF73oq4ouPABQxTTIY4Q9a0g9UPcHILhLHg1cKiegPgLDv1iBdnlH1WcYtygYCHwdn4P7teIoDwC0MlO+2ElBEuekPQFK/0qACF+G8r6cgJYJ9NywG/cu2qRlF7jtGidACZ5NyMY/teAGDwC0MEs+2Jg0a2hLCtdHIOjhwzDelRPQPAG+76/5KdSLA5o5D8ADAJ08cpW5+wsngeJ5EFh04hZ3gxPwioBn3//jn1D9Iq/u5xUw3klWAqxmgMGCOLWfB+ABgKyPgTLCE7MGdwIVPiIE7ZXRyLVwAuoiMPzLlWiXe0RdRnFrgp3AV/E5GKhmCDwAUPPsVGEb+9QfYSucRoFJAAwadoWbzgn4TYBl+WPZ/njzjQAF4KBAuRsoZ98vfTEpFnLZlwCYCc8R7hvdS70pHo/PxYd+jVVgEA8AFIAsh4pes9OaC6BzQJEgh3wukxPQAoGwknKk/+sHsC0A3q5PoMANnKkAClyXXvq08rsvjQUBLDBg3yMMQC0jEMEzilSF8AJxomXcXpypqmMgfs4DgEBQF6nTPit1BAhYNj+ev18kSz5c2wRSvl+LTttZiXbeLifA3u3nXZUvffbFPt3L0VhAwAIB9lXdwFcJrsWYAJ/F5WC4HPzFyuQBgFiCCo7v89mDNVwG578B3KegWq6KE1AlgSZHzuDJmT+D/xGrnJ4KCpxzAacrKr+z/1ayGQlQwwDUNlZ+Z//Nm4cABUFifDZWqI0HnyK1zch17LHPTruVUvoZAWI1YjI3kxOQjQAr8Tv+o4WIPpMvmw6tCGa1aA87gINOwKXwS/96jAwEaGQCGpj54aRLjHYW1EHHpGWoUNNzxQMANc3GNWxJnpdsPu00/oVQjAVfYVP5bHHzlCJgX5eLu37eopQ6Veph7/rjTmC/Q74lfrGOsy2CJmYg1sT/eFGKCQm5+LtYplKO5wGAlDQlltUna0hrF9xzANwssWgujhPQLIHIghJMnjEfFoeqPkwpypPt6+91AMVuRdX6rcwmAM3MlWcFgrgVGU1odfN2qCZPNQ8AVPo0Xjrox9JJhqjURG4WJxAQAg99tRLtc4Lzzn++C9jjAC6ydX8NtigD0NwMRAbppWVK8UVCLpLVMnU8AFDLTFyyY8CCAZbSC1HvgWKEykzj5nACASfQ4sBJPD5nacDtUNoAtty/pxw47FRaszz6GpiA5pbg3BZwA/065WCxPGR9k8oDAN94ydq719yU+oJL+BKgnWRVxIVzAhol8Myni9Hw2FmNWu+f2ew0/46yypP9emrspkA7a1DeFlgbn4OuaphLHgCoYRYAJGWl9KEg/wFQUyUmcTM4AVURaHbwFEbNXqIqm+Q2psQNbC0D2Hc9tlAB6GAF2PegagR94rMR8IeZBwAqeOqSslInUeA1ns5XBZPBTVAtAfbyZ0FAsDT2iZ998lf6Pr/SfFm+ALYSwFYEgqZRLInPRZ9A+8sDgADOQPePHwk3WUs/AVV3wYgAIuKqOQEPAbbsz5b/g6WxvX6256+Sa/2yY2cvInYmgJ0NCKLWNT4HawPpLw8AAkTfPif1JrjxNYCbAmQCV8sJaIbAo/OWo/WeY5qxV4yhOeXAMZ0c9vOVQ10T0Cp4ipn/EJ+Du3xlJGV/HgBISdNLWUmz0+6nlH4KINzLIbwbJxC0BGJPXfRk/QuGxpL6sK9gbixxEPsKhkYEdIjbhW2B8pUHAAqTT8xKzSDAqzyrn8LguTrNEhj21Sp0yDmsWfu9NfxUReWeP2+VZwLqBEfSoHnxORgcqDnnAYBC5O1L7UYcjZ4OQh5VSCVXwwlonkDtcwWYNGMBCNX3bnihG9hYAujspp/fzx87D5gQCoTr/3aA2+1G6055yPMbloiBPAAQAc/boQOyhkSUEvcXoOjr7RjejxPgBIBB89fjlq37dI3CQYF1JerN5x8o+KyOwC2hgFnnbykCfBSXg8cCwVnnaAOB9Eqdlcl9yHwA7QJvDbeAE9AOAbPThan/+BoWh35PxLHr/ZtKAZbil7erCbCUwfEhgM4XAgrKCxHd7ShKlX4GeAAgI/HeswbHuYnwA4AYGdVw0ZyALgnE7TyIId+u0aVvvzm1qww4Ebw1jbya2xgj0MbqVVfNdiIUaXG5mKu0AzwAkIl40qyUOygh/wVgk0kFF8sJ6JrAyLlL0XL/Sd36yEr5Zpfr1j1JHWttqSwprNtG8WN8LgYo7R8PAGQgbs9KGQ2Qd3hmPxngcpFBQSCysBTPv/utbg//uSiwmu/7e/0ss/MA3UIBg37fWC4XQb3O2VA04tUvTq8fLek6Tp06VVjaPO8NQjFOOqlcEicQfASS1uTgziVbdev4AQewL8jv+/s6uU3NQGMd5wcgFOPjcvGWr1zE9OcBgBh6l41NnpdsOOMwsuQ+QyUSycVwAkFLgF39q3M2X5f+s1P/q9iVP33fbJR87tin/+56vhVAsS0+Fx0kB3cDgTwAkIB28rxk82mHYS4BuV8CcVwEJxDUBOqfOI8x//eTbhnklQNH9HuxQdZ5q28CWuo4VTClaJ+Qix2yQrxMOA8ARJLuOi85xOIwfQlQxQ9wiDSdD+cEVEngvkWb0GPDblXaJtYoVtZ3TUnwFPkRy+vP49kLq2uojssHU7wZn4uJUnO7njweAIggbZ+XHAaH8XsAdhFi+FBOgBO4RED4X8Y/dvffVqLP4/Hby4DT/NqfqOe9thFor99rgSficlCXKBQj8gDAz0fR/snwKJjKFgKki58i+DBOgBP4E4EGx87h2U8X6ZILS/azQfFUL7pEiU4hAEsSpMcmEHTsmA1FTsDyAMCPJ6jnvORaBoeR/ZVS9MCGH6byIZyApgj0WZ2N25cGrDiarKzYnX9295838QRYTgCWG0CPTcnbADwA8PEJ6js3JdbpIj8DaOXjUN6dE+AEqiDw+JylaHFA0avQiswJO/C/vBhw8pP/kvA2EaCXDdDjC4wAC+JycIckoKoQokd+snGzz01pRF3kFwI0kU0JF8wJBCkBg8uNV/7+BVgNAL21C67KnP+8SUeA1Qiops9tgMKCOqietAyynxbhAYCXz2OvmcMaC0LFrwDqezmEd+MEOAEfCDQ5fBqjZ/3iwwjtdN1dDhzmy/+STlgDE9BCp9sAAkX3jrlYLSmwawjjAYAXhHt/llzXbTCsAEhjL7rzLpwAJ+AHgX4rdqL/csWuQPthof9DWOKfUlb6jzfJCIQIlYmB9NgI8HxcDl6R2zceAFRBuN/MYbUdQsVyAC3lngwunxMIZgLs0z9bBdBbK3IDa0v05pU6/OkSCoTpsFYwAZbF5SBJbso8ALgB4R6z06oZ3HQZIWgv90Rw+ZxAMBMwVbjw6ptfgJ0D0Fvjef/lm1Ed1wcoLy9EtW5HIevJER4AXOfZ7P7xI+FGS+nP/zuR2Vm+x5dL5gQ4AUaAnfxnNwD02NaXAAX6i2tUMVURAtBZv9sAfeNywG6cydZ4AHANtHfNuCu0wBa2kN00kY08F8wJcAK/E9Dr/j+79vdrMZ9oOQkk2gB2LVB3jWJqfC6myemXHrGJ4lVZ2Mf0PQHtJ0qQDgaHm8PQICIGDSJj0SAiFtG2WrCZQxFqtCLUFOL5shotKHaW4HxpPi6U5eN86UWcv/Td899l+bhQmo+zpedR4dbf9S4dTLMqXBj69Wp0zD6kClukNILv/0tJ89qy9HoOAMB/4nOQKidBHgBcRte+1G7EsegvAHKPnNDVKJuAoHFUfcRHt0VcdBvcVLMpoiwRkplaWlGGLaeyseH4dmw4sQ3HCk9JJpsL0j6BcR/9iLqnLmjfkT95cM4FbJF1F1d3yHx2qGMIUEOH+QAosDUhBx19BuLDAB4AXII1depU4ddmeVkU8kZcPsyN7F0tRgt61ItHj3oJ6BDdWtIXflXGnyg6jfUntmPD8W3YcmoXSpxlVQ3hP9cpAfZH6LXX5+kyARBL/ctSAPMmHwGWEpilBtZhK4nLQZichYF4AHDpqUmalfIBJWSUDh+iK1wihCCuThv0bdwDvRp0Rogx8GW12NZA9tk9+PXwOszftwzlFfwvpt6fw8v9iyoowfPvfqtLl/kNAPmnVcc3AeAyoEHnnTgiF0UeAABInJU6kRC8LhdkNcg1Cgbc1bwP0lrfjZqh1dVg0jVtuFhWgHk58/HN7sVg2wa86Z+Anm8A5JUDR3gGQFkf4vomoKVOMwK6gX6dcrBYLoBBHwAkzk5LJpT+F/qsKwG2t5/Y8BY81mEwYsPqyPUcSS630FGEL3IX4qu8n1Dk4FlUJAesIoE9Nu7GfT9tUpFF0pmyvQw4LXtGd+ns1aKk2kagfeAXMuVBR/F0fC7ek0e4Tl963sLqPSulm5sQlnxcl49Phzqt8XjHVNxUo6m3SFTXj90w+DpvET7PXYCC8iLV2ccNEk+AvfxZEKDHtqEUyOeXX2Sd2kgD0ClEVhWBE07wXnw2npbLgKBdAbDPGtoMxLUGQE254AZKLjvNP7JDCrrUlfUAqaLuse2Ab3f/jM92fIkyfkZAUfZyK9NrCWDGbWUxUMZLAMv6CFkJ0MMmq4pACv85Pgd95TIgKAOAPp89WMNlcKwFSDO5wAZCbq3Q6ni4fTJua9IL7LCfHtvRghOYtvKf2HtBf3fG9Thf3vjEDgCyg4B6bMuKgQoeAMg6tcb/Jc636zcAOBKfgwZyAdTnW+IGtOyfDLdSU/kvBOgmF9RAyE1q2BWTu4wEu9qn9+Z0OzF981x8lfej3l3VvX8CpXj9tf9Ar3+IVpcAJTwNsKzPsZ6rAgKg+3JgGgTIspGk19+7az9wFCRxdup/CDBI1idSQeHskN/w9g/gwXb3KahVHapWH9uMv62Zzs8GqGM6/LLCWu70FAHSa9tYClyU5U+3Xon57leUAUjQ6xkAFgGUIyphP/J9J1P1iKAKABKzUv9GgElVY9FGD5aGN6PrKM99/mBtZ0vO45VV72Pb6ZxgRaBpvyMLSvCCTnMAsInZUQac4rcAZH1G6xiBdro8xl2JzWhC/Zu346gcEIMmAEjMSnmMgHwoB8RAyKwdWgOv2iegWbWGgVCvKp2UUsza+TU+2/EV3JSvt6pqcqowpva5AkyePl9LJvtk6+5y4DDPA+ATM187NzABLXS880ldaJWwG7m+cvGmf1AEAEkzU25xC2Q5AczeQFF7nzY1m+PlxHGoZo1Uu6mK2rf66CY89+tboOCnrhQFL0JZ/ePnMeaTn0RIUPfQQw5gj0PdNmrduuZmoKEu/rJfeyYEAZ077sIGOeZJ9wFAz3nJtQwO42YA9eQAqLTMfk16YsItI2AS9Jn8WizPf2/9D+bs+k6sGD5eIQLNDp3CqKwlCmlTXs3JCmAnT2gpK/g2ViDGKKuKgAqnbvROyMNSOYzQdQCQPC/ZcNppXEQoessBT2mZj9ycjGFtg++wny+c2RbA2J9fwfbTsqyY+WIK7+sFgTa7j+GRz5d70VObXc67gM28GqCskxcXAlTXYTXA36ARgnvisiHLpxpdBwB6OvR3Z7PeGH/LCFl/kXwRXu5y4HzpRZwvy0eo0YpqIZGItIR7Ug8Huq08shHPL38r0GZw/V4QiNt1CEO+We1FT212KXYDa/SZ4kA1E9I1FLAJqjFHckMoxZCEXMyRXLBe898zUEmzUgdSAl3cL7q5diu82ScTrKCPko19mt5xJg8bTmzH6eJzOFt6wfPSP1d64Zr5+Q3EgChruOdsAvuqHxGLTjHtwFISsxsLSjVWO+CeL0byA4FKARehp+vmvXhgoSzbmyKskm6oiwIsGRA/lSId08slsY8bLAmQIfCfO+RxkEkleCI+GzPkUKBLbPY5qTfBjfUAwuWApqTMmLDamH7bK4iwhCmiln2y33RiB1Ye3YjVRzcjv7xQtF6jYES72i3ROaY9EmLao2m1BrKvFIz68Xnkntsn2nYuQF4C9nW5uOvnLfIqCbB0tgXAtgJ4k54AW/pnWwB6bpRiQkIu/i6Hj7oLAOzzksPgMLKXfys5gCkpM9Rkxfv9X0KjSHnPL7JT82zZfPGBlVh/YjvKZc61HxNWC6mt78aApolgwYEcbdKSv3pWLnhTN4FbV+3CgGX6nidWDpiVBeZNegKsDDArB6zz9lx8Dl6Vw0f9BQBZqZ8DeEAOWErKZLn8X02cgK4yF/TZciobM7bMQd65/Uq659FVM7Q6UlvfiTua9YbFIO09nmHfjwerG8Cbugl027wXA3W8BcDos2JArCgQb9ITYEWAWDEgPTdCMCouG9Pl8FFX6OyzUyaAkjfkAKW0TFbGN6X1XbKp3XfhED7c+h+sP75NNh3eCmbnBQa1ugP3tugryVkBtqLRf+5wsJoBvKmbQLu8oxj+xQp1GymBdetKgEKeo0oCkn+ICBeAW0IlFalWYffH5+BrOYzTTQDQe1ZKNzch7D6RsiflZJiVfo17IqPbKBkkA6eLz+LjbZ9j8cGVYBn01NRiw+rghR5Po2WNJqLM2nRyJyb88pooGXywMgQaHTuLpz9drIyyAGrZ7wDYF2/SEWhiBtiX3huh6BaXC1a6XvKmiwCg+8ePhJssJdsA0lhyQgoLbBhZF/++/TVZEv2wT/svrXwXxU713ktiNx1GdBjsWRHw50ohu7nw2IIM7L94ROGZ4+r8IVDjYhEy3//en6GaGsM+/bNVAN6kI8A+/bNVAL3KJqNPAAAgAElEQVQ3dwWadtoDWfZodREAJGWlzaSgw/TwILySOB7d68VL7srnuQswffMczVyN6xTT3rMK4mu642/3/Ix/rP8/yflxgfIQMDsr8JfX2bEd/bdVJUAp3waQZKJ1XgL4CkY0FLaETZAlfNR8AGCfnZYCSudK8lQFWEi7Wi3xz34vSmpFhbsCb63/GAv3/SqpXCWEsZf/5K6P45bYDl6pW7hvGd7Z8CnYVUbetEPgtTc+h8Wh/5J5vDCQdM+k3gsAXUaqKD5Hvuvsmg4Abv0suUGFwchOsUVJ92gFTtJ7/aeBFfqRql0sK/BkxNt5ZrdUIgMip0f9BDwZNxQsJ8K1WllFOd7e8H9YtF//h8kCMgEyK8384HvUuFAks5bAi2ef/leX8KRAYmeCvbS6hQJsFSAI2r74HDSTy0/NBgBTp04VljbLW0qAXnLBUVJuz/qd8FKvsZKpZNn6Rv/0Ik4Vn5VMZiAFseJHfRt3BzsjwQIBtjrAri5uPrkTW0/noMTJE64Hcn7E6H76s8VodFQfz2lVHFg+AJYXgDf/CbB7/+z+fzA0QrAqLhs95PJVswFAYlZqxv/K++riqDdLofvpna+jXkSMJPPscDnx7OKXeCY8SWhyIXITGP7lSrTLDY5Dm04KsLMAFeq6gCP3FEsm30iA7qGASbNvLp9RfBWfg4E+j/JygCYx2memJEAgrIKILnJA3d38Vozt/IiXU1Z1t1dWvY9fDq6quiPvwQmogMDtS7ehz+psFViijAkHHMA+fkzFL9hNzUDjILj6dxmcV+Nz8JxfsLwYpLkAoN/MYbZyQ8VmQtHCC/9U34UVyZl999uoHiLNMYY5u77Dv7f+R/V+cwM5gd8ItNx/AiPnLgsaIOwiwKpioJyvAvg05xb26d8GBMfWfyUaStE/IReLfALlQ2fNBQBJWakfUuAxH3xUddcH292Ph9tLk7l49dFNeG75W6pL8KPqCeDGBZyAxeHEK29+CUFliankBHPcCWTz+gA+IW5tAWJ1sebrtdsVFoJqbbMh2wlZTQUASbNS7qCE/OA1PpV3DDFa8cX9H4AV/RHbjhScwBM/TkGJs0ysKD6eE1CcwJhPfkL94+cV1xsohezD/9oSoJjnBfBqCmwC0CWUVcYNnkaA9XE5uEVOjzXDszLbX+kuAPXlBKKk7P5NeiG96xOSqExf+jrWHd8qiSwuhBNQmgArCcxKAwdTO+cCtvDLK15NeccQoIbmk7x75erlnd6Iz8Ekn0f5MEAzAYA9K+09gI72wTfVd32rzxR0jG4j2k5W0W/cz6+IlsMFcAKBItBmzzE8Mo+V8giuxg8EVj3fQXjwrxIKxV3xuZB1xVsTAUBS1pDuFG6W5UUT9lb9SAO1Q2vgP/f9069895fLZ5Xvnlj4HHafP+CNWt6HE1AlgZAyB15+6yuQIDoH8NtE7CwDTuo/EaJfz120EWgrfofUL90BHuQWLKjRcSsuymmH6l+oAxYMsJSej2Jr2zfJCUJp2UPa3oMRNw8WrfaXg6vxyqr3RMvhAjiBQBMY/9FCxJ6S9e9doF28pn52DGBjCVDAzwNcwSdCABJCg+vU/28AKLA1IQcd5X5gVR8A2LPSXgaobPcg5QZ8Pfkf3v4amldrJEo9y/P/4PfjcaLojCg5fDAnoAYC9y7ahJ4btJ222l+O7Erg+hJ+NfA3fuzKX+dQgH0PxkYo/hmXi2fl9l3VeHtlDWknwL1JLwl/fpvMCEsYvnlghujl/y9zf8R7m2bK/Yxw+ZyAIgRYNkCWFTBYG1sBYCsBwb4QwO75s0/+bAUgaBvFwPhcfCW3/6oNAC7l+l/DAkG5ISgtv1eDzpjWc4xotSMWZGDfhUOi5XABnIAaCISWOjD1H1/D4A7eVyA7C8DOBARzY3v+bO8/iJuznCC6WzZkvxer2gAgcXbKWELJW3p8CMZ0ehj3tOgryrWTxWeQ+o3sK0SibOSDOQFfCTz8+Qq03X3U12G66n/UCbCiQcGWKJC9jFiRn3rBleznqmeXAt8m5OBeJR5qVQYAvWYOaywIFTsA2JSAoLSOmXf9HfVFFv75Ku9HvLuRL/8rPXdcn7wE2ucewUNBvA3wG93zLmBHGcCKBwVDY8V92lmB6sF31/+q6SUUD8Tl4ksl5l2VAYA9K/VHAP2VAKC0jnBzGL5L/lC02nG/vIotJ1leJN44Af0QMLrcnm0Adi0w2FuJG9hWpv9sgSzL381WIDSY9/z/eNgvRDgR03wvFEkUrboAIGlWyt2UkG/1+svfpmZzvNd/mij3Ch3FuO+LJ+CiLlFy+GBOQI0EHli4AV0371WjaYrbxMoGs5UAljVQj41l92Of/FmZX948yX9mxOdCmvSwXgBVFfbkecnmMw7DLoA088J2TXaRIv3v4gMr8drqDzTjP6t50Lx6I7Ss3gQ2c0jA7b5QVoC8c/ux78JhON3OgNvDDbiSQKOjZ/H0Z4s5lksE2C7AnnLgsM4e1QYmoLlFR9ndJHhiBYruHXPBSt0r0lQVANhnp0wAJW8o4nmAlLDkPywJkJjGEv+wBEBqb02i6mNc50fRumZzEKKqR82DrsLtwvrjW/H2hk9wtkT2A7dqny5V2Zf5wfeocUG2Imiq8tVbY1gFwd0OgK0KaLmxT/stzEFX2c+bKdsXnwNFP/yq5q9yv5nDapcLFXsIEOENKa32Ydf/2DVAMe3Jn15Azln1LpEKREBam7vxULv7YRTUf5+n2FmC9zbOxI/7gy8XvZjnUM6x/ZfvQL8VO+VUoUnZDgqw+gHspoDW4gD2smEn/BubAbNq3jwqegwopsbnQtz+sI/uqGYakrJSP6TAYz7ar7nuUmQAHPT1Uzij4k+sw9sPxEPtBmpubl5e+S6WHFqjObv1aDD79M9WAXi7NoFSN7DXAZzSSA2BOkagmRkI4Qf9rvtIUwOaJezEPiWfeVUEAPbZaR0opZtIEKR9nnPPO4gJq+X3HFNK0Xfug6o9AMjSG39w28swCtq7z1NQXoThP0zEhbJ8v+eHD5SOADsHwM4D8HZ9AgUuYI8DuKDSQ4LVDEBzMxChvT8HSj92q+Nz0F1ppeoIAGalLgNBotLOB0IfSwEcaQn3WzV7Od3/5Si/x8s9UIoVDrltvJF8XlwpkPSv1M1uArAbAbxVTeBsBbDPARSqJIliuACwMr411b8DWDVcJXoQPBGfjRlKqLpcR8ADgKRZqQMpwRdKOx4ofYtSP4NJ8D/V1Z7zBzBy4ZRAmX9DvVHWCHw9cLoqbfPWKHbF8u7Pdb8T5S2OgPazljvx/Lvfgn3nzTsCLHfA6QrgjAvIV3hVINIA1DIAtY38Tr93s/V7rwKnE/W77EWBj+NEdw9oAFBZ6jcyByCNRXuiAQHsQNziVHHZ+9Yc24LMZeq8KHFLbAf8NWmSBmbixiamfTsGJ4pOa94PPTjwwLKN6Lpqjx5cUdwHdmDwDAsGKgCWWVDqxQG2nc8y99UyVn7xg31+T/Hr8TmY7PdoEQMDGgAkZqVmEOA1EfZraiirAvjtA+KyAP6wdwn+vu4jVfo9rO19eOTmZFXa5otR01a8g2WH1/kyhPeVgUDP8KN4NmQdDo93gGrksJsMGCQR6aLAWVflFgELDMrdlaWH2VdV6YZZml5Wlpd9sZe8RQDYEn9NA2AI6BtEEjQBFUKJULG910P3PTL9kx8CYUjApq/nvORaBodxP4CwQDgeCJ02Uyh+GCTu5b1o/wr8Zc2/AmF+lTrvb9kfTyc8VGU/tXf425rp/EpgACcpVHDi6ejNuC2K/XkADv0bOLcsgAbpXDVbGWABgScwuHS38PKXPT+4L98DcLhpgnt3j6HfTU4fc598Wq4vOWABgH1W2hsgdEIgnA6UTpYMZ0nabFHqN53ciQm/qHPRRIo0x6LgSDR46op38CtfAZCIpm9i2oeeQUbdNYg2Ff8+sOw4kM12lrR28d0313nvICNACcHPt44Gopu63XC3yswcv1tpBAEJAOyfJEfD5Pn0H/i8sAoTXzj4E1iNFr+1Hso/5rmqpsZmMZgxf/DHMBBt3/mZvPRvWH98mxoR69YmI3HjkVo7kFIzB+Qab/p9bwH5m3TrPncsCAkcj22FNZ0HwWoJgcVq/ffk9DEjlcYQkAAgMSvtHQL6jNLOqkHfl/d/gOohUX6bwrLW3TlvhN/j5R44sctI3N7ULrcaWeU/s2gadpzJk1UHF/4HgcaWfEypuxpNrRevi6V4N5CnaI40PkOcgLwEliaOwPlqdT1p0sPDIh0uShpMmTLmlLxar5SueABgzxpSD9S9FwT+fwxWkpDEumbd9XfUi4gRJXXAfx9GWYUi1SJ9tjPUFIJP7nwdtUNr+DxWLQMeW5CBvRcOqcUc3drB/vg8UCMXj9XeBhOp+oz67peAIh6X6fZ5CCbHztZoiF97Dv/dZbYKYDZbX0vPHKPoHe8ABABp/wKoYuUO1fZQvdtvKtrWaiHKrGHfjcPRwpOiZMg5OD66Lf6SNFFUvgM57atKttpTLVdlvxZ+XttUgvTYteho8/4DT/5mYN/fteAdt5ETuDGBVV3TcLJO8987sVWAsLCIwnKHJXbq1NGKVcFSNACwz01pBBdhBx38z4Sj8SdrUpfHMaCpuKSHY39+BVtPZauaRMPIusjoOgotazRRtZ1/Nq60ogy3//cRTdmsNWNvjTyIMTEbYRN8TPBDgezJQNkxrXnM7eUE/iCQH1EbP/e+Opur5yyA2TJ2cubYfyjFS9EAIDEr9WMCBPVfV1Yl77EOKaLm9/1Ns/BF7kJRMpQYzKoC3tuiL+Jj2qFl9SaoIeLsgxL2Mh1qzrSoFAO59IQbHBgXswH2iMN+qzi3HDikeMJUv83lAzmBqwhsiL8Ph+u3v+r/s1UAW1jESYejoP7UqVMVyXyhWABgnzW0GYgrB0BQZ4fuWb8TXuo1VtSvBfv0z1YBtNZYAMByIcjVutWLw+Md00SJ/+XgKryy6n1RMvjgqwkkhJ30LPnXMJaKwkNdwK7xgOOMKDF8MCcQEAJFtupYdOtoUHLt7AoWixVWi3Xo5Iyx4u6Le+mdYgFAUlbaTAo6zEu7dNutUWQ9zyE5Mc1FXbjvi1EodCi2VSTGXMXGvtjzWdgb3CJK3yfbP8fMHV+LksEH/0HAQlwYWWcr7qu+G1L9sbmwGjjAYzT+mGmQwLpOyThat/V1LWerAKHhYXunZEz444CAjH5K9Tt5QxPtc1Jvom7sCoZyv1XNFSsEtGDwx2B1AcS0v6z+FxYdWCFGhK7GWowWfDNwuqgcCwzIC8vfxoojvAKdFA9HC+t5TKm7Bg0sEtc4oUDuc0DJQSms5DI4AWUIsCt/7OpfVY2tAoRYbP0nZTyzqKq+Yn+uTAAwKzULBEPEGquX8e/0fQHta98kyp3lh9fjxRWKnRURZasSg3s16IxpPceIUkVBce8Xj6OgnK+siAEpgGJIzWw8WGsnWIIfOVrhLmCPOhNiyuEul6kDAst7DMeZmg2r9IStAljDbZuez5iYUGVnkR1kDwB6zU2pL7gIy/on7iOvSEfVNPyhdgMxvP1AUSax0+r3fP44nG4fT1KL0qrewS/0eBpJDbuKMpDd/Wc5AHjzn0CsuQiZddegTchZ/4V4OXLv34CC7V525t04gQASOBHdAqu7pHptAVsFMFtscRkZz2zxepAfHWUPAOxZqW8CGO+Hbbod0q5WS/yz34ui/Utf+jrWHd8qWo7WBbAUxN88MEP08v+8nPn412ZFzt5oHfk17b+z2j6MrrMZVkGRA8woPQzkZPIaAbp8mHTklCfnf+9RKAiv5bVXbBUgJNy28LmMibd7PciPjrIGAAOyhkSUwH2EABF+2KbbIUbBgO+TPxL9wtLqbQCpJ3bgTbfhqfgHRYvlAZV/CKsZyzAxZj26hit/Qf/gdOA8Pwrj38TxUYoQONiwIzZ1vNtnXRaLlZot1iYZGWNlO+0iawBgn50yAZS84bPnQTDgL/aJ6FK3o2hPM5a9gbXHZF0lEm2jnAJYYaW597yDKKu4GNPhcnr2/9nWCm/eE+gefhQTYtcjyhCY1NSOc0D2eIDvhHk/Z7yncgRcBiN+6vsMSq3hPislREBYeNh7GRnjn/Z5sJcDZAsA4meMNIXbCtnefz0vbQmqbn0adcNz3Z8S7fOBi0fw6IJ0UBqctVKHtr0Xj948SDTHZYfWYtrKf4qWEywCQoQKPB29CQOi2K94YNuxOcCp+YG1gWvnBK5FIK9FD+xs3cdvONbQUGeIVag2ceLEP+pj+y3t6oGyBQD2rNShAGZJaKuuRLF9668G/guseI7Y9vraD7Fw3zKxYjQ3Ptxsw9x735EkuVCwr6T4MvltQ88gM3YtYszquC3hKgZ2jgXYd944AbUQcJhD8GPfZ+E0+V/3zmAwIswWMWpyxrPT5fBLzgCAnU67WQ6j9SJzUpeRGCBB6dyzJecx9LtxKHc59ILGKz9YSmWWWllsu1hWgAe+Gg2WYIm36xNgV/qG19qBtJo5IFDXihNbAWArAbxxAmohsK1df+xt2kW0OZawkHMvTkmvKVrQNQTIEgDYZ6fdCkoXy2GwnmTeXLsV/tH3eUlc+mjbfzF757eSyNKCEFZsaMaAV8FWUsQ2VleB1Vfg7foEGlryPUl9mlsvqBITdQK7JgAO+W8fqtJ/bpS6CBTbqmFRn9FwCwbRhplMZlhDQvtkZIxdIlrYnwTIEwBkpf4IoL/UxupNHgHxpAVmLzOxjX36f2bRNOw+f0CsKNWPZwf/pt/2iiTc2NmJh+dPwqF85U+wqx404EnfO7B6Hh6rsw1mou4VkvxNwL63tECV26h3Aqu6pOFktHTZfE2RIZunpafHS81N8gCgV9aQdgLcPD2HlzPVvV48XkmUJk3CmZLzeOLH53C+9KKX2rXZbUr30bi1UXdJjP9p/3L8dY0s22uS2BdIIbVMJZ4CPnG2U4E0wyfd+94E8oP3UoxPrHhneQgcj7kJa24ZLKnwysRA1sZSXwmUPACwZ6V8ApDhknqvc2EsKRBLDiRFyz67F2MWv6zbDIF3Ne+DcZ0flQIV2NW/Yd+Nw+mSc5LI05OQPpGHMCZ6I8IM2jpXwqoEZk8C3NoyW0+PTlD74jKYPNX+SkIiJeXAEgOZwkM+m5oxWdJ3q6QBgP2T4VEwlR8HIP5ou6T41C2sTc3meK//NMmMZEWCWLEgvbXm1Rvj/f5TwQoqSdH+m/MDpm/mJ8cuZxlucGBMzEb0jjgkBeKAyDj5DXD884Co5kqDnAC78seu/snRLCEhLuquFjF16uMlUsmXNgDIShkNkPekMi6Y5LzUayx61u8kmcsztszBf7J/kExeoAU1rdYQb/bOEJ3w5zc/ihwlSPv2WRQ6+N2x35jE205icuw6sKV/LTdaAeSkA2UntOwFt11rBArDa+LnpFFwC4IsphsMBthCI0amZ475t1QKJA4AUtnuWwepjAsmOfUiYvDpna/DQMSfGmXc2OG219fOwI/7l2seI1sh+WvSZISZQyXz5cMtczE3+3vJ5GlZEDvcN7LONtxfPc9z6E8PjVcL1MMsasuH5T0ewpmajWQ12mwLOTv1uXTviwpUYY1kv+/2mSkJEAgvpC5i+sd2fgR3N79VhISrh7ICN9O3zNFspsD46LaeQ5Ls5L9UjR2WZHv/wZY34Vr82LU+dr2PXfPTWzvwHnBhjd684v6okcCReu2wPuF+2U27dCUwKSNjrCSZ3yQLABJnpcwghIyUnYCOFVQPicLsu9+W9GXHcLGKgS+vfA/FTm0t7bIbEi/2fEayPf/fHp1gzZx4+a+OAIrUmtkYXmsnWIIfPTbnRSB7AuAq1aN33Ce1EHAaLVh061Mos4YpYlJIuG3Z85mTkqRQJkkA0G/mMJtDqGA7br5XPJDCCx3JeLj9A3iwnfSR5OGC48hc9gaOFar/Shc75PfwzQ9gcKs7IBBp99PYff9H5k+Gm+rzpefNrwJL4ctS+bKUvnpvp38EjvIcT3qf5oD6t63dbdjb9BbFbGBVAsMjLDXHjRt3XqxSSQKApKyURyjIx2KN4eOBEKPVk+GufkSM5DjYgbdXV73vWRFQa2Mn/TO7jUKjSOlrSLFUvxN++QtYGeVgbbdH7cNT0ZvBivkEQ2NxXu4UoPRwMHjLfVSawMXIaCyxjwQlkrxKvTJfEFiVwIgn09PHir7qJYnV9qyUNQARn/TYK/f134kdCPxX/5clPfR2OTVWPnjGlrk4mH9UNTCNggGssh/7kuog5J+d++fGT/F13iLV+KykIaxc78TYdegWHnwZD4v3AHnslq26yhcoOf1cl0wElvV6FOeqS/9hpSpzTWHW49OmZIhOISs6ALDPHNwWgrCjKoP5z30jkBDTHn9LmiT5EvhvVrAlcHZD4P+2fY5zpYHL784SXLC9/uHtBoJd9ZOrfb/nF7y1PjgXqdhLf2LMekQZy+TCq3q5R2YCZ35SvZncQA0R2NekM7a2HxAQi81mC0JtthaTJj27R4wBogOAxKy0dwjoM2KM4GOvTWDgTbfhqfgHZcVTXlGOL3J/xJzs71DiVO60FCvi079JLyS3uh31wqNl9ZEt+U9c8hdUuNWdy15qCGyZ/8k6m3FntX1Si9acPJYZMDeT5wbQ3MSp1ODCsBr4JekJuAzGgFjIPjiZw0PfeTFj0hgxBogKAOyfDLdSU/kxAlQXYwQfe30CE7uMxO0SlAyuijFLjLP62CasOroJG45vR2mFPJ8Wa4VWx+1Nk3Bvy76IskRUZZbon58oOu2pj1BQro7a9aId8lJAm5CzyKy7BrHm4PL7RniK9wG7pwG86rOXDxHvdk0ClAhY2utRXKgWG1BC5lBr2YvPpYcSQvze3BIVACTOTksmlM4LKAWdKzcKRrx16xTJagV4g8vpdmLzyV1YeWQj1hzbjHMiigvZTKHoUKcV4qPbIT6mLRpEKPdLw1Y0nvzphaCq9Meu9D1UayfSamaDXfXj7UoCJ74ETnzFqXAC/hPIuSkR2TfZ/Rcg0UiWEyAk1NYzPX3MSn9FigoA7LNTvwDFQH+V83HeEWCflKcPeAV1bDW9GyBhLwqKAxeP4FTxOZwtOY+zpRc831lQwBLqXCjL99xcqBYSierWSFT77SskEi2qNULLGk1kO8dwIzdZJsTMX98EO/AYLK2hpcDzqb+FVfTtIN0iY5/+814ESvRfNVu3cxhIxy5ExWJp4qNgqwCBbqycvCnSMn9qesad/tridwBgn5ccBofxNC/84y9638axA3Lv9ZsqeZIg36zQTm9W5IcV+wmGxn6J76u+GyPrbIWFBNc5B3/mt+xY5dVAt9Of0XxMsBJg+/2/2B8Hy/mvlsYKBFWLCrU988wz5f7Y5HcAkJSVkkZBZvujlI/xj0D72jeBFQ2KtPB8S9cjyFYsPtn2BWbt/No/yBobVdNYisl11yLBdlJjlgfWXJ4gKLD8tahd6YQ/3jAyGo2whYQlT84c+4U3/f/cx+8AIDEr9VsC3O2PUj7GfwIxYbXwauIENI6q778QnY5kBxdfW/2B5+xCMLSkiMMYG7MBrIQvbz4SoMCe14DC4M0J5SOw4O5+ulZjrOgu740sfwmbw0M3Ts2c7FcpWb8CgFvnJUdWlBtPgUC6Ci3+eh+E49ie+3PdR6Nbvfgg9P7aLp8sPoMpy/6O/Rf1n/ItzODAs9GbcGvkQT7/Igg4zgE5k3mtABEIg2Ko02TF4t6jUBoi/60lf4BarSE01GasPWHChLO+jvcrALBnpT4E4FNflfH+0hFgB0Ae7TAIQ9rcI51QjUrafjoXLy7/By6WF2jUA+/N7mg7hfTYtaht0lZhJ+89VLbnuRXAoenK6uTatEVgQ/x9OFy/vWqNNhgMsIWFP5WePvZ9X430MwBIWwDQwKRA8tVDnffv06gbJnV5HGaDSeeeXtu9H/YuwTsbPtF9kh8TceOx2lvxQI08+PVLG5RPh3dO738buBgcu0beAeG9fidwLLY11nZOVj0RU1hIzrQp6a19NdTnvyX95yVXL3cY2Ymj4Hzj+EpYgf7sqt2rieNRI6SaAtrUoYKlMn5/0yx8laf//K7NrBcwpe4aNLLkqwO+zqyoKACyJwPsO2+cwG8EWHnfxb2fhMMconooFosV1WCLfGbqMz49xT4HAPZZqSNA8G/VEwkyA2uERCG96ygkxLTTvedsv//Ntf/GppM7de0rAUVKzRw8UmsHWIIf3uQjkL8Z2Pd3+eRzydojsKprGk7Waa4JwwXBgIiwiEGTMsZ87ovBvgcAs1MXgaKvL0p4X+UIsCJCj3dMRTMZC+so582VmgodRZi18xt8k7cYLFuhnluMqQgZddeiXegZPbupKt8OfQic+1VVJnFjAkTgQKN4bO7gd36dgFhtCLesezkz06eqvD4FAD3nJdcyOIwnABgC4iFX6hUBdkDw1sbd8ejNgwKSPdArI33o5HA5PUv9s3d9A1azQO9tQNR+PBW9GaGCvoMcNc1jcXkEFm5KRsxnXyOkiGdSVNPcKG1Lsa0afu49ChUaO1dltlrdrVs1NQ8aNMjrbGA+BQBJWSmPUJDgrKmq9FMogT6TYMJ9LfthaNt7EG4Ok0CisiJYOt/FB1bi4+2f43SxzzdclDVWAm2RhnKMj12PnuFHJZDGRXhLYP+Z1liwMw0ljjBUO7UXcYveB6G8joK3/PTUjxKCX3s+jHPVtZdnxWg0IdQWlpiePma5t3PiUwBgz0qZBxD1H4n01vsg6RdmDvVcF7y/5W2auS2w4cR2zNgyF/suHAqKWeoSdhyTYtehmlGeKoxBAdFHJ11uI5btvgubDiVeMbLFxm/QIHuZj9J4dz0QyGvRAztb99GsK8Yoy9yXJmemeeuA1wFA8rxkwxmHkX0Mi/JWOO+nLgK1Q2sgudXtuLVRd0RZ1ZfUosLtwrrjWz3L/Zt1fsDvtyfDKiH+D88AACAASURBVFTgyTpbcFe1vep6WHRuzbniOvh+24M4XVj3Kk8FVwVumf8mbBd5emWdPwZXuJcfWQdLEh+DW9DuDrcp1Foy7fkMm7fz5nUAkJQ1pDuF2++yg94axPvJT8BADOgc2x79mvRC93pxYFsFgWx55/Zj0YEV+OXgauSXFwbSFEV1tw45i8y6a1HXHDw+Kwr4Osq2He2GJbn3wukyX9ec8PNH0XnB2yBur7dT1eAat8FPAuylv8Q+EvkRtf2UoI5hZrMFZoulZWbm+N3eWOR1AGDPSn0FwBRvhPI+2iHAtgc6x9yMjtFt0KFOa9QLj5bd+EJHMbadysGWU9nYcGIbjhSwc6XB0wyE4sGaOzG01i4I4HvNSs18mTMUP+5Kwe5T3mV1a7x9EZpuXaCUeVxPAAnsaNMXu5t3C6AF0qgWBAGh4eEZmenj/uqNRF8CAJYriyef94aqhvvUCq2OjnXagCUXahARiwYRMahlqwF2s8Cfxl72hwuO43D+cU+efvbi33vxENgBv2Bs9c0FnqQ+LUP4SXMl5//Ihab4YfswFJZ5v4NJqBsJC99B5NngOIei5HyoSdfZGg2wvMdwsAOAemimcOvhaZkZDb3xxSuP+80cVtshVLANMa/6e6OY99EOAYvRggbhMYgOqwWbKQShl32FGC1g1/RKnGUocZaipKLU8+9zpRc8L/1gyM/v7UzeW30PnqizBRbCl5W9ZSa2n5sKWL2vP9bs7wdKff/zFVpwBrf88AYMFbzioti5UOP4CqPZc+WvONT7wFCNflxuk8USQsMjzDXHjRtX5acMr34jkmalPUgJ/UztjnP7OAE1EqhhLMXk2HXoFBZcWx2Bnov80ur4fvuDOH6xkShT6u1ehZvW+pRgTZQ+Plg5Ahvj7sGhBh2UU6iAJqPBiNCw8GHp6WOyqlLnXQCQlTqHAqlVCeM/5wQ4gSsJJEYcwfiY9Qg38E+QSj4bOSfisCh7EMorrJKobbtiFqIPbJJEFheiDgIHG3TApjh9VlO1RoUueGHy5DuqIl1lADB16lRhWbO80wBqVCWM/5wT4AQqCdgEJ56J2Yh+kQc5EgUJOFwW/JwzEDuPdZZUK9sC6LTgbYRd5Ks4koINkLCLkdFY1utRuAzGAFkgr1pzqLV06vMZoVVpqTIASJqZcgsVyNqqBPGfcwKcQCWBDrbTyIhdg9om/actVtOcnyyo77nbf6GklixmsfMAnef/HUYnT9YkC2CFhDpNVvxiHwmW8levzWwyI9xsbTD+ufFHbuRjlQGAfVba1P/lxXxRr6C4X5yAVARMxI0RtbchuUYeWCU/3pQiQLD+QBKW77kDbipvEpfah7ej/bL/U8oxrkdyAgSru6TgRHQLySWrSSAhBGHh4Q9nZIz/VFwAkJWyEiDd1eQct4UTUBuBJtaLnut9TSwX1Waaru1hRXzm7xiCg+daKuZn803foeGuJYrp44qkI5Dbsid2teotnUA1Swo3bnwt8/lOfgcAyfOSzWfKjQUgsKjZT24bJxAoAuyT/uAauXi09nYYiTtQZgSl3n1nWmPhpSI+SgJg+QHiFn+Aaid5+mYluYvVdbpWE6zsNlQ39/2r4mEMMZe/9MKUG56CveEWQOKc1K7EjdVVKeI/5wSCkUAdU7EnlW/7UHZGljelCFQW8bkbmw71UkrlVXrMZYW45Yc3YSnJD5gNXLH3BEpDIvBL0uMoN1d5Ls57oSrvaTKZEWqLqDt58tPHr2fqDQMA++yUCaDkDZX7yc3jBBQn0D/qAJ6J3oRQwam47mBWeK4oGt9tfxBnCmMDjiHq9AHEL3qP1wsI+Ezc2ACW55+V+D1f7erCTyo3XZR5LC1wRFhE2qSMsXP9DABSvwbFvaKs4IM5AR0RiDCUY3zMBvSKuOHhWh15rB5Xth7phiV596HCFdjiVZcTaZDzK1ps+Fo9kLglVxHYevPt2Nf4hlvhuqVmiLD++HJGxgC/AoDErNRTBNB2eSTdTi13TGkCt4SdwMTYdWCZ/XhTjgAr4rNwVwr2eFnERznLKjW1W/4Z6hzcorRars8LAofrt8OG+Pu96KnPLqZQS9G05zPDfQ4Aes1Oay5Q6lVJQX2i415xApUELIILo+pswT3V9nAkChM4cr4Zftgx1KciPgqbCENFOTrPfxu2fFYuhTe1ECiIqI0liSPgMqhnxUhpNhazFUZzSPSUKWNOXUv3dc8A2GenDQelnyhtMNfHCaiJwE0h5zzX++qZC9Vklu5tYUV8Vu0dgLUHbvWriI/SgGz5p9B5wVswOMuVVs31XYNAhcmCXxIfQ1FYcCewNRiMCLeFD5qUMeaaxSyuGwAkZaV+SIHH+NPFCQQjAQOhGFpzF4bV3An2b96UI5BfWgPfbx8muoiPchZXaqp9aBva/8o/MynN/Vr6NnYbgkO1m6nBlADbQBASYZv5fMbEh3xaAUjMSt1FgNYBtp6r5wQUJ8A+7bNP/ezTP2/KEmBFfH7KHgSHREV8lLUeaLHxGzTIXqa0Wq7vMgKH2vTGrva3obS0mHMBYLJZz057LuOa+bGvuQLQY3ZaNSOl7K9flamCOWFOQE8E2D4/2+9n+/68KUfAU8QneyB2Hpe2iI9yHlRqYkmC4n96D1Gn9yutmusDcKFOM2zu9yQqKEVRUQFnAsBqDaFuWmadOnXqVSVJr/mCT5qVcgcl5AdOjxMIFgLVjWWYFLsW7KQ/b8oSqCzi8xAulNRUVrFM2sylBejyw5tg33lTjkB5SATW3TURDmvlofeCwouglG/fsYRA1pDwuIyMZ666qnLNAMCelfoKgCnKTR3XxAkEjkDPiCOYELMB7I4/b0oSIFh3oDdW7Lld9iI+SnrFdLEVALYSwFYEeJOfACUCNvV/ChdrN/ldWVFxIVyuCvmVq1yDQATYwiMey8gY+9GfTb1eAMA+/d+hcr+4eZyAKAIsix/L5sey+vGmLIEiTxGfoTh0Tr9V2dhZAHYmgDf5CexOuBeHW9uvUFRaVgKHgwf1DIoQblr0SuZz/b0NAA4DqC//tHENnEBgCLD8/Rl11yLaxA8KKT0D+860wYKdaSh12JRWrbg+diuA3Q7gTT4Cpxp2wI7E4VcpcDgd/CDgJSqGUNP5l59/7qo7kVetANg/GR4FU/kF+aaLS+YEAkeAVexjlftYBT9WyY835QhUuE1Ylnc3Nh/uqZzSAGtieQFYfgCWJ4A36QkUR9bB+jvGwWW8umCty+VCUTE/h8Gomy1m+uKLmQZCrrzTfFUAkDgrpSchZLn0U8UlcgKBJdDYko/n6q5GE+vFwBoShNori/g8hDOFMUHnPcsQ2HnB2zxJkMQz7zJZsP72sSiOjL6u5PwC9rvOA32j0QhrSGjLzMzxV2T3vXoFICtlNEDek3iuuDhOIGAE2EOeXCMXI2pvg4nwQ1lKT8TWI92xJO9eVRXxUZpBzWPZuHnJR/xQoETg2aG/bb1H4GzdG6eq4QcBK4Gzg4BhEVGD09OfnXf5FFxrBWAGIWSkRPPExXACASVQ21SCjNg16GA7HVA7glG5p4jPzlTsOd0uGN2/ymdeOVC6x2B3p/twuFVilQL5QcA/EFkjbNNfyJg06oYBgD0rZQ1AulRJlnfgBFROoG/kQTwbsxE2walyS/Vn3mFPEZ9hKCqL1J9zIjxqtXYe6u5eLUICH3qsRTfkdBnkFQiHsxylpSVe9dV7J2OYZf9LUzKbXj8AoCD22ans1ESY3mFw//RLINzgwLiYDbBHsMssvClJgBXxWbl3ANZppIiPkmyYLpYXoOPif6H6SV5Z0h/256ObY0vfUWBbAN40fhDwD0qWEKvzxRcyzNcNAHr/Z3BTd4Ww1xuwvA8noEYCncJOYHLsOtQwlqrRPF3bdJEV8dn2IE7kN9S1n2KdMzlK0GnB2wgtOCNWVFCNL4mohQ23j4XTHOqT3/kF/FIbA2axWGENCas7efLTx38DeMUZgMSslPsIyFc+0eWdOQEVELAQF56oswX3VuefrAIxHdkn4rEoO1mzRXyUZsZe/p0Wvg1TOV+e9oa90xKKDQPGggUBvrbCony43fzwr8loQojNdmd6+tj51wwAkrJSX6DANF8B8/6cQCAJtAw576neV9/M7/wqPQ+OCgsW5zyAXcc7Ka1a8/qqndyDuJ+ng7h54akbTSYVDNh86xO4EN3crzkvLilERQVPCSwIBoTZwsenZ45965oBgH126hegGOgXZT6IE1CYgACKobV24cGaO2G4Mr+FwpYEp7oT+Q3w/fYHcVEnRXwCMYt196xFqzX/CYRqzejM6ZqCY839P5fObwL8MdXmyJAvp6anP3CdLYDUXQS48cVKzTw23FA9E6hrLkRm3bVoHXJWz26q0jdKCdYf1GcRn0AAZ/UCWN0A3q4mwPL7szz/Ylq5owxlZfxMEGNIwi0HX83MbHydACCtmID6dsJCzMzwsZyAHwTurLYXo+tsgVXgy3p+4BM1pKg8EvN3DNF1ER9RgPwYTCjFzUs/Qs2ju/wYrd8hZ+u1wbakEaDkmjXrvHbcWeFESUmR1/313NEcaimd+nzm7+/438n2mzmstkOo4Amr9Tz7GvetmrEMk2LXoUvY74dYNe6Rtszfe6YNFgZJER+lZ8ZQUY5OC/+BsAsnlFatSn1F1WKwYcCYa+b499Vgl9uFoiJ+Pohxs1istFXrpqZBgwZ5Dp78HgD0np3W2U3pOl/h8v6cgBIEeoQfxfjY9Ygy8PKeSvC+XEdlEZ97sPlwD6VVB5U+a/F5dJ7/NsxlhUHl95+ddVjDsf6OsSizVZeIA0VlTQDezCYzbKaIJhOff9pTA/33AMCelTIYIPw0Cn9GVEUgVHDiqejNGBC1X1V2BYsxZ1kRn20P4WxR8BXxCcQcR545iPhF70NwBWf2SrfBhE39RiO/ViNJ8fOrgJU4DQYjImy2vhMzxv18ZQAwO20yKP2rpNS5ME5ABIF2oWeQUXctYkx8/04ERr+HbjncA0vz7gFbAeBNOQLRBzah7YpZyilUkaadPYfhZON4yS3iVwErkRJCEB4R9UR6+pgZf1oBSJ0O4HHJyXOBnICPBIzEjYdr7UBqzRwQXsrTR3riu5c6bfhxZwov4iMepd8Smm5diMbbf/J7vBYHHmjfH/s6DJDFdH4V8A+sIeFhHz+fOXHEFQFAYlbaTwS0nyz0uVBOwEsCjSz5nqQ+zaw8faeXyCTtdvh8c/ywYygv4iMpVX+EUbRbPhN1Dm7xZ7Dmxpxq1BE7ej14+a60pD7wq4B/4DTarNteei6jw5UBwOzUPELRQlLqXBgn4CUBdhjlgRp5GFF7G8yEZ0bzEptk3SqL+NyOdQf6gN3z5y3wBNg5gISf3kXEWX0XtSqo2QAb+z8Ntv8vV+NXAf8gaw61Xpj6fIbnhGXlbzqrApiVWgoCi1wTwOVyAtcjUNtUgvTYteho47dQA/GUVBbxeQgssx9v6iJgKS1ApwVvwVqsz1PsZbYobLh9HMpDImQFz68C/oHXGhLifuGFdMPvAUDfuSmxThc5JusMcOGcwDUI9Ik8hDHRGxFmcHA+ASCw63gCFuewIj489g8Afq9U2vJPIuHHf+qucBAr8LPxtmdQHBntFQcxnSilKCjUZxDlKxerJQQGkzV6ypQxpzwrAElZQ7pTuFf6Koj35wT8JRBucGBszAYkReh7edNfPnKPqyzikwwWAPCmfgLsemDc4g9gqNBHoOwymrG575OSX/e70UzyssCVdMxmC2yW0C4TM8es8wQA9tlpQ0Bplvp/DbiFeiCQYDuJyXXXoqaR5+cOxHx6ivhsewhs6Z837RCoeSwbNy/5CIRqu7QtJQK29R6Bs3WVLTvDcwFUPuusLHBoSNg9kzPHfFcZAGSljgfwpnZ+FbilWiRgIS6MrLMV91Xf/UcGKi06olGb2eE+dsiPHfZjh/540x6BmH0b0GbVHM/BLW02gl3d03CiqfLlo4uKC+By8QPGLBlQWGj4iMmZYz7+LQD4C4B0bT5Q3GotEGhuvYApdVejoYXn5A7EfLEiPj9sHwp2zY83bRNomL0UzTd+q0kn9iTcg0OtkwJie3FJESoqgjPD4uXABUFAWHhkRnr6mL9eOgOQ+iEFHgvIrHCluiYggCKtZjYeqrUTLMEPb8oT2HO6nSexD0vww5s+CDTf9B0a7lqiKWcOtemNPfF3B8zmktJiOJ36OEMhFqItMuxfU9InPukJABKzUr4kIPeLFcrHcwKXE4g1FyEzdg3ahJ7lYAJAgKXwZal8WUpf3vRGgKLNqrmI2bdeE46daNoZu7qnypboxxsIZWWlYAmBeANMkSE/T0tP71u5BTArdRkIEjkYTkAqAndE7cPo6M0IESqkEsnl+ECAFe+pLOIj/xUrH8ziXSUkwA4D3rz0I9Q8mi2hVOlFna3XGtuSRoAd/gtk49kA/6BvjLDmvZSRcdNvZwB2AGgbyMnhuvVBIMpYhokx69EtnKeVCNSMsrK9rHwvL+ITqBlQTi/LFhi/6ANEnvFUd1Vdy6/VGJv6PSlrlj9vnXY4HSgtLfa2u677GW3msy89N6XWbwHAcQC83qeup1x+59hLn738WRDAm/IESh02LNyVir2neSyvPP3AaTQ5SjyJgmwXTwbOiGtoLo6K9iT6cZpDVWEXOwDIDgLyBphDrGVTX8gIuXQGILWcAGYOhhPwhwBb5mfL/WzZn7fAEDh0vjnmbx8Kdtqft+AjYCnJR6eF/4C1WB1FtMps1bBhwBiUh6rneXS5KlBUXBh8D8c1PLZYre4XX8wwEPu85DA4jJwKfyz8IsAO+E2JXYMYM4+s/QIocpCbGrBiz+1Yf7A3L+IjkqXWh4cWnEanhe/AVB7YZW6nxXYpxW8dVSF1u91gyYB4AyxmKyipbiP2uSmN4CLq3EDiM6VaAuxK3/BaO5FaMxvsqh9vyhO4WFIT329/kBfxUR69ajWyyoHxi94LWMpgluJ3U7+nwCr8qa3xegB/zIjJZEa4ObIRSZqdFk8p3ai2yeL2qJcAS+bDkvqw5D68BYbAruOdsDjnAV7EJzD4Va21xvFcdPj/9s4Dvqoi++O/ufe+lvdeEiD0KgIiItaVVbquvYsFdNft6+66oqK0hPKkqLu6dtelt1Ck2HuvdEEUqVJDTSXJ6+3+//MCS1Agr9925vPxE3Yzc+ac75mXe96dmXM+mQoWzW7WO1kQ8e2lf0ZFq66q5cMLAvFAwOgtlg7YkfMLdmnxHVdEIbxvdCBkf8ME+IERnsb3nubfwsyy+8elYe2M0SMYtuKDjbdh44ELjGEwWZkUgRY7v0H3L3l5l2w97Bg29Pk1Dp6m7nVJ9QDqlpMkmXg64KtZv7mDBzMGnlyaGhE4KQFeuGdk6xW4wK6uk8ZGctmB6vZ4c/3dVMTHSE5PwdZ2mz5Hl9WvpiAh/qFbf3Ez9pyp/lQyte4aRLP8ZiR+itnrKUm8HoDjTtZ/7uA/gWFq9qammbRG4NLc3Xig5RrwEr7Usk+grojPr/DVj1dTEZ/s49f0jJ3WvYUO33+UURt2nf0r/HjedRmdI13CqSBQHUleEMhpd/ye9S8edC/AXkgXYJKjHwIOMYgHWqzBZXm79WOUxixx+/Pw1ve/wZ7KThrTnNRVC4Fuyxai1Y8rMqLO/k6/xMZLBmVEdiaE8muA/Dqg0ZsoirA7cv/K+s0b9CCT2VNGB0L2H0/gfPshjGy1Ak1NXkKjEIEfS3vgnQ2D4A+pI5GKQhho2hQJ8JTBPT6biaYlPOFr+lpZ27PxXf/fK57iNxGLPJ5ahCkAgCCIcNpz72f9iwfzMsC8HDA1IhA73Pfn5usxsPEWxLJEUcs+AcEGtH4K7+0+A999+F3256cZdUeApww+/8OXkF+6Iy22HW7WEWsv/5sqUvwmYhCVBK6jxUsCOx15w1n/eYPGQWauRCBSX30S4Nf6ilovR3sLJctQzMO2s4EOCwDrWbHrSjMXz0f5DqqmqJg/dDSxFPThwvefh6OKZ35PvrkbtcKaK+9D2GxLXohCIykAOBIAMAG5uXlj+BbAJCazQoX8QdOqgACDjMEFm/D7pt+DJ/ihphCBpv8AWj0BCNb/KVDuqcLcaQsR8tEBTIW8oqtpLb4aXPjuM7C5K5Oyy+dojDU8xa8tN6nxSg/y+twIhUJKq6H4/IwxOB35E/kWwJMAHlJcI1JAEQItTW6Mar0CZ+eUKTI/Tcov5RYA7WYCeSc+Sb1mx3p8sugzQkUE0kIgp6YMF773LMz+xNJ3B60OrLnqfnhzm6ZFDyWEeH0ehEIUTMcCgNy8J/kWwPOQ2T+UcAbNqSyBq/N34B8t1iJHoIhYMU84fwW0nwOYTl2Mc8nHb2LH6vTs3ypmK02sGgK8cuDZX86Go+pAXDq5G7XE931+C17hT8uNlwPmZYGpAY68/JdYv7mDJjPG/kJAjEMgXwzgoVar0Nu51zhGq81SZgJaTgSaDwPiOG7pDwcwY1Yx3OWJfWtTm9mkj3oICJEwTv/2HbTb+CnYSdLjyoxhT7cB2H7uNYiKknqUT1ITn9+LYDCQ5Gh9DcvJdc7lWwCzAPxWX6aRNScjcLFzH4a1XIVGkp8gKUXA0qnuoF/OhQlpsLOiBEunvwZe1YwaEUgXAWflXjTZvwW5FXvgrKj7UlDbpA1qmrSN5fWvbdwmXVMpLsfv9yJAAUDMD9Zc++s8E+ACMGgnk4PiS0ibCliFMO5tvg7XNfpRmwboRevGdwNtXwQER1IWfbT2C6z9YF1SY2kQETA6Ab/fh0CQvvzwdWBx2j9m/YoHLWVgtxh9YejZ/m62chS2XoHW5lo9m6lu28RcoO1/gUaDU9JThozZi19G6fZDKcmhwUTAiAT8AR8CAQoAYgFAbs5yvgXwFoBrjbgY9G6zyGT8tun3uKtgI4SsVQXTO9Uk7LP/EugwHzCflsTgnw+p9B7G3GkLEPDSYaa0ACUhhiHAH/48CKAGmJ229RQA6HQltLPUoLDVcpxhS+6+r06xZNksAWgxCmjhAlh6D1Ct27UBHy78OMv20HREQNsEKAA45r9YAEBbANpe0D/VnqfvvanxVtzT/FtYWERfxmnJGlMboEMx4MhcidRXPnkbP66iMx1aWhakq7IEaAvgGH9Lrm0ZHQJUdj2mdfYmki9WwOdCx8G0yiVhCRLIvxloNw0QGyc4MLHuwUgQM2bNQ01ZTWIDqTcRMCgBCgCOOd7qtH9E1wB18kHon7sHQ1uuhlOkfWHFXBor4vM0UHBP1lTYXbkPS6a/ikiE3vZkDTpNpFkCdA2wXgCQa3+VEgFpdinXKW4XQri/5RpcnrdL45ZoXH1bjyNFfLpl3ZBP1y/D6ndXZ31empAIaI0AJQI65rGcXOdsSgWstRVcT9/z7Idir/ybmbwatkIHqje9D2j9BMAsihjDrwYWL1mMAz/Gl9ZVESVpUiKgAgI+nxfBEGUC5K5w5Oa9QMWAVLAoE1XBxKL4c7P1uLXJ5jiSyCYqnfrHTUBqCrSfCeQqf4v2sK8mVjXQ56ErTnH7jzoajgAVA6pzOS8GlOts9BiVA9bYR+B062EUtV6G0yzVGtNcZ+o6Lwfaz26wiE82rf5u9ya8t+CDbE5JcxEBTRGgAOC4AMDFtwDGQWYuTXnRgMoyyLijyWb8sdl3kBjlgldsCfAiPq0mAc0ejquIT7b1fOPT97B55ZZsT0vzEQFNEPB63QiFqfqpIAhwOvJG8i2Akf+fFfAxTXjPoEq2MHkwqvVy9MgpMygBlZht6XykiM8FKlHo52oEIyHMnjMfVYcOq1ZHUowIKEXA43UjTAEAeACQ68x/gG8BPMhk9pRSDqF5T03gqvwduK/FWuQIFLUqulYa/w5o+3zSRXyyqXtJ1X4snv4KwmG6GphN7jSX+gl4vLUIh8PqVzTDGoqCCIcj72+sf/GgewH2QobnI/EJEsgTA3io5Wr0yS1JcCR1TysBMe9IER9tFcz84rsVWPHOyrSiIGFEQOsE3J5aRCIUAIiiCKfd+XueCfBPYJiqdcfqSf+ejv0Y3molGktUtUpRv9ovPlLEp4OiaiQ7+fxXl2Dvln3JDqdxREB3BCgAqHOpJEpw2B13sn5zBw9mDPN152kNGmQRIvh787W4oRHld1fWfbyITyHQYlzai/hk064afy3mTF0Ir4fyRGSTO82lXgJudw0iUdoakyQTnDnOW9ilxXdcEYXwvnpdZgzNzrRVoLD1crQx1xrDYLVaaW4LtOdFfPqqVcOE9PqhZCvenvduQmOoMxHQK4Ga2mrIMt2i4gFAjt1+DRsw784LZFleo1eHq90ukcn4TcEG/LrgB/B/U1OQQP4tR4r4NFJQifRP/fbnH+KH5RvTL5gkEgGNEaiuqdKYxplR12Qyw2rLuYz1XzCoAyJsZ2amIamnIsC/7fOkPl1tlQRKSQJCzpEiPn9RUouMzR2OhjF7zgJUHKR1ljHIJFj1BGRZRk0tXY/ljuIBgC3HeS7rv+g2B4ISvXfO8vK9sdE2/K35OvB9f2oKErCdc6SIz5kKKpH5qfcdPohF05ciFKIT0JmnTTOokUA0GkWtmzKoct+YzRaYzDktGP8f/YoHBxhgVqPT9KZTE8kXO+F/kYMKtyju26b3A63/qVgRn2zbv2zDanz11rJsT0vzEQFVEODX//gtAGqAxWKTZfilWADQv3jwfgAtCUxmCfTNLYnd7c8VqRpVZkk3ID1WxGcWkHuNomooMfnLr72K3Zv3KDE1zUkEFCXAMwDyTIDUAIvNGhw3dpTlaADwPYDuBCYzBHgWv/tbfoMr8uioRWYIJyDVecWRIj4tEhikn661AQ/mTJ0Pj5uuBurHq2RJPARCoSB4MSBqgMluqXxkdGGTugBg7uDPwNCPwKSfwDk5pRjVegWam2jhpZ9uAhKZ+UgRn4dUWcQnAUtS7rp53494Y+7bKcshAURASwQCcwsOQgAAIABJREFUwQD8fgp8uc8kp2Xr+MLCM46cARi0lIHdoiVnql1XXrGPV+7jFfx4JT9qyhHYFzgNls5TUdDkMuWUUNnM7335Cb77mr/4o0YEjEHAH/AhEKDsqtzbZqftQ1fhyCtiAcCA4sFTZODPxlgGmbeyo+UwilovR0crXTnJPO1Tz/BO+e14Zs8EnN4sgBeu6waRiUqrpIr5w9EI5s5diLID5arQh5QgApkm4PN7EQzS+SvO2Zqb+9zYUQ/df/QMAC8HzMsCU0uBAP+mf3uTLfhjs/UwMco2lQLKlId6Ik48sfuf+KTy+v/J+t2FZfjDeeelLFsvAg5Wl2LBtCUIhajSpF58SnacnADf/+fnAIzeeClgpz3v/hGFDzx3NADgG6NPGh1MKvbzPX6+18/3/KkpS2CD+0KM3/E8DgbbHKeIwKJ44QYZ3Zu1V1ZBFc2+cuNafP7GlyrSiFQhApkhQKWA67iKogS7I/eOkSPvX1QXAMy78y7IcnFmsOtf6hV5u3B/yzXgp/2pKUcgKouYc+A+zDrwAPi/T9Ra5How65Z2yDHZlFNUZTMveeMN7NhIN1RU5hZSJ80EqBBQHdC6LID2fiNHPvDFkTMAd/WSEf0qzbx1L47f5x/acjX65Zbo3la1G1gabBX71v+d+6IGVb3ijFKM7nt+g/2M0sEd8GLu9IWoraEkKUbxuRHt5GmAeTpgozeeBdBssZxRWPjQ1lgAcPmCQa1CEUaFwxNYGTyTH8/oxzP7UVOWwOdV1+Bfu/6F2khe3IqMvawWv+qo7/S/ccMAsHX/Drw+9y36A5kINOqrGQJUB+CYq6wWG/KRkzfENaQmFgBAButfPNgHBotmPKqQojx3P8/hz3P5U1OWgD9qw/MlLrxZdmfCitgtQcy8JQ8tHE0SHqvXAR9+/TnWffmtXs0juwxMgNIA1wsAbDnRsWNHxPZI6wIAXg9g3uAtTEYXA6+RBk3nVfsKWy9HW3NNg32pQ2YJbPOehUd2vIA9/k5JT9SjZSWeu7Y7BCYkLUNPAyNyFMXFL+PQPjrIqie/ki2Inf6nLIB1K8Fit7nHjR7pPD4AKL7zfQb5ClosPycgQMavm/6Auws2QGS0h6TkGpHBsOTQH/HfvaMQklOvX/Wni8px9znnKmmSquYurSnH/GmLEQzSdSlVOYaUSYlAIOiH30/btbEAwJGzfVzRiNg3p/+9AehfPPi/AO5JibIOB7cx18a+9Z9pq9ChddoyqSpcgMd2PoUV1QPSprgoRPGfGxnOLGibNplaF7Rm03p88vpnWjeD9CcC/yNASYCOLQa707GkqHDYbccHAPPuHAFZfpzWzDECNzT6MbbfbxWohrrS62JVTT9M2vkMqkIFaVeldV4tZtxyGmySNe2ytSrw1bfewrYN27WqPulNBI4jwKsA8mqA1IC83EbDR4x64ImfvAEYdAfAFhIgoLHkj53w7+ngVZKpKUkgJJswZe8oLDr0J35WNWOqXHNmKUb2pquBRwF7g77Y1cDqajrvkrFFR4KzRqDWXYNoNJK1+dQ6kSiIsDsdN4wcOfTN4wKAS+fdeVFUlleqVfFs6dXHuRcPtVqFPJFyRmeL+cnmKfF3jB302+o9OyuqjL/Cjf7tu2ZlLi1Msv3Abrwy53W6GqgFZ5GOpyRQXVNFhI4kAbI7HF2GD78/do3tf1+prpjzm2ZBIXzIqJR4Fr/7WqzFVfk7jIpAVXa/XX4Hnt0zHv5oTtb0cloDmDmwMZrlNMranGqf6JNlX2LNF2vVribpRwROSiAqR1FbW02E+AFAi1WWETC7XK7YvvZx71T7Fd/pYZCz9xdXJS7pkVOGUa2Xo4XJoxKNjKuGO5KLJ3Y/jk/rFfHJJo3z2lTgmat6gLHMbTdk055U5+J/POfNW4wDew+mKorGEwFFCFAOgGPYpRyLd/yYQvvR/+cnAcDgHxjQTREvKTCpxKL4Q9PvMahgE3glP2rKEvje/QtM2PHcz4r4ZFurv/6yHHeeTVcDj3Ivr63EvGmLEAjQtli21yLNlzoBygFwjCHLNf04adTozicMAPrPG7wEMgamjlz9Ek6zVKOo9TKcbj2sfmV1riEv3DP7wBDMPnD/SYv4ZBOBJETx35sEdGlyfDXBbOqgtrnWbdmAD1/9WG1qkT5EoEEC/oAPgYC/wX5G6CDmWedMGDnqtycMAAYUDx4rA4/oGQR/5XFrk834c7P1MLGonk3VhG2Hgq0xIVbE5xeq0rdtfg2m33w6rBJlxz7qmNffeQdbvqMU2KpaqKRMgwS8PjdCIboCKAgicp25vx0+8oE5JwwA+hUPupmBvdIgUY12aGbyYmSrFTjPbtizjqry3KdV1+GJXf8E3/dXY7u+WymG9aKrgUd94wv5Y1cDDx+mA1VqXK+k04kJ1LqrEY3Slz2TZEKOI6fniBFDV50wALh04R2nR8PCj3pcSL/K24UHWq6BXaBIUGn/8pP9z+55BG+XD1JalQbnn3SlB33andFgP6N02HWoBEtmv0Z/UI3icI3bSVUAjznQYrGiEeyxKoAnDABiVQHnDea/dGjc7/9T3ykGMbTlavTP3aMXkzRtxzZv9yNFfE7XhB251gBm31qAJrb4Sw1rwrAUlPx85TKs/HR1ChJoKBHIDgG6AXCMsznHGnSNGXXcnubP7jr1Lx60HGC/zI57MjvLhY6DsVf+TSQqApFZ0g1L51n8Fh/6EybHiviYGh6goh4Xti3Hv686ByyDmQhVZG6DqvBvVfMXLMa+PQca7EsdiICSBILBAHgdAGqAyWHd9UjRqNPqs/hZANBv7qDJjLG/aBmYhUXwl+bf4ubGW+lPtgocyfP3P7rraays7q8CbZJT4d5LKnDHWeckN1iHoyrdh1E8bSH8froaqEP36sYkKgJ0zJW2XEfxmFHDfnPKAKB/8aB7AfaCVldAF2slilovRzsL5TBXgw/5Q58//DNRxCeb9pmEKCbfLKFT41bZnFbVc323bSPeW/qhqnUk5YxNwO2pBd8GMHoTBAFOe979IwofeK6hNwB9GGNfaA2YABl3FWzE3U03gCf4oaYsAf6an7/u56/9M1nEJ5tWtm9cg2k3dYJFNGdzWlXP9da772Pj+s2q1pGUMy6BmtrDVMsCgCSZ4LDl9B1eOPTLU78BmPm7fJgCmqqc0MrsRmHr5TjLVm7cla4iy/f4T48d9OMH/vTWbu5eigcvpquBR/0aCAcxZ/oCVFVRQi29rXWt28Ov/vErgNQAs9mC3DxrztChQ487EHfChOf9iwfzI/NttQDuukbbcW/ztbAK9JpHDf56q3wwntvzCPxRmxrUyYgO/7zah4vb/C+bZkbm0JLQPaX7sGjWK3Q1UEtOM4CuoXAIXq/bAJY2bKJkM9eMH1v0s6tMJwsA3gJwbcNileuRL/kxvOUqXOzcp5wSNPP/CPBkPv/a9S98VqXqZZMWj+Xb/Jh9azM0sqozgVFajExQyFerVmDZJ4avJp4gNeqeSQKUAvgYXcFp+mxi4egBP+V9sgBgIoCiTDonFdm9nHvxcKtVyBfpBHIqHNM1lqfx5el8eVpfo7Se7cvxryvoauBRf/OrgS+//Ar27NprlCVAdqqcAP/2z98CGL3xyqa5jtzfjSgcOjuuAGDA3EHXyozxtwCqajYhjH+0WItr8rerSi+jKlNXxOf+WCEf/m+jtft7V2LgmT2MZvZJ7a3yVMeuBvp8VHiFFoXyBCgFcJ0PYgcAnc4uw4ff/7NCHid8A9B73p2NJFmuANRzjb57ThkKW61ASzPt6Sj/0UKsZC8v3ctL+Bq1mcUIpt5ixmn5LY2K4Gd2/7B9C95e/B7xIAKKEqADgMfwm62WqGtc4Qm/oZ0wAOBD+xUP/oEB3RT1Io9eWBS/a/o97izYBAZZaXVo/v9fG59WXo8ndj+u2iI+2XTS6U2qMfnGLjCL2spumElG77z/ITas25jJKUg2ETglgVAoCK/PQ5QACHZTycTRo9udCMZJA4ABxYOnyMCflSTY3lIdS+rT2aqpW4lKIsvo3HVFfMbj7fI7MjqP1oTf2qMUQ3rS1cCjfuNXA4tnLkRFBX1utbaW9aIvZQA85klLru3ZcaNGPpBQANB/3p2/gyzPVGJB8KjklsZb8Jfm62FmESVUoDl/QmCr9+zY3f4Sf0di8xMC/M3UE9cEcFHrTsTmCIF9ZQewcNZSRCL0+aVFkX0Cbk8NrT0AoijCac+/cvioIR8kFAD0nXdnZ0GWt2bbdU1N3lgBn/Pth7I9Nc13AgI8i9+iQ3/GlL0jNVfEJ5sObZzjw6yBLZBvdWZzWlXPtXzNanz50TJV60jK6Y8AlQCu9+2fJwBitkYPuh48Yaauk24BcBH9igcfYkCzbC2Ry/J244EWa+AQg9makuY5BQGev3/SzmewqqYfcYqDQK8O5Xjs8nPj6GmMLjJkLH75NezaSaW4jeFxdVgZDofgoQRAMWeYciyeR8YUOk7mmVMGAP3nDX4VMm7KtFudYhAPtFyDS3N3Z3oqkh8ngRXVA/DYzqdQFS6IcwR14wQe6luFG884m2AcIVDtrcXcaQvg9VJJbloU2SFACYCOcTbl2j55ZNTIy5IMAAY9DJk9kUm3XWA/iBGtVoK/+qemPIGQbMZ/947CkkN/1E0Rn2xStUhhTLvFhvZ5zbM5rarn2rxjG95Y9I6qdSTl9EPA46lFmCoAglcAdDjz/jpy5AOTkwoA+s0ffDGLIiObePxwHz/kxw/7nfI1hH7Wpeot2ePvdKSIz1mq11XNCnZuehiTb+gKSZDUrGZWdXv/o0+wfs33WZ2TJjMmgZqaw+DbT0ZvJpMZthznuSNHDlmfVABw26LbzGUBqQYMlnTC5Nf6+PU+fs2PmjoIvFl2J54vcem6iE82SQ86twx//8V52ZxS1XOFIiHMnfkyyst5fjFqRCAzBCKRMNye2swI15hUs80aRjRgcblc0aQCAD6of/GgrwDWKx22C5AxuGAjftd0QyzBDzXlCdRG8mJFfD6vukZ5ZXSkAb8a+NR1IVzQkq5NHnXrgYpDWDBzMcJhuhqoo6WuKlMCQT/8fjpvwp0iOE3fTywcfcpc5Q2+fe8/904XmDwuVS/zFL48lS9P6UtNHQS+c1+E8TueR2mwlToU0pkWBXYvZg1shVzLSQ/h6szihs1ZtXYtPvvgy4Y7Ug8ikAQBKgBUB40XALI7cv9UWDh0+qkwNhgADJgzqKcssBVJ+OJ/Q3jxHl7EhxfzoaY8AV64Z+b+BzH34D8MWcQnmx7o27EMEy+jrYD6zJcsfh07tu/KphtoLoMQqKk9DJ4HwOitrgBQo5bDh997MKUAwOVyCZ912lIKoEmiUHm5Xl62l5fvpaYOAgcDbTB+5/PY4L5QHQoZQIsR/Q/j2s7dDWBpfCbW+tyYM20BPB66+RMfMeoVD4FwOAyPl/b/OSvRZvJMGDu6wVePDb4B4MIGFA+eLwOD43HC0T6XOPdhWMtVyJeoNGgi3DLZ95NYEZ9/whOhbHWZ5PxT2VYphBkD7WiTm7WcWtk0L6m5tu7ajtcWqq7ieFK20CB1EOB7//wMADW+/29ZPLGw8PaGWMQXAMy9826ZybMbEsZ/z1/z/735WlzXaHs83alPFgjwIj7P7JmAd8obXA9Z0MaYU3RtVoX/XN8NknDCqpyGhPLRx59h7eqT3lAyJBMyOnkCbncNIlE6YCoIIhzO3H4jRz7wRUM04woArpjzm2ZBIcz3Ek7Z/yxbOQpbL0crs7uheen3WSKwJVbE50Xs9Z+WpRlpmpMR+PX5ZfjLBXQe4CgfnqylePbLKC0tp0VDBFIiEI1GUeuma+UcotliloGQ2eVyNXjoLq4AgAvtXzx4DYALTuQlfqXvt0034M6CjeBX/agpT4AX8Xn54F8wdd8IKuKjvDtiGghMxrPXh3FOcwrGjrrkUGUZ5s1YBL5/S40IJEsgGAyAlwCmBjC76cdJo0d3jodFIgHARABFPxXa3lIT+9bfxVoZz3zUJwsEKkNNY0V8Vtf0zcJsNEUiBJo5PJg5sC2c5pxEhum675pvv8Un732uaxvJuMwSoOt/dXz59T+b037f6FHDXoiHeNwBwIDiu3rJiH51VCgfeHPjrfhL829hYbTvEg/sbPRZUX0pHt35FA6HE760kQ31aA4Al3YqhWvA+cSiHoGlS9/E9m07iAkRSIoAXf+rw8bT/+aare0eGv1QSTwg4w4Ablt0m1gWlPhmXX6B5MOI1itwof2UVwzjmZ/6pIkAL+LzUkkRlpT+IU0SSUwmCRQOqMZVnajmwlHGbr8ndjXQ7fZkEjvJ1iEBKv97zKmSzewdP7bIHq+b4w4AuMD+xYMWDcgtue3BlqvBS/hSUweB3bEiPi/iR283dShEWjRIIMccwoxbnGjlpHLLR2Ft37MTS+e/0SA76kAE6hPw+70IBAMEhb8BcFoWPVJYeEe8MBIKAOa/3/W5wU033xevcOqXeQJvlN2FF0rGURGfzKNO+wxnNa/CC9d3g8joauBRuJ98+gXWrFyXdtYkUL8Eat01iNL1P0iiBKfdfvmwUUM/itfbCQUA73ze/ryrnbvXxiuc+mWOAC/i889dT+CLqqszNwlJzjiB311Yhj+cR1cDj4IORyOYN2cRDh3kyUepEYFTE6Drf8f4mC3WaOPG9pwhQ4bE/TokoQCAT1W2yuYtkHw2WpjKEVhf2zOWzrcs2FI5JWjmtBAQWBQv3CCje7P2aZGnByGlVeWxq4GhUEgP5pANGSRA1f+OwZWclrXjCwtPeFX/ZC5IOADY9HWTz7raKvpl0Kck+iQEIrIUK+JTfOAfiEIgTjoh0CLXg5m3tIPdRHH1UZeu++57fPjOJzrxMJmRKQJuTw0iEbqFJggC8hz5twwbdf+ribBOOAA4sML++xZmz4xEJqG+qRPgRXwe2fkCfnAnFOClPjFJyAqBy7uUYkw/uhpYH/Zrr76NrVt+zAp/mkR7BPi+P9//pwaYzOZokybOhF7/c24JBwDySjSRTShPeCB5KWkCH1fegCd3P05FfJImqI2BYy6rweUd6SbHUW95/F7Mmb4AtbWUWlwbKzi7WgYCfvgDvuxOqtLZRLvpmwmjRydc4jWp53jVasuufDFAm5YZXgy+qB1P756A9ypuy/BMJF4NBOzmIGYOzEMLByVxOuqPnSV7sGT+a1TjXQ0LVGU60On/Oofw7H9Oe941I4sefDdRFyUVAHjXiM/ZhAhdB0yUdgL9N3t6YPzOF6iITwLM9NC1R8tKPHdtdwiMzngc9efnn3+Nlct5KRJqRKCOAK/6x6v/UQMkiynSvVsXy+23357wYYikAgD5WwxAFHRCJwOrjxfxWXjwnlgRn7AsZWAGEql2An+6qBx3n3Ou2tXMmn78j/38uYtx4MChrM1JE6mbAH/1z7cAqAFCjvnziWOK+ifDIrkAQAbzfmM6mCOEmiUzKY05MYGKULNYEZ81NX0IkYEJiEIUL94IdCtoZ2AKx5tefrgSxTMWIhikq4G0KBAr/ctzABi9xU7/23MvGVb44PJkWCQVAPCJPKslV44YHpfMpDTm5wSWV1+Gx3b+m4r40OKIEWidV4vpN5+GHJOViBwhsH7DBrz/1sfEw+AE+LU/fv2PGiBZzaHx44rMybJIOgCQ16BlVGD7BMhJy0hWaT2N40V8/lMyGktLf68ns8iWNBC4umspRvWhq4H1Ub7x+rvYvGlrGuiSCK0S8Pt94AmAqAFirnnphFFFtybLIqWH94GV9tUtTJ6Erx4kq6zexu3ydY4V8dnuO1NvppE9aSLwyOVuDOjQNU3StC/GF/Bj9oz5qKmu1b4xZEFSBOj1fx02SZKQY7f3GDly6PdJgUwmD0D9iWpXmW9xSMGlyU5u5HFvlP0az5eMQyBKr3iNvA4ast1hCWDWrY3RLKdRQ10N8/vd+/ZiUfErdDXQMB4/ZmgkEobbQ8FfLADIMXvHj4m/9O+JlktKbwDkRRDdp5kPO8Sgw4BrMSmTa8L5+NduXsTnqqTG0yDjETivVQWeuaZH7L4vtToCX365HMu/XkU4DEbA5/MiGIq71o1u6fC/BaZc21OukSMeSsXIlP+i7F3h+G9rs/ueVJQwythva3+JCTufoyI+RnF4Gu386y/LcefZdDXwKNKoHMX84iXYv+9AGimTKDUTkGU5dvqf/zR6M5nMsNpsp48aNXRHKixSDgDkdeggy9iZsqBUrFD52LoiPkNRfOBeKuKjcl+pVT1JiOKlmwSc0aSNWlXMul6VNYdjqYKDgWDW56YJs08gGAzA5/dmf2IVzmhyWPc/UjSqdaqqpeW5fWCl/YcWJg8lMT+BNw4E2mL8jhfwg4dOc6e6WI0+vm1+DabffDqsksXoKP5n/4aNm/DOGx8QDwMQoMp/dU7md/+d9vzfjSi8f3aqbk9LAFC9yvrrXMk/N1Vl9Db+o8qb8O/dj8EToSMSevOtUvZc360Uw3pRMFmf/9tvvo8fftislEto3iwQoMN/xyCbLZZI48YO+5AhQ1I+DJGWAEDeALPXb6rOEUJ0pB1AXRGfiXivIunrmVn4SNEUWiUw6UoP+rQ7Q6vqp11vfzAQuxpYfZiSw6QdrkoE0uG/egGA07rAVTjqznS4Ji0BAFdk7wrn3Nbm2l+nQykty9jsOQeP7HgB+wIdtGwG6a5iArnWAGbfWoAmtjwVa5ld1Ur278PLxa9QetjsYs/KbHT47xhmURSRZ23c4eHR/9idDvhpCwDkNegKAZvSoZQWZfAiPgsO/hXT9g2nIj5adKDGdL6wbQX+fVUPMKTtI6wxAj9Xd9mylfjqixWat4MMOJ4AHf47xoPZpH2Txo5J20ngtP71OLQy58dmJu/pRlvAvIjPxJ3P4pua3kYznexVkMC9l1TgjrPOUVADdU3NrwYunP8K9pbsU5dipE1KBOjwXx0+fvff7nDeWFj40BspAa03OK0BQNnKnL8WmLwvpUs5Lcj5+vDleHzXk6gON9aCuqSjjgiYhCgm3yyhU+NWOrIqNVMO11Zj9vQFCPhTPh+VmiI0Oi0E6PDfMYyiRQqNHzfawhhLWyKEtAYA8jLYAmbxsEWIJF2dKC2rJgtCglEL/rN3NF4p/V0WZqMpiMCJCbRvXINpN3WCRdT9Ry7uJbBp81a8+dq7cfenjuolQIf/6vnGaX7x0cKif6TTW2kNALhipSvsC5uaPXekU0m1ydrp6xIr4rPDR0Va1OYbI+pzU/dSDL2YrgbW9/07b3+IDd9vNOJy0I3NdPjvmCslk0kuEHLzh7iGpPWqS9oDAHkdzoWMdbpZhT8x5LWy3+DFkrFUxEevDtaoXY9f7cMlbTprVPv0qx0IBTFnxgJUVR1Ov3CSmBUCgYAf/oAvK3OpfRLmkJZNKhrTK916pj0A4ArWrjFvdQhBXf01qgk3wj93PYEvD1+Zbh+QPCKQMoF8mx+zBjZDY1tuyrL0ImDfwQNYMGcJXQ3UqENranne/6hGtU+f2qIoIdeWe/awovs3pE9qnaSMBADyN/gLGCanW1ml5K2rvSR2yr8s2EIpFWheItAggZ7ty/GvK86hq4H1SK1YsRpffLasQXbUQV0EeMU/vv9PDRBzzIcmjCnKyMMnMwHANlgC1dIBixDWdBFzXsRnxv6hmEdFfOhzqBECQ3pX4tYze2hE28yryfeRX17wCvbs2Zv5yWiGtBGoddcgGo2kTZ5WBfG8/3ZH3qBRox54ORM2ZCQA4IoGvxEeMLHo05lQOhsy9wfaxYr4bPScl43paA4ikBYCJjGCqbeY0TG/ZVrk6UFItbsGs6ctgN/v14M5urchFA7B63Xr3s54DDRbLQHIQYfL5QrH0z/RPhkLAORPYfU6pUM5Qlhzm5IfVtyMp/Y8SkV8El1N1F8VBDo2qcaUG7vALJpUoY8alNiydRtef+UdNahCOjRAwOOpRTiSkeedptjzxD85TufYolEPTciU4hkLALjCNavNw51i8J+ZUj7dcr0RB57eMxHvVwxMt2iSRwSySuDWHqUY0pOuBtaH/v57H2P9t2k/R5VVv+p9Mkr8c8zDksUcEVCQ63Ldk7HDEBkNAPhbAI/TVG4XQna1L9xNnnNjr/z3BdqrXVXSjwg0SIBBxhPXBHBR604N9jVKh2A4FLsaWFlZZRSTNWen1+dBKBTUnN6ZUNjktL7wSOGo+zIh+6jMjAYAfJIDK3PGtTB5XZk0IhXZUQhYcPBvmL7vYSrikwpIGqs6Ao1y/Jg9sDnyrU7V6aaUQgcOHcL8OYsRidABM6V8cLJ5o9Eoat3ValNLEX1EkyTnOq3OYcOGeTKpQMYDAJ4e2G0yVzjEoC2ThiQjuzzUHBN3PIu1tWnPr5CMOjSGCKSdQK8O5Xjs8nPTLlfLAletXIvPPv1SyyboUnef3wte+Y8awOzi0kmjx96aaRYZDwC4ATtX5D3awVw9KtPGJCKfF/F5bNe/wRP8UCMCeiYwtG8VbjrjbD2bmJBtMmQsWvgadu/ak9A46pw5ArG0vzzxD9JW5yZzymZYsiCKstNpyRsxYkRthqfKTCKgnyqtprcAvIjPi3vH4NXS32aaLcknAqogYJHCmHaLDe3zmqtCHzUoUetxY9a0+fD5KNWsGvzh9/sQCNI1Te4LZhffnDR67A3Z8EtW3gBwQ/ascD7a1lyr6FuAnb4z4NrxIvhPakTASAQ6Nz2MyTd0hSRIRjL7lLZu+3E7Xl3yFvFQmABP91tbW0Pf/gGIkiTb7aZGI0eOzMphiKwFAPwtgMdsqrALIUXOArxaejde3DsW/A0ANSJgRAKDzi3D339Bia3q+/7D9z/FunXfGXE5qMZm2vs/5grRYX5lQlFR1u6hZy0A4CbuX+6Y1NLiLszmyuN7/Hyvn+/5UyMCRibArwY+dV0IF7TsaGQMx9nOs87NmbUQFeWVxEQBAnTy/xh0ySTJNltvdDpeAAAgAElEQVSTJqNG/T1r91SzGgDIa5Djhak8J0tvAfjpfn7Kn5/2p0YEiABQYPdi1sBWyLU4CMcRAofKylA862W6GqjAiuAFf3jhH2qA5LQsHl9YeHs2WWQ1AOCGla7ImdDU7B2dSSN5EZ9p+x6O3e/n9/ypEQEicIxA345lmHgZbQXUXxPfrPkWH3/0OS2TLBLgxX540R9qgGQyyVZrftPCwn9UZJNH1gMA/hbAB6ncJoQzchaAZ/LjGf14Zj9qRIAInJjA8H6HcV2X7oTnCAF+/WzJotexc8duYpIlApT17xhok8O28JGikYOzhP5/02Q9AOAzl63KGV8gecek29gPKm7BU3smgef0p0YEiMDJCVilEGYMtKNNbjPCdISA2+uJXQ30ejOWep1YHyEQiUbgpm//MRpmk1m2O80thg0bVprtBaJIACCvh90XkkptQjgnHQbzBz5/8PMAgBoRIALxEejarAr/ub4bJEGMb4ABem3fvhNLF79hAEuVNZGX++UHMKkBZkfOFFfRiHuUYKFIAMANrVhlfaSx5B+bqtEbPefFXvnvD7RLVRSNJwKGI/Dr88vwlwvoPEB9x/OzAPxMALXMEKCKf8e4ihZTpFFujnPo0KGKZKRSLADgbwECIfGQRYgkVSmQH+6bf+DvmL7/IfBDf9SIABFInIDAZDxzXRjntjgt8cE6HcFr0c+d9TLKysp1aqGyZnm8boTp2z8YYzDbLUPHFY16WimPKBYAcIMDa4URZkQfT9T4smALTNz5LNbVXpLoUOpPBIjATwg0c3gwc2BbOM1p2ZHTBd+y8nLMnbUQ4TBVDUynQ/mDnwcA1ADBIrknjBudyxhTrACCogGAvA0WX7W0xyaE4z6J9NXhK/D4riepiA99gohAGgkM6FSGRwbQVkB9pGvXrsdHH3yWRsokil/749f/jN74t3+rzX75mDHDPlKShaIBADdcXotBABY0BCEQNePFEhdeK/tNQ13p90SACCRBoHBANa7qdFYSI/U75JUlb+LHH3fo18AsWsaL/fCiP9QAZhF3T3KN7aA0C+UDABnM/430nVUIn/RS8k7f6XDtmIKdvi5K86L5iYBuCdhMYcwc6EArZ4FubUzUMK/Ph5nTiuHx0NXARNnV7x8r9+uuBv9p9CYIAixWW6cxY4ZvV5qF4gFA7C3AGvSGgC9PBOPVssF4sWQCFfFReqXQ/IYgcFbzKrxwfTeIjK4GHnX4rl27sWjha4bwf6aMpJS/x8gKNtM7E8eOvjZTrBORq4oAgCvsXyO+bREi1xxVvjqcg8d3PYuvD1+ViD3UlwgQgRQJ/O7CMvzhPDoPUB/jp598idWr1qZI1pjDI5EI3B5K+cu9L5qkaK7Tmjts2DCPGlaDagIA+Vt0iUbZRgGyuNbdFRO3z0V5qIUaGJEORMBQBAQWxfM3RHF2M8W3KFXDnT/Eiue8jEOHylSjk1YUcXtqwe/+G70xMJgdtsJxRSMeUwsL1QQAsbcA35ien3tw8J+L902wUBEftSwR0sOIBFo43Zg5sD3spoyU7NAk0oqKSsyZtQChED3M4nVgKBQEz/lPDRCtptrxY4vylLz291M/qCoA6P2f3Y2YFN0BSPm0YIgAEVCWwOVdSjGm3/nKKqGy2dd/uwHvv/exyrRSpzr8wB/P9x+Vo+pUMIta8YN/thzHpUVFD32axWkbnEpVAQDXtu+UvbfLkF9uUHPqQASIQMYJjLmsBpd37JbxebQ0wauvvIVtWxU/wK16ZP6AD4GAX/V6ZkNB0W7eOGF0keru2KouAODO6DP1x48gWy7LhmNoDiJABE5OwG4OYubAPLRwNCFMRwj4/H7MnD4P7lrKaHeyRRGNRmPX/qgBkkmS7fa8diNGDNmrNh6qDAD6T93bJiKHt/FdE7UBI32IgNEI9GhZieeu7Q6BCUYz/aT27t5TgkULXqV77SchRPn+68DwjH+mHOt41+iR49T44VFlAMBB9Z26615ZFl9QIzTSiQgYjcAfLyrHb88512hmn9Lezz/7GitXrCEmPyEQDAXA7/1TAwSrqWLC2KKmajr4V98vqg0AIMusz7Tt30C20IVk+iQRAYUJiEIUL94IdCugsttHXRGJRjFvziIcPHhIYe+oZ3pZ5q/+a+jNCAB+8C/Hbj+zsPDhzerx0PGaqDcAANB/8v6uERbaAAiUlkytK4j0MgyBVrluzLilA3JMtDN31OmVVVWYM3MBgsGQYdbBqQz1et0IUanfGCLRZi6eMLZI1cVrVB0AxLYCpuwYLcM0gT5dRIAIKE/g6q6lGNWHrgbW98T3323Eu+98qLxzFNaA7vwfc4BgEn09und13n777aoufaj6AAAuWejT+sdvIVvPVnh90/REgAj8/8GmRy53Y0CHrsSiHoHXX3sHWzZvMywTKvZzzPX84J/ZYrt03LgRqrrzf6LFqf4AAMAlk/ecLrLIJn6hwrCfMDKcCKiEgMMSwKxbG6NZTiOVaKS8Gv5AALOmz0NNTa3yyiigAc/2x98AUAOY1fThpHGjr9ACC00EAHVbAZvvl2F/RgtQSUcioHcC57WqwDPX9Ihdc6JWR6CkZB8Wzl9quANw4XAI/NofNUAwicG2rZs77rnnHk0cCtHUp7fv1A2rZTnvQlpoRIAIKE/gnp7luKsHXQ2s74kvv1iO5ctWKe+cLGkQS/frqQFP/GP0xpiAHIvjV0XjHtJMrmhNBQB9Ju9qCRbZAZjpGLLRP21kv+IEJCGKl24ScEaTNorrohYF+INwfvFi7N9/UC0qZVQPn9+LYDCQ0Tm0IlzIMX0yccxoTWWw1VQAwBdCn6mbfw3ZPlcri4L0JAJ6JtAmvxYzbu4Iq2TRs5kJ2Xb4cDVmzZiPYFDfe+LhcBgerzHPPPx0QYgWKSCiTb7L9XtNFT/QXABQFwT88C7k3KsS+lRSZyJABDJC4PpupRjWi64G1of7w4bNePut9zPCWw1C607984Q/9OqfJ/xx5tivGFH0sObugmoyAOg/c2d+JBTZDVhy1fBhIB2IgNEJTLzSg77tzjA6huPsf+uN97Bx4xZdMqGEP8fcarbZlrrGjrxVi47WZADAQfedvOMKmZn0G2JrcTWRzoYlkGsNYPatBWhiyzMsg58aHggGY1cDq6trdMWE7/nzvX9qgGgxVYkIN3O5XGEt8tBsABALAqZumi3Ljru1CJ50JgJ6I3Bh2wr8+6oeYND0n5W0umXfvgOxQ4H8lbkeWiQagdvN9/31YU8qPhFEUbZYrJ3HjBm+PRU5So7V9Cf1gsn7c3IE74+QLS2VhEhzEwEiUEfg3osrcEf3cwhHPQJff7USX3+1QgdM5NjDnwcB1ABLjnXouDGjntYyC00HABx878klPRmTl/PKy1p2BOlOBPRAwCREMflmCZ0at9KDOWmxISrLWDBvCfbt3Z8WeUoJoSt/x8gzi7R+kmuM5pNg6OKh2WfK9kcB8yilPhg0LxEgAscItG9cg2k3dYJFNBOWIwSqa2owa/p8BALavDPPK/zxg3/UACYJIZMo57pcLk1d+TuR73QRANQVDNqyHLL9IlqgRIAIKE/gpu6lGHoxXQ2s74lNm7bizdffVd45CWoQlaNwx6780b4/T31tsZr7jh1b+GWCGFXZXR8BAIDLXtjbJGjxbYNspQolqlxqpJTRCDx+tQ+XtOlsNLNPae/bb32AHzZs0hQTnuyHJ/2hBjCL+Nwk19j79cJCNwEAd0jvqbsvYLK8ChAFvTiI7CACWiWQb/Nj1sBmaGyjdB1HfcizA/IsgTxboBZaIOCHP+DTgqoZ15FZxK2TXGN1lexCVwFALAiYsuXvDDkvZnw10AREgAg0SKBnu3L868pz6GpgPVIHDhzEvLmLVV9Ah6r8HXOaIIlBSYzm6WHfv/6HVncBADeuz9RNiyE7NJmZqcG/qNSBCGiMwJDelbj1zB4a0zqz6q5YvhpffL4ss5OkID3K7/t7amnfHwBP9Wu22C8cO/bhb1JAqsqhugwArn5um8Vti/zw/0WDTlcldVKKCBiIgEmMYOotZnTMp3QdR93OD9QtXLAUJXv2qW4l1JX4rQUPAoze+KE/q802esyYEZP0yEKXAQB3VK/J+9sJzLcZMNv06DiyiQhoiUDHJtWYcmMXmEWTltTOqK41NbWYNWMe/H51XQ2kPP/H3C5ZzSvGjyu6OKMLQUHhug0AYlsBU3ZeCYjvUpIgBVcYTU0EjhC4tUcphvSkq4H1F8SWzdvw+mvvqGaN0KG/Y64QLFJV25bNmt9zzz0h1TgozYroOgDgrPpO3ThRlp1FaeZG4ogAEUiCwBPX+NGzdackRup3yHvvfoTv1v+guIF06K/ew18UIjZbXuuiogcOKe6YDCqg+wAAssz6TNv8GWRH3wxyJNFEgAjEQaBRjh+zBzZHvtUZR29jdAmFQpg9cwEqK6sUM5gO/R1Dz/f9bSZrn9GPjPxKMYdkaWL9BwAAej63Lddsk7dBtjXLEleahggQgZMQ6NWhHI9drvk06mn178GDpSie87IiVwPp0N/xrmQ2U9GksaMfTauDVSrMEAEAZ99/2p7ukWh0LUCnkFS6FkktAxEY2rcKN51xtoEsbtjUVSu/wWefZv9LJx36q+cbi/D+o65xVzXsLX30MEwAwN3Ve/Lu2xgTFunDdWQFEdAuAYsUxrRbrGif10K7RqRZc55pf9HCV7B7V0maJZ9cHM/yxw/+UQNgEvY9On5cGyOxMFQAwB3bd8qOh2WYnjCSk8lWIqBGAp0LqjH5xjMgCZIa1VNEJ7fbjZnT58Hny/xDORgMgJf4pQYwUfCZJLnA5XIZCojhAoBYEDBt24ty1Pp3WvhEgAgoS+COc0px70V0NbC+F7Zt24FXl76ZUcdQed9jeJkgREwmcyeXa9SujEJXoXBDBgB1NwO2vgE55zoV+oRUIgKGIcAg46nrQrigZUfD2ByPoR+8/wm+Xfd9PF0T7hOJhOHxuinNLwAmMNliyek3duxwXZT3TXQxGDMA+P+9tm6LNpibVJuWQc65IFFo1J8IEIH0ESiwezFrYCvkWhzpE6pxSbz8Lr8aWFFRmVZLotEo3J4aevjzhz9jsFgtfxw7dtSMtELWkDDDBgDcR3XXA6PfQc5pryGfkapEQHcE+nYsw8TLztOdXakYVFpajrmzFyISSU9Ofrrud7w3zBbbMy7XyAdT8ZHWxxo6AODO6zV9TyshGvgBsjVf684k/YmAlgkM73cY13XprmUT0q77mtXr8MnHX6RBLi/w4wZ//U8NEG2mDyaMHX2l0VkYPgDgC6Dv1F1nynJkHWC2GH1BkP1EQCkCVimMGQNz0CaX8nUd9QG/Grjk5dewc+fulNzi9XkQCgVTkqGXwYJF+n6iawzVp+bbIHpxaqp29P3vjr6yIHwCiGKqsmg8ESACyRHo2qwK/7m+GySBPoZHCXo8ntjVQK/XlxRUv9+LQFBdFQeTMiQdg8zi3kmuMe0YYzy2MnyjAKDeEug9ecdtjEkvU/VAw38uCICCBO46vwz3XEDnAeq7YPv2nVi6+I2EvULV/Y4hYyah0iTIzV0uF+2DHMFCAcBPPlK9J+8cwpj0bMKfNBpABIhAWggITMYz14VxbovT0iJPL0I++vAzrP1mfdzmUKKfeg9/SfCYRLmFy+Vyxw3QAB0pADiBk3tP3fEkk00PGcD/ZCIRUCWBpg5+NbANnOYcVeqnhFL8auCc2QtRXlbR4PT08K/38BeFYE5Ualf0aJGuS/s2uChO0IECgBNRk2XWd+quWTKku5OBSmOIABFIncCATmV4ZABtBdQnyR/+c2YvQDh88quBwVAQPp8ndQfoQAITWIQx8ayJE8ds0YE5aTeBAoCTIeXZAqdunw1YfpN26iSQCBCBuAgUDqjGVZ3OiquvUTrxbQC+HXCixk/68xP/1GJZ/qImk+kCl6voW+JxYgIUAJxqZcSCgB9nA1YKAugTRAQUIGAzhTFzoAOtnAUKzK7eKfmBQH4wsH4LhULw+miLmzOpe/hLPV2u0WvU60XlNaMAoCEf1NUNmAM559cNdaXfEwEikH4CZzWvwgvXd4PI6GrgUbr8SuDM6cXweOqK14XDoVh+f2r84S/IFoup19ixhcuJx6kJUAAQzwqJBQFb5kK23xVPd+pDBIhAegn89sIy/PE8Og9QnypPDrT45dfo4V8PCn/4W03mS8e4Rp14jyS9y1Lz0igASMCFfadumi3LDjoYmAAz6koE0kFAYFE8f0MUZzfrkA5xupHx6adf4uMPP4EMymtT9/C3XTXGNfwD3Tg4w4ZQAJAg4L5Ttk6XYftDgsOoOxEgAikSaOF0Y+bA9rCbbClK0sdwn8+P8vJKfPrJZ9iyZas+jErSCv7wN5utl40bN+LTJEUYchgFAEm4ve/UrZNl2faXJIbSECJABFIgcHmXUozpd34KEvQxlJ8B4A9/XuFPEBhmzZwLv9+vD+MStIIJQtRiMfWmPf8EwVEtgMSBHR3Rd8r2F2WY/568BBpJBIhAMgTGXFaDyzt2S2aoLsa43R5UVFQdZ4vP68XcufN1YV8iRjBBiJhM0oV01S8Rasf60huA5LjFRvWduuNZWTYNSUEEDSUCRCBBAnZzEDMH5qGFo0mCI7XfvaamFlVV1Sc0ZOPGjfjqy2XaNzJOC5jAwlYm9hgzccymOIdQt58QoAAgxSXRZ8rOpwDpwRTF0HAiQAQSINCjZSWeu7Y7BCYkMErbXQ8frkF1dc1JjeBbAa++8joOHSrVtqFxaM8EFmRM7DZx4pjtcXSnLichQAFAGpZGnyk7/wlIw9MgikQQASIQJ4E/XlSO355zbpy9td2tsvIwamsbvucvy1FMmzozdjZAt01gfgapy6RJo0t0a2OWDKMAIE2ge0/ePYQx9gyVEk4TUBJDBBogIApRvHgj0K2gna5Z8cN+RxP+xGNo6aFSvPZa4qWD45GteB8R1WaJdXG5XPp/zZEF2BQApBFyn6l7boQcXQKIUhrFkigiQAROQqBVrhszbumAHJNVd4z4t3j+8Ocn/hNpjDF8+cVX2LhRZ1vjEttrFtHZ5XIZ87pDIosgzr4UAMQJKt5ufaaVXIRo6CPA5Ix3DPUjAkQgeQJXdy3FqD76uhrIH/6lpeXw+wNJgeHnAebMngevty5VsNYbMwlrTYL8C5fLFdW6LWrSnwKADHij94zdHYVw6AsZltYZEE8iiQAR+AkB1+W1uLTDmbrgEolEUFZWgUAgmJI9fr8vFgRovYlm6bUJj4y5Wet2qFF/CgAy5JWLp5U0Nsn+j2XZaoxTShniSGKJQDwEHJYAZt3aGM1yGsXTXbV9gsEQysrKEQ5H0qLjls1b8PnnX6ZFVvaFMJgtln+7XKMezv7cxpiRAoAM+rn/zJ3WSCiyBLBcm8FpSDQRIAIAzmtVgWeu6QG+B67FVj+7X7r05yzeeP1NHDhwMF0isyKHMSabJfMfx40vnJmVCQ06iTY/KVpyFq8kOHXns4DpPi2pTboSAS0SuKdnOe7qob2XbqdK8JOqH/h5gunTZiIa1cb2OU/wYxHMfcdOoHK+qfq+ofEUADREKE2/p2uCaQJJYojAKQhIQhQv3STgjCZtNMGJP5wrK6vgdmf2sF55eTleWfqa6pkwkdVCls6cNGn0PtUrqwMFKQDIohP7Ttlzg4zYNUFTFqelqYiAoQi0ya/FjJs7wipZVG13JBKN7fenetgvXiOXfb0MGzZsjLd79vtJbIfPXd396aefTuzeY/Y11c2MFABk2ZV11wTDHwBSXpanpumIgGEIXNetFMN7qfdqYCgUQmlpBcLhcNZ8wq8G8oJBHrcna3PGPZHEPjSLuIqu+cVNLC0dKQBIC8bEhPR/aWeHiIi3AOmsxEZSbyJABOIlMPFKD/q2OyPe7lnr5/P5UV5egWg0++l6A4EAZs+amzVb45lIlMRHJ0wYWxRPX+qTXgIUAKSXZ9zSrn5um8VtkV4Ck34f9yDqSASIQNwEcq0BzBrYBAU5+XGPyXTHTB72i1f3bVu34dNPP4+3e+b6CSwsMPHaiRPHfJC5SUjyqQhQAKDw+ug9de/dTA5Po3MBCjuCptclgQvbVuDfV/UAg7J/6uoO+x2GWwWv3/nVwDfffBv79+1XzOdMFA7JUem8Rx8tOqCYEjSxwp8KckCMQN/JJWfLLPgOYNbG0WXyGxHQEIF7L67AHd3PUUxjvt9fVlYJ/lNNjV8N5FkHs91ESfpAFCNX035/tsn/fD5lw2Ll7VeNBj2f25ZrtrEFkC3XqEYpUoQI6ICASYjivzeL6Nw4+5m5eRW/iooqVZbnraysxJLFr2TNwzy5j2Qyj3zkkcJ/ZW1SmuiUBCgAUNkC6TN1xzDI0uMAE1SmGqlDBDRLoF3jGky/qRMsojkrNqjplf+pDF6xfCW+++77jDNhouA1SVIvl6vo24xPRhPETYACgLhRZa9jn2n7eiHqfwswq+f0UvbMp5mIQEYI3NS9FEMvzvzVQLW+8j8RVEEQUDx3Ptxud0aYc6HMJKwxCXIvl8uVWnWjjGloXMEUAKjU95e8dLCZaKp9A1FrT5WqSGoRAc0RePxqHy5p0zljevNDfvywH38DoJUWDAYxa+ac9KvLmCwIYtHEiWMeS79wkpgOAhQApINihmTctkgWDx3eNUmGNCJDU5BYImAoAvk2P2YNbIbGtty02s0f+Hyvn+/5a7Ht2L4DH330SfpUF+ARBbHPhAlj16VPKElKNwEKANJNNAPy+kzeey1YeAEgOjMgnkQSAUMR6NmuHP+68py0XQ2se+VfgVAoe1n90u0wfjXwnbffRUnJ3pRFM1FYEfDX/urJJ59UYcrBlM3TlQAKADTizl7T97QSItHZgPgrjahMahIB1RIY0rsSt57ZI2X9tPjK/1RGz5g+K/n0xIxFRSY8NGHS2GdSBksCskKAAoCsYE7fJL2n7PkDQ/QFQLSlTypJIgLGImASI5h6ixkd81smZTi/P89f+fO0vnpqVVVVWLxoacImCaKwR5bF3pMmjS5JeDANUIwABQCKoU9+4l6T97cTBC/PGXBJ8lJoJBEwNoGOTaox5cYuMCdYnJPv8/ODftFoVJcAV69eg3Vr47ytx+/2S+KT48ePGa5LGDo3igIArTpYllmfqTv/AQj/pjTCWnUi6a00gYFnl+L+X8Z3NVCv3/p/6gN+NXD+vIWoqak5pXuYKFQLzNJvwoSR65X2I82fHAEKAJLjpppRvWfs7ihEgktl2XquapQiRYiAhgg8cY0fPVt3OqXGev/W/1Pjw6EQZsyYfWImjEGSpAXjx4++C4B27jtqaE1mS1UKALJFOpPzuGShb6vdQ2WwRwHBlMmpSDYR0BuBRjl+zB7YHPnWn1+yMcq3/hP5dNeuXfjg/Y+O+5UgCh5Jslzjco38Qm/rwIj2UACgI6/3mr7vDCHifxkwK1f5REc8yRTjELikQxkev/y84wx2u72oqtLvXn9D3uVXA9979wPs3r071tVsMr3+w6YuAxcvvj37FYQaUpZ+nxQBCgCSwqbeQTx50MHDe4b/fy2B8QCT1KspaUYE1EXgwT5VuLnr2bEKeXo84Z8MbcaAWbPm+hCRB44bX/RuMjJojHoJUACgXt+kpFn/aXu6R6KReYCU+mXnlDShwURAGwQsUhhTrrVDCoR0e8I/EU/wNwDu2tpyt6ema8+ePSsSGUt9tUGAAgBt+Ck5LV2y0KfV3j8C4ScBKb25T5PTiEYRAVUSCARDqKhxo397C8b2tmsql38mgEpm6ZDNYr6pSZMmKzIhn2SqgwAFAOrwQ0a16D9zZ340HPmnLJv/RGWGM4qahGuMQCQaRVWtB27vsYQ+T1/dDBc2M+bhdkEUIjk2W2FBQeN/acyVpG4SBCgASAKaVof0mrL7LIEFZkK2/UKrNpDeRCBdBGo8Phx2exCNHv+wFwC8f3dLWJl2c/snyoi/7jdbTe/KkcitrVq10mZFo0SNpv6gAMCAi6DPlJKBQPAlwNzUgOaTyQYn4A+GUFnjRvAUxXvOKLBg+vX5kHWa7a/+EhBN4l6LyXZDs2aNqHKfwT4bFAAYzOFHzb34qRKb6IgUMrARlDvAoIvAYGbHXvfXeOCOM3//fRc3wu1d9HuRhgnMb7VYHmzevOl/DbYUyNwjBCgAMPhSiNUVYN7/AJZrDY6CzNcpAf6Cv5a/7q/1IContre/+I4WaGHV2bV3BtlsMk3zeGrv69y5c0Cnbiez4iBAAUAckIzQpd/kvQOiLDAVMJ9uBHvJRmMQ8PgDsQd/KJzcQzzfJuKNQU3BosmNVxtlQRK+ioSCvznttNN2qU030if7BCgAyD5z1c7IkwgdqNpzL2PyJEB0qFZRUowINEDAFwjGTvefap8/XojXnOFA4cU5mr4aGGXyJkEW7+rQoTXt88freAP0owDAAE5O1MT+L5Y6IpL3QTB5JCDlJDqe+hMBpQgEQmFU1bjBD/qlsz1/XTOc2ySx7YN0zp+srAiL7jML5rvatm35ebIyaJx+CVAAoF/fpmxZz+e25Zptpochyw8Dki1lgSSACGSIAH/Fz7/xe/2Z2dKWBOC937SEBdq4GigzucIsiX9s3br16xlCTmJ1QIACAB04MdMm8ERCkRB4fYGhgGjJ9HwknwjESyAcicbu8tdP5BPv2ET7dW9uwX+vUfnVQAa3STLd37p1ixmJ2kf9jUeAAgDj+Txpiy+eVtJYlAOFTJbuA0Rz0oJoIBFIkQC/0lft9qLW68/q3vzQXo1xcycxRe0zMJzBbzGbx7Ro0expxpg+TixmABOJPJ4ABQC0IhIm0H/y/oIw841mEP8OiKaEBdAAIpAkAf7g51f6eBa/RK/0JTnlz4a9MrgFmppV8oxlCJtNpicrK8vHde/ePZguG0mOMQhQAGAMP2fEysum7mgeRGQcZPOfAUG/GVMyQo+EJkIgHFjx884AAAfdSURBVInEHvrZ/sZ/Ih0LckS8ekdTQMGrgUxgIYvZ9EI0GhlNqXsTWUnUtz4BCgBoPaRMoM/kXS0Zw2gZjAcC9EYgZaIk4CgBfo2v2uOFx5eZw33Jkr7xTAcevkiBc7EiDltN1vHNmxc8yxiLJqs/jSMCnAAFALQO0kagz4wDTVk4dI+M8IOAqXHaBJMgwxHg1/j4Hj+/z6/W9tL1zdG9cZaewSLbbpHMQ1q2bPaOWnmQXtojQAGA9nymeo0vmLzGlMOaDZRZoIjJ1u6qV5gUVA0Bfo2PP/j5fX61N5PA8P5vWsCUuauBsiCxL6Jh4W8dOrTapHYepJ/2CFAAoD2faUrjPtNKLkLUPwow3wAIvNIqNSJwHAFZluH2BVDj8SadslcppOe0tOLFK3PTehNBZnJEkqRZIsPIVq1alStlG82rfwIUAOjfx6qwkJ8TgBB+EDL7G2CmNMOq8IqySvA7/G5v3cE+frpfq21E38a47rTUrwZGEfWYRPOEcNj/7GmnnebXKg/SWzsEKADQjq90oenVz22zeCy2QbLoK0LU2lkXRpERCRHwBoJwe3zgP/XSXr+zJRqbkty2ELFeBArbtGnzLmNMe/mG9eJEA9pBAYABna4Wk3tN3t1bYNGHAfF6gNH2gFockwE9IpEoan3+2Dd+/s1fb62ZQ8LS2wrivhrIBOazmM3TQ6HAuLZt21bqjQfZow0CFABow0+61rL/1L1tolH51zJCfwYzddS1sQYzjp/i56/4ff4A9P7V9tbuTtx/gfWkHmYCg8kkbTKbpMKCgoLXDLYUyFwVEqAAQIVOMbJKl0zZe67Egr+XZfm3gDnPyCy0ajvfz+e5+fmDnyfwMVKbelNzdM07/g2HKIkem9U6V5KEwvz8/Coj8SBb1U2AAgB1+8e42rlkoV/rPZfJ8P5Nlm3XUu0BdS8FfpKff9vnp/mN8G3/ZN7gVwM/uLsFTCwqWyzSaqvFwh/6H6vbe6SdUQlQAGBUz2vI7gsm78+xCeEbGfx/hWztTecF1OE8WUbsoe/x81f8QcVy86uDBiAKjD/0t/yitX3uuIsi/+7cubO60heqBRTpoRoCFACoxhWkSDwELnnpYDNRDN0BBO8BzGfFM4b6pI8A38f384e+LwCetEepgjzpsyg1SbGHvlncLEnmKVaH+8Vv7rkwlJpEGk0EskeAAoDssaaZ0kyg95S9XQRZvjPKgncwmLumWTyJq0cg9tD3B+Dh3/Q1fGc/HU49+tA3Ceb/FngO/Ocz14Ak7/+lQxuSQQSSJ0ABQPLsaKSKCPBEQzITrmbMMxiytQ8gWVSkniZV4fn4j37T13KinnTAN0ssbJLE75koTdvU7szJuJ0Z63RjOiCSDNURoABAdS4hhVIlwGsRONCitywEb5IRuQWytU2qMo0wnt/V53v6sf+C/Ju+3i/undyrgsBgMcmlIrO+aZZML65/qPM6I6wBstFYBCgAMJa/DWlt/5d2dgiL4jWM+e+AbLmYShbXLQN+iC8QCsUO8PGHfjBs7DfZZkkOSJK0QmCmGc29h+bTq31D/rkwlNEUABjK3WTsxU+V2AQH+oty+KYoi97IYG5uJCr8Xv7Rb/n+QMiwh/gYYzCb5LBJjG6Tme3laCA0bevoc/cZaS2QrUSAAgBaA4Ym0HfGvrYIyxfLCPcBgpcCljMAIfXKLiqhyvfuA8EQ+H4+f/CHwsbcujZLEswmhCQpukEUHfOdTJ795ZDOZSpxE6lBBBQhQAGAIthpUrUSiBUrsuZcAEQukZn/V5DFiwBzI7XqW18v/kqfv8bnD3z+aj8QDBsuEx/nIYkCzCb+wJfdZsm0zmy2LWWMvbXsnnbbteBH0pEIZIsABQDZIk3zaJbA0bcEUfgvZSzSH7K1kxreEvCiOnUPev7ADyMYCqe1Lr0WHCbEXuWLstkc9pnE8FaTqcnLFsn8qQ/i99/c08qrBRtIRyKgFAEKAJQiT/NqlsDRtwSyLPcEwmczIXKeLIudANGRKaP43j1/fc8f8vxhzx/6Rruax0/mSyKTzVK0RhLZekl0vmGxS++s2Nd+C1xMfyUGM7WYSC4ROEKAAgBaCkQgTQT6zDjQlAVDZ4IJZ0Lwng9EzpchnQ7ZGtcWAr90Fw7zB3049rCPPfCP/Jvn2td7EwUh9vpeEkWIsZ8hr8AiO5ng+FQymT5xStFlH/+54yG9cyD7iEC2CFAAkC3SNI9hCVwx56DdGwh0ZRDORFQ+k7HQedFo9Gx/iLUOBMPs6IOef8vX83M+9oCXxCMPeSZLQiQoipEqkWGXWXKsYqJ1E2SUQJBLvFHxR3qFb9iPDBmeJQIUAGQJNE1DBH5GQJbZBVN2twj7w12ZHOkUlXGaHI22l+HvJMtySzmKvKgsWKOyYIpEwXgK3khUVmyfn1+d4/8JDLGfdf+u+1n3H478b/77SFASwm5RCJdJYmS7ZHauFGTnd7Igl0TDlpJlf21eBsb0/1qDlj0RUDEBCgBU7BxSjQgcJdB/5k4r/GghM1PLIEIdwmH5dDkqt4AAG+RgPliwEaJRhwzZCsAKGRYZglkGzExmogwmgQmiLDMBEAReUVGWGX9ug7FohDE5wlg0LCAaYkwOxv5D1CsIUZ8A2cMEuGXIbiagFrKtjMl5B2UmeJgMXxTwgsEHWS6TJbnk65K2B2lPntYuEVA/gf8DXOm5RA2CKTAAAAAASUVORK5CYII=') !important;
    background-size: 20px 20px !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
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
/* --- Radio Button Styling (Enhanced) --- */

/* 1. Sidebar Styles (Vertical List - Match User Snippet) */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 10px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: transparent !important;
    border: none !important;
    padding: 12px 20px !important;
    border-radius: 0 !important;
    font-weight: 500 !important;
    color: #9391ad !important; /* User's light-grey */
    margin-bottom: 2px !important;
    transition: all 0.2s ease;
    border-left: 3px solid transparent !important; /* Match user's 3px width */
    display: flex !important;
    align-items: center !important;
}

/* Icons in the label (First child usually) */
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* Active State - Gradient & Blue Bar */
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    /* User's Linear Gradient */
    background: linear-gradient(
        90deg,
        rgba(247, 247, 251, 1) 0%,
        rgba(248, 248, 251, 1) 21%,
        rgba(253, 253, 254, 1) 62%,
        rgba(255, 255, 255, 1) 100%
    ) !important;
    
    color: #131340 !important; /* User's magenta-blue */
    font-weight: 600 !important;
    
    /* Blue Bar (User's $dark-blue: #577bf9) */
    border-left: 3px solid #577bf9 !important;
    padding-left: 17px !important; /* 20px - 3px border */
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    color: #131340 !important;
}

/* 2. Main Page Horizontal Radios (Segmented Control Pill Style) */
/* 2. Main Page Horizontal Radios (Dark Toggle Pill Style) */
/* 2. Main Page Header Radios - Force Toggle Style */
/* 2. Main Page Header Radios - Force Toggle Style (Refined) */
/* Target specifically the radio group in the main content area (not sidebar) */
/* Target specifically the radio group in the main content area (not sidebar) */
.stApp section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] {
    background-color: #222222 !important; /* Slightly darker */
    padding: 4px !important;
    border-radius: 50px !important;
    display: flex !important;
    flex-direction: row !important;
    gap: 0px !important;
    border: 1px solid #444444 !important; /* Subtle border */
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    width: fit-content !important;
    margin-left: auto !important;
    margin-top: 12px !important; /* Vertically align with Title */
}

.stApp section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label {
    padding: 8px 20px !important; /* Sleeker padding */
    border-radius: 50px !important;
    margin: 0 !important;
    border: none !important;
    background-color: transparent !important;
    color: #aaaaaa !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-align: center !important;
    flex: 1 !important;
    justify-content: center !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    font-size: 0.9rem !important;
}

.stApp section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-weight: 800 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
    transform: scale(1.02);
}

.stApp section[data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    color: #ffffff !important;
}

/* Dark Mode Dashboard Icon Override */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1)::before {
    background-image: url('data:image/png;base64,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5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBAAPxBIQB+VlTmJoAA5M6f7oMQQAD8QSEAflZU5iaAAOTOn+6DEEAA/EEhAH5WVOYmgADkzp/ugxBA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KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrcBBCA3PnTfRACCIA/KATAz4rK3AQQgNz5030QAgiAPygEwM+KytwEEIDc+dN9EAIIgD8oBMDPisrc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') !important;
}

/* Dark Mode CRM Icon Override */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2)::before {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAAAXNSR0IArs4c6QAAIABJREFUeF7tnQe0LUW1rv9nuIpiDpgzJsxZVMwBMQdUDJizmHP2qpj1YgAxYkIRRVRERTAgCkYw53gVUFEQREC9vv45vWWfc/baq7u6qrq665tjnMF9z670Ve3Vs6tq/vP/CYMABCAAAQhAoDoC/6+6ETNgCEAAAhCAAASEA8AigAAEIAABCFRIAAegwklnyBCAAAQgAAEcANYABCAAAQhAoEICOAAVTjpDhgAEIAABCOAAsAYgAAEIQAACFRLAAahw0hkyBCAAAQhAAAeANQABCEAAAhCokAAOQIWTzpAhAAEIQAACOACsAQhAAAIQgECFBHAAKpx0hgwBCEAAAhDAAWANQAACEIAABCokgANQ4aQzZAhAAAIQgAAOAGsAAhCAAAQgUCEBHIAKJ50hQwACEIAABHAAWAMQgAAEIACBCgngAFQ46QwZAhCAAAQggAPAGoAABCAAAQhUSAAHoMJJZ8gQgAAEIAABHADWAAQgAAEIQKBCAjgA4076hSVtJekCki4o6ULt/72lpC0knb3t3rkknWXcrtI6BCAAgc4E/inpxPbpUyT9XdJJkv4k6Y+Sjmv/HSvpD51r5cGoBHAAouJcs7KLSLp6+++yki4jyf/1v3Okb54WIAABCBRN4GRJv9zk3/ckfUeSHQQsEQEcgLhgLyHpJpJuIOkakq7ZftXHbYXaIAABCNRBwLsDdgT87whJh0n6XR1DTz9KHIBhjK8i6daSbizpppIuNaw6SkMAAhCAwBICv5b0ZUlfbX53PyfpxxALI4AD0I+bt+y3lXRnSXdpt/P71cDTEIAABCAQk8Cvmt/lz7bOwGck/TVm5XOuCwdg+eyeV9JdJe3Yfu2fbXkRnoAABCAAgREInNo6Ah+S9HFJJ4zQh8k0iQOw9lSdU9LdJN1H0u0k8dKfzJKmoxCAAAROJ+DoA+8I7CPpY5J82RBbRQAHYOPlsI2kBzaXTB4h6fysFAhAAAIQmAUBHwt8UNJbm+Pbb81iRBEGgQMg+Wv//pIeKem6EZhSBQQgAAEIlEvgG5LeJul9te8K1OwAWITnsY0wxeNb8Z1ylys9gwAEIACB2AR8P2CvRo/lVbWGFtboAFy1uSX6FEkP4Gw/9t8T9UEAAhCYHAHfFXivpNdJ+tHkej+gwzU5AFbee5akh0k68wBmFIUABCAAgfkR+L9GsfUjkp4n6SfzG97mI6rBAbi0pOdIeih6+jUsacYIAQhAYBCBFUfA742fDaqp8MJzdgCcYOdFkh4l6ayFzwPdgwAEIACBsgicJmmP9j3yl7K6Fqc3c3QAnDXPX/svRYc/ziKhFghAAAIVE/DL/8XN++TNzfGAsxzOxubmAFi05w2SrNGPQQACEIAABGIRcIbCJ0k6OFaFY9czFwfgfJJe0cbyj82U9iEAAQhAYL4EPizpcc2/P059iHNwAO7dbs1caOqTQf8hAAEIQGASBP4s6dmS9pxEbxd0csoOwMVbNaftpzwB9B0CEIAABCZL4IB25/n3UxzBVB2Au7cvf9/0xyAAAQhAAAJjEThe0mPaXANj9SGo3ak5AFu0Z/27BI2WQhCAAAQgAIE0BKwmaHn5k9JUH7/WKTkA12lu9zvH8xXiY6BGCEAAAhCAwGACP27khO/bpJM/cnBNGSqYigNg3X6ncTxHBiY0AQEIQAACEAgl4NwCjhJ4Z2gFucqV7gBY1MeCPs/MBYR2IAABCEAAAhEIOELgCY0UvRUFi7SSHYCLSdpX0o2LJEenIAABCEAAAusTOEzSvSQdUyKoUh2Aq0lyeMWlSoRGnyAAAQhAAAIdCfxO0p1KvBdQogNwm/bL/zwd4fIYBCAAAQhAoGQCJ0q6j6QDS+pkaQ7AQ9rLfmTvK2mV0BcIQAACEBhKwImEHt++44bWFaV8SQ6Acy+/LMqoqAQCEIAABCBQHoF/S3pWE9H2qhK6VooD8CJJLywBCH2AAAQgAAEIJCbwytYRSNzM+tWP7QC4/ddKevKoFGgcAhCAAAQgkJfAm9swQe8KjGJjOgBu2+I+jxhl5DQKAQhAAAIQGJeA34HOIzCKEzCmA+Av/6eMy57WIQABCEAAAqMSeFO7E5C9E2M5ALuWcP6RnTYNQgACEIAABDYn8PoxPojHcABeIOnFrAAIQAACEIAABP5D4LmSXp6TR24HwLrIu+UcIG1BAAIQgAAEJkLA6YR3z9XXnA7ADpL2l3TmXIOjHQhAAAIQgMCECPxL0j3bd2XybudyAK4r6YuSzpl8RDQAAQhAAAIQmC6Bk5v35S0lfS31EHI4AJeR9FVJF0k9GOqHAAQgAAEIzIDA0W0m3F+nHEtqB2DL9uXv7H4YBCAAAQhAAALdCBwlaVtJ3hFIYqkdgA+2GZCSdJ5KIQABCEAAAjMmsLeknVKNL6UD8LTmzP/VqTpOvRCAAAQgAIEKCOwi6Y0pxpnKAfAFhs9KOkuKTlMnBCAAAQhAoBIC/5B0G0lfij3eFA7AVpJ8duH/YtKx7cR9X9KP23/HS/K/kxpRJM+BoyPOK+l8kq4o6cqSfG/iZpIuDMTNCJwq6QhJX2+2x37S/vtto6T11/a87G8ty3NIOrekK0i6Uvvvpi1fsEIAAhCYCoHfS7qmpD/F7HBsB8D1fbIJX7hjzE5OsC6Hb/js5iBJfvGHmnnaEbhtew7kcMpa7Zjmxe07JR+XdLikvw8AcdE2zOY+TV13aNS3/mtAXRSFAAQgkIOAdXTuFrOh2A7A4yQ5sUGN5q/PPSS9S9KPEgG4qqSHSnpkk0b5XInaKKlaZ8g6QJLTZtqZskhGbDt/sytzvzYl9eVjV059EIAABCISeJSkPWPVF9MB8MvpG5K2iNW5idRzXLN9/4bW8fG2fg7zS8sXQ/zPxwZzs/9rv/Zf0ahifTfT4KxQeW9J1uMmbDUTdJqBAAR6EfDxpneCfZw82GI5AGdtz2SvPbhH06nAL6l3tFkN/zxSty8k6VWSdm7vEozUjajNflOSd5J8xj+G+eKq9bhfIuk8Y3SANiEAAQisQ8Af2jeW9M+hlGI5AM+R9LKhnZlQeV8880vXZ9ElmC+2vVvSlLewT2nO9Z/Z7qTYuRrbfIn1rZLuOnZHaB8CEIDAJgSeESPMPoYD4FvrvvV/9kqm6COSHt7e4i9pyL7t7hfWfUvqVMe+2KHyhbwjOz6f87EHtXc7ajvaysmYtiAAgX4EfAn6GpJ+1q/Yxk8PdQBc/guSthvSiYmU9Vfpk1IJMkRkYAEmHwsMnduIXVq3qk+1L3+HRJZqN2jO3T5BSGap00O/IFAlgUNafQBflg6yoS8J30j0zfe5m+PO/SW4z0QGev82GsF3M0q297S7KRa6KN22lvRpSZcrvaP0DwIQqIaAo8IceRZkQxwA30T31u0FglqeTiG//O/SKhtOp9fSDo1wxH7N3YxSnYC3NKIWj5cU7L2OMBnOaOm01j72wiAAAQiMTeAP7e/RCSEdGeIA7CbpCSGNTqiMt/0dIz6VL/9N0brv72tutJ+pMOYW9PEuRQmX/fqiuYSkrzQRIJfsW5DnIQABCCQg8NpGVdZHv70t1AG4Snvxr9Svy94gFhSwgzN1YaPSkjId3CpFnhZrkkaox5dvDm1lhkdoniYhAAEI/IeAf0uv3u7I98IS6gAc2Eqo9mpsYg9/aKI36tfC/IF2J2PsKXBehGtJsqzv1G1HSV4jGAQgAIGxCViC/859OxHiANyuESH4TN+GJva8VZau1ybrmVjX1+yuEw1ZYGfMC2yW8XVGK0eNzMUsyfmIuQyGcUAAApMmcOsmIs+RAZ0txAGw+M0NO7cwvQd9Lm2VJSf0mZM5s6AvsIXMeQwOr24y9Vm8Yk5mbYDvjexYzYknY4EABMIJHCbJonCdre/LwFsMzsY2Z3NY42NmOsC92nDG3MP732a73PdGSo71D2Vy+zY8MLQ85SAAAQjEIrB9n9+jPg6An/U28pz1/p1r2Xnjx9L2j7UIFtVz4TaJhI8EcprPyz+cs8HMbdkp7n3+lrmPNAcBCMyfgPMEWLisU3h1Hwfgnk2WtH1nzs85DXad+Rid5Ob5Gcf47WbX6DoZ2xujKd/AtRx2n7+nMfpJmxCAwPwJ3K35UN+/yzD7/GA5O5s9i7mahRQuU6DGf2zeFnD6laRzxa54QX3W+J+qjkIfRJYKvlOfAjwLAQhAIAGBr3d9V3d1AG4+s9vbazH3l793AGowC0c8JcNAnajiys2OgyMA5m43aaIcvjz3QTI+CEBgEgR86Xvp71FXB6CGrxu/qBz+V4NdVdL3Mwz0uZJenqGdUppwRMA2pXSGfkAAAtUS+FhzLHn3ZaPv4gD4UtwPCpSTXTa2Pv+7pV39BVeT+WzeojypzJdQLi/pl6kaKLDe50n67wL7RZcgAIG6CPj31x8jP1xv2F0cAIfFOevfnG0Okr995+fpbdrgvuW6Pu/tJ29D1WQWWvp5TQNmrBCAQLEEdpf02CEOwJaSfp/xwthYJL3L4cyGNZnDOb+VcMCONHhpwvpLrdrryKmDMQhAAAJjEjhR0sUl+b9r2rIdgEdKeuuYI8jQth0cQ6rNnCHQ2vwXTDTwTpdQErU9ZrXIA49Jn7YhAIHVBB4m6Z2hDoDlcK8/c557N1//O818jIuG99EuF0UC2PxdksWGppzxL2DYpxfxWnp/aGHKQQACEIhIwNL9lrbvvQPglKcWN5m71XZTffV8+sKaL67FthrEfxYxq+XvJvaaoT4IQCANAV/2XvNdvt4RwG6SfDlu7navJpfyR+Y+yAXje0BzU/+9CcZu4R8LANVoThDknAc+YsEgAAEIjE3g9Yt0XxY5AGeW5AQuFxm75xna9xfbdzO0U2ITVna0wmNs8+W/nHLDsfs/tD4rLV56aCWUhwAEIBCBwO+aewCXkuRMtxvZIgfgVk0I18ERGp5CFRdrwhyPnkJHE/QxVdjaEyV5B6lWsxTn9WodPOOGAASKI7CdpEO7OgA1xP6vsDj3emESxU1j3A45AuCPcas8vbZ1b54maK+0Kg+RdMvSOkV/IACBagm8WdLjuzgAZ5HkLQOnjp27WS3J491sa2TuA2/HdzZJpyQYay0JgBahcyauuyTgSpUQgAAEQgg45Nvh7hvlZVnrCMBfLv6CqcFqdwD+S9KpCSYaBwAHIMGyokoIQGAAASf1+9Lq8ms5AK9ubjE/bUAjUyta8xHABZptoT8lmLDajwA+32TPvEUCrlQJAQhAIJTAK5oPvmcvcwBqy2hW8yXAyyRK1lP7JcBvSLpu6F8p5SAAAQgkIGAtgI0SwG26A3BJSb9J0HDJVS4USSi505H6lioM0AJDL4jUxylW4wyIdq4wCEAAAqUQ8JH3Jdr8Pqf3aVMHoAbt/00n496S9i1lhjL3I5UQ0Ick3TfzWEpp7uytEJC1NDAIQAACJRF4aKNR8q6VDm3qAPhFeM+SepuhL5bCfVmGdkps4sWJvtSPlORsgzXa1SV9p8aBM2YIQKB4Aht9nG3qAFgQpwb1v9WzVPPXaqpkQCe3yYD+UfyfQ/wOeufDCaYwCEAAAqURcIi/jwFOt9UOwOUl/ay03mboj50eXwSszTz3f0iYDnhbSV+tDaqk3SU9usJxM2QIQGAaBHw/6debOgAPkrTXNPofvZdXlvTj6LWWXeE1JXmrPpXVerTykyYd8NapoFIvBCAAgYEEfPfr9JTlq3cAapL/3ZRfjWFrz5D0yoELab3iX6hQDtcJgJwICIMABCBQKgHvUj52UwfAMYLOjFejOSPejSobuL/+vQuQyiyv7Beis0rWYhbZeHktg2WcEIDAJAn855L2yg6ANeFPbG7Dn3WSw4nT6StJ8vZtDXZVSd/PMFC/EK0+VYs5rfTVahks44QABCZJwJezt5R02ooDYDGcb09yKPE6vZlMYryqi6vp9ZKelKFXvldhZ6OGZEs3lHR4BqY0AQEIQGAoAe/2f3fFAdi5US5799AaJ17+r+2W9fETH8ey7p+/vQFqDzCH3aM5atgvR0Mjt/Gxxom+68h9oHkIQAACXQicfhFwxQF4TXME8NQupWb+TA1b1qnEfxYtDe8sWRffMpRzNe9yePv/THMdIOOCAARmRcAXwJ+14gB8RtLtZjW8sMEc14i4+C6A/ztH26oNdzxP5sHNfReAr//MC4rmIACBQQQOlHTHFQfgF40GwGUHVTefwg6HfMx8hrPRSKzzYL2H3OYEU/5K/lvuhjO0d/smguTTGdqhCQhAAAKxCPxU0hXtADhpyd8rjwBYDdUX1hwS+PVYpAup56aSvrRGAqhc3ZvjJcst2q1/q2hiEIAABKZC4LRGB2YLOwCIl2w+ZZZE9rm1LwbOwbzl77P4MXd5/tk4ILeSdOgcgLZjQPZ3RpPJUCBQGYFL2gG4haTPVzbwLsOdU5KgDzRn//frMujEz1gUyFkC/5S4nRzVO430Pjkaog0IQAACCQhsZwfgwavzAydoZMpVPl7Sm6c8gDa6w1EepdhBzfHKDpKmnCnQKX+/LOncpUClHxCAAAR6EtjZDsBzJb20Z8FaHv+XJKd33XeiA/ZX//sKDE9zIooHTjQ08FJNxMxXJF18omuCbkMAAhAwgefYAcilCjdV5KdKupOkz01sAHdottv3b7Tp/6vQfv+PpCdPzAm4cHNk5iRHVymUKd2CAAQg0JXA6+wAvFeSVYGwxQR8Y9Lhc74XMAW7Z/vlf/bCO/ueJlnQwydyHOALlA73u2LhTOkeBCAAgS4E9rID8ClJ23d5uvJnHB64ywTuBFjR8VUFbvsvWj6faJIw7STppILX1/WaqBD38yIF95GuQQACEOhD4AA7AF+TdP0+pSp/1vcB/NV6QmEcfCHtre2dhcK6trQ7Thp0H0lOSV2aeefH4lCO+ccgAAEIzIXA4XYArAh0hbmMKNM4nDbYxyaliAVt2x7lXC7T+FM0YzGqp0tybH0J2QN93u8IkHulGCx1QgACEBiZwE/sADg2mxvN/WfCyW18w95b7n/sXzxKCWf2e2ETV+9wxbkkovmWpMc2x1JHRCHUvxJztHP3WkkX7F+cEhCAAAQmQeA3dgCOleSvHSyMgBMH+WXxlozHAudrX/q+Re//e27m8Mu9Je0q6QeZBucXvy9PPk+Sc2VjEIAABOZM4Fg7AMc3oYC5s8PNEarvBPis+B3tsUqKMV5Z0sMkPapxOs6VooHC6vRRwH4t10MSHQ3YgdpR0hMJ7yts9ukOBCCQksDxdgBO5oJTdMa+WOkvWKdZ/uGA2j0/zqLnjHO+Ke/8BLWaj6rM9ABJh0uyPkOoOS3yLdsvfms8lB4uGTpOykEAAhBYROBkv2CcpMUZAbE0BI5ps/B9p90Z8KVL3xlw2Jt3X2znlbRlc+nsQm2c+dbNl+81JW3H8cyak2Kn9bA2wZEvZP6o2RU5uvmK/0vL1TLD52x3Sby75Wx93j25kiRfmNxmxKyIaVYZtUIAAhDoR+BfdgB8mQ2DAAQgAAEIQKAiAjgAFU02Q4UABCAAAQisEMABYC1AAAIQgAAEKiSAA1DhpDNkCEAAAhCAAA4AawACEIAABCBQIQEcgAonnSFDAAIQgAAEcABYAxCAAAQgAIEKCeAAVDjpDBkCEIAABCCAA8AagAAEIAABCFRIAAegwklnyBCAAAQgAAEcANYABCAAAQhAoEICOAAVTjpDhgAEIAABCOAAsAYgAAEIQAACFRLAAahw0hkyBCAAAQhAAAeANQABCEAAAhCokAAOQIWTzpAhAAEIQAACOACsAQhAAAIQgECFBHAAKpx0hgwBCEAAAhDAAWANQAACEIAABCokgANQ4aQzZAhAAAIQgAAOAGsAAhCAAAQgUCEBHIAKJ50hQwACEIAABHAAWAMQgAAEIACBCgngAFQ46QwZAhCAAAQggAPAGoAABCAAAQhUSAAHoMJJZ8gQgAAEIAABHADWAAQgAAEIQKBCAjgAFU46Q4YABCAAAQjgALAGIAABCEAAAhUSwAGocNIZMgQgAAEIQAAHgDUAAQhAAAIQqJAADkCFk86QIQABCEAAAjgArAEIQAACEIBAhQRwACqcdIYMAQhAAAIQwAFgDUAAAhCAAAQqJIADUOGkM2QIQAACEIAADgBrAAIQgAAEIFAhARyACiedIUMAAhCAAARwAFgDEIAABCAAgQoJ4ABUOOkMGQIQgAAEIIADwBqAAAQgAAEIVEgAB6DCSWfIEIAABCAAATsA+4ABAhCAAAQgAIG6CNgBwCAAAQhAAAIQqIwADkBlE85wIQABCEAAAiaAA8A6gAAEIAABCFRIAAegwklnyBCAAAQgAAEcANYABCAAAQhAoEICOAAVTjpDhgAEIAABCOAAsAYgAAEIQAACFRLAAahw0hkyBCAAAQhAAAeANQABCEAAAhCokAAOQIWTzpAhAAEIQAACOACsAQhAAAIQgECFBHAAKpx0hgwBCEAAAhDAAWANQAACEIAABCokgANQ4aQzZAhAAAIQgAAOAGsAAhCAAAQgUCEBHIAKJ50hQwACEIAABHAAWAMQgAAEIACBCgngAFQ46QwZAhCAAAQggAPAGoAABCAAAQhUSAAHoMJJZ8gQgAAEIAABHADWAAQgAAEIQKBCAjgAFU46Q4YABCAAAQjgALAGIAABCEAAAhUSwAGocNIZMgQgAAEIQAAHgDUAAQhAAAIQqJAADkCFk86QIQABCEAAAjgArAEIQAACEIBAhQRwACqcdIYMAQhAAAIQwAFgDUAAAhCAAAQqJIADUOGkM2QIQAACEIAADgBrAAIQgAAEIFAhARyACiedIUMAAhCAAARwAFgDEIAABCAAgQoJ4ABUOOkMGQIQgAAEIIADwBqAAAQgAAEIVEgAB6DCSWfIEIAABCAAARwA1gAEIAABCECgQgI4ABVOOkOGAAQgAAEI4ACwBiAAAQhAAAIVEsABqHDSGTIEIAABCEAAB4A1AAEIQAACEKiQAA5AhZPOkCEAAQhAAAJ2APYBAwQgAAEIQAACdRGwA/DvuobMaCEAAQhAAAIQwAFgDUAAAhCAAAQqJIADUOGkM2QIQAACEIAADgBrAAIQgAAEIFAhARyACiedIUMAAhCAAARwAFgDEIAABCAAgQoJ4ABUOOkMGQIQgAAEIIADwBqAAAQgAAEIVEgAB6DCSWfIEIAABCAAARwA1gAEIAABCECgQgI4ABVOOkOGAAQgAAEI4ACwBiAAAQhAAAIVEsABqHDSGTIEIAABCEAAB4A1AAEIQAACEKiQAA5AhZPOkCEAAQhAAAI4AKwBCEAAAhCAQIUEcAAqnHSGDAEIQAACEMABYA1AAAIQgAAEKiSAA1DhpDNkCEAAAhCAAA4AawACEIAABCBQIQEcgAonnSFDAAIQgAAEcABYAxCAAAQgAIEKCeAAVDjpDBkCEIAABCCAA8AagAAEIAABCFRIAAegwklnyBCAAAQgAAEcANYABCAAAQhAoEICOAAVTjpDhgAEIAABCOAAsAYgAAEIQAACFRLAAahw0hkyBCAAAQhAAAeANQABCEAAAhCokAAOQIWTzpAhAAEIQAACOACsAQhAAAIQgECFBHAAKpx0hgwBCEAAAhDAAWANQAACEIAABCokgANQ4aQzZAhAAAIQgAAOAGsAAhCAAAQgUCEBHIAKJ50hQwACEIAABHAAWAMQgAAEIACBCgngAFQ46QwZAhCAAAQggAPAGoAABCAAAQhUSAAHoMJJZ8gQgAAEIAABHADWAAQgAAEIQKBCAjgAFU46Q4YABCAAgeoJnIoDUP0aAAAEIAABCFRI4E84ABXOOkOGAAQgAIHqCfwAB6D6NQAACEAAAhCokMB+OAAVzjpDhgAEIACB6gm8BAeg+jUAAAhAAAIQqJDALXEAKpx1hgwBCEAAAlUTOEHSVjgAVa8BBg8BCEAAAhUSeIekh+MAVDjzDBkCEIAABKomcGNJh+MAVL0GGDwEIAABCFRG4GBJt/GYcQAqm3mGCwEIQAAC1RL4P0nbSjoCB6DaNcDAIQABCECgQgJvl/SIlXGzA1DhCmDIEIAABCBQHYGfS7quJEcAnG44ANWtAQYMAQhAAAKVEThZ0s0kfWv1uHEAKlsFDBcCEIAABKoi8C9J95L0sU1HjQNQ1TpgsBCAAAQgUBGBUyTtJGm/tcaMA1DRSmCoEIAABCBQDYFjJO0o6dBFI8YBqGYtMFAIQAACEKiEwGcl7SzJTsBCwwGoZDUwTAhAAAIQmD2B30h6pqQPdhkpDkAXSjwDAQhAAAIQKJfAdyXtJuk9kk7r2k0cgK6keA4CEIAABCBQBgGH9X1D0iHt7f6jQrqFAxBCjTLLCBzbqE39TtIfJR236p8X7YoIxamS/P/GIAABCEBgOYGTJPmft/n979/Li6z/BA7AUIL1lj9Rkred/O97zYWTX7b/fsWLvd5FwcghAIHpEMABmM5cjdnTf0j6pqSvSDpM0pHty36wBzrmoGgbAhCAQM0EcABqnv3FY3fGKJ8vHdjIRzp1pP/vv4MKAhCAAATmQwAHYD5zOXQk3tL/pKQDmnSRjiH1+T0GAQhAAAIzJYADMNOJ7Tgsf9X7C//Dkj4i6W8dy/EYBCAAAQhMnAAOwMQnMLD7X5b0Nkn7cmEvkCDFIAABCEycAA7AxCewR/cdjmeRCL/4f9ijHI9CAAIQgMAMCeAAzHBSNxnSL1qFqLezxT//yWaEEIAABLoSwAHoSmp6zzlk7zWS9pfkW/0YBCAAAQhA4D8EcADmtxiOkPQySZ+Y39AYEQQgAAEIxCKAAxCL5Pj1WJznBbz4x58IegABCEBgCgRwAKYwS+v38ejmf36RpHdI+tf0h8MIIAABCEAgBwEcgByU07ThlI97NC/950v6a5omqBUCEIAABOZKAAdgmjNrpb7HSPINfwwCEIAABCDQmwAOQG9koxY4vtHkf2Yby08inlGngsYhAAEITJsADsATHsf9AAAgAElEQVR05u9DknaR9IfpdJmeQgACEIBAqQRwAEqdmTP65fP9p0vas/yu0kMIQAACEJgKARyAsmfqcEkPkPTzsrtJ7yAAAQhAYGoEcADKnDEr971E0ksJ7StzgugVBCAAgakTwAEobwa95b+zpI+V1zV6BAEIQAACcyGAA1DWTB4l6R6E95U1KfQGAhCAwBwJ4ACUM6v7tl/+J5fTJXoCAQhAAAJzJYADUMbM7ibpyWTtK2My6AUEIACBGgjgAIw7y9buf6KkN4/bDVqHAAQgAIHaCOAAjDfjp0jakex9400ALUMAAhComQAOwDiz73P+u0k6aJzmaRUCEIAABGongAOQfwWcIGkHSYflb5oWIQABCEAAAhsI4ADkXQlO5nNbSd/I2yytQQACEIAABDYmgAOQb0V42/8Okg7N1yQtQQACEIAABNYmgAOQZ2X8vd32/3ye5mgFAhCAAAQgsD4BHID0K+S09sLfgembogUIQAACEIBANwI4AN04hT71b0kPkbRXaAWUgwAEIAABCKQggAOQguoZdb6ouWj54rRNUDsEIAABCECgPwEcgP7MupbYW9L9JXkXAIMABCAAAQgURQAHIM10fLm57X9rST7/xyAAAQhAAALFEcABiD8lxzTyvteV9Pv4VVMjBCAAAQhAIA4BHIA4HFdq+Uf75U+sf1yu1AYBCEAAApEJ4ADEBfoESW+KWyW1QQACEIAABOITwAGIx/Rjku4erzpqggAEIAABCKQjgAMQh63P+68h6bg41VELBCAAAQhAIC0BHIDhfP9P0u0lfW54VdQAAQhAAAIQyEMAB2A459dJeurwaqgBAhCAAAQgkI8ADsAw1j9rt/6d7AfbnMBZJV1F0rXa/27VXJK8YPvvwpLOvwa0v0j6U3uccnQjpvTT9t9PJP1IkiMtsHQELippO0nbSLqSpCtKOq+k80g6l6SzRGz6REmnNA60//s3SSc10tm/lvQLSb9s//vz9v8vYrNVVnVpSbdqQ5SvKumSki4g6dzt35T/5hzC/K12N/NgSX+uklT/QV9E0m3aVO8+Cr5Q+881eV2b628lfa9NBW+2f+jfTPwSOADhTK3wZ7EfMvydwdA/KNs3TG4u6dqSribpbOGINytpR+ubTRtHNH9wFls6RNJfI9Zfa1XbSrpfu57tsJVm/rE8vJ33rzaZNb/eOgul9bO0/tjZflDjTO3cfqj06d+pkt7fOAje4fx+n4IVPXuj5vfnKZLuIenMPcbtY2Ov53dJ+uCYaxkHoMesbfLo2yU9Irz4bEpeuXkp37nxbO8k6SY9/xCGQrDSoh2BTzXOxr58KfbCeT5Jj2mTVV2hV8nxH/a82/F25M3HEd3abEK8Y/PMZhfNYcnnHDhd/tB5d3vM6d05TLq4pLc0uyV3iQDDOy+vanZj3tjuhkWosnsVOADdWa1+0ls6/lI6Pqz45Ett0WzH37fZxnqspOsVMhp71RZgcubFj7AzsHBWfPTirxbPnbf0p26ed+8IfKid+9q3re2M7yHpYpEn1sdxD5NUe1rzBzZHl7u1x2IxEf9Q0kPbnYGY9a5bFw5AGGpPlLdvarPLNV9bj2x/CLy9WKr5LPkDzQvutZJ8dwCTziTpAe2Wro9q5mjetvaOwJ4VRuX4t/wZzZHbrk0GUv/fKexfzUfPkyoVOzPTF7b/UrB1nf9snXPvBmQxHID+mH0GfQNJ/vKoxXxhyKmNfZbY56xrbD7+g/JugFMy28Ou1XyhzzsjzlFRix0l6RWS9qngb9XO3dvaL8gc82uuz87RUCFtmK//fuxA57DnN5dtX5qjIRyAfpR9HuYb0j53rsF8Tuw/9MdL8rb/VM1fLv4DthPj27g12UPaL7Zz1DToVWP1zWvP+0dnnJrbW9I+789pDn32BcEa7H+aiIhdMg/U7SXfCcAB6Der/pq4T78ik3zaHq9f+v7htBMwF3PI2SvbbVJvF8/ZHK63u6SHz3mQPcZ2ZHsx7rM9ykzhUe/K+ZJebvMOqH8Lffl2zvbkkRwd7146tPCLKeHiAHSn669Ih7U5Fn3OdhlJ72wW3i1nPEjrN/gS3EEzHaNDLx3Cdc+Zjm/IsD7ZRj/875BKCil7qTZEb8uR+uMYd2t8+O9pjuYwP+/2jnXs+ZtWj8N3mpIYDkB3rN5CfnD3xyf3pNfCo9uQlLF+UHJC83GOQ3me3nwZzknIyUc1vqltLQZsbQKO3nlue1t+ynd59o8UijZknTjy5hYzvGfhv6Nvt2JYQ/gMLeuLzE8bWsmi8jgA3chafc7x7lYom6N5m9+35u8wx8EtGZPPiB3SOAexE2/7+6zboWDYcgL+urMA0hR3A/x1alGkEsyRAT4nn5P5xetw2bHNx5bW6fhdio7gAHSj6hu2Dn+bo9mxcejU1nMcXMcxeQfA8/u+js+X+tg7Mt4EL5VB335ZiMU7ewf0LTjy8/6bLcXRs/aCQ4RPGJlJrOZ9DPpjSf8Vq8KB9byhYeu7CNENB2A5Um8RWhN9judczmJoKUorh2EbBD78hzbFbWGrUjr+HetPwMdBvnHt4yCrDJZuVqJzzoSxzqbX4vOSxDHyOefElyp9ubIUs4NlYafoF5dxAJZP8X6t1vPyJ6f1hMNMHMZT0o9ICQQ93/ef2L2Aq7c6+VMO1Sxh7p1bwrrupX/JWubXsfglmRM6eRfAOypTNn/s+TiwtN9FX+j18V5UwwFYjvOmTZanw5Y/Nqkn/KVj/WlsbQLWmbfOd7LbtxHB+9zf4lTOQoYNJ/CdNqHV74dXlawGX7zz71Jp5rBhi25N2XzcW2LorHclrOkR1XAA1sdpjXGr/s3JLODxmjkNKNFYPPe+FFm6trwvKvnCEhaPgF/+zmppZ6A0c/6G4yQ51XZp5n457bDDA6dozpPho5WzF9h5XwK8ROx+4QCsT9TSj46nnotZK9xCOFg3Ak7ZaTGOUn/QLtpeVppDUp9uM5LvKTt+nnuHgpVk7lPJ+hXOMOlkRFM0y+86PLRU8xHLL2N2DgdgMU3/APiyjcMw5mD+w3TcO9aPgGPq79r8MDgUtDTz7eAnltapGfXnD62eQkniX2Mp03Wd1p+2IdNTu0jrtMkW3jl/14GO8Jx/hxz9Ec1wABajdFyr41vnYP5q8IvM58VYfwIOD3xQYVryF2rC137V3OWoVeO//yyGlbBGgM/bvTVcgk0h1NMXKX2ZdkrmXAqOAirZvDvx8pgdxAFYTNOyv3MQh/GtVguGzEnTP+bfQNe6ov/xdW14wXMOu3LWMCw9AX/V3qyRED42fVNLW/iMpNstfWrcB77SHFPcZNwu9GrdN/6dNtxb7CWbj1a8kxvNcADWRumz3xtHozxeRd7O8lhqFvmJRd+5IO4oqYRkMk7W5K9/p2nG8hBwJJDzY4x9FOSLiQ77LN3sANgRmILtKOlDE+iot/99DBDNcADWRulzNp+vTtk8t5+QtMOUB1FY333L+boFbAffutmW/lxhbGrojreIx75z4V0I31Yv3aakn/K1Rgny+qUDbT5A3M8bxuwnDsDmNH15xVm2kmgvx5y8JXWhDJcG9pfaL8ExLzm9XdLD0gyPWpcQ2KlRBt17JEr+vbZS4RTu8vjvwzLjPj4p2Zw06wsld3BV337e5gWI1l0cgM1RWmRju2iEx6nIZ1lHNfH+NWT1G4OwY+9fP0bDbZu+kGYnFctPwCGh/gob437QeZqLyc5kOBWLfmadYODeJb1TgnpTVPmX2FEKOACbT5Nvg74pxexlqtMXWuzRlqgUlglB8macPOg6TRbBMcLDLj/TvBTJJy1iA96K3ba5hOl7ITnNjr2/Aqdi/juxMNAfC+3wVVpHzu/BKZh3VZygKNq6wwHYfNqdCaqUkJ+QRenQxTG/TkP6PMUylgu+1Qgdf2hz+c+hYNi4BMa4J3S95k6PFSqnZJYGtkRwiTbFozSH/0bLt4ADsPGy/IGkbUpcqR375Fv/PnMrWcyi41Am8di9Je2buael5CnPPOzimju5vY3/i4w9szS19TymZKXKA2/VRtKUKPu73vz6XoVTFUcxHICNMfrH9WlRyI5TiY8uHjdO01W26p0ibyN6qzOXfZLIjlyol7bjmHy/lHPZ/SR9IFdjEdspUR64dNnfRfh99GRdlyiGA7AxRivmHRyFbP5K/CJyjPAUbgjnp5OuRWdWzJlcyYIl6Dqkm8++Nd8+ozbE4yW9sW8HC3i+NHngKcj+Lpq2O0vyR0AUwwE4A6O/4qyWd2oUsvkrOaAVqsnfct0tHi3J90YcnpXDnKMCVcccpLu1cYSkG3V7dPBTL5hwut2S5IGnIPu7aLHs3CgWvmfwSmorwAE4g+QXm9vzt4gFNnM9U7wclBlR0ubuJmn/pC2cUbkdjRJTwWYafpHNRP0qW2eEzk+yS5EElncquojN8ibXfMJRUj5DdzTNFC1qCDIOwBlLYNfmK+45U1wR7bmgzwexcQg4ZbRTR6c2X1jKed8g9XjmUr9TBlsh8t+JB/TeTOss1TBKkAeeiuzvojnw3YVoOUBwAM7AbDEIb6NPzSwI49hgzv7HmzmrRl4iQ/PnlnRChnZooj+B7ZujgE/3L9arxNSP+UqQB56K7O+ihbG7pMf2WjXrPIwDsAGOPfcLNttrPl+dmvkC2lOn1ukZ9tdhRc4fn9JwAFLSHVb3RyXdc1gVS0v7vsENlj5V7gMWsnGY9RgCWqbiI17rd0zZnLTovrEGgAOwgeTPJnqz2lK/zlduidApmM+vLWTiMJZftoJLvkTndeiX2xZNHvFrNrdcfafBcqsXn8Kg2j7m2N4syQHwHFmaNJb5YqP/OX21VRb9Y116etbVY3eWQO/GHRMLyBr1zCECZEx54CnJ/i5aRgfFTAeNA7ABcwlbUyG/G/dvkkO8L6Rg5jLfa8OXPtzjpeG16RzsD5F0rwnkNXDWxU8l5lqSAxBVkWwBt2s0Yi0PbhMfeeyl27MlvSJhJy2qM3WRr7Hkgacm+7toGX2rvW8SZZnhAGzAWLJc5XoT7fzQvoFcqnl3wpKpHxl4QeoC7Rw9quC7DjkiAWpzAFbW9XnbdfSM5gVbsnJbyp1E3173DtqZSv1j79GvMX5vpyj7uxbSX0m6bA/W6z6KA7ABj8/ufIY3JfN2qbcbnRyiRLNi2aOb+wknRuzcVZuY+3cXmrs7h4hUrQ7AyhJy6NZeknzcUqp51+K7CTpnJziaBnyC/vWp0smBnCQoV0TLRVrZ37P16WShz/r3NNpuGA7Ahlm+4gTyVm+6HktNCuMLlc+S9KpEf0D+AvRNWG8Nl2RRNboXDKx2B8BYHO3iteWdpRLNuxSvTtAxqz/6DsBczDfZ/Xecw1424RDvtfjYkYkiPIYDIP2zvXzm/07JHHJkGdLSzNkILViS2uxkWLuhBLN65Lkk+SJYSsMBOIOuBVEcAVNaKtdDJN06wSKw2mA0DfgE/etbZS554CnL/i5ietFYl01xAKSoZyp9/woCn/e2v29gnyOwfKpiTkPsH+Zc5i9Ba/GPbYdK2i5DJ3AANob83GZHwMIoJZm/zLxdf1LkTt1xojol62HIcfRq5cQcHySRp3vd6hxK6cy1gw0HQPqCpFsOJpm3ghs3oSBfydvk0tYssHHTDF/Bqzvi9WsVvrFVEP0ievlSQsMfwAHYnKF10R84HG3UGlJIA3uM0TTgo442vDLvaDi7XSrzcZGPTaJdmkvV0Z71+mPDHx2DDQdgw6Uyh5pNyZ6ZONyoLwt/9Th+fwyBD2sgfH9EzQCLmzhe3amBUxsOwOaEvcXr0Cjf4ynFnLTnvyN35omS3hC5zhKq80fDYYk6ch9JH0xU95jVRos4wgGYZghgaTnhfenJl5/GsrtkTMaz6Rgd4midghyGA7A2ZZ+5fy7HBHRsw3oX1pyPaS+JqQEfs2MD6/qYpLsPrGNR8anL/i4a18Ma0al3xmCGAyA5x/abY8DMVIfjgC0I4tjoEsxnnU6H6z6Nafs0OwH3ztyBf7Wqdd/J1C4OwGLQJWlieCfMwjMx7U2SHhezwkLq8g6aWcWOcLh5oybp4905mu89+QLsYMMB2KCrbH3lqZhftpbRLcW8LVlCSJaT8fhijG/j57LdmsuY3prNZTgAi0lbI99a+SWYHUOvw5hx7nvH1IAvAdKqPry11QyJ2a05yP4u4mG1SatODjYcAOm2hW0fLptU9/ezyx7K+L9Hu5Eaoc85pZF97+D6kX/klyHAAVif0DfbHZllHHP8785n4DTBsewzMTXgY3UqUj2x5YEtGGb58dJCRCPh0p6SrIo62HAApGtLOnIwyXwVPEbSW/I1t25LTuxTWnayHNkRj23V6JyGOafhAKxP2ztRr8s5Ieu0FTu9+DdiasAXwmh1N2LKA89F9nfRNEW7d4QDsOH8OscN7lh/c/6BK2HL3eNJcdt5KCevad/psKOUwvzytwDTUSkqX1InDsD6gPzl552ZEuzhkt4RsSO/mGE422o8ljm2PPDJA5nNSfZ3EQqnNL7VQE6nF8cBkKKpKsWYkA51lHS25S1wf5mUaFYKtEiMk6jEMl/2s3iJk76MYTgA61P375kdNGcqHNtia0OcEFMDfmw4C9qPIQ88N9nftVD5d8hh14MNB2CDatefB5PMV4HPFa+Vr7mFLdlTdwx+yRLKjjF+WxMLbJ3+IeYxvrEROfKPesyLXX37hAOwnJhvfvsG+NjmnbqnRurEWZtLX5abnuuZ9gomO9b+W/UlyhDbst3NnXrK5GVjd5bVSy57qMv/jgMgedH8rQusQp6xhvYVCuhLLvnboUP1j6cvzPjH2Mc9fcw/RD5v805CigxvffriZ3EAlhNzfHQJwl4O23vC8u52emKrWNrvnVob96Eh8sBzlP1dazb8ERJFBh4HYEM63dRJXGL+SR0tyedcY9seCc/ZU4zNRwGOoLBWwC1a9b5Ff1yHSzpQkkOv7G2XYjgAy2fC+SickGpsi3ZTu42Tj6L9PjaUDu2HygPPVfZ3ETI7AIN3I3EApretZuEdy5+ObU764x/bqZqPLyzh6yMg/x3YCfxN+6/UYw0cgOWrzTHSlsoe22JKjPsoK4r2+9hQOrYfIg88V9nfRcise/K7jjwXPoYDMC0HwCqAfjmVcBboPzir72H5COAALGddimKe7548cnl3Oz0xptR1pw5GfihEHtghydeL3I+Sq/MlwMEKpDgAZbxMuy4031c4sevDiZ/bXtKnE7dB9RsTwAFYviKc/MXO6dgWMzX2g5sQuXeNPaCM7feVB/aRnkPjajJnsB0sdYwDMC0HoKQXgNN4+rwOy0egpPl3qJ1jt0uzUqJknA3QOhkx7GnNsZ8TbtVkfeSBD5B0x5rgtAnIfEF5kOEA4ACELqCrt3KboeUp158ADsD6zM7e5Gb4S5Mq2/8d25wdM9ZLu4bY9k3nyxfcHLXzhyUTOXfZ30XD9/GSj5kGGQ4ADkDoArqUpN+GFqZcEAEcgPWxeVv0kCCy8Qvt1EaRxKjZX8Ox7hPE6E+uOrrIA1tt8aG5OlRQO04G5AuvgwwHAAcgdAGVugUcOp4plMMBWH+WnJkyZ3bG9XqzXcSb+2Okui7h72GZPLBVXJ0Z9WwldDZzH7y75F2mQYYDgAMQuoBwAELJhZfDAVjMzoJP3pGyaE4J5hDTWGm7D46l/V4CmJ59eNw6yc9eHistbs8+lfC4Ba8eNrQjOAA4AKFrCAcglFx4ORyAxexKuil/iqRzRZTJLuViY/jKDS+5SB7YEVHW7ThfeNWTLhkSKrnZgHEAcABC/wpwAELJhZfDAVibndU8nf9963C0UUt+M3JMul90UbTfo44yX2X3aiW5V7dYi+zvIspRpNhxAHAAQv+McQBCyYWXwwFYm91zJPmmfCnmi2lOBxzLnHhri1iVTbAei/zcYFW/Lev9k3XkvCc4xN5ddtrrq/UutUkBOwBWlouZMnVon3KXL0FVr+uYeQF0JTXP55j/zef1GpKcu6GkF6S/Tp09MoY5pHGw5nuMjoxcx2p54Npkf9dCf4w2pLIfZH75eXGVEDc7aCADCuMAhMFjByCM25BSOAAb0/P5r8WorjQEaoKy15Z0ZKR6LxZD8z1SX8asZvWZd22yv2txPy1G9INffie0aUbHnNwx28YBCKOPAxDGbUgpHIAz6PmL/zOSbjYEaIKyxzW31i/cqABazjaGWXBrsOZ7jI6MXMeKPLAdotpkfxeh9+/BIGl4v/wca+mMaLUaDkDYzOMAhHEbUgoHYAO980ravxH9cax9afZRSc5pH8tq1LlfxM6CSL4MWZvs7yIeVkr89ZCF5pefUwraq6rVcADCZh4HIIzbkFI4ABsuPn1Y0pWHgExY9lHN7+meEeu/xxo34CNWP6mqTpXkiI8p/WanBHxdSd8a0oBB/rDgP6YhY+tadkqLiRdA11md53M1z7+FfqzyZ3nYcxQ6vf9qP6aW6df36b6jCQZrvvdpkGcnQ+C2kj43pLd++X2lOUu78ZBKJl4WByBsAtkBCOM2pFSNDoAjlHaU9HxJVxkCL0NZn03fKnI7z4yh+R65T1RXBgFHQ1gmOtj88vukpB2Ca5h+QRyAsDnEAQjjNqRULQ6AX/re3rybpAdMSATnMZL2GDLBa5R9ZQzN98h9oroyCDy2kb7efUhX/PJ7b/tHNqSeKZfFAQibPRyAMG5DSpXkADjf/d+GDGZVWf8N+mKfLyM7pO+aE4xMMouLt1FVkbCcXs3bY2i+x+wQdRVD4HlDBbD8h1dSBq0xyOIAhFHHAQjjNqRUSQ7AkHHMsWyU5CxrgHFUwd3nCIwxDSbweklPGVKLX35Pk+TUgrUaDkDYzOMAhHEbUgoHYAi9tGVvJOmIBE18sdBwxwRDpcqeBPaS5CRYweaXX+2yijgAYcsHByCM25BSOABD6KUr64vUN0lUvZMcbZOobqqdNgHf37vzkCH45ecIAC/gWg0HIGzmcQDCuA0phQMwhF66srdrHICDElX/+xia7xH65pwxZ4lQzxyqKIXFYMfTLz9fXPnfOcxK4BhwAMLA4QCEcRtSCgdgCL00Zb3t7+3/VLYifpOq/q71WovgEV0fnvlzvpgZM9tjKK4fD9Xw8cvPITcnVZwQCAcgbPnhAIRxG1IKB2AIvTRlb9PkIzg4TdXacqjWe8R+OSzTCXksxVuzOfnUK1op6rE5/LHNOxHcj5WXn5NNOOlEjYYDEDbrOABh3IaUwgEYQi9+WecjsFZBKrt0c8nrV6kq71mvd4rvJ+k1PcvN7XFLM/vFe2gBA7PypKWRgxNPrbz8PtheBixgTNm7gAMQhhwHIIzbkFI4AEPoxS37D23IS/CTuNVuVJvTCg/Seo/YN2dftBzzb1rNhohVT6aqX0i6YvvvB4X02imxjw/ty8rL7wWtxnZoPVMuhwMQNns4AGHchpTCARhCL25ZbwM/O26Vm9V266Fa75H6d3ITKn7Otq5XNQJQT49U79SqWVHe20rSMYV0/gqSfh7al5WX372HagqHdqCAcjgAYZOAAxDGbUgpHIAh9OKV9dffdRoHwBf0Ulopv8u+JL5y9u+jAH8Je+u5JvO2v9Pv2hnyTojnvoR3xw0aKf+vh07EygC2TryVFdq/HOVKmMSu4yzpBYAD0HXW4j1X0vzHG9W0avJ563aSDsvQbecWeEuGdpY1cWRz6c3HEStmAZoHLSs0s//dWShftGpMJxQiV719E4Xy6VDWKy8///c4ST5PqM1wAMJmHAcgjNuQUjgAQ+jFKbvpiyBOrWvX8pyhWu+ROrdplsNrNJcf7RRM6bdzCIq/S/KFTO8CrNgv2x2BIfXGKHv/5k7CB0IrWj2BFrJwSEttNqVFXNILAAcg/19KSfOff/Tjt3hII5pm0R/fvs5hr2uSCz05R0NL2vhwm5J59WP+6rx9AX3L0QVn3PP5/2r7RpuxMkf767WxS5NE642hnVj98nt5hkstof1MWQ4HIIwuDkAYtyGlcACG0BtW1pe+vA2e8/LXuyXtPKzbUUq/tRn3ozep6baSPhul9rIr8ZGPpZh/tEk3PXYzGNt8LOFdqSBb/fJzPOt+QbVMuxAOQNj84QCEcRtSCgdgCL3wsk71ewtJ/urLaR8fqvUeqbO7SvJxxKb27UYc6FqR2ii1GosfrZWNce/GKbhvAZ321793AYJs9cvv/O0Zx5mCappuIRyAsLnDAQjjNqQUDsAQemFlvd1/z5GU33zRcNuwbkct5Yyxr12jxgdIem/UlsqrzEme1sqV8+Y1jgXG6P37JXkegmzTl59FJ1bf9gyqdGKFcADCJgwHIIzbkFI4AEPo9S/7b0mPavKlWAd/DPvhUK33SJ1+aHMJ7l1r1OVwOMegz1Ue2LK/ixywlzR3QZ4fie+Qag6UdMfQCjZ9+dnLe0poZRMthwMQNnE4AGHchpTCARhCr19Zv/yfJGm3fsWiPu1b5xeMWmNYZXdtdA98HLGWPXXG8sCW/V10LO618fownFFLfU3SDUNr3PTld6fmZuMnQiubaDkcgLCJwwEI4zakFA7AEHrdy/rl/8Qht6u7N7XwSf8unVZICt6bNRFiX17Q03PNVB54RfZ3UcTHAyW9J8I8D63COzBWAwyyTV9+nkx7nWcLqm2ahXAAwuYNByCM25BSOABD6HUr61zvFuBxytcx7TxDNN4jd9y34NfTvp+jPPCK7O8ilDtI+mRkziHV/aXZpfL9vSBb6+XnM4U7BNU2zUI4AGHzhgMQxm1IKRyAIfSWl3VadN/sPmD5o8mfuHxzuetnyVvp1oC17/+wzqNzkwe2KJ6Ffxz9schu1Ogg+I7A2ObdKssy23HtbWu9/Oz5+IZjLYYDEDbTOABh3IaUwgEYQm/9ss5yd2dJTo1egl1viMZ75AF4R9jHEevZnOSBfcHvhUvG66yAP47MObS64N/itV5+9uZ+W5HMIw5A2LILXnRhzSufzhEAAByySURBVFGq1R63BjkWl4C/+C244y+/Usy7sN6NHdv+2lx283HEMrt6Ey9/1AzeG6e0Er/HLhnwBST9aRmUTP/7lUJz+Sx6+X2zzXaVqf+jNoMDEIYfByCM25BS7AAMobd5WW+bPrdJdfvq5ovPW6kl2f2GaLxHHMivJF22Y32faaWSOz5e5GNrqR6u1dEzt7siJejmOFQx6Dhi0cvvmZKc77oGwwEIm2UcgDBuQ0rhAAyht7YDcKkm1v/ouNVGqe0JI4cgrgzCH4M+juhiU5cHXiT7u2jsfy4kgZ6j94LurSx6+VnYwZ5fCd5Nl4U35BkcgDB6OABh3IaUwgEYQm/tsv7Y8S320sxn0KvTz47VP2ve90n6M2UxOcf8O/a/q/10SAhe10Y6POfjq6CQxPVefl+QdPMOjU/9ERyAsBnEAQjjNqQUDsAQemuX/a4kp7ctzf5niMZ7xMF8qKfm/ZTlgW/aJPix/HJXO3yICE/XRjo854yRb+jw3GaPrPfye6Qkn4fM3XAAwmYYByCM25BSOABD6C0ue+WCbnSv9PJ9kpzrfWxzRNjje3TC8sAOX/TRypQsRFHvU5K2L2CQ/y3pBSH9WO/ldz5Jv5O0RUjFEyqDAxA2WTgAYdyGlMIBGEJvcdlnF3jnqZSXy0sDNO+nKA/shE8f7bm8nAgpOBFPz7bWe/wtjYDf40LqW/byKyUfdcjYupZZxqBrPTmeK+kFgAOQY8Y3bqOk+c8/+nQtOs3v9dNVH1TzEZJuEFQybqGQ7eWpyQMvk/1dRHSqxzT/Gc+yl9+NF6RCjLvExq1tGYNxe1fuCwAHIP/KwAFIx/xyjRbAL9NV37tmb6NbDXBse1Bgyt8pyQMvk/1dNAelXNQ8KDT8ssvL78gmI9I1x16FCdvvwiBh872qLukFgAPQa+qiPFzS/EcZUEGVOAtqCdndVpBYlChY4z0iV6sjhmjeX0KSv6x9J6Bks5iPZX9PDuik70a8MaBc7CKOvLhuSKVdXn6PlrR7SOUTKdOFQSlDKekFgAOQf1WUNP/5R5+2xUMlbZe2ic61z0Jkpg1Nc9a8kq2L7O+i/u8k6f0FDK6PWNNG3e3y8jtHqwngH/w5WhcGpYy7pBcADkD+VVHS/Ds//KkDEPicuKSkY077etE2G+qAYUUpWpLM7JAICYdXege51N/Yv7eyv+slOlpvQq2P8OkoMz6skhNbmfDetXSdmFLOOnoPsEOBrgw6VJX8kZJeADgAyad7swbmNP9naV+2582PcWGLD222g99VQH9KSjRzwYE5EkqWB96jTf0cOuW+OOrwwRKsS8KmzfrZ9eXnsyhnyzpnCSON3IeuDCI3G1TdnF4AQQAqLzS3+bfIzI4Fzen+zRfr3QroTymXry2N61Sz3h0JtVLlgT22q0n6YejAmiMOXxz9+YDyMYtepHFmliUwCnYAXPBNobGGMUeZoC4cgDCo7ACEcRtSam4OgCVMHWpcinlL2F+8IRfCYo5hh8CLdzH74Lqsde/jiKFWojxwX9nftRh49+ovQ+FEKr9N40z/oG9dfV5+Vnb6iSRvNczJ+jAYe9xzewGMzXNq7c9t/u1EHlNYzpG7NplQfb9hTHPo3V5jdqBt26GIW0fohy8CBmnVR2h7URV9ZX/XqsfvjtMk+ThrbLuZpC/37UTfl59DHvrIQvbtzxjP92UwRh9X2pzbC2BMllNse47z7zPUkkR43inpYSMvDovvvG7kPrh5ixHdKEI/SpMHDpH9XYTBFwhLuCDvoysfYfWyvi8/35K1V+jIgLlYXwZjjnuOL4AxeU6t7TnOvzPe+ZJxKeYf9IsNPPceOhZruz9vaCURyh/YXHK7Y4R6XMXTmjtkr45U19BqQmR/F7XpOwSOlBjbgi6whrz8XiPJWs9zsRAGY419ji+AsVhOsd05zn9JN6lX1kTQdmrEBeUEPFanG9uckChWHL/DPn/biC2dZ+RBhcr+Luq2swduO/KY3PzTJfnd3MtCXn6+JOM8yCWF7/Qa9CYPhzAY0t6QsnN8AQzhUVvZOc7/mST9vhEb26qgyfQPqX9Qx7K9e6bgTdVPH/nuErFy7wB4J2BMc9IcJ8+JZb4vYrXEsW3X5j7Cc/p2IvTlZ9nM1/ZtrNDnQxmMMRxnZhz7hvLKuIkCyL8C5ugAmKJj7x+cH+fCFv2B41j8sayU2PkXNwB8RBPLxpYHHiL7u4hBKQnz9pT0qL4TFfryc2zod0f+I+k71kXPhzKI1X7fev4pyVKhY5u/2EIVtMbu+1Tbn6sDcG9J+xQ2KVcdGCM+ZDjOThik7T6k0TXK+us/ttb9mC9MOzN2amKaP4T9QTy27SvJf0e9bMjLz9seY4fL9BrsgoeHMIjRft86ji/gHM19HiIR2nfMMZ/3fPvH/dptiNP52tBWcz262Xr9kaSvSjohZqOR6pqrA+DjRDuTJSWOebakV0Sat77V+Jz6sn0LJXjeue5ja91fpv0byx1O7vV1heb+mmVzY9pzmzDAl8asMLCuz0u6Vd+yQ19+viVakp533/H7+aEMQtocUuZ/JV18SAWRyo59UarvMK7TqFn6pqxvAFs1az2z8pmdAF+C8r+/9W0s0fNzdQCM6wuSbp6IW0i1h0uyIt8YZufTcz22bZ9I636MuwChKX+XzUEpyfKOknStZZ3d9H8f+vKzl/q9iYcFDmXQl/nQ5/2FeqWhlUQoHzOUJkJ3FlbhVNbOTX67wEZ8bujyb5D0j8A6YhWbswPwDEmvjAUqQj2WivWZtXeFcpp3QZxkqYTfpRsm0rr3XSY7WE4WlMP8oWp1xX8naMxS1pa0Htv8YXjJvp2Isch8W9Y/kFM0f9ltObGOW5zjBgX0+fmFbH0tQmF1LsdTe33GuDNhmU1viX57RPZzdgCsy+57RSWZL1X5clVO890aqyOWYN4yT6V1748Y/5alDgv8dSOrfL1GwM6OfAq7taTPpai4Z52+HN47V08MB8A/tF8P2X7oOcAUj3tx+ExqSvbB5nLSfQro8MGN9ORtCujHWl3wuf7HEuR3P0XSI9pjgTGGPmcHwDyd1/zSY4Bd0Oan2i/HnF26Soime6IOOglcSq17f8g44iFVSLkT2N1Sku9UpDLfJXKugxLMAn3OZ9HZYjgAbswels9MS9BE7jz4Jn7zm23f+5QZ+9lSVMK80PyiHZITPgVLJy/xebK/KFOYtxEdS7x7isqX1Dl3B8Dx2Y8ZgeuiJu3wOdz1pIx9skb9oRnbW9SU78E42stHISnN746PhmxfL+mUd5Oc1+GXKTvfOqx2XEswH1n9rk9HYjkAbtNynjFjRvuMI/TZjzR3GO4VWnikcqUkCvHwLRPq87VSzDeLv9j0yWeXKc0/ij778/rJaXN3AO7UhL99IifQDm3lvutylxBN9w7j6PuIt8xzadxbXM7hgT6nj2HvkPSEvl/DgQ37CDl2ZEFgV06/U9HrGC2mA+Cvf2cjSv3jGwpnrXKWNC4h6UafMZWSK9x9jqkV3ofBomdzSqj6j96RBc6Nkcvm7gB4C/O4Jvzu7LmAdmjHL6aHdHgu1iNuywmJxrYfj6Bx79Byh146TDfEvtLe+fF/c5p3inKHNa41Ph93ePezs8V0ANyo1bN8HtL7MkLnHsd9MNUt17i93Lg2e8t/TNlAj7q9He4zS/9YjG0OIXMsbOw1vd64vtT8wd0i0e3itdqduwPgMfvc3eFnpZj/1pwEzVviOcwfJb013RN0zEe6Y2jcWxr6ts3W/c6txO6yS9p2GL0TZ0fNfR7DLGXtNTK29d6tSvFj6UtSuW/OhoD3wvGkjR3aFdJ3n2uVcnnRMq6Orx/TfFbp+xypzv3XG5svZOZSsavBAfDW7W5jLqY12r5JE0aa66vy5c29GosQjW2fLEDj3tE727Q7bf6t9v0eO2I+nvBL13/z/vhIEd7Xh79D4d3Pse2RjUbM2/p0IoUD4PbHlHvsOn5v/U81q+F7Imbp6spr0XP+43OM/ZihMGOmlP1OGwGT40eoBgfA2iIpb22HrHdvS+d6Kb+1ebn5h3xs26uw/Axj81ivfd872q6ADvZWr0zlAFjowR5zb2WijBDtsTm2e4pW2i6LdySuPpJiniWJjxz5DM5bpTm2H2twAPz3WIrY1cpvw/cz7i5Z091buWPblD+QcrPbr/kNulvuRtdozwqLFtTqbKkcAHfAP8xfa7IGOg90aTZGfG9MBr5rUcK5++ox+YvBF5hyfAmvtOs4ZV889T2EMS122tRFY6nFASglwcrqebh8pp0J62v01nRPsPhLF/pKMOTgKt8u6WHBpeMVdPTDw/tUl9IBcD8cYufz0dTt9Bmzz/wdLuGvjKmaeVqitKQc6mZpRchnZoLqG+MHjXRRadMheicpxxlgLQ5AKepqq+f5SY3uxf9kWNvezbJ89dhmrQvrMmDLCfh3z4qjY5vFz+7epxM5XszPayVZ+/Qr5bP+unhaygYy1e1QoZzhSV2H9ZxmO37Xrg8HPmflMDuWvi1cgnnXw5KmqeOBa3EAfKnTt+9LSIizsr5yKV9ava63pnuCP4L7FqJxn2Bo0av0R89YmSNXD8ZRSb0SauVwANzGeyXdPzr2/hX6tqbj6HMqe/XvZbcSt0+Uqatb6+s/9YH2IlOKLHr+0rana53yksz521NLgtbiAHheHdp1j4Im2DuHFsZJnSbafzPe3RrbfLHXO2zYcgKl3MnqfVclhwNgfBb2OGTE9Jruw58lXT/TOd7yJTP8CQsvORQml1pX3x57Me7U/Ij7lnwM81fhLq3i5LLY4Bjt9a3DabGta57SanIAfKbqs9WS7H7N3Sbn4khl/p3speWeqiONImMOhzZh97NWbUc1tyroWgP0sfDF+ow8lwPgPjmG87NtTGefPsZ41n9UVpnyNt6cbI/mLoAzlpVq/2x/xJ3mNVQv246Ob9g6PnrrUgfanr15ZyKl1eQA+IfMKU5z/kYtm7v3txkhlz0X+r97zL203EMb6lDO4Zihf7Mdqp/VIxYDswjZ2Oa8LL1UNHP/cTl5zKczp7M9vtmatb52CQk2Yi8QSz96Z6V0syNwgKS9221F78asZ37p+yKUzyGdgvcipQ+wyW/ODkD8SfKRirOtlWLOjHdhSV7PKcyhtLF2zIb2z85m6jstQ/tYSvmS5s1Rd52PuHM7AJ4wX5ayUFCOuEl/QTjByFGlrJTI/bBs5g9bCebIVSerzol0HMLoPOO/bY8xztp6rt4lsg649SOsJTEl84vKN7hTWk07AOZYSubL1XPaW2+9x4LwBa5eWu496u7z6Gkj62r06WsJz1683a0qoS9WiHWa+042hgOw0jFvXVtsItWFFzsZT5bkHYA526NHSk07Z6Z9x2anxo5tZ8+7bwPt87U5ACUlvlqZspQCOaWcJR9TiLZ94J9J9mL+WDk5e6trN+gEZd/u2pcxHQD30Te5X9xu9fprNoY5HeKz2qQiMeorvQ47UPb4nCQIG4eAt21zxG7X5gBYC94vo5LW9k8T7rhZxKWXlnui5Z5L1yJR90eptpToDYdGd5ZlH9sBWJkpb/tax9jHAqE3vK0IZ0EGJ7HIqUY3ymrbpNESt0pL4JKrDym/ClePoTYHwGN/XyEhxKvnwcqTKYTESokn92/pzXL98cykHR9nXqKAsfRKTlaKA7DCzVspTgV61/Yc2HLCDv9ayxzy8PX2S9956S2gUav5kpz1+HvdAK0VVoJxO7z0Gwnq3bTKGh0Ah5L69n1JZr11667HNkfL9NJyj92Btr79M93RStT9UaotRcHxsX2OhEtzADadOV8Oswb3OSX5iMA/gH7x+2VXSrzsKKttjUatRJVLhreUMZfQD+e7uGGmjtToADjfwx+aC4E+DijFHFGUIvtbKZryJaT4LmWuu/bD0Vi+IDq2WXn3ZV07UboD0HUcPLfBOfL5pMOUsHwEfGzlL6YcVqMDYK7ekr5JDsAd23BOeufhOK7j810f+2hfLfeuFfd87jWFaNv37Paoj3+4zX0zaieay8ivl/SUrp3AAehKahrPERGQd57s9TtxTS6r1QF4rqSX5oLcsZ0HtRLnHR/v9Ji13Es4e++dV77T6Ob90Ftb+fOxR+msrA/u2gkcgK6kpvGct0kdAmJhCiwtAYvBOOTGUSe5rFYHwLoQnUObMk2Gv/h2jNyWc5XkyCq5rNuPLCQaYVk/S/rfrVRqx2ls+0QrfNepHzgAnTBN6iGfQzkMJFZY5aQGn7GzTg3rFLE5rVYHwL9TvmVtwZVS7K9tHg6L5sQy5/a4aKzKBtRzb0n7DihfY1FnmE1xMbQvy6/0OS7DAeiLdxrPv0HSE6fR1Un20pdQHfefWyq1VgfAi8Tx8Y6TL8liZ8yzlvuiqKec406pdphzHDnbcmp2p2gf26yy6ui5ToYD0AnT5B46WxuWdrXJ9bz8Dlv171bNjd8vjtDVmh2Au0vyJbmS7I1thsoYfbL+SW6HclG/7dyWkpMgBtscdTh0PXUysC7j+GOfi+A4AF2QTvOZ60nydpBDKbF4BHKJ/qzV45odACc58Y+bndtSzDtBl4vUmUv10XCP1Oaiai5ZkLZ94qFGq/6mhSSc890k7yJ1EsPDAYg2/0VWVOLt6SJBdezUEU3aTyds8VbtGFazA2DeBzUhgbcZA/w6bfZKvrJOPU4m5eyHJZh1V0rRti+BR5c+WM32+10ezPCMs+52yoGDA5BhNkZswvP7oWZh+lIPNozAsY3MtHdVnGFyLKvdAXByL+/AlGT3b3IDfCBChxxO2lnDPUJ7i6qwwFqqBG0Juz161daFcN6KEszieb/o0hEcgC6Upv2M/5h9Xu2XFxZG4B+SnGRjjHP/1T2u3QG4UiIN/rBVsaHUC5uIm5cMqaAt65BCO+tj2+8K0bQfm0Pf9n3U6p3BEt6pN2hl8peOoYTOLu0kDwwm4PApS9ZebHBN9VXgs7SdE4i+hJCs3QEwM6tdOotoKbZnI0/u1OZDzbH3FpMZ26xrcY2xOzHR9k9o5erH7n7n6BQcgLGnKl/71230y61c55cI1p3A05sMlZZGLcF8Ec7x5yWYU/TGlsLtMi7rL+zS5cFMz8TSzfeYPLax7QuFaNqPzSGkfV8K9Z2Qse1Okg7o0gkcgC6U5vPMjSR9utGLPs98hpR0JE4vXVKCJSs9+jiihL9bZ+48JSn9tSu/fbuGR2h6zSadwOcRETrzmCZ86y0R6hlaxUcK0bQfOo4xyjsjqD+0xjZ2AMaegYLbd+a6z+AELJ2h/5b0gqVP5X/gL5LOm7/ZjVo8SZJ3I8Ywp7z+U5shdIz2N23TOQqeH6Ej92pkgC0vPLbthohY8BR8XNKdg0vHK2iJ8k7S2SV8ScQbNjV1JeBLInYCxn6RdO1v7ueeJcm52Us03+W4/sgd84+Lf2TGMmdfvMtYjW/SrtUJ3xGhLz53PypCPUOrsIKonQCsP4ESFFgtVOYdXjvpSw0HYCmi2T7gBCv+IbUACbaBgHXdnVHR57ql2u5tH8fsX6xt79AxlJT10mqbMeK/Ld7i3Z2xQ/BuLOnw0ImpvJxDQt83MoMfNdEkV+naBxyArqTm+dyFW3nVknKtj0Xa28r3bGR+nZK1ZCthq/i+I4esOZrlN5J8J2JMc9y3+9JJda1DR31x644dnkv1iMVjHM8eM8FRqr6WWK/XgpNWjZmIrZc8NQ5Aicsob58srerLRw/N22xRrVmBzWJJncQzRu65vxD94hnrDP5vki7SdYsxIasSjgFiZ4R0uOm7EzJbVrXbdlIbLJyAPyBuFl58cMnt+kgS4wAM5j2bCh7bprMcewsyJ1B/ub2++eJ5zojyviHjfbMkz9cY5qx8jlkf2/yl3CnUKVFHvXacNMdx87HMErz+grSU6xjmC8K+Y4KFE7hfJGXIkB74KOrqfXakcABCMM+3zNbtF8i28x3if0ZmxTNf4HJY5NTMscZO+5k7daxDEH2++PMCgPm36/NtboYxurNfkzHvHgkafl5ztOEIlNxmGWKrXWLDCJylvRNyxWHVBJXeSdLefUriAPShVcezPle15rp/hBxyNTf7V3vk4R/aUkR1Qhjv2sThO1ohp1kQycJIpZgdVt+ctyZBTrP+gb/+f5KgUe8CfC+zoIwzyDl+nRTAcSbUESo+osppzvzqowdHAXQ2HIDOqKp78MrNjWQL4ZQQ1xoL/lfbGOevx6pwxHp8VOPt2m0y9cG3i51PwncASjLL8O6RuUOpw0Sd8dBhurkuk72oEZd6cWaGc2/uPc1O2QMzDdJ/kw7t/kHf9nAA+hKr73l7lY6Jd3jQVM1nY06NnNsrT83LKUgPy6Dn4J0SR4r4y7REs2BTrheYlfKcuKfXl1YAtFxHAQe2mgreBcDiEfAl3UPbnaJ4tW5ek++i2NF4f0gjOAAh1Oor43Vyt/ZH1pdMpmLfbG7Lv1bSPo1am7f+52i+9fuphMp4zgtvbXGft5dsVuTzZc6Uv2nWyd9BkpnksDdJelzChhzvb9nYExO2UXPVl2j/blImr3rqkBTZKf9Yap74OY/95u0N9LtLcgrM0sxfMr4dblUu/2DXYM7xYBnSC0UerLUR7tq8JHy+OAWzRsI7E4VIevfIN7z/nhGEf599F8e7V7HNRwwOfeXlH5vsxvVdtDk6+2QC5Uz/zjkSyFE5wYYDEIyu+oJe2A4He0Ah6VktT+tzN9+CPbbC2fHXhlXI7KDFMMcze24dljYlu1KbVc9Jg2KYRXH8AvZOUizBn779crSBUwU7A+NQcySHd0teNuNdsaGMYpf3ZWp/kPj3MsY711kHHyTpy0M7GqMzQ/tA+ekT8IVB33z1VrFDCHMotJ3apC39Yrv97S/+n00f4+AR+O/ZYjI+Dw+VePYL/4VtOOhYL7zBINqten89X3tAZZ9ovpC9xfrTAXXEKurdHc+rQ1dDd9583v+Mgu9yxGJVaj0+rvPFausthJgv+1m3xHeyOmn9L2sEB2AZIf73vgQu0IajONeAf3z939CX0UrbPr+39Ku/8n2T/4gmOsHn+7nOYvsyGPt56wPcR9KDJflHx7HJ65n52pnaS9IHZyYF68RJTtdr59S7VsvMKouO8bc6ZomXHi/e5oKwHHOXs+XjWrnvPRsGTleLjU/g1q0j5zW5ZYfuONT1A5Kcg+PPHZ7v/AgOQGdUPDiAwPmbi3i+se6vGGuN+7/+5y3N1S8nx1d7gftHy/8s1uOvLwvP+Isf60/g3JJu2oYLWkDImcJsvtn/q1a0xLeVp6yJ0JWKX5hmcel27Xn9+avKa83CSnYw/WOb+oZ/1/4ue846CL7/YdEZ69D75rmd4pXxWOLaY5rrBdhlfEr/3+2oezfAmhJem/54sjS7k0L9vg3r80XNZMdwOAClLxH6BwEIQAACEEhAAAcgAVSqhAAEIAABCJROAAeg9BmifxCAAAQgAIEEBHAAEkClSghAAAIQgEDpBHAASp8h+gcBCEAAAhBIQAAHIAFUqoQABCAAAQiUTgAHoPQZon8QgAAEIACBBARwABJApUoIQAACEIBA6QRwAEqfIfoHAQhAAAIQSEAAByABVKqEAAQgAAEIlE4AB6D0GaJ/EIAABCAAgQQEcAASQKVKCEAAAhCAQOkEcABKnyH6BwEIQAACEEhAAAcgAVSqhAAEIAABCJROAAeg9BmifxCAAAQgAIEEBHAAEkClSghAAAIQgEDpBHAASp8h+gcBCEAAAhBIQAAHIAFUqoQABCAAAQiUTgAHoPQZon8QgAAEIACBBARwABJApUoIQAACEIBA6QRwAEqfIfoHAQhAAAIQSEDg/wP0HuU/It/5UAAAAABJRU5ErkJggg==') !important;
}

/* Dark Mode CRM Icon Override */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2)::before {
    background-image: url('data:image/png;base64,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') !important;
}

/* Dark Mode Power Dialer Override */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3)::before {
    background-image: url('data:image/png;base64,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') !important;
}

/* Dark Mode Scraped Leads Icon Override */
section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4)::before {
    content: "" !important;
    background-image: url('data:image/png;base64,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VQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPwZ9mpLAAAWEUlEQVSmBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RNVQJAm1GlNUoA8NMSAPymBAC/KQEgx7RN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') !important;
    background-size: 20px 20px !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    width: 24px !important;
    height: 24px !important;
    display: inline-block !important;
}



/* Force text visibility */
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
    font-size: 0.95rem;
    margin-bottom: 4px;
    white-space: normal;
    line-height: 1.2;
    word-break: break-word;
}
.mc-company { 
    color: #94a3b8 !important; 
    font-size: 0.85rem;
    margin-bottom: 8px;
    white-space: normal;
    line-height: 1.3;
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
div[data-testid="stDataFrame"], div[data-testid="stTable"], div[data-testid="stDataEditor"] {
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

/* ⚠️ AGGRESSIVE HEADER & CELL FIX (DataEditor Specific) */
[data-testid="stDataFrame"] thead th,
[data-testid="stTable"] thead th,
[data-testid="stDataEditor"] thead th,
[data-testid="stDataEditor"] th,
.stDataFrame thead th,
table thead th,
th {
    background-color: #1e293b !important; 
    color: #ffffff !important;
    border-bottom: 1px solid #334155 !important;
}

[data-testid="stDataEditor"] td,
[data-testid="stDataEditor"] table tbody tr td {
    background-color: #0f172a !important;
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

# 4. SHARED RESPONSIVE CSS (Mobile Optimization - Enhanced)
RESPONSIVE_CSS = """
<style>
/* --- MOBILE RESPONSIVENESS (Screens < 768px) --- */
@media only screen and (max-width: 768px) {
    
    /* 1. Main Container Padding */
    .block-container {
        padding-top: 3rem !important; /* Space for hamburger menu */
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 4rem !important;
        max-width: 100vw !important;
    }

    /* 2. Header & Titles Scaling */
    h1 { font-size: 1.6rem !important; line-height: 1.2 !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.2rem !important; }
    p, div, label { font-size: 14px !important; }
    
    /* 3. Force Column Stacking (The Critical Fix) */
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 auto !important;
        min-width: 100% !important;
        margin-bottom: 12px !important;
    }
    
    /* EXCEPTION: Content Action Buttons Row (Keep Horizontal) */
    div[data-testid="stVerticalBlock"]:has(.css-actions-row) div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: auto !important;
        min-width: unset !important;
        flex: 1 !important;
        margin-bottom: 0 !important;
    }

    /* 4. Touch-Friendly Inputs & Buttons */
    div.stButton > button {
        width: 100% !important; /* Full width buttons on mobile */
        min-height: 48px !important; /* Touch target size */
        margin-bottom: 8px !important;
    }
    
    /* Exception for Actions Row Buttons */
    div[data-testid="stVerticalBlock"]:has(.css-actions-row) div.stButton > button {
         width: auto !important;
         min-height: 48px !important;
    }
    div[data-testid="stTextInput"] input, 
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        min-height: 48px !important;
    }
    
    /* 5. Data Tables/Editors Scroll */
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        width: 100% !important;
        overflow-x: auto !important;
        display: block !important;
    }
    
    /* 6. Hide Sidebar default minimize arrow if it overlaps */
    section[data-testid="stSidebar"] {
        z-index: 99999 !important; /* Ensure sidebar is on top */
    }
    
    /* 7. Card/Container Margins */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.5rem !important;
    }
    
    /* 8. Google Toggle Widget Responsive Container */
    iframe {
        max-width: 100% !important;
    }
}
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
# Force "light" theme to ensure consistent UI rendering across all components
st.session_state.theme = "light"

st.markdown(COMMON_CSS, unsafe_allow_html=True)

# Force Light CSS
st.markdown(LIGHT_CSS, unsafe_allow_html=True)
st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)

# Global Padding Fix (Move content higher)
st.markdown("""
<style>
/* Reduce top whitespace */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}
/* Adjust header positions */
h1 {
    padding-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)

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

# Force Light Logo since we killed dark mode
target_logo = sb_logo_light if sb_logo_light else sb_logo_dark

if target_logo:
    st.sidebar.markdown(f"""
    <div style="margin-bottom: 20px;">
        <img src="data:image/png;base64,{target_logo}" style="width: 100%; max-width: 240px; height: auto;">
    </div>
    """, unsafe_allow_html=True)
elif sb_logo_dark:
    st.sidebar.image("logo.png", width=240)
else:
    st.sidebar.title("SHDPIXEL")

# Helper for Animated Icons
def get_icon_html(icon_name, width=60):
    icon_path = f"assets/icons/{icon_name}"
    if os.path.exists(icon_path):
        b64 = get_sidebar_img_b64(icon_path)
        return f'<img src="data:image/png;base64,{b64}" style="width: {width}px; height: auto; vertical-align: middle; margin-right: 15px;">'
    return ""

# Navigation
page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard", 
        "CRM Grid", 
        "Power Dialer", 
        # "Lead Generator", 
        "Scraped Leads",
        "Spreadsheet Tool",
        "Google Maps Scraper"
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
# st.sidebar.header("⚙️ Settings")

# Theme Toggle
# if st.session_state.theme == "light":
#     if st.sidebar.button("🌙 Switch to Dark Mode", use_container_width=True):
#         st.session_state.theme = "dark"
#         st.rerun()
# else:
#     if st.sidebar.button("☀️ Switch to Light Mode", use_container_width=True):
#         st.session_state.theme = "light"
#         st.rerun()

# Seed Data Button (Demo Mode)
# Seed Data Button (Live Mode Only)
if IS_LIVE_ENV:
    if st.sidebar.button("🌱 Add Dummy Data", use_container_width=True, help="Injects 10 sample leads for demo purposes"):
        try:
            # Check if backend is reachable first
            r = requests.post(f"{BACKEND_BASE}/leads/seed", timeout=10)
            if r.status_code == 200:
                st.toast("✅ Dummy data added!", icon="🌱")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Failed to seed data. Status: {r.status_code}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

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
                meetings_html = '<div style="max-height: 350px; overflow-y: auto; padding-right: 4px;">'
                
                for idx, row in future_meetings.iterrows():
                    # Create Link
                    m_date = row["meetingDate"]
                    name = str(row.get("contactName", "Lead")).strip() or "Lead"
                    comp = str(row.get("businessName", "Company")).strip() or "Company"
                    
                    # Generate Link
                    start_str = m_date.strftime("%Y%m%d")
                    end_str = (m_date + pd.Timedelta(days=1)).strftime("%Y%m%d")
                    title = urllib.parse.quote(f"Meeting with {name} ({comp})")
                    details = urllib.parse.quote(f"Phone: {row.get('phone', '')}\nAddress: {row.get('address', '')}")
                    cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&details={details}&dates={start_str}/{end_str}"
                    
                    # Append Card HTML (No indentation to prevent Markdown code block rendering)
                    meetings_html += f"""
<a href="{cal_url}" target="_blank" style="text-decoration: none; color: inherit;">
<div class="meeting-card">
<div class="mc-date-box">
<span class="mc-month">{m_date.strftime('%b').upper()}</span>
<span class="mc-day">{m_date.strftime('%d')}</span>
</div>
<div class="mc-details" style="min-width: 0;">
<div class="mc-title" title="{comp}" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{comp}</div>
<div class="mc-company" title="{name}" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">👤 {name}</div>
</div>
</div>
</a>"""
                
                meetings_html += "</div>"
                st.sidebar.markdown(meetings_html, unsafe_allow_html=True)
except Exception as e:
    # Fail silently to not break main app
    st.sidebar.caption(f"Syncing calendar... ({e})")

# ================== DASHBOARD ==================
if "Dashboard" in page:
    st.markdown(f"""
    <div style="margin-bottom: 20px; margin-top: 0px;">
        <h1 style="margin: 0; padding: 0; font-size: 2.2rem; font-weight: 800; display: flex; align-items: center;">
            {get_icon_html('rocket.png', 70)}
            <span>Sales & Growth Engine</span>
        </h1>
        <p style="margin-left: 85px; margin-top: -5px; opacity: 0.7; font-size: 1rem;">
            End-to-end command center: from data mining to closed deals
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
    
    # Calculate Recent Imports (CRM)
    recent_crm_count = 0
    if not df_all.empty and 'createdAt' in df_all.columns:
        # Convert to datetime and strip timezone for comparison
        df_all["createdAt"] = pd.to_datetime(df_all["createdAt"], errors='coerce').dt.tz_localize(None)
        last_24h = datetime.now() - pd.Timedelta(hours=24)
        recent_crm_count = len(df_all[df_all["createdAt"] >= last_24h])

    # Calculate Fresh Scraped Leads (From History, not yet in CRM)
    executions = fetch_data(EXECUTIONS_API)
    scraped_today_count = 0
    if executions:
        df_exec = pd.DataFrame(executions)
        if 'date' in df_exec.columns and 'leadsGenerated' in df_exec.columns:
            df_exec["date"] = pd.to_datetime(df_exec["date"], errors='coerce').dt.tz_localize(None)
            last_24h = datetime.now() - pd.Timedelta(hours=24)
            # Sum up leads generated since yesterday
            scraped_today_count = df_exec[df_exec["date"] >= last_24h]["leadsGenerated"].fillna(0).astype(int).sum()

    c1, c2, c3 = st.columns(3)
    with c1: metric_card("Fresh Scraped (Today)", int(scraped_today_count), icon="✨", color="blue")
    with c2: metric_card("Imported to CRM (Today)", recent_crm_count, icon="📥", color="purple")
    
    # --- SECTION 2: CRM PIPELINE ---
    st.markdown("---")
    st.subheader("💼 Active Pipeline (CRM)")
    
    # Calculate CRM specific metrics
    crm_total = len(df_crm)
    
    hot_leads = 0
    meetings = 0
    closed_won = 0
    
    if not df_crm.empty:
        # Hot Leads (Robust Check)
        if 'priority' in df_crm.columns:
            hot_leads = len(df_crm[df_crm['priority'].astype(str).str.upper() == 'HOT'])
            
        # Meetings (Robust Check)
        if 'status' in df_crm.columns:
            meetings = len(df_crm[df_crm['status'].astype(str).str.contains("Meeting", case=False, na=False)])
            # Closed Won (Robust Check for 'Won' or 'Closed - Won')
            closed_won = len(df_crm[df_crm['status'].astype(str).str.contains("Won", case=False, na=False)])
    
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
    st.markdown(f"""<h1 style='display: flex; align-items: center;'><i class="fas fa-user-friends" style="margin-right: 15px; color: #2563EB;"></i> Advanced CRM Grid</h1>""", unsafe_allow_html=True)
    
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

    # --- GOOGLE SHEETS FUNCTIONALITY: FILTERS & SEARCH ---
    st.markdown("""
    <style>
    .filter-bar {
        background: rgba(150, 150, 150, 0.05);
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .grid-footer {
        background: #f8f9fa;
        padding: 5px 15px;
        border-radius: 0 0 8px 8px;
        border-top: 1px solid #ddd;
        font-size: 0.85rem;
        color: #666;
        display: flex;
        justify-content: space-between;
        margin-top: -5px;
    }
    /* GRID HEADER STYLING (Sheets Style) */
    div[data-testid="stDataEditor"] .glide-grid-header {
        background: #f1f3f4 !important;
        font-weight: bold !important;
    }
    
    /* Overall grid border for Sheet look */
    div[data-testid="stDataEditor"] {
        border: 1px solid #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- CALLBACKS ---
    def clear_all_filters_cb():
        st.session_state.global_search_input = ""
        st.session_state.f_status_multi = []
        st.session_state.f_prio_multi = []

    # 1. SEARCH & FILTERS ROW
    col_search, col_status, col_prio, col_clear, col_export = st.columns([2.5, 1.5, 1.2, 0.4, 1])
    
    with col_search:
        search_q = st.text_input("🔍 Search", placeholder="Search name, company, notes...", label_visibility="collapsed", key="global_search_input")
    
    with col_status:
        # Sync Options with Palette Keys to ensure 100% match
        status_keys = list(STATUS_PALETTE.keys())
        if "Generated" not in status_keys: status_keys.insert(0, "Generated")
        status_options = status_keys
        f_status = st.multiselect("Filter Status", options=status_options, placeholder="All Statuses", label_visibility="collapsed", key="f_status_multi")
    
    with col_prio:
        f_prio = st.multiselect("Filter Priority", options=["HOT", "WARM", "COLD"], placeholder="All Priorities", label_visibility="collapsed", key="f_prio_multi")

    with col_clear:
        st.button("🧹", help="Clear All Filters", on_click=clear_all_filters_cb)
    
    with col_export:
        import io
        def to_excel(df_to_save):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_to_save.to_excel(writer, index=False, sheet_name='CRM_Leads')
            return output.getvalue()

    # 2. APPLY REACTIVE FILTERING
    if not df.empty:
        if search_q:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_q, case=False, na=False)).any(axis=1)
            df = df[mask]
        if f_status:
            df = df[df['status'].isin(f_status)]
        if f_prio:
            df = df[df['priority'].isin(f_prio)]

        # --- SORTING LOGIC ---
        # -1 = Urgent (Follow-up is TODAY)
        #  0 = Normal
        #  1 = Closed - Lost (Bottom)
        
        today_date = datetime.now().date()
        
        def get_sort_key(row):
            # 1. Check Closed-Lost (Deprioritize)
            st_val = str(row.get('status', '')).strip()
            if st_val in ["Closed – Lost", "Closed - Lost"]:
                return 1
            
            # 2. Check Follow-up Date (Prioritize)
            d = row.get('nextFollowUpDate')
            # Ensure d is a valid date object for comparison
            if d == today_date:
                return -1
                
            return 0

        df['_sort_key'] = df.apply(get_sort_key, axis=1)
        
        # Sort: SortKey ASC, then ID DESC (Newest first)
        df = df.sort_values(by=['_sort_key', 'id'], ascending=[True, False])
        df = df.drop(columns=['_sort_key'])
            
    with col_export:
        if not df.empty:
            excel_data = to_excel(df)
            st.download_button(
                label="📥 Export Excel",
                data=excel_data,
                file_name=f"CRM_Export_{time.strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download filtered leads to Excel",
                use_container_width=True
            )
        else:
            st.button("📥 Export", disabled=True, use_container_width=True)

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
    # zoom_val and scroll logic REMOVED. relying on native browser scroll.
    
    # --- CUSTOM TOOLBAR UI ---
    st.markdown("""<div class="crm-toolbar"></div>""", unsafe_allow_html=True)
    
    # Simple Layout: Spacer | Actions
    toolbar_c2, toolbar_c3 = st.columns([4.0, 2.5])
    
    with toolbar_c2:
         st.write("") # Spacer

    with toolbar_c3:
        st.write("⚙️ **Actions**")
        
        # Init Zoom Level
        if "zoom_level" not in st.session_state:
            st.session_state.zoom_level = 100
            
        current_wrap = st.session_state.get("wrap_text", False)

        # CSS Marker for Mobile Row Targeting
        st.markdown('<div class="css-actions-row"></div>', unsafe_allow_html=True)

        if current_wrap:
             # Edit | Wrap | Zoom In | Zoom Out | Save | All
             ac1, ac2, z_out, z_in, ac3, ac4 = st.columns([1, 1, 0.6, 0.6, 1, 1], gap="small")
        else:
             # Normal Layout
             ac1, ac2, ac3, ac4 = st.columns([1, 1, 1, 1], gap="small") 
        
        with ac1:
             # Edit/Read Toggle
             if mode == "👁️ Read Only":
                 if st.button("✏️", use_container_width=True, key="btn_edit_mode", help="Switch to Edit Mode"):
                     st.session_state.mode_state = "✏️ Edit" 
                     st.rerun() 
             else:
                 if st.button("👁️", use_container_width=True, key="btn_read_mode", help="Switch to Read Only Mode"):
                    st.session_state.mode_state = "👁️ Read Only"
                    st.rerun()
        
        with ac2:
            btn_label = "📏" if current_wrap else "↩️"
            btn_help = "Standard Table View" if current_wrap else "Wrapped Text View"
            if st.button(btn_label, use_container_width=True, help=btn_help, key="wrap_btn_toggle"):
                st.session_state.wrap_text = not current_wrap
                st.rerun()

        if current_wrap:
             with z_out:
                  # Use unique key per render if needed, but fixed key is better for debounce
                  if st.button("➖", use_container_width=True, help="Zoom Out (10%)", key="zoom_out_btn"):
                       # Ensure int
                       curr = int(st.session_state.get('zoom_level', 100))
                       st.session_state.zoom_level = max(50, curr - 10)
                       st.rerun()
             
             # Display current zoom level with a small hack using a disabled button styling or just centering logic
             # But here we just assume it's sandwiched
             
             with z_in:
                  if st.button("➕", use_container_width=True, help="Zoom In (10%)", key="zoom_in_btn"):
                       curr = int(st.session_state.get('zoom_level', 100))
                       st.session_state.zoom_level = min(200, curr + 10)
                       st.rerun()

        with ac3:
             # Auto-Save Indicator (Visual only)
             if mode == "✏️ Edit":
                  st.button("⚡", disabled=True, use_container_width=True, help="Auto-save enabled", key="btn_autosave_indicator")
             else:
                  st.button("🔒", disabled=True, use_container_width=True, help="Read Only", key="btn_readonly_indicator")

        with ac4:
            # "All" / Show All icon
            st.button("📑", use_container_width=True, key="btn_show_all", help="Show All Rows / Reset Filters", on_click=clear_all_filters_cb)

    # CSS Injection (Clean Native)
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
        # LIGHT MODE
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
    
    # Full View Adjustments
    full_view_css = ""
    if st.session_state.get("full_view", False):
        full_view_css = """
        section[data-testid="stSidebar"] { display: none !important; }
        button[kind="header"] { display: none !important; }
        .stMain { padding-top: 0 !important; }
        """

    viewport_offset = 64
    st.markdown(f"""
    <style>
    {full_view_css}
    
    /* REMOVE ALL STREAMLIT VERTICAL WASTE */
    section.main > .block-container,
    div[data-testid="stAppViewContainer"] .block-container,
    div[data-testid="stAppViewContainer"] .main,
    .stAppViewContainer, .main, .block-container {{
        padding: 0 !important;
        margin: 0 !important;
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }}
    
    /* NATIVE SCROLL LOGIC ONLY */
    div[data-testid="stDataEditor"] {{
        width: 100% !important;
        max-width: 100% !important;
        overflow: auto !important;
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
        Applies Google Sheets-style conditional formatting to Status cells.
        Strict exact matching only.
        """
        if not val or pd.isna(val):
            return ""
            
        status_val = str(val).strip()
        
        # EXACT Google Sheets Color Mapping (Per User Request)
        # Background color | Text color
        GS_MAPPING = {
            "Interested":          "background-color: #DFF5E1; color: #1B5E20;",
            "Not picking":         "background-color: #F0F0F0; color: #616161;",
            "Asked to call later": "background-color: #FFF8E1; color: #8D6E00;",
            "Meeting set":         "background-color: #E3F2FD; color: #0D47A1;",
            "Meeting Done":        "background-color: #E0F2F1; color: #004D40;",
            "Proposal sent":       "background-color: #F3E5F5; color: #4A148C;",
            "Follow-up scheduled": "background-color: #FFE0B2; color: #E65100;",
            "Not interested":      "background-color: #FDECEA; color: #B71C1C;",
            "Closed – Won":        "background-color: #C8E6C9; color: #1B5E20;", # En-dash
            "Closed - Won":        "background-color: #C8E6C9; color: #1B5E20;", # Hyphen fallback
            "Closed – Lost":       "background-color: #ECEFF1; color: #37474F;", # En-dash
            "Closed - Lost":       "background-color: #ECEFF1; color: #37474F;"  # Hyphen fallback
        }

        # Logic: Strict Case-Sensitive Exact Match
        return GS_MAPPING.get(status_val, "")
        
    def get_priority_style(val):
        """
        Applies strict Google Sheets-style conditional formatting to Priority cells.
        """
        if not val or pd.isna(val):
            return ""
            
        p_val = str(val).strip()
        
        # EXACT Colors - DO NOT CHANGE
        PRIO_MAPPING = {
            "HOT":  "background-color: #F25C54; color: #FFFFFF;",
            "WARM": "background-color: #FFE5B4; color: #5A3E00;",
            "COLD": "background-color: #E3F2FD; color: #1E3A8A;"
        }
        
        return PRIO_MAPPING.get(p_val, "")

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

    def highlight_closed_rows(row):
        """
        Highlight entire row if Status is Closed-Won or Closed-Lost.
        """
        s = str(row.get('Status', '')).strip()
        
        style = ''
        if s in ["Closed – Won", "Closed - Won"]:
             style = 'background-color: #C8E6C9; color: #1B5E20;'
        elif s in ["Closed – Lost", "Closed - Lost"]:
             style = 'background-color: #ECEFF1; color: #37474F;'
             
        return [style] * len(row)

    def highlight_today(val):
        """
        Highlight cell if date is today (Urgent).
        """
        try:
            today = datetime.now().date()
            if val == today:
                 # Match "Follow-up scheduled" style
                 return 'background-color: #FFE0B2; color: #E65100; font-weight: bold;'
        except: pass
        return ''

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

    # --- GLOBAL HEIGHT CALCULATION ---
    total_content_height = (len(df) + 1) * 35 + 10
    final_height = min(total_content_height, 20000) 
    final_height = max(final_height, 400) # Increased min height for usability

    if is_wrap:
        # --- HTML WRAPPED VIEW ---
        # Fixed Width/Scale for Wrap View since we removed usage of variable zoom
        scale_val = 1.0
        width_str = "100%"
        
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

        # Mapping logic cleared to allow Styler to handle background

        
        # --- ADD EDIT BUTTON (If in Edit Mode) ---
        if mode == "✏️ Edit":
            df_ids = df["id"].tolist()
            display_df_html.insert(0, "Action", [f'<a href="?edit_id={i}" target="_self" style="text-decoration:none;">✏️ Edit</a>' for i in df_ids])
            
            # CHECK QUERY PARAMS HERE (Local catch)
            # Use safe extraction for streamlit new versions if needed
            try:
                qp = st.query_params
            except:
                qp = st.experimental_get_query_params()
                
            if "edit_id" in qp:
                edit_id = qp["edit_id"]
                st.session_state.edit_trigger = edit_id
                
                # Clear param
                try:
                    st.query_params.clear()
                except:
                    st.experimental_set_query_params()
                    
                st.rerun()

        # 3. Create HTML for Wrapped View
        # Exclude 'Status' and 'Priority' from base props
        non_styled_cols = [c for c in display_df_html.columns if c not in ['Status', 'Priority']]

        styled_html = display_df_html.style\
            .map(get_status_style, subset=['Status'])\
            .map(get_priority_style, subset=['Priority'])\
            .map(get_user_style, subset=['Called By', 'Meeting By', 'Closed By'])\
            .map(highlight_today, subset=['Next Follow-up'])\
            .set_properties(**base_props, subset=non_styled_cols)\
            .apply(highlight_closed_rows, axis=1)\
            .hide(axis="index")\
            .format({"Last Follow-up": "{:%d/%m/%Y}", "Next Follow-up": "{:%d/%m/%Y}", "Meeting Date": "{:%d/%m/%Y}"}, na_rep="")\
            .to_html(escape=False)

        # 4. Inject Custom Table CSS (Streamlit Native Look)
        current_zoom = st.session_state.get('zoom_level', 100)
        zoom_ratio = current_zoom / 100.0
        base_font_size = 14 * zoom_ratio
        
        # Scale padding
        p_v = 8 * zoom_ratio
        p_h = 10 * zoom_ratio
        th_p = 12 * zoom_ratio
        
        table_css = f"""
        <style>
        .wrap-table-container {{
            max-height: {final_height}px;
            overflow-y: auto;
            border: 1px solid {border_col};
            border-radius: 4px;
            background-color: {base_props.get('background-color', '#fff')};
            width: 100% !important;
            display: block;
        }}
        .wrap-table-container table {{
            width: 100%;
            border-collapse: collapse;
            font-family: "Source Sans Pro", sans-serif; /* Streamlit Font */
            font-size: {base_font_size}px !important;
            color: {base_props.get('color', '#31333F')};
        }}
        .wrap-table-container th {{
            position: sticky;
            top: 0;
            z-index: 10;
            padding: {th_p}px {p_h}px !important; /* Scaled padding */
            text-align: left;
            font-weight: 600;
            font-size: {base_font_size}px !important;
            
            /* Streamlit Native Header Style */
            background-color: {header_bg if st.session_state.theme == 'dark' else '#ffffff'}; 
            color: {header_col if st.session_state.theme == 'dark' else 'rgba(49, 51, 63, 0.6)'};
            border-bottom: 2px solid {border_col if st.session_state.theme == 'dark' else 'rgba(49, 51, 63, 0.1)'};
        }}
        .wrap-table-container td {{
            padding: {p_v}px {p_h}px !important; /* Scaled padding */
            border-bottom: 1px solid {border_col if st.session_state.theme == 'dark' else 'rgba(49, 51, 63, 0.1)'};
            vertical-align: top; /* Better for wrapped text */
            text-align: left;
            
            /* WRAPPING ENABLED */
            white-space: normal !important; 
            word-wrap: break-word;
            line-height: 1.5;
            font-size: {base_font_size}px !important;
        }}
        .wrap-table-container tr:hover td {{
            background-color: { 'rgba(255,255,255,0.05)' if st.session_state.theme == 'dark' else '#f8f9fb' };
        }}
        </style>
        """
        st.markdown(table_css, unsafe_allow_html=True)
        st.markdown(f'<div class="wrap-table-container">{styled_html}</div>', unsafe_allow_html=True)

    else:
        # NORMAL MODE (Edit or Read)
        # If Edit Mode -> st.data_editor
        if mode == "✏️ Edit":
             st.caption("📍 Standard Grid Edit (No Wrap). Double-click cells to modify.")
             
             # --- AUTO-SAVE CALLBACK ---
             def auto_save_crm_grid(snapshot_df):
                 changes = st.session_state.get("crm_grid", {})
                 edited_rows = changes.get("edited_rows", {})
                 added_rows = changes.get("added_rows", [])
                 deleted_rows = changes.get("deleted_rows", [])
                 
                 count = 0
                 if edited_rows:
                     for index, updates in edited_rows.items():
                         if index < len(snapshot_df):
                             lead_id = int(snapshot_df.iloc[index]["id"])
                             if update_lead(lead_id, updates):
                                 count += 1
                 if added_rows:
                     for row in added_rows:
                         if not row.get("businessName"): row["businessName"] = "New Business"
                         if create_lead(row):
                             count += 1
                 if deleted_rows:
                     for index in deleted_rows:
                         if index in snapshot_df.index:
                             lead_id = int(snapshot_df.loc[index]["id"])
                             if delete_lead(lead_id):
                                 count += 1
                 if count > 0:
                     st.toast(f"💾 Auto-saved {count} changes!", icon="✅")

             edited_df = st.data_editor(
                df[cols],
                column_config=grid_config,
                hide_index=False, # Show row numbers explicitly
                use_container_width=True,
                num_rows="dynamic",
                key="crm_grid",
                height=int(final_height),
                column_order=display_cols,
                on_change=auto_save_crm_grid,
                kwargs={"snapshot_df": df}
            )
        
        else:
            # Standard Read Only
            styled_df = display_df.style\
                .map(get_status_style, subset=['Status'])\
                .map(get_priority_style, subset=['priority'])\
                .map(get_user_style, subset=['calledBy', 'meetingBy', 'closedBy'])\
                .set_properties(**base_props, subset=[c for c in display_df.columns if c not in ['Status', 'priority']])\
                .map(highlight_today, subset=['nextFollowUpDate'])\
                .apply(highlight_closed_rows, axis=1)\
                .format({"lastFollowUpDate": "{:%d/%m/%Y}", "nextFollowUpDate": "{:%d/%m/%Y}"}, na_rep="")
                
            read_only_config = grid_config.copy()
            if "status" in read_only_config: del read_only_config["status"]
            
            # Force hide index
            st.dataframe(
                styled_df, 
                column_config=read_only_config,
                use_container_width=True, 
                height=int(final_height),
                hide_index=False # Show row numbers explicitly
            )

# ==========================
# TOOL: SPREADSHEET INTELLIGENCE
# ==========================
# ==========================
# TOOL: SPREADSHEET INTELLIGENCE
# ==========================
if "Spreadsheet" in page:
    st.markdown(f"""<h1 style='display: flex; align-items: center;'>{get_icon_html('chart.png', 65)} Spreadsheet Intelligence</h1>""", unsafe_allow_html=True)

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
    
    
    # Header Layout with Filter on Right
    c_header, c_filter = st.columns([3.5, 2])
    
    with c_header:
        # Import Outfit Font
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap');
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <h1 style='font-family: "Outfit", sans-serif; font-weight: 700; display: flex; align-items: center; gap: 10px;'>
            <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Telephone%20Receiver.png" width="50" height="50" alt="📞"> 
            Power Dialer
        </h1>
        """, unsafe_allow_html=True)
        
    with c_filter:
        # Custom Toggle Switch UI
        # --- HIDDEN NATIVE RADIO FOR STATE MANAGEMENT ---
        # We keep this in the DOM but invisible so our custom JS can click it.
        # This ensures Streamlit state is handled natively without full reloads.
        st.markdown("""
        <style>
        /* Target ONLY the radio in the main content area (not sidebar) */
        section[data-testid="stMain"] div[data-testid="stRadio"] > label { display: none; }
        section[data-testid="stMain"] div[key="pd_filter_choice"], 
        section[data-testid="stMain"] div[data-testid="stRadio"] {
            height: 0px; opacity: 0; overflow: hidden; margin: 0; padding: 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        filter_choice = st.radio(
            "Filter Leads:", 
            ["Today's Follow-ups", "All Leads"],
            index=0,
            horizontal=True,
            key="pd_filter_choice"
        )

        # --- CUSTOM 3D TOGGLE COMPONENT ---
        # User-provided source code adapted for Streamlit bridge
        
        # Determine initial state for the visual toggle
        init_checked_1 = "checked" if filter_choice == "Today's Follow-ups" else ""
        init_checked_2 = "checked" if filter_choice == "All Leads" else ""
        init_flap_text = "Today's Follow-ups" if filter_choice == "Today's Follow-ups" else "All Leads"
        init_rotation = "-15deg" if filter_choice == "Today's Follow-ups" else "15deg" # Initial animation state helper
        
        # HTML/CSS/JS Block
        toggle_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        :root {{
            --accent: #04da97;
            --border-width: 4px; /* Scaled down from 6px */
            --border-radius: 55px;
            --font-size: 14px; /* Scaled down from 30px to fit UI */
        }}

        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            background-color: transparent; /* Transparent to blend */
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}

        .container {{
            perspective: 800px;
            transform: scale(0.85); /* Slight overall scale fix */
        }}

        .toggle {{
            position: relative;
            border: solid var(--border-width) var(--accent);
            border-radius: var(--border-radius);
            transition: transform cubic-bezier(0, 0, 0.30, 2) .4s;
            transform-style: preserve-3d;
            perspective: 800px;
            display: flex;
            flex-direction: row;
        }}

        .toggle>input[type="radio"] {{
            display: none;
        }}

        .toggle>#choice1:checked~#flap {{
            transform: rotateY(-180deg);
        }}

        .toggle>#choice1:checked~#flap>.content {{
            transform: rotateY(-180deg);
        }}

        .toggle>#choice2:checked~#flap {{
            transform: rotateY(0deg);
        }}

        .toggle>label {{
            display: inline-block;
            min-width: 140px; /* Adjusted width */
            padding: 12px 10px; /* Adjusted padding */
            font-size: var(--font-size);
            text-align: center;
            color: var(--accent);
            cursor: pointer;
            white-space: nowrap;
             user-select: none;
        }}

        .toggle>label,
        .toggle>#flap {{
            font-weight: bold;
            text-transform: capitalize;
        }}

        .toggle>#flap {{
            position: absolute;
            top: calc( 0px - var(--border-width));
            left: 50%;
            height: calc(100% + var(--border-width) * 2);
            width: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: var(--font-size);
            background-color: var(--accent);
            border-top-right-radius: var(--border-radius);
            border-bottom-right-radius: var(--border-radius);
            transform-style: preserve-3d;
            transform-origin: left;
            transition: transform cubic-bezier(0.4, 0, 0.2, 1) .5s;
        }}

        .toggle>#flap>.content {{
            color: #333;
            transition: transform 0s linear .25s;
            transform-style: preserve-3d;
        }}
        </style>
        </head>
        <body>

        <div class="container">
            <form class="toggle">
                <input type="radio" id="choice1" name="choice" value="today" {init_checked_1} onclick="selectOption('today')">
                <label for="choice1">Today's Follow-ups</label>

                <input type="radio" id="choice2" name="choice" value="all" {init_checked_2} onclick="selectOption('all')">
                <label for="choice2">All Leads</label>

                <div id="flap"><span class="content">{init_flap_text}</span></div>
            </form>
        </div>

        <script>
        const st = {{}};
        st.flap = document.querySelector('#flap');
        st.toggle = document.querySelector('.toggle');
        st.choice1 = document.querySelector('#choice1');
        st.choice2 = document.querySelector('#choice2');

        st.flap.addEventListener('transitionend', () => {{
            if (st.choice1.checked) {{
                st.toggle.style.transform = 'rotateY(-15deg)';
                setTimeout(() => st.toggle.style.transform = '', 400);
            }} else {{
                st.toggle.style.transform = 'rotateY(15deg)';
                setTimeout(() => st.toggle.style.transform = '', 400);
            }}
        }})

        st.clickHandler = (e) => {{
            if (e.target.tagName === 'LABEL') {{
                setTimeout(() => {{
                    st.flap.children[0].textContent = e.target.textContent;
                }}, 250);
            }}
        }}

        document.addEventListener('click', (e) => st.clickHandler(e));

        // --- SMART BRIDGE TO STREAMLIT ---
        function selectOption(val) {{
            try {{
                // 1. Target labels specifically in the MAIN section (avoid sidebar)
                const doc = window.parent.document;
                const main = doc.querySelector('section[data-testid="stMain"]');
                
                if (main) {{
                    const labels = main.querySelectorAll('div[role="radiogroup"] label');
                    
                    // 2. Find by TEXT CONTENT instead of index to be safe
                    for (let label of labels) {{
                        const text = label.textContent.trim();
                        if (val === 'today' && text.includes("Today")) {{
                            label.click();
                            return;
                        }}
                        if (val === 'all' && text.includes("All")) {{
                            label.click();
                            return;
                        }}
                    }}
                }}
            }} catch(e) {{
                console.error("Streamlit Bridge Error:", e);
            }}
        }}
        </script>
        </body>
        </html>
        """
        
        components.html(toggle_html, height=85, scrolling=False)
    
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
        
        # EXCLUDE Empty Dates (String comparison "" <= "2024-.." is True, so we must explicitly filter them out)
        mask_has_date = df["nextFollowUpDate"] != ""

        filtered_df = df[mask_active & mask_due & mask_not_contacted_today & mask_has_date]
        
        # SORT: Oldest First (Overdue -> Today)
        filtered_df = filtered_df.sort_values(by="nextFollowUpDate", ascending=True)
        
        # --- NEW: QUEUE VIEW vs DIALER VIEW LOGIC ---
        
        # 1. Check if we are in "List Mode" or "Active Call Mode"
        # We use a session state variable to track the actively selected lead from the list
        if "pd_active_lead_id" not in st.session_state:
            st.session_state.pd_active_lead_id = None
            
        # If filtered list is empty, show empty state
        if filtered_df.empty:
            # Styled Empty State (Existing Code)
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
            
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                def switch_to_all_leads():
                    st.session_state.pd_filter_choice = "All Leads"
                st.button("📂 Browse All Leads", type="primary", use_container_width=True, on_click=switch_to_all_leads)
            st.stop()
            
        # If we have leads, decide what to show



        if st.session_state.pd_active_lead_id is None:
            # --- SHOW THE LIST (QUEUE VIEW) ---
            st.markdown("### 📋 Today's Call Queue")
            
            # Custom CSS for the Cards Grid & Clickable Overlay
            # IMPORTANT: We use unindented string content to prevent Markdown from treating it as a code block.
            st.markdown("""<style>
@import url('https://fonts.googleapis.com/css?family=Inter:400,600,700&display=swap');
.queue-grid-wrapper {
    display: grid;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 20px;
    padding: 10px 0;
}
.queue-card-container {
    position: relative;
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 12px;
    padding: 18px;
    color: #333;
    background: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    transition: transform 0.1s ease, box-shadow 0.2s ease;
    height: 190px !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    pointer-events: none; /* Let clicks pass through to the button */
}

/* Typography */
.qc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.qc-date-badge {
    background: rgba(255,255,255,0.5);
    border-radius: 8px;
    padding: 6px 10px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.4);
    backdrop-filter: blur(4px);
}
.qc-day-num { font-size: 1.3rem; font-weight: 800; line-height: 1; color: #333; }
.qc-day-name { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #555; margin-top: 2px; }
.qc-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 8px;
    line-height: 1.35;
    word-wrap: break-word;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.qc-details {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #4a5568;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.qc-row { display: flex; align-items: center; gap: 8px; }

/* --- CARD INTERACTION & LAYOUT FIXES --- */

/* 1. Target the specific stVerticalBlock that wraps ONE card (our custom container)
   We use :not(:has(...)) to ensure we don't target the parent column which also "has" the card. */
/* 2. SIBLING SELECTOR STRATEGY: Target the Button immediately following the Card */
/* Move the button container UP to overlap the card. */
/* Calculation: Card Height (190px) + Gap (approx 16px) = 206px */

div[data-testid="stElementContainer"]:has(.queue-card-container) + div[data-testid="stElementContainer"]:has(.stButton),
div[data-testid="element-container"]:has(.queue-card-container) + div[data-testid="element-container"]:has(.stButton) {
    margin-top: -206px !important;
    height: 190px !important;
    z-index: 10 !important;
    position: relative !important;
    pointer-events: auto !important;
    margin-bottom: 24px !important; /* Visual gap between rows */
}

/* Ensure the stButton wrapper and internal button fill the space */
div[data-testid="stElementContainer"]:has(.queue-card-container) + div[data-testid="stElementContainer"]:has(.stButton) .stButton,
div[data-testid="element-container"]:has(.queue-card-container) + div[data-testid="element-container"]:has(.stButton) .stButton {
    width: 100% !important;
    height: 100% !important;
    min-height: 190px !important;
}

div[data-testid="stElementContainer"]:has(.queue-card-container) + div[data-testid="stElementContainer"]:has(.stButton) .stButton button,
div[data-testid="element-container"]:has(.queue-card-container) + div[data-testid="element-container"]:has(.stButton) .stButton button {
    width: 100% !important;
    height: 100% !important;
    border: none !important;
    background: transparent !important;
    color: transparent !important;
    cursor: pointer !important;
    padding: 0 !important;
    margin: 0 !important;
    display: block !important;
}

/* Remove default hover/focus effects from the invisible button */
div[data-testid="stElementContainer"]:has(.queue-card-container) + div[data-testid="stElementContainer"]:has(.stButton) .stButton button:hover,
div[data-testid="stElementContainer"]:has(.queue-card-container) + div[data-testid="stElementContainer"]:has(.stButton) .stButton button:focus,
div[data-testid="stElementContainer"]:has(.queue-card-container) + div[data-testid="stElementContainer"]:has(.stButton) .stButton button:active,
div[data-testid="element-container"]:has(.queue-card-container) + div[data-testid="element-container"]:has(.stButton) .stButton button:hover,
div[data-testid="element-container"]:has(.queue-card-container) + div[data-testid="element-container"]:has(.stButton) .stButton button:focus,
div[data-testid="element-container"]:has(.queue-card-container) + div[data-testid="element-container"]:has(.stButton) .stButton button:active {
    background: transparent !important;
    color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Pointer Events: Allow clicks on the button, but pass-through visuals on the card */
.queue-card-container {
    pointer-events: none;
    height: 190px !important; 
    margin-bottom: 0px !important; /* Ensure no extra margin inside the container */
}

/* 4. ANIMATION: Scale card when the sibling button is active */
/* Note: :has(+ ...) allows us to style the card when the NEXT sibling button is active */
div[data-testid="stElementContainer"]:has(.queue-card-container):has(+ div[data-testid="stElementContainer"] .stButton button:active) .queue-card-container,
div[data-testid="element-container"]:has(.queue-card-container):has(+ div[data-testid="element-container"] .stButton button:active) .queue-card-container {
    transform: scale(0.98);
    transition: transform 0.1s ease;
}
</style>""", unsafe_allow_html=True)

            # Gradients
            gradients = [
                "linear-gradient(135deg, #E3F2FD 0%, #90CAF9 100%)", # Blue
                "linear-gradient(135deg, #FFF3E0 0%, #FFCC80 100%)", # Orange
                "linear-gradient(135deg, #E8F5E9 0%, #A5D6A7 100%)", # Green
                "linear-gradient(135deg, #F3E5F5 0%, #CE93D8 100%)", # Purple
                "linear-gradient(135deg, #FAFAFA 0%, #E0E0E0 100%)"  # Grey
            ]

            # Icons
            import base64
            def get_b64_icon(path):
                try:
                    with open(path, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                except: return ""

            icon_phone_path = '/Users/satyajeetsinhrathod/.gemini/antigravity/brain/dc0185d0-ed71-439f-bab7-e65957b15690/uploaded_image_2_1768732438815.png'
            phone_icon_b64 = get_b64_icon(icon_phone_path)
            phone_icon_html = f'<img src="data:image/png;base64,{phone_icon_b64}" width="16" style="vertical-align:middle;">' if phone_icon_b64 else '📞'
            
            # --- RENDER GRID ---
            # We iterate in chunks of 3 to create rows
            cols = st.columns(3)
            
            for i, (idx, row) in enumerate(filtered_df.iterrows()):
                col_idx = i % 3
                with cols[col_idx]:
                    # USE CONTAINER TO ISOLATE EACH CARD CONTEXT
                    with st.container():
                        bg_gradient = gradients[i % len(gradients)]
                        
                        # Date Logic
                        try:
                            d_obj = pd.to_datetime(row.get('nextFollowUpDate'))
                            day_num = d_obj.strftime("%d")
                            day_name = d_obj.strftime("%b").upper()
                        except:
                            day_num = "--"
                            day_name = "TODO"
                        
                        # 1. Render the Visual Card (Markdown)
                        # We ensure the markdown takes up the fixed height
                        card_html = f"""
                        <div class="queue-card-container" style="background: {bg_gradient};">
                            <div class="qc-header">
                                <div class="qc-date-badge">
                                    <div class="qc-day-num">{day_num}</div>
                                    <div class="qc-day-name">{day_name}</div>
                                </div>
                                <!-- Index removed as requested -->
                            </div>
                            <div class="qc-title">{row.get('businessName', 'Unknown')}</div>
                            <div class="qc-details">
                                <div class="qc-row">👤 {row.get('contactName', 'No Name')}</div>
                                <div class="qc-row">{phone_icon_html} {row.get('phone', 'No Phone')}</div>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # 2. Render the Button OVERLAY
                        # The CSS now targets this button using the Sibling Selector (+ div:has(.stButton))
                        # It will be pulled UP by 206px to cover the card.
                        if st.button(" ", key=f"btn_card_{row['id']}", use_container_width=True):
                             st.session_state.pd_active_lead_id = row['id']
                             st.session_state.pd_jump_to_id = row['id'] # Signal to force-update the index
                             st.rerun()

            st.stop()

        else:
            # --- ACTIVE CALL MODE (QUEUE NAV) ---
            # We want to iterate through the filtered queue, not just see one record.
            
            # 1. Use the Queue subset (filtered_df) as our working dataframe
            if not filtered_df.empty:
                df = filtered_df.reset_index(drop=True)
            else:
                # Fallback if queue empty
                st.session_state.pd_active_lead_id = None
                st.rerun()

            # 2. Handle "Jump To" from Card Click
            if "pd_jump_to_id" in st.session_state and st.session_state.pd_jump_to_id is not None:
                # Find the index of the requested lead in our new 'df'
                jump_id = st.session_state.pd_jump_to_id
                idx_list = df.index[df['id'] == jump_id].tolist()
                
                if idx_list:
                    st.session_state.dialer_index = idx_list[0]
                else:
                    # Lead might have disappeared from filter (e.g. status changed elsewhere)
                    st.toast("Lead not found in current queue.")
                    st.session_state.dialer_index = 0
                
                # Clear the trigger so we don't keep forcing index on next run
                st.session_state.pd_jump_to_id = None

            # 3. Back Button to return to Grid View
            if st.button("⬅ Back to Queue"):
                st.session_state.pd_active_lead_id = None
                st.rerun()

        # The existing code continues below, rendering the 'Main Lead Card' using 'df' and 'dialer_index'
        # which we have now correctly set up.
        
        # We assign to df, so the logic falls through
        pass # proceed to rendering
        
    else:
        # For "All Leads", we reset the active lead state to ensure standard navigation
        st.session_state.pd_active_lead_id = None
        df = df
        st.success(f"Showing all {len(df)} leads.")
    
    # ... Existing pagination logic below ...

    # Session State for Current Index
    if "dialer_index" not in st.session_state:
        st.session_state.dialer_index = 0
        
    # Validation
    if st.session_state.dialer_index >= len(df):
        st.session_state.dialer_index = 0
        
    lead = df.iloc[st.session_state.dialer_index]
    
    # --- PREMIUM LAYOUT RESTRUCTURE ---
    
    # Custom CSS for Cards (Dynamic Theme Support)
    st.markdown("""
    <style>
    .style_card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
    }
    .dark-mode-card {
        background-color: #1E1E1E !important;
        border: 1px solid #333 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        color: #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. Progress Bar Section (Full Width)
    current_theme = st.session_state.get("theme", "light") # 'light' or 'dark'
    # Check boolean toggle for Google Mode as well
    is_google_mode = st.session_state.get("google_ui_mode", False)
    
    # Determine CSS classes based on effective theme
    card_bg = "#1E1E1E" if (current_theme == "dark" and not is_google_mode) else "white"
    card_border = "#333" if (current_theme == "dark" and not is_google_mode) else "#f0f0f0"
    card_shadow = "0 4px 12px rgba(0,0,0,0.2)" if (current_theme == "dark" and not is_google_mode) else "0 4px 12px rgba(0,0,0,0.05)"
    
    def get_card_style(key):
        return f"""<style>
div[data-testid="stVerticalBlock"]:has(div#{key}) {{
    background-color: {card_bg};
    border-radius: 12px;
    padding: 20px;
    box-shadow: {card_shadow};
    border: 1px solid {card_border};
    gap: 10px;
}}
</style>
<div id="{key}" style="display:none;"></div>"""

    card_class = "style_card"
    if current_theme == "dark" and not is_google_mode:
        card_class += " dark-mode-card"
    
    progress_val = st.session_state.dialer_index + 1
    total_leads = len(df)
    prog_percent = int((progress_val / total_leads) * 100) if total_leads > 0 else 0
    
    # Colors
    prog_color = "#1976d2" if not (current_theme == "dark" and not is_google_mode) else "#90caf9"
    text_main = "#333" if not (current_theme == "dark" and not is_google_mode) else "#fff"
    text_color = text_main # Alias for use in f-strings
    text_sub = "#888" if not (current_theme == "dark" and not is_google_mode) else "#aaa"

    with st.container():
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 8px;">
                <div style="font-weight: 600; font-size: 1.1rem; display: flex; align-items: center; gap: 8px; color: {text_main};">
                    <span style="color: {prog_color};">📊</span> Lead {progress_val} of {total_leads}
                </div>
                <div style="font-size: 0.85rem; color: {text_sub};">
                    <span style="margin-right: 15px;">Completed <b style="color: {prog_color}; font-size:1.1rem;">{st.session_state.dialer_index}</b></span>
                    <span>Remaining <b style="color: {text_main}; font-size:1.1rem;">{total_leads - st.session_state.dialer_index}</b></span>
                </div>
            </div>
            <div style="font-size: 0.8rem; color: {text_sub}; margin-bottom: 8px;">{prog_percent}% Complete</div>
            <div style="width: 100%; background-color: {'#f0f0f0' if not (current_theme == 'dark' and not is_google_mode) else '#333'}; height: 6px; border-radius: 4px; overflow: hidden;">
                <div style="width: {prog_percent}%; background-color: {prog_color}; height: 100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 2. Main 2-Column Layout
    main_col1, main_col2 = st.columns([2.2, 1])

    # --- LEFT COLUMN ---
    with main_col1:
        # A. Lead Header Card
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 2.5rem;">🏢</div>
                <div>
                    <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: {text_main};">{lead.get('businessName', 'Unknown')}</h2>
                    <div style="color: {text_sub}; margin-top: 4px;">{lead.get('contactName', 'None')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
        # B. Lead Information Card
        with st.container():
            st.markdown(get_card_style("lead_info_card"), unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:{text_main}'>Lead Information</h3>", unsafe_allow_html=True)
            
            # Status & Priority Row
            c_info1, c_info2 = st.columns(2)
            with c_info1:
                st.caption("STATUS")
                # Custom Badge Style
                st.markdown(f"""
                <div style="
                    background-color: #dff5e1; 
                    color: #1b5e20; 
                    padding: 4px 12px; 
                    border-radius: 16px; 
                    display: inline-block; 
                    font-weight: 600; 
                    font-size: 0.9rem;">
                    {lead.get('status', 'New')}
                </div>
                """, unsafe_allow_html=True)

            with c_info2:
                # Priority Key Logic
                prio_key = f"prio_edit_{lead['id']}"
                current_prio = lead.get('priority', 'WARM')
                
                # Sync state if needed
                if prio_key not in st.session_state:
                    st.session_state[prio_key] = current_prio
                
                # Priority Dropdown
                prio_opts = ["HOT", "WARM", "COLD"]
                if current_prio not in prio_opts: prio_opts.append(current_prio)
                
                new_prio = st.selectbox("PRIORITY", prio_opts, key=prio_key)
                
                # Update if changed
                if new_prio != current_prio:
                    update_lead(lead['id'], {"priority": new_prio})
                    st.toast(f"Priority updated to {new_prio}")
                    time.sleep(0.5)
                    st.rerun()

            st.markdown("---")
        
            # Contact Details List (HTML representation)
            def icon_row(icon, label, value):
                theme_text = "#eee" if (current_theme == "dark" and not is_google_mode) else "#333"
                theme_sub = "#aaa" if (current_theme == "dark" and not is_google_mode) else "#999"
                return f"""
                <div style="display: flex; gap: 15px; margin-bottom: 15px; align-items: flex-start;">
                    <div style="min-width: 24px; text-align: center; font-size: 1.2rem; color: #666;">{icon}</div>
                    <div>
                        <div style="font-size: 0.75rem; color: {theme_sub}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom:2px;">{label}</div>
                        <div style="font-size: 1rem; color: {theme_text}; font-weight: 500;">{value}</div>
                    </div>
                </div>
                """
            
            contact_html = ""
            contact_html += icon_row("📍", "Address", lead.get('address', 'N/A'))
            
            # Phone with copy style
            # Phone with copy style
            phone_val = str(lead.get('phone', 'N/A'))
            if phone_val and phone_val not in ['N/A', 'nan', 'None', '']:
                phone_content = f"<a href='tel:{phone_val}' style='color: inherit; text-decoration: none;'>{phone_val}</a>"
            else:
                phone_content = phone_val
                
            phone_box = f"<span style='background: {'#333' if (current_theme == 'dark' and not is_google_mode) else '#f5f5f5'}; padding: 4px 8px; border-radius: 4px; font-family: monospace;'>{phone_content}</span>"
            contact_html += icon_row("📞", "Phone", phone_box)
            
            contact_html += icon_row("✉️", "Email", lead.get('email', 'N/A'))
            
            st.markdown(contact_html, unsafe_allow_html=True)
            # End Card

        # C. Call Notes Card
        with st.container():
            st.markdown(get_card_style("call_notes_card"), unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:{text_main}'>📝 Call Notes</h3>", unsafe_allow_html=True)
            
            notes_key = f"notes_{lead['id']}"
            if notes_key not in st.session_state:
                st.session_state[notes_key] = lead.get('callNotes', '')
                
            new_notes = st.text_area(
                "Add notes about this call",
                value=st.session_state[notes_key],
                height=150,
                key=f"widget_{notes_key}",
                placeholder="Type call details here..."
            )
            # Sync back to session state
            st.session_state[notes_key] = new_notes

    # --- RIGHT COLUMN (Action Panel) ---
    with main_col2:
        # D. Quick Actions Card
        with st.container():
            # Inject Card Style + Special Button Style for Not Interested
            st.markdown(get_card_style("actions_card") + """
<style>
/* Specific red outline for the 5th button in this specific container */
div[data-testid="stVerticalBlock"]:has(div#actions_card) div.stButton:nth-of-type(5) button {
    border-color: #ef4444 !important;
    color: #ef4444 !important;
}
div[data-testid="stVerticalBlock"]:has(div#actions_card) div.stButton:nth-of-type(5) button:hover {
    background-color: #fef2f2 !important;
    border-color: #dc2626 !important;
}
</style>
""", unsafe_allow_html=True)
            
            st.markdown(f"<h3 style='color:{text_main}'>⚡ Quick Actions</h3>", unsafe_allow_html=True)
            
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            # Action Helper
            def next_lead():
                if filter_choice == "All Leads":
                    st.session_state.dialer_index += 1
                # If 'Today', rerun handles list update
            
            # 1. Interested (Primary)
            if st.button("✅ Interested", type="primary", use_container_width=True):
                update_lead(lead['id'], {
                    "status": "Interested", "priority": "HOT", 
                    "callNotes": st.session_state[notes_key], "lastFollowUpDate": today_date
                })
                st.toast("Marked Interested! 🚀")
                next_lead()
                time.sleep(0.5)
                st.rerun()
                
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # 2. Meeting Set (Primary)
            if st.button("📅 Meeting Set", type="primary", use_container_width=True):
                st.session_state[f"open_meet_{lead['id']}"] = True
            
            if st.session_state.get(f"open_meet_{lead['id']}", False):
                @st.dialog("📅 Schedule Meeting")
                def show_meeting_modal():
                    st.write(f"Book meeting with {lead.get('businessName')}")
                    c1, c2 = st.columns(2)
                    d = c1.date_input("Date", value=datetime.now().date() + pd.Timedelta(days=1))
                    t = c2.time_input("Time", value=datetime.now().time())
                    if st.button("Confirm", type="primary", use_container_width=True):
                        ts = pd.Timestamp(datetime.combine(d, t))
                        update_lead(lead['id'], {
                            "status": "Meeting set", "priority": "HOT",
                            "callNotes": st.session_state[notes_key], "lastFollowUpDate": today_date,
                            "meetingDate": str(ts), "nextFollowUpDate": str(d)
                        })
                        st.success("Meeting Scheduled!")
                        del st.session_state[f"open_meet_{lead['id']}"]
                        next_lead()
                        st.rerun()
                show_meeting_modal()

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            # 3. Not Picking (Standard)
            if st.button("🚫 Not Picking", use_container_width=True):
                next_d_val = st.session_state.get(f"next_action_date_{lead['id']}", datetime.now().date() + pd.Timedelta(days=1))
                update_lead(lead['id'], {
                    "status": "Not picking", "callNotes": st.session_state[notes_key],
                    "lastFollowUpDate": today_date, "nextFollowUpDate": str(next_d_val)
                })
                st.toast(f"Marked Not Picking (Next: {next_d_val})")
                next_lead()
                time.sleep(0.3)
                st.rerun()
            
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # 4. Call Later
            if st.button("⏰ Call Later", use_container_width=True):
                next_d_val = st.session_state.get(f"next_action_date_{lead['id']}", datetime.now().date() + pd.Timedelta(days=1))
                update_lead(lead['id'], {
                    "status": "Call Later", "callNotes": st.session_state[notes_key],
                    "lastFollowUpDate": today_date, "nextFollowUpDate": str(next_d_val)
                })
                st.toast(f"Snoozed until {next_d_val}")
                next_lead()
                time.sleep(0.3)
                st.rerun()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            
            # 5. Not Interested
            if st.button("❌ Not Interested", use_container_width=True):
                update_lead(lead['id'], {
                    "status": "Not Interested", "priority": "COLD",
                    "callNotes": st.session_state[notes_key], "lastFollowUpDate": today_date
                })
                st.toast("Marked Not Interested")
                next_lead()
                time.sleep(0.3)
                st.rerun()



        # E. Next Follow-Up (Nav) Card
        with st.container():
            st.markdown(get_card_style("next_step_card"), unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:{text_main}'>🗓 Next Follow-Up</h3>", unsafe_allow_html=True)
            
            next_date_key = f"next_action_date_{lead['id']}"
            
            # Default to tomorrow
            default_d = datetime.now().date() + pd.Timedelta(days=1)
            f_next = lead.get('nextFollowUpDate')
            if f_next:
                try:
                    parsed_d = pd.to_datetime(f_next).date()
                    default_d = max(parsed_d, datetime.now().date())
                except: pass

            def on_next_date_change():
                new_val = st.session_state[next_date_key]
                if new_val:
                    update_lead(lead['id'], {"nextFollowUpDate": str(new_val)})
                    st.toast(f"Updated Next Follow-Up: {new_val}")

            st.date_input(
                "Select Date",
                value=default_d,
                min_value=datetime.now().date(),
                key=next_date_key,
                label_visibility="collapsed",
                on_change=on_next_date_change
            )

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            
            # Navigation Buttons
            c_nav1, c_nav2 = st.columns(2)
            with c_nav1:
                # Previous Button (Secondary/Outline style if possible via CSS, using standard here)
                if st.button("Previous", use_container_width=True, disabled=(st.session_state.dialer_index == 0)):
                    st.session_state.dialer_index = max(0, st.session_state.dialer_index - 1)
                    st.rerun()
            with c_nav2:
                # Skip Button
                if st.button("Skip", use_container_width=True):
                    st.session_state.dialer_index += 1
                    st.rerun()
                    




        



# ================== LEAD GENERATOR (COMMENTED OUT) ==================
# if "Lead Generator" in page:
#     st.markdown(f"""<h1 style='display: flex; align-items: center;'>{get_icon_html('rocket.png', 70)} Lead Generator</h1>""", unsafe_allow_html=True)
#     
#     with st.form("gen_form"):
#         c1, c2 = st.columns(2)
#         query = c1.text_input("Business Type", "Dentist")
#         loc = c2.text_input("Location", "New York")
#         submitted = st.form_submit_button("Start Mining Leads", type="primary")
#         
#     if submitted:
#         with st.spinner("Disconnecting from matrix... (Scraping)"):
#             try:
#                 r = requests.post(LEAD_GEN_API, json={"query": query, "location": loc}, timeout=120)
#                 if r.status_code == 200:
#                     st.success("✅ Leads Generated & Saved to CRM!")
#                     st.download_button("Download CSV", r.content, f"{query}.csv", "text/csv")
#                 else:
#                     st.error("backend error")
#             except Exception as e:
#                 st.error(f"Error: {e}")
#                 
#     # History moved to Sidebar

# ================== GOOGLE MAPS SCRAPER ==================
if "Google Maps Scraper" in page:

    
    # INIT SESSION STATE
    if 'scraper_running' not in st.session_state:
        st.session_state.scraper_running = False
        
    # --- STATE MANAGEMENT BRIDGE ---
    # We use a native Streamlit checkbox to track the toggle state.
    # We HIDE it visually using CSS so the user doesn't see it, 
    # but the JS bridge can still click it programmatically.
    
    st.markdown("""
    <style>
    /* HIDE the specific checkbox used for state management */
    /* We target all checkboxes on this page view since it's the only one here. */
    div[data-testid="stCheckbox"] {
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if 'google_ui_mode' not in st.session_state:
        st.session_state.google_ui_mode = False

    # The Logic Trigger (Hidden by CSS above)
    google_mode = st.checkbox("Google UI Mode", value=st.session_state.google_ui_mode, key="google_ui_toggle")

    # --- CONDITIONAL STYLES ---
    if google_mode:
        # GOOGLE THEME (Blue/Colorful + Global Overrides)
        st.markdown("""
        <style>
        /* --- GLOBAL GOOGLE FONT & BACKGROUND --- */
        @import url('https://fonts.googleapis.com/css?family=Product+Sans:400,500,700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Product Sans', 'Roboto', Arial, sans-serif !important;
        }
        
        /* App Background - Google Drive/Docs Light Grey */
        .stApp {
            background-color: #ffffff !important; 
        }
        
        /* --- GOOGLE SHEETS STYLE TABLES --- */
        div[data-testid="stDataFrame"] {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
        }
        div[data-testid="stDataFrame"] table {
            font-family: 'Roboto', sans-serif !important;
        }
        thead tr th {
            background-color: #f1f3f4 !important; /* Google Headers */
            color: #202124 !important;
            font-weight: 600 !important;
            border-bottom: 1px solid #e0e0e0 !important;
        }
        tbody tr td {
            color: #3c4043 !important;
        }
        
        /* --- GOOGLE STYLE ALERTS --- */
        div[data-testid="stAlert"] {
            padding: 0.5rem 1rem !important;
            border-radius: 8px !important;
            border: 1px solid transparent !important;
            background-color: #fce8e6 !important; /* Default to generic error light red, overridden below */
        }
        
        /* Google Blue Button */
        div[data-testid="stMain"] div.stButton > button {
            background-color: #1a73e8 !important;
            color: white !important;
            border-radius: 24px !important;
            border: none !important;
            box-shadow: 0 1px 2px rgba(60,64,67,0.3) !important;
            font-family: 'Product Sans', sans-serif !important;
            padding: 0.5rem 1.5rem !important;
        }
        div[data-testid="stMain"] div.stButton > button:hover {
            background-color: #1765cc !important;
            box-shadow: 0 1px 3px 1px rgba(60,64,67,0.15), 0 1px 2px 0 rgba(60,64,67,0.3) !important;
            transform: translateY(-1px);
        }
        
        /* Material Inputs */
        div[data-testid="stTextInput"] input {
            border-radius: 8px !important;
            border: 1px solid #dadce0 !important;
            background: #fff !important;
            color: #202124 !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border: 2px solid #1a73e8 !important;
            padding: 9px 11px !important;
            box-shadow: none !important;
        }
        div[data-testid="stTextInput"] label {
            color: #5f6368 !important;
            font-weight: 500 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        gradient_bar = "linear-gradient(to right, #4285F4 25%, #EA4335 25%, #EA4335 50%, #FBBC05 50%, #FBBC05 75%, #34A853 75%)"
        
    else:
        # STEALTH/COOL THEME (Black/Monochrome)
        st.markdown("""
        <style>
        /* Stealth Black Button */
        div[data-testid="stMain"] div.stButton > button {
            background-color: #202124 !important; /* Google Dark Grey */
            color: #e8eaed !important;
            border-radius: 8px !important;
            border: 1px solid #3c4043 !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
        }
        div[data-testid="stMain"] div.stButton > button:hover {
            background-color: #303134 !important;
            border-color: #5f6368 !important;
            color: #fff !important;
            transform: scale(1.01);
        }
        /* Stealth Inputs */
        div[data-testid="stTextInput"] input {
            border-radius: 6px !important;
            border: 1px solid #3c4043 !important;
            background-color: #f1f3f4 !important; /* Light Grey surface */
            color: #202124 !important;
        }
        div[data-testid="stTextInput"] input:focus {
            background-color: #ffffff !important;
            border: 1px solid #202124 !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        gradient_bar = "linear-gradient(to right, #202124, #3c4043, #5f6368)"


    # --- ANIMATED HEADER WIDGET (With Bridge) ---
    # We pass the current python state 'checked' to the HTML so it preserves state on reload
    is_checked = "checked" if google_mode else ""
    
    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css?family=Product+Sans&display=swap');
    :root {
        --blue: #4285F4;
        --yellow: #fBBC05;
        --green: #34A853;
        --red: #EA4335;
        --red-darker: #DE2817;
    }
    body {
        font-family: 'Product Sans', 'Arial', sans-serif;
        margin: 0; padding: 0;
        display: flex; align-items: center;
        background: transparent;
        height: 100px;
        overflow: hidden;
    }
    .wrapper {
        display: flex; align-items: center;
        margin-left: 2px;
    }
    .widget {
        position: relative;
        display: flex; align-items: center;
        font-size: 55px; 
        font-weight: 600;
        line-height: 1;
    }
    input#toggle { display: none; }
    
    span.letter {
        display: inline-block;
        color: #000000;
        transition: color 0.2s ease-in;
    }
    
    .upperg { font-size: 1.0em; }
    .e { transform: rotate(-15deg); }

    /* Checked State */
    #toggle:checked ~ label { background: var(--yellow); }
    #toggle:checked ~ label #switch { 
        transform: translateX(0.4em); 
        background: #DDA703; 
    }

    #toggle:checked ~ .blue { color: var(--blue); }
    #toggle:checked ~ .green { color: var(--green); }
    #toggle:checked ~ .red { color: var(--red); }
    
    /* Default State */
    label {
        display: inline-block;
        background: #333333;
        width: 0.9em; height: 0.5em;
        border-radius: 0.4em;
        margin: 0 0.05em;
        position: relative;
        cursor: pointer;
        vertical-align: middle;
        transition: background 0.2s;
    }
    
    #switch {
        position: absolute;
        top: 0; left: 0;
        width: 0.5em; height: 0.5em;
        border-radius: 50%;
        background: #000000;
        box-shadow: 2px 0px 5px rgba(0,0,0,0.3);
        transition: transform 0.2s ease-in, background 0.2s;
    }

    .maps-text {
        font-size: 48px;
        font-weight: 800;
        color: #31333F;
        margin-left: 15px;
        white-space: nowrap;
    }
    @media (prefers-color-scheme: dark) {
        .maps-text { color: #FAFAFA; }
    }
    
    /* --- WIDGET MOBILE RESPONSIVENESS --- */
    @media only screen and (max-width: 600px) {
        .widget { font-size: 32px; }
        .maps-text { font-size: 28px; margin-left: 8px; }
        .wrapper { transform: scale(0.9); transform-origin: left center; }
    }
    </style>
    </head>
    <body>
    <div class="wrapper">
        <div class="widget">
            <!-- Inject Python State Here -->
            <input id="toggle" type="checkbox" {is_checked}>
            <span class="letter blue upperg">G</span>
            <label for="toggle"><div id="switch"></div></label>
            <span class="letter blue g">g</span>
            <span class="letter green l">l</span>
            <span class="letter red e">e</span>
        </div>
        <div class="maps-text">Maps Scraper</div>
    </div>
    
    <script>
    const toggle = document.getElementById('toggle');
    
    toggle.addEventListener('change', function() {
        // BRIDGE: Trigger Streamlit Checkbox
        try {
            const doc = window.parent.document;
            // Search for label by text content
            const labels = doc.querySelectorAll('label');
            for (let label of labels) {
                if (label.textContent.includes("Google UI Mode")) {
                    label.click();
                    break;
                }
            }
        } catch (e) {
            console.error("Bridge Error:", e);
        }
    });
    </script>
    </body>
    </html>
    """.replace("{is_checked}", is_checked), height=100)
    
    # INIT SESSION STATE
    if 'scraper_running' not in st.session_state:
        st.session_state.scraper_running = False

    with st.container(border=True):
        # 1. Dynamic Top Bar
        st.markdown(f"""
        <div style="
            height: 6px; 
            width: 100%; 
            background: {gradient_bar}; 
            border-radius: 4px;
            margin-bottom: 15px;
            transition: all 0.5s ease;
        "></div>
        """, unsafe_allow_html=True)
        
        # 2. Header
        st.markdown("### 🎯 Start New Mining Job")
        st.caption("Enter a business category and location to retrieve real-time leads from Google Maps.")
        
        c1, c2 = st.columns(2)
        # Enhanced Labels with Icons
        target_business = c1.text_input("🏢 Business Category", value="Dentist", placeholder="e.g. Gym, Plumber, Architect")
        target_location = c2.text_input("📍 Target Location", value="Gotri, Vadodara", placeholder="e.g. New York, Mumbai")
        
        st.write("") # Visual Spacer
        start_scrape = st.button("🚀 Launch Scraper", type="primary", use_container_width=True)
    
    # --- SHOW EXISTING SCRAPED RESULTS ---
    output_file = "scraped_results.csv"
    if os.path.exists(output_file) and not start_scrape:
        try:
            if os.stat(output_file).st_size == 0:
                df_existing = pd.DataFrame()
            else:
                df_existing = pd.read_csv(output_file)
            
            if not df_existing.empty:
                st.markdown("---")
                st.subheader(f"📊 Previous Scrape Results ({len(df_existing)} leads)")
                
                # Reorder and Rename Columns
                # Reorder and Rename Columns
                # Format: Business Name, Phone Number, Address, Website, Email, Map Link, Status, Notes
                col_map = {
                    "clinic_name": "Business Name",
                    "phone_number": "Phone Number",
                    "address": "Address",
                    "website_url": "Website",
                    "email": "Email",
                    "place_url": "Map Link", # "Map Link" as per user request
                    "google_maps_url": "Map Link",
                    "url": "Map Link",
                    "Maps Link": "Map Link" # Handle legacy/user-edit consistency
                }
                
                df_existing.rename(columns=col_map, inplace=True)

                # Ensure missing columns exist
                if "Status" not in df_existing.columns:
                    df_existing["Status"] = "Generated"
                if "Priority" not in df_existing.columns:
                    df_existing["Priority"] = "WARM"
                if "Notes" not in df_existing.columns:
                    df_existing["Notes"] = ""
                
                # Define desired order
                desired_order = ["Business Name", "Phone Number", "Address", "Website", "Email", "Map Link", "Status", "Priority", "Notes"]
                
                # Filter / Arrange columns
                final_cols = [c for c in desired_order if c in df_existing.columns]
                # Add any other remaining columns at the end just in case
                remaining_cols = [c for c in df_existing.columns if c not in final_cols and c not in ["query", "location", "rating", "reviews"]]
                final_cols.extend(remaining_cols)
                
                df_display_existing = df_existing[final_cols]
                
                # Force string type for phone to avoid decimals causing issues later
                if "Phone Number" in df_display_existing.columns:
                     df_display_existing["Phone Number"] = df_display_existing["Phone Number"].astype(str).replace(r'\.0$', '', regex=True).replace("nan", "")
                
                # --- Interactive Editor Config ---
                scrape_config = {
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Generated", "Interested", "Not picking", "Asked to call later", "Meeting set", "Meeting Done", "Proposal sent", "Follow-up scheduled", "Not interested", "Closed - Won", "Closed - Lost"],
                        required=True,
                        width="medium"
                    ),
                    "Priority": st.column_config.SelectboxColumn(
                         "Priority",
                         options=["HOT", "WARM", "COLD"],
                         required=True,
                         width="small"
                    ),
                    "Map Link": st.column_config.LinkColumn(
                        "Map Link", display_text="View on Map"
                    ),
                    "Website": st.column_config.LinkColumn(
                        "Website", display_text="Visit"
                    ),
                    "Notes": st.column_config.TextColumn(
                        "Notes", width="large"
                    )
                }

                edited_scrape_df = st.data_editor(
                    df_display_existing, 
                    column_config=scrape_config,
                    use_container_width=True, 
                    height=400,
                    key="scraped_results_editor",
                    num_rows="dynamic",
                    hide_index=True
                )
                
                # Update df_display_existing with edits for download/saving
                if not edited_scrape_df.equals(df_display_existing):
                    df_display_existing = edited_scrape_df
                
                # Download and Import buttons
                # Download and Import buttons
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                
                import io
                # Robust filename sanitizer
                def sanitize_name(s):
                    if not s: return "data"
                    # Keep alphanumeric, underscores, hyphens. Replace spaces with underscores.
                    s = str(s).strip().replace(" ", "_")
                    s = "".join(c for c in s if c.isalnum() or c in ('_', '-'))
                    return s if s else "data"
                
                # Use current inputs for filename, default to "Scraped_Leads" if empty
                safe_query = sanitize_name(target_business) if target_business else "Search"
                safe_loc = sanitize_name(target_location) if target_location else "Location"
                export_filename = f"{safe_query}_{safe_loc}_Leads"

                # Prepare Export DataFrame with Renamed Columns
                export_df = df_display_existing.copy()
                
                # Normalize columns to ensure matching works
                export_df.columns = [str(c).strip() for c in export_df.columns]
                
                # Direct mapping - force rename
                # We used "Business Name" in the UI, we want "Name" in export
                rename_map = {
                    "Business Name": "Name",
                    "Phone Number": "Contact No",
                    "Priority": "Response",
                    "Map Link": "Map Link",
                    "Status": "Status", # Keep same
                    "Address": "Address", # Keep same
                    "Website": "Website", # Keep same
                    "Email": "Email" # Keep same
                }
                export_df.rename(columns=rename_map, inplace=True)
                
                # Enforce exact column order for the primary columns
                target_order = ["Name", "Contact No", "Address", "Website", "Email", "Status", "Response", "Map Link", "Notes"]
                
                # Reorder columns: Keep those that exist in target_order, append the rest
                existing_cols = list(export_df.columns)
                ordered_cols = [c for c in target_order if c in existing_cols]
                other_cols = [c for c in existing_cols if c not in ordered_cols]
                
                export_df = export_df[ordered_cols + other_cols]
                
                # Explanation for the user constraint - Removed per user request

                # Removed Plain CSV button to avoid confusion
                
                with col_btn2:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        export_df.to_excel(writer, index=False, sheet_name='Leads')
                        
                        # --- Excel Styling & Validation ---
                        workbook = writer.book
                        worksheet = writer.sheets['Leads']
                        
                        # 1. Validation (Hidden Sheet)
                        ref_sheet = workbook.create_sheet("DataValidation")
                        ref_sheet.sheet_state = 'hidden'
                        
                        status_options = ["Generated", "Interested", "Not picking", "Asked to call later", "Meeting set", "Meeting Done", "Proposal sent", "Follow-up scheduled", "Not interested", "Closed - Won", "Closed - Lost"]
                        response_options = ["HOT", "WARM", "COLD"]
                        
                        for idx, val in enumerate(status_options, start=1): ref_sheet.cell(row=idx, column=1).value = val
                        for idx, val in enumerate(response_options, start=1): ref_sheet.cell(row=idx, column=2).value = val
                            
                        from openpyxl.worksheet.datavalidation import DataValidation
                        from openpyxl.styles import Font, PatternFill, Alignment
                        from openpyxl.utils import get_column_letter

                        max_row = len(export_df) + 1
                        
                        # Apply Validation Logic
                        def get_col_letter_map(col_name):
                            try: return get_column_letter(export_df.columns.get_loc(col_name) + 1)
                            except: return None

                        # Status Validation
                        status_col = get_col_letter_map("Status")
                        if status_col:
                            dv_status = DataValidation(type="list", formula1=f"'DataValidation'!$A$1:$A${len(status_options)}", allow_blank=True)
                            worksheet.add_data_validation(dv_status)
                            dv_status.add(f'{status_col}2:{status_col}{max_row}')

                        # Response (Priority) Validation
                        resp_col = get_col_letter_map("Response")
                        if resp_col:
                            dv_resp = DataValidation(type="list", formula1=f"'DataValidation'!$B$1:$B${len(response_options)}", allow_blank=True)
                            worksheet.add_data_validation(dv_resp)
                            dv_resp.add(f'{resp_col}2:{resp_col}{max_row}')

                        # 2. Header Styling (Dark Grey Background, Yellow Bold Text)
                        header_fill = PatternFill(start_color="595959", end_color="595959", fill_type="solid") # Dark Grey
                        header_font = Font(color="FFFF00", bold=True, size=11, name='Calibri') # Yellow, Bold
                        
                        for cell in worksheet[1]:
                            cell.fill = header_fill
                            cell.font = header_font
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                        
                        # 3. AutoFilter
                        worksheet.auto_filter.ref = worksheet.dimensions
                        
                        # 4. Make Links Clickable (Website & Map)
                        # Helper to apply hyperlinks
                        link_font = Font(color="0563C1", underline="single")
                        
                        # Website Column
                        try:
                            web_idx = export_df.columns.get_loc("Website") + 1
                            web_col = get_column_letter(web_idx)
                            for row in range(2, max_row + 1):
                                cell = worksheet[f"{web_col}{row}"]
                                if cell.value and isinstance(cell.value, str) and (cell.value.startswith('http') or cell.value.startswith('www')):
                                    cell.hyperlink = cell.value
                                    cell.font = link_font
                        except: pass

                        # Google Maps Column
                        try:
                            map_idx = export_df.columns.get_loc("Map Link") + 1
                            map_col = get_column_letter(map_idx)
                            for row in range(2, max_row + 1):
                                cell = worksheet[f"{map_col}{row}"]
                                if cell.value:
                                    cell.hyperlink = cell.value
                                    cell.value = "View on Map"
                                    cell.font = link_font
                        except Exception as e:
                            print(f"DEBUG: Map Link formatting failed: {e}")
                        
                        # 5. Conditional Formatting with DXF (Differential Formatting)
                        # This ensures styles apply even if cells have default styles
                        from openpyxl.styles import PatternFill, Font, Color
                        from openpyxl.styles.differential import DifferentialStyle
                        from openpyxl.formatting.rule import Rule

                        def create_dxf_rule(col_letter, value, fill_hex, font_hex):
                            # Strip hash
                            bg_color = Color(rgb="FF" + fill_hex.lstrip('#')) 
                            font_color = Color(rgb="FF" + font_hex.lstrip('#'))
                            
                            dxf = DifferentialStyle(
                                font=Font(color=font_color), 
                                fill=PatternFill(start_color=bg_color, end_color=bg_color, fill_type='solid')
                            )
                            rule = Rule(type="expression", dxf=dxf, stopIfTrue=True)
                            # Formula: check if cell equals value (wrapped in quotes)
                            rule.formula = [f'${col_letter}2="{value}"'] 
                            return rule

                        # Status Colors
                        status_styles = {
                            "Interested": ("#DFF5E1", "#1B5E20"),
                            "Not picking": ("#F0F0F0", "#616161"),
                            "Asked to call later": ("#FFF8E1", "#8D6E00"),
                            "Meeting set": ("#E3F2FD", "#0D47A1"),
                            "Meeting Done": ("#E0F2F1", "#004D40"),
                            "Proposal sent": ("#F3E5F5", "#4A148C"),
                            "Follow-up scheduled": ("#FFE0B2", "#E65100"),
                            "Not interested": ("#FDECEA", "#B71C1C"),
                            "Closed - Won": ("#C8E6C9", "#1B5E20"),
                            "Closed - Lost": ("#ECEFF1", "#37474F"),
                            "Generated": ("#FFFFFF", "#000000")
                        }
                        # Response (Priority) Colors
                        response_styles = {
                            "HOT": ("#F25C54", "#FFFFFF"),
                            "WARM": ("#FFE5B4", "#5A3E00"),
                            "COLD": ("#E3F2FD", "#1E3A8A")
                        }

                        # Status Rules
                        if status_col:
                            ws_range = f'{status_col}2:{status_col}{max_row}'
                            for status_val, (bg, txt) in status_styles.items():
                                rule = create_dxf_rule(status_col, status_val, bg, txt)
                                worksheet.conditional_formatting.add(ws_range, rule)

                        # Response Rules
                        if resp_col:
                            ws_range_resp = f'{resp_col}2:{resp_col}{max_row}'
                            for resp_val, (bg, txt) in response_styles.items():
                                rule = create_dxf_rule(resp_col, resp_val, bg, txt)
                                worksheet.conditional_formatting.add(ws_range_resp, rule)

                        # 6. Auto-width columns adjustments
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except: pass
                            adjusted_width = (max_length + 2) * 1.05
                            worksheet.column_dimensions[column_letter].width = min(adjusted_width, 50)

                    st.download_button(
                        label="📥 Excel (Formatted)",
                        data=buffer.getvalue(),
                        file_name=f"{export_filename}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key='dl_xlsx_formatted_v1',
                        use_container_width=True
                    )

                with col_btn3:
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

                # Add explicit Save to History button
                if st.button("📂 Save to Scraped Leads History", use_container_width=True):
                    try:
                        csv_for_history = df_display_existing.to_csv(index=False)
                        # Use actual input values if available
                        ts = datetime.now().strftime("%d %b %H:%M")
                        
                        # Get values directly from the input widgets above if possible
                        # Since button is pressed, input widgets 'target_business' and 'target_location' from lines 3459/3460 are in scope
                        t_biz = target_business.strip() if target_business else "Search"
                        t_loc = target_location.strip() if target_location else "Location"
                        
                        # Format: Dentist_Gotri, Vadodara
                        q_name = f"{t_biz}_{t_loc}"
                        
                        # POST to backend
                        requests.post(
                            EXECUTIONS_API, 
                            json={
                                "query": t_biz, 
                                "location": t_loc, 
                                "name": q_name,
                                "leadsGenerated": len(df_display_existing),
                                "status": "Success",
                                "fileContent": csv_for_history
                            },
                            timeout=10
                        )
                        st.toast("✅ Saved to Scraped Leads History!")
                        time.sleep(1)
                    except Exception as h_err:
                        st.error(f"Save Error: {h_err}")
        except Exception as e:
            if "No columns to parse" not in str(e):
                st.info(f"Could not load previous results: {e}")

    if start_scrape:
        if not target_business or not target_location:
            st.error("Please provide both Business Type and Location.")
        else:
            search_query = f"{target_business} in {target_location}"
            
            # Persist params for autosave
            st.session_state['last_scrape_business'] = target_business
            st.session_state['last_scrape_location'] = target_location
            
            output_file = "scraped_results.csv"
            
            # Remove previous file if exists
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except: pass
            
            scraper_dir = os.path.join(os.getcwd(), "dental_scraper")
            # Output in root
            cmd = [
                sys.executable, "-m", "scrapy", "crawl", "dental_spider",
                "-a", f"search_query={search_query}",
                "-O", f"../{output_file}"
            ]
            
            # Status container placeholder
            status_container = st.empty()
            status_container.info("Initializing scraper...")
            
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
                
                # Monitor loop removed for background logic
                pass
                
                # Result processing logic removed
                st.session_state.scraper_process = process
                st.session_state.scraper_running = True
                st.rerun()
                        
            except Exception as e:
                st.error(f"Execution Error: {e}")

    # --- BACKGROUND MONITOR ---
    if st.session_state.scraper_running:
        status_container = st.empty()
        
        # Get Process
        process = st.session_state.get('scraper_process')

        # Robust check if process is actually running
        if process:
            # Poll status
            poll = process.poll()
            
            if poll is None:
                # --- RUNNING ---
                # Read progress
                progress_file = "scraper_progress.txt"
                count_info = "Starting..."
                current_query = "Initializing..."
                
                if os.path.exists(progress_file):
                    try:
                        with open(progress_file, "r") as f:
                            progress = f.read().strip()
                            parts = progress.split("|")
                            if len(parts) == 2:
                                count_info = parts[0]
                                current_query = parts[1]
                    except: pass
                
                # STYLE DISPATCHER FOR STATUS CARD
                if st.session_state.get("google_ui_mode", False):
                    # Google Material Style
                    s_bg = "#ffffff"
                    s_border = "1px solid #dadce0"
                    s_shadow = "0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)"
                    s_text_main = "#202124"
                    s_text_sub = "#5f6368"
                    s_icon_bg = "#e8f0fe"
                    s_rocket_filter = "grayscale(100%) brightness(0) sepia(100%) hue-rotate(190deg) saturate(1000%)" 
                    s_scale = "1.005"
                else:
                    # Stealth/Cyber Gradient Style
                    s_bg = "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)"
                    s_border = "1px solid rgba(255, 255, 255, 0.2)"
                    s_shadow = "0 8px 32px rgba(59, 130, 246, 0.3)"
                    s_text_main = "white"
                    s_text_sub = "rgba(255, 255, 255, 0.9)"
                    s_icon_bg = "rgba(255, 255, 255, 0.2)"
                    s_rocket_filter = "none"
                    s_scale = "1.02"

                status_container.markdown(f"""
                <div style="
                    background: {s_bg};
                    border-radius: 16px;
                    padding: 24px 32px;
                    margin: 20px 0;
                    box-shadow: {s_shadow};
                    border: {s_border};
                    animation: pulse 2s ease-in-out infinite;
                ">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div style="
                            width: 48px;
                            height: 48px;
                            background: {s_icon_bg};
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 24px;
                            animation: spin 2s linear infinite;
                            filter: {s_rocket_filter};
                        ">
                            🚀
                        </div>
                        <div style="flex: 1;">
                            <div style="
                                color: {s_text_main};
                                font-size: 18px;
                                font-weight: 700;
                                margin-bottom: 4px;
                                font-family: 'Product Sans', sans-serif;
                            ">
                                Agents Deployed! ({count_info})
                            </div>
                            <div style="
                                color: {s_text_sub};
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
                        0%, 100% {{ transform: scale(1); box-shadow: {s_shadow}; }}
                        50% {{ transform: scale({s_scale}); box-shadow: {s_shadow}; }}
                    }}
                    @keyframes spin {{
                        from {{ transform: rotate(0deg); }}
                        to {{ transform: rotate(360deg); }}
                    }}
                </style>
                """, unsafe_allow_html=True)

                if st.button("🛑 Stop Scraper"):
                    process.terminate()
                    st.session_state.scraper_running = False
                    st.rerun()

                time.sleep(1)
                st.rerun()
            
            else:
                # --- FINISHED ---
                st.session_state.scraper_running = False
                
                if poll == 0:
                    status_container.success("✅ Scraping Complete!")
                    st.balloons()
                    
                    output_file = "scraped_results.csv"
                    # --- POST PROCESSING LOGIC ---
                    if os.path.exists(output_file):
                        df_res = pd.DataFrame()
                        if os.stat(output_file).st_size == 0:
                             st.warning("⚠️ Scraper finished but no data was found. Please try a different location or business type.")
                        else:
                            try:
                                df_res = pd.read_csv(output_file)
                            except pd.errors.EmptyDataError:
                                st.warning("⚠️ Scraper finished but the results file was empty.")
                        
                        if not df_res.empty:
                            # Show Data
                            col_map = {
                                "clinic_name": "Business Name",
                                "phone_number": "Phone Number",
                                "address": "Address",
                                "website_url": "Website",
                                "email": "Email",
                                "place_url": "Map Link"
                            }
                            df_res.rename(columns=col_map, inplace=True)
                            
                            # Add CRM Columns
                            if "Status" not in df_res.columns: df_res["Status"] = "Generated"
                            if "Priority" not in df_res.columns: df_res["Priority"] = "WARM"
                            
                            st.dataframe(df_res, use_container_width=True)
                            
                            # Save to History (Automatic)
                            try:
                                csv_for_history = df_res.to_csv(index=False)
                                
                                # Use persisted params or fallback
                                s_bus = st.session_state.get('last_scrape_business', target_business)
                                s_loc = st.session_state.get('last_scrape_location', target_location)
                                
                                q_name = f"{s_bus} - {s_loc}"
                                
                                requests.post(
                                    EXECUTIONS_API, 
                                    json={
                                        "query": f"{s_bus} in {s_loc}", 
                                        "location": s_loc, 
                                        "name": q_name,
                                        "leadsGenerated": len(df_res), # Save TOTAL scraped, not just new
                                        "status": "Success",
                                        "fileContent": csv_for_history
                                    },
                                    timeout=10
                                )
                                st.success(f"✅ Auto-saved results to Scraped Leads History ({len(df_res)} records)")
                            except Exception as h_err:
                                st.error(f"Auto-save to History Failed: {h_err}")
                            except Exception as e:
                                st.error(f"Failed to connect to backend: {e}")
                                
                            if st.button("🗑️ Clear Results"):
                                st.rerun()

                    else:
                        status_container.error(f"❌ Scraper Failed with Exit Code {poll}")
                        # Capture Stderr (Robust)
                        try:
                            # We might have already consumed pipe? communicate() handles this.
                            _, stderr_out = process.communicate(timeout=5)
                            if stderr_out:
                                with st.expander("📝 View Error Logs (Click Here)", expanded=True):
                                    st.code(stderr_out, language="text")
                                
                                if "playwright" in stderr_out.lower() or "browser" in stderr_out.lower() or "executable" in stderr_out.lower():
                                    st.warning("💡 To Fix: In Dashboard, click 'Manage App' -> 'Reboot App' to install browsers.")
                        except Exception as e:
                             st.error(f"Could not retrieve error logs: {e}")
        else:
            st.session_state.scraper_running = False
            st.rerun()

# ================== LEAD GEN HISTORY ==================
# ================== SCRAPED LEADS (History + Editing) ==================
if "Scraped Leads" in page:
    st.markdown(f"""<h1 style='display: flex; align-items: center;'>{get_icon_html('chart.png', 65)} Lead Staging & Import</h1>""", unsafe_allow_html=True)
    st.markdown("Review, edit, and import your scraped leads before pushing them to the main CRM.")

    # 1. Fetch Summary List
    executions = fetch_data(EXECUTIONS_API)
    
    if not executions:
        st.info("No scraped data found.")
    else:
        df_hist = pd.DataFrame(executions)
        
        # Prepare minimal list
        if "name" not in df_hist.columns:
            df_hist["name"] = "Untitled"
        
        # Formatting
        try:
            df_hist["date_fmt"] = pd.to_datetime(df_hist["date"]).dt.strftime("%d %b %H:%M")
        except:
            df_hist["date_fmt"] = df_hist["date"]
            
        df_hist["label"] = df_hist.apply(lambda x: f"{x['name']} ({x['leadsGenerated']}) - {x['date_fmt']}", axis=1)
        
        # --- CONTROL BAR (Card Style) ---
        with st.container(border=True):
            c_sel, c_meta, c_ren = st.columns([0.4, 0.4, 0.2])
            
            with c_sel:
                # Selection handling
                if "selected_scrape_id" not in st.session_state:
                    st.session_state.selected_scrape_id = None
                    
                def_idx = 0
                if st.session_state.selected_scrape_id:
                    try:
                        match = df_hist[df_hist["id"] == st.session_state.selected_scrape_id]
                        if not match.empty:
                            def_idx = df_hist.index.get_loc(match.index[0])
                    except: pass
    
                sel_label = st.selectbox(
                    "Select Session",
                    options=df_hist["label"].tolist(),
                    index=def_idx,
                    key="scrape_selector_box",
                    label_visibility="collapsed"
                )
                
                # Find ID
                sel_row = df_hist[df_hist["label"] == sel_label].iloc[0]
                st.session_state.selected_scrape_id = sel_row["id"]
            
            with c_meta:
                # Clean metadata display
                st.markdown(f"**📅 Date:** {sel_row['date_fmt']} &nbsp;&nbsp;|&nbsp;&nbsp; **📍 Location:** {sel_row['location']}")
                
            with c_ren:
                with st.popover("Rename Session", use_container_width=True):
                    new_name = st.text_input("New Name", value=sel_row["name"])
                    if st.button("Save", type="primary"):
                         try:
                             requests.put(f"{EXECUTIONS_API}/{sel_row['id']}", json={"name": new_name})
                             st.toast("Renamed updated successfully")
                             time.sleep(0.5)
                             st.rerun()
                         except: pass

        st.divider()

        # REMOVE INDENTATION FOR EDITOR BLOCK
        with st.container():
            if st.session_state.selected_scrape_id:
                # FETCH FULL RECORD (with fileContent)
                try:
                    res_detail = requests.get(f"{EXECUTIONS_API}/{st.session_state.selected_scrape_id}")
                    if res_detail.status_code == 200:
                        full_data = res_detail.json()
                        csv_content = full_data.get("fileContent", "")
                        
                        if csv_content:
                            # Parse CSV string
                            from io import StringIO
                            df_file = pd.read_csv(StringIO(csv_content))
                            
                            # --- 1. STANDARDIZE COLUMNS TO MATCH CRM ---
                            col_map = {
                                "clinic_name": "Company Name",
                                "Business Name": "Company Name",
                                "phone_number": "Phone Number",
                                "address": "Address",
                                "email": "Email",
                                "website": "Website",
                                "Website": "Website",
                                "rating": "Rating",
                                "reviews": "Reviews",
                                "url": "Map", # Scraper usually dumps url here
                                "google_maps_url": "Map",
                                "place_url": "Map",
                                "Maps Link": "Map",  # Handle files exported with "Maps Link"
                                "Map Link": "Map"
                            }
                            df_file.rename(columns=col_map, inplace=True)
                            
                            # Ensure essential columns exist
                            desired_order = ["Company Name", "Phone Number", "Email", "Address", "Map", "Website", "Status", "Priority", "Notes"]
                            for col in desired_order:
                                if col not in df_file.columns:
                                    if col == "Status": df_file[col] = "Generated"
                                    elif col == "Priority": df_file[col] = "WARM"
                                    elif col == "Notes": df_file[col] = "" 
                                    else: df_file[col] = None
                            
                            # Reorder for UI
                            other_cols = [c for c in df_file.columns if c not in desired_order]
                            final_cols = desired_order + other_cols
                            df_file = df_file[final_cols]

                            # FORCE TEXT TYPES for editable columns
                            text_cols = ["Company Name", "Phone Number", "Email", "Address", "Notes", "Map", "Website"]
                            for t_c in text_cols:
                                if t_c in df_file.columns:
                                    df_file[t_c] = df_file[t_c].astype(str).replace("nan", "")
                                    df_file[t_c] = df_file[t_c].replace("None", "")
                                    
                                    # Fix Phone Number formatting (remove .0 decimals)
                                    if t_c == "Phone Number":
                                        df_file[t_c] = df_file[t_c].str.replace(r'\.0$', '', regex=True)

                            
                            # --- Header & Actions ---
                            h_col1, h_col2 = st.columns([3, 1])
                            h_col1.subheader(f"Editing: {full_data.get('name')}")
                            
                            with h_col2:
                                import io
                                from openpyxl.worksheet.datavalidation import DataValidation
                                from openpyxl.styles import PatternFill, Font, Color, Alignment
                                from openpyxl.styles.differential import DifferentialStyle
                                from openpyxl.formatting.rule import Rule
                                from openpyxl.utils import get_column_letter

                                if st.button("📥 Export to Excel", use_container_width=True, key=f"btn_export_staging_{st.session_state.selected_scrape_id}"):
                                    # Prepare Data
                                    export_staging = df_file.copy()
                                    
                                    # Create Excel
                                    buffer = io.BytesIO()
                                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                        export_staging.to_excel(writer, index=False, sheet_name='Leads')
                                        wb = writer.book
                                        ws = writer.sheets['Leads']
                                        
                                        # --- 1. SETUP DROPDOWNS (Data Validation) ---
                                        # Create hidden sheet for lists
                                        ref_sheet = wb.create_sheet("DataValidation")
                                        ref_sheet.sheet_state = 'hidden'
                                        
                                        status_options = ["Generated", "Interested", "Not picking", "Asked to call later", "Meeting set", "Meeting Done", "Proposal sent", "Follow-up scheduled", "Not interested", "Closed - Won", "Closed - Lost"]
                                        priority_options = ["HOT", "WARM", "COLD"]
                                        
                                        # Write options to hidden sheet
                                        for idx, val in enumerate(status_options, start=1):
                                            ref_sheet.cell(row=idx, column=1).value = val
                                        for idx, val in enumerate(priority_options, start=1):
                                            ref_sheet.cell(row=idx, column=2).value = val
                                            
                                        # Helper for max row
                                        max_row = len(export_staging) + 1
                                        
                                        # Apply Validation to Status Column
                                        if "Status" in export_staging.columns:
                                            s_idx = export_staging.columns.get_loc("Status") + 1
                                            s_let = get_column_letter(s_idx)
                                            dv_status = DataValidation(type="list", formula1=f"'DataValidation'!$A$1:$A${len(status_options)}", allow_blank=True)
                                            dv_status.error = 'Select valid status'
                                            ws.add_data_validation(dv_status)
                                            dv_status.add(f"{s_let}2:{s_let}{max_row}")

                                        # Apply Validation to Priority Column
                                        if "Priority" in export_staging.columns:
                                            p_idx = export_staging.columns.get_loc("Priority") + 1
                                            p_let = get_column_letter(p_idx)
                                            dv_prio = DataValidation(type="list", formula1=f"'DataValidation'!$B$1:$B${len(priority_options)}", allow_blank=True)
                                            dv_prio.error = 'Select valid priority'
                                            ws.add_data_validation(dv_prio)
                                            dv_prio.add(f"{p_let}2:{p_let}{max_row}")
                                        
                                        # --- 2. HEADER STYLING ---
                                        header_fill = PatternFill(start_color="595959", end_color="595959", fill_type="solid")
                                        header_font = Font(color="FFFF00", bold=True, size=11, name='Calibri')
                                        for cell in ws[1]:
                                            cell.fill = header_fill
                                            cell.font = header_font
                                            
                                        # 3. HYPERLINKS (Short text)
                                        link_font = Font(color="0563C1", underline="single")
                                        
                                        # Flexible Column Mapping
                                        # (Column Name in DF -> Link Label)
                                        link_map_targets = {
                                            "Map": "View on Map",
                                            "Map Link": "View on Map",
                                            "Google Maps Link": "View on Map",
                                            "Website": "Visit Website",
                                            "Place Url": "View on Map",
                                            "url": "View on Map"
                                        }

                                        for col_name in export_staging.columns:
                                            # Check if this column matches any target (case-insensitive)
                                            matched_label = None
                                            for target_key, label in link_map_targets.items():
                                                if col_name.strip().lower() == target_key.lower():
                                                    matched_label = label
                                                    break
                                            
                                            if matched_label:
                                                c_idx = export_staging.columns.get_loc(col_name) + 1
                                                c_let = get_column_letter(c_idx)
                                                for r in range(2, max_row + 1):
                                                    cell = ws[f"{c_let}{r}"]
                                                    val = cell.value
                                                    if val and isinstance(val, str) and len(val) > 5:
                                                        # Basic validity check
                                                        if val.startswith('http') or val.startswith('www') or 'google.com/maps' in val:
                                                            try:
                                                                cell.hyperlink = val
                                                                cell.value = matched_label
                                                                cell.font = link_font
                                                            except: pass

                                        # --- 4. CONDITIONAL FORMATTING (Colors) ---
                                        # Status Colors
                                        status_styles = {
                                            "Interested": ("#DFF5E1", "#1B5E20"),
                                            "Not picking": ("#F0F0F0", "#616161"),
                                            "Asked to call later": ("#FFF8E1", "#8D6E00"),
                                            "Meeting set": ("#E3F2FD", "#0D47A1"),
                                            "Meeting Done": ("#E0F2F1", "#004D40"),
                                            "Proposal sent": ("#F3E5F5", "#4A148C"),
                                            "Follow-up scheduled": ("#FFE0B2", "#E65100"),
                                            "Not interested": ("#FDECEA", "#B71C1C"),
                                            "Closed - Won": ("#C8E6C9", "#1B5E20"),
                                            "Closed - Lost": ("#ECEFF1", "#37474F"),
                                            "Generated": ("#FFFFFF", "#000000")
                                        }
                                        # Priority Colors
                                        prio_styles = {
                                            "HOT": ("#F25C54", "#FFFFFF"),
                                            "WARM": ("#FFE5B4", "#5A3E00"),
                                            "COLD": ("#E3F2FD", "#1E3A8A")
                                        }
                                        
                                        def apply_dxf(col_name, style_map):
                                            if col_name not in export_staging.columns: return
                                            c_idx = export_staging.columns.get_loc(col_name) + 1
                                            c_let = get_column_letter(c_idx)
                                            rng = f"{c_let}2:{c_let}{max_row}"
                                            
                                            for val, (bg, fg) in style_map.items():
                                                bg_c = Color(rgb="FF"+bg.lstrip('#'))
                                                fg_c = Color(rgb="FF"+fg.lstrip('#'))
                                                dxf = DifferentialStyle(font=Font(color=fg_c), fill=PatternFill(start_color=bg_c, end_color=bg_c, fill_type='solid'))
                                                rule = Rule(type="expression", dxf=dxf, stopIfTrue=True)
                                                rule.formula = [f'${c_let}2="{val}"']
                                                ws.conditional_formatting.add(rng, rule)
                                        
                                        apply_dxf("Status", status_styles)
                                        apply_dxf("Priority", prio_styles)
                                        
                                        # --- 5. AUTO WIDTH ---
                                        for col in ws.columns:
                                            try:
                                                max_len = 0
                                                col_let = col[0].column_letter
                                                for cell in col:
                                                    if cell.value: 
                                                        max_len = max(max_len, len(str(cell.value)))
                                                ws.column_dimensions[col_let].width = min(max_len + 2, 50)
                                            except: pass

                                    st.download_button(
                                        label="✅ Download Excel",
                                        data=buffer.getvalue(),
                                        file_name=f"{full_data.get('name')}_Export.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key=f"dl_staging_{st.session_state.selected_scrape_id}"
                                    )
                            
                            # --- 2. CRM-STYLE COLUMN CONFIG ---
                            # Using exact CRM styling where applicable
                            staging_config = {
                                "Company Name": st.column_config.TextColumn("Company Name", required=True, width="medium"),
                                "Phone Number": st.column_config.TextColumn("Phone Number", width="medium"),
                                "Email": st.column_config.TextColumn("Email", width="medium"),
                                "Address": st.column_config.TextColumn("Address", width="large"),
                                "Map": st.column_config.LinkColumn("Map", display_text="View on Map"),
                                "Website": st.column_config.LinkColumn("Website", display_text="Visit"),
                                "Status": st.column_config.SelectboxColumn("Status", options=["Generated", "Interested", "Not picking", "Asked to call later", "Meeting set", "Meeting Done", "Proposal sent", "Follow-up scheduled", "Not interested", "Closed - Won", "Closed - Lost"], default="Generated", required=True),
                                "Priority": st.column_config.SelectboxColumn("Priority", options=["HOT", "WARM", "COLD"], default="WARM", required=True),
                                "Notes": st.column_config.TextColumn("Notes", width="large"),
                                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                                "Reviews": st.column_config.NumberColumn("Reviews"),
                            }
                            
                            edited_df = st.data_editor(
                                df_file,
                                num_rows="dynamic",
                                use_container_width=True,
                                key=f"editor_{st.session_state.selected_scrape_id}",
                                height=600,
                                column_config=staging_config,
                                column_order=final_cols
                            )
                            
                            # AUTO-SAVE LOGIC
                            if not edited_df.equals(df_file):
                                new_csv = edited_df.to_csv(index=False)
                                try:
                                    # Optimistic update or silent save
                                    requests.put(
                                        f"{EXECUTIONS_API}/{st.session_state.selected_scrape_id}", 
                                        json={"fileContent": new_csv}
                                    )
                                    st.toast("✅ Changes saved automatically!", icon="💾")
                                except Exception as e:
                                    st.error(f"Auto-save failed: {e}")
                            
                            # Export Button
                            st.download_button(
                                "📥 Download as CSV",
                                edited_df.to_csv(index=False).encode('utf-8'),
                                f"{full_data.get('name').replace(' ', '_')}.csv",
                                "text/csv",
                                key=f"dl_{st.session_state.selected_scrape_id}",
                                use_container_width=True
                            )
                            

                        else:
                            st.warning("⚠️ This record has no CSV content attached.")
                    else:
                        st.error("Failed to load details.")
                except Exception as e:
                    st.error(f"Error loading data: {e}")
            else:
                st.info("👈 Select a scrape session from the left to view data.")
 
  