#------------------------------------------------------------
# Watchlists Blueprint
#
# Routes for managing user watchlists and their items.
# Supports the [Jake-4] user stories: a user can view their
# watchlists, create new ones, list items in a watchlist, add
# movies, and remove movies.
#------------------------------------------------------------
from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import get_db

watchlists = Blueprint('watchlists', __name__)


#------------------------------------------------------------
# GET /watchlists/user/<user_id>
# Return every watchlist owned by the given user, newest first.
# Stories: [Jake-4]
#------------------------------------------------------------
@watchlists.route('/user/<int:user_id>', methods=['GET'])
def get_user_watchlists(user_id):
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            '''
            SELECT watchlist_id, name, created_at, user_id
            FROM Watchlist
            WHERE user_id = %s
            ORDER BY created_at DESC
            ''',
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f'get_user_watchlists failed: {e}')
        return jsonify({'error': 'Failed to fetch watchlists'}), 500


#------------------------------------------------------------
# POST /watchlists/
# Create a new watchlist for a user.
# Body: { "user_id": int, "name": str }
# Stories: [Jake-4]
#------------------------------------------------------------
@watchlists.route('/', methods=['POST'])
def create_watchlist():
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get('user_id')
        name = data.get('name')

        if user_id is None or not name:
            return jsonify({'error': 'user_id and name are required'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            '''
            INSERT INTO Watchlist (name, user_id)
            VALUES (%s, %s)
            ''',
            (name, user_id)
        )
        new_id = cursor.lastrowid
        db.commit()
        cursor.close()

        return jsonify({
            'watchlist_id': new_id,
            'user_id': user_id,
            'name': name
        }), 201
    except Exception as e:
        current_app.logger.error(f'create_watchlist failed: {e}')
        return jsonify({'error': 'Failed to create watchlist'}), 500


#------------------------------------------------------------
# GET /watchlists/<watchlist_id>/items
# Return every item in a watchlist, joined with movie details
# (title, release_year, runtime_minutes, average_rating).
# Ordered by most recently added first.
# Stories: [Jake-4]
#------------------------------------------------------------
@watchlists.route('/<int:watchlist_id>/items', methods=['GET'])
def get_watchlist_items(watchlist_id):
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(
            '''
            SELECT
                wi.watchlist_item_id,
                wi.watchlist_id,
                wi.movie_id,
                wi.added_at,
                m.title,
                m.release_year,
                m.runtime_minutes,
                m.average_rating
            FROM WatchlistItem wi
            JOIN Movie m ON m.movie_id = wi.movie_id
            WHERE wi.watchlist_id = %s
            ORDER BY wi.added_at DESC
            ''',
            (watchlist_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f'get_watchlist_items failed: {e}')
        return jsonify({'error': 'Failed to fetch watchlist items'}), 500


#------------------------------------------------------------
# POST /watchlists/<watchlist_id>/items
# Add a movie to an existing watchlist.
# Body: { "movie_id": int }
# Stories: [Jake-4]
#------------------------------------------------------------
@watchlists.route('/<int:watchlist_id>/items', methods=['POST'])
def add_watchlist_item(watchlist_id):
    try:
        data = request.get_json(silent=True) or {}
        movie_id = data.get('movie_id')

        if movie_id is None:
            return jsonify({'error': 'movie_id is required'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            '''
            INSERT INTO WatchlistItem (watchlist_id, movie_id)
            VALUES (%s, %s)
            ''',
            (watchlist_id, movie_id)
        )
        new_item_id = cursor.lastrowid
        db.commit()
        cursor.close()

        return jsonify({
            'watchlist_item_id': new_item_id,
            'watchlist_id': watchlist_id,
            'movie_id': movie_id
        }), 201
    except Exception as e:
        current_app.logger.error(f'add_watchlist_item failed: {e}')
        return jsonify({'error': 'Failed to add item to watchlist'}), 500


#------------------------------------------------------------
# DELETE /watchlists/<watchlist_id>/items/<item_id>
# Hard-delete a single item from a watchlist. The item must
# belong to the specified watchlist, otherwise 404.
# Stories: [Jake-4]
#------------------------------------------------------------
@watchlists.route('/<int:watchlist_id>/items/<int:item_id>', methods=['DELETE'])
def delete_watchlist_item(watchlist_id, item_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            '''
            DELETE FROM WatchlistItem
            WHERE watchlist_item_id = %s AND watchlist_id = %s
            ''',
            (item_id, watchlist_id)
        )
        affected = cursor.rowcount
        db.commit()
        cursor.close()

        if affected == 0:
            return jsonify({'error': 'Watchlist item not found'}), 404

        return jsonify({
            'message': 'Item removed',
            'watchlist_item_id': item_id,
            'watchlist_id': watchlist_id
        }), 200
    except Exception as e:
        current_app.logger.error(f'delete_watchlist_item failed: {e}')
        return jsonify({'error': 'Failed to delete watchlist item'}), 500
