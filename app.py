from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import logging

# Import routes
from routes.genre_routes import genre_bp
from routes.book_routes import book_bp
from routes.user_routes import user_bp
from routes.loan_routes import loan_bp
from routes.external_routes import external_bp
from routes.data_routes import data_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_app(config_class=Config):
    """
    Create and configure the Flask application with all routes, blueprints, and error handlers.

    :param config_class: Config - Configuration class to load app settings from.
    :return: Flask app instance - The configured Flask application.
    """

    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    # Register blueprints
    app.register_blueprint(genre_bp, url_prefix='/api/genres')
    app.register_blueprint(book_bp, url_prefix='/api/books')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(loan_bp, url_prefix='/api/loans')
    app.register_blueprint(external_bp, url_prefix='/api/external')
    app.register_blueprint(data_bp, url_prefix='/data')

    # Root endpoint
    @app.route('/')
    def index():
        """
        Root endpoint providing API basic info.
        :return: JSON response with API message, version, status, and endpoints.
        """

        return jsonify({
            'message': 'Library Management System API',
            'version': '1.0',
            'status': 'Running',
        })

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """
        Health check endpoint to verify database connection status.
        :return: JSON response indicating API and database health status.
        """

        try:
            from models.database import test_connection
            db_status = 'connected' if test_connection() else 'disconnected'
            return jsonify({
                'status': 'healthy',
                'database': db_status,
                'message': 'Health check successful'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'database': 'error',
                'error': str(e)
            }), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 errors for resource not found.
        :param error: The error raised.
        :return: JSON response with error message and 404 status.
        """
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(400)
    def bad_request(error):
        """
        Handle 400 errors for bad requests.
        :param error: The error raised.
        :return: JSON response with error message and 400 status.
        """
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(500)
    def internal_error(error):
        """
        Handle 500 errors for internal server errors.
        :param error: The error raised.
        :return: JSON response with error message and 500 status.
        """
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()

    app.run(debug=True, host='0.0.0.0', port=5000)
