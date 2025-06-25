import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any, List, Callable
from services.loan_service import LoanService
import logging

logger = logging.getLogger(__name__)


class DataService:

    def __init__(self):
        self.loan_service = LoanService()

    @staticmethod
    def _handle_exception(operation: str, error: Exception) -> Dict[str, Any]:
        """
        Handle all exceptions consistently
        :param operation: Name of the operation being performed
        :param error: Exception that occurred
        :return: Dictionary with error information
        """
        logger.error(f"Error in {operation}: {error}")
        return {'success': False, 'error': 'Export failed'}

    @staticmethod
    def _create_temp_excel_file(filename_prefix: str) -> str:
        """
        Create Excel file in data directory
        :param filename_prefix: Prefix for the filename
        :return: Full path to the created Excel file
        """

        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(data_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        return os.path.join(data_dir, filename)

    @staticmethod
    def _loans_to_dataframe(enriched_loans: List[Dict]) -> pd.DataFrame:
        """
        Convert enriched loan data to pandas DataFrame
        :param enriched_loans: List of enriched loan dictionaries
        :return: DataFrame with loan data
        """

        if not enriched_loans:
            return pd.DataFrame()

        # Use pandas json_normalize - it's designed exactly for this
        df = pd.json_normalize(enriched_loans)

        # Convert date columns to proper datetime
        date_columns = [col for col in df.columns if 'date' in col]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Fill NaN with empty strings for cleaner Excel
        df = df.fillna('')

        return df

    def _create_excel_result(self, df: pd.DataFrame, filename_prefix: str,
                             data_count: int, extra_data: Dict = None) -> Dict[str, Any]:
        """
        Create Excel file
        :param df: DataFrame with loan data
        :param filename_prefix: Prefix for the filename
        :param data_count: Number of loans in the data
        :param extra_data: Additional data to include in the result
        :return: Dictionary with result information
        """

        file_path = self._create_temp_excel_file(filename_prefix)

        # Simple Excel export - pandas handles everything
        df.to_excel(file_path, sheet_name='Data', index=False, engine='openpyxl')

        result = {
            'success': True,
            'file_path': file_path,
            'filename': f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            'loans_count': data_count
        }

        if extra_data:
            result.update(extra_data)

        return result

    def _export_loans(self, service_method: Callable, method_args: tuple,
                      filename_prefix: str, error_message: str,
                      data_key: str = 'data', extra_data_keys: List[str] = None) -> Dict[str, Any]:
        """
        Generic export method for all loan exports
        :param service_method: Service method to call
        :param method_args: Arguments to pass to the service method
        :param filename_prefix: Prefix for the output filename
        :param error_message: Error message if no loans found
        :param data_key: Key to extract loan data from the result
        :param extra_data_keys: Additional keys to extract from the result
        :return: Dictionary with result information
        """

        try:
            # Call the service method
            result = service_method(*method_args)
            if not result['success']:
                return result

            # Extract loan data
            if data_key == 'data' and isinstance(result['data'], dict) and 'loans' in result['data']:
                loans = result['data']['loans']  # For user loans
            else:
                loans = result[data_key]  # For direct loan lists

            if not loans:
                return {'success': False, 'error': error_message}

            # Create DataFrame and Excel file
            df = self._loans_to_dataframe(loans)

            # Extract extra data if specified
            extra_data = {}
            if extra_data_keys:
                for key in extra_data_keys:
                    if key in result:
                        extra_data[key] = result[key]

            return self._create_excel_result(df, filename_prefix, len(loans), extra_data)

        except Exception as e:
            return self._handle_exception(f'export_{filename_prefix}', e)

    def export_user_loans_to_excel(self, username: str, **kwargs) -> Dict[str, Any]:
        """
        Export user loans to Excel
        :param username: Username of the user whose loans to export
        :return: Dictionary with result information
        """

        # Get user first
        user = self.loan_service.user_repo.get_by_username(username)
        if not user:
            return {'success': False, 'error': f'User "{username}" not found'}

        return self._export_loans(
            service_method=self.loan_service.get_user_loans,
            method_args=(user.id, 1, 10000),
            filename_prefix=f"user_loans_{username}",
            error_message=f'No loans found for user "{username}"'
        )

    def export_all_loans_to_excel(self, status_filter: str = None, **kwargs) -> Dict[str, Any]:
        """
        Export all loans to Excel
        :param status_filter: Optional filter for loan status (e.g., 'active', 'overdue')
        :return: Dictionary with result information
        """

        suffix = f"_{status_filter}" if status_filter else "_all"
        return self._export_loans(
            service_method=self.loan_service.get_all_loans,
            method_args=(1, 10000, status_filter),
            filename_prefix=f"all_loans{suffix}",
            error_message='No loans found'
        )

    def export_overdue_loans_to_excel(self, **kwargs) -> Dict[str, Any]:
        """
        Export overdue loans to Excel
        :return: Dictionary with result information
        """

        return self._export_loans(
            service_method=self.loan_service.get_overdue_loans,
            method_args=(),
            filename_prefix="overdue_loans",
            error_message='No overdue loans found',
            extra_data_keys=['total_fines']
        )