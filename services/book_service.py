# services/book_service.py
from typing import List, Optional, Dict, Any
from repositories.book_repository import BookRepository
from repositories.genre_repository import GenreRepository
from repositories.book_genre_repository import BookGenreRepository
from models.book_model import Book
from utils.validators import validate_book_data
import logging

logger = logging.getLogger(__name__)


class BookService:

    def __init__(self):
        self.book_repo = BookRepository()
        self.genre_repo = GenreRepository()
        self.book_genre_repo = BookGenreRepository()

    def create_book(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new book with genres"""
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
            if genre_ids:
                for genre_id in genre_ids:
                    genre = self.genre_repo.get_by_id(genre_id)
                    if not genre:
                        return {
                            'success': False,
                            'error': f'Genre with ID {genre_id} does not exist'
                        }

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

            # Save book to database
            created_book = self.book_repo.create(book)
            if not created_book:
                return {
                    'success': False,
                    'error': 'Failed to create book'
                }

            # Add genre relationships
            if genre_ids:
                success = self.book_genre_repo.update_book_genres(created_book.id, genre_ids)
                if not success:
                    # If genre assignment fails, we might want to delete the book
                    # For now, we'll just return an error
                    return {
                        'success': False,
                        'error': 'Book created but failed to assign genres'
                    }

                # Refresh book with genres
                created_book = self.book_repo.get_by_id(created_book.id)

            return {
                'success': True,
                'data': created_book.to_dict(),
                'message': 'Book created successfully'
            }

        except Exception as e:
            logger.error(f"Error in create_book: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def get_book_by_id(self, book_id: int) -> Dict[str, Any]:
        """Get book by ID with genres"""
        try:
            if not isinstance(book_id, int) or book_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid book ID'
                }

            book = self.book_repo.get_by_id(book_id)
            if book:
                return {
                    'success': True,
                    'data': book.to_dict()
                }
            else:
                return {
                    'success': False,
                    'error': 'Book not found'
                }

        except Exception as e:
            logger.error(f"Error in get_book_by_id: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def get_book_by_isbn(self, isbn: str) -> Dict[str, Any]:
        """Get book by ISBN with genres"""
        try:
            if not isbn or not isbn.strip():
                return {
                    'success': False,
                    'error': 'ISBN is required'
                }

            book = self.book_repo.get_by_isbn(isbn.strip())
            if book:
                return {
                    'success': True,
                    'data': book.to_dict()
                }
            else:
                return {
                    'success': False,
                    'error': 'Book not found'
                }

        except Exception as e:
            logger.error(f"Error in get_book_by_isbn: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def get_all_books(self, page: int = 1, per_page: int = 20, search: str = None,
                      genre_id: int = None, available_only: bool = False) -> Dict[str, Any]:
        """Get all books with pagination, search, and filtering"""
        try:
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20

            offset = (page - 1) * per_page

            if available_only:
                books = self.book_repo.get_available_books(limit=per_page, offset=offset)
                total = self.book_repo.count()  # This could be improved to count only available
            elif search and search.strip():
                genre_ids = [genre_id] if genre_id else None
                books = self.book_repo.search(search.strip(), genre_ids=genre_ids, limit=per_page)
                total = len(books)  # For search, we estimate
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
            logger.error(f"Error in get_all_books: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def update_book(self, book_id: int, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing book including genres"""
        try:
            # Validate book ID
            if not isinstance(book_id, int) or book_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid book ID'
                }

            # Check if book exists
            existing_book = self.book_repo.get_by_id(book_id)
            if not existing_book:
                return {
                    'success': False,
                    'error': 'Book not found'
                }

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
            if genre_ids:
                for genre_id in genre_ids:
                    genre = self.genre_repo.get_by_id(genre_id)
                    if not genre:
                        return {
                            'success': False,
                            'error': f'Genre with ID {genre_id} does not exist'
                        }

            # Update book object
            updated_book = Book(
                id=book_id,
                isbn=book_data['isbn'].strip(),
                title=book_data['title'].strip(),
                author=book_data['author'].strip(),
                publication_year=book_data.get('publication_year'),
                pages=book_data.get('pages'),
                language=book_data.get('language', 'English').strip(),
                description=book_data.get('description', '').strip(),
                copies_total=book_data.get('copies_total', existing_book.copies_total),
                copies_available=book_data.get('copies_available', existing_book.copies_available),
            )

            # Save book to database
            result = self.book_repo.update(book_id, updated_book)
            if not result:
                return {
                    'success': False,
                    'error': 'Failed to update book'
                }

            # Update genre relationships if provided
            if 'genre_ids' in book_data:
                success = self.book_genre_repo.update_book_genres(book_id, genre_ids)
                if not success:
                    return {
                        'success': False,
                        'error': 'Book updated but failed to update genres'
                    }

                # Refresh book with updated genres
                result = self.book_repo.get_by_id(book_id)

            return {
                'success': True,
                'data': result.to_dict(),
                'message': 'Book updated successfully'
            }

        except Exception as e:
            logger.error(f"Error in update_book: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def delete_book(self, book_id: int) -> Dict[str, Any]:
        """Delete a book"""
        try:
            # Validate book ID
            if not isinstance(book_id, int) or book_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid book ID'
                }

            # Check if book exists
            existing_book = self.book_repo.get_by_id(book_id)
            if not existing_book:
                return {
                    'success': False,
                    'error': 'Book not found'
                }

            # TODO: Check if book has active loans/reservations
            # For now, we'll allow deletion (constraints will handle it)

            # Delete book (this will also delete book-genre relationships due to CASCADE)
            success = self.book_repo.delete(book_id)
            if success:
                return {
                    'success': True,
                    'message': 'Book deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to delete book'
                }

        except Exception as e:
            logger.error(f"Error in delete_book: {e}")
            # Handle foreign key constraint error
            if 'foreign key constraint' in str(e).lower():
                return {
                    'success': False,
                    'error': 'Cannot delete book: it has active loans or reservations'
                }
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def search_books(self, search_term: str, genre_ids: List[int] = None) -> Dict[str, Any]:
        """Search books by title, author, or ISBN"""
        try:
            if not search_term or not search_term.strip():
                return {
                    'success': False,
                    'error': 'Search term is required'
                }

            books = self.book_repo.search(search_term.strip(), genre_ids=genre_ids)
            return {
                'success': True,
                'data': [book.to_dict() for book in books],
                'search_term': search_term.strip(),
                'genre_filter': genre_ids
            }

        except Exception as e:
            logger.error(f"Error in search_books: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def add_genre_to_book(self, book_id: int, genre_id: int) -> Dict[str, Any]:
        """Add a genre to a book"""
        try:
            # Validate IDs
            if not isinstance(book_id, int) or book_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid book ID'
                }

            if not isinstance(genre_id, int) or genre_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid genre ID'
                }

            # Check if book exists
            book = self.book_repo.get_by_id(book_id)
            if not book:
                return {
                    'success': False,
                    'error': 'Book not found'
                }

            # Check if genre exists
            genre = self.genre_repo.get_by_id(genre_id)
            if not genre:
                return {
                    'success': False,
                    'error': 'Genre not found'
                }

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
                # Get updated book with genres
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
            logger.error(f"Error in add_genre_to_book: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def remove_genre_from_book(self, book_id: int, genre_id: int) -> Dict[str, Any]:
        """Remove a genre from a book"""
        try:
            # Validate IDs
            if not isinstance(book_id, int) or book_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid book ID'
                }

            if not isinstance(genre_id, int) or genre_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid genre ID'
                }

            # Check if book exists
            book = self.book_repo.get_by_id(book_id)
            if not book:
                return {
                    'success': False,
                    'error': 'Book not found'
                }

            # Check if genre exists
            genre = self.genre_repo.get_by_id(genre_id)
            if not genre:
                return {
                    'success': False,
                    'error': 'Genre not found'
                }

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
                # Get updated book with genres
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
            logger.error(f"Error in remove_genre_from_book: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def update_book_availability(self, book_id: int, copies_available: int) -> Dict[str, Any]:
        """Update book availability (used for loans/returns)"""
        try:
            # Validate book ID
            if not isinstance(book_id, int) or book_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid book ID'
                }

            # Validate copies_available
            if not isinstance(copies_available, int) or copies_available < 0:
                return {
                    'success': False,
                    'error': 'Available copies must be a non-negative integer'
                }

            # Check if book exists
            book = self.book_repo.get_by_id(book_id)
            if not book:
                return {
                    'success': False,
                    'error': 'Book not found'
                }

            # Check if available copies doesn't exceed total copies
            if copies_available > book.copies_total:
                return {
                    'success': False,
                    'error': 'Available copies cannot exceed total copies'
                }

            # Update availability
            success = self.book_repo.update_availability(book_id, copies_available)
            if success:
                # Get updated book
                updated_book = self.book_repo.get_by_id(book_id)
                return {
                    'success': True,
                    'data': updated_book.to_dict(),
                    'message': 'Book availability updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update book availability'
                }

        except Exception as e:
            logger.error(f"Error in update_book_availability: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def get_available_books(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get all currently available books"""
        try:
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20

            offset = (page - 1) * per_page

            books = self.book_repo.get_available_books(limit=per_page, offset=offset)
            # For total count, we could create a specific method, but for now we'll estimate
            total = len(books) + offset if len(books) == per_page else len(books) + offset

            return {
                'success': True,
                'data': [book.to_dict() for book in books],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,  # This is an estimate
                    'pages': (total + per_page - 1) // per_page
                }
            }

        except Exception as e:
            logger.error(f"Error in get_available_books: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }