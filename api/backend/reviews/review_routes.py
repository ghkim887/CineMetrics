#------------------------------------------------------------
# Reviews Blueprint
#
# Endpoints for managing movie reviews, including soft-delete,
# moderation-status updates, and user review flagging.
#
# Related user stories:
#   - Priya-1: submit a review
#   - Priya-5: browse / read reviews with user + movie context
#   - Priya-6: edit or delete own review
#   - Marcus-4: moderate reviews and review flags
#------------------------------------------------------------
from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import get_db

reviews = Blueprint('reviews', __name__)


#------------------------------------------------------------
# GET /reviews
# List reviews with optional filters:
#   status (moderation_status), user_id, movie_id,
#   include_deleted (default false)
# Joins User.username and Movie.title. Orders by review_date DESC.
# Stories: [Marcus-4, Priya-5]
#------------------------------------------------------------
@reviews.route('/', methods=['GET'])
def list_reviews():
    try:
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        movie_id = request.args.get('movie_id', type=int)
        include_deleted = request.args.get(
            'include_deleted', 'false'
        ).lower() == 'true'

        query = '''
            SELECT r.review_id,
                   r.review_title,
                   r.review_body,
                   r.review_date,
                   r.updated_at,
                   r.is_deleted,
                   r.moderation_status,
                   r.user_id,
                   u.username,
                   r.movie_id,
                   m.title AS movie_title
            FROM Review r
            JOIN `User` u ON r.user_id = u.user_id
            JOIN Movie m ON r.movie_id = m.movie_id
            WHERE 1=1
        '''
        params = []

        if not include_deleted:
            query += ' AND r.is_deleted = FALSE'
        if status:
            query += ' AND r.moderation_status = %s'
            params.append(status)
        if user_id is not None:
            query += ' AND r.user_id = %s'
            params.append(user_id)
        if movie_id is not None:
            query += ' AND r.movie_id = %s'
            params.append(movie_id)

        query += ' ORDER BY r.review_date DESC'

        cursor = get_db().cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()

        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f'Error listing reviews: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# POST /reviews
# Create a new review. Defaults moderation_status='pending',
# is_deleted=FALSE. Returns 201 with the new review_id.
# Body: {user_id, movie_id, review_title, review_body}
# Stories: [Priya-1]
#------------------------------------------------------------
@reviews.route('/', methods=['POST'])
def create_review():
    try:
        data = request.get_json() or {}
        required = ['user_id', 'movie_id', 'review_title', 'review_body']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400

        query = '''
            INSERT INTO Review
                (review_title, review_body, moderation_status,
                 is_deleted, user_id, movie_id)
            VALUES (%s, %s, 'pending', FALSE, %s, %s)
        '''
        params = (
            data['review_title'],
            data['review_body'],
            data['user_id'],
            data['movie_id'],
        )

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        new_id = cursor.lastrowid
        db.commit()
        cursor.close()

        return jsonify({
            'review_id': new_id,
            'message': 'Review created successfully'
        }), 201
    except Exception as e:
        current_app.logger.error(f'Error creating review: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# GET /reviews/<review_id>
# Return single review with user + movie info. 404 if not found.
# Stories: [Priya-5]
#------------------------------------------------------------
@reviews.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    try:
        query = '''
            SELECT r.review_id,
                   r.review_title,
                   r.review_body,
                   r.review_date,
                   r.updated_at,
                   r.is_deleted,
                   r.moderation_status,
                   r.user_id,
                   u.username,
                   r.movie_id,
                   m.title AS movie_title
            FROM Review r
            JOIN `User` u ON r.user_id = u.user_id
            JOIN Movie m ON r.movie_id = m.movie_id
            WHERE r.review_id = %s
        '''
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(query, (review_id,))
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return jsonify({'error': 'Review not found'}), 404

        return jsonify(row), 200
    except Exception as e:
        current_app.logger.error(f'Error fetching review {review_id}: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# PUT /reviews/<review_id>
# Partial update of review_title, review_body, and/or
# moderation_status. Sets updated_at = NOW().
# Stories: [Priya-6, Marcus-4]
#------------------------------------------------------------
@reviews.route('/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    try:
        data = request.get_json() or {}
        allowed = ['review_title', 'review_body', 'moderation_status']
        fields = {k: v for k, v in data.items() if k in allowed}

        if not fields:
            return jsonify({
                'error': 'No updatable fields provided'
            }), 400

        db = get_db()
        cursor = db.cursor()

        # Verify existence first so we can return 404 cleanly
        cursor.execute(
            'SELECT review_id FROM Review WHERE review_id = %s',
            (review_id,)
        )
        if cursor.fetchone() is None:
            cursor.close()
            return jsonify({'error': 'Review not found'}), 404

        set_clauses = [f'{col} = %s' for col in fields.keys()]
        set_clauses.append('updated_at = NOW()')
        params = list(fields.values()) + [review_id]

        query = f'''
            UPDATE Review
            SET {", ".join(set_clauses)}
            WHERE review_id = %s
        '''
        cursor.execute(query, tuple(params))
        db.commit()
        cursor.close()

        return jsonify({
            'review_id': review_id,
            'message': 'Review updated successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error updating review {review_id}: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# DELETE /reviews/<review_id>
# Soft delete: is_deleted=TRUE, updated_at=NOW().
# Stories: [Priya-6]
#------------------------------------------------------------
@reviews.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            'SELECT review_id FROM Review WHERE review_id = %s',
            (review_id,)
        )
        if cursor.fetchone() is None:
            cursor.close()
            return jsonify({'error': 'Review not found'}), 404

        cursor.execute(
            '''
            UPDATE Review
            SET is_deleted = TRUE, updated_at = NOW()
            WHERE review_id = %s
            ''',
            (review_id,)
        )
        db.commit()
        cursor.close()

        return jsonify({
            'review_id': review_id,
            'message': 'Review soft-deleted successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error deleting review {review_id}: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# POST /reviews/<review_id>/flags
# Flag a review for moderation. flag_status defaults to 'pending'.
# Body: {flag_reason, flagged_by_user_id}
# Stories: [Marcus-4]
#------------------------------------------------------------
@reviews.route('/<int:review_id>/flags', methods=['POST'])
def flag_review(review_id):
    try:
        data = request.get_json() or {}
        required = ['flag_reason', 'flagged_by_user_id']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400

        db = get_db()
        cursor = db.cursor()

        # Make sure the review actually exists before flagging it
        cursor.execute(
            'SELECT review_id FROM Review WHERE review_id = %s',
            (review_id,)
        )
        if cursor.fetchone() is None:
            cursor.close()
            return jsonify({'error': 'Review not found'}), 404

        cursor.execute(
            '''
            INSERT INTO ReviewFlag
                (flag_reason, flag_status, review_id, flagged_by_user_id)
            VALUES (%s, 'pending', %s, %s)
            ''',
            (
                data['flag_reason'],
                review_id,
                data['flagged_by_user_id'],
            )
        )
        new_flag_id = cursor.lastrowid
        db.commit()
        cursor.close()

        return jsonify({
            'flag_id': new_flag_id,
            'review_id': review_id,
            'message': 'Review flagged successfully'
        }), 201
    except Exception as e:
        current_app.logger.error(
            f'Error flagging review {review_id}: {e}'
        )
        return jsonify({'error': str(e)}), 500
