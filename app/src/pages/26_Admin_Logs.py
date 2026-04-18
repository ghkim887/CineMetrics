import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title('Admin Audit Logs')
st.write('#### Recent administrative actions on the platform')
st.write('')

# ---- Filters ----
c1, c2 = st.columns([1, 1])
with c1:
    action_filter = st.selectbox(
        'Filter by action_type',
        [
            'all',
            'update_user_status',
            'moderate_review',
        ],
        index=0,
    )
with c2:
    limit = st.number_input(
        'Limit', min_value=10, max_value=500, value=100, step=10
    )

params = {'limit': int(limit)}
if action_filter != 'all':
    params['action_type'] = action_filter

logs = []
try:
    r = requests.get(f'{API_BASE}/admin/logs', params=params, timeout=5)
    if r.status_code == 200:
        logs = r.json() or []
    else:
        st.error(f'Could not load logs: {r.status_code}')
except Exception as e:
    st.error(f'Could not load logs: {e}')

st.write(f'Showing {len(logs)} log entries')

if logs:
    df = pd.DataFrame([{
        'log_id': l.get('log_id'),
        'action_type': l.get('action_type'),
        'target_table': l.get('target_table'),
        'target_id': l.get('target_id'),
        'action_timestamp': l.get('action_timestamp'),
        'admin_username': l.get('admin_username'),
        'notes': l.get('notes'),
    } for l in logs])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info('No log entries found.')
