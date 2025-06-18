
from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging
from services.user_service import UserService
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)
user_bp = Blueprint('users', __name__)
user_service = UserService()

# ========== HELPER FUNCTIONS ==========


def create_response(success: bool, message: str, data: Any = None, errors: list = None, status_code: int = 200) -> tuple:
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


def handle_service_result(result: Dict, data: Any = None, success_status: int = 200, not_found_status: int = 404) -> tuple:
    if result['success']:
        return create_response(
            success=True,
            message=result['message'],
            data=data,
            status_code=success_status
        )
    else:
        status = not_found_status if 'not found' in result['message'].lower() else 400
        return create_response(
            success=False,
            message=result['message'],
            errors=result.get('errors', []),
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


@user_bp.route('', methods=['POST'])
def create_user():
    try:
        data, error = get_validated_json()
        if error:
            return error
        user, result = user_service.create_user(data)
        data = user.to_dict() if user else None
        return handle_service_result(result, data=data, success_status=201)
    except Exception as e:
        return handle_exception('create_user', e)


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    try:
        user, result = user_service.get_user_by_id(user_id)
        data = user.to_dict() if user else None
        return handle_service_result(result, data=data)
    except Exception as e:
        return handle_exception('get_user', e)


@user_bp.route('', methods=['GET'])
def get_all_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()

        if search:
            users, result = user_service.search_users(search, page, per_page)
        else:
            users, result = user_service.get_all_users(page, per_page)

        users_data = [user.to_dict() for user in users]
        return handle_service_result(result, data={
            'users': users_data,
            'pagination': result.get('pagination', {}),
            'search_term': result.get('search_term')
        })

    except Exception as e:
        return handle_exception('get_all_users', e)


@user_bp.route('/username/<username>', methods=['GET'])
def get_user_by_username(username: str):
    try:
        user, result = user_service.get_user_by_username(username)
        data = user.to_dict() if user else None
        return handle_service_result(result, data=data)
    except Exception as e:
        return handle_exception('get_user_by_username', e)


@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id: int):
    try:
        data, error = get_validated_json()
        if error:
            return error
        user, result = user_service.update_user(user_id, data)
        data = user.to_dict() if user else None
        return handle_service_result(result, data=data)
    except Exception as e:
        return handle_exception('update_user', e)


@user_bp.route('/<int:user_id>/password', methods=['PUT'])
def update_user_password(user_id: int):
    try:
        data, error = get_validated_json(['current_password', 'new_password'])
        if error:
            return error

        success, result = user_service.update_user_password(
            user_id,
            data['current_password'],
            data['new_password']
        )
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('update_user_password', e)


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id: int):
    try:
        success, result = user_service.delete_user(user_id)
        return handle_service_result(result)
    except Exception as e:
        return handle_exception('delete_user', e)


@user_bp.route('/search', methods=['GET'])
def search_users():
    try:
        search_term = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if not search_term:
            return create_response(
                success=False,
                message='Search term is required',
                errors=['Query parameter "q" is required'],
                status_code=400
            )

        users, result = user_service.search_users(search_term, page, per_page)
        users_data = [user.to_dict() for user in users]
        return handle_service_result(result, data={
            'users': users_data,
            'pagination': result.get('pagination', {}),
            'search_term': result.get('search_term')
        })
    except Exception as e:
        return handle_exception('search_users', e)


@user_bp.route('/authenticate', methods=['POST'])
def authenticate_user():
    try:
        data, error = get_validated_json(['username', 'password'])
        if error:
            return error

        user, result = user_service.authenticate_user(data['username'], data['password'])
        data = user.to_dict() if user else None
        return handle_service_result(result, data=data, success_status=200)
    except Exception as e:
        return handle_exception('authenticate_user', e)


@user_bp.route('/stats', methods=['GET'])
def get_user_stats():
    try:
        repo = UserRepository()
        total_users = repo.get_count()
        return create_response(
            success=True,
            message='User statistics retrieved',
            data={'total_users': total_users}
        )
    except Exception as e:
        return handle_exception('get_user_stats', e)
