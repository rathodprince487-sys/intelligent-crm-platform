
import os

APP_PATH = '/Users/satyajeetsinhrathod/Desktop/n8n-backend/app.py'

NEW_SIDEBAR_LOGIC = r'''
with st.sidebar:
    # 1. Profile Section with Popover (Dropdown)
    profile_container = st.container()
    with profile_container:
        # We use a button-like popover to mimic the profile dropdown
        # Custom CSS will style this to look like the profile row
        # Avatar + Name + Role
        
        avatar_path = getattr(current_user, "avatar_file", "default_avatar.png")
        if avatar_path and os.path.exists(avatar_path):
            import base64
            with open(avatar_path, "rb") as f:
                b64_avatar = base64.b64encode(f.read()).decode()
            avatar_html = f'<img src="data:image/png;base64,{b64_avatar}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;">'
        else:
            avatar_html = f'<div style="width: 32px; height: 32px; background: #e0e7ff; color: #4338ca; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">{current_user.name[0].upper()}</div>'

        # We construct a label for the popover that includes the HTML (if supported) or just text
        # Streamlit popover label only supports text/emoji. We can't put HTML in label.
        # So we use "Name (Role)" text and rely on CSS to hide/show parts if possible, OR
        # We put the detailed profile ABOVE the navigation and use a small settings icon for the menu?
        # The prompt says: "When user clicks avatar: Open dropdown menu".
        # We can use st.popover with an icon "👤" and label "Profile".
        # Let's try to make it look clean.
        
        with st.popover(f"{current_user.name} ({current_user.role})", icon="👤", use_container_width=True):
            st.markdown(f"**{current_user.name}**")
            st.caption(current_user.role)
            if st.button("View Profile", use_container_width=True):
                st.session_state.nav_selection = "Profile Settings"
                st.rerun()
            if st.button("Logout", type="primary", use_container_width=True):
                if cookie_manager:
                    cookie_manager.delete('crm_user')
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()

    st.markdown("---")

    # 2. Define Menu Options (Clean Text Only)
    opts_map = {}
    
    # Core
    opts_map["Dashboard"] = "Dashboard"
    opts_map["My CRM"] = "My CRM"
    opts_map["SHD PIXEL"] = "SHD PIXEL"
    opts_map["Search Leads"] = "Search Leads"
    
    # Role Based - Intern
    if current_user.role == Role.INTERN:
        opts_map["Tasks"] = "Tasks"
        
    # Management (HR/CEO)
    if current_user.role in [Role.HR, Role.CEO]:
        # Interns group
        intern_users = [u for u in auth_manager.users.values() if u.role == Role.INTERN]
        for u in intern_users:
            opts_map[f"Intern: {u.name}"] = f"Intern: {u.name}"
            
        if current_user.role == Role.CEO:
            hr_users = [u for u in auth_manager.users.values() if u.role == Role.HR]
            for u in hr_users:
                 opts_map[f"HR: {u.name}"] = f"HR: {u.name}"
                 
        opts_map["User Mgmt"] = "User Management"
        
        if current_user.role == Role.CEO:
             opts_map["Analytics"] = "Analytics"

    # Tools
    opts_map["Power Dialer"] = "Power Dialer"
    opts_map["Email Verifier"] = "Email Verifier"
    opts_map["Google Maps Scraper"] = "Google Maps Scraper"
    opts_map["Spreadsheet Tool"] = "Spreadsheet Tool"
    
    # Profile Settings (Hidden from radio usually, but kept in map for logic if needed)
    # We don't add "Profile Settings" to radio list to keep it hidden, handled via session state override.
    
    # Determine Index
    current_val = st.session_state.get('nav_selection', 'Dashboard')
    
    # Handle hidden pages (like Profile Settings) finding a "parent" or defaulting
    display_val = current_val
    if current_val == "Profile Settings":
        display_val = None # No selection highlight or custom
    
    nav_keys = list(opts_map.keys())
    nav_index = 0
    try:
        val_list = list(opts_map.values())
        if current_val in val_list:
            nav_index = val_list.index(current_val)
        elif current_val == "CRM Grid": # Map back to My CRM context
             if "My CRM" in val_list: nav_index = val_list.index("My CRM")
    except:
        pass
    
    # 3. Render Navigation
    selected_label = st.radio("Navigation", nav_keys, index=nav_index, label_visibility="collapsed")
    
    # Check if radio changed state (user clicked sidebar)
    if opts_map[selected_label] != st.session_state.get('nav_selection'):
        # If user clicked something in sidebar, update state
        # But if we are in 'Profile Settings' and sidebar is clicked, it works naturally.
        selected_val = opts_map[selected_label]
    else:
        # If no change, stick to current (handles profile settings persist if not in radio)
        selected_val = st.session_state.get('nav_selection', opts_map[selected_label])

    # 4. Dynamic CSS Injection for Icons & Tooltips
    # Map Labels to FontAwesome Unicode
    ICON_MAP = {
        "Dashboard": "\\f201", # chart-line
        "My CRM": "\\f1c0", # database
        "SHD PIXEL": "\\f135", # rocket
        "Search Leads": "\\f002", # search
        "Tasks": "\\f0ae", # tasks
        "User Mgmt": "\\f509", # users-cog
        "Analytics": "\\f200", # chart-pie
        "Power Dialer": "\\f095", # phone
        "Email Verifier": "\\f658", # check-double / envelope
        "Google Maps Scraper": "\\f3c5", # map-marker
        "Spreadsheet Tool": "\\f0ce", # table
    }
    
    css_icons = ""
    for idx, key in enumerate(nav_keys):
        # Default Icon
        icon_code = ICON_MAP.get(key, "\\f111") # circle default
        
        # Handle dynamic keys like "Intern: Name"
        if "Intern:" in key: icon_code = "\\f501" # user-graduate
        if "HR:" in key: icon_code = "\\f508" # user-tie
        
        # 1. Inject Icon into ::before
        # nth-child is 1-based.
        # Streamlit radio divs: div[role="radiogroup"] > label:nth-child(idx+1)
        css_icons += f"""
        section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child({idx+1})::before {{
            content: "{icon_code}" !important;
        }}
        """
        
        # 2. Inject Tooltip into ::after (Collapsed Hover)
        css_icons += f"""
        body.sidebar-mj-collapsed section[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child({idx+1}):hover::after {{
            content: "{key}" !important;
        }}
        """
        
    st.markdown(f"<style>{css_icons}</style>", unsafe_allow_html=True)
    
    # 5. Bottom Section (Logout/Settings) - Visual Only as radio handles it or separate buttons
    # We used popover for logout.
'''

def refactor_app():
    with open(APP_PATH, 'r') as f:
        content = f.read()
    
    # 1. Add Import
    if "from components.profile_page import render_profile_page" not in content:
        content = "from components.profile_page import render_profile_page\n" + content
        
    # 2. Replace Sidebar Logic
    # Identify start and end of sidebar block
    start_marker = "with st.sidebar:"
    # We look for the end of the sidebar block. The next block usually starts with "if selected_val == ..." or dedent.
    # In previous reads, line ~1880 started the if chain.
    # Lines 1805 to 1900 approx.
    
    # Let's find the exact block range carefully.
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Could not find sidebar block")
        return

    # Find the end: look for "if selected_val == 'Logout':" or similar logic that WAS inside sidebar in previous code but logic dictates it should be outside?
    # Actually in previous app.py, logic was inside "if selected_val ...". No, dedentation implies outside sidebar context?
    # Python code: The `if selected_val` chain was indented?
    # Let's check view_file output from Step 279.
    # Line 1880: `    if selected_val == 'Logout':` -> Indented by 4 spaces. It WAS inside sidebar?
    # Wait, `with st.sidebar:` is usually col 0 or 4?
    # Line 1805: `with st.sidebar:` (col 0).
    # Line 1880: `    if selected_val == 'Logout':` (col 4).
    # So the logic was inside the sidebar block.
    # I want to extract the logic out or keep it in?
    # Usually logic is better outside UI blocks, but Streamlit allows it anywhere.
    # I'll replace the text from `with st.sidebar:` up to the end of the radio block logic.
    # But I need to preserve the `if selected_val` logic structure, just updating it.
    
    # I will construct the NEW logic block which includes the `if/elif` handling.
    NEW_LOGIC_BLOCK = NEW_SIDEBAR_LOGIC + r'''
    
    # Logic Handling
    if selected_val == 'Logout':
        # Handled by popover but keep safe
        pass 

    elif selected_val == 'Profile Settings':
        render_profile_page(auth_manager, current_user)

    elif selected_val == 'Dashboard':
        st.session_state.nav_selection = "Dashboard"
        # render_dashboard() ... (existing code follows)
    '''
    
    # Actually, replacing using string matching is risky if I don't match exact indentation/content.
    # I will replace `with st.sidebar:` ... until `elif selected_val == 'Dashboard':`
    
    # Target string to identify split point
    split_point_start = 'with st.sidebar:'
    # The existing code has `if selected_val == 'Logout':` then `elif selected_val == 'Dashboard':`.
    # I'll replace everything from `with st.sidebar:` up to `elif selected_val == 'Dashboard':`.
    # And insert my new sidebar + new handlers.
    
    end_marker = "elif selected_val == 'Dashboard':"
    end_idx = content.find(end_marker)
    
    if end_idx == -1:
        print("End marker not found")
        return
        
    # We need to include the "Logout" logic which was before Dashboard.
    # My NEW_SIDEBAR_LOGIC doesn't include the main content rendering, only sidebar UI.
    # I need to bridge the gap.
    
    # New logic to insert before 'Dashboard':
    BRIDGE = r'''
    if selected_val == 'Profile Settings':
        render_profile_page(auth_manager, current_user)
    '''
    
    # Remove old sidebar code
    # We keep content BEFORE start_marker
    # We keep content AFTER end_marker (Dashboard logic)
    # We insert NEW_SIDEBAR + BRIDGE
    
    new_content = content[:start_idx] + NEW_SIDEBAR_LOGIC + "\n    " + BRIDGE + "\n    " + content[end_idx:]
    
    with open(APP_PATH, 'w') as f:
        f.write(new_content)
    print("Refactor complete")

if __name__ == "__main__":
    refactor_app()
