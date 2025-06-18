from repositories.open_library_repository import OpenLibraryRepository


class ExternalBookService:

    @staticmethod
    def get_languages_by_title(title):
        try:
            data = OpenLibraryRepository.search_book_by_title(title)
            if not data['docs']:
                return {"error": "Book not found"}

            doc = data['docs'][0]
            raw_languages = doc.get("language", [])
            languages = list(set(raw_languages))  # Remove duplicates if any

            return {
                "title": doc.get("title", title),
                "languages": languages
            }

        except RuntimeError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Unexpected error while getting languages: {str(e)}"}

    @staticmethod
    def get_same_author_books_by_title(title):
        try:
            data = OpenLibraryRepository.search_book_by_title(title)
            if not data.get('docs'):
                return {"error": "Book not found"}

            doc = data['docs'][0]
            author_key = doc.get('author_key', [None])[0]
            main_title = doc.get('title', title)

            same_author_books = []

            if author_key:
                author_data = OpenLibraryRepository.get_books_by_author(author_key)
                for entry in author_data.get('entries', []):
                    book_title = entry.get('title')
                    if book_title and book_title.lower() != main_title.lower():
                        same_author_books.append(book_title)

            return {
                "title": main_title,
                "same_author_books": same_author_books
            }

        except RuntimeError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Unexpected error while getting books by the same author: {str(e)}"}
