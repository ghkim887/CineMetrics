# This file has functions to add links to the left sidebar based on the user's role.

import base64
from pathlib import Path

import streamlit as st


# ---- Role: casual (Jake Morrison) -------------------------------------------

def casual_home_nav():
    st.sidebar.page_link("pages/00_Casual_Viewer_Home.py", label="Home", icon="🏠")

def browse_movies_nav():
    st.sidebar.page_link("pages/01_Browse_Movies.py", label="Browse Movies", icon="🎬")

def my_recommendations_nav():
    st.sidebar.page_link("pages/02_My_Recommendations.py", label="My Recommendations", icon="⭐")

def watch_history_nav():
    st.sidebar.page_link("pages/03_Watch_History.py", label="Watch History", icon="📺")

def my_watchlist_nav():
    st.sidebar.page_link("pages/04_My_Watchlist.py", label="My Watchlist", icon="📋")

def rate_movie_nav():
    st.sidebar.page_link("pages/05_Rate_Movie.py", label="Rate Movie", icon="🌟")

def search_movies_nav():
    st.sidebar.page_link("pages/06_Search_Movies.py", label="Search Movies", icon="🔍")


# ---- Role: enthusiast (Priya Sharma) ----------------------------------------

def enthusiast_home_nav():
    st.sidebar.page_link("pages/10_Enthusiast_Home.py", label="Home", icon="🏠")

def write_review_nav():
    st.sidebar.page_link("pages/11_Write_Review.py", label="Write Review", icon="✏️")

def my_stats_nav():
    st.sidebar.page_link("pages/12_My_Stats.py", label="My Stats", icon="📊")

def similar_movies_nav():
    st.sidebar.page_link("pages/13_Similar_Movies.py", label="Similar Movies", icon="🔗")

def advanced_browse_nav():
    st.sidebar.page_link("pages/14_Advanced_Browse.py", label="Advanced Browse", icon="🔎")

def read_reviews_nav():
    st.sidebar.page_link("pages/15_Read_Reviews.py", label="Read Reviews", icon="📖")

def manage_reviews_nav():
    st.sidebar.page_link("pages/16_Manage_Reviews.py", label="Manage Reviews", icon="📝")


# ---- Role: admin (Marcus Chen) ----------------------------------------------

def admin_home_nav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="Home", icon="🏠")

def add_movie_nav():
    st.sidebar.page_link("pages/21_Add_Movie.py", label="Add Movie", icon="➕")

def edit_movie_nav():
    st.sidebar.page_link("pages/22_Edit_Movie.py", label="Edit Movie", icon="✏️")

def manage_movies_nav():
    st.sidebar.page_link("pages/23_Manage_Movies.py", label="Manage Movies", icon="🎬")

def moderate_reviews_nav():
    st.sidebar.page_link("pages/24_Moderate_Reviews.py", label="Moderate Reviews", icon="🛡️")

def manage_users_nav():
    st.sidebar.page_link("pages/25_Manage_Users.py", label="Manage Users", icon="👥")

def admin_logs_nav():
    st.sidebar.page_link("pages/26_Admin_Logs.py", label="Admin Logs", icon="📋")


# ---- Role: analyst (Elena Vasquez) ------------------------------------------

def analyst_home_nav():
    st.sidebar.page_link("pages/30_Analyst_Home.py", label="Home", icon="🏠")

def rating_distribution_nav():
    st.sidebar.page_link("pages/31_Rating_Distribution.py", label="Rating Distribution", icon="📊")

def trending_genres_nav():
    st.sidebar.page_link("pages/32_Trending_Genres.py", label="Trending Genres", icon="📈")

def click_through_rates_nav():
    st.sidebar.page_link("pages/33_Click_Through_Rates.py", label="Click-Through Rates", icon="🖱️")

def top_movies_nav():
    st.sidebar.page_link("pages/34_Top_Movies.py", label="Top Movies", icon="🏆")

def engagement_metrics_nav():
    st.sidebar.page_link("pages/35_Engagement_Metrics.py", label="Engagement Metrics", icon="📉")

def export_data_nav():
    st.sidebar.page_link("pages/36_Export_Data.py", label="Export Data", icon="💾")


# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks():
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page (if it exists)
    try:
        logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
        if logo_path.exists():
            logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
            st.sidebar.markdown(
                f"""
                <div style="text-align: center; padding: 0.5rem 0;">
                    <img src="data:image/png;base64,{logo_b64}"
                         style="width: 100%; max-width: 240px; height: auto; border-radius: 12px;" />
                </div>
                """,
                unsafe_allow_html=True,
            )
    except Exception:
        pass

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "casual":
            casual_home_nav()
            browse_movies_nav()
            my_recommendations_nav()
            watch_history_nav()
            my_watchlist_nav()
            rate_movie_nav()
            search_movies_nav()

        if st.session_state["role"] == "enthusiast":
            enthusiast_home_nav()
            write_review_nav()
            my_stats_nav()
            similar_movies_nav()
            advanced_browse_nav()
            read_reviews_nav()
            manage_reviews_nav()

        if st.session_state["role"] == "admin":
            admin_home_nav()
            add_movie_nav()
            edit_movie_nav()
            manage_movies_nav()
            moderate_reviews_nav()
            manage_users_nav()
            admin_logs_nav()

        if st.session_state["role"] == "analyst":
            analyst_home_nav()
            rating_distribution_nav()
            trending_genres_nav()
            click_through_rates_nav()
            top_movies_nav()
            engagement_metrics_nav()
            export_data_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
