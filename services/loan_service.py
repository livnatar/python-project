from typing import Optional, Dict, Any
from datetime import timedelta
from repositories.loan_repository import LoanRepository
from repositories.user_repository import UserRepository
from repositories.book_repository import BookRepository
from models.loan_model import Loan
from utils.loans_validation import validate_loan_data, validate_return_data, validate_renewal_data
import logging

logger = logging.getLogger(__name__)


class LoanService:
    """
    Service layer responsible for handling the business logic related to book loans.
    """

    def __init__(self):
        """
        Initialize the LoanService with required repositories.
        """
        self.loan_repo = LoanRepository()
        self.user_repo = UserRepository()
        self.book_repo = BookRepository()

    @staticmethod
    def _validate_loan_id(loan_id: int) -> Optional[str]:
        """
        Validate loan ID format.
        :param loan_id: int - The loan ID to validate.
        :return: Optional[str] - An error message if invalid, or None if valid.
        """

        if not isinstance(loan_id, int) or loan_id <= 0:
            return 'Invalid loan ID'
        return None

    @staticmethod
    def _validate_user_id(user_id: int) -> Optional[str]:
        """
        Validate user ID format.
        :param user_id: int - The user ID to validate.
        :return: Optional[str] - An error message if invalid, or None if valid.
        """

        if not isinstance(user_id, int) or user_id <= 0:
            return 'Invalid user ID'
        return None

    @staticmethod
    def _validate_book_id(book_id: int) -> Optional[str]:
        """
        Validate book ID format.
        :param book_id: int - The book ID to validate.
        :return: Optional[str] - An error message if invalid, or None if valid.
        """

        if not isinstance(book_id, int) or book_id <= 0:
            return 'Invalid book ID'
        return None

    @staticmethod
    def _validate_pagination(page: int, per_page: int) -> tuple[int, int]:
        """
        Validate and normalize pagination parameters.
        :param page: int - The page number.
        :param per_page: int - The number of items per page.
        :return: Tuple[int, int] - A tuple containing the validated (page, per_page) values.
        """

        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        return page, per_page

    def _check_user_exists(self, user_id: int) -> Optional[str]:
        """
        Check if a user exists by their ID.
        :param user_id: int - The ID of the user.
        :return: Optional[str] - An error message if the user doesn't exist, or None.
        """

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return 'User not found'
        return None

    def _check_book_exists(self, book_id: int) -> Optional[str]:
        """
        Check if a book exists by its ID.
        :param book_id: int - The ID of the book.
        :return: Optional[str] - An error message if the book doesn't exist, or None.
        """

        book = self.book_repo.get_by_id(book_id)
        if not book:
            return 'Book not found'
        return None

    def _check_loan_exists_and_active(self, loan_id: int) -> tuple[Optional[Loan], Optional[str]]:
        """
        Check if a loan exists and is active.
        :param loan_id: int - The ID of the loan.
        :return: Tuple[Optional[Loan], Optional[str]] - The loan object if found, or error message if not.
        """

        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            return None, 'Loan not found'
        return loan, None

    @staticmethod
    def _handle_exception(operation: str, error: Exception) -> Dict[str, Any]:
        """
        Handle exceptions consistently across all service methods.
        :param operation: str - The name of the operation where the exception occurred.
        :param error: Exception - The exception that was raised.
        :return: Dict[str, Any] - A standardized error response dictionary.
        """

        logger.error(f"Error in {operation}: {error}")

        # Handle specific constraint errors
        error_str = str(error).lower()
        if 'foreign key constraint' in error_str:
            return {
                'success': False,
                'error': 'Cannot perform operation: referenced data is in use'
            }

        return {
            'success': False,
            'error': 'Internal server error'
        }

    @staticmethod
    def _validate_input_data(data: Dict[str, Any], validation_func) -> Optional[Dict[str, Any]]:
        """
        Generic input validation helper for loan data.
        :param data: Dict[str, Any] - The input data to validate.
        :param validation_func: Callable - A function that returns a validation result.
        :return: Optional[Dict[str, Any]] - None if valid, or an error response dictionary if not.
        """

        validation_result = validation_func(data)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': 'Validation failed',
                'details': validation_result['errors']
            }
        return None

    def create_loan(self, loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new loan (borrow a book), including all required validation and availability checks.
        :param loan_data: Dict[str, Any] - A dictionary containing 'user_id', 'book_id', and optional 'loan_period_days'.
        :return: Dict[str, Any] - A response indicating success or failure and loan details if created.
        """

        try:
            # Validate input data
            validation_error = self._validate_input_data(loan_data, validate_loan_data)
            if validation_error:
                return validation_error

            user_id = loan_data['user_id']
            book_id = loan_data['book_id']

            # Validate IDs
            user_id_error = self._validate_user_id(user_id)
            if user_id_error:
                return {'success': False, 'error': user_id_error}

            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            # Check if user and book exist
            user_error = self._check_user_exists(user_id)
            if user_error:
                return {'success': False, 'error': user_error}

            book_error = self._check_book_exists(book_id)
            if book_error:
                return {'success': False, 'error': book_error}

            # Check user's loan limits
            user_active_loans = self.loan_repo.count_user_active_loans(user_id)
            max_loans = loan_data.get('max_loans', 5)
            if user_active_loans >= max_loans:
                return {
                    'success': False,
                    'error': f'User has reached maximum loan limit ({max_loans}). Current active loans: {user_active_loans}'
                }

            # Get current availability info for logging
            availability_info = self.loan_repo.get_book_availability_info(book_id)
            logger.info(
                f"Attempting to create loan for book {book_id}. Current availability: {availability_info.get('copies_available', 'unknown')}")

            # Create loan object
            loan_period_days = loan_data.get('loan_period_days', 14)
            loan = Loan(
                user_id=user_id,
                book_id=book_id,
                loan_period_days=loan_period_days
            )

            # Create loan with atomic availability check
            created_loan = self.loan_repo.create_with_availability_check(loan)
            if created_loan:
                return {
                    'success': True,
                    'data': self._enrich_loan_data(created_loan),
                    'message': 'Loan created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'No copies of this book are currently available'
                }

        except Exception as e:
            return self._handle_exception('create_loan', e)

    def get_loan_by_id(self, loan_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific loan by its ID, enriched with related data.
        :param loan_id: int - The ID of the loan to retrieve.
        :return: Dict[str, Any] - A result dictionary with loan details or error information.
        """

        try:
            loan_id_error = self._validate_loan_id(loan_id)
            if loan_id_error:
                return {'success': False, 'error': loan_id_error}

            loan, error = self._check_loan_exists_and_active(loan_id)
            if error:
                return {'success': False, 'error': error}

            return {
                'success': True,
                'data': self._enrich_loan_data(loan)
            }

        except Exception as e:
            return self._handle_exception('get_loan_by_id', e)

    def get_all_loans(self, page: int = 1, per_page: int = 20, status: str = None) -> Dict[str, Any]:
        """
        Retrieve all loans with pagination and optional status filtering.
        :param page: int - The page number to retrieve.
        :param per_page: int - The number of items per page.
        :param status: Optional[str] - Filter loans by status (e.g., 'active', 'returned').
        :return: Dict[str, Any] - A result dictionary containing loan data, pagination, and filters.
        """

        try:
            page, per_page = self._validate_pagination(page, per_page)
            offset = (page - 1) * per_page

            loans = self.loan_repo.get_all(limit=per_page, offset=offset, status=status)
            total = self.loan_repo.count(status=status)

            # Enrich loan data
            enriched_loans = [self._enrich_loan_data(loan) for loan in loans]

            return {
                'success': True,
                'data': enriched_loans,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                },
                'filters': {
                    'status': status
                }
            }

        except Exception as e:
            return self._handle_exception('get_all_loans', e)

    def get_user_loans(self, user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Retrieve all loan records for a specific user with pagination.

        :param user_id: int - The ID of the user.
        :param page: int - The page number to retrieve (default is 1).
        :param per_page: int - Number of loans per page (default is 20).
        :return: Dict[str, Any] - A dictionary with the user info, loan data, and pagination metadata.
        """

        try:
            user_id_error = self._validate_user_id(user_id)
            if user_id_error:
                return {'success': False, 'error': user_id_error}

            user_error = self._check_user_exists(user_id)
            if user_error:
                return {'success': False, 'error': user_error}

            page, per_page = self._validate_pagination(page, per_page)
            offset = (page - 1) * per_page

            loans = self.loan_repo.get_by_user_id(user_id, limit=per_page, offset=offset)
            total = len(self.loan_repo.get_by_user_id(user_id, limit=10000, offset=0))

            # Get user info
            user = self.user_repo.get_by_id(user_id)
            enriched_loans = [self._enrich_loan_data(loan) for loan in loans]

            return {
                'success': True,
                'data': {
                    'user': user.to_dict() if hasattr(user, 'to_dict') else user,
                    'loans': enriched_loans,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page
                    }
                }
            }

        except Exception as e:
            return self._handle_exception('get_user_loans', e)

    def return_book(self, loan_id: int, return_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Mark a book as returned, optionally calculating and updating a fine if overdue.
        :param loan_id: int - The ID of the loan to return.
        :param return_data: Optional[Dict[str, Any]] - Data used for fine calculation (e.g., 'fine_per_day').
        :return: Dict[str, Any] - A response dictionary with return result and updated loan info.
        """

        try:
            loan_id_error = self._validate_loan_id(loan_id)
            if loan_id_error:
                return {'success': False, 'error': loan_id_error}

            # Validate return data if provided
            if return_data:
                validation_error = self._validate_input_data(return_data, validate_return_data)
                if validation_error:
                    return validation_error

            # Check if loan exists and is active
            loan, error = self._check_loan_exists_and_active(loan_id)
            if error:
                return {'success': False, 'error': error}

            if loan.returned_date:
                return {
                    'success': False,
                    'error': 'Book has already been returned'
                }

            # Calculate and update fine if overdue
            if loan.is_overdue:
                fine_per_day = return_data.get('fine_per_day', 1.0) if return_data else 1.0
                fine_amount = loan.calculate_fine(fine_per_day)
                logger.info(f"Loan {loan_id} is overdue by {loan.days_overdue} days. Calculated fine: ${fine_amount}")
                self.loan_repo.update_fine(loan_id, fine_amount)

            # Get book info before return for logging
            availability_info = self.loan_repo.get_book_availability_info(loan.book_id)
            logger.info(
                f"Returning book {loan.book_id}. Current availability: {availability_info.get('copies_available', 'unknown')}")

            # Return the book with atomic availability update
            returned_loan = self.loan_repo.return_book_with_availability_update(loan_id)
            if returned_loan:
                return {
                    'success': True,
                    'data': self._enrich_loan_data(returned_loan),
                    'message': 'Book returned successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to return book'
                }

        except Exception as e:
            return self._handle_exception('return_book', e)

    def renew_loan(self, loan_id: int, renew_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Renew an active loan by extending its due date.

        :param loan_id: int - The ID of the loan to renew.
        :param renew_data: Optional[Dict[str, Any]] - Data for renewal (e.g., 'renewal_days').
        :return: Dict[str, Any] - A response dictionary with renewal result and new due date.
        """

        try:
            loan_id_error = self._validate_loan_id(loan_id)
            if loan_id_error:
                return {'success': False, 'error': loan_id_error}

            # Validate renewal data if provided
            if renew_data:
                validation_error = self._validate_input_data(renew_data, validate_renewal_data)
                if validation_error:
                    return validation_error

            # Check if loan exists and is active
            loan, error = self._check_loan_exists_and_active(loan_id)
            if error:
                return {'success': False, 'error': error}

            if loan.returned_date:
                return {
                    'success': False,
                    'error': 'Cannot renew: book has already been returned'
                }

            # Check if renewal is allowed
            if loan.days_overdue > 7:
                return {
                    'success': False,
                    'error': f'Cannot renew: loan is {loan.days_overdue} days overdue (maximum 7 days allowed)'
                }

            # Calculate new due date
            renewal_days = renew_data.get('renewal_days', 14) if renew_data else 14
            new_due_date = loan.due_date + timedelta(days=renewal_days)

            logger.info(f"Renewing loan {loan_id}. Old due date: {loan.due_date}, New due date: {new_due_date}")

            # Renew the loan
            renewed_loan = self.loan_repo.renew_loan(loan_id, new_due_date)
            if renewed_loan:
                return {
                    'success': True,
                    'data': self._enrich_loan_data(renewed_loan),
                    'message': f'Loan renewed successfully. New due date: {new_due_date.strftime("%Y-%m-%d")}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to renew loan'
                }

        except Exception as e:
            return self._handle_exception('renew_loan', e)

    def get_overdue_loans(self) -> Dict[str, Any]:
        """
        Retrieve all loans that are currently overdue, including calculated fines.
        :return: Dict[str, Any] - A dictionary containing overdue loan data and total accumulated fines.
        """
        try:
            loans = self.loan_repo.get_overdue_loans()

            # Enrich and update fines
            enriched_loans = []
            total_fines = 0.0

            for loan in loans:
                # Update fine calculation
                fine_amount = loan.calculate_fine()
                if fine_amount != loan.fine_amount:
                    self.loan_repo.update_fine(loan.id, fine_amount)
                    loan.fine_amount = fine_amount

                enriched_loan = self._enrich_loan_data(loan)
                enriched_loans.append(enriched_loan)
                total_fines += fine_amount

            logger.info(f"Retrieved {len(enriched_loans)} overdue loans with total fines: ${total_fines}")

            return {
                'success': True,
                'data': enriched_loans,
                'total_overdue': len(enriched_loans),
                'total_fines': total_fines
            }

        except Exception as e:
            return self._handle_exception('get_overdue_loans', e)

    def get_book_loans(self, book_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Retrieve all loan records for a specific book with pagination and availability info.
        :param book_id: int - The ID of the book.
        :param page: int - The page number to retrieve (default is 1).
        :param per_page: int - Number of loans per page (default is 20).
        :return: Dict[str, Any] - A dictionary with book info, loan records, availability, and pagination.
        """

        try:
            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            book_error = self._check_book_exists(book_id)
            if book_error:
                return {'success': False, 'error': book_error}

            page, per_page = self._validate_pagination(page, per_page)
            offset = (page - 1) * per_page

            loans = self.loan_repo.get_by_book_id(book_id, limit=per_page, offset=offset)
            total = len(self.loan_repo.get_by_book_id(book_id, limit=10000, offset=0))

            # Get book info
            book = self.book_repo.get_by_id(book_id)
            enriched_loans = [self._enrich_loan_data(loan) for loan in loans]
            availability_info = self.loan_repo.get_book_availability_info(book_id)

            return {
                'success': True,
                'data': {
                    'book': book.to_dict() if hasattr(book, 'to_dict') else book,
                    'availability': availability_info,
                    'loans': enriched_loans,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page
                    }
                }
            }

        except Exception as e:
            return self._handle_exception('get_book_loans', e)

    def get_loan_statistics(self) -> Dict[str, Any]:
        """
        Generate and return statistics about all loan activity in the system.
        :return: Dict[str, Any] - A dictionary of statistics including totals, rates, and outstanding fines.
        """

        try:
            # Get counts for different loan statuses
            total_loans = self.loan_repo.count()
            active_loans = self.loan_repo.count(status='active')
            returned_loans = self.loan_repo.count(status='returned')
            overdue_loans = self.loan_repo.count(status='overdue')

            # Get overdue loans for fine calculation
            overdue_loan_objects = self.loan_repo.get_overdue_loans()
            total_fines = sum(loan.calculate_fine() for loan in overdue_loan_objects)

            statistics = {
                'total_loans': total_loans,
                'active_loans': active_loans,
                'returned_loans': returned_loans,
                'overdue_loans': overdue_loans,
                'total_outstanding_fines': total_fines,
                'loan_completion_rate': (returned_loans / total_loans * 100) if total_loans > 0 else 0,
                'overdue_rate': (overdue_loans / active_loans * 100) if active_loans > 0 else 0
            }

            logger.info(f"Generated loan statistics: {statistics}")

            return {
                'success': True,
                'data': statistics
            }

        except Exception as e:
            return self._handle_exception('get_loan_statistics', e)

    def get_user_active_loans(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieve all currently active (non-returned) loans for a specific user.
        :param user_id: int - The ID of the user.
        :return: Dict[str, Any] - A dictionary with the user's active loan data.
        """

        try:
            user_id_error = self._validate_user_id(user_id)
            if user_id_error:
                return {'success': False, 'error': user_id_error}

            # Get active loans for user
            loans = self.loan_repo.get_by_user_id(user_id, limit=100, offset=0)
            active_loans = [loan for loan in loans if not loan.returned_date]

            # Enrich loan data
            enriched_loans = [self._enrich_loan_data(loan) for loan in active_loans]

            return {
                'success': True,
                'data': {
                    'user_id': user_id,
                    'active_loans': enriched_loans,
                    'count': len(enriched_loans)
                }
            }

        except Exception as e:
            return self._handle_exception('get_user_active_loans', e)

    def get_current_book_loans(self, book_id: int) -> Dict[str, Any]:
        """
        Retrieve all active loans for a specific book, along with availability details.
        :param book_id: int - The ID of the book.
        :return: Dict[str, Any] - A dictionary with active loans, availability info, and count of active loans.
        """

        try:
            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            # Get active loans for book
            loans = self.loan_repo.get_by_book_id(book_id, limit=100, offset=0)
            active_loans = [loan for loan in loans if not loan.returned_date]

            # Enrich loan data
            enriched_loans = [self._enrich_loan_data(loan) for loan in active_loans]

            # Get availability info
            availability_info = self.loan_repo.get_book_availability_info(book_id)

            return {
                'success': True,
                'data': {
                    'book_id': book_id,
                    'availability': availability_info,
                    'current_loans': enriched_loans,
                    'copies_on_loan': len(enriched_loans)
                }
            }

        except Exception as e:
            return self._handle_exception('get_current_book_loans', e)

    def get_book_availability(self, book_id: int) -> Dict[str, Any]:
        """
        Get detailed availability information for a specific book.
        :param book_id: int - The ID of the book.
        :return: Dict[str, Any] - A dictionary with availability details or an error message if not found.
        """

        try:
            book_id_error = self._validate_book_id(book_id)
            if book_id_error:
                return {'success': False, 'error': book_id_error}

            # Get comprehensive availability info
            availability_info = self.loan_repo.get_book_availability_info(book_id)

            if not availability_info:
                return {'success': False, 'error': 'Book not found'}

            return {
                'success': True,
                'data': availability_info
            }

        except Exception as e:
            return self._handle_exception('get_book_availability', e)

    def delete_loan(self, loan_id: int, force: bool = False) -> Dict[str, Any]:
        """
        Delete a loan record. If the loan is still active, deletion requires admin override via 'force=True'.
        :param loan_id: int - The ID of the loan to delete.
        :param force: bool - Whether to force delete an active loan (default is False).
        :return: Dict[str, Any] - A dictionary indicating success or failure, and loan info if deleted.
        """

        try:
            loan_id_error = self._validate_loan_id(loan_id)
            if loan_id_error:
                return {'success': False, 'error': loan_id_error}

            # Check if loan exists
            loan, error = self._check_loan_exists_and_active(loan_id)
            if error:
                return {'success': False, 'error': error}

            # Business rule: Only allow deletion of returned loans unless forced
            if not force and not loan.returned_date:
                return {
                    'success': False,
                    'error': 'Cannot delete active loan. Return the book first or use force=true for admin override.'
                }

            # If deleting an active loan (force=true), we need to update book availability
            if not loan.returned_date and force:
                logger.warning(f"Force deleting active loan {loan_id}. Updating book availability.")
                # This should update the book's available copies since we're removing an active loan
                current_availability = self.loan_repo.get_book_availability_info(loan.book_id)
                if current_availability:
                    new_available = current_availability.get('copies_available', 0) + 1
                    self.book_repo.update_availability(loan.book_id, new_available)

            # Store loan info for response before deletion
            loan_info = {
                'id': loan.id,
                'user_id': loan.user_id,
                'book_id': loan.book_id,
                'loan_date': loan.loan_date.isoformat() if loan.loan_date else None,
                'due_date': loan.due_date.isoformat() if loan.due_date else None,
                'returned_date': loan.returned_date.isoformat() if loan.returned_date else None,
                'was_active': not bool(loan.returned_date)
            }

            # Delete the loan
            success = self.loan_repo.delete(loan_id)
            if success:
                logger.info(f"Deleted loan {loan_id}. Was active: {loan_info['was_active']}")
                return {
                    'success': True,
                    'message': 'Loan deleted successfully',
                    'data': loan_info
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to delete loan'
                }

        except Exception as e:
            return self._handle_exception('delete_loan', e)

    def _enrich_loan_data(self, loan: Loan) -> Dict[str, Any]:
        """
        Add user and book metadata to a loan object for display or API output.
        :param loan: Loan - The loan object to enrich.
        :return: Dict[str, Any] - The loan data dictionary enriched with user and book info.
        """

        loan_dict = loan.to_dict()

        try:
            # Add user information
            user = self.user_repo.get_by_id(loan.user_id)
            if user:
                loan_dict['user'] = {
                    'id': user.id,
                    'username': getattr(user, 'username', 'Unknown'),
                    'email': getattr(user, 'email', 'Unknown')
                }

            # Add book information
            book = self.book_repo.get_by_id(loan.book_id)
            if book:
                loan_dict['book'] = {
                    'id': book.id,
                    'title': getattr(book, 'title', 'Unknown'),
                    'author': getattr(book, 'author', 'Unknown'),
                    'isbn': getattr(book, 'isbn', 'Unknown'),
                    'copies_total': getattr(book, 'copies_total', 0),
                    'copies_available': getattr(book, 'copies_available', 0)
                }

        except Exception as e:
            logger.warning(f"Error enriching loan data for loan {loan.id}: {e}")

        return loan_dict