from datetime import datetime
from typing import Dict, Any


class BookGenre:
    def __init__(self, id: int = None, book_id: int = None, genre_id: int = None,):
        self.id = id
        self.book_id = book_id
        self.genre_id = genre_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'book_id': self.book_id,
            'genre_id': self.genre_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookGenre':
        return cls(
            id=data.get('id'),
            book_id=data.get('book_id'),
            genre_id=data.get('genre_id')
        )