import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title("Trending Genres")
st.write("Top genres by watch count in a selected window.")
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
    resp = requests.get(f"{API_BASE}/analytics/trending-genres", params=params, timeout=15)
    if resp.status_code != 200:
        st.error(f"API error: {resp.status_code} - {resp.text}")
        st.stop()
    payload = resp.json()
except Exception as e:
    st.error(f"Failed to reach API: {e}")
    st.stop()

if isinstance(payload, dict) and 'genres' in payload:
    rows = payload['genres']
elif isinstance(payload, list):
    rows = payload
else:
    rows = []

if not rows:
    st.info("No genre data in the selected range.")
    st.stop()

df = pd.DataFrame(rows)

genre_col = next((c for c in ['genre', 'name', 'genre_name', 'label'] if c in df.columns), df.columns[0])
count_col = next((c for c in ['watch_count', 'count', 'watches', 'total'] if c in df.columns), df.columns[-1])

df = df.sort_values(by=count_col, ascending=False).head(10)

st.metric("Genres shown", len(df))

fig = px.bar(
    df.sort_values(by=count_col, ascending=True),
    x=count_col,
    y=genre_col,
    orientation='h',
    labels={genre_col: "Genre", count_col: "Watch Count"},
    title=f"Top {len(df)} Genres ({start_date} to {end_date})",
)
fig.update_layout(template='plotly_dark', height=550)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Raw data"):
    st.dataframe(df, use_container_width=True)
