import re
import sys

file_path = "components/email_verifier.py"

with open(file_path, "r") as f:
    content = f.read()

# 1. Replace the CSS block
old_css_regex = r"<style>.*?</style>"
new_css = """<style>
    /* Websites Showcase Style Theme for Email Verifier */

    @font-face {
        font-family: 'Inter';
        src: url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    }

    /* --- HERO HEADER --- */
    .hero-container {
        font-family: 'Inter', sans-serif;
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 40px;
        border-radius: 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.8);
        display: flex;
        align-items: center;
        gap: 24px;
        color: #000;
    }

    .hero-icon {
        background: rgba(0, 0, 0, 0.05);
        color: #000;
        width: 72px;
        height: 72px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        box-shadow: inset 0 2px 10px rgba(255,255,255,1);
    }

    /* --- CARDS & CONTAINERS --- */
    .verifier-card {
        font-family: 'Inter', sans-serif;
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 30px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.04);
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        margin-bottom: 24px;
        color: #000;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    /* Hover Effect for Cards */
    .verifier-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
        border-color: rgba(255, 255, 255, 1) !important;
    }

    /* --- RESULTS CARD COLORING --- */
    .result-valid { border: 2px solid rgba(52, 168, 83, 0.3) !important; }
    .result-risky { border: 2px solid rgba(251, 188, 5, 0.3) !important; }
    .result-invalid { border: 2px solid rgba(234, 67, 53, 0.3) !important; }

    /* --- METRIC BOXES --- */
    .metric-grid-box {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.9);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #666;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 18px;
        font-weight: 700;
        color: #000;
    }
    .metric-sub {
        font-size: 12px;
        color: #888;
        margin-top: 6px;
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(0,0,0,0.03);
        padding: 6px;
        border-radius: 30px;
        border-bottom: none;
        margin-bottom: 30px;
        display: inline-flex;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        font-weight: 600;
        color: #666;
        border: none;
        border-radius: 24px;
        background: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #000 !important;
        background: #fff !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: none !important;
    }
    
    /* Hide Streamlit tab selection border */
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
        background-color: transparent !important;
    }
    
    /* --- INPUTS AND BUTTONS --- */
    input[type="text"] {
        border-radius: 20px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        background: rgba(255,255,255,0.8) !important;
        padding: 14px 20px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    button {
        border-radius: 20px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: bold !important;
    }
    
    /* --- DATAFRAME / TABLE --- */
    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        border: none;
        box-shadow: 0 5px 20px rgba(0,0,0,0.03);
        background: rgba(255,255,255,0.6);
        overflow: hidden;
    }
    
    /* Hiding Streamlit Branding where possible */
    footer {visibility: hidden;}
    </style>"""

content = re.sub(old_css_regex, new_css, content, flags=re.DOTALL)

with open(file_path, "w") as f:
    f.write(content)
