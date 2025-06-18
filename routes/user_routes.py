
from flask import Blueprint, request
import logging
from services.user_service import UserService
from repositories.user_repository import UserRepository
from utils.route_helpers import create_response, handle_exception, handle_service_result, get_validated_json

logger = logging.getLogger(__name__)
user_bp = Blueprint('users', __name__)
user_service = UserService()


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
