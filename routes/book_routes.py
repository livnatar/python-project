from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging
from services.book_service import BookService

logger = logging.getLogger(__name__)
book_bp = Blueprint('books', __name__)
book_service = BookService()


# ========== HELPER FUNCTIONS ==========


def create_response(success: bool, message: str, data: Any = None, errors: list = None,
                    status_code: int = 200) -> tuple:
    response = {
        'success': success,
        'message': message
    }
    if data is not None:
        response['data'] = data
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code


def handle_exception(func_name: str, e: Exception) -> tuple:
    logger.error(f"Error in {func_name}: {e}")
    return create_response(
        success=False,
        message='Internal server error',
        errors=['An unexpected error occurred'],
        status_code=500
    )


def handle_service_result(result: Dict, data: Any = None, success_status: int = 200,
                          not_found_status: int = 404) -> tuple:
    if result['success']:
        return create_response(
            success=True,
            message=result.get('message', 'Operation successful'),
            data=data or result.get('data'),
            status_code=success_status
        )
    else:
        # Check if it's a not found error
        error_message = result.get('error', result.get('message', 'Operation failed'))
        status = not_found_status if 'not found' in error_message.lower() else 400

        return create_response(
            success=False,
            message=error_message,
            errors=result.get('details', [error_message]) if isinstance(result.get('details'), list) else [
                error_message],
            status_code=status
        )


def get_validated_json(required_fields: list[str] = None) -> tuple[dict, None] | tuple[None, tuple]:
    data = request.get_json()
    if not data:
        return None, create_response(
            success=False,
            message='No data provided',
            errors=['Request body is required'],
            status_code=400
        )
    if required_fields:
        missing = [field for field in required_fields if field not in data or data[field] is None]
        if missing:
            return None, create_response(
                success=False,
                message='Missing required fields',
                errors=[f"Missing: {', '.join(missing)}"],
                status_code=400
            )
    return data, None


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


@book_bp.route('/<int:book_id>/availability', methods=['PUT'])
def update_book_availability(book_id: int):
    """Update book availability (for loan/return operations)"""
    try:
        data, error = get_validated_json(['copies_available'])
        if error:
            return error

        result = book_service.update_book_availability(book_id, data['copies_available'])
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('update_book_availability', e)
