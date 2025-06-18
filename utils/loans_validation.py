from datetime import datetime


def validate_loan_data(data):
    """Validate loan creation data"""
    errors = []

    # Check if data is provided
    if not data:
        return {'valid': False, 'errors': ['No data provided']}

    # Required fields
    required_fields = ['user_id', 'book_id']
    for field in required_fields:
        if field not in data:
            errors.append(f'Missing required field: {field}')
        elif data[field] is None:
            errors.append(f'{field} cannot be null')

    # Validate user_id
    if 'user_id' in data:
        try:
            user_id = int(data['user_id'])
            if user_id <= 0:
                errors.append('user_id must be a positive integer')
        except (ValueError, TypeError):
            errors.append('user_id must be a valid integer')

    # Validate book_id
    if 'book_id' in data:
        try:
            book_id = int(data['book_id'])
            if book_id <= 0:
                errors.append('book_id must be a positive integer')
        except (ValueError, TypeError):
            errors.append('book_id must be a valid integer')

    # Validate optional fields
    if 'loan_period_days' in data:
        try:
            loan_period = int(data['loan_period_days'])
            if loan_period <= 0 or loan_period > 365:
                errors.append('loan_period_days must be between 1 and 365')
        except (ValueError, TypeError):
            errors.append('loan_period_days must be a valid integer')

    if 'max_loans' in data:
        try:
            max_loans = int(data['max_loans'])
            if max_loans <= 0 or max_loans > 50:
                errors.append('max_loans must be between 1 and 50')
        except (ValueError, TypeError):
            errors.append('max_loans must be a valid integer')

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_return_data(data):
    """Validate book return data"""
    errors = []

    if not data:
        return {'valid': True, 'errors': []}  # Return data is optional

    # Validate fine_per_day if provided
    if 'fine_per_day' in data:
        try:
            fine_per_day = float(data['fine_per_day'])
            if fine_per_day < 0:
                errors.append('fine_per_day cannot be negative')
            elif fine_per_day > 100:
                errors.append('fine_per_day cannot exceed 100')
        except (ValueError, TypeError):
            errors.append('fine_per_day must be a valid number')

    # Validate returned_date if provided
    if 'returned_date' in data:
        try:
            if isinstance(data['returned_date'], str):
                returned_date = datetime.fromisoformat(data['returned_date'].replace('Z', '+00:00'))
                if returned_date > datetime.utcnow():
                    errors.append('returned_date cannot be in the future')
            elif not isinstance(data['returned_date'], datetime):
                errors.append('returned_date must be a valid datetime or ISO string')
        except ValueError:
            errors.append('returned_date must be a valid datetime format')

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_renewal_data(data):
    """Validate loan renewal data"""
    errors = []

    if not data:
        return {'valid': True, 'errors': []}  # Renewal data is optional

    # Validate renewal_days if provided
    if 'renewal_days' in data:
        try:
            renewal_days = int(data['renewal_days'])
            if renewal_days <= 0 or renewal_days > 365:
                errors.append('renewal_days must be between 1 and 365')
        except (ValueError, TypeError):
            errors.append('renewal_days must be a valid integer')

    # Validate new_due_date if provided
    if 'new_due_date' in data:
        try:
            if isinstance(data['new_due_date'], str):
                new_due_date = datetime.fromisoformat(data['new_due_date'].replace('Z', '+00:00'))
                if new_due_date <= datetime.utcnow():
                    errors.append('new_due_date must be in the future')
            elif not isinstance(data['new_due_date'], datetime):
                errors.append('new_due_date must be a valid datetime or ISO string')
        except ValueError:
            errors.append('new_due_date must be a valid datetime format')

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_loan_search_params(params):
    """Validate loan search parameters"""
    errors = []

    # Validate page
    if 'page' in params:
        try:
            page = int(params['page'])
            if page < 1:
                errors.append('page must be a positive integer')
        except (ValueError, TypeError):
            errors.append('page must be a valid integer')

    # Validate per_page
    if 'per_page' in params:
        try:
            per_page = int(params['per_page'])
            if per_page < 1 or per_page > 100:
                errors.append('per_page must be between 1 and 100')
        except (ValueError, TypeError):
            errors.append('per_page must be a valid integer')

    # Validate status
    if 'status' in params and params['status']:
        valid_statuses = ['active', 'returned', 'overdue']
        if params['status'].lower() not in valid_statuses:
            errors.append(f'status must be one of: {", ".join(valid_statuses)}')

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_id_parameter(param_value, param_name):
    """Validate a single ID parameter"""
    errors = []

    try:
        id_value = int(param_value)
        if id_value <= 0:
            errors.append(f'{param_name} must be a positive integer')
    except (ValueError, TypeError):
        errors.append(f'{param_name} must be a valid integer')

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }