##################################################
# Watch History - Story Jake-3
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

st.title('Watch History 📺')
st.write('Keep track of what you\'ve watched.')
st.write('')

# ---- Fetch watch history ----
st.subheader('Your History')

try:
    with st.spinner('Loading history...'):
        hist_resp = requests.get(f'{API_BASE}/users/{user_id}/history', timeout=10)

    if hist_resp.status_code == 200:
        history = hist_resp.json() or []
        if not history:
            st.info('You haven\'t watched any movies yet. Add one below!')
        else:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning(f'Could not load history (status {hist_resp.status_code})')
except requests.exceptions.RequestException as e:
    st.error(f'Unable to reach API: {e}')

st.write('---')

# ---- Mark new as watched ----
st.subheader('Mark a Movie as Watched')

# Fetch movie options
movies = []
try:
    with st.spinner('Loading movies...'):
        movies_resp = requests.get(f'{API_BASE}/movies/', timeout=10)
    if movies_resp.status_code == 200:
        movies = movies_resp.json() or []
except requests.exceptions.RequestException as e:
    st.error(f'Unable to reach API for movie list: {e}')

if not movies:
    st.info('No movies available to select. Check the API connection.')
else:
    # map display -> movie_id
    movie_map = {}
    for m in movies:
        mid = m.get('movie_id') or m.get('id')
        title = m.get('title', 'Untitled')
        year = m.get('release_year') or m.get('year') or ''
        label = f"{title} ({year})" if year else title
        if mid is not None:
            movie_map[label] = mid

    with st.form('mark_watched_form'):
        selected_label = st.selectbox('Movie', list(movie_map.keys()))
        status = st.selectbox('Completion status', ['completed', 'in_progress', 'abandoned'])
        submitted = st.form_submit_button('Submit', type='primary', use_container_width=True)

        if submitted:
            movie_id = movie_map[selected_label]
            payload = {'movie_id': movie_id, 'completion_status': status}
            try:
                with st.spinner('Saving...'):
                    post_resp = requests.post(
                        f'{API_BASE}/users/{user_id}/history',
                        json=payload,
                        timeout=10
                    )
                if post_resp.status_code in (200, 201):
                    st.success(f'Marked "{selected_label}" as {status}!')
                    st.rerun()
                else:
                    st.error(f'Failed to save (status {post_resp.status_code}): {post_resp.text}')
            except requests.exceptions.RequestException as e:
                st.error(f'Unable to reach API: {e}')
