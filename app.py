from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import routes
from routes.genre_routes import genre_bp
from routes.book_routes import book_bp
from routes.user_routes import user_bp

# Other routes will be imported as we create them

# from routes.loan_routes import loan_bp
# from routes.reservation_routes import reservation_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)  # Add CORS like your working project
    app.config.from_object(config_class)

    # Register blueprints
    app.register_blueprint(genre_bp, url_prefix='/api/genres')
    app.register_blueprint(book_bp, url_prefix='/api/books')
    app.register_blueprint(user_bp, url_prefix='/api/users')

    # Other blueprints will be registered as we create them
    # app.register_blueprint(loan_bp, url_prefix='/api/loans')
    # app.register_blueprint(reservation_bp, url_prefix='/api/reservations')

    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Library Management System API',
            'version': '1.0',
            'status': 'Running',
            'available_endpoints': {
                'genres': '/api/genres',
                'books': '/api/books',
                'health': '/health'
            }
        })

    # Health check endpoint (test DB connection here, not on startup)
    @app.route('/health')
    def health_check():
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
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print("Starting Library Management System with Many-to-Many Genre Support...")
    print("Database connection tested successfully!")
    print("\n=== GENRE ENDPOINTS ===")
    print("  - GET    /api/genres")
    print("  - POST   /api/genres")
    print("  - GET    /api/genres/<id>")
    print("  - GET    /api/genres/<genre_name>")
    print("  - PUT    /api/genres/<id>")
    print("  - DELETE /api/genres/<id>")
    print("  - GET    /api/genres/search?q=<term>")
    print("  - GET    /api/genres/<id>/books")
    print("\n=== BOOK ENDPOINTS ===")
    print("  - GET    /api/books")
    print("  - POST   /api/books")
    print("  - GET    /api/books/<id>")
    print("  - PUT    /api/books/<id>")
    print("  - DELETE /api/books/<id>")
    print("  - GET    /api/books/isbn/<isbn>")
    print("  - GET    /api/books/search?q=<term>&genre_id=<id>")
    print("  - GET    /api/books/available")
    print("  - GET    /api/books/genre/<genre_id>")
    print("  - POST   /api/books/<id>/genres")
    print("  - DELETE /api/books/<id>/genres/<genre_id>")
    print("  - PUT    /api/books/<id>/availability")
    print("\n=== USER ENDPOINTS ===")
    print('POST /api/users')
    print('GET /api/users')
    print('GET /api/users/<id>')
    print('GET /api/users/username/<username>')
    print('PUT /api/users/<id>')
    print('PUT /api/users/<id>/password')
    print('DELETE /api/users/<id>')
    print('POST /api/users/authenticate')
    print('GET /api/users/stats')

    app.run(debug=True, host='0.0.0.0', port=5000)