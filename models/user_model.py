from datetime import datetime
from typing import Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, id: int = None, username: str = None, email: str = None,
                 password_hash: str = None, first_name: str = None, last_name: str = None,
                 phone: str = None, address: str = None, membership_date: datetime = None,
                 max_loans: int = 5):
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
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches"""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> Dict[str, Any]:
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
    