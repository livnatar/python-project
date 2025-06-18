from flask import Blueprint, request, jsonify, send_file
from services.data_service import DataService
import logging
import os

logger = logging.getLogger(__name__)

data_bp = Blueprint('data', __name__)
data_service = DataService()


def _handle_export_route(export_function, *args, **kwargs):
    """Generic handler for all export routes"""
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
    """Export user loans to Excel"""
    if not username.strip():
        return jsonify({'error': 'Username required'}), 400

    return _handle_export_route(
        data_service.export_user_loans_to_excel,
        username.strip()
    )


@data_bp.route('/export/all-loans', methods=['GET'])
def export_all_loans():
    """Export all loans to Excel"""
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
    """Export overdue loans to Excel"""
    return _handle_export_route(
        data_service.export_overdue_loans_to_excel
    )