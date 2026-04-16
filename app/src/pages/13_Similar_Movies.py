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

st.title('Find Similar Movies')
st.write('Pick a movie you love and we\'ll surface others with a similar vibe.')

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

selected_label = st.selectbox('Start with a movie:', list(movie_options.keys()))
selected_id = movie_options[selected_label]

# ---- Similar movies ----
if selected_id:
    similar = []
    try:
        resp = requests.get(f'{API_BASE}/movies/{selected_id}/similar', timeout=5)
        if resp.status_code == 200:
            similar = resp.json() or []
        else:
            st.error(f'Failed to load similar movies (status {resp.status_code})')
    except Exception as e:
        st.error(f'Could not fetch similar movies: {e}')

    st.write('---')
    st.subheader(f'Movies similar to {selected_label}')

    if not similar:
        st.info('No similar movies found for this title.')
    else:
        for i in range(0, len(similar), 3):
            cols = st.columns(3)
            for j, movie in enumerate(similar[i:i + 3]):
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"### {movie.get('title', 'Untitled')}")
                        st.caption(f"Released: {movie.get('release_year', 'N/A')}")
                        rating = movie.get('average_rating')
                        if rating is not None:
                            st.write(f"**Rating:** {float(rating):.1f} / 10")
                        shared = movie.get('shared_genres') or movie.get('genres') or []
                        if shared:
                            if isinstance(shared, list):
                                genre_names = ', '.join(
                                    g['genre_name'] if isinstance(g, dict) else str(g) for g in shared
                                )
                                st.write(f"**Shared genres:** {genre_names}")
                            else:
                                label = shared['genre_name'] if isinstance(shared, dict) else str(shared)
                                st.write(f"**Shared genres:** {label}")
