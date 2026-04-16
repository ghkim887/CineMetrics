##################################################
# Browse Movies - Story Jake-1
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

st.title('Browse Movies 🎬')
st.write('Filter movies by genre, year, and country.')
st.write('')

# ---- Filter form ----
GENRE_OPTIONS = [
    'Any', 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror',
    'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western'
]

COUNTRY_OPTIONS = [
    'Any', 'USA', 'UK', 'France', 'Germany', 'Italy', 'Spain', 'Japan',
    'South Korea', 'India', 'China', 'Canada', 'Australia', 'Mexico', 'Brazil'
]

YEAR_OPTIONS = ['Any'] + [str(y) for y in range(2026, 1949, -1)]

with st.form('browse_filters'):
    col1, col2 = st.columns(2)
    with col1:
        selected_genre = st.selectbox('Genre', GENRE_OPTIONS, index=0)
        selected_country = st.selectbox('Country', COUNTRY_OPTIONS, index=0)
    with col2:
        selected_year = st.selectbox('Year', YEAR_OPTIONS, index=0)

    submitted = st.form_submit_button('Apply Filters', type='primary', use_container_width=True)

# ---- Build request params ----
params = {}
if selected_genre and selected_genre != 'Any':
    params['genre'] = selected_genre
if selected_country and selected_country != 'Any':
    params['country'] = selected_country
if selected_year and selected_year != 'Any':
    params['year'] = selected_year

st.write('---')

# ---- Fetch movies ----
try:
    with st.spinner('Loading movies...'):
        resp = requests.get(f'{API_BASE}/movies/', params=params, timeout=10)

    if resp.status_code == 200:
        movies = resp.json() or []

        if not movies:
            st.info('No movies match your filters. Try adjusting them.')
        else:
            st.write(f'**Found {len(movies)} movie(s).**')
            st.write('')

            # ---- Render movie grid ----
            cols_per_row = 3
            for i in range(0, len(movies), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(movies):
                        m = movies[i + j]
                        with col:
                            with st.container(border=True):
                                title = m.get('title', 'Untitled')
                                year = m.get('release_year') or m.get('year') or 'N/A'
                                rating = m.get('average_rating')
                                synopsis = m.get('synopsis') or m.get('description') or 'No synopsis available.'

                                st.markdown(f"### {title}")
                                rating_display = f"⭐ {rating}" if rating is not None else "N/A"
                                st.caption(f"**Year:** {year}  |  **Rating:** {rating_display}")
                                if len(synopsis) > 180:
                                    synopsis = synopsis[:180] + '...'
                                st.write(synopsis)
    else:
        st.error(f'Failed to load movies (status {resp.status_code})')
except requests.exceptions.RequestException as e:
    st.error(f'Unable to reach API: {e}')
