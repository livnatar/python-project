from datetime import datetime
from typing import List, Optional, Dict, Any


class Genre:
    def __init__(self, id: int = None, name: str = None, description: str = None):
        self.id = id
        self.name = name
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Genre':
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description')
        )