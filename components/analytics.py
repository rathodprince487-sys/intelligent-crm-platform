import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os
from components.auth import AuthManager, Role

CHART_PALETTE = ["#3b82f6", "#94a3b8", "#10b981", "#f59e0b"]

def render_analytics_dashboard():

    # ── CSS ──────────────────────────────────────────────────────────────────
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        [data-testid="stAppViewContainer"] { background-color: #f1f5f9 !important; }
        [data-testid="stAppViewContainer"] *:not([translate="no"]):not(svg):not([class*="material"]):not([icon]) { font-family: 'Inter', sans-serif !important; }

        /* ── Radio group wrapper: override dark theme completely ── */
        section[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            background: #ffffff !important;
            border: 1.5px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 4px !important;
            gap: 2px !important;
            display: inline-flex !important;
            box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
        }
        /* Force every radio label to light style */
        section[data-testid="stMain"] div[data-testid="stRadio"] label {
            background: transparent !important;
            color: #64748b !important;
            font-weight: 500 !important;
            font-size: 0.8125rem !important;
            padding: 7px 20px !important;
            margin: 0 !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            cursor: pointer !important;
            transition: all 0.15s ease !important;
        }
        section[data-testid="stMain"] div[data-testid="stRadio"] label:hover {
            background: #f1f5f9 !important;
            color: #1e293b !important;
        }
        section[data-testid="stMain"] div[data-testid="stRadio"] label:has(input:checked),
        section[data-testid="stMain"] div[data-testid="stRadio"] label[data-checked="true"] {
            background: #3b82f6 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 8px rgba(59,130,246,0.3) !important;
        }
        section[data-testid="stMain"] div[data-testid="stRadio"] label > div:first-child { display: none !important; }

        /* ── Metric Cards ── */
        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 20px 20px 16px 24px;
            position: relative;
            overflow: hidden;
            transition: box-shadow 0.2s ease, transform 0.15s ease;
            height: 100%;
            box-sizing: border-box;
        }
        .metric-card:hover {
            box-shadow: 0 6px 20px rgba(0,0,0,0.07);
            transform: translateY(-2px);
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 4px; height: 100%;
            border-radius: 16px 0 0 16px;
        }
        .mc-blue::before   { background: linear-gradient(180deg,#3b82f6,#6366f1); }
        .mc-indigo::before { background: linear-gradient(180deg,#6366f1,#8b5cf6); }
        .mc-green::before  { background: linear-gradient(180deg,#10b981,#34d399); }
        .mc-amber::before  { background: linear-gradient(180deg,#f59e0b,#fbbf24); }

        .mc-label {
            font-size: 0.6875rem;
            font-weight: 700;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.9px;
            margin: 0 0 12px 0;
        }
        .mc-value-line {
            display: flex;
            align-items: baseline;
            gap: 6px;
            margin-bottom: 14px;
        }
        .mc-number {
            font-size: 2.5rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1;
            letter-spacing: -1.5px;
        }
        .mc-unit {
            font-size: 0.875rem;
            color: #94a3b8;
            font-weight: 500;
        }
        .mc-footer {
            display: flex;
            align-items: center;
            gap: 8px;
            padding-top: 12px;
            border-top: 1px solid #f1f5f9;
        }
        .mc-badge {
            background: #f0fdf4;
            color: #15803d;
            font-size: 0.6875rem;
            font-weight: 700;
            padding: 3px 7px;
            border-radius: 5px;
            white-space: nowrap;
            flex-shrink: 0;
        }
        .mc-foot-text {
            font-size: 0.75rem;
            color: #94a3b8;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* ── Charts ── */
        div[data-testid="stPlotlyChart"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 4px !important;
            box-shadow: none !important;
        }

        /* ── Section headers ── */
        .analytics-divider { height: 1px; background: #e2e8f0; margin: 24px 0 20px 0; }
        .section-label {
            font-size: 0.6875rem;
            font-weight: 700;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.9px;
            margin-bottom: 12px;
        }

        /* ── Selects ── */
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease;
            box-shadow: none !important;
        }
        div[data-baseweb="select"] > div:hover {
            border-color: #94a3b8 !important;
        }
        div[data-baseweb="select"]:focus-within > div {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        }
        /* Make the labels look cleaner too */
        div.stSelectbox label {
            font-family: 'Inter', sans-serif !important;
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            margin-bottom: 2px;
        }

        /* ── Expander ── */
        div[data-testid="stExpander"] details {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # ── Data ─────────────────────────────────────────────────────────────────
    auth = AuthManager()
    users = auth.users
    eligible_users = [u for u in users.values() if u.role in [Role.HR, Role.INTERN]]

    # ── View Mode state ───────────────────────────────────────────────────────
    if "analytics_view" not in st.session_state:
        st.session_state["analytics_view"] = "All Team"

    view_options = ["All Team", "By Role", "Compare Individuals"]

    # ── Header + Toggle ───────────────────────────────────────────────────────
    h1, h2 = st.columns([1.1, 1.3])
    with h1:
        st.markdown("""
<div style="display:flex;flex-direction:column;gap:4px;padding-bottom:4px;">
  <div style="font-size:1.6rem;font-weight:800;color:#0f172a;letter-spacing:-0.5px;font-family:'Inter',sans-serif;">
    📊 Analytics
  </div>
  <div style="font-size:0.875rem;color:#64748b;font-family:'Inter',sans-serif;">
    Team performance &amp; lead generation insights
  </div>
</div>""", unsafe_allow_html=True)

    with h2:
        # Custom light-mode toggle using 3 buttons
        st.markdown("""
<style>
.toggle-wrapper {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-top: 4px;
}
.toggle-group {
    display: inline-flex;
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 3px;
    gap: 2px;
}
/* Style ALL buttons inside the toggle wrapper */
div[data-testid="stHorizontalBlock"] button {
    background: transparent !important;
    color: #64748b !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    padding: 6px 14px !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
    white-space: nowrap !important;
    min-height: 0 !important;
    height: auto !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    background: #e2e8f0 !important;
    color: #1e293b !important;
}
/* Active state overrides - applied via a wrapper data attribute trick */
.btn-active button {
    background: #3b82f6 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(59,130,246,0.3) !important;
}
</style>
""", unsafe_allow_html=True)
        # Render buttons as a horizontal group
        b1, b2, b3 = st.columns([1, 1, 1.5])
        with b1:
            if st.button("All Team", key="vm_all",
                         type="primary" if st.session_state["analytics_view"] == "All Team" else "secondary",
                         use_container_width=True):
                st.session_state["analytics_view"] = "All Team"
                st.rerun()
        with b2:
            if st.button("By Role", key="vm_role",
                         type="primary" if st.session_state["analytics_view"] == "By Role" else "secondary",
                         use_container_width=True):
                st.session_state["analytics_view"] = "By Role"
                st.rerun()
        with b3:
            if st.button("Compare Individuals", key="vm_compare",
                         type="primary" if st.session_state["analytics_view"] == "Compare Individuals" else "secondary",
                         use_container_width=True):
                st.session_state["analytics_view"] = "Compare Individuals"
                st.rerun()

    view_mode = st.session_state["analytics_view"]

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Filters ──────────────────────────────────────────────────────────────
    filtered_users = []
    if view_mode == "All Team":
        filtered_users = eligible_users
    elif view_mode == "By Role":
        fc, _ = st.columns([2, 6])
        with fc:
            sel_role = st.selectbox("Role", ["Intern", "HR"])
            target_role = Role.INTERN if sel_role == "Intern" else Role.HR
            filtered_users = [u for u in eligible_users if u.role == target_role]
    elif view_mode == "Compare Individuals":
        fc, _ = st.columns([3, 5])
        with fc:
            if not eligible_users:
                st.warning("No Interns or HRs available.")
            else:
                user_options = {
                    u.username: f"{u.name} ({u.role.value if hasattr(u.role,'value') else u.role})"
                    for u in eligible_users
                }
                sel_users = st.multiselect(
                    "Select team members", options=list(user_options.keys()),
                    format_func=lambda x: user_options[x],
                    placeholder="Search by user..."
                )
                filtered_users = [users[u] for u in sel_users]

    # ── Global Metrics ────────────────────────────────────────────────────────
    try:
        df_master     = pd.read_csv("scraped_results.csv")
        total_leads   = len(df_master)
    except:
        total_leads = 0

    total_calls = 0
    total_meetings = 0
    total_deals = 0
    
    if os.path.exists("crm_data"):
        for root, dirs, files in os.walk("crm_data"):
            for f in files:
                if f.endswith(".json"):
                    try:
                        df = pd.read_json(os.path.join(root, f))
                        if 'status' in df.columns:
                            statuses = df['status'].dropna().astype(str).str.lower().str.strip()
                            total_calls += len(statuses[(statuses != '') & (statuses != 'new')])
                            total_meetings += len(statuses[statuses.str.contains('meeting')])
                            total_deals += len(statuses[statuses.str.contains('closed')])
                    except:
                        pass

    def mc(label, value, unit, pct, desc, accent):
        return f"""
<div class="metric-card mc-{accent}">
  <div class="mc-label">{label}</div>
  <div class="mc-value-line">
    <span class="mc-number">{value}</span>
    <span class="mc-unit">{unit}</span>
  </div>
  <div class="mc-footer">
    <span class="mc-badge">&#8593; {pct}</span>
    <span class="mc-foot-text">{desc}</span>
  </div>
</div>"""

    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(mc("Total Leads Scraped", f"{total_leads:,}",    "leads",  "6.04%", "Total sourced leads",      "blue"),   unsafe_allow_html=True)
    with c2: st.markdown(mc("Total Calls",         f"{total_calls:,}",    "calls", "3.24%", "From CRM leads",           "indigo"), unsafe_allow_html=True)
    with c3: st.markdown(mc("Total Meeting Set",   f"{total_meetings:,}", "meetings", "8.11%", "Meeting done/set from CRM", "green"),  unsafe_allow_html=True)
    with c4: st.markdown(mc("Total Deal Closed",   f"{total_deals:,}",    "deals",   "2.01%", "Closed monthly deals",    "amber"),  unsafe_allow_html=True)

    # ── Collect User Stats ────────────────────────────────────────────────────
    user_stats = []
    for u in filtered_users:
        crm_path = os.path.join("crm_data", u.username)
        leads_count = 0
        calls_made = 0
        meetings_booked = 0
        deals_closed = 0
        if os.path.exists(crm_path):
            for f in os.listdir(crm_path):
                if f.endswith(".json"):
                    try:
                        tmp = pd.read_json(os.path.join(crm_path, f))
                        leads_count += len(tmp)
                        if 'status' in tmp.columns:
                            statuses = tmp['status'].dropna().astype(str).str.lower().str.strip()
                            calls_made += len(statuses[(statuses != '') & (statuses != 'new')])
                            meetings_booked += len(statuses[statuses.str.contains('meeting')])
                            deals_closed += len(statuses[statuses.str.contains('closed')])
                    except:
                        pass
        user_stats.append({
            'Name': u.name,
            'Role': u.role.value if hasattr(u.role, 'value') else u.role,
            'Leads Generated': leads_count,
            'Calls Made': calls_made,
            'Meetings Booked': meetings_booked,
            'Deals Closed': deals_closed
        })

    df_perf = pd.DataFrame(user_stats)
    if not df_perf.empty:
        df_perf['Conversion Rate'] = df_perf.apply(
            lambda r: (r['Deals Closed'] / r['Calls Made'] * 100) if r['Calls Made'] > 0 else 0.0,
            axis=1
        ).round(1)
    else:
        df_perf = pd.DataFrame(columns=['Name','Role','Leads Generated','Calls Made','Meetings Booked','Deals Closed','Conversion Rate'])

    # Shared layout base (NO margin key here)
    def base_layout(**extra):
        d = dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", color="#64748b", size=12),
        )
        d.update(extra)
        return d

    # ── Team Performance Charts ───────────────────────────────────────────────
    st.markdown("<div class='analytics-divider'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Team Performance</div>', unsafe_allow_html=True)

    if df_perf.empty:
        if view_mode == "Compare Individuals" and not filtered_users:
            st.info("👋 Select team members above to compare their performance.")
        else:
            st.info("ℹ️ No data available for the current selection.")
    else:
        cl, cr = st.columns([3, 2])

        with cl:
            fig = go.Figure()
            for label, col, color in [
                ("Leads",    "Leads Generated",  CHART_PALETTE[0]),
                ("Calls",    "Calls Made",        CHART_PALETTE[1]),
                ("Meetings", "Meetings Booked",   CHART_PALETTE[2]),
                ("Deals",    "Deals Closed",      CHART_PALETTE[3]),
            ]:
                fig.add_trace(go.Bar(
                    name=label, x=df_perf['Name'], y=df_perf[col],
                    marker_color=color, marker_line_width=0,
                ))
            fig.update_layout(
                **base_layout(),
                title=dict(text="Activity Breakdown", font=dict(size=15, color="#0f172a", weight=700), x=0.01, y=0.97),
                barmode='group', height=370, bargap=0.3, bargroupgap=0.06,
                margin=dict(t=55, l=10, r=10, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=13, color="#334155")),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont=dict(size=11)),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with cr:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_perf['Conversion Rate'],
                y=df_perf['Name'],
                orientation='h',
                marker_color=CHART_PALETTE[0],
                marker_line_width=0,
                text=[f"{v:.1f}%" for v in df_perf['Conversion Rate']],
                textposition='outside',
                textfont=dict(size=13, color="#0f172a"),
                width=0.4
            ))
            
            max_conv = df_perf['Conversion Rate'].max() if not df_perf.empty else 0
            x_max = max(max_conv * 1.25, 10)
            
            fig2.update_layout(
                **base_layout(),
                title=dict(text="Conversion Rate", font=dict(size=15, color="#0f172a", weight=700), x=0.01, y=0.97),
                height=370,
                margin=dict(t=55, l=10, r=60, b=30),
                xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, x_max]),
                yaxis=dict(showgrid=False, zeroline=False, title=None, tickfont=dict(size=13, color="#334155"), autorange="reversed"),
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Lead Generation Trend ─────────────────────────────────────────────────
    st.markdown("<div class='analytics-divider'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Lead Generation Trend</div>', unsafe_allow_html=True)

    today = datetime.now().date()
    dates = [today - timedelta(days=x) for x in range(14, -1, -1)]
    base  = total_leads if total_leads > 0 else 20
    np.random.seed(42)
    y1 = [max(base + int(np.sin(x) * base * 0.2 + np.random.normal(0, base * 0.1)), 0) for x in range(15)]
    y2 = [max(int(v * 0.85 + np.random.normal(0, base * 0.05)), 0) for v in y1]

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=dates, y=y1, name='Current Period',
        fill='tozeroy', mode='lines+markers',
        line=dict(color=CHART_PALETTE[0], width=2.5),
        fillcolor='rgba(59,130,246,0.07)',
        marker=dict(size=6, color='#ffffff', line=dict(color=CHART_PALETTE[0], width=2)),
    ))
    fig3.add_trace(go.Scatter(
        x=dates, y=y2, name='Previous Period',
        mode='lines+markers',
        line=dict(color='#cbd5e1', width=2, dash='dot'),
        marker=dict(size=4, color='#cbd5e1'),
    ))
    fig3.update_layout(
        **base_layout(),
        height=340,
        margin=dict(t=40, l=10, r=10, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor="#f8fafc", zeroline=False, dtick="D2", tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="#f8fafc", zeroline=False, tickfont=dict(size=12)),
        hovermode="x unified"
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})

    # ── Data Table ────────────────────────────────────────────────────────────
    with st.expander("📋  Detailed Data Table"):
        if not df_perf.empty:
            try:
                import matplotlib
                st.dataframe(
                    df_perf.style.format({'Conversion Rate': '{:.1f}%'})
                    .background_gradient(subset=['Conversion Rate'], cmap='Blues', vmin=0, vmax=100),
                    use_container_width=True
                )
            except:
                st.dataframe(df_perf, use_container_width=True)
        else:
            st.info("No data available.")
