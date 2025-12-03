"""Vercel serverless function entry point for VidCourse."""
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Flask app
from web_app import app

# Vercel expects the app to be available
# For Vercel Python runtime, we export the app directly
__all__ = ['app']