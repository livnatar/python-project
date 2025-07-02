from typing import List, Optional, Dict, Any
from repositories.book_repository import BookRepository
from repositories.genre_repository import GenreRepository
from repositories.book_genre_repository import BookGenreRepository
from models.book_model import Book
from models.database import get_db_connection
from utils.validators import validate_book_data
import logging

logger = logging.getLogger(__name__)


class BookService:
    """
    Service class for managing book operations including creation, updating,
    retrieval, deletion, and genre management.
    """

    def __init__(self):
        """
        Initialize the BookService with repositories for books, genres, and book-genre relationships.
        """
        self.book_repo = BookRepository()
        self.genre_repo = GenreRepository()
        self.book_genre_repo = BookGenreRepository()

    @staticmethod
    def _validate_book_id(book_id: int) -> Optional[str]:
        """
        Validate book ID format
        :param book_id: ID of the book to validate
        :return: None if valid, error message if invalid
        """

        if not isinstance(book_id, int) or book_id <= 0:
            return 'Invalid book ID'
        return None

    @staticmethod
    def _validate_genre_id(genre_id: int) -> Optional[str]:
        """
        Validate genre ID format
        :param genre_id: ID of the genre to validate
        :return: None if valid, error message if invalid
        """

        if not isinstance(genre_id, int) or genre_id <= 0:
            return 'Invalid genre ID'
        return None

    def _validate_genres_exist(self, genre_ids: List[int]) -> Optional[str]:
        """
        Validate that all genre IDs exist in database
        :param genre_ids: List of genre IDs to validate
        :return: None if all exist, error message if any do not exist
        """

        if not genre_ids:
            return None

        for genre_id in genre_ids:
            genre = self.genre_repo.get_by_id(genre_id)
            if not genre:
                return f'Genre with ID {genre_id} does not exist'
        return None

    @staticmethod
    def _handle_exception(operation: str, error: Exception) -> Dict[str, Any]:
        """
        Handle exceptions consistently
        :param operation: Name of the operation being performed
        :param error: Exception that occurred
        :return: Dictionary with error details
        """

        logger.error(f"Error in {operation}: {error}")

        # Handle specific constraint errors
        error_str = str(error).lower()
        if 'foreign key constraint' in error_str:
            return {
                'success': False,
                'error': 'Cannot perform operation: referenced data is in use'
            }

        return {
            'success': False,
            'error': 'Internal server error'
        }

    def create_book(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new book with genres using proper transaction management
        :param book_data: Dictionary containing book details
        :return: Dictionary with success status and created book data or error message
        """

        try:
            # Validate input data
            validation_result = validate_book_data(book_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }

            # Check if book with same ISBN already exists
            existing_book = self.book_repo.get_by_isbn(book_data['isbn'])
            if existing_book:
                return {
                    'success': False,
                    'error': 'Book with this ISBN already exists'
                }

            # Validate genre IDs exist
            genre_ids = book_data.get('genre_ids', [])
            genre_error = self._validate_genres_exist(genre_ids)
            if genre_error:
                return {'success': False, 'error': genre_error}

            # Create book object
            book = Book(
                isbn=book_data['isbn'].strip(),
                title=book_data['title'].strip(),
                author=book_data['author'].strip(),
                publication_year=book_data.get('publication_year'),
                pages=book_data.get('pages'),
                language=book_data.get('language', 'English').strip(),
                description=book_data.get('description', '').strip(),
                copies_total=book_data.get('copies_total', 1),
                copies_available=book_data.get('copies_available', book_data.get('copies_total', 1))
            )

            # Use transaction to ensure atomicity
            with get_db_connection() as conn:
                try:
                    # Create book using repository with connection
                    created_book = self.book_repo.create(book, conn=conn)
                    if not created_book:
                        raise Exception("Failed to create book")

                    # Add genre relationships if provided
                    if genre_ids:
                        for genre_id in genre_ids:
                            success = self.book_genre_repo.add_genre_to_book(
                                created_book.id, genre_id, conn=conn)
                            if not success:
                                raise Exception(f"Failed to add genre {genre_id} to book")

                    # Commit happens automatically when exiting context manager

                except Exception as db_error:
                    # Rollback happens automatically on exception
                    raise db_error

            # Prepare the response with the created book
            book_dict = created_book.to_dict()

            # Add genre information to the response
            if genre_ids:
                genres = []
                for genre_id in genre_ids:
                    genre = self.genre_repo.get_by_id(genre_id)
                    if genre:
                        genres.append({
                            'id': genre.id,
                            'name': genre.name
                        })
                book_dict['genres'] = genres
            else:
                book_dict['genres'] = []

            return {
                'success': True,
                'data': book_dict,
                'message': 'Book created successfully'
            }

        except Exception as e:
            return self._handle_exception('create_book', e)

    def update_book(self, book_id: int, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing book including genres using proper transaction management
        :param book_id: ID of the book to update
        :param book_data: Dictionary containing updated book details
        :return: Dictionary with success status and updated book data or error message
        """

        try:
            # Validate book ID
            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            # Check if book exists
            existing_book = self.book_repo.get_by_id(book_id)
            if not existing_book:
                return {'success': False, 'error': 'Book not found'}

            # Validate input data
            validation_result = validate_book_data(book_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }

            # Check if another book with same ISBN exists
            isbn_check = self.book_repo.get_by_isbn(book_data['isbn'])
            if isbn_check and isbn_check.id != book_id:
                return {
                    'success': False,
                    'error': 'Another book with this ISBN already exists'
                }

            # Validate genre IDs exist
            genre_ids = book_data.get('genre_ids', [])
            genre_error = self._validate_genres_exist(genre_ids)
            if genre_error:
                return {'success': False, 'error': genre_error}

            # Create updated book object
            updated_book_data = Book(
                isbn=book_data['isbn'].strip(),
                title=book_data['title'].strip(),
                author=book_data['author'].strip(),
                publication_year=book_data.get('publication_year'),
                pages=book_data.get('pages'),
                language=book_data.get('language', 'English').strip(),
                description=book_data.get('description', '').strip(),
                copies_total=book_data.get('copies_total', existing_book.copies_total),
                copies_available=book_data.get('copies_available', existing_book.copies_available)
            )

            logger.info(f"Updated book data: {updated_book_data.to_dict()}")
            logger.info(f"Genre IDs to be assigned: {genre_ids}")

            # Use transaction to ensure atomicity
            with get_db_connection() as conn:
                try:
                    # Update book using repository with connection
                    updated_book = self.book_repo.update(book_id, updated_book_data, conn=conn)
                    if not updated_book:
                        raise Exception("Failed to update book")

                    # Update genre relationships if provided
                    if 'genre_ids' in book_data:
                        # Remove existing genre relationships
                        self.book_genre_repo.remove_all_genres_from_book(book_id, conn=conn)

                        # Add new genre relationships
                        for genre_id in genre_ids:
                            success = self.book_genre_repo.add_genre_to_book(book_id, genre_id, conn=conn)
                            if not success:
                                raise Exception(f"Failed to add genre {genre_id} to book")

                except Exception as db_error:
                    # Rollback happens automatically on exception
                    raise db_error

            # Get updated book with genres
            final_book = self.book_repo.get_by_id(book_id)

            # Commit happens automatically when exiting context manager
            return {
                'success': True,
                'data': final_book.to_dict(),
                'message': 'Book updated successfully'
            }

        except Exception as e:
            return self._handle_exception('update_book', e)

    def get_book_by_id(self, book_id: int) -> Dict[str, Any]:
        """
        Get book by ID with genres
        :param book_id: ID of the book to retrieve
        :return: Dictionary with success status and book data or error message
        """

        try:
            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            book = self.book_repo.get_by_id(book_id)
            if book:
                return {'success': True, 'data': book.to_dict()}
            else:
                return {'success': False, 'error': 'Book not found'}

        except Exception as e:
            return self._handle_exception('get_book_by_id', e)

    def get_book_by_isbn(self, isbn: str) -> Dict[str, Any]:
        """
        Get book by ISBN with genres
        :param isbn: ISBN of the book to retrieve
        :return: Dictionary with success status and book data or error message
        """

        try:
            if not isbn or not isbn.strip():
                return {'success': False, 'error': 'ISBN is required'}

            book = self.book_repo.get_by_isbn(isbn.strip())
            if book:
                return {'success': True, 'data': book.to_dict()}
            else:
                return {'success': False, 'error': 'Book not found'}

        except Exception as e:
            return self._handle_exception('get_book_by_isbn', e)

    def get_all_books(self, page: int = 1, per_page: int = 20, search: str = None,
                      genre_id: int = None, available_only: bool = False) -> Dict[str, Any]:
        """
        Get all books with pagination, search, and filtering
        :param page: Page number for pagination
        :param per_page: Number of books per page
        :param search: Search term for book title, author, or ISBN
        :param genre_id: Filter by genre ID
        :param available_only: Whether to return only available books
        :return: Dictionary with success status, book data, pagination info, and filters
        """

        try:
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20

            offset = (page - 1) * per_page

            if available_only:
                books = self.book_repo.get_available_books(limit=per_page, offset=offset)
                total = len(books)
            elif search and search.strip():
                genre_ids = [genre_id] if genre_id else None
                books = self.book_repo.search(search.strip(), genre_ids=genre_ids, limit=per_page)
                total = len(books)
            elif genre_id:
                books = self.book_repo.get_by_genre(genre_id, limit=per_page, offset=offset)
                total = self.book_repo.count(genre_id=genre_id)
            else:
                books = self.book_repo.get_all(limit=per_page, offset=offset)
                total = self.book_repo.count()

            return {
                'success': True,
                'data': [book.to_dict() for book in books],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                },
                'filters': {
                    'search': search,
                    'genre_id': genre_id,
                    'available_only': available_only
                }
            }

        except Exception as e:
            return self._handle_exception('get_all_books', e)

    def delete_book(self, book_id: int) -> Dict[str, Any]:
        """
        Delete a book
        :param book_id: ID of the book to delete
        :return: Dictionary with success status and message or error
        """

        try:
            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            # Check if book exists
            existing_book = self.book_repo.get_by_id(book_id)
            if not existing_book:
                return {'success': False, 'error': 'Book not found'}

            # Delete book (CASCADE will handle book-genre relationships)
            success = self.book_repo.delete(book_id)
            if success:
                return {'success': True, 'message': 'Book deleted successfully'}
            else:
                return {'success': False, 'error': 'Failed to delete book'}

        except Exception as e:
            return self._handle_exception('delete_book', e)

    def search_books(self, search_term: str, genre_ids: List[int] = None) -> Dict[str, Any]:
        """
        Search books by title, author, or ISBN
        :param search_term: Search term to filter books
        :param genre_ids: Optional list of genre IDs to filter results
        :return: Dictionary with success status, book data, search term, and genre filter
        """

        try:
            if not search_term or not search_term.strip():
                return {'success': False, 'error': 'Search term is required'}

            books = self.book_repo.search(search_term.strip(), genre_ids=genre_ids)
            return {
                'success': True,
                'data': [book.to_dict() for book in books],
                'search_term': search_term.strip(),
                'genre_filter': genre_ids
            }

        except Exception as e:
            return self._handle_exception('search_books', e)

    def add_genre_to_book(self, book_id: int, genre_id: int) -> Dict[str, Any]:
        """
        Add a genre to a book
        :param book_id: ID of the book to add genre to
        :param genre_id: ID of the genre to add
        :return: Dictionary with success status, updated book data, or error message
        """

        try:
            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            genre_id_error = self._validate_genre_id(genre_id)
            if genre_id_error:
                return {'success': False, 'error': genre_id_error}

            # Check if book exists
            book = self.book_repo.get_by_id(book_id)
            if not book:
                return {'success': False, 'error': 'Book not found'}

            # Check if genre exists
            genre = self.genre_repo.get_by_id(genre_id)
            if not genre:
                return {'success': False, 'error': 'Genre not found'}

            # Check if book already has 5 genres (limit)
            current_genre_count = self.book_genre_repo.count_genres_for_book(book_id)
            if current_genre_count >= 5:
                return {
                    'success': False,
                    'error': 'Book already has the maximum number of genres (5)'
                }

            # Add genre to book
            result = self.book_genre_repo.add_genre_to_book(book_id, genre_id)
            if result:
                updated_book = self.book_repo.get_by_id(book_id)
                return {
                    'success': True,
                    'data': updated_book.to_dict(),
                    'message': f'Genre "{genre.name}" added to book successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Book already has this genre or failed to add genre'
                }

        except Exception as e:
            return self._handle_exception('add_genre_to_book', e)

    def remove_genre_from_book(self, book_id: int, genre_id: int) -> Dict[str, Any]:
        """
        Remove a genre from a book
        :param book_id: ID of the book to remove genre from
        :param genre_id: ID of the genre to remove
        :return: Dictionary with success status, updated book data, or error message
        """

        try:
            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            genre_id_error = self._validate_genre_id(genre_id)
            if genre_id_error:
                return {'success': False, 'error': genre_id_error}

            # Check if book exists
            book = self.book_repo.get_by_id(book_id)
            if not book:
                return {'success': False, 'error': 'Book not found'}

            # Check if genre exists
            genre = self.genre_repo.get_by_id(genre_id)
            if not genre:
                return {'success': False, 'error': 'Genre not found'}

            # Check if this would leave the book with no genres
            current_genre_count = self.book_genre_repo.count_genres_for_book(book_id)
            if current_genre_count <= 1:
                return {
                    'success': False,
                    'error': 'Cannot remove last genre from book. Books must have at least one genre.'
                }

            # Remove genre from book
            success = self.book_genre_repo.remove_genre_from_book(book_id, genre_id)
            if success:
                updated_book = self.book_repo.get_by_id(book_id)
                return {
                    'success': True,
                    'data': updated_book.to_dict(),
                    'message': f'Genre "{genre.name}" removed from book successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Genre not found on this book or failed to remove'
                }

        except Exception as e:
            return self._handle_exception('remove_genre_from_book', e)

    def get_available_books(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all currently available books
        :param page: Page number for pagination
        :param per_page: Number of books per page
        :return: Dictionary with success status, book data, and pagination info
        """

        try:
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20

            offset = (page - 1) * per_page

            books = self.book_repo.get_available_books(limit=per_page, offset=offset)
            total = len(books) + offset if len(books) == per_page else len(books) + offset

            return {
                'success': True,
                'data': [book.to_dict() for book in books],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }

        except Exception as e:
            return self._handle_exception('get_available_books', e)
