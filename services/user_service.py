from typing import List, Optional, Dict, Any, Tuple
import logging
from models.user_model import User
from repositories.user_repository import UserRepository
from utils.validators import validate_user_data

logger = logging.getLogger(__name__)


class UserService:
    """
    Service layer for user business logic.
    Provides methods to create, retrieve, and validate users.
    """

    def __init__(self):
        """
        Initialize UserService with a UserRepository instance.
        """
        self.user_repository = UserRepository()

    @staticmethod
    def _handle_exception(operation: str, error: Exception) -> Any:
        """
        Handle exceptions consistently by logging and returning a standard error response.
        :param operation: str - The name of the operation where the error occurred.
        :param error: Exception - The caught exception.
        :return: Dict[str, Any] - Standardized error response dictionary.
        """

        logger.error(f"Error in {operation}: {error}")
        return {
            'success': False,
            'message': 'Internal server error',
            'errors': ['An unexpected error occurred']
        }

    @staticmethod
    def _validate_user_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Validate the format of a user ID.
        :param user_id: int - The user ID to validate.
        :return: Optional[Dict[str, Any]] - Error dictionary if invalid; otherwise None.
        """

        if not isinstance(user_id, int) or user_id <= 0:
            return {
                'success': False,
                'message': 'Invalid user ID',
                'errors': ['User ID must be a positive integer']
            }
        return None

    @staticmethod
    def _validate_pagination(page: int, per_page: int) -> Tuple[int, int]:
        """
        Validate and normalize pagination parameters.
        :param page: int - Requested page number.
        :param per_page: int - Number of items per page.
        :return: Tuple[int, int] - Validated and normalized (page, per_page) values.
        """

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        return page, per_page

    def _get_user_or_error(self, user_id: int) -> Tuple[Optional[User], Optional[Dict[str, Any]]]:
        """
        Retrieve a user by ID or return an error response if not found or invalid.
        :param user_id: int - The ID of the user to retrieve.
        :return: Tuple[Optional[User], Optional[Dict[str, Any]]] - User object and None if found; otherwise None and error dict.
        """

        validation_error = self._validate_user_id(user_id)
        if validation_error:
            return None, validation_error

        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None, {
                'success': False,
                'message': 'User not found',
                'errors': ['No user found with the provided ID']
            }
        return user, None

    def _check_username_exists(self, username: str, exclude_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Check if a username already exists in the system.
        :param username: str - The username to check.
        :param exclude_id: Optional[int] - User ID to exclude from the check (for updates).
        :return: Optional[Dict[str, Any]] - Error dict if username exists; otherwise None.
        """

        if self.user_repository.exists_by_username(username, exclude_id=exclude_id):
            return {
                'success': False,
                'message': 'Username already exists',
                'errors': ['Username is already taken']
            }
        return None

    def _check_email_exists(self, email: str, exclude_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Check if an email address already exists in the system.
        :param email: str - The email to check.
        :param exclude_id: Optional[int] - User ID to exclude from the check (for updates).
        :return: Optional[Dict[str, Any]] - Error dict if email exists; otherwise None.
        """

        if self.user_repository.exists_by_email(email, exclude_id=exclude_id):
            return {
                'success': False,
                'message': 'Email already exists',
                'errors': ['Email is already registered']
            }
        return None

    def create_user(self, user_data: Dict[str, Any]) -> Tuple[Optional[User], Dict[str, Any]]:
        """
        Create a new user after validating data and checking for duplicates.
        :param user_data: Dict[str, Any] - User data dictionary with required fields.
        :return: Tuple[Optional[User], Dict[str, Any]] - Created User object and success message; or None and error dict.
        """

        try:
            # Validate input data
            validation_result = validate_user_data(user_data)
            if not validation_result['valid']:
                return None, {
                    'success': False,
                    'message': 'Validation failed',
                    'errors': validation_result['errors']
                }

            # Check for existing username
            username_error = self._check_username_exists(user_data['username'])
            if username_error:
                return None, username_error

            # Check for existing email
            email_error = self._check_email_exists(user_data['email'])
            if email_error:
                return None, email_error

            # Create user object
            user = User(
                username=user_data['username'].strip(),
                email=user_data['email'].strip().lower(),
                first_name=user_data['first_name'].strip(),
                last_name=user_data['last_name'].strip(),
                phone=user_data.get('phone', '').strip() if user_data.get('phone') else None,
                address=user_data.get('address', '').strip() if user_data.get('address') else None,
                max_loans=user_data.get('max_loans', 5)
            )

            # Set password
            user.set_password(user_data['password'])

            # Save to database
            created_user = self.user_repository.create(user)

            if created_user:
                logger.info(f"User created successfully: {created_user.username}")
                return created_user, {
                    'success': True,
                    'message': 'User created successfully',
                    'user_id': created_user.id
                }
            else:
                return None, {
                    'success': False,
                    'message': 'Failed to create user',
                    'errors': ['Database error occurred']
                }
        except Exception as e:
            return self._handle_exception('create_user', e)

    def get_user_by_id(self, user_id: int) -> Tuple[Optional[User], Dict[str, Any]]:
        """
        Retrieve a user by their unique ID.
        :param user_id: int - The user ID.
        :return: Tuple[Optional[User], Dict[str, Any]] - User object and success message; or None and error dict.
        """

        try:
            user, error = self._get_user_or_error(user_id)
            if error:
                return None, error

            return user, {
                'success': True,
                'message': 'User found'
            }
        except Exception as e:
            return self._handle_exception(f"get_user_by_id({user_id})", e)

    def get_user_by_username(self, username: str) -> Tuple[Optional[User], Dict[str, Any]]:
        """
        Retrieve a user by their username.
        :param username: str - The username.
        :return: Tuple[Optional[User], Dict[str, Any]] - User object and success message; or None and error dict.
        """

        try:
            if not username or not username.strip():
                return None, {
                    'success': False,
                    'message': 'Invalid username',
                    'errors': ['Username cannot be empty']
                }

            user = self.user_repository.get_by_username(username.strip())

            if user:
                return user, {
                    'success': True,
                    'message': 'User found'
                }
            else:
                return None, {
                    'success': False,
                    'message': 'User not found',
                    'errors': ['No user found with the provided username']
                }
        except Exception as e:
            return self._handle_exception(f"get_user_by_username({username})", e)

    def get_all_users(self, page: int = 1, per_page: int = 20) -> Tuple[List[User], Dict[str, Any]]:
        """
        Retrieve all users with pagination support.
        :param page: int - The page number to retrieve.
        :param per_page: int - Number of users per page.
        :return: Tuple[List[User], Dict[str, Any]] - List of users and pagination metadata.
        """

        try:
            # Validate pagination parameters
            page_normalized, per_page_normalized = self._validate_pagination(page, per_page)
            offset = (page_normalized - 1) * per_page_normalized

            users = self.user_repository.get_all(limit=per_page_normalized, offset=offset)
            total_count = self.user_repository.get_count()
            total_pages = (total_count + per_page_normalized - 1) // per_page_normalized

            return users, {
                'success': True,
                'message': f'Retrieved {len(users)} users',
                'pagination': {
                    'page': page_normalized,
                    'per_page': per_page_normalized,
                    'total': total_count,
                    'total_pages': total_pages,
                    'has_next': page_normalized < total_pages,
                    'has_prev': page_normalized > 1
                }
            }
        except Exception as e:
            return self._handle_exception("get_all_users", e)

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Tuple[Optional[User], Dict[str, Any]]:
        """
        Update user information by user ID with validation and uniqueness checks.
        :param user_id: int - The ID of the user to update.
        :param user_data: Dict[str, Any] - Dictionary containing fields to update.
        :return: Tuple[Optional[User], Dict[str, Any]] - Updated User object and success message; or None and error dict.
        """

        try:
            # Check if user exists
            existing_user, error = self._get_user_or_error(user_id)
            if error:
                return None, error

            # Prepare update data (exclude password from regular updates)
            update_data = {}
            allowed_fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address', 'max_loans']

            for field in allowed_fields:
                if field in user_data:
                    if field in ['username', 'email', 'first_name', 'last_name']:
                        update_data[field] = user_data[field].strip()
                    elif field in ['phone', 'address']:
                        update_data[field] = user_data[field].strip() if user_data[field] else None
                    else:
                        update_data[field] = user_data[field]

            # Validate updated data if any core fields are being changed
            if any(field in update_data for field in ['username', 'email', 'first_name', 'last_name']):
                # Create validation data with existing values as defaults
                validation_data = {
                    'username': update_data.get('username', existing_user.username),
                    'email': update_data.get('email', existing_user.email),
                    'first_name': update_data.get('first_name', existing_user.first_name),
                    'last_name': update_data.get('last_name', existing_user.last_name),
                    'password': 'dummy_password'  # Skip password validation for updates
                }

                validation_result = validate_user_data(validation_data)
                # Remove password error since we're not updating it
                validation_result['errors'] = [err for err in validation_result['errors']
                                               if 'password' not in err.lower()]

                if validation_result['errors']:
                    return None, {
                        'success': False,
                        'message': 'Validation failed',
                        'errors': validation_result['errors']
                    }

            # Check for username uniqueness (excluding current user)
            if 'username' in update_data:
                username_error = self._check_username_exists(update_data['username'], exclude_id=user_id)
                if username_error:
                    return None, username_error

            # Check for email uniqueness (excluding current user)
            if 'email' in update_data:
                update_data['email'] = update_data['email'].lower()
                email_error = self._check_email_exists(update_data['email'], exclude_id=user_id)
                if email_error:
                    return None, email_error

            # Update user
            updated_user = self.user_repository.update(user_id, update_data)

            if updated_user:
                logger.info(f"User updated successfully: {updated_user.username}")
                return updated_user, {
                    'success': True,
                    'message': 'User updated successfully'
                }
            else:
                return None, {
                    'success': False,
                    'message': 'Failed to update user',
                    'errors': ['Update operation failed']
                }
        except Exception as e:
            return self._handle_exception(f"update_user({user_id})", e)

    def update_user_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Update a user's password after verifying the current password and validating the new one.
        :param user_id: int - The ID of the user whose password is to be changed.
        :param current_password: str - The user's current password for verification.
        :param new_password: str - The new password to set.
        :return: Tuple[bool, Dict[str, Any]] - True and success message if updated; False and error dict otherwise.
        """

        try:
            # Get user
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return False, {
                    'success': False,
                    'message': 'User not found',
                    'errors': ['No user found with the provided ID']
                }

            # Verify current password
            if not user.check_password(current_password):
                return False, {
                    'success': False,
                    'message': 'Current password is incorrect',
                    'errors': ['Current password verification failed']
                }

            # Validate new password
            validation_result = validate_user_data({
                'password': new_password, 'username': 'dummy', 'email': 'dummy@example.com',
                'first_name': 'dummy', 'last_name': 'dummy'
            })
            password_errors = [err for err in validation_result['errors'] if 'password' in err.lower()]

            if password_errors:
                return False, {
                    'success': False,
                    'message': 'New password validation failed',
                    'errors': password_errors
                }

            # Hash new password and update
            user.set_password(new_password)
            updated_user = self.user_repository.update(user_id, {'password_hash': user.password_hash})

            if updated_user:
                logger.info(f"Password updated for user: {user.username}")
                return True, {
                    'success': True,
                    'message': 'Password updated successfully'
                }
            else:
                return False, {
                    'success': False,
                    'message': 'Failed to update password',
                    'errors': ['Password update operation failed']
                }
        except Exception as e:
            return self._handle_exception(f"update_user_password({user_id})", e)

    def delete_user(self, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete a user by their user ID.
        :param user_id: int - The ID of the user to delete.
        :return: Tuple[bool, Dict[str, Any]] - True and success message if deleted; False and error dict otherwise.
        """

        try:
            # Check if user exists
            user, error = self._get_user_or_error(user_id)
            if error:
                return False, error

            # Delete user
            deleted = self.user_repository.delete(user_id)

            if deleted:
                logger.info(f"User deleted successfully: {user.username}")
                return True, {
                    'success': True,
                    'message': 'User deleted successfully'
                }
            else:
                return False, {
                    'success': False,
                    'message': 'Failed to delete user',
                    'errors': ['Delete operation failed']
                }
        except Exception as e:
            return self._handle_exception(f"delete_user({user_id})", e)

    def search_users(self, search_term: str, page: int = 1, per_page: int = 20) -> Tuple[List[User], Dict[str, Any]]:
        """
        Search for users matching a search term, with pagination support.
        :param search_term: str - The term to search for in user fields.
        :param page: int - The page number to retrieve.
        :param per_page: int - Number of users per page.
        :return: Tuple[List[User], Dict[str, Any]] - List of matching users and pagination metadata.
        """

        try:
            if not search_term or not search_term.strip():
                return [], {
                    'success': False,
                    'message': 'Search term cannot be empty',
                    'errors': ['Please provide a search term']
                }

            # Validate pagination parameters
            page_normalized, per_page_normalized = self._validate_pagination(page, per_page)
            offset = (page_normalized - 1) * per_page_normalized

            users = self.user_repository.search_users(search_term.strip(), limit=per_page_normalized, offset=offset)

            return users, {
                'success': True,
                'message': f'Found {len(users)} users matching "{search_term}"',
                'search_term': search_term,
                'pagination': {
                    'page': page_normalized,
                    'per_page': per_page_normalized,
                    'results_count': len(users)
                }
            }
        except Exception as e:
            return self._handle_exception("search_users", e)

    def authenticate_user(self, username: str, password: str) -> Tuple[Optional[User], Dict[str, Any]]:
        """
        Authenticate a user by username and password.
        :param username: str - The username of the user.
        :param password: str - The password of the user.
        :return: Tuple[Optional[User], Dict[str, Any]] - User object and success message if authenticated; None and error dict otherwise.
        """

        try:
            if not username or not password:
                return None, {
                    'success': False,
                    'message': 'Username and password are required',
                    'errors': ['Both username and password must be provided']
                }

            user = self.user_repository.get_by_username(username.strip())

            if user and user.check_password(password):
                logger.info(f"User authenticated successfully: {user.username}")
                return user, {
                    'success': True,
                    'message': 'Authentication successful'
                }
            else:
                logger.warning(f"Authentication failed for username: {username}")
                return None, {
                    'success': False,
                    'message': 'Invalid credentials',
                    'errors': ['Username or password is incorrect']
                }
        except Exception as e:
            return self._handle_exception(f"authenticate_user({username})", e)
