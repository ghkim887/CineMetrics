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

st.title('Edit Movie Metadata')
st.write('#### Update catalog info for an existing movie')
st.write('')

# ---- Load movie list ----
movies = []
try:
    r = requests.get(f'{API_BASE}/movies/', timeout=5)
    if r.status_code == 200:
        movies = r.json() or []
    else:
        st.error(f'Could not load movies: {r.status_code}')
except Exception as e:
    st.error(f'Could not load movies: {e}')

if not movies:
    st.info('No movies available to edit.')
    st.stop()

# Build selectbox options
option_map = {
    f"{m['title']} ({m.get('release_year','?')}) [id={m['movie_id']}]": m['movie_id']
    for m in movies
}
selection = st.selectbox('Select a movie to edit', list(option_map.keys()))
selected_id = option_map[selection]

# ---- Load full detail for that movie ----
movie = None
try:
    r = requests.get(f'{API_BASE}/movies/{selected_id}', timeout=5)
    if r.status_code == 200:
        movie = r.json()
    else:
        st.error(f'Could not load movie detail: {r.status_code}')
except Exception as e:
    st.error(f'Could not load movie detail: {e}')

if not movie:
    st.stop()

st.write('---')

with st.form('edit_movie_form'):
    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input('Title', value=movie.get('title') or '')
        release_year = st.number_input(
            'Release Year',
            min_value=1880, max_value=2100,
            value=int(movie.get('release_year') or 2024), step=1,
        )
        runtime_minutes = st.number_input(
            'Runtime (minutes)',
            min_value=0, max_value=600,
            value=int(movie.get('runtime_minutes') or 0), step=1,
        )
    with c2:
        country_of_origin = st.text_input(
            'Country of Origin', value=movie.get('country_of_origin') or ''
        )
        language = st.text_input(
            'Language', value=movie.get('language') or ''
        )
        status_options = ['active', 'flagged', 'removed']
        current_status = movie.get('status') or 'active'
        if current_status not in status_options:
            status_options.append(current_status)
        status = st.selectbox(
            'Status',
            status_options,
            index=status_options.index(current_status),
        )

    synopsis = st.text_area(
        'Synopsis', value=movie.get('synopsis') or '', height=150
    )

    submitted = st.form_submit_button('Save Changes', type='primary')

if submitted:
    payload = {
        'title': title,
        'release_year': int(release_year),
        'runtime_minutes': int(runtime_minutes) if runtime_minutes else None,
        'synopsis': synopsis or None,
        'country_of_origin': country_of_origin or None,
        'language': language or None,
        'status': status,
    }
    try:
        r = requests.put(
            f'{API_BASE}/movies/{selected_id}', json=payload, timeout=10
        )
        if r.status_code == 200:
            st.success('Movie updated successfully.')
        else:
            st.error(f'Failed to update: {r.status_code} - {r.text}')
    except Exception as e:
        st.error(f'Request failed: {e}')
