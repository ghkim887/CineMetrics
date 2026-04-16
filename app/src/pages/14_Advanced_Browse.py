import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title('Advanced Movie Browse')
st.write('Filter and sort the full catalog.')

# ---- Filter controls ----
with st.form('filter_form'):
    year_range = st.slider('Release year', 1900, 2025, (1990, 2025))

    c1, c2, c3 = st.columns(3)
    with c1:
        countries = st.multiselect(
            'Country',
            ['USA', 'UK', 'France', 'Japan', 'South Korea', 'New Zealand',
             'Australia', 'Mexico', 'Brazil', 'Italy'],
        )
    with c2:
        languages = st.multiselect(
            'Language',
            ['English', 'Spanish', 'French', 'German', 'Japanese', 'Korean',
             'Hindi', 'Mandarin', 'Italian', 'Portuguese'],
        )
    with c3:
        genres = st.multiselect(
            'Genre',
            ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
             'Drama', 'Family', 'Fantasy', 'Horror', 'Mystery', 'Romance',
             'Sci-Fi', 'Thriller', 'War', 'Western'],
        )

    sort_by = st.selectbox('Sort by', ['rating', 'year', 'title'])

    submitted = st.form_submit_button('Apply Filters', type='primary', use_container_width=True)

# ---- Fetch ALL movies (no filter params — API doesn't support multi-value filters) ----
# Client-side filtering provides richer filtering than the API contract supports.
all_movies = []
try:
    resp = requests.get(f'{API_BASE}/movies/', timeout=10)
    if resp.status_code == 200:
        all_movies = resp.json() or []
    else:
        st.error(f'Failed to load movies (status {resp.status_code})')
except Exception as e:
    st.error(f'Could not fetch movies: {e}')

# ---- Client-side filtering using pandas ----
results = []
if all_movies:
    try:
        df = pd.DataFrame(all_movies)

        # Year range filter
        if 'release_year' in df.columns:
            df = df[df['release_year'].fillna(0).astype(int).between(year_range[0], year_range[1])]

        # Country filter (multi-value)
        if countries and 'country_of_origin' in df.columns:
            df = df[df['country_of_origin'].isin(countries)]

        # Language filter (multi-value)
        if languages and 'language' in df.columns:
            df = df[df['language'].isin(languages)]

        # Genre filter (multi-value)
        if genres and 'genres' in df.columns:
            df = df[df['genres'].apply(
                lambda g: any(x['genre_name'] in genres for x in g) if isinstance(g, list) else False
            )]

        # Sorting (client-side)
        sort_map = {'rating': 'average_rating', 'year': 'release_year', 'title': 'title'}
        sort_col = sort_map.get(sort_by, sort_by)
        if sort_col in df.columns:
            ascending = sort_by == 'title'
            df = df.sort_values(by=sort_col, ascending=ascending, na_position='last')

        results = df.to_dict('records')
    except Exception as e:
        st.error(f'Could not apply filters: {e}')
        results = all_movies

st.write('---')
st.subheader(f'Results ({len(results)})')

if not results:
    st.info('No movies match the current filters.')
else:
    try:
        df = pd.DataFrame(results)
        preferred_cols = [c for c in ['title', 'release_year', 'country_of_origin', 'language',
                                      'average_rating', 'runtime_minutes'] if c in df.columns]
        if preferred_cols:
            df = df[preferred_cols]
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f'Could not render results: {e}')
        for m in results:
            st.write(m)
