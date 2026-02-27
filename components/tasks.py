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
        .task-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.2s;
        }
        .task-card:hover {
             border-color: #cbd5e1;
             box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .task-title {
            font-size: 20px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 8px;
        }
        .task-meta {
            font-size: 14px;
            color: #64748b;
            margin-bottom: 16px;
            display: flex;
            gap: 16px;
            align-items: center;
        }
        .priority-High { color: #ef4444; font-weight: 600; background: #fee2e2; padding: 2px 8px; border-radius: 12px; font-size: 13px;}
        .priority-Medium { color: #f59e0b; font-weight: 600; background: #fef3c7; padding: 2px 8px; border-radius: 12px; font-size: 13px;}
        .priority-Low { color: #3b82f6; font-weight: 600; background: #dbeafe; padding: 2px 8px; border-radius: 12px; font-size: 13px;}
        
        .status-Pending { color: #64748b; font-weight: 600; }
        .status-In-Progress { color: #3b82f6; font-weight: 600; }
        .status-Completed { color: #10b981; font-weight: 600; }
        
        .task-desc {
            font-size: 15px;
            color: #334155;
            background: #f8fafc;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 16px;
            border-left: 3px solid #cbd5e1;
        }
        
        /* Specific Tab Overrides for Tasks */
        div[data-testid="stTabs"] button {
            font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='font-weight: 700; color: #1e293b; margin-bottom: 8px;'>📝 Task Management</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-bottom: 24px;'>Assign, track, and manage team deliverables efficiently.</p>", unsafe_allow_html=True)

    tasks = load_tasks()

    if is_assigner:
        tabs = st.tabs(["📋 Track Tasks", "➕ Assign New Task"])
        tab_track = tabs[0]
        tab_assign = tabs[1]
    else:
        # Interns
        tab_track = st.container()
        tab_assign = None

    if tab_assign:
        with tab_assign:
            with st.container():
                st.markdown("### Create a New Task")
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
                 st.markdown("### My Assiged Tasks")
            else:
                 st.markdown("### Active Team Tasks")
                 
            # Sort tasks: High priority first, then deadline
            priority_map = {"High": 1, "Medium": 2, "Low": 3}
            my_tasks.sort(key=lambda x: (priority_map.get(x.get("priority", "Low"), 3), x.get("deadline", "")))

            for t in my_tasks:
                with st.container(border=True):
                    current_status = t.get("status", "Pending")
                    status_colors = {
                        "Pending": "#64748b", "In Progress": "#3b82f6", "Completed": "#10b981"
                    }
                    status_bg = {
                        "Pending": "#f1f5f9", "In Progress": "#eff6ff", "Completed": "#f0fdf4"
                    }
                    color = status_colors.get(current_status, "#64748b")
                    bg_color = status_bg.get(current_status, "#f1f5f9")
                    
                    priority = t['priority']
                    prio_colors = {
                        "High": ("#ef4444", "#fee2e2"),
                        "Medium": ("#f59e0b", "#fef3c7"),
                        "Low": ("#3b82f6", "#dbeafe")
                    }
                    p_color, p_bg = prio_colors.get(priority, ("#64748b", "#f1f5f9"))
                    category = t.get('category', 'N/A')
                    
                    assigner_user = auth_manager.users.get(t['assigned_by'])
                    assigner_name = assigner_user.name if assigner_user else t['assigned_by']
                    
                    assignee_user = auth_manager.users.get(t['assigned_to'])
                    assignee_name = assignee_user.name if assignee_user else t['assigned_to']
                    
                    assignee_str = f"""<span style="color: #64748b; font-size: 13px;">👤 <b>To:</b> {assignee_name}</span>""" if is_assigner else ""
                    
                    html_block = f"""
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
<div style="display: flex; flex-direction: column; gap: 8px;">
<div style="display: flex; align-items: center; gap: 12px;">
<h4 style="margin: 0; padding: 0; color: #0f172a; font-weight: 600; font-size: 18px;">{t["title"]}</h4>
<span style="background-color: {p_bg}; color: {p_color}; padding: 2px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600;">{priority}</span>
</div>
<div style="display: flex; gap: 16px; align-items: center; flex-wrap: wrap;">
<span style="color: #64748b; font-size: 13px;">📅 <b>Due:</b> {t['deadline']}</span>
<span style="color: #64748b; font-size: 13px;">🏷️ {category}</span>
<span style="color: #64748b; font-size: 13px;">✍️ <b>By:</b> {assigner_name}</span>
{assignee_str}
</div>
</div>
<span style="background-color: {bg_color}; color: {color}; padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: 600;">{current_status}</span>
</div>
"""
                    st.markdown(html_block, unsafe_allow_html=True)
                    
                    if t.get('description'):
                        st.markdown(f"<div style='color: #334155; font-size: 15px; margin-top: 4px; margin-bottom: 8px; line-height: 1.5;'>{t['description']}</div>", unsafe_allow_html=True)
                        
                    if t.get('remarks'):
                        st.markdown(f"<div style='background: #f0fdf4; border-left: 3px solid #10b981; padding: 12px; color: #166534; font-size: 14px; margin-bottom: 8px;'><b>✅ Completion Remarks:</b><br/>{t['remarks']}</div>", unsafe_allow_html=True)
                    
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
