from flask import Blueprint, request, jsonify, current_app, Response
from backend.db_connection import get_db
from datetime import date, timedelta
import csv
import io

analytics = Blueprint('analytics', __name__)


# ------------------------------------------------------------
# GET /analytics/ratings-distribution
# Histogram of all ratings bucketed into 5 intervals of 2.
# Stories: Elena-1
# ------------------------------------------------------------
@analytics.route('/ratings-distribution', methods=['GET'])
def get_ratings_distribution():
    try:
        cursor = get_db().cursor(dictionary=True)

        query = (
            "SELECT "
            "    CASE "
            "        WHEN rating_value BETWEEN 0 AND 2 THEN '0-2' "
            "        WHEN rating_value BETWEEN 2.1 AND 4 THEN '2-4' "
            "        WHEN rating_value BETWEEN 4.1 AND 6 THEN '4-6' "
            "        WHEN rating_value BETWEEN 6.1 AND 8 THEN '6-8' "
            "        WHEN rating_value BETWEEN 8.1 AND 10 THEN '8-10' "
            "    END AS bucket, "
            "    COUNT(*) AS count "
            "FROM Rating "
            "GROUP BY bucket "
            "ORDER BY bucket"
        )
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_ratings_distribution: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# GET /analytics/trending-genres
# Top 10 genres by watch count in a given date range.
# Query params: start_date, end_date (default: last year to today)
# Stories: Elena-2
# ------------------------------------------------------------
@analytics.route('/trending-genres', methods=['GET'])
def get_trending_genres():
    try:
        cursor = get_db().cursor(dictionary=True)

        today = date.today()
        default_start = today - timedelta(days=365)

        start_date = request.args.get('start_date', default_start.isoformat())
        end_date = request.args.get('end_date', today.isoformat())

        query = (
            "SELECT g.genre_name, COUNT(wh.history_id) AS watch_count "
            "FROM WatchHistory wh "
            "JOIN MovieGenre mg ON wh.movie_id = mg.movie_id "
            "JOIN Genre g ON mg.genre_id = g.genre_id "
            "WHERE wh.watched_date BETWEEN %s AND %s "
            "GROUP BY g.genre_name "
            "ORDER BY watch_count DESC "
            "LIMIT 10"
        )
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()

        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_trending_genres: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# GET /analytics/click-through-rates
# Click-through rate (recommendations clicked / recommendations
# generated) grouped by user role.
# Stories: Elena-3
# ------------------------------------------------------------
@analytics.route('/click-through-rates', methods=['GET'])
def get_click_through_rates():
    try:
        cursor = get_db().cursor(dictionary=True)

        query = (
            "SELECT "
            "    u.role AS user_role, "
            "    COUNT(DISTINCT r.recommendation_id) AS total_recs, "
            "    COUNT(DISTINCT rc.click_id) AS total_clicks, "
            "    ROUND("
            "        COUNT(DISTINCT rc.click_id) * 100.0 / "
            "        NULLIF(COUNT(DISTINCT r.recommendation_id), 0), 2"
            "    ) AS ctr_pct "
            "FROM `User` u "
            "JOIN Recommendation r ON u.user_id = r.user_id "
            "LEFT JOIN RecommendationClick rc "
            "    ON r.recommendation_id = rc.recommendation_id "
            "GROUP BY u.role "
            "ORDER BY ctr_pct DESC"
        )
        cursor.execute(query)
        results = cursor.fetchall()

        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_click_through_rates: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# GET /analytics/top-movies
# Top movies by either review count or average rating.
# Query params: sort_by (reviews|rating, default reviews),
#               limit (default 20)
# Stories: Elena-4
# ------------------------------------------------------------
@analytics.route('/top-movies', methods=['GET'])
def get_top_movies():
    try:
        cursor = get_db().cursor(dictionary=True)

        sort_by = request.args.get('sort_by', 'reviews')
        try:
            limit = int(request.args.get('limit', 20))
        except (TypeError, ValueError):
            limit = 20

        if sort_by == 'rating':
            order_clause = "ORDER BY avg_rating DESC, review_count DESC"
        else:
            order_clause = "ORDER BY review_count DESC, avg_rating DESC"

        query = (
            "SELECT m.movie_id, m.title, m.release_year, "
            "       COUNT(DISTINCT rv.review_id) AS review_count, "
            "       ROUND(AVG(rt.rating_value), 2) AS avg_rating "
            "FROM Movie m "
            "LEFT JOIN Review rv "
            "    ON m.movie_id = rv.movie_id AND rv.is_deleted = 0 "
            "LEFT JOIN Rating rt ON m.movie_id = rt.movie_id "
            "WHERE m.status = 'active' "
            "GROUP BY m.movie_id, m.title, m.release_year "
            f"{order_clause} "
            "LIMIT %s"
        )
        cursor.execute(query, (limit,))
        results = cursor.fetchall()

        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_top_movies: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# GET /analytics/engagement
# User engagement metrics in a date range: total ratings,
# reviews, watchlist additions, and distinct active users.
# Query params: start_date, end_date (default: last 30 days)
# Stories: Elena-5
# ------------------------------------------------------------
@analytics.route('/engagement', methods=['GET'])
def get_engagement():
    try:
        cursor = get_db().cursor(dictionary=True)

        today = date.today()
        default_start = today - timedelta(days=30)

        start_date = request.args.get('start_date', default_start.isoformat())
        end_date = request.args.get('end_date', today.isoformat())

        # Total ratings in period
        cursor.execute(
            "SELECT COUNT(*) AS total_ratings FROM Rating "
            "WHERE DATE(rating_date) BETWEEN %s AND %s",
            (start_date, end_date)
        )
        total_ratings = cursor.fetchone()['total_ratings']

        # Total reviews in period (non-deleted)
        cursor.execute(
            "SELECT COUNT(*) AS total_reviews FROM Review "
            "WHERE DATE(review_date) BETWEEN %s AND %s "
            "AND is_deleted = 0",
            (start_date, end_date)
        )
        total_reviews = cursor.fetchone()['total_reviews']

        # Total watchlist additions in period
        cursor.execute(
            "SELECT COUNT(*) AS total_watchlist_additions "
            "FROM WatchlistItem "
            "WHERE DATE(added_at) BETWEEN %s AND %s",
            (start_date, end_date)
        )
        total_watchlist_additions = (
            cursor.fetchone()['total_watchlist_additions']
        )

        # Distinct active users (any of rating, review, watch) in period
        cursor.execute(
            "SELECT COUNT(DISTINCT user_id) AS active_users FROM ("
            "    SELECT user_id FROM Rating "
            "        WHERE DATE(rating_date) BETWEEN %s AND %s "
            "    UNION "
            "    SELECT user_id FROM Review "
            "        WHERE DATE(review_date) BETWEEN %s AND %s "
            "        AND is_deleted = 0 "
            "    UNION "
            "    SELECT user_id FROM WatchHistory "
            "        WHERE watched_date BETWEEN %s AND %s "
            ") AS active",
            (start_date, end_date,
             start_date, end_date,
             start_date, end_date)
        )
        active_users = cursor.fetchone()['active_users']

        return jsonify({
            'start_date': start_date,
            'end_date': end_date,
            'total_ratings': total_ratings,
            'total_reviews': total_reviews,
            'total_watchlist_additions': total_watchlist_additions,
            'active_users': active_users,
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_engagement: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# GET /analytics/export
# Export a table as CSV.
# Query params:
#   table: 'movies' | 'ratings' | 'reviews' (default 'movies')
#   start_date, end_date: optional filter for ratings/reviews
# Stories: Elena-6
# ------------------------------------------------------------
@analytics.route('/export', methods=['GET'])
def export_csv():
    try:
        table = request.args.get('table', 'movies')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        cursor = get_db().cursor(dictionary=True)

        if table == 'movies':
            cursor.execute(
                "SELECT movie_id, title, release_year, runtime_minutes, "
                "country_of_origin, language, average_rating, status "
                "FROM Movie WHERE status = %s",
                ('active',)
            )
        elif table == 'ratings':
            if start_date and end_date:
                cursor.execute(
                    "SELECT rating_id, user_id, movie_id, rating_value, "
                    "rating_date FROM Rating "
                    "WHERE DATE(rating_date) BETWEEN %s AND %s",
                    (start_date, end_date)
                )
            else:
                cursor.execute(
                    "SELECT rating_id, user_id, movie_id, rating_value, "
                    "rating_date FROM Rating"
                )
        elif table == 'reviews':
            if start_date and end_date:
                cursor.execute(
                    "SELECT review_id, user_id, movie_id, review_title, "
                    "review_body, review_date, moderation_status "
                    "FROM Review WHERE is_deleted = 0 "
                    "AND DATE(review_date) BETWEEN %s AND %s",
                    (start_date, end_date)
                )
            else:
                cursor.execute(
                    "SELECT review_id, user_id, movie_id, review_title, "
                    "review_body, review_date, moderation_status "
                    "FROM Review WHERE is_deleted = 0"
                )
        else:
            return jsonify({
                'error': (
                    "Invalid table. Must be 'movies', 'ratings', "
                    "or 'reviews'."
                )
            }), 400

        rows = cursor.fetchall()

        output = io.StringIO()
        if rows:
            writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        else:
            # Still emit a header line when the result set is empty so
            # downstream tools don't choke on a zero-byte response.
            output.write('')

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': (
                    f'attachment; filename={table}_export.csv'
                )
            }
        )
    except Exception as e:
        current_app.logger.error(f'Error in export_csv: {e}')
        return jsonify({'error': str(e)}), 500
