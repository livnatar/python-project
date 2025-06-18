from flask import request, jsonify
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_response(success: bool, message: str, data: Any = None, errors: list = None,
                    status_code: int = 200) -> tuple:
    """
    Create a standardized JSON response.
    """
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
    """
    Handle exceptions with logging and return standardized error response.
    """
    logger.error(f"Error in {func_name}: {e}")
    return create_response(
        success=False,
        message='Internal server error',
        errors=['An unexpected error occurred'],
        status_code=500
    )


def handle_service_result(result: Dict, data: Any = None, success_status: int = 200,
                          not_found_status: int = 404) -> tuple:
    """
    Handle service layer results and return appropriate HTTP response.
    """
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
    """
    Validate JSON request data and check for required fields.
    """
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
