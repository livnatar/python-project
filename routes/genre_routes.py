from flask import Blueprint, request
import logging
from services.genre_service import GenreService
from utils.route_helpers import create_response, handle_exception, handle_service_result, get_validated_json

logger = logging.getLogger(__name__)
genre_bp = Blueprint('genres', __name__)
genre_service = GenreService()

# ========== ROUTES ==========


@genre_bp.route('', methods=['GET'])
def get_genres():
    """Get all genres with optional search and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()

        result = genre_service.get_all_genres(page=page, per_page=per_page, search=search)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('get_genres', e)


@genre_bp.route('/<int:genre_id>', methods=['GET'])
def get_genre(genre_id: int):
    """Get a specific genre by ID"""
    try:
        result = genre_service.get_genre_by_id(genre_id)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('get_genre', e)


@genre_bp.route('/<string:genre_name>', methods=['GET'])
def get_genre_id(genre_name: str):
    """Get a specific ID by genre name"""
    try:
        result = genre_service.get_id_by_genre(genre_name)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('get_genre_id', e)


@genre_bp.route('', methods=['POST'])
def create_genre():
    """Create a new genre"""
    try:
        data, error = get_validated_json()
        if error:
            return error

        result = genre_service.create_genre(data)
        return handle_service_result(result, success_status=201)
    except Exception as e:
        return handle_exception('create_genre', e)


@genre_bp.route('/<int:genre_id>', methods=['PUT'])
def update_genre(genre_id: int):
    """Update an existing genre"""
    try:
        data, error = get_validated_json()
        if error:
            return error

        result = genre_service.update_genre(genre_id, data)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('update_genre', e)


@genre_bp.route('/<int:genre_id>', methods=['DELETE'])
def delete_genre(genre_id: int):
    """Delete a genre"""
    try:
        result = genre_service.delete_genre(genre_id)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('delete_genre', e)


@genre_bp.route('/search', methods=['GET'])
def search_genres():
    """Search genres by name or description"""
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return create_response(
                success=False,
                message='Search term is required',
                errors=['Query parameter "q" is required'],
                status_code=400
            )

        result = genre_service.search_genres(search_term)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('search_genres', e)


@genre_bp.route('/<int:genre_id>/books', methods=['GET'])
def get_books_in_genre(genre_id: int):
    """Get all books in a specific genre"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        result = genre_service.get_books_in_genre(genre_id, page=page, per_page=per_page)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('get_books_in_genre', e)
