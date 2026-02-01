import streamlit as st
import base64

def render_sidebar_toggle():
    """
    Renders the CSS and JavaScript necessary for the collapsible sidebar.
    This should be called at the top of the app, preferably before other sidebar content.
    """
    
    # CSS for the collapsible sidebar
    st.markdown("""
    <style>
    /* === COLLAPSIBLE SIDEBAR CSS (Desktop Only) === */
    
    /* Hide the custom toggle on mobile - rely on Streamlit's native one */
    @media (max-width: 767.98px) {
        #sidebar-custom-toggle {
            display: none !important;
        }
    }

    /* Wrap ALL custom collapse logic in Desktop Media Query */
    @media (min-width: 768px) {
        
        /* Transition for smooth width change */
        /* Transition for smooth width change */
        section[data-testid="stSidebar"] {
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.5s cubic-bezier(0.4, 0, 0.2, 1), max-width 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
            overflow-x: hidden !important;
        }
        
        /* Force Expanded Width */
        body:not(.sidebar-mj-collapsed) section[data-testid="stSidebar"] {
            width: 260px !important;
            min-width: 260px !important;
        }
        
        /* Prevent text wrapping in navigation */
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: clip !important;
            transition: opacity 0.3s ease, transform 0.3s ease, width 0.3s ease;
            transform-origin: left center;
        }
    
        /* Toggle Button Style (Desktop) */
        #sidebar-custom-toggle {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 999999;
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 1.5rem;
            color: #555;
            padding: 5px;
            border-radius: 5px;
            transition: color 0.2s, left 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            display: block;
        }
        #sidebar-custom-toggle:hover {
            color: #000;
            background: rgba(0,0,0,0.05);
        }
    
        /* COLLAPSED STATE STYLES */
        
        /* 1. Shrink Sidebar Width */
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] {
            width: 70px !important;
            min-width: 70px !important;
            max-width: 70px !important;
        }
    
        /* 2. Hide Texts in Radio Buttons (Navigation) */
        /* 2. Hide Texts with Fade */
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            opacity: 0 !important;
            transform: scaleX(0) translateX(-10px);
            width: 0 !important;
            margin: 0 !important;
        }
        
        /* 3. Center Icons in Radio Buttons */
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label {
            padding-left: 0 !important;
            padding-right: 0 !important;
            justify-content: center !important;
            text-align: center !important;
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
            margin-right: 0 !important;
        }
    
        /* 4. Hide other elements */
        div[data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] h1,
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] h2,
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] h3,
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .mc-details,
        body.sidebar-mj-collapsed [data-testid="stLogo"],
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] img {
            display: none !important;
        }
    
        /* === SETTINGS BUTTONS TRANSFORM === */
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .stButton button p,
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .stButton button div p {
            font-size: 0 !important;
            visibility: visible !important;
            line-height: 0 !important;
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .stButton button p::first-letter,
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .stButton button div p::first-letter {
            font-size: 1.25rem !important;
            line-height: normal !important;
            visibility: visible !important;
            display: inline-block !important;
        }
    
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .stButton button {
            width: 36px !important;
            height: 36px !important;
            padding: 0 !important;
            min-width: unset !important;
            border-radius: 6px !important; 
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 1px solid rgba(128,128,128, 0.2) !important;
            background-color: transparent !important;
            margin-left: -3px !important; 
            margin-right: auto !important;
            transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), background-color 0.2s ease !important;
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .stButton button:has(p:contains("🌱")) p::first-letter,
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .stButton button:has(div p:contains("🌱")) div p::first-letter {
            font-size: 1.1rem !important;
            margin-left: 1px !important;
        }
    
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .stButton button:hover {
            background-color: rgba(128,128,128, 0.1) !important;
            transform: scale(1.08) !important;
        }
    
        /* === MEETING CARDS TRANSFORM === */
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .meeting-card {
            width: 36px !important;
            height: 36px !important;
            padding: 0 !important;
            min-height: unset !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            margin: 8px 0 8px -3px !important;
            transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .meeting-card:hover {
            transform: scale(1.08);
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .mc-date-box {
            display: flex !important;
            flex-direction: column !important;
            width: 36px !important;
            height: 36px !important;
            min-width: 36px !important;
            max-width: 36px !important;
            border: 1px solid rgba(128,128,128, 0.2) !important;
            border-radius: 6px !important;
            background: #ffffff !important; 
            align-items: stretch !important;
            justify-content: flex-start !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
            box-sizing: border-box !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .mc-month {
            font-size: 0.5rem !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 2px 0 1px 0 !important;
            text-transform: uppercase;
            color: white !important;
            background-color: #FF4B4B !important;
            text-align: center !important;
            width: 100% !important;
            letter-spacing: 0.5px;
            display: block !important;
            height: auto !important;
            font-weight: 600 !important;
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .mc-day {
            font-size: 1.0rem !important;
            line-height: normal !important;
            font-weight: 700 !important;
            color: #333333 !important; 
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: 100% !important;
            flex-grow: 1 !important;
            padding-bottom: 2px !important; 
        }
    
        /* === NO MEETINGS TEXT === */
        
        .no-meetings-text {
            color: rgba(49, 51, 63, 0.6);
            font-size: 0.85rem;
            margin-bottom: 0.5rem;
            white-space: nowrap;
        }

        /* Collapsed State for No Meetings */
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .no-meetings-text {
            font-size: 0 !important;
            color: transparent !important;
            margin: 0 !important;
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
        }
        
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] .no-meetings-text::after {
            content: "none";
            font-size: 0.8rem !important;
            color: rgba(49, 51, 63, 0.6) !important;
            visibility: visible !important;
            display: block !important;
            text-align: center !important;
            width: 100% !important;
            margin-left: -5px; /* Visual centering adjustment for shrunk sidebar */
        }

        /* Adjust Toggle Button Position when collapsed */
        body.sidebar-mj-collapsed #sidebar-custom-toggle {
            left: 18px; 
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # JavaScript to handle the toggle
    # We inject a button into the DOM and attach a click listener
    js_code = """
    <script>
    function setupSidebarToggle() {
        const toggleId = 'sidebar-custom-toggle';
        let toggleBtn = parent.document.getElementById(toggleId);
        
        if (!toggleBtn) {
            // Create the button
            toggleBtn = parent.document.createElement('button');
            toggleBtn.id = toggleId;
            toggleBtn.innerHTML = '☰'; // Hamburger icon
            toggleBtn.title = "Toggle Sidebar";
            
            // Insert it into the header or sidebar area
            // We'll put it in the main parent container so it stays fixed
            parent.document.body.appendChild(toggleBtn);
            
            // Toggle Logic
            toggleBtn.onclick = function() {
                parent.document.body.classList.toggle('sidebar-mj-collapsed');
                
                // Optional: Save state to localStorage to persist across reloads
                const isCollapsed = parent.document.body.classList.contains('sidebar-mj-collapsed');
                parent.localStorage.setItem('sidebar_collapsed', isCollapsed);
            };
            
            // Restore state on load
            const savedState = parent.localStorage.getItem('sidebar_collapsed');
            if (savedState === 'true') {
                parent.document.body.classList.add('sidebar-mj-collapsed');
            }
        }
    }
    
    // Run setup
    setupSidebarToggle();
    // Re-run on potential re-renders (Streamlit quirk mitigation)
    setTimeout(setupSidebarToggle, 1000);
    </script>
    """
    import streamlit.components.v1 as components
    components.html(js_code, height=0, width=0)

