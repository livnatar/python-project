import requests


class OpenLibraryRepository:
    """
    OpenLibraryRepository is a class that interacts with the Open Library API to search for books
    and retrieve information about authors and their works.
    It provides methods to search for books by title and to get books by a specific author.
    It uses the requests library to make HTTP GET requests to the Open Library API endpoints.
    This class does not require any authentication to access the Open Library API.
    """
    BASE_URL = "https://openlibrary.org"

    @staticmethod
    def search_book_by_title(title):
        """
        Search for a book by its title using the Open Library API.
        :param title: Title of the book to search for
        :return: JSON response containing book details
        """

        try:
            response = requests.get(f"{OpenLibraryRepository.BASE_URL}/search.json", params={"title": title})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenLibraryRepository: Failed to search book by title: {e}")

    @staticmethod
    def get_books_by_author(author_id, limit=10):
        """
        Get books by a specific author using the Open Library API.
        :param author_id: ID of the author to retrieve books for
        :param limit: Number of books to return (default is 10)
        :return: JSON response containing books by the author
        """

        try:
            response = requests.get(f"{OpenLibraryRepository.BASE_URL}/authors/{author_id}/works.json", params={"limit": limit})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenLibraryRepository: Failed to get books by author: {e}")
