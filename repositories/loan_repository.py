import logging
from typing import List, Optional
from datetime import datetime

from models.database import execute_query, execute_single_query
from models.loan_model import Loan

logger = logging.getLogger(__name__)


class LoanRepository:

    @staticmethod
    def create_with_availability_check(loan: Loan) -> Optional[Loan]:
        """Create a loan only if book has available copies (atomic operation)"""
        # Single atomic transaction that checks and updates in one go
        query = """
            WITH book_check AS (
                SELECT id, copies_available 
                FROM books 
                WHERE id = %s AND copies_available > 0
                FOR UPDATE  -- This locks the row until transaction completes
            ),
            loan_insert AS (
                INSERT INTO loans (user_id, book_id, loan_date, due_date, fine_amount)
                SELECT %s, %s, %s, %s, %s
                FROM book_check
                RETURNING id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
            ),
            book_update AS (
                UPDATE books 
                SET copies_available = copies_available - 1
                WHERE id = %s AND copies_available > 0
                RETURNING copies_available
            )
            SELECT l.id, l.user_id, l.book_id, l.loan_date, l.due_date, l.returned_date, l.fine_amount, b.copies_available
            FROM loan_insert l, book_update b
        """
        try:
            result = execute_single_query(query, (
                loan.book_id,  # book_check
                loan.user_id, loan.book_id, loan.loan_date, loan.due_date, loan.fine_amount,  # loan_insert
                loan.book_id   # book_update
            ))
            if result:
                # Log the new availability for debugging
                loan_data = dict(result)
                copies_available = loan_data.pop('copies_available', None)
                logger.info(f"Loan created successfully. Book {loan.book_id} now has {copies_available} copies available")
                return Loan.from_dict(loan_data)
            return None  # No available copies or other error
        except Exception as e:
            logger.error(f"Error creating loan atomically: {e}")
            raise

    @staticmethod
    def get_by_id(loan_id: int) -> Optional[Loan]:
        """Get loan by ID"""
        query = """
            SELECT id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
            FROM loans 
            WHERE id = %s
        """
        try:
            result = execute_single_query(query, (loan_id,))
            if result:
                return Loan.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error getting loan by id {loan_id}: {e}")
            raise

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0, status: str = None) -> List[Loan]:
        """Get all loans with pagination and optional status filter"""
        base_query = """
            SELECT id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
            FROM loans
        """

        if status == 'active':
            base_query += " WHERE returned_date IS NULL"
        elif status == 'returned':
            base_query += " WHERE returned_date IS NOT NULL"
        elif status == 'overdue':
            base_query += " WHERE returned_date IS NULL AND due_date < NOW()"

        query = base_query + " ORDER BY loan_date DESC LIMIT %s OFFSET %s"

        try:
            results = execute_query(query, (limit, offset), fetch=True)
            return [Loan.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error getting all loans: {e}")
            raise

    @staticmethod
    def get_by_user_id(user_id: int, limit: int = 100, offset: int = 0) -> List[Loan]:
        """Get all loans for a specific user"""
        query = """
            SELECT id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
            FROM loans 
            WHERE user_id = %s
            ORDER BY loan_date DESC 
            LIMIT %s OFFSET %s
        """
        try:
            results = execute_query(query, (user_id, limit, offset), fetch=True)
            return [Loan.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error getting loans for user {user_id}: {e}")
            raise

    @staticmethod
    def get_by_book_id(book_id: int, limit: int = 100, offset: int = 0) -> List[Loan]:
        """Get all loans for a specific book"""
        query = """
            SELECT id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
            FROM loans 
            WHERE book_id = %s
            ORDER BY loan_date DESC 
            LIMIT %s OFFSET %s
        """
        try:
            results = execute_query(query, (book_id, limit, offset), fetch=True)
            return [Loan.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error getting loans for book {book_id}: {e}")
            raise

    @staticmethod
    def get_overdue_loans() -> List[Loan]:
        """Get all overdue loans"""
        query = """
            SELECT id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
            FROM loans 
            WHERE returned_date IS NULL AND due_date < NOW()
            ORDER BY due_date ASC
        """
        try:
            results = execute_query(query, fetch=True)
            return [Loan.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error getting overdue loans: {e}")
            raise

    @staticmethod
    def count_active_loans_for_book(book_id: int) -> int:
        """Count active loans for a specific book"""
        query = """
            SELECT COUNT(*) as count
            FROM loans 
            WHERE book_id = %s AND returned_date IS NULL
        """
        try:
            result = execute_single_query(query, (book_id,))
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting active loans for book {book_id}: {e}")
            raise

    @staticmethod
    def return_book_with_availability_update(loan_id: int, returned_date: datetime = None) -> Optional[Loan]:
        """Mark a loan as returned and update book availability atomically"""
        if returned_date is None:
            returned_date = datetime.utcnow()

        query = """
            WITH loan_update AS (
                UPDATE loans 
                SET returned_date = %s
                WHERE id = %s AND returned_date IS NULL
                RETURNING id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
            ),
            book_update AS (
                UPDATE books 
                SET copies_available = copies_available + 1
                WHERE id = (SELECT book_id FROM loan_update)
                RETURNING copies_available
            )
            SELECT l.id, l.user_id, l.book_id, l.loan_date, l.due_date, l.returned_date, l.fine_amount, b.copies_available
            FROM loan_update l, book_update b
        """
        try:
            result = execute_single_query(query, (returned_date, loan_id))
            if result:
                # Note: copies_available is returned but not part of Loan model, used for logging / validation
                loan_data = dict(result)
                copies_available = loan_data.pop('copies_available', None)
                logger.info(f"Book returned successfully for loan {loan_id}. Book {loan_data['book_id']} now has {copies_available} copies available")
                return Loan.from_dict(loan_data)
            return None
        except Exception as e:
            logger.error(f"Error returning book for loan {loan_id}: {e}")
            raise

    @staticmethod
    def renew_loan(loan_id: int, new_due_date: datetime) -> Optional[Loan]:
        """Renew a loan by extending the due date"""
        query = """
            UPDATE loans 
            SET due_date = %s
            WHERE id = %s AND returned_date IS NULL
            RETURNING id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
        """
        try:
            result = execute_single_query(query, (new_due_date, loan_id))
            if result:
                logger.info(f"Loan {loan_id} renewed successfully. New due date: {new_due_date}")
                return Loan.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error renewing loan {loan_id}: {e}")
            raise

    @staticmethod
    def update_fine(loan_id: int, fine_amount: float) -> Optional[Loan]:
        """Update the fine amount for a loan"""
        query = """
            UPDATE loans 
            SET fine_amount = %s
            WHERE id = %s
            RETURNING id, user_id, book_id, loan_date, due_date, returned_date, fine_amount
        """
        try:
            result = execute_single_query(query, (fine_amount, loan_id))
            if result:
                logger.info(f"Fine updated for loan {loan_id}: ${fine_amount}")
                return Loan.from_dict(dict(result))
            return None
        except Exception as e:
            logger.error(f"Error updating fine for loan {loan_id}: {e}")
            raise

    @staticmethod
    def count(status: str = None) -> int:
        """Get total count of loans"""
        base_query = "SELECT COUNT(*) as count FROM loans"

        if status == 'active':
            query = base_query + " WHERE returned_date IS NULL"
        elif status == 'returned':
            query = base_query + " WHERE returned_date IS NOT NULL"
        elif status == 'overdue':
            query = base_query + " WHERE returned_date IS NULL AND due_date < NOW()"
        else:
            query = base_query

        try:
            result = execute_single_query(query)
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting loans: {e}")
            raise

    @staticmethod
    def count_user_active_loans(user_id: int) -> int:
        """Get count of active loans for a user"""
        query = """
            SELECT COUNT(*) as count 
            FROM loans 
            WHERE user_id = %s AND returned_date IS NULL
        """
        try:
            result = execute_single_query(query, (user_id,))
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting active loans for user {user_id}: {e}")
            raise

    @staticmethod
    def get_book_availability_info(book_id: int) -> dict:
        """Get comprehensive availability information for a book"""
        query = """
            SELECT 
                b.id,
                b.title,
                b.copies_total,
                b.copies_available,
                (SELECT COUNT(*) FROM loans WHERE book_id = b.id) as total_loans_ever,
                (SELECT COUNT(*) FROM loans WHERE book_id = b.id AND returned_date IS NULL) as current_active_loans
            FROM books b
            WHERE b.id = %s
        """
        try:
            result = execute_single_query(query, (book_id,))
            if result:
                return dict(result)
            return {}
        except Exception as e:
            logger.error(f"Error getting book availability info for book {book_id}: {e}")
            raise

    @staticmethod
    def delete(loan_id: int) -> bool:
        """Delete a loan (use with caution - usually not needed)"""
        query = "DELETE FROM loans WHERE id = %s"
        try:
            rows_affected = execute_query(query, (loan_id,))
            if rows_affected > 0:
                logger.warning(f"Loan {loan_id} deleted - this should be rare")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting loan {loan_id}: {e}")
            raise
