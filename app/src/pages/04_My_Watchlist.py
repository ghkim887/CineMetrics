##################################################
# My Watchlist - Story Jake-4
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

st.title('My Watchlist 📋')
st.write('Organize movies you want to watch.')
st.write('')

# ---- Create new watchlist ----
with st.expander('➕ Create New Watchlist'):
    with st.form('create_watchlist_form'):
        new_name = st.text_input('Watchlist name')
        create_sub = st.form_submit_button('Create', type='primary')

        if create_sub:
            if not new_name.strip():
                st.error('Please enter a name.')
            else:
                payload = {
                    'user_id': user_id,
                    'name': new_name.strip(),
                }
                try:
                    with st.spinner('Creating...'):
                        resp = requests.post(f'{API_BASE}/watchlists/', json=payload, timeout=10)
                    if resp.status_code in (200, 201):
                        st.success(f'Created "{new_name}"!')
                        st.rerun()
                    else:
                        st.error(f'Failed to create (status {resp.status_code}): {resp.text}')
                except requests.exceptions.RequestException as e:
                    st.error(f'Unable to reach API: {e}')

st.write('---')

# ---- Fetch user's watchlists ----
st.subheader('Your Watchlists')

watchlists = []
try:
    with st.spinner('Loading watchlists...'):
        wl_resp = requests.get(f'{API_BASE}/watchlists/user/{user_id}', timeout=10)
    if wl_resp.status_code == 200:
        watchlists = wl_resp.json() or []
    else:
        st.warning(f'Could not load watchlists (status {wl_resp.status_code})')
except requests.exceptions.RequestException as e:
    st.error(f'Unable to reach API: {e}')

if not watchlists:
    st.info('You have no watchlists. Create one above!')
else:
    # Fetch all movies for the add form
    all_movies = []
    try:
        movies_resp = requests.get(f'{API_BASE}/movies/', timeout=10)
        if movies_resp.status_code == 200:
            all_movies = movies_resp.json() or []
    except requests.exceptions.RequestException:
        pass

    movie_map = {}
    for m in all_movies:
        mid = m.get('movie_id') or m.get('id')
        title = m.get('title', 'Untitled')
        year = m.get('release_year') or m.get('year') or ''
        label = f"{title} ({year})" if year else title
        if mid is not None:
            movie_map[label] = mid

    for wl in watchlists:
        wl_id = wl.get('watchlist_id') or wl.get('id')
        wl_name = wl.get('name', 'Untitled list')
        wl_desc = wl.get('description', '')

        with st.expander(f"📋 {wl_name}", expanded=True):
            if wl_desc:
                st.caption(wl_desc)

            # ---- Fetch items ----
            try:
                items_resp = requests.get(f'{API_BASE}/watchlists/{wl_id}/items', timeout=10)
                if items_resp.status_code == 200:
                    items = items_resp.json() or []
                else:
                    items = []
                    st.warning(f'Could not load items (status {items_resp.status_code})')
            except requests.exceptions.RequestException as e:
                items = []
                st.error(f'Unable to reach API: {e}')

            if not items:
                st.caption('_No movies in this watchlist yet._')
            else:
                for it in items:
                    item_id = it.get('watchlist_item_id')
                    title = it.get('title', 'Untitled')
                    year = it.get('release_year') or it.get('year') or ''
                    ic1, ic2 = st.columns([5, 1])
                    with ic1:
                        st.write(f"• **{title}** ({year})")
                    with ic2:
                        if st.button('Remove', key=f'rm_{wl_id}_{item_id}', use_container_width=True):
                            try:
                                del_resp = requests.delete(
                                    f'{API_BASE}/watchlists/{wl_id}/items/{item_id}',
                                    timeout=10
                                )
                                if del_resp.status_code in (200, 204):
                                    st.success('Removed!')
                                    st.rerun()
                                else:
                                    st.error(f'Failed (status {del_resp.status_code})')
                            except requests.exceptions.RequestException as e:
                                st.error(f'Unable to reach API: {e}')

            # ---- Add movie to this watchlist ----
            if movie_map:
                with st.form(f'add_item_form_{wl_id}'):
                    sel_label = st.selectbox(
                        'Add a movie',
                        list(movie_map.keys()),
                        key=f'add_sel_{wl_id}'
                    )
                    add_sub = st.form_submit_button('➕ Add to Watchlist')
                    if add_sub:
                        payload = {'movie_id': movie_map[sel_label]}
                        try:
                            add_resp = requests.post(
                                f'{API_BASE}/watchlists/{wl_id}/items',
                                json=payload,
                                timeout=10
                            )
                            if add_resp.status_code in (200, 201):
                                st.success(f'Added "{sel_label}"!')
                                st.rerun()
                            else:
                                st.error(f'Failed (status {add_resp.status_code}): {add_resp.text}')
                        except requests.exceptions.RequestException as e:
                            st.error(f'Unable to reach API: {e}')
