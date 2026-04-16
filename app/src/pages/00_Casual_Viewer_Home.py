##################################################
# Casual Viewer Home - Jake Morrison's Dashboard
##################################################

import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Require authentication
if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)
first_name = st.session_state.get('first_name', 'Jake')

# ---- Welcome header ----
st.title(f'Welcome back, {first_name}! 🎬')
st.write('#### Your personal movie dashboard')
st.write('')

# ---- Quick stats ----
st.subheader('Your Stats')

try:
    with st.spinner('Loading your stats...'):
        resp = requests.get(f'{API_BASE}/users/{user_id}/stats', timeout=5)

    if resp.status_code == 200:
        stats = resp.json() or {}

        # Separate call to get watchlist count
        watchlist_count = 0
        try:
            wl_resp = requests.get(f'{API_BASE}/watchlists/user/{user_id}', timeout=5)
            if wl_resp.status_code == 200:
                watchlist_count = len(wl_resp.json() or [])
        except requests.exceptions.RequestException:
            pass

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric('In Watchlist', watchlist_count)
        with col2:
            st.metric('Watched', stats.get('total_movies_watched', 0))
        with col3:
            st.metric('Rated', stats.get('total_ratings', 0))
        with col4:
            avg = stats.get('average_rating_given')
            st.metric('Avg Rating', f"{float(avg):.1f}" if avg is not None else '—')
    else:
        st.info(f'Could not load stats (status {resp.status_code})')
except requests.exceptions.RequestException as e:
    st.error(f'Unable to reach API: {e}')

st.write('---')

# ---- Feature buttons ----
st.subheader('What would you like to do?')

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button('🎬 Browse Movies', use_container_width=True, type='primary'):
        st.switch_page('pages/01_Browse_Movies.py')

with col2:
    if st.button('⭐ My Recommendations', use_container_width=True, type='primary'):
        st.switch_page('pages/02_My_Recommendations.py')

with col3:
    if st.button('📋 My Watchlist', use_container_width=True, type='primary'):
        st.switch_page('pages/04_My_Watchlist.py')

with col4:
    if st.button('🌟 Rate a Movie', use_container_width=True, type='primary'):
        st.switch_page('pages/05_Rate_Movie.py')

st.write('')
st.write('---')
st.caption('CineMetrics - Your movie journey starts here.')
