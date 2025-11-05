import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    LINK_PER_PAGE = 8
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB limit for uploaded files
    UPLOAD_EXTENSIONS = ['jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp']
    UPLOAD_PATH = os.path.join(basedir, 'uploads')

    # Session configuration for "Remember Me" functionality
    REMEMBER_COOKIE_DURATION = timedelta(days=30)  # Remember for 30 days
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookie
    REMEMBER_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)  # Session lifetime