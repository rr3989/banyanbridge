from app import app
from flask import jsonify

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Handle the request and return proper response
        response = app(request.environ, lambda status, headers: None)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel Python runtime expects 'application' variable
application = app