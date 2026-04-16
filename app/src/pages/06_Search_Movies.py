##################################################
# Search Movies - Story Jake-6
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

st.title('Search Movies 🔍')
st.write('Find a movie by title, keyword, or actor.')
st.write('')

# ---- Session state for selection ----
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = []
if 'selected_movie_id' not in st.session_state:
    st.session_state['selected_movie_id'] = None

# ---- Search form ----
with st.form('search_form'):
    query = st.text_input('Search query', placeholder='e.g. "Inception" or "Tarantino"')
    col1, col2 = st.columns([1, 5])
    with col1:
        submitted = st.form_submit_button('🔍 Search', type='primary', use_container_width=True)

    if submitted:
        if not query.strip():
            st.warning('Please enter a search query.')
        else:
            try:
                with st.spinner('Searching...'):
                    resp = requests.get(
                        f'{API_BASE}/movies/',
                        params={'search': query.strip()},
                        timeout=10
                    )
                if resp.status_code == 200:
                    st.session_state['search_results'] = resp.json() or []
                    st.session_state['selected_movie_id'] = None
                else:
                    st.error(f'Search failed (status {resp.status_code})')
            except requests.exceptions.RequestException as e:
                st.error(f'Unable to reach API: {e}')

st.write('---')

# ---- Display detail view if a movie is selected ----
if st.session_state['selected_movie_id'] is not None:
    movie_id = st.session_state['selected_movie_id']

    if st.button('← Back to results'):
        st.session_state['selected_movie_id'] = None
        st.rerun()

    try:
        with st.spinner('Loading details...'):
            d_resp = requests.get(f'{API_BASE}/movies/{movie_id}', timeout=10)
        if d_resp.status_code == 200:
            m = d_resp.json() or {}
            title = m.get('title', 'Untitled')
            year = m.get('release_year') or m.get('year') or 'N/A'
            rating = m.get('average_rating')
            synopsis = m.get('synopsis') or m.get('description') or 'No synopsis.'
            runtime = m.get('runtime_minutes', '')

            st.markdown(f"# {title}")
            rating_display = f"⭐ {rating}" if rating is not None else "N/A"
            st.caption(f"**Year:** {year}  |  **Rating:** {rating_display}  |  **Runtime:** {runtime} min")
            st.write('### Synopsis')
            st.write(synopsis)

            st.write('---')
            st.subheader('Reviews')
            try:
                rev_resp = requests.get(f'{API_BASE}/movies/{movie_id}/reviews', timeout=10)
                if rev_resp.status_code == 200:
                    reviews = rev_resp.json() or []
                    if not reviews:
                        st.caption('_No reviews yet._')
                    else:
                        for rev in reviews:
                            with st.container(border=True):
                                r_user = rev.get('username') or rev.get('user_id', 'User')
                                r_title = rev.get('review_title', '')
                                r_body = rev.get('review_body', '')
                                r_date = rev.get('review_date', '')
                                header = f"**{r_user}**"
                                if r_date:
                                    header += f" — _{r_date}_"
                                st.write(header)
                                if r_title:
                                    st.markdown(f"**{r_title}**")
                                if r_body:
                                    st.write(r_body)
                else:
                    st.caption(f'_Could not load reviews (status {rev_resp.status_code})_')
            except requests.exceptions.RequestException as e:
                st.error(f'Unable to reach API: {e}')
        else:
            st.error(f'Could not load movie (status {d_resp.status_code})')
    except requests.exceptions.RequestException as e:
        st.error(f'Unable to reach API: {e}')

# ---- Display results list ----
else:
    results = st.session_state['search_results']
    if not results:
        st.caption('_Enter a query above and click Search._')
    else:
        st.write(f'**{len(results)} result(s):**')
        st.write('')

        cols_per_row = 3
        for i in range(0, len(results), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(results):
                    m = results[i + j]
                    mid = m.get('movie_id') or m.get('id')
                    with col:
                        with st.container(border=True):
                            title = m.get('title', 'Untitled')
                            year = m.get('release_year') or m.get('year') or 'N/A'
                            rating = m.get('average_rating')
                            synopsis = m.get('synopsis') or m.get('description') or ''

                            st.markdown(f"### {title}")
                            rating_display = f"⭐ {rating}" if rating is not None else "N/A"
                            st.caption(f"**Year:** {year}  |  **Rating:** {rating_display}")
                            if synopsis:
                                short = synopsis[:140] + ('...' if len(synopsis) > 140 else '')
                                st.write(short)

                            if mid is not None:
                                if st.button('View Details', key=f'det_{mid}_{i}_{j}', use_container_width=True):
                                    st.session_state['selected_movie_id'] = mid
                                    st.rerun()
