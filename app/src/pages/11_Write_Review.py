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

st.title('Write a Review')
st.write('Share your thoughts on a movie you\'ve seen.')

# ---- Load movies ----
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

# ---- Review form ----
with st.form('review_form', clear_on_submit=True):
    st.subheader('New Review')

    if movie_options:
        selected_label = st.selectbox('Movie', list(movie_options.keys()))
        movie_id = movie_options[selected_label]
    else:
        st.warning('No movies available right now.')
        movie_id = None

    review_title = st.text_input('Review Title', max_chars=200)
    review_body = st.text_area('Your Review', height=250,
                               placeholder='What did you think? Share your perspective.')

    submitted = st.form_submit_button('Submit Review', type='primary', use_container_width=True)

    if submitted:
        if not movie_id:
            st.error('Please select a movie.')
        elif not review_title.strip():
            st.error('Please add a title.')
        elif not review_body.strip():
            st.error('Please write something before submitting.')
        else:
            payload = {
                'user_id': user_id,
                'movie_id': movie_id,
                'review_title': review_title.strip(),
                'review_body': review_body.strip(),
            }
            try:
                r = requests.post(f'{API_BASE}/reviews/', json=payload, timeout=5)
                if r.status_code in (200, 201):
                    st.success('Your review has been posted!')
                else:
                    st.error(f'Failed to post review (status {r.status_code}): {r.text}')
            except Exception as e:
                st.error(f'Could not post review: {e}')

st.write('---')

# ---- Recent reviews ----
st.subheader('Your Recent Reviews')
try:
    r = requests.get(f'{API_BASE}/reviews/', params={'user_id': user_id}, timeout=5)
    if r.status_code == 200:
        recent = r.json() or []
        if not recent:
            st.info('You haven\'t written any reviews yet.')
        for rev in recent[:5]:
            with st.container(border=True):
                st.markdown(f"**{rev.get('review_title', 'Untitled')}**  \n"
                            f"*{rev.get('movie_title', '')}* — {rev.get('review_date', '')}")
                st.write(rev.get('review_body', ''))
    else:
        st.info('Recent reviews unavailable.')
except Exception as e:
    st.error(f'Could not load recent reviews: {e}')
