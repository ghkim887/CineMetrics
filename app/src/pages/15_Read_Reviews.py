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

st.title('Read Reviews')
st.write('See what other movie enthusiasts are saying.')

# ---- Movie selector ----
movies = []
try:
    resp = requests.get(f'{API_BASE}/movies/', timeout=5)
    if resp.status_code == 200:
        movies = resp.json() or []
    else:
        st.error(f'Failed to load movies (status {resp.status_code})')
except Exception as e:
    st.error(f'Could not fetch movies: {e}')

movie_options = {
    f"{m.get('title', 'Untitled')} ({m.get('release_year', 'N/A')})": m.get('movie_id')
    for m in movies
}

if not movie_options:
    st.info('No movies available right now.')
    st.stop()

selected_label = st.selectbox('Select a movie:', list(movie_options.keys()))
selected_id = movie_options[selected_label]

# ---- Reviews ----
if selected_id:
    reviews = []
    try:
        resp = requests.get(f'{API_BASE}/movies/{selected_id}/reviews', timeout=5)
        if resp.status_code == 200:
            reviews = resp.json() or []
        else:
            st.error(f'Failed to load reviews (status {resp.status_code})')
    except Exception as e:
        st.error(f'Could not fetch reviews: {e}')

    st.write('---')
    st.subheader(f'Reviews for {selected_label}')

    if not reviews:
        st.info('No reviews yet for this movie. Be the first to write one!')
    else:
        for rev in reviews:
            with st.container(border=True):
                header_col, date_col = st.columns([3, 1])
                with header_col:
                    st.markdown(f"### {rev.get('review_title', 'Untitled')}")
                    username = rev.get('username') or rev.get('user_name') or 'Anonymous'
                    st.caption(f"by **{username}**")
                with date_col:
                    st.caption(f"{rev.get('review_date', '')}")
                st.write(rev.get('review_body', ''))
