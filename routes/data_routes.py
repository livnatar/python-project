from flask import Blueprint, request, jsonify, send_file
from services.data_service import DataService
import logging

logger = logging.getLogger(__name__)

data_bp = Blueprint('data', __name__)
data_service = DataService()


def _handle_export_route(export_function, *args, **kwargs):
    """
    Generic handler for export routes to manage file generation and response.
    :param export_function: The function that performs the export logic.
    :param args: The positional arguments to pass to the export function.
    :param kwargs: The keyword arguments to pass to the export function.
    :return: A Flask response with the generated file or an error message.
    """

    try:
        result = export_function(*args, **kwargs)

        if not result['success']:
            return jsonify({'error': result['error']}), 400

        file_path = result['file_path']
        return send_file(
            file_path,
            as_attachment=True,
            download_name=result['filename'],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"Export route error: {e}")
        return jsonify({'error': 'Export failed'}), 500


@data_bp.route('/export/user-loans/<username>', methods=['GET'])
def export_user_loans(username):
    """
    Export loans for a specific user to Excel.
    :param username: The username of the user whose loans are to be exported.
    :return: A response with the generated Excel file or an error message.
    """
    if not username.strip():
        return jsonify({'error': 'Username required'}), 400

    return _handle_export_route(
        data_service.export_user_loans_to_excel,
        username.strip()
    )


@data_bp.route('/export/all-loans', methods=['GET'])
def export_all_loans():
    """
    Export all loans to Excel with optional status filter.
    :return: A response with the generated Excel file or an error message.
    """
    status = request.args.get('status')

    # Validate status parameter if provided
    if status:
        valid_statuses = ['active', 'returned', 'overdue']
        if status not in valid_statuses:
            return jsonify({
                'error': f'Invalid status filter. Must be one of: {", ".join(valid_statuses)}'
            }), 400

    return _handle_export_route(
        data_service.export_all_loans_to_excel,
        status_filter=status
    )


@data_bp.route('/export/overdue-loans', methods=['GET'])
def export_overdue_loans():
    """
    Export all overdue loans to Excel.
    :return: A response with the generated Excel file or an error message.
    """
    return _handle_export_route(
        data_service.export_overdue_loans_to_excel
    )