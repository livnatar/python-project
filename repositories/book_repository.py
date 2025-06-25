from typing import List, Optional
from models.database import execute_query, execute_single_query
from models.book_model import Book
from repositories.book_genre_repository import BookGenreRepository
import logging

logger = logging.getLogger(__name__)


class BookRepository:
    """
    Repository for managing books in the database
    This class provides methods to create, read, update, delete, and search books.
    """

    @staticmethod
    def create(book: Book, conn=None) -> Optional[Book]:
        """Create a new book - supports both standalone and transactional usage
        :param book: Book object to create
        :param conn: Optional database connection for transactional usage
        :return: Created Book object with genres, or None if creation failed
        """

        query = """
            INSERT INTO books (isbn, title, author, publication_year, pages, 
                             language, description, copies_total, copies_available)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, isbn, title, author, publication_year, pages, 
                     language, description, copies_total, copies_available
        """
        try:
            if conn:
                # Use provided connection (transactional)
                with conn.cursor() as cursor:
                    cursor.execute(query, (
                        book.isbn, book.title, book.author, book.publication_year,
                        book.pages, book.language, book.description, book.copies_total,
                        book.copies_available
                    ))
                    result = cursor.fetchone()
                    if result:
                        created_book = Book.from_dict(dict(result))
                        return created_book
                    return None
            else:
                # Use standalone execution
                result = execute_single_query(query, (
                    book.isbn, book.title, book.author, book.publication_year,
                    book.pages, book.language, book.description, book.copies_total,
                    book.copies_available
                ))
                if result:
                    created_book = Book.from_dict(dict(result))
                    # Get genres for this book (will be empty for new book)
                    created_book.genres = BookGenreRepository.get_genres_by_book_id(created_book.id)
                    return created_book
                return None
        except Exception as e:
            logger.error(f"Error creating book: {e}")
            raise

    @staticmethod
    def get_by_id(book_id: int) -> Optional[Book]:
        """
        Get book by ID with genres
        :param book_id: ID of the book to retrieve
        :return: Book object with genres, or None if not found
        """

        query = """
            SELECT id, isbn, title, author, publication_year, pages, 
                   language, description, copies_total, copies_available
            FROM books 
            WHERE id = %s
        """
        try:
            result = execute_single_query(query, (book_id,))
            if result:
                book = Book.from_dict(dict(result))
                # Get genres for this book
                book.genres = BookGenreRepository.get_genres_by_book_id(book_id)
                return book
            return None
        except Exception as e:
            logger.error(f"Error getting book by id {book_id}: {e}")
            raise

    @staticmethod
    def get_by_isbn(isbn: str) -> Optional[Book]:
        """
        Get book by ISBN with genres
        :param isbn: ISBN of the book to retrieve
        :return: Book object with genres, or None if not found
        """

        query = """
            SELECT id, isbn, title, author, publication_year, pages, 
                   language, description, copies_total, copies_available
            FROM books 
            WHERE isbn = %s
        """
        try:
            result = execute_single_query(query, (isbn,))
            if result:
                book = Book.from_dict(dict(result))
                # Get genres for this book
                book.genres = BookGenreRepository.get_genres_by_book_id(book.id)
                return book
            return None
        except Exception as e:
            logger.error(f"Error getting book by ISBN {isbn}: {e}")
            raise

    @staticmethod
    def get_all(limit: int = 50, offset: int = 0) -> List[Book]:
        """
        Get all books with pagination and genres
        :param limit: Number of books to return
        :param offset: Offset for pagination
        :return: List of Book objects with genres
        """

        query = """
            SELECT id, isbn, title, author, publication_year, pages, 
                   language, description, copies_total, copies_available
            FROM books 
            ORDER BY title 
            LIMIT %s OFFSET %s
        """
        try:
            results = execute_query(query, (limit, offset), fetch=True)
            books = []
            for row in results:
                book = Book.from_dict(dict(row))
                # Get genres for each book
                book.genres = BookGenreRepository.get_genres_by_book_id(book.id)
                books.append(book)
            return books
        except Exception as e:
            logger.error(f"Error getting all books: {e}")
            raise

    @staticmethod
    def search(search_term: str, genre_ids: List[int] = None, limit: int = 50) -> List[Book]:
        """
        Search books by title, author, or ISBN with optional genre filter
        :param search_term: Term to search in title, author, or ISBN
        :param genre_ids: List of genre IDs to filter by (optional)
        :param limit: Maximum number of results to return
        :return: List of Book objects matching the search criteria
        """

        if genre_ids:
            # Search with genre filter
            query = """
                SELECT DISTINCT b.id, b.isbn, b.title, b.author, b.publication_year, 
                       b.pages, b.language, b.description, b.copies_total, b.copies_available
                FROM books b
                JOIN book_genres bg ON b.id = bg.book_id
                WHERE (LOWER(b.title) LIKE LOWER(%s) OR LOWER(b.author) LIKE LOWER(%s) OR b.isbn LIKE %s)
                AND bg.genre_id = ANY(%s)
                ORDER BY b.title 
                LIMIT %s
            """
            search_pattern = f"%{search_term}%"
            params = (search_pattern, search_pattern, search_pattern, genre_ids, limit)
        else:
            # Search without genre filter
            query = """
                SELECT id, isbn, title, author, publication_year, pages, 
                       language, description, copies_total, copies_available
                FROM books 
                WHERE LOWER(title) LIKE LOWER(%s) OR LOWER(author) LIKE LOWER(%s) OR isbn LIKE %s
                ORDER BY title 
                LIMIT %s
            """
            search_pattern = f"%{search_term}%"
            params = (search_pattern, search_pattern, search_pattern, limit)

        try:
            results = execute_query(query, params, fetch=True)
            books = []
            for row in results:
                book = Book.from_dict(dict(row))
                # Get genres for each book
                book.genres = BookGenreRepository.get_genres_by_book_id(book.id)
                books.append(book)
            return books
        except Exception as e:
            logger.error(f"Error searching books: {e}")
            raise

    @staticmethod
    def get_by_genre(genre_id: int, limit: int = 50, offset: int = 0) -> List[Book]:
        """
        Get all books in a specific genre
        :param genre_id: ID of the genre to filter by
        :param limit: Number of books to return
        :param offset: Offset for pagination
        :return: List of Book objects in the specified genre
        """

        query = """
            SELECT b.id, b.isbn, b.title, b.author, b.publication_year, 
                   b.pages, b.language, b.description, b.copies_total, b.copies_available
            FROM books b
            JOIN book_genres bg ON b.id = bg.book_id
            WHERE bg.genre_id = %s
            ORDER BY b.title 
            LIMIT %s OFFSET %s
        """
        try:
            results = execute_query(query, (genre_id, limit, offset), fetch=True)
            books = []
            for row in results:
                book = Book.from_dict(dict(row))
                # Get genres for each book
                book.genres = BookGenreRepository.get_genres_by_book_id(book.id)
                books.append(book)
            return books
        except Exception as e:
            logger.error(f"Error getting books by genre {genre_id}: {e}")
            raise

    @staticmethod
    def update(book_id: int, book: Book, conn=None) -> Optional[Book]:
        """
        Update an existing book - supports both standalone and transactional usage
        :param book_id: ID of the book to update
        :param book: Book object with updated data
        :param conn: Optional database connection for transactional usage
        :return: Updated Book object with genres, or None if update failed
        """

        query = """
            UPDATE books 
            SET isbn = %s, title = %s, author = %s, publication_year = %s,
                pages = %s, language = %s, description = %s, copies_total = %s, 
                copies_available = %s
            WHERE id = %s
            RETURNING id, isbn, title, author, publication_year, pages, 
                     language, description, copies_total, copies_available
        """
        try:
            if conn:
                # Use provided connection (transactional)
                with conn.cursor() as cursor:
                    cursor.execute(query, (
                        book.isbn, book.title, book.author, book.publication_year,
                        book.pages, book.language, book.description, book.copies_total,
                        book.copies_available, book_id
                    ))
                    result = cursor.fetchone()
                    if result:
                        updated_book = Book.from_dict(dict(result))
                        return updated_book
                    return None
            else:
                # Use standalone execution
                result = execute_single_query(query, (
                    book.isbn, book.title, book.author, book.publication_year,
                    book.pages, book.language, book.description, book.copies_total,
                    book.copies_available, book_id
                ))
                if result:
                    updated_book = Book.from_dict(dict(result))
                    # Get genres for this book
                    updated_book.genres = BookGenreRepository.get_genres_by_book_id(book_id)
                    return updated_book
                return None
        except Exception as e:
            logger.error(f"Error updating book {book_id}: {e}")
            raise

    @staticmethod
    def delete(book_id: int) -> bool:
        """
        Delete a book (this will also delete book-genre relationships due to CASCADE)
        :param book_id: ID of the book to delete
        :return: True if deletion was successful, False otherwise
        """

        query = "DELETE FROM books WHERE id = %s"
        try:
            rows_affected = execute_query(query, (book_id,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error deleting book {book_id}: {e}")
            raise

    @staticmethod
    def count(search_term: str = None, genre_id: int = None) -> int:
        """
        Get total count of books with optional filters
        :param search_term: Term to filter by title, author, or ISBN
        :param genre_id: ID of the genre to filter by
        :return: Total count of books matching the criteria
        """

        if search_term and genre_id:
            query = """
                SELECT COUNT(DISTINCT b.id) as count 
                FROM books b
                JOIN book_genres bg ON b.id = bg.book_id
                WHERE (LOWER(b.title) LIKE LOWER(%s) OR LOWER(b.author) LIKE LOWER(%s) OR b.isbn LIKE %s)
                AND bg.genre_id = %s
            """
            search_pattern = f"%{search_term}%"
            params = (search_pattern, search_pattern, search_pattern, genre_id)
        elif search_term:
            query = """
                SELECT COUNT(*) as count 
                FROM books 
                WHERE LOWER(title) LIKE LOWER(%s) OR LOWER(author) LIKE LOWER(%s) OR isbn LIKE %s
            """
            search_pattern = f"%{search_term}%"
            params = (search_pattern, search_pattern, search_pattern)
        elif genre_id:
            query = """
                SELECT COUNT(*) as count 
                FROM books b
                JOIN book_genres bg ON b.id = bg.book_id
                WHERE bg.genre_id = %s
            """
            params = (genre_id,)
        else:
            query = "SELECT COUNT(*) as count FROM books"
            params = None

        try:
            result = execute_single_query(query, params)
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting books: {e}")
            raise

    @staticmethod
    def update_availability(book_id: int, copies_available: int) -> bool:
        """
        Update book availability (used when books are borrowed/returned)
        :param book_id: ID of the book to update
        :param copies_available: New number of available copies
        :return: True if update was successful, False otherwise
        """
        query = "UPDATE books SET copies_available = %s WHERE id = %s"
        try:
            rows_affected = execute_query(query, (copies_available, book_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error updating availability for book {book_id}: {e}")
            raise

    @staticmethod
    def get_available_books(limit: int = 50, offset: int = 0) -> List[Book]:
        """
        Get all available books (copies_available > 0)
        :param limit: Number of books to return
        :param offset: Offset for pagination
        :return: List of available Book objects with genres
        """

        query = """
            SELECT id, isbn, title, author, publication_year, pages, 
                   language, description, copies_total, copies_available
            FROM books 
            WHERE copies_available > 0
            ORDER BY title 
            LIMIT %s OFFSET %s
        """
        try:
            results = execute_query(query, (limit, offset), fetch=True)
            books = []
            for row in results:
                book = Book.from_dict(dict(row))
                # Get genres for each book
                book.genres = BookGenreRepository.get_genres_by_book_id(book.id)
                books.append(book)
            return books
        except Exception as e:
            logger.error(f"Error getting available books: {e}")
            raise
