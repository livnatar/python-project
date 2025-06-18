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
    def get_work_details(work_key):
        try:
            response = requests.get(f"{OpenLibraryRepository.BASE_URL}{work_key}.json")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenLibraryRepository: Failed to get work details: {e}")

    @staticmethod
    def get_work_editions(work_key, limit=10):
        try:
            response = requests.get(f"{OpenLibraryRepository.BASE_URL}{work_key}/editions.json", params={"limit": limit})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenLibraryRepository: Failed to get work editions: {e}")

    @staticmethod
    def get_books_by_subject(subject, limit=5):
        try:
            response = requests.get(f"{OpenLibraryRepository.BASE_URL}/subjects/{subject}.json", params={"limit": limit})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenLibraryRepository: Failed to get books by subject: {e}")

    @staticmethod
    def get_books_by_author(author_id, limit=5):
        try:
            response = requests.get(f"{OpenLibraryRepository.BASE_URL}/authors/{author_id}/works.json", params={"limit": limit})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"OpenLibraryRepository: Failed to get books by author: {e}")
