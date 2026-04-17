import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title("Engagement Metrics")
st.write("User engagement across ratings, reviews, watchlist activity, and active users.")
st.write('---')

today = date.today()
default_start = today - timedelta(days=365)

col_s, col_e = st.columns(2)
with col_s:
    start_date = st.date_input("Start date", value=default_start)
with col_e:
    end_date = st.date_input("End date", value=today)

if start_date > end_date:
    st.error("Start date must be on or before end date.")
    st.stop()

params = {
    'start_date': start_date.isoformat(),
    'end_date': end_date.isoformat(),
}

try:
    resp = requests.get(f"{API_BASE}/analytics/engagement", params=params, timeout=15)
    if resp.status_code != 200:
        st.error(f"API error: {resp.status_code} - {resp.text}")
        st.stop()
    data = resp.json()
except Exception as e:
    st.error(f"Failed to reach API: {e}")
    st.stop()

# Support either a flat dict or a wrapped dict
if isinstance(data, list) and data:
    data = data[0]
if not isinstance(data, dict):
    data = {}

total_ratings = data.get('total_ratings', 'N/A')
total_reviews = data.get('total_reviews', 'N/A')
total_watchlist = data.get('total_watchlist_additions',
                          data.get('total_watchlist', 'N/A'))
active_users = data.get('active_users', 'N/A')

st.subheader(f"Window: {start_date} - {end_date}")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Ratings", total_ratings)
with c2:
    st.metric("Total Reviews", total_reviews)
with c3:
    st.metric("Watchlist Additions", total_watchlist)
with c4:
    st.metric("Active Users", active_users)

with st.expander("Raw response"):
    st.json(data)
