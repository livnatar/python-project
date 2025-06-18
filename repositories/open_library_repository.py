import requests


class OpenLibraryRepository:
    BASE_URL = "https://openlibrary.org"

    @staticmethod
    def search_book_by_title(title):
        try:
            response = requests.get(f"{OpenLibraryRepository.BASE_URL}/search.json", params={"title": title})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenLibraryRepository: Failed to search book by title: {e}")

    @staticmethod
    def get_books_by_author(author_id, limit=10):
        try:
            response = requests.get(f"{OpenLibraryRepository.BASE_URL}/authors/{author_id}/works.json", params={"limit": limit})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenLibraryRepository: Failed to get books by author: {e}")
