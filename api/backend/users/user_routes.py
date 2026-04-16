from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import get_db
from datetime import date

users = Blueprint('users', __name__)


# ============================================================
# GET /users/<user_id>/recommendations
# Personalized recommendations for a user, joined with Movie
# details. Active movies only, ordered by score desc.
# Stories: [Jake-2]
# ============================================================
@users.route('/<int:user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
    try:
        cursor = get_db().cursor(dictionary=True)
        query = '''SELECT r.recommendation_id,
                          r.reason,
                          r.recommendation_score,
                          r.generated_at,
                          m.movie_id,
                          m.title,
                          m.release_year,
                          m.average_rating,
                          m.synopsis
                   FROM Recommendation r
                   JOIN Movie m ON r.movie_id = m.movie_id
                   WHERE r.user_id = %s AND m.status = 'active'
                   ORDER BY r.recommendation_score DESC'''
        cursor.execute(query, (user_id,))
        return jsonify(cursor.fetchall()), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching recommendations for user {user_id}: {e}')
        return jsonify({'error': str(e)}), 500


# ============================================================
# GET /users/<user_id>/history
# Watch history with movie details, ordered by watched_date desc.
# Stories: [Priya-2, Jake-3]
# ============================================================
@users.route('/<int:user_id>/history', methods=['GET'])
def get_watch_history(user_id):
    try:
        cursor = get_db().cursor(dictionary=True)
        query = '''SELECT wh.history_id,
                          wh.watched_date,
                          wh.completion_status,
                          wh.rewatch_count,
                          m.movie_id,
                          m.title,
                          m.release_year
                   FROM WatchHistory wh
                   JOIN Movie m ON wh.movie_id = m.movie_id
                   WHERE wh.user_id = %s
                   ORDER BY wh.watched_date DESC'''
        cursor.execute(query, (user_id,))
        return jsonify(cursor.fetchall()), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching watch history for user {user_id}: {e}')
        return jsonify({'error': str(e)}), 500


# ============================================================
# POST /users/<user_id>/history
# Insert a new WatchHistory row for this user. Body JSON:
# { movie_id, completion_status, rewatch_count (optional) }.
# watched_date defaults to today.
# Stories: [Jake-3]
# ============================================================
@users.route('/<int:user_id>/history', methods=['POST'])
def add_watch_history(user_id):
    try:
        data = request.get_json() or {}
        movie_id = data.get('movie_id')
        completion_status = data.get('completion_status', 'in_progress')
        rewatch_count = data.get('rewatch_count', 0)

        if movie_id is None:
            return jsonify({'error': 'movie_id is required'}), 400

        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = '''INSERT INTO WatchHistory
                       (watched_date, completion_status, rewatch_count, user_id, movie_id)
                   VALUES (%s, %s, %s, %s, %s)'''
        cursor.execute(query, (date.today(), completion_status, rewatch_count, user_id, movie_id))
        db.commit()

        return jsonify({
            'history_id': cursor.lastrowid,
            'user_id': user_id,
            'movie_id': movie_id,
            'watched_date': date.today().isoformat(),
            'completion_status': completion_status,
            'rewatch_count': rewatch_count
        }), 201
    except Exception as e:
        current_app.logger.error(f'Error adding watch history for user {user_id}: {e}')
        return jsonify({'error': str(e)}), 500


# ============================================================
# GET /users/<user_id>/ratings
# All ratings by this user joined with movie title, ordered by
# rating_date desc.
# Stories: [Jake-5]
# ============================================================
@users.route('/<int:user_id>/ratings', methods=['GET'])
def get_user_ratings(user_id):
    try:
        cursor = get_db().cursor(dictionary=True)
        query = '''SELECT r.rating_id,
                          r.rating_value,
                          r.rating_date,
                          m.movie_id,
                          m.title,
                          m.release_year
                   FROM Rating r
                   JOIN Movie m ON r.movie_id = m.movie_id
                   WHERE r.user_id = %s
                   ORDER BY r.rating_date DESC'''
        cursor.execute(query, (user_id,))
        return jsonify(cursor.fetchall()), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching ratings for user {user_id}: {e}')
        return jsonify({'error': str(e)}), 500


# ============================================================
# POST /users/<user_id>/ratings
# Upsert a rating for (user_id, movie_id). After write, recompute
# Movie.average_rating as AVG(rating_value) for that movie.
# Stories: [Jake-5]
# ============================================================
@users.route('/<int:user_id>/ratings', methods=['POST'])
def upsert_user_rating(user_id):
    try:
        data = request.get_json() or {}
        movie_id = data.get('movie_id')
        rating_value = data.get('rating_value')

        if movie_id is None or rating_value is None:
            return jsonify({'error': 'movie_id and rating_value are required'}), 400

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Check if a rating already exists for this (user, movie) pair.
        cursor.execute(
            'SELECT rating_id FROM Rating WHERE user_id = %s AND movie_id = %s',
            (user_id, movie_id)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                '''UPDATE Rating
                   SET rating_value = %s, rating_date = CURRENT_TIMESTAMP
                   WHERE rating_id = %s''',
                (rating_value, existing['rating_id'])
            )
            rating_id = existing['rating_id']
        else:
            cursor.execute(
                '''INSERT INTO Rating (rating_value, user_id, movie_id)
                   VALUES (%s, %s, %s)''',
                (rating_value, user_id, movie_id)
            )
            rating_id = cursor.lastrowid

        # Recalculate the movie's average rating.
        cursor.execute(
            '''UPDATE Movie
               SET average_rating = (
                   SELECT AVG(rating_value) FROM Rating WHERE movie_id = %s
               )
               WHERE movie_id = %s''',
            (movie_id, movie_id)
        )

        db.commit()

        return jsonify({
            'rating_id': rating_id,
            'user_id': user_id,
            'movie_id': movie_id,
            'rating_value': rating_value
        }), 201
    except Exception as e:
        current_app.logger.error(f'Error upserting rating for user {user_id}: {e}')
        return jsonify({'error': str(e)}), 500


# ============================================================
# GET /users/<user_id>/stats
# Aggregate viewing statistics for the user.
# Stories: [Priya-2]
# ============================================================
@users.route('/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    try:
        cursor = get_db().cursor(dictionary=True)

        # total_movies_watched: DISTINCT movies in WatchHistory.
        cursor.execute(
            '''SELECT COUNT(DISTINCT movie_id) AS total_movies_watched
               FROM WatchHistory
               WHERE user_id = %s''',
            (user_id,)
        )
        total_movies_watched = cursor.fetchone()['total_movies_watched'] or 0

        # total_ratings and average_rating_given.
        cursor.execute(
            '''SELECT COUNT(*) AS total_ratings,
                      AVG(rating_value) AS average_rating_given
               FROM Rating
               WHERE user_id = %s''',
            (user_id,)
        )
        rating_row = cursor.fetchone()
        total_ratings = rating_row['total_ratings'] or 0
        avg_rating = rating_row['average_rating_given']
        average_rating_given = float(avg_rating) if avg_rating is not None else None

        # total_reviews (exclude soft-deleted).
        cursor.execute(
            '''SELECT COUNT(*) AS total_reviews
               FROM Review
               WHERE user_id = %s AND is_deleted = 0''',
            (user_id,)
        )
        total_reviews = cursor.fetchone()['total_reviews'] or 0

        # genre_breakdown: movies watched grouped by genre.
        cursor.execute(
            '''SELECT g.genre_name,
                      COUNT(DISTINCT wh.movie_id) AS movies_watched
               FROM WatchHistory wh
               JOIN MovieGenre mg ON wh.movie_id = mg.movie_id
               JOIN Genre g ON mg.genre_id = g.genre_id
               WHERE wh.user_id = %s
               GROUP BY g.genre_id, g.genre_name
               ORDER BY movies_watched DESC''',
            (user_id,)
        )
        genre_breakdown = cursor.fetchall()

        return jsonify({
            'user_id': user_id,
            'total_movies_watched': total_movies_watched,
            'total_ratings': total_ratings,
            'average_rating_given': average_rating_given,
            'total_reviews': total_reviews,
            'genre_breakdown': genre_breakdown
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching stats for user {user_id}: {e}')
        return jsonify({'error': str(e)}), 500
