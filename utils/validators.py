import re
from typing import Dict, Any


def validate_genre_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate genre data"""
    errors = []

    # Check required fields
    if not data.get('name'):
        errors.append('Name is required')
    else:
        name = data['name'].strip()
        if len(name) < 2:
            errors.append('Name must be at least 2 characters long')
        elif len(name) > 100:
            errors.append('Name must not exceed 100 characters')
        elif not re.match(r'^[a-zA-Z0-9\s\-&]+$', name):
            errors.append('Name contains invalid characters')

    # Check description if provided
    if data.get('description'):
        description = data['description'].strip()
        if len(description) > 500:
            errors.append('Description must not exceed 500 characters')

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user data"""
    errors = []

    # Required fields
    required_fields = ['username', 'email', 'first_name', 'last_name', 'password']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field.replace("_", " ").title()} is required')

    # Username validation
    if data.get('username'):
        username = data['username'].strip()
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        elif len(username) > 80:
            errors.append('Username must not exceed 80 characters')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores')

    # Email validation
    if data.get('email'):
        email = data['email'].strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append('Invalid email format')

    # Phone validation (if provided)
    if data.get('phone'):
        phone = data['phone'].strip()
        if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            errors.append('Invalid phone format')

        # Password validation
    if data.get('password'):
        password = data['password']
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')
    else:
        errors.append('Password is required')

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_book_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate book data"""
    errors = []

    # Required fields
    required_fields = ['isbn', 'title', 'author']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field.replace("_", " ").title()} is required')

    # ISBN validation
    if data.get('isbn'):
        isbn = data['isbn'].strip().replace('-', '')
        if not isbn.isdigit() or len(isbn) not in [10, 13]:
            errors.append('ISBN must be 10 or 13 digits')

    # Title validation
    if data.get('title'):
        title = data['title'].strip()
        if len(title) < 1:
            errors.append('Title is required')
        elif len(title) > 200:
            errors.append('Title must not exceed 200 characters')

    # Author validation
    if data.get('author'):
        author = data['author'].strip()
        if len(author) < 1:
            errors.append('Author is required')
        elif len(author) > 200:
            errors.append('Author must not exceed 200 characters')

    # Genre validation
    if data.get('genre_ids'):
        genre_ids = data['genre_ids']
        if not isinstance(genre_ids, list):
            errors.append('Genre IDs must be a list')
        elif len(genre_ids) == 0:
            errors.append('At least one genre is required')
        elif len(genre_ids) > 5:
            errors.append('A book cannot have more than 5 genres')
        else:
            for genre_id in genre_ids:
                if not isinstance(genre_id, int) or genre_id <= 0:
                    errors.append('All genre IDs must be positive integers')
                    break

    # Numeric validations
    numeric_fields = ['publication_year', 'pages', 'copies_total', 'copies_available']
    for field in numeric_fields:
        if data.get(field) is not None:
            try:
                value = int(data[field])
                if value < 0:
                    errors.append(f'{field.replace("_", " ").title()} must be non-negative')
                elif field == 'publication_year' and (value < 1000 or value > 2030):
                    errors.append('Publication year must be between 1000 and 2030')
                elif field in ['copies_total', 'copies_available'] and value == 0:
                    errors.append(f'{field.replace("_", " ").title()} must be greater than 0')
            except (ValueError, TypeError):
                errors.append(f'{field.replace("_", " ").title()} must be a number')

    # Validate copies_available <= copies_total
    if data.get('copies_total') is not None and data.get('copies_available') is not None:
        try:
            total = int(data['copies_total'])
            available = int(data['copies_available'])
            if available > total:
                errors.append('Available copies cannot exceed total copies')
        except (ValueError, TypeError):
            pass  # Already handled in numeric validation

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
