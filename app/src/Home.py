##################################################
# This is the main/entry-point file for the
# CineMetrics application
##################################################

import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not authenticated.
st.session_state['authenticated'] = False

SideBarLinks()

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the CineMetrics Home page")

st.title('CineMetrics')
st.write('#### Your personal movie analytics and discovery platform.')
st.write('')
st.write('##### Select a persona to get started:')

# ---- Persona 1: Jake Morrison (Casual Viewer) ----
st.write('')
st.subheader('Jake Morrison - Casual Viewer')
st.write('Browse movies, get recommendations, and track what you watch.')
if st.button('Login as Jake', type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'casual'
    st.session_state['first_name'] = 'Jake'
    st.session_state['user_id'] = 1
    logger.info("Logging in as Casual Viewer Persona")
    st.switch_page('pages/00_Casual_Viewer_Home.py')

# ---- Persona 2: Priya Sharma (Movie Enthusiast) ----
st.write('---')
st.subheader('Priya Sharma - Movie Enthusiast')
st.write('Write reviews, explore stats, and discover similar movies.')
if st.button('Login as Priya', type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'enthusiast'
    st.session_state['first_name'] = 'Priya'
    st.session_state['user_id'] = 11
    logger.info("Logging in as Movie Enthusiast Persona")
    st.switch_page('pages/10_Enthusiast_Home.py')

# ---- Persona 3: Marcus Chen (Platform Admin) ----
st.write('---')
st.subheader('Marcus Chen - Platform Admin')
st.write('Manage movies, moderate reviews, and oversee platform users.')
if st.button('Login as Marcus', type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'admin'
    st.session_state['first_name'] = 'Marcus'
    st.session_state['user_id'] = 21
    logger.info("Logging in as Platform Admin Persona")
    st.switch_page('pages/20_Admin_Home.py')

# ---- Persona 4: Elena Vasquez (Data Analyst) ----
st.write('---')
st.subheader('Elena Vasquez - Data Analyst')
st.write('Analyze rating distributions, trends, and engagement metrics.')
if st.button('Login as Elena', type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'analyst'
    st.session_state['first_name'] = 'Elena'
    st.session_state['user_id'] = 31
    logger.info("Logging in as Data Analyst Persona")
    st.switch_page('pages/30_Analyst_Home.py')
