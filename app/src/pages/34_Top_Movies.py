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

st.title("Top Movies")
st.write("The most-reviewed and highest-rated titles on the platform.")
st.write('---')


def fetch_top(sort_by: str):
    try:
        resp = requests.get(
            f"{API_BASE}/analytics/top-movies",
            params={'sort_by': sort_by},
            timeout=15,
        )
        if resp.status_code != 200:
            st.error(f"API error: {resp.status_code} - {resp.text}")
            return pd.DataFrame()
        payload = resp.json()
    except Exception as e:
        st.error(f"Failed to reach API: {e}")
        return pd.DataFrame()

    if isinstance(payload, dict) and 'movies' in payload:
        rows = payload['movies']
    elif isinstance(payload, list):
        rows = payload
    else:
        rows = []

    return pd.DataFrame(rows)


tab1, tab2 = st.tabs(["Most Reviewed", "Highest Rated"])

with tab1:
    st.subheader("Most Reviewed Movies")
    df_rev = fetch_top('reviews')
    if df_rev.empty:
        st.info("No data available.")
    else:
        st.dataframe(df_rev, use_container_width=True)

with tab2:
    st.subheader("Highest Rated Movies")
    df_rat = fetch_top('rating')
    if df_rat.empty:
        st.info("No data available.")
    else:
        st.dataframe(df_rat, use_container_width=True)
