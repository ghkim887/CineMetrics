##################################################
# My Recommendations - Story Jake-2
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

st.title('My Recommendations ⭐')
st.write('Personalized movie picks based on what you like.')
st.write('')

# ---- Track dismissed recs in session state ----
if 'dismissed_recs' not in st.session_state:
    st.session_state['dismissed_recs'] = set()

# ---- Generate new recs button ----
col_left, col_right = st.columns([3, 1])
with col_right:
    if st.button('🔄 Generate New', use_container_width=True, type='primary'):
        try:
            with st.spinner('Generating new recommendations...'):
                gen_resp = requests.get(
                    f'{API_BASE}/recommendations/generate/{user_id}',
                    timeout=15
                )
            if gen_resp.status_code == 200:
                st.session_state['dismissed_recs'] = set()
                st.success('New recommendations generated!')
                st.rerun()
            else:
                st.error(f'Failed to generate (status {gen_resp.status_code})')
        except requests.exceptions.RequestException as e:
            st.error(f'Unable to reach API: {e}')

st.write('---')

# ---- Fetch recs ----
try:
    with st.spinner('Loading recommendations...'):
        resp = requests.get(f'{API_BASE}/users/{user_id}/recommendations', timeout=10)

    if resp.status_code == 200:
        recs = resp.json() or []
        # filter dismissed
        recs = [r for r in recs if r.get('recommendation_id', r.get('movie_id')) not in st.session_state['dismissed_recs']]

        if not recs:
            st.info('No recommendations available. Try generating new ones!')
        else:
            st.write(f'**{len(recs)} recommendation(s) for you:**')
            st.write('')

            # ---- Render rec cards in grid ----
            cols_per_row = 2
            for i in range(0, len(recs), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(recs):
                        r = recs[i + j]
                        rec_key = r.get('recommendation_id', r.get('movie_id', f'rec_{i+j}'))
                        with col:
                            with st.container(border=True):
                                title = r.get('title', 'Untitled')
                                year = r.get('release_year') or r.get('year') or 'N/A'
                                score = r.get('recommendation_score') or 0
                                reason = r.get('reason') or r.get('explanation') or 'Matches your taste.'

                                st.markdown(f"### {title}")
                                st.caption(f"**Year:** {year}  |  **Score:** {float(score):.2f}")
                                st.write(f"**Why:** {reason}")

                                if st.button(
                                    'Not interested',
                                    key=f'dismiss_{rec_key}',
                                    use_container_width=True
                                ):
                                    st.session_state['dismissed_recs'].add(rec_key)
                                    st.rerun()
    else:
        st.error(f'Failed to load recommendations (status {resp.status_code})')
except requests.exceptions.RequestException as e:
    st.error(f'Unable to reach API: {e}')
