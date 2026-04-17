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
first_name = st.session_state.get('first_name', 'Elena')

st.title(f"Welcome, {first_name}!")
st.write("#### Data Analyst Dashboard")
st.write("Dive into platform analytics, user engagement trends, and movie performance metrics.")
st.write('---')

# ---- KPIs ----
st.subheader("Platform KPIs")

total_users = total_movies = total_reviews = total_ratings = "N/A"

# Total users
try:
    r = requests.get(f"{API_BASE}/admin/users", timeout=10)
    if r.status_code == 200:
        data = r.json()
        total_users = len(data) if isinstance(data, list) else data.get('count', len(data.get('users', [])) if isinstance(data.get('users'), list) else "N/A")
except Exception as e:
    st.warning(f"Could not load users: {e}")

# Total movies
try:
    r = requests.get(f"{API_BASE}/movies/", timeout=10)
    if r.status_code == 200:
        data = r.json()
        total_movies = len(data) if isinstance(data, list) else data.get('count', len(data.get('movies', [])) if isinstance(data.get('movies'), list) else "N/A")
except Exception as e:
    st.warning(f"Could not load movies: {e}")

# Total reviews
try:
    r = requests.get(f"{API_BASE}/reviews/", timeout=10)
    if r.status_code == 200:
        data = r.json()
        total_reviews = len(data) if isinstance(data, list) else data.get('count', len(data.get('reviews', [])) if isinstance(data.get('reviews'), list) else "N/A")
except Exception as e:
    st.warning(f"Could not load reviews: {e}")

# Total ratings (derive from ratings distribution)
try:
    r = requests.get(f"{API_BASE}/analytics/ratings-distribution", timeout=10)
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            total_ratings = sum(d.get('count', 0) for d in data)
        elif isinstance(data, dict):
            total_ratings = data.get('total', sum(d.get('count', 0) for d in data.get('buckets', [])))
except Exception as e:
    st.warning(f"Could not load ratings: {e}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Users", total_users)
with col2:
    st.metric("Total Movies", total_movies)
with col3:
    st.metric("Total Reviews", total_reviews)
with col4:
    st.metric("Total Ratings", total_ratings)

st.write('---')

# ---- Quick access ----
st.subheader("Analytics Modules")

row1_col1, row1_col2, row1_col3 = st.columns(3)
with row1_col1:
    st.write("**Rating Distribution**")
    st.caption("Inspect how user ratings are distributed across buckets.")
    if st.button("Open", key="go_rating", use_container_width=True):
        st.switch_page("pages/31_Rating_Distribution.py")

with row1_col2:
    st.write("**Trending Genres**")
    st.caption("See which genres are trending over a given window.")
    if st.button("Open", key="go_trending", use_container_width=True):
        st.switch_page("pages/32_Trending_Genres.py")

with row1_col3:
    st.write("**Click-Through Rates**")
    st.caption("Measure how often users engage with recommendations.")
    if st.button("Open", key="go_ctr", use_container_width=True):
        st.switch_page("pages/33_Click_Through_Rates.py")

row2_col1, row2_col2, row2_col3 = st.columns(3)
with row2_col1:
    st.write("**Top Movies**")
    st.caption("Find the most reviewed and highest rated titles.")
    if st.button("Open", key="go_top", use_container_width=True):
        st.switch_page("pages/34_Top_Movies.py")

with row2_col2:
    st.write("**Engagement Metrics**")
    st.caption("Compare engagement activity across time ranges.")
    if st.button("Open", key="go_engage", use_container_width=True):
        st.switch_page("pages/35_Engagement_Metrics.py")

with row2_col3:
    st.write("**Export Data**")
    st.caption("Download raw CSV slices for offline analysis.")
    if st.button("Open", key="go_export", use_container_width=True):
        st.switch_page("pages/36_Export_Data.py")
