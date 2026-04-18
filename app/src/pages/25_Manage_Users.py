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

st.title('Manage Users')
st.write('#### Update account status for platform users')
st.write('')

# ---- Filters ----
c1, c2 = st.columns(2)
with c1:
    role_filter = st.selectbox(
        'Filter by role',
        ['all', 'casual', 'enthusiast', 'admin', 'analyst'],
        index=0,
    )
with c2:
    status_filter = st.selectbox(
        'Filter by status',
        ['all', 'active', 'inactive', 'banned'],
        index=0,
    )

params = {}
if role_filter != 'all':
    params['role'] = role_filter
if status_filter != 'all':
    params['status'] = status_filter

users = []
try:
    r = requests.get(f'{API_BASE}/admin/users', params=params, timeout=5)
    if r.status_code == 200:
        users = r.json() or []
    else:
        st.error(f'Could not load users: {r.status_code}')
except Exception as e:
    st.error(f'Could not load users: {e}')

st.write(f'Showing {len(users)} users')

# ---- Summary table ----
if users:
    df = pd.DataFrame([{
        'user_id': u.get('user_id'),
        'username': u.get('username'),
        'email': u.get('email'),
        'role': u.get('role'),
        'status': u.get('status'),
        'join_date': u.get('join_date'),
    } for u in users])
    st.dataframe(df, use_container_width=True, hide_index=True)

st.write('---')

# ---- Per-user status update ----
st.subheader('Update User Status')

if not users:
    st.info('No users to manage with the current filters.')
    st.stop()

STATUS_OPTIONS = ['active', 'inactive', 'banned']

for u in users:
    uid = u.get('user_id')
    current_status = u.get('status') or 'active'
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.markdown(
                f"**{u.get('username','(no username)')}** "
                f"({u.get('role','?')}) - id {uid}"
            )
            st.caption(f"{u.get('email','')} | current status: {current_status}")
        with c2:
            try:
                default_idx = STATUS_OPTIONS.index(current_status)
            except ValueError:
                default_idx = 0
            new_status = st.selectbox(
                'New status',
                STATUS_OPTIONS,
                index=default_idx,
                key=f'status_{uid}',
            )
        with c3:
            st.write('')
            st.write('')
            if st.button('Update', key=f'update_{uid}', type='primary',
                         use_container_width=True):
                payload = {
                    'status': new_status,
                    'admin_user_id': user_id,
                }
                try:
                    r = requests.put(
                        f'{API_BASE}/admin/users/{uid}',
                        json=payload,
                        timeout=10,
                    )
                    if r.status_code == 200:
                        st.success(
                            f'User {uid} status updated to {new_status}.'
                        )
                        st.rerun()
                    else:
                        st.error(f'Failed: {r.status_code} - {r.text}')
                except Exception as e:
                    st.error(f'Request failed: {e}')
