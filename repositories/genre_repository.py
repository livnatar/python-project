import logging
from typing import List, Optional

from models.database import execute_query, execute_single_query
from models.genre_model import Genre

logger = logging.getLogger(__name__)


class GenreRepository:
    """
    Repository for managing genres in the database
    This class provides methods to create, read, update, delete, and search genres.
    """

    @staticmethod
    def create(genre: Genre) -> Optional[Genre]:
        """
        Create a new genre
        :param genre:  object to be created
        :return:  Genre object or None if creation failed
        """

        query = """
            INSERT INTO genres (name, description)
            VALUES (%s, %s)
            RETURNING id, name, description
        """
        try:
            result = execute_single_query(query, (genre.name, genre.description))
            if result:
                return Genre.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error creating genre: {e}")
            raise

    @staticmethod
    def get_by_id(genre_id: int) -> Optional[Genre]:
        """
        Get genre by ID
        :param genre_id:  of the genre to retrieve
        :return: Genre object or None if not found
        """

        query = "SELECT id, name, description FROM genres WHERE id = %s"
        try:
            result = execute_single_query(query, (genre_id,))
            if result:
                return Genre.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error getting genre by id {genre_id}: {e}")
            raise

    @staticmethod
    def get_by_name(name: str) -> Optional[Genre]:
        """
        Get genre by name
        :param name:  of the genre to retrieve
        :return: Genre object or None if not found
        """

        query = "SELECT id, name, description FROM genres WHERE LOWER(name) = LOWER(%s)"
        try:
            result = execute_single_query(query, (name,))
            if result:
                return Genre.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error getting genre by name {name}: {e}")
            raise

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Genre]:
        """
        Get all genres with pagination
        :param limit:  number of genres to return
        :param offset:  number of genres to skip
        :return: List of Genre objects
        """

        query = """
            SELECT id, name, description
            FROM genres 
            ORDER BY name 
            LIMIT %s OFFSET %s
        """
        try:
            results = execute_query(query, (limit, offset), fetch=True)
            return [Genre.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error getting all genres: {e}")
            raise

    @staticmethod
    def update(genre_id: int, genre: Genre) -> Optional[Genre]:
        """
        Update an existing genre
        :param genre_id:  of the genre to update
        :param genre:  object with updated data
        :return: Updated Genre object or None if update failed
        """

        query = """
            UPDATE genres 
            SET name = %s, description = %s
            WHERE id = %s
            RETURNING id, name, description
        """
        try:
            result = execute_single_query(query, (genre.name, genre.description, genre_id))
            if result:
                return Genre.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error updating genre {genre_id}: {e}")
            raise

    @staticmethod
    def delete(genre_id: int) -> bool:
        """
        Delete a genre
        :param genre_id:  of the genre to delete
        :return: True if deletion was successful, False otherwise
        """

        query = "DELETE FROM genres WHERE id = %s"
        try:
            rows_affected = execute_query(query, (genre_id,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error deleting genre {genre_id}: {e}")
            raise

    @staticmethod
    def count() -> int:
        """
        Get total count of genres
        :return: Total number of genres
        """

        query = "SELECT COUNT(*) as count FROM genres"
        try:
            result = execute_single_query(query)
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting genres: {e}")
            raise

    @staticmethod
    def search(search_term: str, limit: int = 50) -> List[Genre]:
        """
        Search genres by name or description
        :param search_term:  term to search for in name or description
        :param limit:  maximum number of results to return
        :return: List of Genre objects matching the search term
        """

        query = """
            SELECT id, name, description 
            FROM genres 
            WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s)
            ORDER BY name 
            LIMIT %s
        """
        search_pattern = f"%{search_term}%"
        try:
            results = execute_query(query, (search_pattern, search_pattern, limit), fetch=True)
            return [Genre.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error searching genres: {e}")
            raise