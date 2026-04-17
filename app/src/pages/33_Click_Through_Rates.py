import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title("Click-Through Rates")
st.write("Recommendation engagement broken down by user role.")
st.write('---')

try:
    resp = requests.get(f"{API_BASE}/analytics/click-through-rates", timeout=15)
    if resp.status_code != 200:
        st.error(f"API error: {resp.status_code} - {resp.text}")
        st.stop()
    payload = resp.json()
except Exception as e:
    st.error(f"Failed to reach API: {e}")
    st.stop()

if isinstance(payload, dict) and 'roles' in payload:
    rows = payload['roles']
elif isinstance(payload, list):
    rows = payload
else:
    rows = []

if not rows:
    st.info("No CTR data available.")
    st.stop()

df = pd.DataFrame(rows)

# Expected columns: role, total_recs, total_clicks, ctr_pct
role_col = next((c for c in ['role', 'user_role'] if c in df.columns), df.columns[0])
recs_col = next((c for c in ['total_recs', 'recs', 'recommendations'] if c in df.columns), None)
clicks_col = next((c for c in ['total_clicks', 'clicks'] if c in df.columns), None)
ctr_col = next((c for c in ['ctr_pct', 'ctr', 'click_through'] if c in df.columns), None)

total_recs_sum = int(df[recs_col].sum()) if recs_col else 0
total_clicks_sum = int(df[clicks_col].sum()) if clicks_col else 0

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Recommendations", f"{total_recs_sum:,}")
with c2:
    st.metric("Total Clicks", f"{total_clicks_sum:,}")
with c3:
    overall_ctr = (total_clicks_sum / total_recs_sum * 100) if total_recs_sum else 0
    st.metric("Overall CTR", f"{overall_ctr:.2f}%")

st.subheader("Breakdown by Role")
st.dataframe(df, use_container_width=True)

if ctr_col:
    fig = px.bar(
        df,
        x=role_col,
        y=ctr_col,
        labels={role_col: "Role", ctr_col: "CTR (%)"},
        title="Click-Through Rate by Role",
        text=ctr_col,
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(template='plotly_dark', height=500)
    st.plotly_chart(fig, use_container_width=True)
