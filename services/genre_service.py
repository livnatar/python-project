# services/genre_service.py
from typing import List, Optional, Dict, Any
from repositories.genre_repository import GenreRepository
from repositories.book_genre_repository import BookGenreRepository
from models.genre_model import Genre
from utils.validators import validate_genre_data
import logging

logger = logging.getLogger(__name__)


class GenreService:

    def __init__(self):
        self.genre_repo = GenreRepository()
        self.book_genre_repo = BookGenreRepository()

    def create_genre(self, genre_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new genre with validation"""
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
            existing_genre = self.genre_repo.get_by_name(genre_data['name'])
            if existing_genre:
                return {
                    'success': False,
                    'error': 'Genre with this name already exists'
                }

            # Create genre object
            genre = Genre(
                name=genre_data['name'].strip(),
                description=genre_data.get('description', '').strip()
            )

            # Save to database
            created_genre = self.genre_repo.create(genre)
            if created_genre:
                genre_dict = created_genre.to_dict()
                genre_dict['books_count'] = 0  # New genre has no books
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
            logger.error(f"Error in create_genre: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def get_genre_by_id(self, genre_id: int) -> Dict[str, Any]:
        """Get genre by ID with book count"""
        try:
            if not isinstance(genre_id, int) or genre_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid genre ID'
                }

            genre = self.genre_repo.get_by_id(genre_id)
            if genre:
                genre_dict = genre.to_dict()
                # Add book count
                genre_dict['books_count'] = self.book_genre_repo.count_books_in_genre(genre_id)
                return {
                    'success': True,
                    'data': genre_dict
                }
            else:
                return {
                    'success': False,
                    'error': 'Genre not found'
                }

        except Exception as e:
            logger.error(f"Error in get_genre_by_id: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def get_id_by_genre(self, genre_name: str) -> Dict[str, Any]:
        """Get genre by ID with book count"""
        try:
            if not isinstance(genre_name, str) or genre_name is None:
                return {
                    'success': False,
                    'error': 'Invalid genre name'
                }

            genre = self.genre_repo.get_by_name(genre_name)
            if genre:
                genre_dict = genre.to_dict()
                # Add book count
                genre_dict['books_count'] = self.book_genre_repo.count_books_in_genre(genre.id)
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
            logger.error(f"Error in get_id_by_genre: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def get_all_genres(self, page: int = 1, per_page: int = 20, search: str = None) -> Dict[str, Any]:
        """Get all genres with pagination, search, and book counts"""
        try:
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20

            offset = (page - 1) * per_page

            if search and search.strip():
                genres = self.genre_repo.search(search.strip(), limit=per_page)
                total = len(genres)
            else:
                genres = self.genre_repo.get_all(limit=per_page, offset=offset)
                total = self.genre_repo.count()

            # Add book counts to each genre
            genres_with_counts = []
            for genre in genres:
                genre_dict = genre.to_dict()
                genre_dict['books_count'] = self.book_genre_repo.count_books_in_genre(genre.id)
                genres_with_counts.append(genre_dict)

            return {
                'success': True,
                'data': genres_with_counts,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }

        except Exception as e:
            logger.error(f"Error in get_all_genres: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def update_genre(self, genre_id: int, genre_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing genre"""
        try:
            # Validate genre ID
            if not isinstance(genre_id, int) or genre_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid genre ID'
                }

            # Check if genre exists
            existing_genre = self.genre_repo.get_by_id(genre_id)
            if not existing_genre:
                return {
                    'success': False,
                    'error': 'Genre not found'
                }

            # Validate input data
            validation_result = validate_genre_data(genre_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }

            # Check if another genre with same name exists
            name_check = self.genre_repo.get_by_name(genre_data['name'])
            if name_check and name_check.id != genre_id:
                return {
                    'success': False,
                    'error': 'Another genre with this name already exists'
                }

            # Update genre object
            updated_genre = Genre(
                id=genre_id,
                name=genre_data['name'].strip(),
                description=genre_data.get('description', '').strip()
            )

            # Save to database
            result = self.genre_repo.update(genre_id, updated_genre)
            if result:
                genre_dict = result.to_dict()
                genre_dict['books_count'] = self.book_genre_repo.count_books_in_genre(genre_id)
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
            logger.error(f"Error in update_genre: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def delete_genre(self, genre_id: int) -> Dict[str, Any]:
        """Delete a genre"""
        try:
            # Validate genre ID
            if not isinstance(genre_id, int) or genre_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid genre ID'
                }

            # Check if genre exists
            existing_genre = self.genre_repo.get_by_id(genre_id)
            if not existing_genre:
                return {
                    'success': False,
                    'error': 'Genre not found'
                }

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
            logger.error(f"Error in delete_genre: {e}")
            # Handle foreign key constraint error
            if 'foreign key constraint' in str(e).lower():
                return {
                    'success': False,
                    'error': 'Cannot delete genre: it has associated books'
                }
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def search_genres(self, search_term: str) -> Dict[str, Any]:
        """Search genres by name or description"""
        try:
            if not search_term or not search_term.strip():
                return {
                    'success': False,
                    'error': 'Search term is required'
                }

            genres = self.genre_repo.search(search_term.strip())

            # Add book counts to each genre
            genres_with_counts = []
            for genre in genres:
                genre_dict = genre.to_dict()
                genre_dict['books_count'] = self.book_genre_repo.count_books_in_genre(genre.id)
                genres_with_counts.append(genre_dict)

            return {
                'success': True,
                'data': genres_with_counts,
                'search_term': search_term.strip()
            }

        except Exception as e:
            logger.error(f"Error in search_genres: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }

    def get_books_in_genre(self, genre_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get all books in a specific genre"""
        try:
            # Validate genre ID
            if not isinstance(genre_id, int) or genre_id <= 0:
                return {
                    'success': False,
                    'error': 'Invalid genre ID'
                }

            # Check if genre exists
            genre = self.genre_repo.get_by_id(genre_id)
            if not genre:
                return {
                    'success': False,
                    'error': 'Genre not found'
                }

            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20

            offset = (page - 1) * per_page

            # Get books in this genre
            books_data = self.book_genre_repo.get_books_by_genre_id(genre_id, limit=per_page, offset=offset)
            total = self.book_genre_repo.count_books_in_genre(genre_id)

            return {
                'success': True,
                'data': {
                    'genre': genre.to_dict(),
                    'books': books_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error in get_books_in_genre: {e}")
            return {
                'success': False,
                'error': 'Internal server error'
            }