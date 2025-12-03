"""Vercel serverless function для простой версии с загрузкой файлов."""
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Flask app
from web_app_upload import app

# Vercel expects the app to be available
__all__ = ['app']