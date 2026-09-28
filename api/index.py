from app import app
from flask import jsonify

def handler(request):
    """Vercel serverless function handler with enhanced error handling"""
    try:
        # Handle the request and return proper response
        environ = create_environ(request)
        response = app(environ, lambda status, headers: None)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_environ(request):
    """Create WSGI environment from Vercel request"""
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string.decode('utf-8') if request.query_string else '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': request.headers.get('content-length', ''),
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '5000',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body,
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add headers
    for key, value in request.headers.items():
        header_key = f'HTTP_{key.upper().replace("-", "_")}'
        environ[header_key] = value
    
    return environ

# Vercel Python runtime expects 'application' variable
application = app