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

st.title('Manage Movies')
st.write('#### Flag duplicates or remove entries from the catalog')
st.write('')

# GET /movies/ only returns active movies per movie_routes._get_movies filter.
# For admin moderation we need to see flagged/removed too. The API doesn't
# surface those directly, so we fetch all active movies here and combine with
# per-id lookups that the admin may want to revisit.

movies = []
try:
    r = requests.get(f'{API_BASE}/movies/', timeout=5)
    if r.status_code == 200:
        movies = r.json() or []
    else:
        st.error(f'Could not load movies: {r.status_code}')
except Exception as e:
    st.error(f'Could not load movies: {e}')

# ---- Filters ----
c1, c2 = st.columns([1, 2])
with c1:
    status_filter = st.selectbox(
        'Filter by status',
        ['all', 'active', 'flagged', 'removed'],
        index=0,
    )
with c2:
    search = st.text_input('Search by title')

filtered = movies
if status_filter != 'all':
    filtered = [m for m in filtered if (m.get('status') or 'active') == status_filter]
if search:
    needle = search.lower()
    filtered = [m for m in filtered if needle in (m.get('title') or '').lower()]

st.write(f'Showing {len(filtered)} of {len(movies)} movies')

# ---- Table view ----
if filtered:
    df_rows = [{
        'movie_id': m.get('movie_id'),
        'title': m.get('title'),
        'year': m.get('release_year'),
        'status': m.get('status') or 'active',
        'avg_rating': m.get('average_rating'),
    } for m in filtered]
    st.dataframe(pd.DataFrame(df_rows), use_container_width=True, hide_index=True)

st.write('---')

# ---- Action panel ----
st.subheader('Flag or Remove a Movie')

if not filtered:
    st.info('No movies match your filter.')
    st.stop()

option_map = {
    f"{m['title']} ({m.get('release_year','?')}) [id={m['movie_id']}, status={m.get('status','active')}]": m['movie_id']
    for m in filtered
}
selection = st.selectbox('Select movie', list(option_map.keys()))
selected_id = option_map[selection]

c1, c2 = st.columns(2)

with c1:
    if st.button('Flag as Duplicate', type='primary', use_container_width=True):
        try:
            r = requests.put(
                f'{API_BASE}/movies/{selected_id}',
                json={'status': 'flagged'},
                timeout=10,
            )
            if r.status_code == 200:
                st.success(f'Movie {selected_id} flagged.')
                st.rerun()
            else:
                st.error(f'Failed: {r.status_code} - {r.text}')
        except Exception as e:
            st.error(f'Request failed: {e}')

with c2:
    if st.button('Remove Movie', use_container_width=True):
        try:
            r = requests.delete(
                f'{API_BASE}/movies/{selected_id}', timeout=10
            )
            if r.status_code == 200:
                st.success(f'Movie {selected_id} removed.')
                st.rerun()
            else:
                st.error(f'Failed: {r.status_code} - {r.text}')
        except Exception as e:
            st.error(f'Request failed: {e}')
