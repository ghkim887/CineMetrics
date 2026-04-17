import streamlit as st
import requests
import pandas as pd
import io
from datetime import date, timedelta
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title("Export Data")
st.write("Pull raw CSV slices for offline analysis.")
st.write('---')

table = st.selectbox("Table", options=['movies', 'ratings', 'reviews'])

today = date.today()
default_start = today - timedelta(days=365)

start_date = end_date = None
if table in ('ratings', 'reviews'):
    st.caption("Optional date range (applies to ratings and reviews).")
    col_s, col_e = st.columns(2)
    with col_s:
        start_date = st.date_input("Start date", value=default_start)
    with col_e:
        end_date = st.date_input("End date", value=today)
    if start_date > end_date:
        st.error("Start date must be on or before end date.")
        st.stop()


def build_params():
    params = {'table': table}
    if start_date and end_date and table in ('ratings', 'reviews'):
        params['start_date'] = start_date.isoformat()
        params['end_date'] = end_date.isoformat()
    return params


def fetch_csv():
    try:
        resp = requests.get(
            f"{API_BASE}/analytics/export",
            params=build_params(),
            timeout=30,
        )
        if resp.status_code != 200:
            st.error(f"API error: {resp.status_code} - {resp.text}")
            return None
        return resp.content
    except Exception as e:
        st.error(f"Failed to reach API: {e}")
        return None


# Keep fetched bytes in session state so preview + download use the same pull
cache_key = f"export_csv_{table}_{start_date}_{end_date}"

col_prev, col_dl = st.columns(2)

with col_prev:
    if st.button("Preview", use_container_width=True):
        content = fetch_csv()
        if content is not None:
            st.session_state[cache_key] = content

with col_dl:
    content = st.session_state.get(cache_key)
    st.download_button(
        label="Download CSV",
        data=content if content is not None else b"",
        file_name=f"{table}_export.csv",
        mime="text/csv",
        disabled=content is None,
        use_container_width=True,
    )

content = st.session_state.get(cache_key)
if content is not None:
    st.subheader("Preview (first 20 rows)")
    try:
        df = pd.read_csv(io.BytesIO(content))
        st.dataframe(df.head(20), use_container_width=True)
        st.caption(f"Total rows: {len(df):,}  |  Columns: {len(df.columns)}")
    except Exception as e:
        st.error(f"Could not parse CSV response: {e}")
        st.text(content[:1000].decode(errors='replace'))
else:
    st.info("Click Preview to fetch data, then Download to save the CSV.")
