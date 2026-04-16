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

st.title('My Viewing Statistics')
st.write('A look at your activity on CineMetrics.')

# ---- Stats ----
stats = {}
try:
    resp = requests.get(f'{API_BASE}/users/{user_id}/stats', timeout=5)
    if resp.status_code == 200:
        stats = resp.json() or {}
    else:
        st.error(f'Failed to load stats (status {resp.status_code})')
except Exception as e:
    st.error(f'Could not fetch stats: {e}')

# ---- Top-level metrics ----
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric('Total Movies Watched', stats.get('total_movies_watched', 0))
with c2:
    st.metric('Total Ratings', stats.get('total_ratings', 0))
with c3:
    avg = stats.get('average_rating_given')
    st.metric('Average Rating', f'{float(avg):.2f}' if avg is not None else '—')
with c4:
    st.metric('Total Reviews', stats.get('total_reviews', 0))

st.write('---')

# ---- Genre breakdown ----
st.subheader('Watched by Genre')
genre_data = stats.get('genre_breakdown') or []
if genre_data:
    try:
        df = pd.DataFrame(genre_data)
        if 'genre_name' in df.columns and 'movies_watched' in df.columns:
            df = df.set_index('genre_name')
            st.bar_chart(df['movies_watched'])
        else:
            st.bar_chart(df)
    except Exception as e:
        st.error(f'Could not render chart: {e}')
else:
    st.info('No genre data yet — rate or review some movies to see your breakdown.')
