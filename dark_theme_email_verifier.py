import re

file_path = "components/email_verifier.py"

with open(file_path, "r") as f:
    content = f.read()

# 1. Replace the CSS block
old_css = """    <style>
    /* Clean Material Design for Email Verifier */

    /* --- HERO HEADER --- */
    .hero-container {
        background: #ffffff;
        padding: 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        border-top: 3px solid #1a73e8;
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .hero-icon {
        background: #e8f0fe;
        color: #1a73e8;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
    }

    /* --- CARDS & CONTAINERS --- */
    .verifier-card {
        background-color: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        margin-bottom: 24px;
    }
    
    /* Hover Effect for Cards */
    .verifier-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
        transition: all 0.3s ease;
    }

    /* --- RESULTS CARD COLORING --- */
    .result-valid { border-left: 6px solid #34a853; }
    .result-risky { border-left: 6px solid #fbbc05; }
    .result-invalid { border-left: 6px solid #ea4335; }

    /* --- METRIC BOXES --- */
    .metric-grid-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        border: 1px solid #e0e0e0;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #5f6368;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 16px;
        font-weight: 600;
        color: #202124;
    }
    .metric-sub {
        font-size: 11px;
        color: #80868b;
        margin-top: 4px;
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 4px;
        font-weight: 500;
        color: #5f6368;
        border: none;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #1a73e8 !important;
        border-bottom: 3px solid #1a73e8 !important;
    }
    
    /* --- DATAFRAME / TABLE --- */
    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* Hiding Streamlit Branding where possible */
    footer {visibility: hidden;}
    </style>"""

new_css = """    <style>
    /* Midnight Professional Theme for Email Verifier */

    /* --- HERO HEADER --- */
    .hero-container {
        background: rgba(20, 22, 26, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 8px 32px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.05);
        border-top: 3px solid #00f0ff;
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .hero-icon {
        background: rgba(0, 240, 255, 0.1);
        color: #00f0ff;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        border: 1px solid rgba(0, 240, 255, 0.2);
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    }

    /* --- CARDS & CONTAINERS --- */
    .verifier-card {
        background: rgba(20, 22, 26, 0.6) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 24px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 8px 32px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 24px;
        color: #e2e8f0;
    }
    
    /* Hover Effect for Cards */
    .verifier-card:hover {
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 12px 40px rgba(0,240,255,0.1);
        border-color: rgba(0,240,255,0.3);
        transition: all 0.3s ease;
    }

    /* --- RESULTS CARD COLORING --- */
    .result-valid { border-left: 6px solid #10b981 !important; }
    .result-risky { border-left: 6px solid #f59e0b !important; }
    .result-invalid { border-left: 6px solid #ef4444 !important; }

    /* --- METRIC BOXES --- */
    .metric-grid-box {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 16px;
        font-weight: 600;
        color: #f8fafc;
    }
    .metric-sub {
        font-size: 11px;
        color: #64748b;
        margin-top: 4px;
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 4px;
        font-weight: 500;
        color: #94a3b8;
        border: none;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom: 3px solid #00f0ff !important;
        text-shadow: 0 0 10px rgba(0,240,255,0.3);
    }
    
    /* --- DATAFRAME / TABLE --- */
    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Hiding Streamlit Branding where possible */
    footer {visibility: hidden;}
    </style>"""

content = content.replace(old_css, new_css)

# 2. Text Colors & Inline Backgrounds
replacements = [
    # Hero container text
    ('color: #202124;', 'color: #f8fafc;'),
    ('color: #5f6368;', 'color: #94a3b8;'),
    
    # Result cards Top Section
    ('background: white;', 'background: transparent;'),
    ('background: #f8fafc;', 'background: rgba(0,0,0,0.1);'),
    ('background: #ffffff;', 'background: transparent;'),
    
    ('color: #334155;', 'color: #e2e8f0;'),
    ('color: #64748b;', 'color: #94a3b8;'),
    ('color: #1e293b;', 'color: #f8fafc;'),
    ('color: #0f172a;', 'color: #f8fafc;'),
    ('color: #475569;', 'color: #e2e8f0;'),
    
    # Borders
    ('border-top: 1px solid #e2e8f0;', 'border-top: 1px solid rgba(255,255,255,0.05);'),
    ('border: 1px solid #e2e8f0;', 'border: 1px solid rgba(255,255,255,0.05);'),
    ('border: 1.5px solid #e2e8f0;', 'border: 1.5px solid rgba(255,255,255,0.05);'),
    ('border: 1px solid #cbd5e1;', 'border: 1px solid rgba(255,255,255,0.05);'),
    ('border: 1px dashed #cbd5e1;', 'border: 1px dashed rgba(255,255,255,0.2);'),
    
    # Bulk Upload icons/backgrounds
    ('background: #f1f5f9;', 'background: rgba(255,255,255,0.05);'),
]

for old, new in replacements:
    content = content.replace(old, new)


# Specifically format Dark themes for the Valid/Risky/Invalid bg_theme colors inside verify_emails:
# In the Python code the colors are set dynamically for inline styles. Let's make sure the inline backgrounds are darkened.

darken_theme_colors = [
    ('#e6f4ea', 'rgba(16, 185, 129, 0.1)'),
    ('#fef7e0', 'rgba(245, 158, 11, 0.1)'),
    ('#fce8e6', 'rgba(239, 68, 68, 0.1)'),
    
    # Digital Presence Detail Colors
    ('#d1fae5', 'rgba(16, 185, 129, 0.2)'),
    ('#065f46', '#34d399'), # Badge dark green text to bright green
    ('#10b98110', 'rgba(16, 185, 129, 0.15)'),
    ('#10b98105', 'rgba(16, 185, 129, 0.05)'),
    
    ('#fef3c7', 'rgba(245, 158, 11, 0.2)'),
    ('#92400e', '#fbbf24'),
    ('#f59e0b10', 'rgba(245, 158, 11, 0.15)'),
    ('#f59e0b05', 'rgba(245, 158, 11, 0.05)'),
    
    ('#f3f4f6', 'rgba(255, 255, 255, 0.05)'),
    ('#374151', '#e2e8f0'),
    ('#6b728010', 'rgba(255, 255, 255, 0.1)'),
    ('#6b728005', 'rgba(255, 255, 255, 0.02)'),
    
    # URL cards
    ('linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', 'linear-gradient(135deg, rgba(2, 132, 199, 0.15) 0%, rgba(2, 132, 199, 0.05) 100%)'),
    ('color: #0c4a6e;', 'color: #38bdf8;'),
    ('color: #0284c7;', 'color: #7dd3fc;'),
    
    ('linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)', 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%)'),
    # Note #065f46 already replaced above, we might need a specific one
    
    ('linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)', 'linear-gradient(135deg, rgba(147, 51, 234, 0.15) 0%, rgba(147, 51, 234, 0.05) 100%)'),
    ('color: #581c87;', 'color: #c084fc;'),
    ('color: #9333ea;', 'color: #d8b4fe;'),
    
    ('linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)', 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%)'),
]

for old, new in darken_theme_colors:
    content = content.replace(old, new)


with open(file_path, "w") as f:
    f.write(content)

print("Theme successfully updated!")
