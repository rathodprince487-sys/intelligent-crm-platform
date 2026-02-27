
import streamlit as st
import os
import base64

def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_profile_page(auth_manager, current_user):
    # --- SaaS Professional Styling ---
    st.markdown("""
    <style>
        /* Page Background */
        .stApp {
            background-color: #F5F7FA;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Container Max Width */
        .block-container {
            max-width: 1100px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Profile Header */
        .profile-header {
            margin-bottom: 2rem;
            border-bottom: 1px solid #E5E7EB;
            padding-bottom: 1rem;
        }
        .profile-header h1 {
            font-size: 24px;
            font-weight: 700;
            color: #111827;
            margin: 0 0 4px 0;
            padding: 0;
        }
        .profile-header p {
            font-size: 14px;
            color: #6B7280;
            margin: 0;
        }

        /* Global Card Styling for st.container(border=True) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            border: 1px solid #E5E7EB !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
            padding: 16px !important; /* Internal padding */
            margin-bottom: 24px;
        }

        /* Avatar Section */
        .avatar-wrapper {
            position: relative;
            display: inline-block;
            margin-bottom: 16px;
        }
        .avatar-img {
            width: 110px;
            height: 110px;
            border-radius: 50%;
            object-fit: contain;
            background-color: #FFFFFF;
            border: 3px solid #FFFFFF;
            box-shadow: 0 0 0 2px #E5E7EB;
        }
        
        /* Typography */
        .profile-name {
            font-size: 18px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 4px;
        }
        .profile-username {
            font-size: 13px;
            color: #9CA3AF;
            font-family: monospace;
            margin-bottom: 12px;
        }
        
        /* Role Badge */
        .role-badge {
            display: inline-block;
            padding: 4px 12px;
            background-color: #EEF2FF;
            color: #4F46E5;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid #C7D2FE;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Card Headers */
        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-title span {
            font-size: 18px;
        }

        /* Input Label Tweaks */
        div[data-testid="stMarkdownContainer"] p {
            font-size: 14px;
            font-weight: 500;
            color: #374151;
        }
        
        /* Button Tweaks */
        button[kind="primary"] {
            border-radius: 6px !important;
            font-weight: 500 !important;
            padding: 0.5rem 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Header Section ---
    st.markdown("""
        <div class="profile-header">
            <h1>Profile Settings</h1>
            <p>Manage your personal information and account security</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Main Layout (30% Left, 70% Right) ---
    col_left, col_right = st.columns([3, 7], gap="large")

    # ==========================
    # LEFT COLUMN: Profile Card
    # ==========================
    with col_left:
        with st.container(border=True):
            # We align content center using markdown for the top part
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            
            # 1. Avatar
            avatar_path = getattr(current_user, "avatar_file", None)
            img_html = ""
            
            if avatar_path and os.path.exists(avatar_path):
                 b64_img = get_image_base64(avatar_path)
                 file_ext = avatar_path.split('.')[-1]
                 mime = f"image/{file_ext}"
                 img_html = f'<img src="data:{mime};base64,{b64_img}" class="avatar-img">'
            else:
                 initial = current_user.name[0].upper() if current_user.name else "U"
                 img_html = f"""
                 <div class="avatar-img" style="display:flex; align-items:center; justify-content:center; background:#F3F4F6; color:#6B7280; font-size:48px; font-weight:600;">
                    {initial}
                 </div>
                 """
            
            st.markdown(f'<div class="avatar-wrapper">{img_html}</div>', unsafe_allow_html=True)
            
            # 2. Identity
            st.markdown(f'<div class="profile-name">{current_user.name}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-username">@{current_user.username}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="role-badge">{current_user.role}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

            # 3. Change Photo Action (Native widget inside container)
            from streamlit_cropper import st_cropper
            from PIL import Image
            import io

            with st.popover("📷 Change Photo", use_container_width=True):
                st.markdown("### Update Profile Picture")
                st.caption("Upload and crop your profile picture.")
                uploaded_file = st.file_uploader("Upload new image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    # Resize huge images to avoid performance issues in browser
                    if image.width > 1000:
                        image.thumbnail((1000, 1000))
                    
                    st.write("Adjust crop box:")
                    # st_cropper returns the cropped image
                    cropped_img = st_cropper(image, realtime_update=True, box_color='#4F46E5', aspect_ratio=(1,1))
                    
                    st.write("Preview:")
                    col_prev1, col_prev2 = st.columns([1, 2])
                    with col_prev1:
                         # Show circular preview
                         st.image(cropped_img, width=100, caption="New Avatar")
                    
                    if st.button("Save New Photo", type="primary", use_container_width=True):
                         # Convert PIL image to bytes for the existing auth_manager
                         img_byte_arr = io.BytesIO()
                         # Determine format from original or default to PNG
                         fmt = image.format if image.format else 'PNG'
                         cropped_img.save(img_byte_arr, format=fmt)
                         img_byte_arr.seek(0)
                         # Wrap in a class that behaves like UploadedFile if needed, or check update_avatar signature
                         # update_avatar likely expects an object with .read() or similar. 
                         # Let's check auth_manager.update_avatar implementation first or adapt passed object.
                         # Assuming update_avatar works with a file-like object.
                         
                         # We create a simple wrapper or just pass the bytesIO with a name attribute
                         img_byte_arr.name = uploaded_file.name
                         
                         new_path = auth_manager.update_avatar(current_user.username, img_byte_arr)
                         if new_path:
                            current_user.avatar_file = new_path
                            st.session_state["user"] = current_user 
                            st.rerun()


    # ==============================
    # RIGHT COLUMN: Fields & Config
    # ==============================
    with col_right:
        
        # --- CARD 1: Personal Information ---
        with st.container(border=True):
            st.markdown('<div class="card-title"><span>👤</span> Personal Information</div>', unsafe_allow_html=True)
            
            with st.form("personal_info_form", border=False):
                # Editable Name
                new_name = st.text_input("Full Name", value=current_user.name)
                
                st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
                
                # Read-only Details Grid
                email_val = getattr(current_user, "email", f"{current_user.username}@n8nOutline.com")
                
                info_cols = st.columns(3)
                with info_cols[0]:
                    st.markdown(f"""
                        <div style="font-size: 12px; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Username</div>
                        <div style="font-size: 14px; color: #111827; font-weight: 500; margin-top: 4px;">@{current_user.username}</div>
                    """, unsafe_allow_html=True)
                with info_cols[1]:
                    st.markdown(f"""
                        <div style="font-size: 12px; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Role</div>
                        <div style="font-size: 14px; color: #111827; font-weight: 500; margin-top: 4px;">{current_user.role}</div>
                    """, unsafe_allow_html=True)
                with info_cols[2]:
                    st.markdown(f"""
                        <div style="font-size: 12px; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Email</div>
                        <div style="font-size: 14px; color: #111827; font-weight: 500; margin-top: 4px;">{email_val}</div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
                
                # Save Button
                b_col1, b_col2 = st.columns([3, 1])
                with b_col2:
                    submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
                
                if submitted:
                    if new_name and new_name != current_user.name:
                        auth_manager.update_profile(current_user.username, new_name)
                        current_user.name = new_name
                        st.session_state["user"] = current_user
                        st.toast("Profile updated successfully!", icon="✅")
                        st.rerun()
                    else:
                        st.info("No changes to save.")


        # --- CARD 2: Security ---
        with st.container(border=True):
            st.markdown('<div class="card-title"><span>🔒</span> Security</div>', unsafe_allow_html=True)
            
            with st.expander("Change Password", expanded=False):
                st.caption("Ensure your account is using a long, random password to stay secure.")
                with st.form("pwd_change_form", border=False):
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        curr_pass = st.text_input("Current Password", type="password")
                    
                    pc3, pc4 = st.columns(2)
                    with pc3:
                        new_pass = st.text_input("New Password", type="password", help="Minimum 8 characters")
                    with pc4:
                        confirm_pass = st.text_input("Confirm New Password", type="password")

                    st.write("")
                    if st.form_submit_button("Update Password"):
                        if new_pass != confirm_pass:
                            st.error("Passwords do not match")
                        elif not curr_pass:
                            st.error("Current password is required")
                        else:
                            success, msg = auth_manager.change_password(current_user.username, curr_pass, new_pass)
                            if success:
                                st.success("Password updated successfully")
                            else:
                                st.error(msg)
