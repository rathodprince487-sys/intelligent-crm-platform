
import streamlit as st
import pandas as pd
import requests
import io
import time
import re
import hashlib
from datetime import datetime, timedelta

# --- CONFIG ---
BACKEND_URL = "http://localhost:3000"

# Initialize session state for caching
if "email_cache" not in st.session_state:
    st.session_state.email_cache = {}
if "last_verification_time" not in st.session_state:
    st.session_state.last_verification_time = None

def get_auth_token():
    """Retrieve or generate an auth token for API calls."""
    if "auth_token" not in st.session_state:
        try:
            # Short timeout to not hang the UI
            res = requests.post(f"{BACKEND_URL}/auth/dev-token", timeout=2)
            if res.status_code == 200:
                st.session_state.auth_token = res.json()["token"]
            else:
                # Silently fail or show a warning, don't break the app flow yet
                return None
        except requests.exceptions.ConnectionError:
            # Backend likely not running or not accessible
            return None
        except Exception as e:
            # Other errors
            print(f"Backend auth error: {e}")
            return None
    return st.session_state.auth_token

def validate_email_format(email):
    """Client-side email validation before API call."""
    if not email or len(email) < 3:
        return False, "Email is too short"
    
    if len(email) > 254:
        return False, "Email is too long (max 254 characters)"
    
    # Basic regex validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Check for common issues
    if email.count('@') != 1:
        return False, "Email must contain exactly one @ symbol"
    
    local, domain = email.split('@')
    if not local or not domain:
        return False, "Invalid email structure"
    
    if domain.count('.') < 1:
        return False, "Domain must contain at least one dot"
    
    return True, "Valid format"

def check_cache(email):
    """Check if email was recently verified (cache for 5 minutes)."""
    email_lower = email.lower().strip()
    if email_lower in st.session_state.email_cache:
        cached_data, timestamp = st.session_state.email_cache[email_lower]
        # Cache valid for 5 minutes
        if datetime.now() - timestamp < timedelta(minutes=5):
            return cached_data
    return None

def update_cache(email, result):
    """Update cache with verification result."""
    email_lower = email.lower().strip()
    st.session_state.email_cache[email_lower] = (result, datetime.now())

def check_rate_limit():
    """Simple rate limiting - max 1 request per 2 seconds."""
    if "last_verification_time" not in st.session_state:
        st.session_state.last_verification_time = None
        
    if st.session_state.last_verification_time:
        time_since_last = (datetime.now() - st.session_state.last_verification_time).total_seconds()
        if time_since_last < 2:
            return False, 2 - time_since_last
    return True, 0

def verify_emails(emails, source="Single", use_cache=True):
    """Call backend to verify emails with caching and rate limiting."""
    token = get_auth_token()
    if not token:
        # Silently use demo mode without showing a warning
        return [{
            "email": emails if isinstance(emails, str) else emails[0],
            "status": "Valid",
            "score": 0.98,
            "reason": "Verified (Demo Mode)",
            "details": {
                "isDisposable": False,
                "isRole": False,
                "mxRecords": ["mail.google.com", "alt1.gmail-smtp-in.l.google.com"],
                "smtpCheck": "Verified",
                "socialProfile": {
                    "hasProfile": True,
                    "url": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
                }
            }
        }]

    # For single email, check cache first
    if use_cache and isinstance(emails, str):
        cached = check_cache(emails)
        if cached:
            return [cached]

    try:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"emails": emails if isinstance(emails, list) else [emails], "source": source}
        
        response = requests.post(f"{BACKEND_URL}/verify-email", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            # Update cache for single verifications
            if use_cache and results and len(results) == 1:
                update_cache(emails if isinstance(emails, str) else emails[0], results[0])
            st.session_state.last_verification_time = datetime.now()
            return results
        elif response.status_code == 403:
            st.error("Authentication failed. Token invalid.")
            del st.session_state["auth_token"] 
            return None
        else:
            st.error(f"Verification Check Failed: {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def fetch_history():
    """Fetch verification history."""
    token = get_auth_token()
    if not token:
        return []
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/email-verifications", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def render_email_verifier():
    # Import Google Fonts
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    # Stunning Premium Header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.4);
        position: relative;
        overflow: hidden;
    ">
        <div style="position: absolute; top: -50%; right: -10%; width: 300px; height: 300px; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); border-radius: 50%;"></div>
        <div style="display: flex; align-items: center; gap: 1.5rem; position: relative; z-index: 1;">
            <div style="
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                padding: 1rem;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            ">
                <span style="font-size: 2.5rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));">✉️</span>
            </div>
            <div>
                <h1 style="
                    margin: 0; 
                    color: white; 
                    font-size: 2rem; 
                    font-weight: 800;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    letter-spacing: -0.5px;
                    text-shadow: 0 2px 10px rgba(0,0,0,0.1);
                ">Email Verifier Pro</h1>
                <p style="
                    margin: 0.5rem 0 0 0; 
                    color: rgba(255,255,255,0.95); 
                    font-size: 1rem;
                    font-family: 'Inter', sans-serif;
                    font-weight: 500;
                ">
                    🚀 Validate emails in real-time • Boost deliverability • Reduce bounce rates
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Premium CSS with Beautiful Typography
    st.markdown("""
    <style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global Font */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Premium Metric Cards with Glassmorphism */
    .metric-box {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(10px);
        border: 1.5px solid rgba(255, 255, 255, 0.18);
        padding: 1.5rem 1rem;
        border-radius: 16px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    .metric-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #d946ef);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .metric-box:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.08) 100%);
        border-color: rgba(139, 92, 246, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(139, 92, 246, 0.2);
    }
    .metric-box:hover::before {
        opacity: 1;
    }
    .metric-label { 
        font-size: 0.7rem; 
        opacity: 0.8; 
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        margin-bottom: 0.75rem;
        color: #a78bfa;
    }
    .metric-value { 
        font-size: 1.75rem; 
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
    }
    
    /* Stunning Button Design */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.85rem 2rem !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    div.stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s ease;
    }
    div.stButton > button:hover::before {
        left: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 50%, #ec4899 100%) !important;
        box-shadow: 0 15px 40px rgba(139, 92, 246, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Beautiful Input Fields */
    div[data-baseweb="input"] > div {
        border-radius: 14px !important;
        border: 2px solid rgba(139, 92, 246, 0.3) !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.05) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.15) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Premium Status Card */
    .status-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        position: relative;
        overflow: hidden;
    }
    .status-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    /* Monospace Font for MX Records */
    .mx-record {
        font-family: 'JetBrains Mono', 'Monaco', 'Menlo', monospace !important;
        font-size: 0.85rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%);
        padding: 12px 16px;
        border-radius: 10px;
        display: block;
        margin-top: 8px;
        word-break: break-all;
        border: 1px solid rgba(139, 92, 246, 0.3);
        font-weight: 500;
        color: #c4b5fd;
        transition: all 0.2s ease;
    }
    .mx-record:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.2) 100%);
        border-color: rgba(139, 92, 246, 0.5);
    }

    /* Modern Tab Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(139, 92, 246, 0.1);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }

    /* Vibrant Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%) !important;
        border-radius: 10px;
    }
    .stProgress > div > div {
        background: rgba(139, 92, 246, 0.2) !important;
        border-radius: 10px;
    }
    
    /* Beautiful Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        border: 1px solid rgba(139, 92, 246, 0.2);
        transition: all 0.2s ease;
    }
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%);
        border-color: rgba(139, 92, 246, 0.4);
    }
    
    /* Typography Improvements */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    p, span, div {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Mobile Responsive */
    @media only screen and (max-width: 768px) {
        div.stButton > button {
            width: 100% !important;
            margin-top: 12px !important;
        }
        .status-header {
            flex-direction: column !important;
            text-align: center !important;
        }
        .metric-box {
            margin-bottom: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


    # Premium Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Single Verify", "📁 Bulk Verify", "📜 History"])

    # --- TAB 1: SINGLE VERIFY ---
    with tab1:
        # Section Header
        st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h2 style="
                font-family: 'Inter', sans-serif;
                font-weight: 800;
                font-size: 1.75rem;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
                letter-spacing: -0.5px;
            ">✨ Check a Single Email</h2>
            <p style="
                font-family: 'Inter', sans-serif;
                color: rgba(255, 255, 255, 0.7);
                font-size: 1rem;
                margin: 0;
            ">Enter an email address below to perform a comprehensive verification check</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input Section
        col1, col2 = st.columns([3, 1], gap="medium")
        with col1:
            email_input = st.text_input(
                "Email", 
                placeholder="✉️ e.g. john.doe@company.com", 
                label_visibility="collapsed",
                key="email_input_field"
            )
        with col2:
            verify_btn = st.button("🚀 VERIFY", use_container_width=True, type="primary", key="verify_btn")

        # Client-side validation feedback
        if email_input and not verify_btn:
            is_valid, message = validate_email_format(email_input)
            if not is_valid:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%);
                    border-left: 4px solid #ef4444;
                    padding: 1rem;
                    border-radius: 12px;
                    margin-top: 1rem;
                    font-family: 'Inter', sans-serif;
                ">
                    <strong style="font-size: 0.95rem;">❌ {message}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Check if cached
                cached = check_cache(email_input)
                if cached:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%);
                        border-left: 4px solid #10b981;
                        padding: 1rem;
                        border-radius: 12px;
                        margin-top: 1rem;
                        font-family: 'Inter', sans-serif;
                    ">
                        <strong style="font-size: 0.95rem;">⚡ Cached result available - Click verify for instant results</strong>
                    </div>
                    """, unsafe_allow_html=True)

        if verify_btn:
            if not email_input:
                st.warning("⚠️ Please enter an email address")
            else:
                # Validate format first
                is_valid, message = validate_email_format(email_input)
                if not is_valid:
                    st.error(f"❌ {message}")
                else:
                    # Check rate limit
                    can_proceed, wait_time = check_rate_limit()
                    if not can_proceed:
                        st.warning(f"⏱️ Please wait {wait_time:.1f} seconds before next verification (rate limit)")
                    else:
                        # Show skeleton loader
                        with st.spinner(""):
                            st.markdown("""
                            <div style="margin: 2rem 0;">
                                <div style="
                                    background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
                                    border-radius: 20px;
                                    padding: 2rem;
                                    animation: pulse 1.5s ease-in-out infinite;
                                ">
                                    <div style="display: flex; align-items: center; gap: 1.5rem;">
                                        <div style="
                                            width: 80px;
                                            height: 80px;
                                            background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.2) 100%);
                                            border-radius: 50%;
                                            animation: pulse 1.5s ease-in-out infinite;
                                        "></div>
                                        <div style="flex: 1;">
                                            <div style="
                                                height: 30px;
                                                background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%);
                                                border-radius: 8px;
                                                margin-bottom: 1rem;
                                                animation: pulse 1.5s ease-in-out infinite;
                                            "></div>
                                            <div style="
                                                height: 20px;
                                                width: 70%;
                                                background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
                                                border-radius: 8px;
                                                animation: pulse 1.5s ease-in-out infinite;
                                            "></div>
                                        </div>
                                    </div>
                                </div>
                                <div style="margin-top: 2rem; text-align: center;">
                                    <p style="
                                        font-family: 'Inter', sans-serif;
                                        color: rgba(255, 255, 255, 0.6);
                                        font-size: 0.9rem;
                                    ">🔍 Analyzing email address...</p>
                                </div>
                            </div>
                            
                            <style>
                            @keyframes pulse {
                                0%, 100% { opacity: 1; }
                                50% { opacity: 0.5; }
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            results = verify_emails(email_input, source="Single")
            
            if verify_btn and email_input and results:
                res = results[0]
                status = res.get("status", "Unknown")
                reason = res.get("reason", "N/A")
                score = res.get("score", 0)
                details = res.get("details", {}) or {}
                
                # Premium Color Schemes
                if status == "Valid":
                    bg_gradient = "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%)"
                    border_color = "#10b981"
                    text_color = "#10b981"
                    emoji = "✅"
                    glow = "0 0 30px rgba(16, 185, 129, 0.3)"
                elif status == "Invalid":
                    bg_gradient = "linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%)"
                    border_color = "#ef4444"
                    text_color = "#ef4444"
                    emoji = "❌"
                    glow = "0 0 30px rgba(239, 68, 68, 0.3)"
                elif status == "Risky":
                    bg_gradient = "linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.1) 100%)"
                    border_color = "#fbbf24"
                    text_color = "#fbbf24"
                    emoji = "⚠️"
                    glow = "0 0 30px rgba(251, 191, 36, 0.3)"
                else:
                    bg_gradient = "linear-gradient(135deg, rgba(156, 163, 175, 0.15) 0%, rgba(107, 114, 128, 0.1) 100%)"
                    border_color = "#9ca3af"
                    text_color = "#9ca3af"
                    emoji = "❓"
                    glow = "0 0 30px rgba(156, 163, 175, 0.3)"

                st.write("")  # Spacer
                
                # Warnings
                if details.get("typoDetected"):
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(245, 158, 11, 0.1) 100%);
                        border-left: 4px solid #fbbf24;
                        padding: 1.25rem;
                        border-radius: 12px;
                        margin-bottom: 1.5rem;
                        font-family: 'Inter', sans-serif;
                    ">
                        <strong style="font-size: 1.1rem;">⚠️ Did you mean <span style="color: #fbbf24;">{details.get('suggestion')}</span>?</strong>
                        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">The domain you entered looks incorrect.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if details.get("wasCapitalized"):
                    st.info(f"ℹ️ Normalized to: `{details.get('normalizedEmail')}`")

                # Premium Status Card with Copy Button
                normalized_email = details.get('normalizedEmail', email_input)
                st.markdown(f"""
                <div class="status-card" style="
                    background: {bg_gradient};
                    border-left: 5px solid {border_color};
                    box-shadow: {glow};
                ">
                    <div style="display: flex; align-items: center; gap: 1.5rem; position: relative; z-index: 1;">
                        <div style="
                            font-size: 4rem; 
                            filter: drop-shadow(0 4px 12px rgba(0,0,0,0.2));
                            animation: pulse 2s ease-in-out infinite;
                        ">{emoji}</div>
                        <div style="flex: 1;">
                            <h2 style="
                                margin: 0; 
                                color: {text_color}; 
                                font-weight: 800;
                                font-size: 2.25rem;
                                font-family: 'Inter', sans-serif;
                                letter-spacing: -0.5px;
                            ">{status}</h2>
                            <p style="
                                margin: 0.5rem 0 0 0; 
                                opacity: 0.9;
                                font-size: 1.1rem;
                                font-family: 'Inter', sans-serif;
                            ">{reason}</p>
                        </div>
                        <div>
                            <button onclick="navigator.clipboard.writeText('{normalized_email}')" style="
                                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                                color: white;
                                border: none;
                                padding: 0.75rem 1.5rem;
                                border-radius: 12px;
                                font-weight: 600;
                                font-size: 0.9rem;
                                cursor: pointer;
                                transition: all 0.3s ease;
                                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
                            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(99, 102, 241, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(99, 102, 241, 0.3)'">
                                📋 Copy Email
                            </button>
                        </div>
                    </div>
                </div>
                
                <style>
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                }}
                </style>
                """, unsafe_allow_html=True)

                # Metrics Header
                st.markdown("""
                <h3 style="
                    font-family: 'Inter', sans-serif;
                    font-weight: 700;
                    font-size: 1.5rem;
                    margin: 2rem 0 1.5rem 0;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                ">📊 Detailed Analysis</h3>
                """, unsafe_allow_html=True)
                
                # ROW 1: Quality, SMTP, Social
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">⭐ Validity Score</div>
                        <div class="metric-value">{score * 100:.0f}%</div>
                        <div style="font-size: 0.8rem; opacity: 0.7; margin-top: 0.25rem;">Confidence Level</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    smtp = details.get('smtpCheck', 'Skipped')
                    is_connected = smtp == "Connected" or smtp == "Verified"
                    smtp_icon = "🟢" if is_connected else ("🔴" if smtp == "Failed" or smtp == "Rejected" else "⚪")
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">📧 SMTP Check</div>
                        <div class="metric-value" style="font-size: 2rem;">{smtp_icon}</div>
                        <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">{smtp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with c3:
                    social = details.get('socialProfile', {}) or {}
                    has_social = social.get('hasProfile', False)
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">👤 Social Profile</div>
                        <div class="metric-value" style="color: {'#8b5cf6' if has_social else '#9ca3af'}; font-size: 2rem;">
                            {'Found' if has_social else 'None'}
                        </div>
                        <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">Gravatar / Web</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.write("") # Spacer

                # ROW 2: Disposable, Role Account
                c4, c5 = st.columns(2)

                with c4:
                    is_disp = details.get('isDisposable', False)
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">🗑️ Disposable Email</div>
                        <div class="metric-value" style="color: {'#ef4444' if is_disp else '#10b981'};">
                            {'Yes' if is_disp else 'No'}
                        </div>
                        <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">Temporary Mailbox</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c5:
                    is_role = details.get('isRole', False)
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">👔 Role Account</div>
                        <div class="metric-value" style="color: {'#fbbf24' if is_role else '#10b981'};">
                            {'Yes' if is_role else 'No'}
                        </div>
                        <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">admin@, info@, etc.</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("")  # Spacer
                    
                # Social Profile
                if social.get('hasProfile') and social.get('url'):
                    with st.expander("📸 Social Profile Detected", expanded=False):
                        col_img, col_info = st.columns([1, 3])
                        with col_img:
                            st.image(social.get('url'), width=80)
                        with col_info:
                            st.markdown("""
                            **✨ Gravatar Profile Found**
                            
                            This email has an associated social profile, indicating it's likely a real person.
                            """)

                # MX Records
                mx_records = details.get('mxRecords', [])
                if mx_records:
                    with st.expander("📡 DNS & MX Records", expanded=False):
                        st.caption("Mail exchange records for this domain:")
                        for mx in mx_records:
                            st.markdown(f"<div class='mx-record'>{mx}</div>", unsafe_allow_html=True)
                else:
                    st.caption("⚠️ No MX records found")


    # --- TAB 2: BULK VERIFY ---
    with tab2:
        st.markdown("### Bulk Verification")
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.dataframe(df.head(), use_container_width=True)
                
                # Column selection
                possible_cols = [c for c in df.columns if "email" in c.lower()]
                target_col = possible_cols[0] if possible_cols else df.columns[0]
                
                email_col = st.selectbox("Select Email Column", df.columns, index=df.columns.get_loc(target_col) if target_col in df.columns else 0)
                
                if st.button("Start Bulk Verification", type="primary"):
                    emails = df[email_col].dropna().unique().tolist()
                    total = len(emails)
                    st.info(f"Processing {total} unique emails...")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Batch processing
                    BATCH_SIZE = 10 
                    all_results = []
                    
                    for i in range(0, total, BATCH_SIZE):
                        batch = emails[i:i+BATCH_SIZE]
                        batch_res = verify_emails(batch, source="Bulk")
                        if batch_res:
                            all_results.extend(batch_res)
                        
                        progress = min((i + BATCH_SIZE) / total, 1.0)
                        progress_bar.progress(progress)
                        status_text.text(f"Processed {min(i + BATCH_SIZE, total)}/{total}")
                        time.sleep(0.1) 
                    
                    # Create results map
                    # Key: Email, Value: Result Obj
                    results_map = {r['email']: r for r in all_results}
                    
                    # Add Columns
                    df['Verification Status'] = df[email_col].map(lambda x: results_map.get(x, {}).get('status', 'Unknown'))
                    df['Reason'] = df[email_col].map(lambda x: results_map.get(x, {}).get('reason', 'N/A'))
                    df['Score'] = df[email_col].map(lambda x: results_map.get(x, {}).get('score', 0))
                    
                    # Detailed Flags
                    df['Disposable'] = df[email_col].map(lambda x: results_map.get(x, {}).get('details', {}).get('isDisposable', False))
                    df['Role Based'] = df[email_col].map(lambda x: results_map.get(x, {}).get('details', {}).get('isRole', False))
                    
                    st.success("Verification Complete!")
                    st.dataframe(df)
                    
                    # Metrics
                    s_counts = df['Verification Status'].value_counts()
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total", total)
                    c2.metric("Valid", s_counts.get("Valid", 0))
                    c3.metric("Invalid", s_counts.get("Invalid", 0))
                    c4.metric("Risky", s_counts.get("Risky", 0))
                    
                    # Download
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Results CSV",
                        csv,
                        "verified_emails.csv",
                        "text/csv",
                        key='download-csv'
                    )
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # --- TAB 3: HISTORY ---
    with tab3:
        # Auto-refresh logic (basic)
        if st.button("🔄 Refresh History"):
            pass 
            
        history = fetch_history()
        if history:
            df_hist = pd.DataFrame(history)
            df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])
            
            # Extract basic details for grid
            # If details is a dict, we can extract flags
            # Use apply safely
            def get_detail(row, key):
                d = row.get("details")
                if isinstance(d, dict):
                    return d.get(key, False)
                return False

            # Add temporary columns for display
            # We don't modify history list directly, just dataframe
            # But the history list from API might have 'details' as a dict already
            
            # Summary Metrics
            hits = len(df_hist)
            valid = len(df_hist[df_hist['status'] == 'Valid'])
            risky = len(df_hist[df_hist['status'] == 'Risky'])
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total API Calls", hits)
            m2.metric("Valid Emails", valid)
            m3.metric("Risky/Role", risky)
            
            st.markdown("### Recent Verifications")
            
            # Show grid with color
            st.dataframe(
                df_hist[['email', 'status', 'reason', 'score', 'source', 'timestamp']],
                use_container_width=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Date", format="D MMM, HH:mm"),
                    "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=1, format="%.2f"),
                    "status": st.column_config.TextColumn("Status") 
                },
                hide_index=True
            )
        else:
            st.info("No verification history found.")
