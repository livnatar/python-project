from datetime import datetime
from typing import Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, id: int = None, username: str = None, email: str = None,
                 password_hash: str = None, first_name: str = None, last_name: str = None,
                 phone: str = None, address: str = None, membership_date: datetime = None,
                 max_loans: int = 5):
        """
        Represents a user in the library system.
        :param id: The unique identifier for the user.
        :param username: The username of the user.
        :param email: The email address of the user.
        :param password_hash: The hashed password of the user.
        :param first_name: The first name of the user.
        :param last_name: The last name of the user.
        :param phone: The phone number of the user.
        :param address: The address of the user.
        :param membership_date: The date when the user became a member. Defaults to the current date and time.
        :param max_loans: The maximum number of books the user can borrow at a time. Defaults to 5.
        """
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.address = address
        self.membership_date = membership_date or datetime.utcnow()
        self.max_loans = max_loans

    def set_password(self, password: str):
        """
        Hash and set password
        :param password: The plain text password to be hashed and stored.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Check if provided password matches
        :param password: The plain text password to check against the stored hash.
        :return: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        """
        Returns the full name of the user by combining first and last names.
        :return: str: The full name of the user.
        """
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the User instance to a dictionary representation.
        :return: Dict[str, Any]: The dictionary representation of the User instance.
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'membership_date': self.membership_date.isoformat() if self.membership_date else None,
            'max_loans': self.max_loans
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Creates a User instance from a dictionary representation.
        :param data: The dictionary containing the user data.
        :return: User: A User instance created from the provided dictionary.
        """
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            address=data.get('address'),
            membership_date=data.get('membership_date'),
            max_loans=data.get('max_loans', 5)
        )
    