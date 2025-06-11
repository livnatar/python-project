from datetime import datetime, timedelta
from typing import Dict, Any


class Loan:
    def __init__(self, id: int = None, user_id: int = None, book_id: int = None,
                 loan_date: datetime = None, due_date: datetime = None,
                 returned_date: datetime = None, fine_amount: float = 0.0,
                 loan_period_days: int = 14):
        self.id = id
        self.user_id = user_id
        self.book_id = book_id
        self.loan_date = loan_date or datetime.utcnow()
        self.due_date = due_date or (self.loan_date + timedelta(days=loan_period_days))
        self.returned_date = returned_date
        self.fine_amount = fine_amount

    @property
    def is_overdue(self) -> bool:
        if self.returned_date:
            return False
        return datetime.utcnow() > self.due_date

    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days

    def calculate_fine(self, fine_per_day: float = 1.0) -> float:
        if self.days_overdue > 0:
            self.fine_amount = self.days_overdue * fine_per_day
        return self.fine_amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'loan_date': self.loan_date.isoformat() if self.loan_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'returned_date': self.returned_date.isoformat() if self.returned_date else None,
            'fine_amount': self.fine_amount,
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Loan':
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            book_id=data.get('book_id'),
            loan_date=data.get('loan_date'),
            due_date=data.get('due_date'),
            returned_date=data.get('returned_date'),
            fine_amount=data.get('fine_amount', 0.0),
        )
    