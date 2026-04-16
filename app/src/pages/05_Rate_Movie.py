##################################################
# Rate Movie - Story Jake-5
##################################################

import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Require authentication
if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title('Rate a Movie 🌟')
st.write('Share how much you enjoyed a movie.')
st.write('')

# ---- Fetch movie options ----
movies = []
try:
    with st.spinner('Loading movies...'):
        movies_resp = requests.get(f'{API_BASE}/movies/', timeout=10)
    if movies_resp.status_code == 200:
        movies = movies_resp.json() or []
except requests.exceptions.RequestException as e:
    st.error(f'Unable to reach API: {e}')

movie_map = {}
for m in movies:
    mid = m.get('movie_id') or m.get('id')
    title = m.get('title', 'Untitled')
    year = m.get('release_year') or m.get('year') or ''
    label = f"{title} ({year})" if year else title
    if mid is not None:
        movie_map[label] = mid

# ---- Rating form ----
st.subheader('Submit Rating')

if not movie_map:
    st.info('No movies available to rate.')
else:
    with st.form('rate_form'):
        sel_label = st.selectbox('Movie', list(movie_map.keys()))
        rating = st.slider('Your rating', 0.0, 10.0, 7.0, 0.1)
        submitted = st.form_submit_button('Submit Rating', type='primary', use_container_width=True)

        if submitted:
            payload = {
                'movie_id': movie_map[sel_label],
                'rating_value': rating,
            }
            try:
                with st.spinner('Submitting...'):
                    resp = requests.post(
                        f'{API_BASE}/users/{user_id}/ratings',
                        json=payload,
                        timeout=10
                    )
                if resp.status_code in (200, 201):
                    st.success(f'You rated "{sel_label}" {rating}/10!')
                    st.rerun()
                else:
                    st.error(f'Failed to submit (status {resp.status_code}): {resp.text}')
            except requests.exceptions.RequestException as e:
                st.error(f'Unable to reach API: {e}')

st.write('---')

# ---- Recent ratings ----
st.subheader('Your Recent Ratings')

try:
    with st.spinner('Loading your ratings...'):
        r_resp = requests.get(f'{API_BASE}/users/{user_id}/ratings', timeout=10)
    if r_resp.status_code == 200:
        ratings = r_resp.json() or []
        if not ratings:
            st.info('You haven\'t rated any movies yet.')
        else:
            df = pd.DataFrame(ratings)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning(f'Could not load ratings (status {r_resp.status_code})')
except requests.exceptions.RequestException as e:
    st.error(f'Unable to reach API: {e}')
