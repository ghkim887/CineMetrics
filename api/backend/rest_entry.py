from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import init_app as init_db
from backend.movies.movie_routes import movies
from backend.users.user_routes import users
from backend.reviews.review_routes import reviews
from backend.recommendations.recommendation_routes import recommendations
from backend.watchlists.watchlist_routes import watchlists
from backend.admin.admin_routes import admin_bp
from backend.analytics.analytics_routes import analytics


def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('API startup')

    # Load environment variables from the .env file so they are
    # accessible via os.getenv() below.
    load_dotenv()

    # Secret key used by Flask for securely signing session cookies.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Database connection settings — values come from the .env file.
    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip()
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip()
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip()
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip())
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip()

    # Register the cleanup hook for the database connection.
    app.logger.info("create_app(): initializing database connection")
    init_db(app)

    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each.
    app.logger.info("create_app(): registering blueprints")
    app.register_blueprint(movies, url_prefix='/movies')
    app.register_blueprint(users, url_prefix='/users')
    app.register_blueprint(reviews, url_prefix='/reviews')
    app.register_blueprint(recommendations, url_prefix='/recommendations')
    app.register_blueprint(watchlists, url_prefix='/watchlists')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(analytics, url_prefix='/analytics')

    return app
