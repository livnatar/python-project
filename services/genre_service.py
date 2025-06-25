from typing import List, Optional, Dict, Any, Tuple
from repositories.genre_repository import GenreRepository
from repositories.book_genre_repository import BookGenreRepository
from models.genre_model import Genre
from utils.validators import validate_genre_data
import logging

logger = logging.getLogger(__name__)


class GenreService:
    """
    Service layer for genre business logic and interactions with repositories.
    """

    def __init__(self):
        """
        Initialize the GenreService with necessary repositories.
        """
        self.genre_repo = GenreRepository()
        self.book_genre_repo = BookGenreRepository()

    @staticmethod
    def _handle_exception(operation: str, error: Exception) -> Dict[str, Any]:
        """
        Handle exceptions consistently
        :param operation: str - The operation being performed when the error occurred.
        :param error: Exception - The exception that was raised.
        :return: dict - A dictionary containing error information.
        """

        logger.error(f"Error in {operation}: {error}")
        # Handle specific database constraints
        if 'foreign key constraint' in str(error).lower():
            return {
                'success': False,
                'error': 'Cannot delete genre: it has associated books'
            }
        return {
            'success': False,
            'error': 'Internal server error'
        }

    @staticmethod
    def _validate_genre_id(genre_id: int) -> Optional[Dict[str, Any]]:
        """
        Validate genre ID format
        :param genre_id: int - The ID of the genre to validate.
        :return: dict - None if valid, or an error dictionary if invalid.
        """

        if not isinstance(genre_id, int) or genre_id <= 0:
            return {
                'success': False,
                'error': 'Invalid genre ID'
            }
        return None

    @staticmethod
    def _validate_pagination(page: int, per_page: int) -> Tuple[int, int]:
        """
        Validate and normalize pagination parameters
        :param page: int - The current page number.
        :param per_page: int - The number of items per page.
        :return: tuple - A tuple containing the normalized page and per_page values.
        """

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        return page, per_page

    def _get_genre_or_error(self, genre_id: int) -> Tuple[Optional[Genre], Optional[Dict[str, Any]]]:
        """
        Get genre by ID or return error response
        :param genre_id: int - The ID of the genre to retrieve.
        :return: tuple - A tuple containing the genre object or None, and an error dictionary if applicable.
        """

        validation_error = self._validate_genre_id(genre_id)
        if validation_error:
            return None, validation_error

        genre = self.genre_repo.get_by_id(genre_id)
        if not genre:
            return None, {
                'success': False,
                'error': 'Genre not found'
            }
        return genre, None

    def _check_genre_name_exists(self, name: str, exclude_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Check if genre name exists and return error if it does
        :param name: str - The name of the genre to check.
        :param exclude_id: Optional[int] - The ID to exclude from the check (for updates).
        :return: dict - None if name is unique, or an error dictionary if it exists.
        """

        existing_genre = self.genre_repo.get_by_name(name)
        if existing_genre and (exclude_id is None or existing_genre.id != exclude_id):
            if exclude_id is None:
                return {
                    'success': False,
                    'error': 'Genre with this name already exists'
                }
            else:
                return {
                    'success': False,
                    'error': 'Another genre with this name already exists'
                }
        return None

    @staticmethod
    def _validate_search_term(search_term: str) -> Optional[Dict[str, Any]]:
        """
        Validate search term
        :param search_term: str - The term to search for in genres.
        :return: dict - None if valid, or an error dictionary if invalid.
        """

        if not search_term or not search_term.strip():
            return {
                'success': False,
                'error': 'Search term is required'
            }
        return None

    def _add_book_count_to_genre(self, genre: Genre) -> Dict[str, Any]:
        """
        Add book count to genre dictionary
        :param genre: Genre - The genre object to convert.
        :return: dict - A dictionary representation of the genre with book count.
        """

        genre_dict = genre.to_dict()
        genre_dict['books_count'] = self.book_genre_repo.count_books_in_genre(genre.id)
        return genre_dict

    def _add_book_counts_to_genres(self, genres: List[Genre]) -> List[Dict[str, Any]]:
        """
        Add book counts to list of genres
        :param genres: List[Genre] - The list of genre objects to convert.
        :return: List[Dict[str, Any]] - A list of dictionaries, each representing a genre with an added 'books_count' field.
        """
        return [self._add_book_count_to_genre(genre) for genre in genres]

    def create_genre(self, genre_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new genre with validation.
        :param genre_data: Dict[str, Any] - The data for the new genre, including 'name' and optional 'description'.
        :return: Dict[str, Any] - A result dictionary with success status, data or error message.
        """
        try:
            # Validate input data
            validation_result = validate_genre_data(genre_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }

            # Check if genre with same name already exists
            name_error = self._check_genre_name_exists(genre_data['name'])
            if name_error:
                return name_error

            # Create genre object
            genre = Genre(
                name=genre_data['name'].strip(),
                description=genre_data.get('description', '').strip()
            )

            # Save to database
            created_genre = self.genre_repo.create(genre)
            if created_genre:
                genre_dict = self._add_book_count_to_genre(created_genre)
                # Override book count for new genre
                genre_dict['books_count'] = 0
                return {
                    'success': True,
                    'data': genre_dict,
                    'message': 'Genre created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create genre'
                }

        except Exception as e:
            return self._handle_exception('create_genre', e)

    def get_genre_by_id(self, genre_id: int) -> Dict[str, Any]:
        """
        Retrieve a genre by its ID and include its book count.
        :param genre_id: int - The ID of the genre to retrieve.
        :return: Dict[str, Any] - A result dictionary with success status and the genre data, or error if not found.
        """

        try:
            genre, error = self._get_genre_or_error(genre_id)
            if error:
                return error

            genre_dict = self._add_book_count_to_genre(genre)
            return {
                'success': True,
                'data': genre_dict
            }

        except Exception as e:
            return self._handle_exception(f"get_genre_by_id({genre_id})", e)

    def get_id_by_genre(self, genre_name: str) -> Dict[str, Any]:
        """
        Retrieve a genre by its name and include its book count.
        :param genre_name: str - The name of the genre to retrieve.
        :return: Dict[str, Any] - A result dictionary with success status and the genre data, or error if not found.
        """

        try:
            if not isinstance(genre_name, str) or genre_name is None:
                return {
                    'success': False,
                    'error': 'Invalid genre name'
                }

            genre = self.genre_repo.get_by_name(genre_name)
            if genre:
                genre_dict = self._add_book_count_to_genre(genre)
                return {
                    'success': True,
                    'data': genre_dict
                }
            else:
                return {
                    'success': False,
                    'error': 'Genre id not found'
                }

        except Exception as e:
            return self._handle_exception(f"get_id_by_genre({genre_name})", e)

    def get_all_genres(self, page: int = 1, per_page: int = 20, search: str = None) -> Dict[str, Any]:
        """
        Retrieve all genres with pagination, optional search, and book counts.
        :param page: int - The page number to retrieve.
        :param per_page: int - The number of genres per page.
        :param search: str - An optional search term to filter genres by name or description.
        :return: Dict[str, Any] - A result dictionary with genre data, pagination metadata, or error.
        """

        try:
            # Validate pagination parameters
            page_normalized, per_page_normalized = self._validate_pagination(page, per_page)
            offset = (page_normalized - 1) * per_page_normalized

            if search and search.strip():
                genres = self.genre_repo.search(search.strip(), limit=per_page_normalized)
                total = len(genres)
            else:
                genres = self.genre_repo.get_all(limit=per_page_normalized, offset=offset)
                total = self.genre_repo.count()

            # Add book counts to each genre
            genres_with_counts = self._add_book_counts_to_genres(genres)

            return {
                'success': True,
                'data': genres_with_counts,
                'pagination': {
                    'page': page_normalized,
                    'per_page': per_page_normalized,
                    'total': total,
                    'pages': (total + per_page_normalized - 1) // per_page_normalized
                }
            }

        except Exception as e:
            return self._handle_exception("get_all_genres", e)

    def update_genre(self, genre_id: int, genre_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing genre with new data after validation.
        :param genre_id: int - The ID of the genre to update.
        :param genre_data: Dict[str, Any] - The new data to update, including 'name' and optionally 'description'.
        :return: Dict[str, Any] - A result dictionary with updated genre data or error message.
        """

        try:
            # Check if genre exists
            existing_genre, error = self._get_genre_or_error(genre_id)
            if error:
                return error

            # Validate input data
            validation_result = validate_genre_data(genre_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }

            # Check if another genre with same name exists
            name_error = self._check_genre_name_exists(genre_data['name'], exclude_id=genre_id)
            if name_error:
                return name_error

            # Update genre object
            updated_genre = Genre(
                id=genre_id,
                name=genre_data['name'].strip(),
                description=genre_data.get('description', '').strip()
            )

            # Save to database
            result = self.genre_repo.update(genre_id, updated_genre)
            if result:
                genre_dict = self._add_book_count_to_genre(result)
                return {
                    'success': True,
                    'data': genre_dict,
                    'message': 'Genre updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update genre'
                }

        except Exception as e:
            return self._handle_exception(f"update_genre({genre_id})", e)

    def delete_genre(self, genre_id: int) -> Dict[str, Any]:
        """
        Delete a genre if it exists and has no associated books.
        :param genre_id: int - The ID of the genre to delete.
        :return: Dict[str, Any] - A result dictionary indicating success or reason for failure.
        """

        try:
            # Check if genre exists
            existing_genre, error = self._get_genre_or_error(genre_id)
            if error:
                return error

            # Check if genre has associated books
            book_count = self.book_genre_repo.count_books_in_genre(genre_id)
            if book_count > 0:
                return {
                    'success': False,
                    'error': f'Cannot delete genre: it has {book_count} associated books'
                }

            # Delete genre
            success = self.genre_repo.delete(genre_id)
            if success:
                return {
                    'success': True,
                    'message': 'Genre deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to delete genre'
                }

        except Exception as e:
            return self._handle_exception(f"delete_genre({genre_id})", e)

    def search_genres(self, search_term: str) -> Dict[str, Any]:
        """
        Search for genres based on a search term in name or description.
        :param search_term: str - The keyword to search in genres.
        :return: Dict[str, Any] - A result dictionary with matched genres or error if input is invalid.
        """

        try:
            search_error = self._validate_search_term(search_term)
            if search_error:
                return search_error

            genres = self.genre_repo.search(search_term.strip())

            # Add book counts to each genre
            genres_with_counts = self._add_book_counts_to_genres(genres)

            return {
                'success': True,
                'data': genres_with_counts,
                'search_term': search_term.strip()
            }

        except Exception as e:
            return self._handle_exception("search_genres", e)

    def get_books_in_genre(self, genre_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all books in a specific genre with pagination.
        :param genre_id: int - The ID of the genre.
        :param page: int - The page number to retrieve.
        :param per_page: int - The number of books per page.
        :return: Dict[str, Any] - A result dictionary with genre info, list of books, and pagination metadata.
        """

        try:
            # Check if genre exists
            genre, error = self._get_genre_or_error(genre_id)
            if error:
                return error

            # Validate pagination parameters
            page_normalized, per_page_normalized = self._validate_pagination(page, per_page)
            offset = (page_normalized - 1) * per_page_normalized

            # Get books in this genre
            books_data = self.book_genre_repo.get_books_by_genre_id(genre_id, limit=per_page_normalized, offset=offset)
            total = self.book_genre_repo.count_books_in_genre(genre_id)

            return {
                'success': True,
                'data': {
                    'genre': genre.to_dict(),
                    'books': books_data,
                    'pagination': {
                        'page': page_normalized,
                        'per_page': per_page_normalized,
                        'total': total,
                        'pages': (total + per_page_normalized - 1) // per_page_normalized
                    }
                }
            }

        except Exception as e:
            return self._handle_exception(f"get_books_in_genre({genre_id})", e)
