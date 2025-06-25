from typing import Dict, Any


class BookGenre:
    def __init__(self, id: int = None, book_id: int = None, genre_id: int = None,):
        """
        Represents a relationship between a book and a genre.
        :param id: The unique identifier for the book-genre relationship.
        :param book_id: The unique identifier for the book.
        :param genre_id: The unique identifier for the genre.
        """
        self.id = id
        self.book_id = book_id
        self.genre_id = genre_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the BookGenre instance to a dictionary representation.
        :return: The dictionary representation of the BookGenre instance.
        """
        return {
            'id': self.id,
            'book_id': self.book_id,
            'genre_id': self.genre_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookGenre':
        """
        Creates a BookGenre instance from a dictionary representation.
        :param data: The dictionary containing the book-genre relationship data.
        :return: A BookGenre instance created from the provided dictionary.
        """
        return cls(
            id=data.get('id'),
            book_id=data.get('book_id'),
            genre_id=data.get('genre_id')
        )