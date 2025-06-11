from typing import List, Optional, Dict, Any
from models.database import get_db_connection, execute_query, execute_single_query
from models.book_genre_model import BookGenre
import logging

logger = logging.getLogger(__name__)


class BookGenreRepository:

    @staticmethod
    def create(book_genre: BookGenre) -> Optional[BookGenre]:
        """Create a new book-genre relationship"""
        query = """
            INSERT INTO book_genres (book_id, genre_id)
            VALUES (%s, %s)
            RETURNING id, book_id, genre_id
        """
        try:
            result = execute_single_query(query, (book_genre.book_id, book_genre.genre_id))
            if result:
                return BookGenre.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error creating book-genre relationship: {e}")
            raise

    @staticmethod
    def get_by_id(book_genre_id: int) -> Optional[BookGenre]:
        """Get book-genre by ID"""
        query = "SELECT id, book_id, genre_id FROM book_genres WHERE id = %s"
        try:
            result = execute_single_query(query, (book_genre_id,))
            if result:
                return BookGenre.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error getting book-genre by id {book_genre_id}: {e}")
            raise

    @staticmethod
    def get_genres_by_book_id(book_id: int) -> List[Dict[str, Any]]:
        """Get all genres for a specific book"""
        query = """
            SELECT g.id, g.name, g.description
            FROM genres g
            JOIN book_genres bg ON g.id = bg.genre_id
            WHERE bg.book_id = %s
            ORDER BY g.name
        """
        try:
            results = execute_query(query, (book_id,), fetch=True)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting genres for book {book_id}: {e}")
            raise

    @staticmethod
    def get_books_by_genre_id(genre_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all books for a specific genre"""
        query = """
            SELECT b.*
            FROM books b
            JOIN book_genres bg ON b.id = bg.book_id
            WHERE bg.genre_id = %s
            ORDER BY b.title
            LIMIT %s OFFSET %s
        """
        try:
            results = execute_query(query, (genre_id, limit, offset), fetch=True)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting books for genre {genre_id}: {e}")
            raise

    @staticmethod
    def add_genre_to_book(book_id: int, genre_id: int) -> Optional[BookGenre]:
        """Add a genre to a book (if not already assigned)"""
        # First check if relationship already exists
        check_query = "SELECT id FROM book_genres WHERE book_id = %s AND genre_id = %s"
        existing = execute_single_query(check_query, (book_id, genre_id))

        if existing:
            return None  # Relationship already exists

        book_genre = BookGenre(book_id=book_id, genre_id=genre_id)
        return BookGenreRepository.create(book_genre)

    @staticmethod
    def remove_genre_from_book(book_id: int, genre_id: int) -> bool:
        """Remove a genre from a book"""
        query = "DELETE FROM book_genres WHERE book_id = %s AND genre_id = %s"
        try:
            rows_affected = execute_query(query, (book_id, genre_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error removing genre {genre_id} from book {book_id}: {e}")
            raise

    @staticmethod
    def delete_all_genres_for_book(book_id: int) -> bool:
        """Remove all genres from a book"""
        query = "DELETE FROM book_genres WHERE book_id = %s"
        try:
            rows_affected = execute_query(query, (book_id,))
            return rows_affected >= 0  # Could be 0 if book had no genres
        except Exception as e:
            logger.error(f"Error removing all genres from book {book_id}: {e}")
            raise

    @staticmethod
    def delete_all_books_for_genre(genre_id: int) -> bool:
        """Remove all books from a genre"""
        query = "DELETE FROM book_genres WHERE genre_id = %s"
        try:
            rows_affected = execute_query(query, (genre_id,))
            return rows_affected >= 0
        except Exception as e:
            logger.error(f"Error removing all books from genre {genre_id}: {e}")
            raise

    @staticmethod
    def get_all_relationships(limit: int = 100, offset: int = 0) -> List[BookGenre]:
        """Get all book-genre relationships"""
        query = """
            SELECT id, book_id, genre_id 
            FROM book_genres 
            LIMIT %s OFFSET %s
        """
        try:
            results = execute_query(query, (limit, offset), fetch=True)
            return [BookGenre.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error getting all book-genre relationships: {e}")
            raise

    @staticmethod
    def count_books_in_genre(genre_id: int) -> int:
        """Count how many books are in a specific genre"""
        query = "SELECT COUNT(*) as count FROM book_genres WHERE genre_id = %s"
        try:
            result = execute_single_query(query, (genre_id,))
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting books in genre {genre_id}: {e}")
            raise

    @staticmethod
    def count_genres_for_book(book_id: int) -> int:
        """Count how many genres a book has"""
        query = "SELECT COUNT(*) as count FROM book_genres WHERE book_id = %s"
        try:
            result = execute_single_query(query, (book_id,))
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting genres for book {book_id}: {e}")
            raise

    @staticmethod
    def update_book_genres(book_id: int, genre_ids: List[int]) -> bool:
        """Update all genres for a book (replace existing with new list)"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Start transaction
            cursor.execute("BEGIN")

            # Remove all existing genres for this book
            cursor.execute("DELETE FROM book_genres WHERE book_id = %s", (book_id,))

            # Add new genres
            for genre_id in genre_ids:
                cursor.execute(
                    "INSERT INTO book_genres (book_id, genre_id) VALUES (%s, %s)",
                    (book_id, genre_id)
                )

            # Commit transaction
            cursor.execute("COMMIT")
            conn.commit()
            return True

        except Exception as e:
            if cursor:
                cursor.execute("ROLLBACK")
            if conn:
                conn.rollback()
            logger.error(f"Error updating genres for book {book_id}: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
