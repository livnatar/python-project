from typing import Dict, Any, List


class Book:
    def __init__(self, id: int = None, isbn: str = None, title: str = None,
                 author: str = None, publication_year: int = None,
                 pages: int = None, language: str = 'English', description: str = None,
                 copies_total: int = 1, copies_available: int = 1, genres: List[Dict] = None):
        """
        Represents a book in the library system.
        :param id: The unique identifier for the book.
        :param isbn: The International Standard Book Number of the book.
        :param title: The title of the book.
        :param author: The author of the book.
        :param publication_year: The year the book was published.
        :param pages: The number of pages in the book.
        :param language: The language of the book, default is 'English'.
        :param description: A brief description of the book.
        :param copies_total: The total number of copies of the book available in the library.
        :param copies_available: The number of copies currently available for loan.
        :param genres: A list of genres associated with the book, each represented as a dictionary.
        """
        self.id = id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.pages = pages
        self.language = language
        self.description = description
        self.copies_total = copies_total
        self.copies_available = copies_available
        self.genres = genres or []

    @property
    def is_available(self) -> bool:
        """
        Checks if the book is available for loan.
        :return: True if there are copies available, False otherwise.
        """
        return self.copies_available > 0

    @property
    def copies_on_loan(self) -> int:
        """
        Calculates the number of copies of the book that are currently on loan.
        :return: The number of copies on loan.
        """
        return self.copies_total - self.copies_available

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Book instance to a dictionary representation.
        :return: The dictionary representation of the Book instance.
        """
        return {
            'id': self.id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publication_year': self.publication_year,
            'pages': self.pages,
            'language': self.language,
            'description': self.description,
            'copies_total': self.copies_total,
            'copies_available': self.copies_available,
            'copies_on_loan': self.copies_on_loan,
            'is_available': self.is_available,
            'genres': self.genres
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        """
        Creates a Book instance from a dictionary representation.
        :param data: The dictionary containing the book data.
        :return: A Book instance created from the provided dictionary.
        """
        return cls(
            id=data.get('id'),
            isbn=data.get('isbn'),
            title=data.get('title'),
            author=data.get('author'),
            publication_year=data.get('publication_year'),
            pages=data.get('pages'),
            language=data.get('language', 'English'),
            description=data.get('description'),
            copies_total=data.get('copies_total', 1),
            copies_available=data.get('copies_available', 1),
            genres=data.get('genres', [])
        )
