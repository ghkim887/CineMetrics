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
first_name = st.session_state.get('first_name', 'Priya')

st.title(f'Welcome back, {first_name}!')
st.write('#### Your Movie Enthusiast Dashboard')
st.write('')

# ---- Stats Section ----
st.subheader('Your Activity at a Glance')

stats = {}
try:
    resp = requests.get(f'{API_BASE}/users/{user_id}/stats', timeout=5)
    if resp.status_code == 200:
        stats = resp.json() or {}
    else:
        st.info('Stats are not available right now.')
except Exception as e:
    st.error(f'Could not fetch stats: {e}')

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('Reviews Written', stats.get('total_reviews', 0))
with col2:
    st.metric('Ratings Given', stats.get('total_ratings', 0))
with col3:
    avg = stats.get('average_rating_given')
    st.metric('Average Rating', f'{float(avg):.2f}' if avg is not None else '—')
with col4:
    st.metric('Movies Watched', stats.get('total_movies_watched', 0))

st.write('---')

# ---- Quick Access ----
st.subheader('Jump back in')
c1, c2, c3 = st.columns(3)
with c1:
    if st.button('Write a Review', use_container_width=True, type='primary'):
        st.switch_page('pages/11_Write_Review.py')
    if st.button('My Stats', use_container_width=True):
        st.switch_page('pages/12_My_Stats.py')
with c2:
    if st.button('Similar Movies', use_container_width=True, type='primary'):
        st.switch_page('pages/13_Similar_Movies.py')
    if st.button('Advanced Browse', use_container_width=True):
        st.switch_page('pages/14_Advanced_Browse.py')
with c3:
    if st.button('Read Reviews', use_container_width=True, type='primary'):
        st.switch_page('pages/15_Read_Reviews.py')
    if st.button('Manage My Reviews', use_container_width=True):
        st.switch_page('pages/16_Manage_Reviews.py')
