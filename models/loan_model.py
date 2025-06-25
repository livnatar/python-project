from datetime import datetime, timedelta
from typing import Dict, Any


class Loan:
    def __init__(self, id: int = None, user_id: int = None, book_id: int = None,
                 loan_date: datetime = None, due_date: datetime = None,
                 returned_date: datetime = None, fine_amount: float = 0.0,
                 loan_period_days: int = 14):
        """
        Represents a loan of a book to a user in the library system.
        :param id: The unique identifier for the loan.
        :param user_id: The unique identifier for the user who borrowed the book.
        :param book_id: The unique identifier for the book being borrowed.
        :param loan_date: The date when the book was borrowed. Defaults to the current date and time.
        :param due_date: The date when the book is due to be returned. Defaults to 14 days after the loan date.
        :param returned_date: The date when the book was returned. Defaults to None if not returned yet.
        :param fine_amount: The amount of fine incurred for late return. Defaults to 0.0.
        :param loan_period_days: The number of days the book can be borrowed before it is due. Defaults to 14 days.
        """
        self.id = id
        self.user_id = user_id
        self.book_id = book_id
        self.loan_date = loan_date or datetime.utcnow()
        self.due_date = due_date or (self.loan_date + timedelta(days=loan_period_days))
        self.returned_date = returned_date
        self.fine_amount = fine_amount

    @property
    def is_overdue(self) -> bool:
        """
        Checks if the loan is overdue.
        :return: True if the book is overdue, False otherwise.
        """
        if self.returned_date:
            return False
        return datetime.utcnow() > self.due_date

    @property
    def days_overdue(self) -> int:
        """
        Calculates the number of days the loan is overdue.
        :return: The number of days overdue, or 0 if not overdue.
        """
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days

    def calculate_fine(self, fine_per_day: float = 1.0) -> float:
        """
        Calculates the fine amount based on the number of days overdue.
        :param fine_per_day: The fine amount charged per day of delay. Defaults to 1.0.
        :return: The total fine amount for the overdue loan.
        """
        if self.days_overdue > 0:
            self.fine_amount = self.days_overdue * fine_per_day
        return self.fine_amount

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Loan instance to a dictionary representation.
        :return: The dictionary representation of the Loan instance.
        """
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
        """
        Creates a Loan instance from a dictionary representation.
        :param data: The dictionary containing the loan data.
        :return: A Loan instance created from the provided dictionary.
        """
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            book_id=data.get('book_id'),
            loan_date=data.get('loan_date'),
            due_date=data.get('due_date'),
            returned_date=data.get('returned_date'),
            fine_amount=data.get('fine_amount', 0.0),
        )
    