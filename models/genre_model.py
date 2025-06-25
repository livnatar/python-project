from typing import Dict, Any


class Genre:
    def __init__(self, id: int = None, name: str = None, description: str = None):
        """
        Represents a genre in the library system.
        :param id: The unique identifier for the genre.
        :param name: The name of the genre.
        :param description: A brief description of the genre.
        """
        self.id = id
        self.name = name
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Genre instance to a dictionary representation.
        :return: The dictionary representation of the Genre instance.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Genre':
        """
        Creates a Genre instance from a dictionary representation.
        :param data: The dictionary containing the genre data.
        :return: A Genre instance created from the provided dictionary.
        """
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description')
        )