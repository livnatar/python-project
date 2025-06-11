from datetime import datetime
from typing import Dict, Any


class Book:
    def __init__(self, id: int = None, isbn: str = None, title: str = None,
                 author: str = None, publication_year: int = None,
                 pages: int = None, language: str = 'English', description: str = None,
                 copies_total: int = 1, copies_available: int = 1,
                 genre_id: int = None, created_at: datetime = None):
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
        self.genre_id = genre_id
        self.created_at = created_at or datetime.utcnow()

    @property
    def is_available(self) -> bool:
        return self.copies_available > 0

    @property
    def copies_on_loan(self) -> int:
        return self.copies_total - self.copies_available

    def to_dict(self) -> Dict[str, Any]:
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
            'genre_id': self.genre_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_available': self.is_available
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
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
            genre_id=data.get('genre_id'),
            created_at=data.get('created_at')
        )
