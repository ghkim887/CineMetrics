import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if not st.session_state.get('authenticated'):
    st.warning('Please log in from the Home page')
    st.stop()

SideBarLinks()

API_BASE = 'http://web-api:4000'
user_id = st.session_state.get('user_id', 1)

st.title("Rating Distribution")
st.write("Histogram of user ratings across the platform.")
st.write('---')

try:
    resp = requests.get(f"{API_BASE}/analytics/ratings-distribution", timeout=15)
    if resp.status_code != 200:
        st.error(f"API error: {resp.status_code} - {resp.text}")
        st.stop()
    payload = resp.json()
except Exception as e:
    st.error(f"Failed to reach API: {e}")
    st.stop()

# Normalize: accept either a list of dicts or {'buckets': [...]}
if isinstance(payload, dict) and 'buckets' in payload:
    rows = payload['buckets']
elif isinstance(payload, list):
    rows = payload
else:
    rows = []

if not rows:
    st.info("No rating data available.")
    st.stop()

df = pd.DataFrame(rows)

# Best-effort column discovery
bucket_col = next((c for c in ['bucket', 'rating', 'rating_bucket', 'score', 'label'] if c in df.columns), df.columns[0])
count_col = next((c for c in ['count', 'total', 'num', 'frequency'] if c in df.columns), df.columns[-1])

df = df.sort_values(by=bucket_col)
total_ratings = int(df[count_col].sum()) if pd.api.types.is_numeric_dtype(df[count_col]) else 0
df['pct'] = (df[count_col] / total_ratings * 100).round(2) if total_ratings else 0

col_a, col_b = st.columns(2)
with col_a:
    st.metric("Total Ratings", f"{total_ratings:,}")
with col_b:
    st.metric("Rating Buckets", len(df))

fig = px.bar(
    df,
    x=bucket_col,
    y=count_col,
    text='pct',
    labels={bucket_col: "Rating", count_col: "Count"},
    title="Ratings by Bucket",
)
fig.update_traces(texttemplate='%{text}%', textposition='outside')
fig.update_layout(template='plotly_dark', height=500)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Raw data"):
    st.dataframe(df, use_container_width=True)
