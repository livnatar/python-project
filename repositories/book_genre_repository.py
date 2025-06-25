from typing import List, Optional, Dict, Any
from models.database import get_db_connection, execute_query, execute_single_query
from models.book_genre_model import BookGenre
import logging

logger = logging.getLogger(__name__)


class BookGenreRepository:
    """
    Repository for managing book-genre relationships in the database.
    This class provides methods to create, read, update, delete, and search book-genre relationships.
    """

    @staticmethod
    def create(book_genre: BookGenre, conn=None) -> Optional[BookGenre]:
        """
        Create a new book-genre relationship - supports both standalone and transactional usage
        :param book_genre: BookGenre object containing book_id and genre_id
        :param conn: Optional database connection for transactional usage
        :return: BookGenre object if created successfully, None otherwise
        """

        query = """
            INSERT INTO book_genres (book_id, genre_id)
            VALUES (%s, %s)
            RETURNING id, book_id, genre_id
        """
        try:
            if conn:
                # Use provided connection (transactional)
                with conn.cursor() as cursor:
                    cursor.execute(query, (book_genre.book_id, book_genre.genre_id))
                    result = cursor.fetchone()
                    if result:
                        return BookGenre.from_dict(dict(result))
                    return None
            else:
                # Use standalone execution
                result = execute_single_query(query, (book_genre.book_id, book_genre.genre_id))
                if result:
                    return BookGenre.from_dict(dict(result))
                return None
        except Exception as e:
            logger.error(f"Error creating book-genre relationship: {e}")
            raise

    @staticmethod
    def get_by_id(book_genre_id: int) -> Optional[BookGenre]:
        """
        Get book-genre by ID
        :param book_genre_id:  of the book-genre relationship
        :return: BookGenre object if found, None otherwise
        """

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
        """
        Get all genres for a specific book
        :param book_id: ID of the book
        :return: List of dictionaries containing genre details
        """

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
        """
        Get all books for a specific genre
        :param genre_id: ID of the genre
        :param limit: Maximum number of books to return
        :param offset: Offset for pagination
        :return: List of dictionaries containing book details
        """

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
    def add_genre_to_book(book_id: int, genre_id: int, conn=None) -> bool:
        """
        Add a genre to a book (if not already assigned) - supports both standalone and transactional usage
        :param book_id: ID of the book
        :param genre_id: ID of the genre
        :param conn: Optional database connection for transactional usage
        :return: True if relationship was created, False if it already exists
        """

        try:
            if conn:
                # Use provided connection (transactional)
                with conn.cursor() as cursor:
                    # First check if relationship already exists
                    check_query = "SELECT id FROM book_genres WHERE book_id = %s AND genre_id = %s"
                    cursor.execute(check_query, (book_id, genre_id))
                    existing = cursor.fetchone()

                    if existing:
                        return False  # Relationship already exists

                    # Create the relationship
                    insert_query = """
                        INSERT INTO book_genres (book_id, genre_id)
                        VALUES (%s, %s)
                    """
                    cursor.execute(insert_query, (book_id, genre_id))
                    return cursor.rowcount > 0
            else:
                # Use standalone execution
                # First check if relationship already exists
                check_query = "SELECT id FROM book_genres WHERE book_id = %s AND genre_id = %s"
                existing = execute_single_query(check_query, (book_id, genre_id))

                if existing:
                    return False  # Relationship already exists

                book_genre = BookGenre(book_id=book_id, genre_id=genre_id)
                result = BookGenreRepository.create(book_genre)
                return result is not None
        except Exception as e:
            logger.error(f"Error adding genre {genre_id} to book {book_id}: {e}")
            raise

    @staticmethod
    def remove_genre_from_book(book_id: int, genre_id: int, conn=None) -> bool:
        """
        Remove a genre from a book - supports both standalone and transactional usage
        :param book_id: ID of the book
        :param genre_id: ID of the genre
        :param conn: Optional database connection for transactional usage
        :return: True if relationship was removed, False if it did not exist
        """

        query = "DELETE FROM book_genres WHERE book_id = %s AND genre_id = %s"
        try:
            if conn:
                # Use provided connection (transactional)
                with conn.cursor() as cursor:
                    cursor.execute(query, (book_id, genre_id))
                    return cursor.rowcount > 0
            else:
                # Use standalone execution
                rows_affected = execute_query(query, (book_id, genre_id))
                return rows_affected > 0
        except Exception as e:
            logger.error(f"Error removing genre {genre_id} from book {book_id}: {e}")
            raise

    @staticmethod
    def remove_all_genres_from_book(book_id: int, conn=None) -> bool:
        """
        Remove all genres from a book - supports both standalone and transactional usage
        :param book_id: ID of the book
        :param conn: Optional database connection for transactional usage
        :return: True if genres were removed, False if book had no genres
        """

        query = "DELETE FROM book_genres WHERE book_id = %s"
        try:
            if conn:
                # Use provided connection (transactional)
                with conn.cursor() as cursor:
                    cursor.execute(query, (book_id,))
                    return cursor.rowcount >= 0  # Could be 0 if book had no genres
            else:
                # Use standalone execution
                rows_affected = execute_query(query, (book_id,))
                return rows_affected >= 0  # Could be 0 if book had no genres
        except Exception as e:
            logger.error(f"Error removing all genres from book {book_id}: {e}")
            raise

    @staticmethod
    def delete_all_books_for_genre(genre_id: int) -> bool:
        """
        Remove all books from a genre
        :param genre_id: ID of the genre
        :return: True if books were removed, False if genre had no books
        """
        query = "DELETE FROM book_genres WHERE genre_id = %s"
        try:
            rows_affected = execute_query(query, (genre_id,))
            return rows_affected >= 0
        except Exception as e:
            logger.error(f"Error removing all books from genre {genre_id}: {e}")
            raise

    @staticmethod
    def get_all_relationships(limit: int = 100, offset: int = 0) -> List[BookGenre]:
        """
        Get all book-genre relationships
        :param limit: Maximum number of relationships to return
        :param offset: Offset for pagination
        :return: List of BookGenre objects
        """

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
        """
        Count how many books are in a specific genre
        :param genre_id: ID of the genre
        :return: Count of books in the genre
        """

        query = "SELECT COUNT(*) as count FROM book_genres WHERE genre_id = %s"
        try:
            result = execute_single_query(query, (genre_id,))
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting books in genre {genre_id}: {e}")
            raise

    @staticmethod
    def count_genres_for_book(book_id: int) -> int:
        """
        Count how many genres a book has
        :param book_id: ID of the book
        :return: Count of genres for the book
        """

        query = "SELECT COUNT(*) as count FROM book_genres WHERE book_id = %s"
        try:
            result = execute_single_query(query, (book_id,))
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting genres for book {book_id}: {e}")
            raise

    @staticmethod
    def update_book_genres(book_id: int, genre_ids: List[int], conn=None) -> bool:
        """
        Update all genres for a book (replace existing with new list) - supports both standalone and transactional usage
        :param book_id: ID of the book
        :param genre_ids: List of genre IDs to set for the book
        :param conn: Optional database connection for transactional usage
        :return: True if genres were updated successfully, False if no changes were made
        """

        try:
            if conn:
                # Use provided connection (transactional)
                with conn.cursor() as cursor:
                    # Remove all existing genres for this book
                    cursor.execute("DELETE FROM book_genres WHERE book_id = %s", (book_id,))

                    # Add new genres
                    for genre_id in genre_ids:
                        cursor.execute(
                            "INSERT INTO book_genres (book_id, genre_id) VALUES (%s, %s)",
                            (book_id, genre_id)
                        )
                    return True
            else:
                # Use standalone execution with manual transaction
                with get_db_connection() as standalone_conn:
                    with standalone_conn.cursor() as cursor:
                        # Remove all existing genres for this book
                        cursor.execute("DELETE FROM book_genres WHERE book_id = %s", (book_id,))

                        # Add new genres
                        for genre_id in genre_ids:
                            cursor.execute(
                                "INSERT INTO book_genres (book_id, genre_id) VALUES (%s, %s)",
                                (book_id, genre_id)
                            )
                        # Commit happens automatically when exiting context manager
                        return True
        except Exception as e:
            # Rollback happens automatically on exception
            logger.error(f"Error updating genres for book {book_id}: {e}")
            raise

    @staticmethod
    def exists(book_id: int, genre_id: int) -> bool:
        """
        Check if a book-genre relationship exists
        :param book_id: ID of the book
        :param genre_id: ID of the genre
        :return: True if relationship exists, False otherwise
        """

        query = "SELECT 1 FROM book_genres WHERE book_id = %s AND genre_id = %s"
        try:
            result = execute_single_query(query, (book_id, genre_id))
            return result is not None
        except Exception as e:
            logger.error(f"Error checking if book-genre relationship exists: {e}")
            raise

    # Legacy method name for backward compatibility
    @staticmethod
    def delete_all_genres_for_book(book_id: int) -> bool:
        """Remove all genres from a book (legacy method name)
        :param book_id: ID of the book
        :return: True if genres were removed, False if book had no genres
        """
        return BookGenreRepository.remove_all_genres_from_book(book_id)