#------------------------------------------------------------
# Recommendation routes.
#
# Endpoints (prefix: /recommendations):
#   GET  /user/<user_id>            - List recommendations for a user (Jake-2)
#   GET  /<rec_id>                  - Get single recommendation (Jake-2)
#   POST /<rec_id>/click            - Record a click on a recommendation (Elena-3)
#   GET  /generate/<user_id>        - Generate new recommendations (Jake-2)
#   GET  /<rec_id>/clicks           - Get all clicks for a recommendation (Elena-3)
#------------------------------------------------------------
from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import get_db

recommendations = Blueprint('recommendations', __name__)


#------------------------------------------------------------
# GET /recommendations/user/<user_id>
# Return all recommendations for a user, joined with movie info,
# ordered by recommendation_score DESC.
# Stories: [Jake-2]
#------------------------------------------------------------
@recommendations.route('/user/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    try:
        cursor = get_db().cursor(dictionary=True)
        query = '''
            SELECT r.recommendation_id,
                   r.reason,
                   r.recommendation_score,
                   r.generated_at,
                   r.user_id,
                   r.movie_id,
                   m.title,
                   m.release_year,
                   m.runtime_minutes,
                   m.synopsis,
                   m.average_rating,
                   m.status AS movie_status
            FROM Recommendation r
            JOIN Movie m ON r.movie_id = m.movie_id
            WHERE r.user_id = %s
            ORDER BY r.recommendation_score DESC
        '''
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f'get_user_recommendations failed: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# GET /recommendations/<rec_id>
# Return a single recommendation with full movie detail.
# 404 if not found.
# Stories: [Jake-2]
#------------------------------------------------------------
@recommendations.route('/<int:rec_id>', methods=['GET'])
def get_recommendation(rec_id):
    try:
        cursor = get_db().cursor(dictionary=True)
        query = '''
            SELECT r.recommendation_id,
                   r.reason,
                   r.recommendation_score,
                   r.generated_at,
                   r.user_id,
                   r.movie_id,
                   m.title,
                   m.release_year,
                   m.runtime_minutes,
                   m.synopsis,
                   m.country_of_origin,
                   m.language,
                   m.average_rating,
                   m.created_at AS movie_created_at,
                   m.status AS movie_status
            FROM Recommendation r
            JOIN Movie m ON r.movie_id = m.movie_id
            WHERE r.recommendation_id = %s
        '''
        cursor.execute(query, (rec_id,))
        row = cursor.fetchone()
        if row is None:
            return jsonify({'error': 'Recommendation not found'}), 404
        return jsonify(row), 200
    except Exception as e:
        current_app.logger.error(f'get_recommendation failed: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# POST /recommendations/<rec_id>/click
# Record a click on a recommendation.
# Body: {"user_id": <int>}
# Returns 201 with the new click_id.
# Stories: [Elena-3]
#------------------------------------------------------------
@recommendations.route('/<int:rec_id>/click', methods=['POST'])
def record_click(rec_id):
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get('user_id')
        if user_id is None:
            return jsonify({'error': 'user_id is required'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO RecommendationClick (recommendation_id, user_id) VALUES (%s, %s)',
            (rec_id, user_id),
        )
        db.commit()
        click_id = cursor.lastrowid
        return jsonify({
            'click_id': click_id,
            'recommendation_id': rec_id,
            'user_id': user_id,
            'message': 'Click recorded'
        }), 201
    except Exception as e:
        current_app.logger.error(f'record_click failed: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# GET /recommendations/generate/<user_id>
# Generate up to 5 new content-based recommendations:
#   1. Find user's top 3 genres by avg rating.
#   2. Find active, unwatched, not-already-recommended movies in those genres.
#   3. Insert new Recommendation rows with a score derived from
#      the movie's average_rating.
# Returns the newly created recommendations.
# Stories: [Jake-2]
#------------------------------------------------------------
@recommendations.route('/generate/<int:user_id>', methods=['GET'])
def generate_recommendations(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Step 1: find user's top 3 genres by average rating.
        top_genres_query = '''
            SELECT mg.genre_id, AVG(r.rating_value) AS avg_rating
            FROM Rating r
            JOIN MovieGenre mg ON r.movie_id = mg.movie_id
            WHERE r.user_id = %s
            GROUP BY mg.genre_id
            ORDER BY avg_rating DESC
            LIMIT 3
        '''
        cursor.execute(top_genres_query, (user_id,))
        top_genres = cursor.fetchall()

        if not top_genres:
            return jsonify({
                'message': 'No ratings found for user - cannot generate recommendations',
                'recommendations': []
            }), 200

        genre_ids = [g['genre_id'] for g in top_genres]

        # Step 2: find candidate movies in those genres the user hasn't
        # watched or already been recommended. Use dynamic placeholders
        # for the IN (...) list because mysql.connector doesn't expand
        # a Python list into multiple parameters.
        placeholders = ', '.join(['%s'] * len(genre_ids))
        candidates_query = f'''
            SELECT DISTINCT m.movie_id, m.title, m.average_rating
            FROM Movie m
            JOIN MovieGenre mg ON m.movie_id = mg.movie_id
            WHERE mg.genre_id IN ({placeholders})
              AND m.status = 'active'
              AND m.movie_id NOT IN (
                    SELECT movie_id FROM WatchHistory WHERE user_id = %s
              )
              AND m.movie_id NOT IN (
                    SELECT movie_id FROM Recommendation WHERE user_id = %s
              )
            ORDER BY m.average_rating DESC
            LIMIT 5
        '''
        params = tuple(genre_ids) + (user_id, user_id)
        cursor.execute(candidates_query, params)
        candidates = cursor.fetchall()

        if not candidates:
            return jsonify({
                'message': 'No new candidate movies available for this user',
                'recommendations': []
            }), 200

        # Step 3: insert a Recommendation row per candidate.
        # Score = average_rating (falls back to 5.0 if NULL) scaled to
        # DECIMAL(5,2) range; clamp defensively.
        write_cursor = db.cursor()
        new_ids = []
        for movie in candidates:
            avg = movie['average_rating']
            score = float(avg) if avg is not None else 5.0
            if score < 0:
                score = 0.0
            if score > 999.99:
                score = 999.99
            reason = f"Recommended because you enjoy similar genres ({movie['title']})"
            write_cursor.execute(
                '''
                INSERT INTO Recommendation
                    (reason, recommendation_score, user_id, movie_id)
                VALUES (%s, %s, %s, %s)
                ''',
                (reason, score, user_id, movie['movie_id']),
            )
            new_ids.append(write_cursor.lastrowid)
        db.commit()

        # Return the freshly created recommendations joined to movie info.
        if new_ids:
            id_placeholders = ', '.join(['%s'] * len(new_ids))
            fetch_query = f'''
                SELECT r.recommendation_id,
                       r.reason,
                       r.recommendation_score,
                       r.generated_at,
                       r.user_id,
                       r.movie_id,
                       m.title,
                       m.release_year,
                       m.average_rating
                FROM Recommendation r
                JOIN Movie m ON r.movie_id = m.movie_id
                WHERE r.recommendation_id IN ({id_placeholders})
                ORDER BY r.recommendation_score DESC
            '''
            cursor.execute(fetch_query, tuple(new_ids))
            created = cursor.fetchall()
        else:
            created = []

        return jsonify({
            'message': f'Generated {len(created)} new recommendations',
            'top_genres': genre_ids,
            'recommendations': created
        }), 200
    except Exception as e:
        current_app.logger.error(f'generate_recommendations failed: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# GET /recommendations/<rec_id>/clicks
# List all clicks for a specific recommendation, joined with
# the clicking user's basic info.
# Stories: [Elena-3]
#------------------------------------------------------------
@recommendations.route('/<int:rec_id>/clicks', methods=['GET'])
def get_recommendation_clicks(rec_id):
    try:
        cursor = get_db().cursor(dictionary=True)
        query = '''
            SELECT rc.click_id,
                   rc.clicked_at,
                   rc.recommendation_id,
                   rc.user_id,
                   u.username,
                   u.email,
                   u.role
            FROM RecommendationClick rc
            JOIN `User` u ON rc.user_id = u.user_id
            WHERE rc.recommendation_id = %s
            ORDER BY rc.clicked_at DESC
        '''
        cursor.execute(query, (rec_id,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f'get_recommendation_clicks failed: {e}')
        return jsonify({'error': str(e)}), 500
