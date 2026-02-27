import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os
from components.auth import AuthManager, Role

def render_analytics_dashboard():
    
    st.markdown("""
        <style>
        /* Base page background */
        [data-testid="stAppViewContainer"] {
            background-color: #f8fafc;
        }
        
        /* Chart containers */
        div[data-testid="stPlotlyChart"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            padding: 1rem;
        }

        /* Analytics Title */
        .analytics-title {
            font-size: 1.75rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .analytics-title .info-icon {
            font-size: 1.1rem;
            color: #94a3b8;
            font-weight: normal;
        }

        /* View Mode Label */
        .view-mode-label {
            font-size: 11px !important;
            font-weight: 600 !important;
            color: #6B7280 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            margin-bottom: 6px !important;
            display: block !important;
            text-align: right !important;
        }
        
        /* Radio Toggle — Light Segmented Control (target by aria-label for max specificity) */
        div[role="radiogroup"][aria-label="View Mode"] {
            background-color: #f1f5f9 !important;
            background: #f1f5f9 !important;
            padding: 4px !important;
            border-radius: 10px !important;
            display: inline-flex !important;
            gap: 2px !important;
            border: 1px solid #e2e8f0 !important;
        }
        div[data-testid="stRadio"] {
            display: flex !important;
            justify-content: flex-end !important;
        }
        /* Override Streamlit emotion-cache background classes */
        div[role="radiogroup"][aria-label="View Mode"].st-ca,
        div[role="radiogroup"][aria-label="View Mode"].st-cb,
        div[role="radiogroup"][aria-label="View Mode"].st-cc,
        div[role="radiogroup"][aria-label="View Mode"][class*="st-c"] {
            background-color: #f1f5f9 !important;
            background: #f1f5f9 !important;
        }
        section[data-testid="stMain"] div[data-testid="stRadio"] label {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 8px 18px !important;
            margin: 0 !important;
            color: #64748b !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }
        section[data-testid="stMain"] div[data-testid="stRadio"] label:hover {
            color: #1e293b !important;
            background-color: #e8edf3 !important;
        }
        section[data-testid="stMain"] div[data-testid="stRadio"] label[data-checked="true"], 
        section[data-testid="stMain"] div[data-testid="stRadio"] label:has(input:checked) {
            background-color: #ffffff !important;
            color: #1e293b !important;
            font-weight: 600 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04) !important;
        }
        /* Hide radio dot for cleaner look */
        section[data-testid="stMain"] div[data-testid="stRadio"] label > div:first-child {
            display: none !important;
        }

        /* Metric Cards */
        .seo-metric-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-bottom: 1rem;
            border-left: 3px solid #38bdf8; /* default */
            transition: box-shadow 0.2s ease;
        }
        .seo-metric-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .seo-metric-title {
            font-size: 0.875rem;
            color: #475569;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .seo-metric-value-row {
            display: flex;
            align-items: baseline;
            gap: 8px;
        }
        .seo-metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #0f172a;
        }
        .seo-metric-subtext {
            font-size: 0.875rem;
            color: #475569;
        }
        .seo-metric-bottom {
            font-size: 0.8rem;
            color: #94a3b8;
            margin-top: 8px;
        }
        .seo-metric-growth {
            font-size: 0.8rem;
            color: #10b981;
            font-weight: 600;
        }
        
        /* Filter row label */
        .filter-row-label {
            font-size: 12px !important;
            font-weight: 600 !important;
            color: #475569 !important;
            margin-bottom: 4px !important;
            display: block !important;
        }
        
        /* Selectboxes styling */
        div[data-testid="stSelectbox"] > div, div[data-testid="stMultiSelect"] > div {
            background-color: white !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
            min-height: 40px;
        }
        
        .main-header-row {
            padding-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Inject JS to force light theme on View Mode radio (Streamlit strips <script> from st.markdown)
    import streamlit.components.v1 as components
    components.html("""
    <script>
    // Force light theme on View Mode radio toggle
    function fixViewModeRadio() {
        var doc = window.parent.document;
        var rg = doc.querySelector('[role="radiogroup"][aria-label="View Mode"]');
        if (rg) {
            rg.style.setProperty('background-color', '#f1f5f9', 'important');
            rg.style.setProperty('background', '#f1f5f9', 'important');
            rg.style.setProperty('border', '1px solid #e2e8f0', 'important');
            rg.style.setProperty('border-radius', '10px', 'important');
            rg.style.setProperty('padding', '4px', 'important');
            rg.style.setProperty('display', 'inline-flex', 'important');
            rg.style.setProperty('gap', '2px', 'important');
            
            var labels = rg.querySelectorAll('label');
            labels.forEach(function(label) {
                label.style.setProperty('color', '#64748b', 'important');
                label.style.setProperty('background-color', 'transparent', 'important');
                label.style.setProperty('border', 'none', 'important');
                label.style.setProperty('padding', '8px 18px', 'important');
                label.style.setProperty('border-radius', '8px', 'important');
                label.style.setProperty('font-weight', '500', 'important');
                label.style.setProperty('font-size', '0.875rem', 'important');
                label.style.setProperty('cursor', 'pointer', 'important');
                label.style.setProperty('box-shadow', 'none', 'important');
                
                var input = label.querySelector('input[type="radio"]');
                if (input && input.checked) {
                    label.style.setProperty('background-color', '#ffffff', 'important');
                    label.style.setProperty('color', '#1e293b', 'important');
                    label.style.setProperty('font-weight', '600', 'important');
                    label.style.setProperty('box-shadow', '0 1px 3px rgba(0,0,0,0.08)', 'important');
                }
                
                var dot = label.querySelector('div');
                if (dot) dot.style.setProperty('display', 'none', 'important');
            });
        }
    }
    
    fixViewModeRadio();
    setInterval(fixViewModeRadio, 300);
    </script>
    """, height=0)

    # --- 1. Load Data ---
    auth = AuthManager()
    users = auth.users
    
    # Define Eligible Users (HR and Interns)
    eligible_users = [u for u in users.values() if u.role in [Role.HR, Role.INTERN]]
    
    # --- Header Section ---
    st.markdown("<div class='main-header-row'></div>", unsafe_allow_html=True)
    h_col1, h_col2 = st.columns([1, 1], gap="small")
    with h_col1:
        st.markdown("<h1 class='analytics-title'>Analytics <span style='font-size: 1.2rem; color: #cbd5e1; font-weight: normal'>ⓘ</span></h1>", unsafe_allow_html=True)
    with h_col2:
        st.markdown('<span class="view-mode-label" style="text-align: right; padding-right: 5px;">📊 View Mode</span>', unsafe_allow_html=True)
        view_mode = st.radio(
            "View Mode",
            ["All Team", "By Role", "Compare Individuals"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # Filter Row (contextual based on view mode)
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    filtered_users = []
    
    if view_mode == "All Team":
        filtered_users = eligible_users
    elif view_mode == "By Role":
        f_col1, f_col2, _ = st.columns([1.5, 1.5, 4])
        with f_col1:
            st.markdown('<span class="filter-row-label">🏷️ Filter by Role</span>', unsafe_allow_html=True)
            selected_role_filter = st.selectbox("Role", ["Intern", "HR"], label_visibility="collapsed", index=0)
            target_role = Role.INTERN if selected_role_filter == "Intern" else Role.HR
            filtered_users = [u for u in eligible_users if u.role == target_role]
    elif view_mode == "Compare Individuals":
        f_col1, _ = st.columns([3, 5])
        with f_col1:
            if not eligible_users:
                st.warning("No Interns or HRs available.")
            else:
                st.markdown('<span class="filter-row-label">👤 Select team members to compare</span>', unsafe_allow_html=True)
                user_options = {u.username: f"{u.name} ({u.role.value if hasattr(u.role, 'value') else u.role})" for u in eligible_users}
                selected_usernames = st.multiselect(
                    "Compare",
                    options=list(user_options.keys()),
                    format_func=lambda x: user_options[x],
                    label_visibility="collapsed",
                    placeholder="Search by user..."
                )
                filtered_users = [users[u] for u in selected_usernames]

    st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)

    # --- Collect Stats ---
    user_stats = []
    
    for u in filtered_users:
        user_crm_path = os.path.join("crm_data", u.username)
        leads_count = 0
        if os.path.exists(user_crm_path):
            for f in os.listdir(user_crm_path):
                if f.endswith(".json"):
                    try:
                        temp_df = pd.read_json(os.path.join(user_crm_path, f))
                        leads_count += len(temp_df)
                    except:
                        pass
        
        user_stats.append({
            'Name': u.name,
            'Role': u.role.value if hasattr(u.role, 'value') else u.role,
            'Leads Generated': leads_count,
            'Calls Made': 0,
            'Meetings Booked': 0,
            'Deals Closed': 0
        })

    df_perf = pd.DataFrame(user_stats)
    if not df_perf.empty:
        df_perf['Conversion Rate'] = df_perf.apply(
            lambda row: (row['Deals Closed'] / row['Calls Made'] * 100) if row['Calls Made'] > 0 else 0.0, 
            axis=1
        ).round(1)
    else:
        df_perf = pd.DataFrame(columns=['Name', 'Role', 'Leads Generated', 'Calls Made', 'Meetings Booked', 'Deals Closed', 'Conversion Rate'])

    # --- Global Metrics (Always Visible) ---
    try:
        df_master = pd.read_csv("scraped_results.csv")
        total_leads_scraped = len(df_master)
    except:
        total_leads_scraped = 0
        
    total_calls = int(df_perf['Calls Made'].sum()) if not df_perf.empty else 0
    total_meetings = int(df_perf['Meetings Booked'].sum()) if not df_perf.empty else 0
    generated_leads = int(df_perf['Leads Generated'].sum()) if not df_perf.empty else total_leads_scraped
    closed_deals = int(df_perf['Deals Closed'].sum()) if not df_perf.empty else 0

    def metric_card(title, value, metric_name, growth_pct, bottom_text, border_color="#38bdf8", change_color="#10b981", change_icon="↑"):
        return f"""
        <div class="seo-metric-card" style="border-left-color: {border_color}; border-left-width: 4px;">
            <div class="seo-metric-title">{title}</div>
            <div class="seo-metric-value-row">
                <div class="seo-metric-value">{value}</div>
                <div class="seo-metric-subtext">{metric_name} <span style="color:{change_color}; font-weight:500; font-size:0.875rem;">{change_icon} 12</span></div>
            </div>
            <div class="seo-metric-bottom">Growth <span style="color:{change_color}; font-weight:500;">{growth_pct}</span> &nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#64748b'>{bottom_text}</span></div>
        </div>
        """

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(metric_card("Generated Leads", f"{generated_leads:,}", "leads", "↑ 6.04%", "Total sourced prospects", "#3b82f6"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("Total Calls", f"{total_calls:,}", "calls", "↑ 2.5%", "Outbound connect calls", "#8b5cf6"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("Total Meetings", f"{total_meetings:,}", "meetings", "↑ 5.2%", "Demos & pitches booked", "#10b981"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("Closed Deals", f"{closed_deals:,}", "deals", "↑ 1.8%", "Finalized contracts", "#f59e0b"), unsafe_allow_html=True)
    
    # --- Graphs ---
    
    if df_perf.empty:
        if view_mode == "Compare Individuals" and not filtered_users:
            st.info("👋 Select users to see the comparison.")
        else:
            st.info("ℹ️ No data available for the current selection.")
    else:
        # Team Performance Analysis - Activity Summary
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            fig_perf = go.Figure()
            
            fig_perf.add_trace(go.Bar(name='Leads', x=df_perf['Name'], y=df_perf['Leads Generated'], marker_color='#38bdf8'))
            fig_perf.add_trace(go.Bar(name='Calls', x=df_perf['Name'], y=df_perf['Calls Made'], marker_color='#94a3b8'))
            fig_perf.add_trace(go.Bar(name='Meetings', x=df_perf['Name'], y=df_perf['Meetings Booked'], marker_color='#a7f3d0'))
            fig_perf.add_trace(go.Bar(name='Deals', x=df_perf['Name'], y=df_perf['Deals Closed'], marker_color='#fde047'))
            
            fig_perf.update_layout(
                title=dict(text="Team Performance Analysis", font=dict(size=18, color="#1e293b", family="sans-serif"), x=0.01, y=0.95),
                barmode='group',
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="sans-serif", color="#475569"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=50, l=40, r=20, b=40),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
            )
            st.plotly_chart(fig_perf, use_container_width=True)

        with col_right:
            # Success Rate
            fig_rate = px.bar(
                df_perf, 
                x='Conversion Rate', 
                y='Name', 
                orientation='h',
                title='Conversion (%)'
            )
            fig_rate.update_traces(marker_color='#a7f3d0', texttemplate='%{x}%', textposition='outside')
            fig_rate.update_layout(
                title=dict(text="Conversion (%)", font=dict(size=18, color="#1e293b", family="sans-serif"), x=0.01, y=0.95),
                height=450,
                xaxis_range=[0, 100], 
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="sans-serif", color="#475569"),
                margin=dict(t=50, l=150, r=40, b=40),
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, title=None)
            )
            st.plotly_chart(fig_rate, use_container_width=True)

    # --- Trend & Table ---
    st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
    
    current_date = datetime.now().date()
    # Mocking dummy historical data to make the trend look like the SEO alive chart
    dates = [current_date - timedelta(days=x) for x in range(14, -1, -1)]
    base_val = generated_leads if generated_leads > 0 else 20
    leads_trend = [base_val + int(np.sin(x)*base_val*0.2 + np.random.normal(0, base_val*0.1)) for x in range(15)]
    leads_trend = [max(val, 0) for val in leads_trend]
    df_trend = pd.DataFrame({'Date': dates, 'Leads Growth': leads_trend})
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=df_trend['Date'], 
        y=df_trend['Leads Growth'], 
        fill='tozeroy',
        mode='lines+markers',
        line=dict(color='#38bdf8', width=2),
        fillcolor='rgba(56, 189, 248, 0.1)',
        marker=dict(size=6, color='#ffffff', line=dict(color='#38bdf8', width=2))
    ))
    
    # Adding a dashed background trend (like SEO alive Previous Period)
    fig_trend.add_trace(go.Scatter(
        x=df_trend['Date'], 
        y=[val * 0.85 + np.random.normal(0, base_val*0.05) for val in leads_trend], 
        mode='lines+markers',
        line=dict(color='#cbd5e1', width=2, dash='dash'),
        marker=dict(size=4, color='#cbd5e1')
    ))

    fig_trend.update_layout(
        title=dict(text="Lead Generation Performance", font=dict(size=18, color="#1e293b", family="sans-serif"), x=0.01, y=0.95),
        height=400, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        showlegend=False,
        margin=dict(t=50, l=40, r=40, b=40),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False, dtick="D2"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
        hovermode="x unified"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # The detailed data table expander has been hidden as per user request.
