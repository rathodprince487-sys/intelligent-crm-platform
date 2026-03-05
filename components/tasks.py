import streamlit as st
import pandas as pd
import json
import os
import uuid
from datetime import datetime

TASKS_FILE = "tasks_db.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def render_tasks_module(current_user, auth_manager):
    from components.auth import Role
    # Determine privileges
    is_assigner = current_user.role in [Role.CEO, Role.HR, "CEO", "HR"]
    
    # Custom CSS for modern tasks
    st.markdown("""
        <style>
        /* Modern Flat SaaS UI */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,400,0,0');
        
        .material-symbols-outlined {
            vertical-align: middle;
            font-size: 16px;
            margin-right: 6px;
            position: relative;
            top: -1px;
            color: inherit;
        }

        /* The overall tab styling */
        div[data-testid="stTabs"] button {
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            color: #64748b;
            transition: all 0.2s ease;
            border-bottom-width: 2px !important;
        }
        div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
            color: #3b82f6 !important;
            font-weight: 600 !important;
            border-bottom-color: #3b82f6 !important;
        }

        /* Task Card */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
            padding: 24px !important;
            margin-bottom: 16px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #cbd5e1 !important;
        }
        
        /* Expander styling */
        div[data-testid="stExpander"] details {
            border: 1px solid #e2e8f0 !important;
            background: #f8fafc !important;
            border-radius: 6px !important;
            margin-top: 16px;
            box-shadow: none !important;
        }
        div[data-testid="stExpander"] summary {
            font-weight: 600 !important;
            color: #334155 !important;
            padding: 12px 16px !important;
            border-radius: 6px !important;
            font-size: 14px;
        }
        div[data-testid="stExpander"] summary p {
            font-family: 'Inter', sans-serif;
        }
        div[data-testid="stExpander"] summary:hover {
            background: #f1f5f9 !important;
        }

        /* Badges */
        .shopify-badge {
            font-family: 'Inter', sans-serif;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.2px;
            display: inline-flex;
            align-items: center;
        }

        /* Meta tags */
        .meta-text {
            font-family: 'Inter', sans-serif;
            display: inline-flex;
            align-items: center;
            color: #64748b;
            font-size: 13px;
            font-weight: 500;
            margin-right: 20px;
            margin-bottom: 8px;
        }
        
        .meta-text b {
            font-weight: 600;
            color: #334155;
            margin-right: 6px;
        }

        /* Description block */
        .desc-block {
            font-family: 'Inter', sans-serif;
            color: #475569;
            font-size: 14px;
            line-height: 1.6;
            margin-top: 16px;
            margin-bottom: 16px;
            padding: 16px;
            background: #f8fafc;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        }
        
        /* Remarks block */
        .remarks-block {
            font-family: 'Inter', sans-serif;
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            padding: 16px;
            color: #166534;
            font-size: 13px;
            margin-bottom: 16px;
            border-radius: 6px;
        }

        /* Typography */
        h2.shopify-title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 8px;
            font-size: 24px;
            display: flex;
            align-items: center;
        }
        p.shopify-subtitle {
            font-family: 'Inter', sans-serif;
            color: #64748b;
            margin-bottom: 24px;
            font-size: 14px;
            font-weight: 400;
        }

        /* Forms */
        div[data-testid="stForm"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            padding: 24px !important;
        }

        /* Inputs & Labels */
        div.stTextInput label, div.stSelectbox label, div.stTextArea label, div.stDateInput label {
            font-family: 'Inter', sans-serif !important;
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            margin-bottom: 4px;
        }

        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div, .stDateInput > div {
            border: 1px solid #cbd5e1 !important;
            border-radius: 6px !important;
            background-color: #f8fafc !important;
            transition: all 0.2s ease;
        }
        
        div[data-baseweb="input"] > div:hover, div[data-baseweb="select"] > div:hover, div[data-baseweb="textarea"] > div:hover {
            border-color: #94a3b8 !important;
        }

        div[data-baseweb="input"]:focus-within > div, div[data-baseweb="select"]:focus-within > div, div[data-baseweb="textarea"]:focus-within > div {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
            background-color: #ffffff !important;
        }

        /* Primary Button */
        button[kind="primary"] {
            background-color: #3b82f6 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 6px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
            padding: 6px 16px !important;
        }
        
        button[kind="primary"]:hover {
            background-color: #2563eb !important;
            color: #ffffff !important;
        }

        /* Secondary Button (Save Update) */
        button[kind="secondary"] {
            background-color: #ffffff !important;
            color: #334155 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 6px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover {
            background-color: #f8fafc !important;
            border-color: #94a3b8 !important;
            color: #1e293b !important;
        }

        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='shopify-title'><span class='material-symbols-outlined' style='font-size: 28px; margin-right: 8px;'>check_circle</span> Task Management</h2>", unsafe_allow_html=True)
    st.markdown("<p class='shopify-subtitle'>Assign, track, and manage team deliverables efficiently.</p>", unsafe_allow_html=True)

    tasks = load_tasks()

    if is_assigner:
        tabs = st.tabs([":material/format_list_bulleted: Track Tasks", ":material/add: Assign New Task"])
        tab_track = tabs[0]
        tab_assign = tabs[1]
    else:
        # Interns
        tab_track = st.container()
        tab_assign = None

    if tab_assign:
        with tab_assign:
            with st.container():
                st.markdown("<h3 class='shopify-title' style='font-size: 20px; padding-bottom: 12px;'><span class='material-symbols-outlined' style='font-size: 24px; margin-right: 8px;'>add_task</span> Create a New Task</h3>", unsafe_allow_html=True)
                from components.auth import Role
                interns = [u for u in auth_manager.users.values() if u.role in [Role.INTERN, "Intern"]]
                intern_usernames = [u.username for u in interns]
                
                if not intern_usernames:
                    st.info("No interns available to assign tasks.")
                else:
                    with st.form("new_task_form", clear_on_submit=True):
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            title = st.text_input("Task Title *", placeholder="e.g., Data Entry for Q3")
                            assigned_to = st.selectbox("Assign To (Intern) *", intern_usernames)
                        with col2:
                            deadline = st.date_input("Deadline Date *", format="DD/MM/YYYY")
                            priority = st.selectbox("Priority *", ["High", "Medium", "Low"])
                            
                        category = st.selectbox("Category", ["Data Entry", "Review", "Follow-up", "Research", "Other"])
                        desc = st.text_area("Task Description *", placeholder="Describe the task and expectations...", height=120)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        submit = st.form_submit_button("Assign Task", type="primary", use_container_width=True)
                        
                        if submit:
                            if not title or not desc:
                                st.error("Please fill in all required fields marked with *.")
                            else:
                                new_t = {
                                    "id": str(uuid.uuid4()),
                                    "title": title,
                                    "assigned_to": assigned_to,
                                    "assigned_by": current_user.username,
                                    "deadline": deadline.strftime("%Y-%m-%d"),
                                    "priority": priority,
                                    "category": category,
                                    "description": desc,
                                    "status": "Pending",
                                    "notes": "",
                                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                tasks.append(new_t)
                                save_tasks(tasks)
                                st.success(f"Task successfully assigned to {assigned_to}!")
                                import time
                                time.sleep(0.5)
                                st.rerun()

    with tab_track:
        # Filter Logic
        from components.auth import Role
        if is_assigner:
            if current_user.role in [Role.CEO, "CEO"]:
                my_tasks = tasks
            else: # HR
                my_tasks = [t for t in tasks if t["assigned_by"] == current_user.username or t["assigned_to"] in [u.username for u in auth_manager.users.values() if u.role in [Role.INTERN, "Intern"]]]
        else: # Intern
            my_tasks = [t for t in tasks if t["assigned_to"] == current_user.username]

        if not my_tasks:
            st.info("No active tasks found in your queue.")
        else:
            if not is_assigner:
                 st.markdown("<h3 style='font-family:Inter; font-weight:600; color:#202223; margin-top:16px; margin-bottom: 20px; font-size: 18px;'>My Assigned Tasks</h3>", unsafe_allow_html=True)
            else:
                 st.markdown("<h3 style='font-family:Inter; font-weight:600; color:#202223; margin-top:16px; margin-bottom: 20px; font-size: 18px;'>Active Team Tasks</h3>", unsafe_allow_html=True)
                 
            # Sort tasks: High priority first, then deadline
            priority_map = {"High": 1, "Medium": 2, "Low": 3}
            my_tasks.sort(key=lambda x: (priority_map.get(x.get("priority", "Low"), 3), x.get("deadline", "")))

            for t in my_tasks:
                with st.container(border=True):
                    current_status = t.get("status", "Pending")
                    status_colors = {
                        "Pending": "#6d7175", "In Progress": "#005bd3", "Completed": "#008060"
                    }
                    status_bg = {
                        "Pending": "#f4f6f8", "In Progress": "#f1f8f5", "Completed": "#f3fcf6"
                    }
                    status_border = {
                        "Pending": "#e1e3e5", "In Progress": "#cce0ff", "Completed": "#b3ebc6"
                    }
                    color = status_colors.get(current_status, "#6d7175")
                    bg_color = status_bg.get(current_status, "#f4f6f8")
                    border_color = status_border.get(current_status, "#e1e3e5")
                    
                    priority = t['priority']
                    prio_colors = {
                        "High": ("#d72c0d", "#ffeaec", "#fdc9d0"),
                        "Medium": ("#8a6116", "#fffbeb", "#fce29f"),
                        "Low": ("#5c5f62", "#f4f6f8", "#e1e3e5")
                    }
                    p_color, p_bg, p_border = prio_colors.get(priority, ("#5c5f62", "#f4f6f8", "#e1e3e5"))
                    category = t.get('category', 'N/A')
                    
                    # Icons for category using Google Material Symbols
                    cat_icon = "label"
                    if category == "Data Entry": cat_icon = "keyboard"
                    elif category == "Review": cat_icon = "visibility"
                    elif category == "Follow-up": cat_icon = "call"
                    elif category == "Research": cat_icon = "search"
                    elif category == "Other": cat_icon = "push_pin"

                    assigner_user = auth_manager.users.get(t['assigned_by'])
                    assigner_name = assigner_user.name if assigner_user else t['assigned_by']
                    
                    assignee_user = auth_manager.users.get(t['assigned_to'])
                    assignee_name = assignee_user.name if assignee_user else t['assigned_to']
                    
                    assignee_str = f"""<div class="meta-text"><span class="material-symbols-outlined">person</span> <b>To:</b> {assignee_name}</div>""" if is_assigner else ""
                    
                    html_block = f"""
<div style="font-family: 'Inter', sans-serif; display: flex; flex-direction: column; gap: 12px;">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; width: 100%; gap: 12px;">
<div style="display: flex; flex-direction: column; gap: 12px; width: 100%;">
<div style="display: flex; align-items: center; gap: 12px;">
<h4 style="margin: 0; padding: 0; color: #1e293b; font-weight: 700; font-size: 16px;">{t["title"]}</h4>
<span class="shopify-badge" style="background-color: {p_bg}; color: {p_color}; border: 1px solid {p_border};">
<span style="width: 6px; height: 6px; border-radius: 50%; background-color: {p_color}; margin-right: 6px;"></span>
{priority}
</span>
</div>
<div style="display: flex; align-items: center; flex-wrap: wrap;">
<div class="meta-text"><span class="material-symbols-outlined">calendar_today</span> <b>Due:</b> {t['deadline']}</div>
<div class="meta-text"><span class="material-symbols-outlined">{cat_icon}</span> {category}</div>
<div class="meta-text"><span class="material-symbols-outlined">edit_square</span> <b>By:</b> {assigner_name}</div>
{assignee_str}
</div>
</div>
<span class="shopify-badge" style="background-color: {bg_color}; color: {color}; border: 1px solid {border_color}; margin-left: auto;">{current_status}</span>
</div>
</div>
"""
                    st.markdown(html_block, unsafe_allow_html=True)
                    
                    if t.get('description'):
                        st.markdown(f"<div class='desc-block'>{t['description']}</div>", unsafe_allow_html=True)
                        
                    if t.get('remarks'):
                        st.markdown(f"<div class='remarks-block'><div style='display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size: 18px;'>check_circle</span><b style='font-size:14px; font-weight:600;'>Completion Remarks</b></div><div style='padding-left: 26px; margin-top: 4px;'>{t['remarks']}</div></div>", unsafe_allow_html=True)
                    
                    # Interactive row for updates
                    with st.expander("Update Status / View Notes"):
                        u_col1, u_col2 = st.columns([1, 2])
                        with u_col1:
                            # Map statuses to distinct options
                            status_options = ["Pending", "In Progress", "Completed"]
                            # Default to Pending if unknown
                            st_index = status_options.index(t.get("status")) if t.get("status") in status_options else 0
                            new_status = st.selectbox("Status", status_options, index=st_index, key=f"status_{t['id']}")
                        with u_col2:
                            new_notes = st.text_area("Task Notes / Updates", value=t.get("notes", ""), key=f"notes_{t['id']}", height=68)
                            
                        new_remarks = t.get("remarks", "")
                        if new_status == "Completed":
                            new_remarks = st.text_area("Completion Remarks *", value=t.get("remarks", ""), key=f"remarks_{t['id']}", placeholder="Provide final remarks/status upon completing this task...")
                            
                        if st.button("Save Update", key=f"save_{t['id']}", type="secondary", use_container_width=True):
                            if new_status == "Completed" and not new_remarks.strip():
                                st.error("Please provide completion remarks.")
                            else:
                                # Find and update
                                for master_t in tasks:
                                    if master_t["id"] == t["id"]:
                                        master_t["status"] = new_status
                                        master_t["notes"] = new_notes
                                        master_t["remarks"] = new_remarks
                                        save_tasks(tasks)
                                        st.success("Task updated!")
                                        import time
                                        time.sleep(0.5)
                                        st.rerun()
                                        break
