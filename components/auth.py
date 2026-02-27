import streamlit as st
import hashlib
import json
import os
import secrets
import base64
from enum import Enum
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
USERS_FILE = "users.json"
CRM_DATA_DIR = "crm_data"

class Role(str, Enum):
    INTERN = "Intern"
    HR = "HR"
    CEO = "CEO"

class User:
    def __init__(self, username, name, role, password_hash, salt, status="Active", email=None, visible_password=None):
        self.username = username
        self.name = name
        self.role = role
        self.password_hash = password_hash
        self.salt = salt
        self.status = status
        self.email = email if email else f"{username}@n8nOutline.com"
        self.visible_password = visible_password
        self.avatar_file = "default_avatar.png"

    def to_dict(self):
        return {
            "username": self.username,
            "name": self.name,
            "role": self.role,
            "password_hash": self.password_hash,
            "salt": self.salt,
            "status": self.status,
            "email": self.email,
            "visible_password": self.visible_password,
            "avatar_file": getattr(self, "avatar_file", "default_avatar.png")
        }

    @staticmethod
    def from_dict(data):
        u = User(
            data["username"],
            data["name"],
            data["role"],
            data["password_hash"],
            data["salt"],
            data.get("status", "Active"),
            data.get("email"),
            data.get("visible_password")
        )
        u.avatar_file = data.get("avatar_file", "default_avatar.png")
        return u

class AuthManager:
    def __init__(self):
        self._ensure_crm_dirs()
        self.users = self._load_users()
        self._ensure_admin_exists()

    def _ensure_crm_dirs(self):
        os.makedirs(CRM_DATA_DIR, exist_ok=True)
        os.makedirs(os.path.join(CRM_DATA_DIR, "shared"), exist_ok=True)
        os.makedirs(os.path.join(CRM_DATA_DIR, "shared", "shd_pixel"), exist_ok=True)

    def _load_users(self):
        if not os.path.exists(USERS_FILE):
            return {}
        try:
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
                return {u["username"]: User.from_dict(u) for u in data}
        except Exception as e:
            st.error(f"Error loading users: {e}")
            return {}

    def _save_users(self):
        with open(USERS_FILE, "w") as f:
            json.dump([u.to_dict() for u in self.users.values()], f, indent=4)

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)
        # Use PBKDF2 with SHA256
        input_enc = password.encode('utf-8')
        salt_enc = salt.encode('utf-8')
        dk = hashlib.pbkdf2_hmac('sha256', input_enc, salt_enc, 100000)
        return dk.hex(), salt

    def _ensure_admin_exists(self):
        if "admin" not in self.users:
            ph, salt = self._hash_password("admin123")
            admin = User("admin", "System Admin", Role.CEO, ph, salt)
            self.users["admin"] = admin
            self._save_users()
            self._ensure_user_crm_folder("admin")

    def _ensure_user_crm_folder(self, username):
        path = os.path.join(CRM_DATA_DIR, username)
        os.makedirs(path, exist_ok=True)

    def login(self, username, password):
        user = self.users.get(username)
        if not user:
            return None
        
        if user.status != "Active":
            return "Inactive"

        ph, _ = self._hash_password(password, user.salt)
        if ph == user.password_hash:
            return user
        return None

    def create_user(self, creator_role, new_username, new_name, new_role, new_password, new_email=None):
        # RBAC for creation
        if creator_role == Role.INTERN:
            return False, "Interns cannot create users."
        if creator_role == Role.HR and new_role != Role.INTERN:
            return False, "HR can only create Interns."
        
        if new_username in self.users:
            return False, "Username already exists."

        ph, salt = self._hash_password(new_password)
        new_user = User(new_username, new_name, new_role, ph, salt, email=new_email, visible_password=new_password)
        self.users[new_username] = new_user
        self._save_users()
        self._ensure_user_crm_folder(new_username)
        return True, "User created successfully."

    def delete_user(self, creator_role, target_username):
        target = self.users.get(target_username)
        if not target: return False, "User not found."

        if creator_role == Role.INTERN:
            return False, "Permission denied."
        if creator_role == Role.HR and target.role != Role.INTERN:
            return False, "HR can only delete Interns."
        if creator_role == Role.CEO and target.role == Role.CEO and target_username == "admin":
             return False, "Cannot delete root admin."
        
        del self.users[target_username]
        self._save_users()
        return True, "User deleted."
    
    def reset_password(self, creator_role, target_username, new_password):
        target = self.users.get(target_username)
        if not target: return False, "User not found."

        if creator_role == Role.INTERN:
            return False, "Permission denied."
        if creator_role == Role.HR and target.role != Role.INTERN:
             return False, "HR can only reset Intern passwords."
        
        ph, salt = self._hash_password(new_password)
        target.password_hash = ph
        target.salt = salt
        target.visible_password = new_password
        self._save_users()
        return True, "Password reset."

    def change_password(self, username, old_password, new_password):
        user = self.users.get(username)
        if not user:
            return False, "User not found"
        
        # Verify old password
        ph, _ = self._hash_password(old_password, user.salt)
        if ph != user.password_hash:
            return False, "Incorrect old password"
            
        # Set new password
        new_ph, new_salt = self._hash_password(new_password)
        user.password_hash = new_ph
        user.salt = new_salt
        user.visible_password = new_password
        self._save_users()
        return True, "Password changed successfully"
        
    def change_email(self, creator_role, target_username, new_email):
        target = self.users.get(target_username)
        if not target: return False, "User not found."

        if creator_role == Role.INTERN:
            return False, "Permission denied."
        if creator_role == Role.HR and target.role != Role.INTERN:
             return False, "HR can only alter Interns."
             
        target.email = new_email
        self._save_users()
        return True, "Email changed successfully."

    def update_profile(self, username, new_name):
        user = self.users.get(username)
        if not user:
            return False, "User not found"
        
        user.name = new_name
        # Persist changes
        self._save_users()
        return True, "Profile updated successfully"

    def update_avatar(self, username, uploaded_file):
        if not uploaded_file:
            return False
        
        # Ensure directory
        avatar_dir = "assets/avatars"
        os.makedirs(avatar_dir, exist_ok=True)
        
        # Save file
        file_ext = uploaded_file.name.split('.')[-1]
        filename = f"{username}_avatar.{file_ext}"
        file_path = os.path.join(avatar_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Update user
        user = self.users.get(username)
        if user:
            user.avatar_file = file_path
            self._save_users()
            return file_path
        return None

    def get_accessible_crms(self, user):
        """Returns list of CRM names (folders) visible to the user."""
        options = ["My CRM", "SHD PIXEL"]
        
        if user.role == Role.INTERN:
            # Intern only sees own + shared
            return options

        # HR sees all Interns
        interns = [u.username for u in self.users.values() if u.role == Role.INTERN]
        if user.role == Role.HR:
            return options + [f"Intern: {i}" for i in interns]

        # CEO sees all
        all_users = [u.username for u in self.users.values() if u.username != user.username]
        if user.role == Role.CEO:
            return options + [f"User: {u}" for u in all_users]
        
        return options

    def resolve_crm_path(self, selection, current_user):
        """Converts dropdown selection to actual file path identifier."""
        if selection == "My CRM":
            return current_user.username
        if selection == "SHD PIXEL":
            return "shared/shd_pixel"
        
        # Parse "Intern: username" or "User: username"
        if ":" in selection:
            return selection.split(": ")[1]
        
        return current_user.username

# Helper for Image to Base64
def get_img_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

def render_login_page(cookie_manager=None):
    # Modern Login UI
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8fafc; 
        }
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            margin-top: 10vh;
            padding: 40px;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Calculate Logo B64
    logo_path = "logo_light.png" if os.path.exists("logo_light.png") else "logo.png"
    logo_b64 = get_img_b64(logo_path)

    c1, c2, c3 = st.columns([1, 1.2, 1]) 
    
    with c2:
        # Logo Area (Centered HTML)
        if logo_b64:
             st.markdown(f"""
             <div style="display: flex; justify-content: center; margin-bottom: 24px;">
                 <img src="data:image/png;base64,{logo_b64}" style="width: 200px; height: auto;">
             </div>
             """, unsafe_allow_html=True)
        else:
             st.markdown("<div style='text-align:center; font-size: 40px;'>🔐 SHDPIXEL</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 26px; margin: 0; color: #1e293b; font-weight: 700;">Welcome back</h1>
            <p style="color: #64748b; font-size: 14px; margin-top: 8px;">Enter your credentials to access your account.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Card Container
        with st.container():
            if "forgot_pass" not in st.session_state:
                st.session_state.forgot_pass = False
                
            if not st.session_state.forgot_pass:
                username = st.text_input("Username", key="login_user", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
                
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
                
                if st.button("SIGN IN", type="primary", use_container_width=True):
                    auth = AuthManager()
                    user = auth.login(username, password)
                    if user == "Inactive":
                        st.error("Account is inactive.")
                    elif user:
                        # Set Session State
                        st.session_state["user"] = user
                        st.session_state["authenticated"] = True
                        st.session_state["active_crm_selection"] = "My CRM"
                        
                        # Set Cookie (Persist Login)
                        if cookie_manager:
                            expires = datetime.now() + timedelta(days=7)
                            cookie_manager.set("crm_user", username, expires_at=expires)
                            import time
                            time.sleep(0.5)
                        
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

                if st.button("Forgot your password?", use_container_width=True):
                    st.session_state.forgot_pass = True
                    st.rerun()
                    
            else:
                st.markdown("<h4 style='color: #1e293b; margin-top: 0;'>Reset Password</h4>", unsafe_allow_html=True)
                reset_input = st.text_input("Username or Email Address", placeholder="Enter username or email")
                
                st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
                
                if st.button("Send Reset Mail", type="primary", use_container_width=True):
                    if reset_input:
                        auth = AuthManager()
                        found = False
                        for u in auth.users.values():
                            if u.username == reset_input or getattr(u, 'email', '') == reset_input:
                                found = True
                                email_dest = getattr(u, 'email', f"{u.username}@n8nOutline.com")
                                st.success(f"✅ An email with password reset instructions has been sent to **{email_dest}**.")
                                break
                        if not found:
                            st.error("❌ No account found with those details.")
                    else:
                        st.warning("Please enter your username or email.")
                        
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.forgot_pass = False
                    st.rerun()


def render_admin_panel(auth_manager, current_user):
    st.markdown("""
        <style>
        .admin-header {
            font-size: 32px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 4px;
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.02em;
        }
        .admin-subtitle {
            color: #64748b;
            font-size: 16px;
            margin-bottom: 32px;
            font-weight: 500;
        }
        
        .admin-section-title {
            font-size: 20px;
            font-weight: 700;
            color: #1e293b;
            margin-top: 16px;
            margin-bottom: 8px;
        }
        
        .admin-section-desc {
            color: #64748b;
            font-size: 15px;
            margin-bottom: 24px;
        }

        /* Custom styling for forms in the admin panel */
        div[data-testid="stForm"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        }
        
        /* Modern Inputs */
        div[data-testid="stForm"] .stTextInput input, div[data-testid="stForm"] .stSelectbox div[data-baseweb="select"] > div {
            height: 48px !important;
            border-radius: 8px !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #f8fafc !important;
            color: #0f172a !important;
            font-size: 15px !important;
            transition: all 0.2s;
        }
        div[data-testid="stForm"] .stTextInput input:focus, div[data-testid="stForm"] .stSelectbox div[data-baseweb="select"] > div:focus-within {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
            background-color: #ffffff !important;
        }
        
        /* Form Label */
        div[data-testid="stForm"] label p {
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #475569 !important;
            margin-bottom: 4px;
        }

        /* Buttons styling */
        div[data-testid="stFormSubmitButton"] button {
            height: 48px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            transition: all 0.2s ease-in-out !important;
        }
        div[data-testid="stFormSubmitButton"] button[kind="primary"] {
            background-color: #2563eb !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
        }
        div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
            background-color: #1d4ed8 !important;
            transform: translateY(-1px);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 48px;
            background-color: transparent;
            border: none;
            color: #64748b;
            font-weight: 600;
            font-size: 15px;
            padding: 0 20px;
            border-radius: 8px 8px 0 0;
            transition: all 0.2s ease;
            margin-bottom: -2px; 
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #1e293b;
            background-color: #f1f5f9;
            border-bottom: 2px solid #cbd5e1;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #2563eb; 
            background-color: #ffffff;
            border-bottom: 2px solid #2563eb;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="admin-header">🛡️ User Management</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="admin-subtitle">Admin Panel for {current_user.role}</div>', unsafe_allow_html=True)

    # Tabs: List Workers, Create User
    tab1, tab2 = st.tabs(["User List", "Create New User"])

    with tab1:
        st.markdown('<div class="admin-section-title">Existing Users</div>', unsafe_allow_html=True)
        st.markdown('<div class="admin-section-desc">Manage your team members, update statuses, or reset passwords.</div>', unsafe_allow_html=True)
        users = auth_manager.users
        # Filter visibility
        visible_users = []
        for u in users.values():
             if current_user.role == Role.HR:
                 if u.role == Role.INTERN:
                     visible_users.append(u)
             elif current_user.role == Role.CEO:
                 visible_users.append(u)
        
        if not visible_users:
            st.warning("No users found based on your role.")
        else:
            # Custom Table Layout
            st.markdown("""
            <div style="display: grid; grid-template-columns: 2fr 1.5fr 2fr 1fr 1fr 2fr; gap: 8px; font-weight: 600; color: #475569; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; margin-bottom: 8px; font-size: 14px;">
                <div>Name</div>
                <div>Username</div>
                <div>Email</div>
                <div>Role</div>
                <div>Status</div>
                <div>Plain Password</div>
            </div>
            """, unsafe_allow_html=True)
            
            for u in visible_users:
                c1, c2, c3, c4, c5, c6 = st.columns([2, 1.5, 2, 1, 1, 2], vertical_alignment="center")
                
                with c1: st.write(u.name)
                with c2: st.write(u.username)
                with c3: st.write(getattr(u, "email", "Not Set"))
                with c4:
                    if u.role == "CEO": st.markdown("👑 CEO")
                    elif u.role == "HR": st.markdown("👔 HR")
                    else: st.markdown("👨‍💻 Intern")
                with c5:
                    color = "green" if u.status == "Active" else "red"
                    st.markdown(f"<span style='color:{color}; font-weight:600;'>{u.status}</span>", unsafe_allow_html=True)
                with c6:
                    actual_pass = getattr(u, "visible_password", "") if getattr(u, "visible_password", None) else "HIDDEN"
                    st.text_input(
                        "Password",
                        value=actual_pass,
                        type="password",
                        key=f"pass_{u.username}",
                        label_visibility="collapsed",
                        help="Click the eye icon to view",
                        disabled=True
                    )

            st.markdown('<div class="admin-section-title">User Actions</div>', unsafe_allow_html=True)
            sel_target = st.selectbox("Select User Action Target", [u.username for u in visible_users])
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                t_status = st.selectbox("Set Status", ["Active", "Inactive"], key="adm_stat_sel")
                if st.button("Update Status"):
                    if sel_target:
                        users[sel_target].status = t_status
                        auth_manager._save_users()
                        st.success("Updated")
                        st.rerun()
            with c2:
                new_em = st.text_input("New Email", key="adm_em_in")
                if st.button("Change Email"):
                    if sel_target and new_em:
                        s, m = auth_manager.change_email(current_user.role, sel_target, new_em)
                        if s: st.success(m)
                        else: st.error(m)
            with c3:
                new_p = st.text_input("New Password", type="password", key="adm_rp_in")
                if st.button("Reset Password"):
                    if sel_target and new_p:
                        auth_manager.reset_password(current_user.role, sel_target, new_p)
                        st.success("Password Reset")
            with c4:
                st.markdown("<br>", unsafe_allow_html=True) # align with input fields
                if st.button("Delete User", type="primary"):
                    if sel_target:
                        ok, msg = auth_manager.delete_user(current_user.role, sel_target)
                        if ok: 
                            st.success(msg)
                            st.rerun()
                        else: st.error(msg)


    with tab2:
        st.markdown('<div class="admin-section-title">Create New User</div>', unsafe_allow_html=True)
        st.markdown('<div class="admin-section-desc">Fill in the details below to add a new user to the system.</div>', unsafe_allow_html=True)
        
        # Use columns to constrain the width of the form for better readability
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.form("create_user_form", clear_on_submit=True):
                new_u = st.text_input("Username", placeholder="e.g. john.doe")
                new_n = st.text_input("Full Name", placeholder="e.g. John Doe")
                new_em = st.text_input("Email Address", placeholder="e.g. john@example.com")
                new_p = st.text_input("Password", type="password", placeholder="Enter a secure password")
                
                role_options = [Role.INTERN]
                if current_user.role == Role.CEO:
                    role_options.append(Role.HR)
                
                new_r = st.selectbox("Role", role_options, format_func=lambda x: x.value)
                
                st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
                
                # Center the submit button
                submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
                with submit_col2:
                    submitted = st.form_submit_button("Create User", type="primary", use_container_width=True)
                
                if submitted:
                    if new_u and new_n and new_p and new_em:
                        success, msg = auth_manager.create_user(current_user.role, new_u, new_n, new_r, new_p, new_em)
                        if success: 
                            st.success(f"✅ User '{new_u}' created successfully!")
                        else: 
                            st.error(f"❌ {msg}")
                    else:
                        st.error("⚠️ Please fill in all required fields.")
