from flask import Blueprint, request, jsonify
from services.external_service import ExternalBookService

external_bp = Blueprint('external', __name__)


@external_bp.route('/languages', methods=['GET'])
def get_languages():
    """
    This endpoint retrieves the languages of a book by its title.
    :return: A JSON response containing the languages of the book or an error message.
    """
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
    """
    This endpoint retrieves books by the same author based on the title of a book.
    :return: A JSON response containing books by the same author or an error message.
    """
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
