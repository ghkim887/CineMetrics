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

st.title('Add New Movie')
st.write('#### Add a new film to the CineMetrics catalog')
st.write('')

# Known genres from seed data (Genre table ids 1-15)
GENRES = [
    (1, 'Action'), (2, 'Comedy'), (3, 'Drama'), (4, 'Horror'),
    (5, 'Sci-Fi'), (6, 'Romance'), (7, 'Thriller'), (8, 'Documentary'),
    (9, 'Animation'), (10, 'Fantasy'), (11, 'Mystery'), (12, 'Adventure'),
    (13, 'Crime'), (14, 'Musical'), (15, 'Western'),
]
GENRE_NAME_TO_ID = {name: gid for gid, name in GENRES}

with st.form('add_movie_form', clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input('Title *')
        release_year = st.number_input(
            'Release Year *', min_value=1880, max_value=2100, value=2024, step=1
        )
        runtime_minutes = st.number_input(
            'Runtime (minutes)', min_value=0, max_value=600, value=100, step=1
        )
    with c2:
        country_of_origin = st.text_input('Country of Origin', value='USA')
        language = st.text_input('Language', value='English')
        genre_names = st.multiselect(
            'Genres', options=[name for _, name in GENRES]
        )

    synopsis = st.text_area('Synopsis', height=150)

    submitted = st.form_submit_button('Add Movie', type='primary')

if submitted:
    if not title:
        st.error('Title is required.')
    else:
        payload = {
            'title': title,
            'release_year': int(release_year),
            'runtime_minutes': int(runtime_minutes) if runtime_minutes else None,
            'synopsis': synopsis or None,
            'country_of_origin': country_of_origin or None,
            'language': language or None,
            'genre_ids': [GENRE_NAME_TO_ID[n] for n in genre_names],
        }
        try:
            r = requests.post(f'{API_BASE}/movies/', json=payload, timeout=10)
            if r.status_code in (200, 201):
                body = r.json()
                st.success(
                    f"Movie added successfully! New movie_id: "
                    f"{body.get('movie_id', 'unknown')}"
                )
            else:
                st.error(f'Failed to add movie: {r.status_code} - {r.text}')
        except Exception as e:
            st.error(f'Request failed: {e}')
