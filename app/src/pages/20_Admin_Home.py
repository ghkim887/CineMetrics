import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)
first_name = st.session_state.get('first_name', 'Marcus')

st.title(f'Welcome, {first_name}')
st.write('#### Platform Admin Dashboard')
st.write('')

# ---- Stats Section ----
st.subheader('Platform at a Glance')

total_movies = 0
total_users = 0
total_flagged = 0

try:
    r = requests.get(f'{API_BASE}/movies/', timeout=5)
    if r.status_code == 200:
        total_movies = len(r.json() or [])
except Exception as e:
    st.error(f'Could not fetch movies: {e}')

try:
    r = requests.get(f'{API_BASE}/admin/users', timeout=5)
    if r.status_code == 200:
        total_users = len(r.json() or [])
except Exception as e:
    st.error(f'Could not fetch users: {e}')

try:
    r = requests.get(f'{API_BASE}/admin/reviews/flagged', timeout=5)
    if r.status_code == 200:
        total_flagged = len(r.json() or [])
except Exception as e:
    st.error(f'Could not fetch flagged reviews: {e}')

c1, c2, c3 = st.columns(3)
with c1:
    st.metric('Total Movies', total_movies)
with c2:
    st.metric('Total Users', total_users)
with c3:
    st.metric('Flagged Reviews', total_flagged)

st.write('---')

# ---- Quick Access ----
st.subheader('Admin Actions')

c1, c2, c3 = st.columns(3)
with c1:
    if st.button('Add Movie', use_container_width=True, type='primary'):
        st.switch_page('pages/21_Add_Movie.py')
    if st.button('Edit Movie', use_container_width=True):
        st.switch_page('pages/22_Edit_Movie.py')
with c2:
    if st.button('Manage Movies', use_container_width=True, type='primary'):
        st.switch_page('pages/23_Manage_Movies.py')
    if st.button('Moderate Reviews', use_container_width=True):
        st.switch_page('pages/24_Moderate_Reviews.py')
with c3:
    if st.button('Manage Users', use_container_width=True, type='primary'):
        st.switch_page('pages/25_Manage_Users.py')
    if st.button('View Admin Logs', use_container_width=True):
        st.switch_page('pages/26_Admin_Logs.py')
