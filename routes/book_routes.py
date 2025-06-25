from flask import Blueprint, request
import logging
from services.book_service import BookService
from utils.route_helpers import create_response, handle_exception, handle_service_result, get_validated_json

logger = logging.getLogger(__name__)
book_bp = Blueprint('books', __name__)
book_service = BookService()

# ========== ROUTES ==========


@book_bp.route('', methods=['GET'])
def get_books():
    """Get all books with optional filtering, search, and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        genre_id = request.args.get('genre_id', type=int)
        available_only = request.args.get('available_only', 'false').lower() == 'true'

        result = book_service.get_all_books(
            page=page,
            per_page=per_page,
            search=search if search else None,
            genre_id=genre_id,
            available_only=available_only
        )
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('get_books', e)


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id: int):
    """Get a specific book by ID"""
    try:
        result = book_service.get_book_by_id(book_id)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('get_book', e)


@book_bp.route('/isbn/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn: str):
    """Get a specific book by ISBN"""
    try:
        result = book_service.get_book_by_isbn(isbn)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('get_book_by_isbn', e)


@book_bp.route('', methods=['POST'])
def create_book():
    """Create a new book"""
    try:
        data, error = get_validated_json()
        if error:
            return error

        result = book_service.create_book(data)
        return handle_service_result(result, success_status=201)
    except Exception as e:
        return handle_exception('create_book', e)


@book_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id: int):
    """Update an existing book"""
    try:
        data, error = get_validated_json()
        if error:
            return error

        result = book_service.update_book(book_id, data)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('update_book', e)


@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id: int):
    """Delete a book"""
    try:
        result = book_service.delete_book(book_id)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('delete_book', e)


@book_bp.route('/search', methods=['GET'])
def search_books():
    """Search books by title, author, or ISBN"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return create_response(
                success=False,
                message='Search term is required',
                errors=['Query parameter "q" is required'],
                status_code=400
            )

        genre_ids = request.args.getlist('genre_id', type=int)
        result = book_service.search_books(search_term, genre_ids if genre_ids else None)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('search_books', e)


@book_bp.route('/available', methods=['GET'])
def get_available_books():
    """Get all currently available books"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        result = book_service.get_available_books(page=page, per_page=per_page)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('get_available_books', e)


@book_bp.route('/<int:book_id>/genres', methods=['POST'])
def add_genre_to_book(book_id: int):
    """Add a genre to a book"""
    try:
        data, error = get_validated_json(['genre_id'])
        if error:
            return error

        result = book_service.add_genre_to_book(book_id, data['genre_id'])
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('add_genre_to_book', e)


@book_bp.route('/<int:book_id>/genres/<int:genre_id>', methods=['DELETE'])
def remove_genre_from_book(book_id: int, genre_id: int):
    """Remove a genre from a book"""
    try:
        result = book_service.remove_genre_from_book(book_id, genre_id)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('remove_genre_from_book', e)