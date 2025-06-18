from flask import Blueprint, request, jsonify
from services.external_service import ExternalBookService

external_bp = Blueprint('external', __name__)

@external_bp.route('/languages', methods=['GET'])
def get_languages():
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Missing 'title' query parameter"}), 400

    result = ExternalBookService.get_languages_by_title(title)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)

@external_bp.route('/similar', methods=['GET'])
def get_similar_books():
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Missing 'title' query parameter"}), 400

    result = ExternalBookService.get_similar_books_by_title(title)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)
