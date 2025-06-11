from flask import Blueprint, request, jsonify
from services.genre_service import GenreService
import logging

logger = logging.getLogger(__name__)

# Create blueprint
genre_bp = Blueprint('genres', __name__)
genre_service = GenreService()


@genre_bp.route('', methods=['GET'])
def get_genres():
    """Get all genres with optional search and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()

        # Get genres
        result = genre_service.get_all_genres(page=page, per_page=per_page, search=search)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        logger.error(f"Error in get_genres: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@genre_bp.route('/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    """Get a specific genre by ID"""
    try:
        result = genre_service.get_genre_by_id(genre_id)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in get_genre: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@genre_bp.route('/<string:genre_name>', methods=['GET'])
def get_genre_id(genre_name):
    """Get a specific ID by genre"""
    try:
        result = genre_service.get_id_by_genre(genre_name)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in get_genre_id: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@genre_bp.route('', methods=['POST'])
def create_genre():
    """Create a new genre"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create genre
        result = genre_service.create_genre(data)

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify({'error': result['error'], 'details': result.get('details')}), 400

    except Exception as e:
        logger.error(f"Error in create_genre: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@genre_bp.route('/<int:genre_id>', methods=['PUT'])
def update_genre(genre_id):
    """Update an existing genre"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update genre
        result = genre_service.update_genre(genre_id, data)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error'], 'details': result.get('details')}), status_code

    except Exception as e:
        logger.error(f"Error in update_genre: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@genre_bp.route('/<int:genre_id>', methods=['DELETE'])
def delete_genre(genre_id):
    """Delete a genre"""
    try:
        result = genre_service.delete_genre(genre_id)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in delete_genre: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@genre_bp.route('/search', methods=['GET'])
def search_genres():
    """Search genres by name or description"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({'error': 'Search term (q) is required'}), 400

        result = genre_service.search_genres(search_term)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        logger.error(f"Error in search_genres: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@genre_bp.route('/<int:genre_id>/books', methods=['GET'])
def get_books_in_genre(genre_id):
    """Get all books in a specific genre"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Get books in genre
        result = genre_service.get_books_in_genre(genre_id, page=page, per_page=per_page)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in get_books_in_genre: {e}")
        return jsonify({'error': 'Internal server error'}), 500
