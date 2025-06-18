from repositories.open_library_repository import OpenLibraryRepository


class ExternalBookService:

    @staticmethod
    def get_languages_by_title(title):
        try:
            data = OpenLibraryRepository.search_book_by_title(title)
            if not data['docs']:
                return {"error": "Book not found"}

            work_key = data['docs'][0].get('key')
            if not work_key:
                return {"error": "Work key not found for this title"}

            editions = OpenLibraryRepository.get_work_editions(work_key)
            languages = set()

            for edition in editions.get('entries', []):
                for lang in edition.get('languages', []):
                    key = lang.get('key', '')
                    if key.startswith("/languages/"):
                        languages.add(key.split("/")[-1])

            return {
                "title": title,
                "languages": list(languages)
            }

        except RuntimeError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Unexpected error while getting languages: {str(e)}"}

    @staticmethod
    def get_similar_books_by_title(title):
        try:
            data = OpenLibraryRepository.search_book_by_title(title)
            if not data['docs']:
                return {"error": "Book not found"}

            doc = data['docs'][0]
            subject_list = doc.get('subject', [])
            author_key = doc.get('author_key', [None])[0]

            similar_books = []

            if subject_list:
                subject = subject_list[0].lower().replace(" ", "_")
                subject_data = OpenLibraryRepository.get_books_by_subject(subject)
                similar_books = [b['title'] for b in subject_data.get('works', []) if b.get('title') != title]
            elif author_key:
                author_data = OpenLibraryRepository.get_books_by_author(author_key)
                similar_books = [b['title'] for b in author_data.get('entries', []) if b.get('title') != title]

            return {
                "title": title,
                "similar_books": similar_books
            }

        except RuntimeError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Unexpected error while getting similar books: {str(e)}"}
