from flask import Flask


def setup_cors(app: Flask):
    """Setup CORS headers for frontend requests."""
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = ['http://localhost:3000', 'https://schlermax.github.io/lesson-plan-generator']
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

