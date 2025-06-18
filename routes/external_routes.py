from flask import Blueprint, request, jsonify
from services.external_service import ExternalBookService

external_bp = Blueprint('external', __name__)


@external_bp.route('/languages', methods=['GET'])
def get_languages():
    try:
        title = request.args.get('title')
        if not title:
            return jsonify({"error": "Missing 'title' query parameter"}), 400

        result = ExternalBookService.get_languages_by_title(title)
        if "error" in result:
            return jsonify(result), 404

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Internal server error while getting languages: {str(e)}"}), 500


@external_bp.route('/same-author', methods=['GET'])
def get_similar_books():
    try:
        title = request.args.get('title')
        if not title:
            return jsonify({"error": "Missing 'title' query parameter"}), 400

        result = ExternalBookService.get_same_author_books_by_title(title)
        if "error" in result:
            return jsonify(result), 404

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Internal server error while getting books by the same author: {str(e)}"}), 500
