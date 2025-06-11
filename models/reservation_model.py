from datetime import datetime, timedelta
from typing import Dict, Any


class Reservation:
    def __init__(self, id: int = None, user_id: int = None, book_id: int = None,
                 reservation_date: datetime = None, expiry_date: datetime = None,
                 status: str = 'active',
                 reservation_period_days: int = 7):
        self.id = id
        self.user_id = user_id
        self.book_id = book_id
        self.reservation_date = reservation_date or datetime.utcnow()
        self.expiry_date = expiry_date or (self.reservation_date + timedelta(days=reservation_period_days))
        self.status = status  # active, fulfilled, expired, cancelled

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expiry_date and self.status == 'active'

    @property
    def days_until_expiry(self) -> int:
        if self.status != 'active':
            return 0
        delta = self.expiry_date - datetime.utcnow()
        return max(0, delta.days)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'status': self.status,
            'is_expired': self.is_expired,
            'days_until_expiry': self.days_until_expiry
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reservation':
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            book_id=data.get('book_id'),
            reservation_date=data.get('reservation_date'),
            expiry_date=data.get('expiry_date'),
            status=data.get('status', 'active')
        )
