#------------------------------------------------------------
# Admin Blueprint
#
# Endpoints for administrative actions: user management,
# review moderation, and audit log retrieval. Every mutating
# route records an AdminLog entry for auditability.
#
# Related user stories:
#   - Marcus-4: moderate reviews flagged by users
#   - Marcus-5: manage user accounts (status changes)
#   - Marcus-6: view recent admin actions for audit
#
# Blueprint variable is `admin_bp` (not `admin`) to avoid
# shadowing conventional names; registered with url_prefix
# '/admin' in rest_entry.py.
#------------------------------------------------------------
from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import get_db

admin_bp = Blueprint('admin', __name__)


#------------------------------------------------------------
# GET /admin/users
# List all users in the system (regardless of role).
# Optional query params:
#   status  - filter by user status (active/inactive/banned)
#   role    - filter by role (casual/enthusiast/admin/analyst)
# Returns user_id, username, email, role, join_date, status.
# Stories: [Marcus-5, landing page]
#------------------------------------------------------------
@admin_bp.route('/users', methods=['GET'])
def list_users():
    try:
        status = request.args.get('status')
        role = request.args.get('role')

        query = '''
            SELECT user_id,
                   username,
                   email,
                   role,
                   join_date,
                   status
            FROM `User`
            WHERE 1=1
        '''
        params = []

        if status:
            query += ' AND status = %s'
            params.append(status)
        if role:
            query += ' AND role = %s'
            params.append(role)

        query += ' ORDER BY join_date DESC'

        cursor = get_db().cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()

        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f'Error listing users: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# PUT /admin/users/<user_id>
# Update a user's status (active / inactive / banned) and
# record an AdminLog entry for the action.
# Body: {status, admin_user_id, notes (optional)}
# Stories: [Marcus-5]
#------------------------------------------------------------
@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user_status(user_id):
    try:
        data = request.get_json() or {}
        required = ['status', 'admin_user_id']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400

        new_status = data['status']
        admin_user_id = data['admin_user_id']
        notes = data.get('notes')

        db = get_db()
        cursor = db.cursor()

        # Verify the target user exists so we can 404 cleanly
        cursor.execute(
            'SELECT user_id FROM `User` WHERE user_id = %s',
            (user_id,)
        )
        if cursor.fetchone() is None:
            cursor.close()
            return jsonify({'error': 'User not found'}), 404

        cursor.execute(
            'UPDATE `User` SET status = %s WHERE user_id = %s',
            (new_status, user_id)
        )

        # Audit trail: record the admin action
        cursor.execute(
            '''
            INSERT INTO AdminLog
                (action_type, target_table, target_id,
                 notes, admin_user_id)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (
                'update_user_status',
                'User',
                user_id,
                notes,
                admin_user_id,
            )
        )

        db.commit()
        cursor.close()

        return jsonify({
            'user_id': user_id,
            'status': new_status,
            'message': 'User status updated successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(
            f'Error updating user {user_id} status: {e}'
        )
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# GET /admin/logs
# Retrieve recent AdminLog entries, joined with the
# admin's username. Newest first.
# Optional query params:
#   limit        - max rows (default 50)
#   action_type  - filter by action_type string
# Stories: [Marcus-6]
#------------------------------------------------------------
@admin_bp.route('/logs', methods=['GET'])
def list_logs():
    try:
        limit = request.args.get('limit', default=50, type=int)
        action_type = request.args.get('action_type')

        query = '''
            SELECT l.log_id,
                   l.action_type,
                   l.target_table,
                   l.target_id,
                   l.action_timestamp,
                   l.notes,
                   l.admin_user_id,
                   u.username AS admin_username
            FROM AdminLog l
            JOIN `User` u ON l.admin_user_id = u.user_id
            WHERE 1=1
        '''
        params = []

        if action_type:
            query += ' AND l.action_type = %s'
            params.append(action_type)

        query += ' ORDER BY l.action_timestamp DESC LIMIT %s'
        params.append(limit)

        cursor = get_db().cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()

        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f'Error listing admin logs: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# GET /admin/reviews/flagged
# Return reviews that have at least one pending ReviewFlag.
# Includes flag_reason, the flagging user's username, and the
# review content for moderator review.
# Stories: [Marcus-4]
#------------------------------------------------------------
@admin_bp.route('/reviews/flagged', methods=['GET'])
def list_flagged_reviews():
    try:
        query = '''
            SELECT f.flag_id,
                   f.flag_reason,
                   f.flag_date,
                   f.flag_status,
                   f.flagged_by_user_id,
                   flagger.username AS flagged_by,
                   r.review_id,
                   r.review_title,
                   r.review_body,
                   r.review_date,
                   r.moderation_status,
                   r.is_deleted,
                   r.user_id AS review_user_id,
                   author.username AS review_author,
                   r.movie_id,
                   m.title AS movie_title
            FROM ReviewFlag f
            JOIN Review r ON f.review_id = r.review_id
            JOIN `User` flagger ON f.flagged_by_user_id = flagger.user_id
            JOIN `User` author ON r.user_id = author.user_id
            JOIN Movie m ON r.movie_id = m.movie_id
            WHERE f.flag_status = 'pending'
            ORDER BY f.flag_date DESC
        '''
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f'Error listing flagged reviews: {e}')
        return jsonify({'error': str(e)}), 500


#------------------------------------------------------------
# PUT /admin/reviews/<review_id>/moderate
# Moderate a review. Sets Review.moderation_status to
# 'approved' or 'rejected'. If rejected, also soft-deletes
# the review (is_deleted=TRUE). Marks any related ReviewFlag
# rows as 'reviewed' and records an AdminLog entry.
# Body: {moderation_status, admin_user_id, notes (optional)}
# Stories: [Marcus-4]
#------------------------------------------------------------
@admin_bp.route('/reviews/<int:review_id>/moderate', methods=['PUT'])
def moderate_review(review_id):
    try:
        data = request.get_json() or {}
        required = ['moderation_status', 'admin_user_id']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400

        moderation_status = data['moderation_status']
        admin_user_id = data['admin_user_id']
        notes = data.get('notes')

        if moderation_status not in ('approved', 'rejected'):
            return jsonify({
                'error': "moderation_status must be 'approved' or 'rejected'"
            }), 400

        db = get_db()
        cursor = db.cursor()

        # Verify the review exists first
        cursor.execute(
            'SELECT review_id FROM Review WHERE review_id = %s',
            (review_id,)
        )
        if cursor.fetchone() is None:
            cursor.close()
            return jsonify({'error': 'Review not found'}), 404

        # Rejected reviews are also soft-deleted; approved reviews
        # leave is_deleted untouched.
        if moderation_status == 'rejected':
            cursor.execute(
                '''
                UPDATE Review
                SET moderation_status = %s,
                    is_deleted = TRUE,
                    updated_at = NOW()
                WHERE review_id = %s
                ''',
                (moderation_status, review_id)
            )
        else:
            cursor.execute(
                '''
                UPDATE Review
                SET moderation_status = %s,
                    updated_at = NOW()
                WHERE review_id = %s
                ''',
                (moderation_status, review_id)
            )

        # Mark any pending flags on this review as reviewed so they
        # drop off the moderation queue.
        cursor.execute(
            '''
            UPDATE ReviewFlag
            SET flag_status = 'reviewed'
            WHERE review_id = %s AND flag_status = 'pending'
            ''',
            (review_id,)
        )

        # Audit trail
        cursor.execute(
            '''
            INSERT INTO AdminLog
                (action_type, target_table, target_id,
                 notes, admin_user_id)
            VALUES (%s, %s, %s, %s, %s)
            ''',
            (
                'moderate_review',
                'Review',
                review_id,
                notes,
                admin_user_id,
            )
        )

        db.commit()
        cursor.close()

        return jsonify({
            'review_id': review_id,
            'moderation_status': moderation_status,
            'message': 'Review moderated successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(
            f'Error moderating review {review_id}: {e}'
        )
        return jsonify({'error': str(e)}), 500
