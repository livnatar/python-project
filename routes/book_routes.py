
from flask import Blueprint, request, jsonify
from services.book_service import BookService
import logging

logger = logging.getLogger(__name__)

# Create blueprint
book_bp = Blueprint('books', __name__)
book_service = BookService()


@book_bp.route('', methods=['GET'])
def get_books():
    """Get all books with optional filtering, search, and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        genre_id = request.args.get('genre_id', type=int)
        available_only = request.args.get('available_only', 'false').lower() == 'true'

        # Get books
        result = book_service.get_all_books(
            page=page,
            per_page=per_page,
            search=search if search else None,
            genre_id=genre_id,
            available_only=available_only
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        logger.error(f"Error in get_books: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book by ID"""
    try:
        result = book_service.get_book_by_id(book_id)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in get_book: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/isbn/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    """Get a specific book by ISBN"""
    try:
        result = book_service.get_book_by_isbn(isbn)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in get_book_by_isbn: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('', methods=['POST'])
def create_book():
    """Create a new book"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Create book
        result = book_service.create_book(data)

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify({'error': result['error'], 'details': result.get('details')}), 400

    except Exception as e:
        logger.error(f"Error in create_book: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update an existing book"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update book
        result = book_service.update_book(book_id, data)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error'], 'details': result.get('details')}), status_code

    except Exception as e:
        logger.error(f"Error in update_book: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    try:
        result = book_service.delete_book(book_id)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in delete_book: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/search', methods=['GET'])
def search_books():
    """Search books by title, author, or ISBN"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({'error': 'Search term (q) is required'}), 400

        # Optional genre filter
        genre_ids = request.args.getlist('genre_id', type=int)

        result = book_service.search_books(search_term, genre_ids if genre_ids else None)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        logger.error(f"Error in search_books: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/available', methods=['GET'])
def get_available_books():
    """Get all currently available books"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        result = book_service.get_available_books(page=page, per_page=per_page)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['error']}), 400

    except Exception as e:
        logger.error(f"Error in get_available_books: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/<int:book_id>/genres', methods=['POST'])
def add_genre_to_book(book_id):
    """Add a genre to a book"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data or 'genre_id' not in data:
            return jsonify({'error': 'Genre ID is required'}), 400

        genre_id = data['genre_id']
        result = book_service.add_genre_to_book(book_id, genre_id)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in add_genre_to_book: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/<int:book_id>/genres/<int:genre_id>', methods=['DELETE'])
def remove_genre_from_book(book_id, genre_id):
    """Remove a genre from a book"""
    try:
        result = book_service.remove_genre_from_book(book_id, genre_id)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in remove_genre_from_book: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@book_bp.route('/<int:book_id>/availability', methods=['PUT'])
def update_book_availability(book_id):
    """Update book availability (for loan/return operations)"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data or 'copies_available' not in data:
            return jsonify({'error': 'copies_available is required'}), 400

        copies_available = data['copies_available']
        result = book_service.update_book_availability(book_id, copies_available)

        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 400
            return jsonify({'error': result['error']}), status_code

    except Exception as e:
        logger.error(f"Error in update_book_availability: {e}")
        return jsonify({'error': 'Internal server error'}), 500
