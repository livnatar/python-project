from flask import Blueprint, request, jsonify
from services.loan_service import LoanService
from utils.loans_validation import validate_loan_search_params
import logging

logger = logging.getLogger(__name__)

# Create blueprint
loan_bp = Blueprint('loans', __name__)
loan_service = LoanService()


def _validate_positive_integer(value: int, field_name: str) -> tuple[bool, str]:
    """Validate that a value is a positive integer"""
    if not isinstance(value, int) or value <= 0:
        return False, f'Invalid {field_name}'
    return True, ''


def _validate_pagination_params(params: dict) -> tuple[bool, dict]:
    """Validate pagination parameters"""
    validation_result = validate_loan_search_params(params)
    if not validation_result['valid']:
        return False, {
            'error': 'Invalid parameters',
            'details': validation_result['errors']
        }
    return True, {}


def _get_pagination_from_request():
    """Extract and return pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return page, per_page


def _validate_status_parameter(status: str) -> tuple[bool, str]:
    """Validate status parameter"""
    if not status:
        return True, ''

    valid_statuses = ['active', 'returned', 'overdue']
    if status not in valid_statuses:
        return False, f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
    return True, ''


def _handle_service_result(result: dict, success_status: int = 200):
    """Handle service layer results consistently"""
    if result['success']:
        return jsonify(result), success_status
    else:
        status_code = 404 if 'not found' in result['error'].lower() else 400
        error_response = {'error': result['error']}
        if 'details' in result:
            error_response['details'] = result['details']
        return jsonify(error_response), status_code


def _handle_exception(operation: str, error: Exception):
    """Handle exceptions consistently"""
    logger.error(f"Error in {operation}: {error}")
    return jsonify({'error': 'Internal server error'}), 500


def _validate_required_fields(data: dict, required_fields: list) -> tuple[bool, dict]:
    """Validate required fields in request data"""
    if not data:
        return False, {'error': 'No data provided'}

    for field in required_fields:
        if field not in data:
            return False, {'error': f'Missing required field: {field}'}

    return True, {}


@loan_bp.route('', methods=['GET'])
def get_loans():
    """Get all loans with optional filtering and pagination"""
    try:
        page, per_page = _get_pagination_from_request()
        status = request.args.get('status')

        # Validate parameters
        params = {'page': page, 'per_page': per_page}
        if status:
            params['status'] = status

        is_valid, error_response = _validate_pagination_params(params)
        if not is_valid:
            return jsonify(error_response), 400

        # Validate status parameter
        is_status_valid, status_error = _validate_status_parameter(status)
        if not is_status_valid:
            return jsonify({'error': status_error}), 400

        # Get loans
        result = loan_service.get_all_loans(page=page, per_page=per_page, status=status)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_loans', e)


@loan_bp.route('/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    """Get a specific loan by ID"""
    try:
        result = loan_service.get_loan_by_id(loan_id)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_loan', e)


@loan_bp.route('', methods=['POST'])
def create_loan():
    """Create a new loan (borrow a book)"""
    try:
        data = request.get_json()

        # Validate required fields
        is_valid, error_response = _validate_required_fields(data, ['user_id', 'book_id'])
        if not is_valid:
            return jsonify(error_response), 400

        # Create loan
        result = loan_service.create_loan(data)
        return _handle_service_result(result, 201)

    except Exception as e:
        return _handle_exception('create_loan', e)


@loan_bp.route('/<int:loan_id>/return', methods=['PUT'])
def return_book(loan_id):
    """Return a book - mark loan as returned"""
    try:
        data = request.get_json() or {}
        result = loan_service.return_book(loan_id, data)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('return_book', e)


@loan_bp.route('/<int:loan_id>/renew', methods=['PUT'])
def renew_loan(loan_id):
    """Renew a loan - extend due date"""
    try:
        data = request.get_json() or {}
        result = loan_service.renew_loan(loan_id, data)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('renew_loan', e)


@loan_bp.route('/overdue', methods=['GET'])
def get_overdue_loans():
    """Get all overdue loans"""
    try:
        result = loan_service.get_overdue_loans()
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_overdue_loans', e)


@loan_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_loans(user_id):
    """Get all loans for a specific user"""
    try:
        page, per_page = _get_pagination_from_request()

        # Validate parameters
        params = {'page': page, 'per_page': per_page}
        is_valid, error_response = _validate_pagination_params(params)
        if not is_valid:
            return jsonify(error_response), 400

        # Get user's loans
        result = loan_service.get_user_loans(user_id, page=page, per_page=per_page)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_user_loans', e)


@loan_bp.route('/book/<int:book_id>', methods=['GET'])
def get_book_loans(book_id):
    """Get all loans for a specific book"""
    try:
        page, per_page = _get_pagination_from_request()

        # Validate parameters
        params = {'page': page, 'per_page': per_page}
        is_valid, error_response = _validate_pagination_params(params)
        if not is_valid:
            return jsonify(error_response), 400

        # Get book's loans
        result = loan_service.get_book_loans(book_id, page=page, per_page=per_page)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_book_loans', e)


@loan_bp.route('/statistics', methods=['GET'])
def get_loan_statistics():
    """Get loan statistics"""
    try:
        result = loan_service.get_loan_statistics()
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_loan_statistics', e)


@loan_bp.route('/user/<int:user_id>/active', methods=['GET'])
def get_user_active_loans(user_id):
    """Get only active loans for a specific user"""
    try:
        result = loan_service.get_user_active_loans(user_id)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_user_active_loans', e)


@loan_bp.route('/book/<int:book_id>/current', methods=['GET'])
def get_current_book_loans(book_id):
    """Get current active loans for a specific book"""
    try:
        result = loan_service.get_current_book_loans(book_id)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_current_book_loans', e)


@loan_bp.route('/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    """Delete a loan record (admin operation)"""
    try:
        # Get optional force parameter for admin override
        # Use ?force=true to delete active loans
        force = request.args.get('force', 'false').lower() == 'true'

        result = loan_service.delete_loan(loan_id, force=force)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('delete_loan', e)

@loan_bp.route('/book/<int:book_id>/availability', methods=['GET'])
def get_book_availability(book_id):
    """Get detailed availability information for a book"""
    try:
        result = loan_service.get_book_availability(book_id)
        return _handle_service_result(result)

    except Exception as e:
        return _handle_exception('get_book_availability', e)