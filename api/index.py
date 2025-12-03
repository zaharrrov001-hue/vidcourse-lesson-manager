"""Vercel serverless function entry point for VidCourse."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app import app

# Vercel expects a handler function
def handler(request):
    """WSGI handler for Vercel."""
    return app(request.environ, request.start_response)

# Export app for Vercel Python runtime
# Vercel will automatically detect and use the Flask app
__all__ = ['app', 'handler']