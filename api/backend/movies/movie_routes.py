from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import get_db

movies = Blueprint('movies', __name__)


# ------------------------------------------------------------
# Helper: attach a list of genre names to each movie row.
# Given a list of movie dicts, look up their genres in one
# query and attach a `genres` list to each row.
# ------------------------------------------------------------
def _attach_genres(cursor, movie_rows):
    if not movie_rows:
        return movie_rows

    movie_ids = [row['movie_id'] for row in movie_rows]
    placeholders = ','.join(['%s'] * len(movie_ids))
    query = (
        f"SELECT mg.movie_id, g.genre_id, g.genre_name "
        f"FROM MovieGenre mg "
        f"JOIN Genre g ON mg.genre_id = g.genre_id "
        f"WHERE mg.movie_id IN ({placeholders})"
    )
    cursor.execute(query, tuple(movie_ids))
    genre_rows = cursor.fetchall()

    genres_by_movie = {}
    for gr in genre_rows:
        genres_by_movie.setdefault(gr['movie_id'], []).append({
            'genre_id': gr['genre_id'],
            'genre_name': gr['genre_name']
        })

    for row in movie_rows:
        row['genres'] = genres_by_movie.get(row['movie_id'], [])

    return movie_rows


# ------------------------------------------------------------
# GET /movies
# List movies with optional filters.
# Query params: genre, year, country, language, search
# Stories: Jake-1, Jake-6, Priya-4
# ------------------------------------------------------------
@movies.route('/', methods=['GET'])
def get_movies():
    try:
        cursor = get_db().cursor(dictionary=True)

        genre = request.args.get('genre')
        year = request.args.get('year')
        country = request.args.get('country')
        language = request.args.get('language')
        search = request.args.get('search')

        base_query = (
            "SELECT DISTINCT m.movie_id, m.title, m.release_year, "
            "m.runtime_minutes, m.synopsis, m.country_of_origin, "
            "m.language, m.average_rating, m.created_at, m.status "
            "FROM Movie m "
        )

        joins = ""
        where_clauses = ["m.status = 'active'"]
        params = []

        if genre:
            joins += (
                "JOIN MovieGenre mg ON m.movie_id = mg.movie_id "
                "JOIN Genre g ON mg.genre_id = g.genre_id "
            )
            # Allow filtering by either genre_id (numeric) or genre_name.
            if genre.isdigit():
                where_clauses.append("g.genre_id = %s")
                params.append(int(genre))
            else:
                where_clauses.append("g.genre_name = %s")
                params.append(genre)

        if year:
            where_clauses.append("m.release_year = %s")
            params.append(int(year))

        if country:
            where_clauses.append("m.country_of_origin = %s")
            params.append(country)

        if language:
            where_clauses.append("m.language = %s")
            params.append(language)

        if search:
            where_clauses.append("m.title LIKE %s")
            params.append(f"%{search}%")

        query = base_query + joins
        if where_clauses:
            query += "WHERE " + " AND ".join(where_clauses) + " "
        query += "ORDER BY m.title ASC"

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        results = _attach_genres(cursor, results)

        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_movies: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# GET /movies/<movie_id>
# Get single movie detail with genres.
# Stories: Priya-3
# ------------------------------------------------------------
@movies.route('/<int:movie_id>', methods=['GET'])
def get_movie_detail(movie_id):
    try:
        cursor = get_db().cursor(dictionary=True)

        query = (
            "SELECT movie_id, title, release_year, runtime_minutes, "
            "synopsis, country_of_origin, language, average_rating, "
            "created_at, status "
            "FROM Movie WHERE movie_id = %s"
        )
        cursor.execute(query, (movie_id,))
        movie = cursor.fetchone()

        if not movie:
            return jsonify({'error': 'Movie not found'}), 404

        rows = _attach_genres(cursor, [movie])
        return jsonify(rows[0]), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_movie_detail: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# GET /movies/<movie_id>/similar
# Return movies sharing at least one genre, excluding itself.
# Ordered by average_rating DESC, limit 20.
# Stories: Priya-3
# ------------------------------------------------------------
@movies.route('/<int:movie_id>/similar', methods=['GET'])
def get_similar_movies(movie_id):
    try:
        cursor = get_db().cursor(dictionary=True)

        # Verify the movie exists before doing similarity work.
        cursor.execute("SELECT movie_id FROM Movie WHERE movie_id = %s",
                       (movie_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Movie not found'}), 404

        query = (
            "SELECT DISTINCT m.movie_id, m.title, m.release_year, "
            "m.runtime_minutes, m.synopsis, m.country_of_origin, "
            "m.language, m.average_rating, m.created_at, m.status "
            "FROM Movie m "
            "JOIN MovieGenre mg ON m.movie_id = mg.movie_id "
            "WHERE m.status = 'active' "
            "AND m.movie_id != %s "
            "AND mg.genre_id IN ("
            "    SELECT genre_id FROM MovieGenre WHERE movie_id = %s"
            ") "
            "ORDER BY m.average_rating DESC "
            "LIMIT 20"
        )
        cursor.execute(query, (movie_id, movie_id))
        results = cursor.fetchall()

        results = _attach_genres(cursor, results)

        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_similar_movies: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# GET /movies/<movie_id>/reviews
# Return approved, non-deleted reviews for a movie.
# Stories: Priya-5
# ------------------------------------------------------------
@movies.route('/<int:movie_id>/reviews', methods=['GET'])
def get_movie_reviews(movie_id):
    try:
        cursor = get_db().cursor(dictionary=True)

        query = (
            "SELECT r.review_id, r.review_title, r.review_body, "
            "r.review_date, r.updated_at, r.moderation_status, "
            "r.user_id, r.movie_id, u.username "
            "FROM Review r "
            "JOIN `User` u ON r.user_id = u.user_id "
            "WHERE r.movie_id = %s "
            "AND r.is_deleted = FALSE "
            "AND r.moderation_status = 'approved' "
            "ORDER BY r.review_date DESC"
        )
        cursor.execute(query, (movie_id,))
        results = cursor.fetchall()

        return jsonify(results), 200
    except Exception as e:
        current_app.logger.error(f'Error in get_movie_reviews: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# POST /movies
# Create a new movie with associated genres.
# Stories: Marcus-1
# ------------------------------------------------------------
@movies.route('/', methods=['POST'])
def create_movie():
    try:
        data = request.get_json(silent=True) or {}

        title = data.get('title')
        release_year = data.get('release_year')

        if not title or release_year is None:
            return jsonify({
                'error': 'title and release_year are required'
            }), 400

        runtime_minutes = data.get('runtime_minutes')
        synopsis = data.get('synopsis')
        country_of_origin = data.get('country_of_origin')
        language = data.get('language')
        genre_ids = data.get('genre_ids', []) or []

        db = get_db()
        cursor = db.cursor()

        insert_movie = (
            "INSERT INTO Movie "
            "(title, release_year, runtime_minutes, synopsis, "
            " country_of_origin, language) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(insert_movie, (
            title,
            release_year,
            runtime_minutes,
            synopsis,
            country_of_origin,
            language,
        ))
        new_movie_id = cursor.lastrowid

        if genre_ids:
            insert_genre = (
                "INSERT INTO MovieGenre (movie_id, genre_id) "
                "VALUES (%s, %s)"
            )
            cursor.executemany(
                insert_genre,
                [(new_movie_id, int(gid)) for gid in genre_ids]
            )

        db.commit()

        return jsonify({
            'movie_id': new_movie_id,
            'message': 'Movie created successfully'
        }), 201
    except Exception as e:
        current_app.logger.error(f'Error in create_movie: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# PUT /movies/<movie_id>
# Update one or more movie fields.
# Stories: Marcus-2
# ------------------------------------------------------------
@movies.route('/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        data = request.get_json(silent=True) or {}

        allowed_fields = [
            'title',
            'release_year',
            'runtime_minutes',
            'synopsis',
            'country_of_origin',
            'language',
            'status',
        ]

        set_clauses = []
        params = []
        for field in allowed_fields:
            if field in data:
                set_clauses.append(f"{field} = %s")
                params.append(data[field])

        if not set_clauses:
            return jsonify({'error': 'No valid fields provided'}), 400

        db = get_db()
        cursor = db.cursor()

        # Confirm the movie exists first, so we can return a clean 404.
        cursor.execute("SELECT movie_id FROM Movie WHERE movie_id = %s",
                       (movie_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Movie not found'}), 404

        params.append(movie_id)
        query = (
            f"UPDATE Movie SET {', '.join(set_clauses)} "
            f"WHERE movie_id = %s"
        )
        cursor.execute(query, tuple(params))
        db.commit()

        return jsonify({
            'movie_id': movie_id,
            'message': 'Movie updated successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error in update_movie: {e}')
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# DELETE /movies/<movie_id>
# Soft delete by setting status = 'removed'.
# Stories: Marcus-3
# ------------------------------------------------------------
@movies.route('/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT movie_id FROM Movie WHERE movie_id = %s",
                       (movie_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Movie not found'}), 404

        cursor.execute(
            "UPDATE Movie SET status = 'removed' WHERE movie_id = %s",
            (movie_id,)
        )
        db.commit()

        return jsonify({
            'movie_id': movie_id,
            'message': 'Movie removed successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f'Error in delete_movie: {e}')
        return jsonify({'error': str(e)}), 500
