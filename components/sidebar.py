
import streamlit as st
import base64

def render_sidebar_toggle():
    """Renders the CSS and JavaScript necessary for the collapsible sidebar."""
    sidebar_css = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
<style>
:root {
    --sidebar-width-expanded: 240px;
    --sidebar-width-collapsed: 64px;
    --primary-color: #577bf9;
    --text-color: #2E2E2E;
    --bg-color: #FFFFFF;
    --hover-bg: #F3F4F6;
    --border-color: #EAEAEA;
}
section[data-testid="stSidebar"] {
    background-color: var(--bg-color) !important;
    border-right: 1px solid var(--border-color) !important;
    transition: width 0.25s ease, min-width 0.25s ease, max-width 0.25s ease !important;
    width: var(--sidebar-width-expanded) !important;
    min-width: var(--sidebar-width-expanded) !important;
    overflow-x: hidden !important;
    padding-top: 0 !important;
    transform: none !important;
    margin-left: 0 !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1rem !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px !important;
    margin-top: 20px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: transparent !important;
    border: none !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    margin-bottom: 4px !important;
    margin-right: 10px !important;
    transition: all 0.2s ease !important;
    height: 40px !important;
    display: flex !important;
    align-items: center !important;
    position: relative !important;
    cursor: pointer !important;
    overflow: visible !important; 
}
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: var(--text-color) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    margin: 0 0 0 35px !important;
    white-space: nowrap !important;
    opacity: 1;
    transition: opacity 0.15s ease !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
    font-family: "Font Awesome 6 Free" !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    color: var(--text-color) !important;
    position: absolute !important;
    left: 14px !important;
    width: 20px !important;
    text-align: center !important;
    transition: color 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: var(--hover-bg) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover p {
    color: var(--primary-color) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before {
    color: var(--primary-color) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background-color: #EFF6FF !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p {
    color: var(--primary-color) !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]::before {
    color: var(--primary-color) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]::after {
    content: "";
    position: absolute;
    left: 0;
    top: 6px;
    bottom: 6px;
    width: 3px;
    background-color: var(--primary-color);
    border-radius: 0 4px 4px 0;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] {
    width: var(--sidebar-width-collapsed) !important;
    min-width: var(--sidebar-width-collapsed) !important;
    max-width: var(--sidebar-width-collapsed) !important;
    transform: none !important;
    margin-left: 0 !important;
    overflow-x: hidden !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] * {
    overflow: hidden !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] button {
    width: 44px !important;
    min-width: 44px !important;
    max-width: 44px !important;
    padding: 8px !important;
    margin: 0 auto 8px auto !important;
    overflow: hidden !important;
    white-space: nowrap !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] button * {
    display: none !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] button svg {
    display: block !important;
    margin: 0 auto !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    opacity: 0 !important;
    width: 0 !important;
    margin: 0 !important;
    display: none !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 0 !important;
    justify-content: center !important;
    width: 44px !important;
    margin: 0 auto 4px auto !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
    left: 50% !important;
    transform: translateX(-50%) !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]::after {
    display: none !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background-color: #EFF6FF !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label:hover::after {
    position: fixed;
    left: 70px;
    background-color: #1F2937;
    color: white;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
    z-index: 999999;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    pointer-events: none;
    display: block !important;
    width: auto !important;
    height: auto !important;
    top: auto !important;
    bottom: auto !important;
}
body.sidebar-mj-collapsed .sidebar-profile-details {
    display: none !important;
}
body.sidebar-mj-collapsed .sidebar-profile-container {
    padding: 10px 0 !important;
    justify-content: center !important;
    gap: 0 !important;
}
body.sidebar-mj-collapsed .sidebar-avatar {
    margin: 0 !important;
    width: 32px !important;
    height: 32px !important;
    font-size: 14px !important;
}
body.sidebar-mj-collapsed [data-testid="stLogo"] {
    display: none !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] button[data-testid="stPopoverButton"] {
    width: 44px !important;
    min-width: 44px !important;
    padding: 8px !important;
    margin: 0 auto !important;
    justify-content: center !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] button[data-testid="stPopoverButton"] span,
body.sidebar-mj-collapsed section[data-testid="stSidebar"] button[data-testid="stPopoverButton"] p,
body.sidebar-mj-collapsed section[data-testid="stSidebar"] button[data-testid="stPopoverButton"] div {
    display: none !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] button[data-testid="stPopoverButton"]::before {
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    width: 36px !important;
    height: 36px !important;
    line-height: 36px !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] p,
body.sidebar-mj-collapsed section[data-testid="stSidebar"] span:not([data-testid]) {
    display: none !important;
}
body.sidebar-mj-collapsed section[data-testid="stSidebar"] hr {
    margin: 8px 0 !important;
}
    /* Hide all known Streamlit sidebar toggle buttons */
    /* Aggressively hide all known Streamlit sidebar toggle buttons */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"],
    button[kind="headerNoPadding"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
        top: -9999px !important;
        left: -9999px !important;
        z-index: -1 !important;
    }
    
    #sidebar-custom-toggle {
        position: fixed;
        top: 20px;
        left: 180px; 
        z-index: 999999;
        background: white;
        border: 1px solid #EAEAEA;
        border-radius: 6px;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: #555;
        font-size: 16px;
        transition: all 0.25s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    #sidebar-custom-toggle:hover {
        color: var(--primary-color);
        border-color: var(--primary-color);
        background: #f8f9fa;
    }
    body.sidebar-mj-collapsed #sidebar-custom-toggle {
        left: 16px;
    }
    body.sidebar-mj-collapsed section[data-testid="stSidebar"] img:not(.sidebar-user-avatar),
    body.sidebar-mj-collapsed section[data-testid="stSidebar"] [data-testid="stLogo"] {
        display: none !important;
    }
    body.sidebar-mj-collapsed .sidebar-user-avatar {
        display: none !important;
    }
    @media (max-width: 768px) {
        #sidebar-custom-toggle { display: none !important; }
        section[data-testid="stSidebar"] { width: 100% !important; min-width: 100% !important; }
        button[data-testid="stSidebarCollapseButton"], button[data-testid="stExpandSidebarButton"] { display: block !important; } 
    }
    </style>
"""
    st.markdown(sidebar_css, unsafe_allow_html=True)

    js_code = """
    <script>
    function setupSidebarToggle() {
        const toggleId = 'sidebar-custom-toggle';
        let toggleBtn = parent.document.getElementById(toggleId);
        
        // Remove from sidebar if it exists there (fix from previous step)
        const existingOnSidebar = parent.document.querySelector('section[data-testid="stSidebar"] #' + toggleId);
        if (existingOnSidebar) existingOnSidebar.remove();

        if (!toggleBtn) {
            toggleBtn = parent.document.createElement('button');
            toggleBtn.id = toggleId;
            toggleBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
            toggleBtn.style.zIndex = "999999";
            
            // Append to Body (Safest for visibility)
            parent.document.body.appendChild(toggleBtn);
            
            toggleBtn.onclick = function() {
                parent.document.body.classList.toggle('sidebar-mj-collapsed');
                const isCollapsed = parent.document.body.classList.contains('sidebar-mj-collapsed');
                parent.localStorage.setItem('sidebar_collapsed', isCollapsed);
            };
            
            const savedState = parent.localStorage.getItem('sidebar_collapsed');
            if (savedState === 'true') {
                parent.document.body.classList.add('sidebar-mj-collapsed');
            }
        }
    }
    setTimeout(setupSidebarToggle, 500);
    // Retry in case of slow load
    setTimeout(setupSidebarToggle, 2000);
    </script>
    """
    import streamlit.components.v1 as components
    components.html(js_code, height=0, width=0)
