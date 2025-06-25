from typing import List, Optional, Dict, Any
import logging
from models.database import execute_query, execute_single_query
from models.user_model import User

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repository layer for User data access operations
    This class provides methods to create, read, update, and delete users,
    as well as methods for user existence checks and searching.
    """

    @staticmethod
    def create(user: User) -> Optional[User]:
        """
        Create a new user in the database
        :param user: User object containing user details
        :return: User object with assigned ID or None if creation failed
        """

        try:
            query = """
                INSERT INTO users (username, email, password_hash, first_name, last_name, 
                                 phone, address, membership_date, max_loans)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, username, email, password_hash, first_name, last_name, 
                         phone, address, membership_date, max_loans
            """
            params = (
                user.username, user.email, user.password_hash, user.first_name,
                user.last_name, user.phone, user.address, user.membership_date,
                user.max_loans
            )

            result = execute_single_query(query, params)
            if result:
                return User(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    password_hash=result['password_hash'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    phone=result['phone'],
                    address=result['address'],
                    membership_date=result['membership_date'],
                    max_loans=result['max_loans']
                )
            return None

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID
        :param user_id:  of the user to retrieve
        :return: User object or None if not found
        """

        try:
            query = """
                SELECT id, username, email, password_hash, first_name, last_name, 
                       phone, address, membership_date, max_loans
                FROM users WHERE id = %s
            """
            result = execute_single_query(query, (user_id,))

            if result:
                return User(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    password_hash=result['password_hash'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    phone=result['phone'],
                    address=result['address'],
                    membership_date=result['membership_date'],
                    max_loans=result['max_loans']
                )
            return None

        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            raise

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """
        Get user by username
        :param username:  of the user to retrieve
        :return: User object or None if not found
        """

        try:
            query = """
                SELECT id, username, email, password_hash, first_name, last_name, 
                       phone, address, membership_date, max_loans
                FROM users WHERE username = %s
            """
            result = execute_single_query(query, (username,))

            if result:
                return User(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    password_hash=result['password_hash'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    phone=result['phone'],
                    address=result['address'],
                    membership_date=result['membership_date'],
                    max_loans=result['max_loans']
                )
            return None

        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Get user by email
        :param email:  of the user to retrieve
        :return: User object or None if not found
        """

        try:
            query = """
                SELECT id, username, email, password_hash, first_name, last_name, 
                       phone, address, membership_date, max_loans
                FROM users WHERE email = %s
            """
            result = execute_single_query(query, (email,))

            if result:
                return User(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    password_hash=result['password_hash'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    phone=result['phone'],
                    address=result['address'],
                    membership_date=result['membership_date'],
                    max_loans=result['max_loans']
                )
            return None

        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[User]:
        """
        Get all users with pagination
        :param limit:  number of users to return
        :param offset:  number of users to skip
        :return: List of User objects
        """

        try:
            query = """
                SELECT id, username, email, password_hash, first_name, last_name, 
                       phone, address, membership_date, max_loans
                FROM users 
                ORDER BY membership_date DESC
                LIMIT %s OFFSET %s
            """
            results = execute_query(query, (limit, offset), fetch=True)

            users = []
            for result in results:
                users.append(User(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    password_hash=result['password_hash'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    phone=result['phone'],
                    address=result['address'],
                    membership_date=result['membership_date'],
                    max_loans=result['max_loans']
                ))

            return users

        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise

    def update(self, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Update user by ID
        :param user_id:  of the user to update
        :param user_data: Dictionary containing fields to update
        :return: Updated User object or None if update failed
        """

        try:
            # Build dynamic update query
            set_clauses = []
            params = []

            updatable_fields = ['username', 'email', 'password_hash', 'first_name',
                                'last_name', 'phone', 'address', 'max_loans']

            for field in updatable_fields:
                if field in user_data:
                    set_clauses.append(f"{field} = %s")
                    params.append(user_data[field])

            if not set_clauses:
                return self.get_by_id(user_id)

            params.append(user_id)

            query = f"""
                UPDATE users 
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING id, username, email, password_hash, first_name, last_name, 
                         phone, address, membership_date, max_loans
            """

            result = execute_single_query(query, params)

            if result:
                return User(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    password_hash=result['password_hash'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    phone=result['phone'],
                    address=result['address'],
                    membership_date=result['membership_date'],
                    max_loans=result['max_loans']
                )
            return None

        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    @staticmethod
    def delete(user_id: int) -> bool:
        """
        Delete user by ID
        :param user_id:  of the user to delete
        :return: True if user was deleted, False otherwise
        """

        try:
            query = "DELETE FROM users WHERE id = %s"
            rows_affected = execute_query(query, (user_id,))
            return rows_affected > 0

        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise

    @staticmethod
    def exists_by_username(username: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if username exists (optionally excluding a specific user ID)
        :param username:  to check for existence
        :param exclude_id:  of the user to exclude from the check
        :return: True if username exists, False otherwise
        """

        try:
            if exclude_id:
                query = "SELECT 1 FROM users WHERE username = %s AND id != %s"
                result = execute_single_query(query, (username, exclude_id))
            else:
                query = "SELECT 1 FROM users WHERE username = %s"
                result = execute_single_query(query, (username,))

            return result is not None

        except Exception as e:
            logger.error(f"Error checking username existence: {e}")
            raise

    @staticmethod
    def exists_by_email(email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email exists (optionally excluding a specific user ID)
        :param email:  to check for existence
        :param exclude_id:  of the user to exclude from the check
        :return: True if email exists, False otherwise
        """

        try:
            if exclude_id:
                query = "SELECT 1 FROM users WHERE email = %s AND id != %s"
                result = execute_single_query(query, (email, exclude_id))
            else:
                query = "SELECT 1 FROM users WHERE email = %s"
                result = execute_single_query(query, (email,))

            return result is not None

        except Exception as e:
            logger.error(f"Error checking email existence: {e}")
            raise

    @staticmethod
    def get_count() -> int:
        """
        Get total count of users
        :return: Total number of users
        """

        try:
            query = "SELECT COUNT(*) as count FROM users"
            result = execute_single_query(query)
            return result['count'] if result else 0

        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            raise

    @staticmethod
    def search_users(search_term: str, limit: int = 50, offset: int = 0) -> List[User]:
        """
        Search users by username, email, or name
        :param search_term:  term to search for in username, email, first name, last name
        :param limit:  maximum number of results to return
        :param offset:  number of results to skip
        :return: List of User objects matching the search term
        """

        try:
            query = """
                SELECT id, username, email, password_hash, first_name, last_name, 
                       phone, address, membership_date, max_loans
                FROM users 
                WHERE username ILIKE %s 
                   OR email ILIKE %s 
                   OR first_name ILIKE %s 
                   OR last_name ILIKE %s
                   OR CONCAT(first_name, ' ', last_name) ILIKE %s
                ORDER BY membership_date DESC
                LIMIT %s OFFSET %s
            """
            search_pattern = f"%{search_term}%"
            params = (search_pattern, search_pattern, search_pattern,
                      search_pattern, search_pattern, limit, offset)

            results = execute_query(query, params, fetch=True)

            users = []
            for result in results:
                users.append(User(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    password_hash=result['password_hash'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    phone=result['phone'],
                    address=result['address'],
                    membership_date=result['membership_date'],
                    max_loans=result['max_loans']
                ))

            return users

        except Exception as e:
            logger.error(f"Error searching users: {e}")
            raise
